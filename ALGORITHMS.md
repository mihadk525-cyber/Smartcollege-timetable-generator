# Algorithms, complexity and viva notes

n = lectures per week (events), m = edges in the conflict graph, S = time slots, R = rooms.

## 1. Conflict graph (`conflict_graph.py`)
Each lecture is a vertex. Two lectures get an edge if they share a faculty member or a batch, because
they can never be in the same slot. Stored as a hash map of sets (adjacency list).
- Time: O(sum of g^2) over faculty/batch groups, worst case O(n^2). Space: O(n + m).

## 2. DSATUR graph colouring (`coloring.py`)
Colour = time-slot class. Repeatedly colour the vertex with the most distinct neighbour colours
(highest "saturation"), ties broken by highest degree. A max-priority queue (`heapq`) selects the vertex.
- Time: O((n + m) log n). Space: O(n + m).
- Result is an **upper bound** on slots needed. If it is <= S, a slot assignment without clashes is guaranteed
  (before considering rooms). It is a greedy heuristic, so it may use more colours than the optimum.

## 3. Backtracking CSP solver (`solver.py`)
Variable = lecture. Domain = all legal (slot, room) pairs (capacity, lab type, faculty availability).
Search is recursive depth-first with:
- **MRV**: choose the lecture with the fewest remaining options (fail early).
- **Forward checking**: after placing a lecture, remove its slot from conflicting lectures' domains and its
  room from every lecture's domain in that slot. An empty domain triggers backtracking.
- **Greedy value ordering**: try days where the batch has the fewest lectures first (spreads the week).
- Time: worst case O((S x R)^n), exponential, as for any CSP. MRV and forward checking prune most of the tree;
  the sample data (44 lectures) solves in about 44 search nodes.
- Space: O(n x S x R) for domains plus O(n) recursion depth.

## 4. Conflict validator (`validator.py`)
A hash map keyed by (faculty/batch/room, id, slot) finds double-bookings in a single pass.
Also checks room capacity, lab vs classroom and faculty unavailability.
- Time: O(n). Space: O(n). Used for every manual edit (`PUT /api/timetable/<id>`).

## Likely viva questions
- Why a graph for scheduling? Conflicts are pairwise, which is exactly what edges represent.
- Why does the solver backtrack? A choice that looks fine now may leave a later lecture with no valid option.
- Why is DSATUR only a bound, not the full answer? Colouring ignores rooms; rooms are handled by the CSP search.
- What happens if no timetable exists? The solver exhausts the search (or hits the node limit) and returns a message.
