lecturer(stevie).
max_slots(stevie,8).
can_teach(stevie,java).
can_teach(stevie,symbolic).
unavailable(stevie,1).
unavailable(stevie,5).
unavailable(stevie,6).
unavailable(stevie,9).
conflict(stevie,lindsey).

lecturer(lindsey).
max_slots(lindsey,12).
can_teach(lindsey,logic).
can_teach(lindsey,symbolic).
unavailable(lindsey,6).
unavailable(lindsey,9).

lecturer(mick).
max_slots(mick,8).
can_teach(mick,logic).
can_teach(mick,java).
unavailable(mick,5).
unavailable(mick,6).
unavailable(mick,10).
unavailable(mick,11).
conflict(mick,stevie).


course(java).
registered(java,30).
required_slots(java,8).

course(symbolic).
registered(symbolic,25).
required_slots(symbolic,6).
prerequisite(symbolic,logic).

course(logic).
registered(logic,35).
required_slots(logic,3).


slot(1..15).

room(1..3).
capacity(1,50).
capacity(2,45).
capacity(3,85).

lab(1..2).



% (a) Write a choice rule for assigning lecturers 
% courses conditional on their being able and available to teach it

{ assign(L, C, S) } :- lecturer(L), course(C), slot(S), can_teach(L, C), not unavailable(L, S).


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

scheduled(C, S) :- course(C), slot(S), schedule(C, _, S).


% (i.ii) write a constraint to ensure every assigned course is scheduled
:- assign(_, C, S), not scheduled(C, S).


% (j.i) define a predicate assigned/2 which holds
% if a course has been assigned a lecturer at a given time.

assigned(C, S) :- course(C), slot(S), assign(_, C, S).


% (j.ii) write a constraint that ensures every scheduled course
% assigned a lecturer 

:- scheduled(C, S), not assigned(C, S).


% (k) write a constraint that ensures no course is scheduled
% before its prerequisites
:- course(C), course(P), prerequisite(C, P), scheduled(P, S1), scheduled(C, S2), S1 >= S2.


% (l) write a constraint that ensures no lecturer is assigned
% to teach a course in a room immediately following another
% lecturer with which they have a conflict;
:- assign(L1, C1, S1), assign(L2, C2, S2), S1 + 1 == S2, room(R), schedule(C1, R, S1), schedule(C2, R, S2), conflict(L2, L1).


% (m) write a constraint that ensures every course must have at least one
% lab slot for every two slots not in a lab
:- course(C), LS = { book(C, _, _) }, required_slots(C, NLS),  NLS / 2 != LS.


% (n) write a constraint that ensures no lab session for a course is booked
% at the same time as its scheduled lecture.
:- course(C), schedule(C, _, S), book(C, _, S).


% (o.i) define a predicate scheduled_before/2 which holds
% if a course has been scheduled before a specific time in the timetable

scheduled_before(C, S) :- slot(S), slot(SB), scheduled(C, SB), SB < S.


% (o.ii) write a constraint that ensures no lab session for a course is booked
% before at least one  lecture has been scheduled.
:- course(C), book(C, _, S), not scheduled_before(C, S).


#show schedule/3.
#show assign/3.
#show book/3.
