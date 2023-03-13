import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, TextIO
import pandas as pd
import re
from check_timetable import check_timetable
from input_validator import eprint, validate_input


def emit_program(json_data: Dict[str, Any], asp_file: TextIO, optimize: bool,msc=bool) -> None:

    # TODO: add code to write facts representing information captured in 'json_data'
    # to 'asp_file'
    # Use the signature provided in the coursework sheet 
    # Below is some code to get you started with defining slot and instance facts

    instance = ""

    # Reads the list of lecturers then uses the items in the list
    # to define a fact for each lecturer, i.e.,
    # lecturer(stevie). lecturer(lindsey). etc

    for lecturer in json_data["lecturer"]:
        instance+= "lecturer(" + str(lecturer).lower()  + ").\n"
    instance+="\n"

    # ... complete the rest

    for course in json_data["course"]:
        instance+= "course(" + str(course).lower()  + ").\n"
    instance+="\n"

    for i in range (1, json_data["slots"] + 1):
        instance+= "slot(" + str(i).lower()  + ").\n"
    instance+="\n"

    for i in range (1, json_data["rooms"] + 1):
        instance+= "room(" + str(i).lower()  + ").\n"
    instance+="\n"

    for i in range (1, json_data["labs"] + 1):
        instance+= "lab(" + str(i).lower()  + ").\n"
    instance+="\n"

    for room, capacity in json_data["capacity"].items():
        instance+= "capacity(" + str(room).lower() + ", " + str(capacity).lower() + ").\n"
    instance+="\n"

    for course, registeredAmount in json_data["registered"].items():
        instance+= "registered(" + str(course).lower() + ", " + str(registeredAmount).lower() + ").\n"
    instance+="\n"

    for lecturer, courses in json_data["can_teach"].items():
        for course in courses: 
            instance+= "can_teach(" + str(lecturer).lower() + ", " + str(course).lower() + ").\n"
    instance+="\n"

    for course, requiredSlots in json_data["required_slots"].items():
        instance+= "required_slots(" + str(course).lower() + ", " + str(requiredSlots).lower() + ").\n"
    instance+="\n"

    for lecturer, maxSlots in json_data["max_slots"].items():
        instance+= "max_slots(" + str(lecturer).lower() + ", " + str(maxSlots).lower() + ").\n"
    instance+="\n"

    for lecturer, unavailableSlots in json_data["unavailable"].items():
        for unavailableSlot in unavailableSlots: 
            instance+= "unavailable(" + str(lecturer).lower() + ", " + str(unavailableSlot).lower() + ").\n"
    instance+="\n"

    for course, preqCourses in json_data["prerequisite"].items():
        for preqCourse in preqCourses: 
            instance+= "prerequisite(" + str(course).lower() + ", " + str(preqCourse).lower() + ").\n"
    instance+="\n"

    for lecturer, conflictedLecturers in json_data["conflict"].items():
        for conflictedLecturer in conflictedLecturers: 
            instance+= "conflict(" + str(lecturer).lower() + ", " + str(conflictedLecturer).lower() + ").\n"
    instance+="\n"

    asp_file.write(instance)

    # TODO: add code to append your encoding of the rules described in 
    # step 2 to 'asp_file'

    problem = "\n\n"

    problem += "% (a) Write a choice rule for assigning lecturers \n"
    problem += "% courses conditional on their being able and available to teach it\n\n" 
    problem += "{assign(X, Y, Z)} :- can_teach(X, Y), not unavailable(X, Z), lecturer(X), course(Y), slot(Z).\n"
    problem += "\n"

    problem += "% (b) write a choice rules that schedules at most one course\n"
    problem += "% at most in one room at any one time.\n\n" 
    problem += "{schedule(X, Y, Z)} :- course(X), room(Y), slot(Z), not schedule(K, Y, Z), course(K).\n"
    problem += "\n"

    problem += "% (c) write a choice rules that books at most one courses\n"
    problem += "% in one lab at any one time.\n\n" 
    problem += "{book(X, Y, Z)} :- course(X), lab(Y), slot(Z), not book(K, Y, Z), course(K).\n"
    problem += "\n"

    problem += "% (d.i) write a rule using aggregate expression that gives the number\n"
    problem += "% of hours a lecturer is assigned to teach\n\n"
    problem += "total_assigned_hours(X, T) :- T = #count {Y, Z: assign(X, Y, Z)}, lecturer(X)."
    problem += "\n"

    problem += "% (d.ii) write a constraint using an aggregate expression that ensures that lecturers are not assigned\n"
    problem += "% to teach more hours than their maximum number of slots.\n\n" 
    problem += ":- T > M, total_assigned_slots(X, T), max_slots(X, M).\n"
    problem += "\n"

    problem += "% (e) write a constraint to ensure no course is scheduled in a room with not \n"
    problem += "% enough capacity. \n\n" 
    problem += ":- N > C, schedule(X, Y, Z), capacity(Y, C), registered(X, N).\n"
    problem += "\n"

    problem += "% (f) write a constraint that ensures courses are scheduled at most once at any specific slot. \n\n" 
    problem += ":- schedule(X, Y, Z), schedule(X, A, Z), Y != A.\n"
    problem += "\n"

    problem += "% (g) write a constraint that ensures  no lecturer is assigned\n"
    problem += "% two courses scheduled at the same time.\n\n"
    problem += ":- assign(X, Y, Z), assign(X, A, Z), Y != A.\n"
    problem += "\n"

    problem += "% (h) write a constraint that ensures that a course is not scheduled for more hours\n"
    problem += "% than it requires\n\n"
    problem += ":- T != S, T = #count {Z: schedule(X, Y, Z)}, required_slots(X, S).\n"
    problem += "\n"

    problem += "% (i.i) define a predicate scheduled/2 which holds\n"
    problem += "% if a course has been scheduled a time in the timetable\n\n"
    problem += "scheduled(X, Z) :- schedule(X, Y, Z).\n"
    problem += "\n"

    problem += "% (i.ii) write a constraint to ensure every assigned course is scheduled\n"
    problem += ":- assigned(C, S), not scheduled(C, S)."
    problem += "\n"

    problem += "% (j.i) define a predicate assigned/2 which holds\n"
    problem += "% if a course has been assigned a lecturer at a given time.\n\n"
    problem += "assigned(Y, Z) :- assign(X, Y, Z).\n"
    problem += "\n"

    problem += "% (j.ii) write a constraint that ensures every scheduled course\n"
    problem += "% assigned a lecturer \n\n"
    problem += ":- not assigned(C, S), scheduled(C, S)."
    problem += "\n"

    problem += "% (k) write a constraint that ensures no course is scheduled\n" 
    problem += "% before its prerequisites\n"
    problem += ":- scheduled(C1, S1), scheduled(C2, S2), S1 < S2, prerequisite(C1, C2)."
    problem += "\n"
 
    problem += "% (l) write a constraint that ensures no lecturer is assigned\n" 
    problem += "% to teach a course in a room immediately following another\n"
    problem += "% lecturer with which they have a conflict;\n"
    problem += "% lecturer with which they have a conflict;\n"
    problem += ":- schedule(Y, R, Z), schedule(B, R, C), conflict(A, X), assign(X, Y, Z), assign(A, B, C), Z + 1 == C."
    problem += "\n"
    
    problem += "% (m) write a constraint that ensures every course must have at least one\n" 
    problem += "% lab slot for every two slots not in a lab\n"
    problem += ":- N != S / 2, N = {book(X, Y, Z)}, required_slots(X, S)."
    problem += "\n"

    problem += "% (n) write a constraint that ensures no lab session for a course is booked\n" 
    problem += "% at the same time as its scheduled lecture.\n"
    problem += ":- book(C, _, Z), scheduled(C, Z)."
    problem += "\n"

    problem += "% (o.i) define a predicate scheduled_before/2 which holds\n"
    problem += "% if a course has been scheduled before a specific time in the timetable\n\n"
    problem += "scheduled_before(X, Z) :- scheduled(X, S), S < Z, slot(Z)."
    problem += "\n"

    problem += "% (o.ii) write a constraint that ensures no lab session for a course is booked\n" 
    problem += "% before at least one lecture has been scheduled.\n"
    problem += ":- not scheduled_before(X, Z), book(X, _, Z), course(X), slot(Z)."
    problem += "\n"

    # TODO: add your encoding of the optimization statements in step3. Only append these to the program
    # if the flag --optimize is true

    if optimize:
        problem += "% (p) write an optimization statement that minimizes the max \n"
        problem += "% number of hours lecturers is assisgned to teach\n\n"

        problem += "\n"

        problem += "% write a rule for assigned_courses/2 that gives the number\n"
        problem += "% of courses assigned to a lecturer.\n\n"

        problem += "\n"

        problem += "% (q) write an optimization statement that minimizes the number of courses\n"
        problem += "% lecturers are assigned\n\n"
        problem += "\n"

        if msc:
            problem += "% write a definition for allocated_rooms/2 which gives the number of rooms to\n"
            problem += "% which a course was allocated\n\n"
    
            problem += "\n"        
            problem += "% (r) write an optimization statement that minimizes the number of different rooms \n"
            problem += "% to which a course was allocated.\n\n"

            problem += "% (s) write an optimization statement that minimizes the gaps between scheduled times \n"
            problem += "% for any given course.\n\n"

    # You may wish to project more atoms in the computed answer set 
    # Do not remove #show schedule/3 nor #show assign/3 as these are
    # necessary for extracting and validating the solution later   

    problem += "#show schedule/3.\n"
    problem += "#show assign/3.\n"
    problem += "#show book/3.\n"

    asp_file.write(problem)

