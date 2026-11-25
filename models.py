from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Faculty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)


class Batch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    size = db.Column(db.Integer, nullable=False)


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    is_lab = db.Column(db.Boolean, nullable=False, default=False)


class Slot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Integer, nullable=False)      # 0 = Monday
    period = db.Column(db.Integer, nullable=False)   # 0-based


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey("faculty.id"), nullable=False)
    batch_id = db.Column(db.Integer, db.ForeignKey("batch.id"), nullable=False)
    lectures_per_week = db.Column(db.Integer, nullable=False, default=3)
    is_lab = db.Column(db.Boolean, nullable=False, default=False)


class FacultyUnavailable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey("faculty.id"), nullable=False)
    slot_id = db.Column(db.Integer, db.ForeignKey("slot.id"), nullable=False)


class Entry(db.Model):
    """One scheduled lecture = a row of the generated timetable."""
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=False)
    slot_id = db.Column(db.Integer, db.ForeignKey("slot.id"), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey("room.id"), nullable=False)
