lecturer(xi).
lecturer(andrew).
lecturer(devi).
lecturer(angus).
lecturer(mona).
lecturer(hans).

course(literature).
course(grammar).
course(classics).
course(poetry).
course(ancient_greek).

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
slot(16).
slot(17).
slot(18).
slot(19).
slot(20).
slot(21).
slot(22).
slot(23).
slot(24).
slot(25).
slot(26).
slot(27).
slot(28).
slot(29).
slot(30).
slot(31).
slot(32).
slot(33).
slot(34).
slot(35).
slot(36).
slot(37).
slot(38).

room(1).
room(2).
room(3).
room(4).
room(5).
room(6).
room(7).
room(8).
room(9).
room(10).

lab(1).
lab(2).
lab(3).
lab(4).
lab(5).

capacity(1, 52).
capacity(2, 47).
capacity(3, 85).
capacity(4, 100).
capacity(5, 65).
capacity(6, 35).
capacity(7, 97).
capacity(8, 65).
capacity(9, 120).
capacity(10, 54).

registered(literature, 75).
registered(grammar, 65).
registered(classics, 97).
registered(ancient_greek, 20).
registered(poetry, 40).

can_teach(xi, literature).
can_teach(xi, grammar).
can_teach(andrew, grammar).
can_teach(andrew, classics).
can_teach(devi, classics).
can_teach(devi, poetry).
can_teach(angus, poetry).
can_teach(angus, ancient_greek).
can_teach(mona, literature).
can_teach(mona, grammar).
can_teach(mona, classics).
can_teach(mona, poetry).
can_teach(mona, ancient_greek).

required_slots(literature, 24).
required_slots(grammar, 20).
required_slots(classics, 20).
required_slots(poetry, 10).
required_slots(ancient_greek, 14).

max_slots(xi, 11).
max_slots(andrew, 8).
max_slots(devi, 15).
max_slots(angus, 15).
max_slots(mona, 9).
max_slots(hans, 15).

unavailable(xi, 20).
unavailable(xi, 21).
unavailable(xi, 22).
unavailable(xi, 23).
unavailable(xi, 24).
unavailable(xi, 25).
unavailable(xi, 26).
unavailable(xi, 27).
unavailable(xi, 28).
unavailable(xi, 29).
unavailable(xi, 30).
unavailable(xi, 1).
unavailable(xi, 4).
unavailable(xi, 9).
unavailable(andrew, 20).
unavailable(andrew, 21).
unavailable(andrew, 22).
unavailable(andrew, 23).
unavailable(andrew, 24).
unavailable(andrew, 25).
unavailable(andrew, 26).
unavailable(andrew, 27).
unavailable(andrew, 28).
unavailable(andrew, 29).
unavailable(andrew, 30).
unavailable(andrew, 2).
unavailable(andrew, 5).
unavailable(andrew, 12).
unavailable(andrew, 17).
unavailable(devi, 20).
unavailable(devi, 21).
unavailable(devi, 22).
unavailable(devi, 23).
unavailable(devi, 24).
unavailable(devi, 25).
unavailable(devi, 26).
unavailable(devi, 27).
unavailable(devi, 28).
unavailable(devi, 29).
unavailable(devi, 30).
unavailable(devi, 1).
unavailable(devi, 2).
unavailable(devi, 3).
unavailable(devi, 4).
unavailable(angus, 20).
unavailable(angus, 21).
unavailable(angus, 22).
unavailable(angus, 23).
unavailable(angus, 24).
unavailable(angus, 25).
unavailable(angus, 26).
unavailable(angus, 27).
unavailable(angus, 28).
unavailable(angus, 29).
unavailable(angus, 30).
unavailable(angus, 1).
unavailable(angus, 5).
unavailable(mona, 20).
unavailable(mona, 21).
unavailable(mona, 22).
unavailable(mona, 23).
unavailable(mona, 24).
unavailable(mona, 25).
unavailable(mona, 26).
unavailable(mona, 27).
unavailable(mona, 28).
unavailable(mona, 29).
unavailable(mona, 30).
unavailable(mona, 2).
unavailable(mona, 3).
unavailable(mona, 4).
unavailable(mona, 5).
unavailable(mona, 6).
unavailable(mona, 7).
unavailable(mona, 8).
unavailable(mona, 9).
unavailable(hans, 20).
unavailable(hans, 21).
unavailable(hans, 22).
unavailable(hans, 23).
unavailable(hans, 24).
unavailable(hans, 25).
unavailable(hans, 26).
unavailable(hans, 27).
unavailable(hans, 28).
unavailable(hans, 29).
unavailable(hans, 30).

prerequisite(ancient_greek, classics).
prerequisite(poetry, literature).

conflict(devi, xi).
conflict(mona, andrew).



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
#show schedule/3.
#show assign/3.
#show book/3.
