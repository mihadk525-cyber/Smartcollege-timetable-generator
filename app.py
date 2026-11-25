"""Flask REST API.  Run:  python app.py   (http://localhost:5000)
Database: SQLite by default; set DATABASE_URL=mysql+pymysql://user:pass@localhost/timetable for MySQL."""
import csv
import io
import os
from dataclasses import replace

from flask import Flask, Response, jsonify, request
from flask_cors import CORS

from models import db, Faculty, Batch, Room, Slot, Subject, FacultyUnavailable, Entry
from scheduler import Event, TimetableSolver, build_problem, find_conflicts
from seed import seed_database

RESOURCES = {"faculty": Faculty, "batches": Batch, "rooms": Room, "slots": Slot,
             "subjects": Subject, "unavailability": FacultyUnavailable}
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"]


def row(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


def load_problem():
    unavailable = {}
    for u in FacultyUnavailable.query.all():
        unavailable.setdefault(u.faculty_id, set()).add(u.slot_id)
    return build_problem([row(x) for x in Subject.query.all()], [row(x) for x in Batch.query.all()],
                         [row(x) for x in Room.query.all()], [row(x) for x in Slot.query.all()],
                         unavailable)


def entries_problem(overrides=None):
    """Rebuild a Problem whose events are the saved timetable rows, plus their assignment."""
    base = load_problem()
    subjects = {s.id: s for s in Subject.query.all()}
    events, assignment = [], {}
    for en in Entry.query.all():
        s = subjects[en.subject_id]
        events.append(Event(en.id, s.id, s.code, s.faculty_id, s.batch_id, s.is_lab))
        assignment[en.id] = (en.slot_id, en.room_id)
    assignment.update(overrides or {})
    return replace(base, events=events), assignment


def timetable_rows():
    subjects = {s.id: s for s in Subject.query.all()}
    faculty = {f.id: f.name for f in Faculty.query.all()}
    batches = {b.id: b.name for b in Batch.query.all()}
    rooms = {r.id: r.name for r in Room.query.all()}
    slots = {s.id: s for s in Slot.query.all()}
    out = []
    for e in Entry.query.order_by(Entry.id).all():
        s, sl = subjects[e.subject_id], slots[e.slot_id]
        out.append({"id": e.id, "code": s.code, "subject": s.name, "faculty": faculty[s.faculty_id],
                    "batch_id": s.batch_id, "batch": batches[s.batch_id], "room_id": e.room_id,
                    "room": rooms[e.room_id], "slot_id": e.slot_id, "day": sl.day, "period": sl.period})
    return out


def register_crud(app):
    def make(name, model):
        def list_or_create():
            if request.method == "POST":
                try:
                    obj = model(**(request.get_json() or {}))
                except TypeError as err:
                    return jsonify(error=str(err)), 400
                db.session.add(obj)
                db.session.commit()
                return jsonify(row(obj)), 201
            return jsonify([row(o) for o in model.query.order_by(model.id).all()])

        def delete(item_id):
            db.session.delete(db.get_or_404(model, item_id))
            db.session.commit()
            return "", 204

        app.add_url_rule(f"/api/{name}", f"{name}_list", list_or_create, methods=["GET", "POST"])
        app.add_url_rule(f"/api/{name}/<int:item_id>", f"{name}_delete", delete, methods=["DELETE"])

    for name, model in RESOURCES.items():
        make(name, model)


def create_app(db_url=None):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///timetable.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    CORS(app)
    db.init_app(app)
    with app.app_context():
        db.create_all()
    register_crud(app)

    @app.post("/api/seed")
    def seed():
        seed_database()
        return jsonify(success=True)

    @app.post("/api/generate")
    def generate():
        problem = load_problem()
        result = TimetableSolver(problem).solve()
        if not result.success:
            return jsonify(success=False, message=result.message, nodes=result.nodes), 422
        Entry.query.delete()
        by_id = {e.id: e for e in problem.events}
        for eid, (slot_id, room_id) in result.assignment.items():
            db.session.add(Entry(subject_id=by_id[eid].subject_id, slot_id=slot_id, room_id=room_id))
        db.session.commit()
        return jsonify(success=True, nodes=result.nodes, elapsed_ms=result.elapsed_ms,
                       colors_used=result.colors_used, graph_edges=result.graph_edges)

    @app.get("/api/timetable")
    def timetable():
        return jsonify(timetable_rows())

    @app.put("/api/timetable/<int:entry_id>")
    def move_entry(entry_id):
        entry = db.get_or_404(Entry, entry_id)
        data = request.get_json() or {}
        if "slot_id" not in data or "room_id" not in data:
            return jsonify(success=False, conflicts=["slot_id and room_id are required"]), 400
        problem, assignment = entries_problem({entry.id: (int(data["slot_id"]), int(data["room_id"]))})
        conflicts = find_conflicts(problem, assignment)
        if conflicts:
            return jsonify(success=False, conflicts=conflicts), 409
        entry.slot_id, entry.room_id = assignment[entry.id]
        db.session.commit()
        return jsonify(success=True)

    @app.get("/api/conflicts")
    def conflicts():
        problem, assignment = entries_problem()
        return jsonify(conflicts=find_conflicts(problem, assignment))

    @app.get("/api/timetable/export")
    def export_csv():
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(["batch", "day", "period", "subject_code", "subject", "faculty", "room"])
        for r in sorted(timetable_rows(), key=lambda r: (r["batch"], r["day"], r["period"])):
            w.writerow([r["batch"], DAYS[r["day"]], r["period"] + 1, r["code"], r["subject"], r["faculty"], r["room"]])
        return Response(buf.getvalue(), mimetype="text/csv",
                        headers={"Content-Disposition": "attachment; filename=timetable.csv"})

    return app


if __name__ == "__main__":
    create_app().run(debug=True, port=5000)