def solve(clingo_path: Path, asp_file: Path,  json_data: Dict[str, Any], output_csv_path: Path, optimize:bool) -> None:
    cmd = [str(clingo_path), str(asp_file)]
    #cmd = [str(clingo_path), "-n 0", str(asp_file)]
    print(f"Running asp solver command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True)
    clingo_output: str = result.stdout.decode('utf-8')

    with open(output_csv_path, "w") as output_csv:
        
        if clingo_output.find("UNKNOWN")!= -1:
            print(f"There is an error in the asp file.")
            output_csv.write("ERROR\n")
            return   
        
        if clingo_output.find("UNSATISFIABLE")!=-1:
           
            print(f"The progarm was UNSATISFIABLE: no timetable satisfies the given constraints.")
            output_csv.write("UNSAT\n")
            return

        print(f"The problem is SAT - a valid timetable exists!")

        output_csv.write("SAT\n")
        
        # Uncomment below for model extraction
        # The code below extracts the last solution present in 'clingo_output' and write the corresponding timetable
        # into a dataframe. It's not the most efficient but serves our needs

#        if clingo_output.rfind("Answer")!=-1:
#            opt_sol=clingo_output[clingo_output.rfind("Answer"): ]
#
#            if optimize:
#                stable_model_index = opt_sol.find("Optimization:")            
#            else:
#                stable_model_index = opt_sol.find("SATISFIABLE")
#            
#            stable_model = opt_sol[10:stable_model_index]
#       
#            atoms = stable_model.split()

#            Uncomment to see assign/3 and schdule/3 atoms in the answer set    
            #print(atoms)

#            schedule_pattern = r"\s*schedule\(\s*(.*)\s*,\s*(.*),\s*(.*)\)\s*"
#            assign_pattern = r"\s*assign\(\s*(.*)\s*,\s*(.*),\s*(.*)\)\s*"
#            book_pattern = r"\s*book\(\s*(.*)\s*,\s*(.*),\s*(.*)\)\s*"
#            
#            header = []
#            for  r in range(0, json_data["rooms"]):
#                header.append("Room " + str(r+1) )
#                header.append("")
#
#            for  r in range(0, json_data["labs"]):
#                header.append("Lab " + str(r+1) )
#                
#
#            df = pd.DataFrame(index=range(1,json_data["slots"]+1),columns=header)
#   
#            for a in atoms:
#                m1 = re.search(schedule_pattern, a, re.IGNORECASE)
#                if m1:
#                    c = str(m1.group(1))
#                    row = m1.group(3)
#                    col = "Room "+ m1.group(2)
#                    df.loc[int(row)][str(col)] = c
#
#            for a in atoms:
#                m1 = re.search(book_pattern, a, re.IGNORECASE)
#                if m1:
#                    c = str(m1.group(1))
#                    row = m1.group(3)
#                    col = "Lab "+ m1.group(2)
#                    df.loc[int(row)][str(col)] = c
#
#            for a in atoms:    
#                m2 = re.search(assign_pattern, a, re.IGNORECASE)
#                if m2:
#                    name = m2.group(1)
#                    course = str(m2.group(2))
#                    sl = int(m2.group(3))
#                    rr = df.loc[sl, :]
#                    inx=0
#                    for items in rr.iteritems():
#                        if items[1] == course:
#                            break
#                        inx+=1    
#
#                    df.loc[sl][inx+1]=name
#            
#            
#            try:
#                # print the timetable as a dataframe
#                print(df) 
#            except:
#                print("An exception occurred")

            
    # TODO: You can uncomment the following
    #  code, so that the correctness of your generated timetable is checked:

#    df.to_csv(output_csv_path)
#    if not check_timetable(json_data, output_csv_path):
#        eprint("The timetable was not valid.")
#        sys.exit(1)
#    print("The timetable was confirmed as valid.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("clingo_path", help="Path to the Clingo excutable", type=Path)
    parser.add_argument("input_file", help="JSON file describing instance to the problem to be solved.", type=Path)
    parser.add_argument("--output_csv", default="timetable.csv", help="Emit timetable to the given CSV file.", type=Path)
    parser.add_argument("--asp_file", default="timetable.lp", help="File to which generated asp program will be written.",
                        type=Path)
    parser.add_argument("--optimize", help="Find optimal solutions.",
                        action='store_true')
    parser.add_argument("--msc", help="For msc students:  minimize gaps between allocated slots for a course.",
                        action='store_true')
    args = parser.parse_args()

    clingo_path: Path = args.clingo_path
    input_file: Path = args.input_file
    output_csv: Path = args.output_csv
    asp_file: Path = args.asp_file
    optimize: bool = args.optimize
    msc: bool = args.msc

    if not input_file.is_file():
        eprint(f"The provided input file {input_file} does not exist.")
        sys.exit(1)

    json_data=validate_input(input_file)

    if json_data is None:
        sys.exit(1)

    emit_program(json_data=json_data, asp_file=open(asp_file, "w"), optimize=optimize,msc=msc)

  
    solve(clingo_path=clingo_path, asp_file=asp_file, json_data=json_data,
          output_csv_path=output_csv, optimize=optimize)


if __name__ == "__main__":
    main()
