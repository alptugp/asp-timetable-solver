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
lab(2).

capacity(1, 50).
capacity(2, 45).
capacity(3, 85).

registered(java, 30).
registered(symbolic, 25).
registered(logic, 35).

can_teach(stevie, java).
can_teach(stevie, symbolic).
can_teach(lindsey, logic).
can_teach(lindsey, symbolic).
can_teach(mick, logic).
can_teach(mick, java).

required_slots(java, 8).
required_slots(symbolic, 6).
required_slots(logic, 3).

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

conflict(stevie, lindsey).
conflict(mick, stevie).



% (a) Write a choice rule for assigning lecturers 
% courses conditional on their being able and available to teach it

{assign(X, Y, Z)} :- can_teach(X, Y), not unavailable(X, Z), lecturer(X), course(Y), slot(Z).

% (b) write a choice rules that schedules at most one course
% at most in one room at any one time.

0 { schedule(C, R, S) : course(C) } 1 :- room(R), slot(S) .


% (c) write a choice rules that books at most one courses
% in one lab at any one time.

0 { book(C, L, S) : course(C) } 1 :-  lab(L), slot(S).


% (d.i) write a rule using aggregate expression that gives the number
% of hours a lecturer is assigned to teach

assigned_slots(L, N) :- lecturer(L), { assign(L, _, S) } = N.


% (d.ii) write a constraint using an aggregate expression that ensures that lecturers are not assigned
% to teach more hours than their maximum number of slots.

:- lecturer(L), max_slots(L, M), assigned_slots(L, N), N > M.


% (e) write a constraint to ensure no course is scheduled in a room with not 
% enough capacity. 

:- course(C), room(R), schedule(C, R, _), capacity(R, CA), registered(C, N), N > CA.


% (f) write a constraint that ensures courses are scheduled at most once at any specific slot. 

:- room(R1), room(R2), course(C), slot(S), R1 != R2, schedule(C, R1, S), schedule(C, R2, S).


% (g) write a constraint that ensures  no lecturer is assigned
% two courses scheduled at the same time.

:- course(C1), course(C2), lecturer(L), slot(S), C1 != C2, assign(L, C1, S), assign(L, C2, S).


% (h) write a constraint that ensures that a course is not scheduled for more hours
% than it requires

:- course(C), required_slots(C, RS), #count { S : schedule(C, _, S) } != RS.


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
