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

    instance = ""

    # step 1: set of ASP facts
    can_teach = json_data["can_teach"]
    max_slots = json_data["max_slots"]
    unavailable = json_data["unavailable"]
    conflict = json_data["conflict"]
    for l in json_data["lecturer"]:
        lec = l.lower()
        instance+= "lecturer(" + lec  + ").\n"
        instance+= "max_slots(" + lec  + "," + str(max_slots[l]) + ").\n"
        for c in can_teach[l]:
            instance+= "can_teach(" + lec  + "," + str(c).lower()  + ").\n"
        for s in unavailable[l]:
            instance+= "unavailable(" + lec  + "," + str(s) + ").\n"
        for c in conflict[l]:
            instance+= "conflict(" + lec  + "," + str(c).lower()  + ").\n"
        instance += "\n"
    instance+="\n"

    registered = json_data["registered"]
    required_slots = json_data["required_slots"]
    prerequisities = json_data["prerequisite"]
    for c in json_data["course"]:
        course = str(c)
        instance+= "course(" + course  + ").\n"
        instance+= "registered(" + course  + "," + str(registered[c]) + ").\n"
        instance+= "required_slots(" + course  + "," + str(required_slots[c]) + ").\n"
        for p in prerequisities[c]:
            instance+= "prerequisite(" + course  + "," + str(p).lower()  + ").\n"
        instance += "\n"
    instance+="\n"

    num_slots = json_data["slots"]
    instance+= "slot(1.." + str(num_slots) + ").\n"
    instance+="\n"

    num_rooms = json_data["rooms"]
    instance+= "room(1.." + str(num_rooms) + ").\n"
    for i in range(1, num_rooms + 1):
        instance+= "capacity(" + str(i) + "," + str(json_data["capacity"][str(i)]) + ").\n"
    instance+="\n"

    num_labs = json_data["labs"]
    instance+= "lab(1.." + str(num_labs) + ").\n"
    instance+="\n"

    asp_file.write(instance)

    problem = "\n\n"
    # step 2: set of ASP rules
    problem += "% (a) Write a choice rule for assigning lecturers \n"
    problem += "% courses conditional on their being able and available to teach it\n\n" 
    problem += "{ assign(L, C, S) } :- lecturer(L), course(C), slot(S), can_teach(L, C), not unavailable(L, S).\n\n"

    problem += "\n"

    problem += "% (b) write a choice rules that schedules at most one course\n"
    problem += "% at most in one room at any one time.\n\n"
    problem += "0 { schedule(C, R, S) : course(C) } 1 :- room(R), slot(S) .\n\n"

    problem += "\n"

    problem += "% (c) write a choice rules that books at most one courses\n"
    problem += "% in one lab at any one time.\n\n" 
    problem += "0 { book(C, L, S) : course(C) } 1 :-  lab(L), slot(S).\n\n"

    problem += "\n"

    problem += "% (d.i) write a rule using aggregate expression that gives the number\n"
    problem += "% of hours a lecturer is assigned to teach\n\n"
    problem += "assigned_slots(L, N) :- lecturer(L), { assign(L, _, S) } = N.\n\n"

    problem += "\n"

    problem += "% (d.ii) write a constraint using an aggregate expression that ensures that lecturers are not assigned\n"
    problem += "% to teach more hours than their maximum number of slots.\n\n" 
    problem += ":- lecturer(L), max_slots(L, M), assigned_slots(L, N), N > M.\n\n"

    problem += "\n"

    problem += "% (e) write a constraint to ensure no course is scheduled in a room with not \n"
    problem += "% enough capacity. \n\n" 
    problem += ":- course(C), room(R), schedule(C, R, _), capacity(R, CA), registered(C, N), N > CA.\n\n"

    problem += "\n"

    problem += "% (f) write a constraint that ensures courses are scheduled at most once at any specific slot. \n\n" 
    problem += ":- room(R1), room(R2), course(C), slot(S), R1 != R2, schedule(C, R1, S), schedule(C, R2, S).\n\n"

    problem += "\n"

    problem += "% (g) write a constraint that ensures  no lecturer is assigned\n"
    problem += "% two courses scheduled at the same time.\n\n"
    problem += ":- course(C1), course(C2), lecturer(L), slot(S), C1 != C2, assign(L, C1, S), assign(L, C2, S).\n\n"

    problem += "\n"

    problem += "% (h) write a constraint that ensures that a course is not scheduled for more hours\n"
    problem += "% than it requires\n\n"
    problem += ":- course(C), required_slots(C, RS), #count { S : schedule(C, _, S) } != RS.\n\n"

    problem += "\n"

    problem += "% (i.i) define a predicate scheduled/2 which holds\n"
    problem += "% if a course has been scheduled a time in the timetable\n\n"
    problem += "scheduled(C, S) :- course(C), slot(S), schedule(C, _, S).\n\n"

    problem += "\n"

    problem += "% (i.ii) write a constraint to ensure every assigned course is scheduled\n"
    problem += ":- assign(_, C, S), not scheduled(C, S).\n\n"

    problem += "\n"

    problem += "% (j.i) define a predicate assigned/2 which holds\n"
    problem += "% if a course has been assigned a lecturer at a given time.\n\n"
    problem += "assigned(C, S) :- course(C), slot(S), assign(_, C, S).\n\n"

    problem += "\n"

    problem += "% (j.ii) write a constraint that ensures every scheduled course\n"
    problem += "% assigned a lecturer \n\n"
    problem += ":- scheduled(C, S), not assigned(C, S).\n\n"

    problem += "\n"

    problem += "% (k) write a constraint that ensures no course is scheduled\n" 
    problem += "% before its prerequisites\n"
    problem += ":- course(C), course(P), prerequisite(C, P), scheduled(P, S1), scheduled(C, S2), S1 >= S2.\n\n"
    problem += "\n"
 
    problem += "% (l) write a constraint that ensures no lecturer is assigned\n" 
    problem += "% to teach a course in a room immediately following another\n"
    problem += "% lecturer with which they have a conflict;\n"
    problem += ":- assign(L1, C1, S1), assign(L2, C2, S2), S1 + 1 == S2, room(R), schedule(C1, R, S1), schedule(C2, R, S2), conflict(L2, L1).\n\n"
    problem += "\n"
    
    problem += "% (m) write a constraint that ensures every course must have at least one\n" 
    problem += "% lab slot for every two slots not in a lab\n"
    problem += ":- course(C), LS = { book(C, _, _) }, required_slots(C, NLS),  NLS / 2 != LS.\n\n"
    
    problem += "\n"

    problem += "% (n) write a constraint that ensures no lab session for a course is booked\n" 
    problem += "% at the same time as its scheduled lecture.\n"
    problem += ":- course(C), schedule(C, _, S), book(C, _, S).\n\n"
    
    problem += "\n"

    problem += "% (o.i) define a predicate scheduled_before/2 which holds\n"
    problem += "% if a course has been scheduled before a specific time in the timetable\n\n"
    problem += "scheduled_before(C, S) :- slot(S), slot(SB), scheduled(C, SB), SB < S.\n\n"

    problem += "\n"

    problem += "% (o.ii) write a constraint that ensures no lab session for a course is booked\n" 
    problem += "% before at least one  lecture has been scheduled.\n"
    problem += ":- course(C), book(C, _, S), not scheduled_before(C, S).\n\n"
    
    problem += "\n"
    
    # step 3: optimisation
    if optimize:
        problem += "% (p) write an optimization statement that minimizes the max \n"
        problem += "% number of hours lecturers is assisgned to teach\n\n"
        problem += "#minimize { N@1 : assigned_slots(_, N) }.\n\n"

        problem += "\n"

        problem += "% write a rule for assigned_courses/2 that gives the number\n"
        problem += "% of courses assigned to a lecturer.\n\n"
        problem += "assigned_courses(L, N) :- lecturer(L), course(C), { assign(L, C, _) } = N.\n\n"

        problem += "\n"

        problem += "% (q) write an optimization statement that minimizes the number of courses\n"
        problem += "% lecturers are assigned\n\n"
        problem += "#minimize { M@2 : assigned_courses(_, M) }.\n\n"
        problem += "\n"


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

        if clingo_output.rfind("Answer")!=-1:
            opt_sol=clingo_output[clingo_output.rfind("Answer"): ]

            if optimize:
                stable_model_index = opt_sol.find("Optimization:")            
            else:
                stable_model_index = opt_sol.find("SATISFIABLE")
            
            stable_model = opt_sol[10:stable_model_index]
       
            atoms = stable_model.split()
           #Uncomment to see assign/3 and schdule/3 atoms in the answer set    
           #print(atoms)
            schedule_pattern = r"\s*schedule\(\s*(.*)\s*,\s*(.*),\s*(.*)\)\s*"
            assign_pattern = r"\s*assign\(\s*(.*)\s*,\s*(.*),\s*(.*)\)\s*"
            book_pattern = r"\s*book\(\s*(.*)\s*,\s*(.*),\s*(.*)\)\s*"
            
            header = []
            for  r in range(0, json_data["rooms"]):
                header.append("Room " + str(r+1) )
                header.append("")

            for  r in range(0, json_data["labs"]):
                header.append("Lab " + str(r+1) )
                

            df = pd.DataFrame(index=range(1,json_data["slots"]+1),columns=header)
   
            for a in atoms:
                m1 = re.search(schedule_pattern, a, re.IGNORECASE)
                if m1:
                    c = str(m1.group(1))
                    row = m1.group(3)
                    col = "Room "+ m1.group(2)
                    df.loc[int(row)][str(col)] = c

            for a in atoms:
                m1 = re.search(book_pattern, a, re.IGNORECASE)
                if m1:
                    c = str(m1.group(1))
                    row = m1.group(3)
                    col = "Lab "+ m1.group(2)
                    df.loc[int(row)][str(col)] = c

            for a in atoms:    
                m2 = re.search(assign_pattern, a, re.IGNORECASE)
                if m2:
                    name = m2.group(1)
                    course = str(m2.group(2))
                    sl = int(m2.group(3))
                    rr = df.loc[sl, :]
                    inx=0
                    for items in rr.iteritems():
                        if items[1] == course:
                            break
                        inx+=1    

                    df.loc[sl][inx+1]=name
            
            
            try:
                # print the timetable as a dataframe
                print(df) 
            except:
                print("An exception occurred")
           
   # TODO: You can uncomment the following
   #  code, so that the correctness of your generated timetable is checked:
    df.to_csv(output_csv_path)
    if not check_timetable(json_data, output_csv_path):
        eprint("The timetable was not valid.")
        sys.exit(1)
    print("The timetable was confirmed as valid.")


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
