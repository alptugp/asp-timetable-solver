import argparse
import csv
import sys

from pathlib import Path
from typing import Any, Dict
from input_validator import eprint
from input_validator import validate_input

def read_row(csv_file, row_num):
    with open(csv_file, "r") as infile:
        r = csv.reader(infile)
        for i in range(row_num-1):
            next(r) 
        row = next(r) 
        return row

def check_timetable(requirements: Dict[str, Any], timetable: Path) -> bool:
    rooms: int = requirements["rooms"]
    labs: int = requirements["labs"]
    cells_per_row: int = 2 * rooms + 1 + labs
    slots: int = requirements["slots"]

    
    slots_per_lecturer: Dict[str, int] = {}
    
    for lecturer in requirements["lecturer"]:
        slots_per_lecturer[lecturer] = 0

    slots_per_course: Dict[str, int] = {}
    slots_per_lab: Dict[str, int] = {}
    
    for course in requirements["course"]:
        slots_per_course[course] = 0
        slots_per_lab[course] = 0

    overall_seen_courses = []
    finished_courses = []
    

    with open(timetable, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        last_row: int = 0
        for i, row in enumerate(reader):
            last_row = i
            if len(row) != cells_per_row:
                eprint(f"CSV row has wrong number of cells: {len(row)}, expected {cells_per_row}: {', '.join(row)}")
                return False
            if i == 0:
                # Checking if room section is valid.
                for j in range(1, 2*rooms+1):
                    if j % 2 == 0:
                        if row[j].strip() != "":
                            eprint(f"Column {j} of row 0 should be empty")
                            return False
                    else:
                        if row[j].strip() != f"Room {int(j/2+1)}":
                            eprint(f"Column {j} of row 0 should contain 'Room {int(j/2)}'")
                            return False
                # Checking if labs are valid
                l = 1
                for j in range(2*rooms+1, 2*rooms+1+labs):
                    if row[j].strip() != f"Lab {l}":
                        eprint(f"Column {j} of row 0 should contain 'Lab {l}'")
                        return False
                    l += 1

            else:
                if i > slots:
                    eprint(f"CSV has too many rows; expected {slots} rows.")
                    return False
                if row[0].strip() != str(i):
                    eprint(f"Column 0 of row {i} should contain '{i }'")
                    return False
                
                seen_courses = set()
                seen_lecturers = set()
                
                # Checking rooms.
                for j in range(1, 2*rooms+1, 2):
                    course = row[j].strip()
                    lecturer = row[j + 1].strip()

                    if course == "":
                        if lecturer != "":
                            eprint(f"Slot indicated as 'Free' at row {i} column {j}, but a lecturer is provided in "
                                   f"column {j + 1}")
                            return False
                    else:
                        if lecturer == "":
                            eprint(f"Lecturer assigned in row {i}"
                                f"column {j + 1}, but a no course is schdeduled in column {j}")
                            return False
                        if course in finished_courses:
                            eprint(f"Course {course} should have finished because it is a prequisite to another module that has started")
                            return False
                        if course not in requirements["course"]:
                            eprint(f"Unknown course {course} at row {i} column {j}")
                            return False
                        if lecturer not in requirements["lecturer"]:
                            eprint(f"Unknown lecturer {lecturer} at row {i} column {j + 1}")
                            return False

                        if course in seen_courses:
                            eprint(
                                f"Row {i} column {j}: Course {course} already scheduled to be taught during this slot")
                            return False
                        if lecturer in seen_lecturers:
                            eprint(
                                f"Row {i} column {j + 1}: Lecturer {lecturer} already scheduled to teach during this "
                                f"slot")
                            return False
                        
                        capacity = requirements["capacity"][str(int(j/2)+1)]
                        registered = requirements["registered"][course]
                             
                        if registered > capacity:
                            eprint(
                                f"Row {i} column {j}: Course {course} allocated room {j/2} with not enough capacity")
                            return False
                        
                        slots_per_course[course] += 1
                        slots_per_lecturer[lecturer] += 1

                        if course not in requirements["can_teach"][lecturer]:
                            eprint(f"Lecturer {lecturer} cannot teach {course}, as scheduled by row {i} columns {j} "
                                   f"and {j + 1}")
                            return False
                        
                        if i in requirements["unavailable"][lecturer]:
                            eprint(f"Lecturer {lecturer} is not available during slot {i}, but is scheduled for "
                                   f"this slot according to row {i} column {j + 1}")
                            return False
                        

                        seen_courses.add(course)
                        if course not in overall_seen_courses: overall_seen_courses.append(course)
                        seen_lecturers.add(lecturer)

                        if not set(requirements["prerequisite"][course]).issubset(overall_seen_courses):
                            eprint(f"Course {course} cannot begin because prerequisites are not met")
                            return False
                        for preq in requirements["prerequisite"][course]:
                            if preq not in finished_courses: finished_courses.append(preq)

                        # open next line
                        next_row = read_row(timetable, i+1)
                        next_lecturer = next_row[j+1].strip()
                        if next_lecturer in requirements["lecturer"]:
                            if lecturer in requirements["conflict"][next_lecturer]:
                                eprint(f"{next_lecturer} has a conflict with {lecturer} and is scheduled to teach directly after them")
                                return False
                        
                # Checking if labs are valid
                for j in range(2*rooms+1, 2*rooms+1+labs):
                    lab_entry = row[j].strip()
                    if lab_entry == "":
                        continue
                    if lab_entry not in requirements["course"]:
                        eprint(f"Unknown course {lab_entry} at row {i} column {j}")
                        return False
                    if lab_entry not in overall_seen_courses:
                        eprint(f"Course {lab_entry} has lab scheduled before first teaching slot")
                        return False
                    if lab_entry in seen_courses:
                        eprint(
                            f"Row {i} column {j}: {lab_entry}: teaching and lab scheduled at the same time")
                        return False
                    
                    slots_per_lab[lab_entry] += 1
                        
        if last_row != slots:
            eprint(f"CSV has too few rows; expected {slots} rows.")

        for course in requirements["course"]:
            scheduled_slots = slots_per_course[course]
            required_slots = requirements["required_slots"][course]
            required_lab_slots = int(requirements["required_slots"][course]/2)
            scheduled_lab_slots = slots_per_lab[course]

            if scheduled_slots != required_slots:
                eprint(f"Course {course} scheduled for {scheduled_slots} slot(s), but {required_slots} slots(s) were "
                       f"required.")
                return False
            
            if scheduled_lab_slots != required_lab_slots:
                eprint(f"Course {course} has {scheduled_lab_slots} scheduled lab slot(s), but {required_lab_slots} slot(s) were required.")
                return False
            

        for lecturer in requirements["lecturer"]:
            scheduled_slots = slots_per_lecturer[lecturer]
            max_slots = requirements["max_slots"][lecturer]
            if scheduled_slots > max_slots:
                eprint(f"Lecturer {lecturer} scheduled for {scheduled_slots} slot(s), which is more than their maximum "
                       f"of {max_slots} slots(s).")
                return False

    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("requirements", help="JSON file describing the timetable requirements.", type=Path)
    parser.add_argument("timetable", help="CSV file containing a timetable to be checked against the requirements.",
                        type=Path)
    args = parser.parse_args()

    requirements = args.requirements
    timetable = args.timetable

    if not requirements.is_file():
        eprint(f"The requirements file {requirements} does not exist.")
        sys.exit(1)

    if not timetable.is_file():
        eprint(f"The timetable file {timetable} does not exist.")
        sys.exit(1)

    json_data = validate_input(requirements)
    if json_data is None:
        sys.exit(1)

    print("Validating timetable.")
    if check_timetable(json_data, timetable):
        print("Timetable is valid.")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
