from models import db, Faculty, Batch, Room, Slot, Subject, FacultyUnavailable, Entry
from scheduler import sample_data as sd


def seed_database():
    """Wipe every table and load the sample data."""
    for model in (Entry, FacultyUnavailable, Subject, Slot, Room, Batch, Faculty):
        model.query.delete()
    db.session.add_all([Faculty(**r) for r in sd.FACULTY] + [Batch(**r) for r in sd.BATCHES]
                       + [Room(**r) for r in sd.ROOMS] + [Slot(**r) for r in sd.SLOTS])
    db.session.commit()
    db.session.add_all([Subject(**r) for r in sd.SUBJECTS]
                       + [FacultyUnavailable(faculty_id=f, slot_id=s)
                          for f, slots in sd.UNAVAILABLE.items() for s in slots])
    db.session.commit()
