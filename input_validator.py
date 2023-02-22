import json
import sys

from pathlib import Path
from typing import Any, Dict, Optional


def eprint(message: str) -> None:
    sys.stderr.write(message + "\n")

def validate_input(input_file: Path) -> Optional[Dict[str, Any]]:

    try:
        def dict_raise_on_duplicates(ordered_pairs):
            """Reject duplicate keys."""
            d = {}
            for k, v in ordered_pairs:
                if k in d:
                    raise ValueError("duplicate key: %r" % (k,))
                else:
                    d[k] = v
            return d
        json_data: Dict[str, Any] = json.load(open(input_file), object_pairs_hook=dict_raise_on_duplicates)
    except json.decoder.JSONDecodeError as json_error:
        eprint(f"Ill-formed JSON input at {json_error.lineno},{json_error.colno}")
        eprint(f"  {json_error.msg}")
        return None
    except ValueError as value_error:
        eprint(f"Value error while loading JSON data")
        eprint(f"  {value_error}")
        return None

    def all_different_strings(should_be_list_of_strings: Any):
        if not isinstance(should_be_list_of_strings, list):
            return None
        observed_strings: Set[str] = set()
        for item in should_be_list_of_strings:
            if not isinstance(item, str) or item in observed_strings:
                return None
            observed_strings.add(item)
        return True

    if "lecturer" not in json_data:
        eprint("No lecturers specified.")
        return None

    if not all_different_strings(json_data["lecturer"]):
        eprint("Lecturers should be a list of distinct strings.")
        return None
    lecturers: List[str] = json_data["lecturer"]

    if "course" not in json_data:
        eprint("No courses specified.")
        return None

    if not all_different_strings(json_data["course"]):
        eprint("Courses should be a list of distinct strings.")
        return None
    courses: List[str] = json_data["course"]

    for lecturer in lecturers:
        if lecturer in courses:
            eprint(f"'{lecturer}' cannot be both a course and a lecturer.")
            return None

    if "slots" not in json_data:
        eprint("No number of slots provided.")
        return None

    if not isinstance(json_data["slots"], int) or json_data["slots"] <= 0:
        eprint("Number of slots must be a positive integer.")
        return None

    if "rooms" not in json_data:
        eprint("No number of rooms provided.")
        return None

    if not isinstance(json_data["rooms"], int) or json_data["rooms"] <= 0:
        eprint("Number of rooms must be an integer.")
        return None
    
    if "labs" not in json_data:
        eprint("No number of labs provided.")
        return None

    if not isinstance(json_data["labs"], int) or json_data["labs"] <= 0:
        eprint("Number of labs must be an integer.")
        return None

    if "capacity" not in json_data:
        eprint("No room capacity specified.")
        return None

    for room in json_data["capacity"]:
        if not isinstance(int(room), int) or int(room) <= 0:
            eprint("Capacity must be an integer.")
            return None
        r = json_data["rooms"]
        if int(room) not in range(1,r+1):
            eprint(f"The room number must be less or equal to '{r}'.")
            return None
        if not isinstance(json_data["capacity"][room],int) or json_data["capacity"][room] <= 0:
            eprint(f"Capacity of rooms must be a positive integer; found '{room}'")
            return None

        for room in (1,json_data["rooms"]):
            if str(room) not in json_data["capacity"]:
                eprint(f"No room capacity provided for room '{room}'.")
                return None
  
        if "registered" not in json_data:
            eprint("No number of registered students specified.")
            return None

        for course in json_data["registered"]:
            if course not in courses:
                eprint(f"Each course with 'registered' students must be a course; found '{course}'.")
                return None
            reg_students = json_data["registered"][course]
            if not isinstance(reg_students, int) or reg_students <= 0:
                eprint(f"Number of registered students for each course must be a positive integer; found {reg_students} for {course}")
                return None
        for course in courses:
            if course not in json_data["registered"]:
                eprint(f"Course {course} missing number of registered students")
                return None


    if "can_teach" not in json_data:
        eprint("Missing property: 'can_teach'.")
        return None
    for lecturer in json_data["can_teach"]:
        if lecturer not in lecturers:
            eprint(f"Each 'can_teach' entry must be a lecturer; found '{lecturer}'.")
            return None
        can_teach_courses = json_data["can_teach"][lecturer]
        if not isinstance(can_teach_courses, list):
            eprint("The courses a lecturer can teach must be a list of strings.")
            return None
        seen_courses = []
        for course in can_teach_courses:
            if not isinstance(course, str):
                eprint("The courses a lecturer can teach must be a list of strings.")
                return None
            if course in seen_courses:
                eprint(f"Duplicate 'can_teach' entry under '{lecturer}' for '{course}'.")
                return None
            if course not in courses:
                eprint(f"Unknown course, '{course}' under list of courses that '{lecturer}' can teach.")
                return None
            seen_courses.append(course)
    if len(json_data["can_teach"]) != len(lecturers):
        eprint("Mismatch between given lecturers and lecturers represented under 'can_teach'.")
        return None

    if "required_slots" not in json_data:
        eprint("Missing property: 'required_slots'.")
        return None
    for course in json_data["required_slots"]:
        if course not in courses:
            eprint(f"Each 'required_slots' entry must be a course; found '{course}'.")
            return None
        required_slots = json_data["required_slots"][course]
        if not isinstance(required_slots, int) or required_slots <= 0:
            eprint(f"Required slots for each course must be a positive integer; found {required_slots} for {course}")
            return None
    if len(json_data["required_slots"]) != len(courses):
        eprint("Mismatch between given courses and courses represented under 'required_slots'.")
        return None

    if "max_slots" not in json_data:
        eprint("Missing property: 'max_slots'.")
        return None
    for lecturer in json_data["max_slots"]:
        if lecturer not in lecturers:
            eprint(f"Each 'max_slots' entry must be a lecturer; found '{lecturer}'.")
            return None
        max_slots = json_data["max_slots"][lecturer]
        if not isinstance(max_slots, int) or max_slots <= 0:
            eprint(f"Max slots for each lecturer must be a positive integer; found {max_slots} for {lecturer}")
            return None
    if len(json_data["max_slots"]) != len(lecturers):
        eprint("Mismatch between given lecturers and lecturers represented under 'max_slots'.")
        return None

    if "unavailable" not in json_data:
        eprint("Missing property: 'unavailable'.")
        return None
    for lecturer in json_data["unavailable"]:
        if lecturer not in lecturers:
            eprint(f"Each 'unavailable' entry must be a lecturer; found '{lecturer}'.")
            return None
        unavailable = json_data["unavailable"][lecturer]
        if not isinstance(unavailable, list):
            eprint(f"Expected a list of integers under 'unavailable' for {lecturer}")
            return None
        observed_slot = set()
        for slot in unavailable:
            if not isinstance(slot, int) or slot <= 0 or slot > json_data["slots"]:
                eprint(f"Each unavailable slot for {lecturer} should be an integer in the range [1, "
                       f"{json_data['slots']}]")
                return None
            if slot in observed_slot:
                eprint(f"Duplicate unavailable slot {slot} for {lecturer}")
                return None
            observed_slot.add(slot)
    if len(json_data["unavailable"]) != len(lecturers):
        eprint("Mismatch between given lecturers and lecturers represented under 'unavailable'.")
        return None
    
    if "prerequisite" not in json_data:
        eprint("Missing property: 'prerequisite'.")
        return None
    for course in json_data["prerequisite"]:
        if course not in courses:
            eprint(f"Each 'prerequisite' entry must be a course; found '{course}'.")
            return None
        prerequisites = json_data["prerequisite"][course]
        if not isinstance(prerequisites, list):
            eprint("The prerequisites of a course must be a list of strings.")
            return None
        seen_prerequisite = []
        for prerequisite in prerequisites:
            if not isinstance(course, str):
                eprint("The prerequisites of a course must be a list of strings.")
                return None
            if prerequisite == course:
                eprint(f"Course '{course}' cannot have itself as a prerequisite.")
                return None
            if prerequisite in seen_prerequisite:
                eprint(f"Duplicate 'prerequisite' entry under '{course}' for '{prerequisite}'.")
                return None
            if prerequisite not in prerequisites:
                eprint(f"Unknown prequisite, '{prerequisite}' for {course}")
                return None
            seen_prerequisite.append(prerequisite)
    if len(json_data["prerequisite"]) != len(courses):
        eprint("Mismatch between given courses and courses represented under 'prerequisite'.")
        return None
    
    if "conflict" not in json_data:
        eprint("Missing property: 'conflict'.")
        return None
    for lecturer in json_data["conflict"]:
        if lecturer not in lecturers:
            eprint(f"Each 'conflict' entry must be a lecturer; found '{lecturer}'.")
            return None
        conflicts = json_data["conflict"][lecturer]
        if not isinstance(conflicts, list):
            eprint("The conflicts a lecturer can have must be a list of strings.")
            return None
        seen_conflicts = []
        for conflict in conflicts:
            if not isinstance(course, str):
                eprint("The conflicts a lecturer can have must be a list of strings.")
                return None
            if conflict == lecturer:
                eprint(f"{lecturer} cannot have themselves as a conflict.")
                return None
            if conflict in seen_conflicts:
                eprint(f"Duplicate 'conflict' entry under '{lecturer}' for '{course}'.")
                return None
            if conflict not in lecturers:
                eprint(f"Unknown lecturer for conflict, '{conflict}' for {lecturer}.")
                return None
            seen_conflicts.append(conflict)
    if len(json_data["conflict"]) != len(lecturers):
        eprint("Mismatch between given lecturers and lecturers represented under 'conflict'.")
        return None
    
    

    return json_data
#if __name__ == '__main__':
#   validate_input("SAT/2c.json")
