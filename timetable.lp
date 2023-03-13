lecturer(stevie).
lecturer(lindsey).
lecturer(mick).

course(java).
course(symbolic).
course(logic).

slot(1).
slot(2).
slot(3).
slot(4).
slot(5).
slot(6).
slot(7).
slot(8).
slot(9).
slot(10).
slot(11).
slot(12).
slot(13).
slot(14).
slot(15).

room(1).
room(2).
room(3).

lab(1).

capacity(1, 50).
capacity(2, 45).
capacity(3, 85).

registered(java, 30).
registered(symbolic, 61).
registered(logic, 75).

can_teach(stevie, java).
can_teach(stevie, symbolic).
can_teach(lindsey, logic).
can_teach(lindsey, symbolic).
can_teach(mick, logic).
can_teach(mick, java).

required_slots(java, 8).
required_slots(symbolic, 6).
required_slots(logic, 12).

max_slots(stevie, 8).
max_slots(lindsey, 12).
max_slots(mick, 8).

unavailable(stevie, 1).
unavailable(stevie, 5).
unavailable(stevie, 6).
unavailable(stevie, 9).
unavailable(lindsey, 6).
unavailable(lindsey, 9).
unavailable(mick, 5).
unavailable(mick, 6).
unavailable(mick, 10).
unavailable(mick, 11).

prerequisite(symbolic, logic).




% (a) Write a choice rule for assigning lecturers 
% courses conditional on their being able and available to teach it

{assign(X, Y, Z)} :- can_teach(X, Y), not unavailable(X, Z), lecturer(X), course(Y), slot(Z).

% (b) write a choice rules that schedules at most one course
% at most in one room at any one time.

{schedule(X, Y, Z)} :- course(X), room(Y), slot(Z), not schedule(K, Y, Z), course(K).

% (c) write a choice rules that books at most one courses
% in one lab at any one time.

{book(X, Y, Z)} :- course(X), lab(Y), slot(Z), not book(K, Y, Z), course(K).

% (d.i) write a rule using aggregate expression that gives the number
% of hours a lecturer is assigned to teach

total_assigned_hours(X, T) :- T = #count {Y, Z: assign(X, Y, Z)}, lecturer(X).
% (d.ii) write a constraint using an aggregate expression that ensures that lecturers are not assigned
% to teach more hours than their maximum number of slots.

:- T > M, total_assigned_slots(X, T), max_slots(X, M).

% (e) write a constraint to ensure no course is scheduled in a room with not 
% enough capacity. 

:- N > C, schedule(X, Y, Z), capacity(Y, C), registered(X, N).

% (f) write a constraint that ensures courses are scheduled at most once at any specific slot. 

:- schedule(X, Y, Z), schedule(X, A, Z), Y != A.

% (g) write a constraint that ensures  no lecturer is assigned
% two courses scheduled at the same time.

:- assign(X, Y, Z), assign(X, A, Z), Y != A.

% (h) write a constraint that ensures that a course is not scheduled for more hours
% than it requires

:- T != S, T = #count {Z: schedule(X, Y, Z)}, required_slots(X, S).

% (i.i) define a predicate scheduled/2 which holds
% if a course has been scheduled a time in the timetable

scheduled(X, Z) :- schedule(X, Y, Z).

% (i.ii) write a constraint to ensure every assigned course is scheduled
:- assigned(C, S), not scheduled(C, S).
% (j.i) define a predicate assigned/2 which holds
% if a course has been assigned a lecturer at a given time.

assigned(Y, Z) :- assign(X, Y, Z).

% (j.ii) write a constraint that ensures every scheduled course
% assigned a lecturer 

:- not assigned(C, S), scheduled(C, S).
% (k) write a constraint that ensures no course is scheduled
% before its prerequisites
:- scheduled(C1, S1), scheduled(C2, S2), S1 < S2, prerequisite(C1, C2).
% (l) write a constraint that ensures no lecturer is assigned
% to teach a course in a room immediately following another
% lecturer with which they have a conflict;
% lecturer with which they have a conflict;
:- schedule(Y, R, Z), schedule(B, R, C), conflict(A, X), assign(X, Y, Z), assign(A, B, C), Z + 1 == C.
% (m) write a constraint that ensures every course must have at least one
% lab slot for every two slots not in a lab
:- N != S / 2, N = {book(X, Y, Z)}, required_slots(X, S).
% (n) write a constraint that ensures no lab session for a course is booked
% at the same time as its scheduled lecture.
:- book(C, _, Z), scheduled(C, Z).
% (o.i) define a predicate scheduled_before/2 which holds
% if a course has been scheduled before a specific time in the timetable

scheduled_before(X, Z) :- scheduled(X, S), S < Z, slot(Z).
% (o.ii) write a constraint that ensures no lab session for a course is booked
% before at least one lecture has been scheduled.
:- not scheduled_before(X, Z), book(X, _, Z), course(X), slot(Z).
% (p) write an optimization statement that minimizes the max 
% number of hours lecturers is assisgned to teach

assigned_slots(L, N) :- {slot(C) : assign(L, C, S)} = N, lecturer(L).#minimize {N @ 1, L: lecturer(L), assigned_slots(L, N)}.
% write a rule for assigned_courses/2 that gives the number
% of courses assigned to a lecturer.

assigned_courses(L, N) :- {course(C): assign(L, C, S)} = N, lecturer(L).
% (q) write an optimization statement that minimizes the number of courses
% lecturers are assigned

#minimize {N @ 2, L: lecturer(L), assigned_courses(L, N)}.
#show schedule/3.
#show assign/3.
#show book/3.
