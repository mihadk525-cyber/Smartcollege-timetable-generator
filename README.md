# Automated College Timetable and Resource Scheduling System

Generates clash-free college timetables from faculty, subjects, batches, classrooms and time slots.
End-to-end project: **React frontend + Flask backend + SQL database (SQLite / MySQL) + DSA core**.

## Folder structure

```
timetable-scheduler/
├── backend/
│   ├── scheduler/            <- DSA core (pure Python, no web/DB needed)
│   │   ├── conflict_graph.py   conflict graph (hash map of sets)
│   │   ├── coloring.py         DSATUR graph colouring + priority queue
│   │   ├── solver.py           backtracking CSP solver (MRV + forward checking)
│   │   ├── validator.py        conflict detection for manual edits
│   │   ├── entities.py         data classes
│   │   ├── sample_data.py      sample data (replace with real Sunstone data)
│   │   └── demo.py             Phase 1 demo (no frontend / DB)
│   ├── app.py                REST API (Flask)
│   ├── models.py, seed.py    database models + sample-data loader
│   └── tests/                pytest tests
├── database/schema.mysql.sql
├── frontend/                 React (Vite) UI
└── docs/                     ALGORITHMS.md, CONTRIBUTIONS.md
```

## Run it

**Backend** (Python 3.10+):
```bash
cd backend
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m pytest                 # run tests
python -m scheduler.demo         # PHASE 1 demo: DSA + algorithms, no frontend
python app.py                    # API on http://localhost:5000
```
SQLite is the default (`timetable.db` is created automatically). To use MySQL:
```bash
export DATABASE_URL="mysql+pymysql://USER:PASSWORD@localhost/timetable"   # create the DB first
```

**Frontend** (Node 18+), in a second terminal:
```bash
cd frontend
npm install
npm run dev                      # http://localhost:5173 (proxies /api to Flask)
```
In the app: **Timetable -> Load sample data -> Generate timetable**. Click any lecture to move it;
the backend rejects moves that create a clash.

## How the brief's features map to the code

| Required feature | Where |
|---|---|
| Add faculty / subject details | `POST /api/faculty`, `/api/subjects` · Setup tab |
| Manage student batches | `/api/batches` |
| Classroom information | `/api/rooms` (capacity, lab or classroom) |
| Define time slots | `/api/slots` |
| Generate timetables automatically | `scheduler/solver.py` · `POST /api/generate` |
| Detect faculty and classroom conflicts | `scheduler/validator.py` · `GET /api/conflicts` |
| Manual timetable modification | `PUT /api/timetable/<id>` (validated) |
| Export the final timetable | `GET /api/timetable/export` (CSV) |

| DSA concept | Where |
|---|---|
| Graph colouring | `coloring.py` (DSATUR) on the conflict graph |
| Backtracking + recursion | `solver.py` `_backtrack` |
| Constraint satisfaction | `solver.py` (domains, forward checking, MRV) |
| Greedy algorithms | DSATUR ordering, value ordering (spread lectures over days) |
| Priority queue | `heapq` inside DSATUR |
| Hash maps / sets | conflict graph, validator |

Time and space complexity of each algorithm: see `docs/ALGORITHMS.md`.

## Before you submit

1. **Replace the sample data** in `backend/scheduler/sample_data.py` (or enter it in the Setup tab)
   with the real Sunstone faculty, rooms, batches and subjects. The sample values are made up.
2. Fill in `docs/CONTRIBUTIONS.md`. Every member must be able to explain their own part.
3. Commit regularly and push to GitHub (the brief requires visible commit history):
   ```bash
   git init && git add . && git commit -m "Initial project structure"
   git branch -M main
   git remote add origin <your-repo-url> && git push -u origin main
   ```

## Known limitations (good extension ideas)
- A lab is a single one-hour lecture; real labs usually need 2 consecutive periods.
- Rules such as "no more than 3 lectures in a row" or "lunch break" are not modelled.
- The solver stops after 200,000 search steps and reports failure instead of running forever.
