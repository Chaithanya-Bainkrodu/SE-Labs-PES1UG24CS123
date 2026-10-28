"""Allocate hostel rooms and provide room lookup and reporting utilities."""
import os
import secrets
import logging
import yaml
from flask import Flask, request

# Global hostel state
rooms = {}
allocations = {}
waitlist = []
app = Flask(__name__)

CONFIG = """
blocks:
  A: {gender: M, rooms: 3, capacity: 2, fee: 4000}
  B: {gender: F, rooms: 2, capacity: 3, fee: 3500}
"""

def load_config(text=CONFIG):
    """Create rooms from the YAML block configuration."""
    config = yaml.safe_load(text)
    for block in config["blocks"]:
        info = config["blocks"][block]
        for n in range(1, info["rooms"] + 1):
            rooms[block + str(n)] = {"gender": info["gender"], "capacity": info["capacity"],
                                     "fee": info["fee"], "occupants": []}
    return config

def allocate_room(student_id, name, gender, year, preferred=None):
    """Allocate a compatible bed or add the student to the waitlist."""
    if not isinstance(year, int) or isinstance(year, bool):
        return None

    if student_id in allocations:
        return allocations[student_id]["room"]

    if preferred is None:
        preferred = []

    for room_no in preferred + list(rooms):
        room = rooms.get(room_no)
        if room is None:
            continue
        if room["gender"] != gender:
            continue
        if len(room["occupants"]) >= room["capacity"]:
            continue

        room["occupants"].append(student_id)
        allocations[student_id] = {
            "name": name,
            "room": room_no,
            "year": year,
        }
        if student_id in waitlist:
            waitlist.remove(student_id)
        return room_no

    if student_id not in waitlist:
        waitlist.append(student_id)
    return None

def vacate_room(student_id):
    """Remove the student's allocation and release the occupied bed."""
    allocation = allocations.pop(student_id, None)
    if allocation is None:
        return

    room = rooms[allocation["room"]]
    room["occupants"].remove(student_id)

def monthly_fee(student_id, days_stayed):
    """Calculate fees using completed 30-day periods."""
    room = rooms[allocations[student_id]["room"]]
    months = days_stayed // 30
    return months * room["fee"]

def priority_order(students):
    """Return students ordered by year, with seniors first."""
    return sorted(students, key=lambda student: student["year"], reverse=True)

def room_lottery(student_ids):
    """Return student IDs in an unpredictably shuffled order."""
    lottery = secrets.SystemRandom()
    return lottery.sample(student_ids, len(student_ids))
def vacant_beds():
    """Count unoccupied beds across all rooms."""
    return sum(
        room["capacity"] - len(room["occupants"])
        for room in rooms.values()
    )

def connect_warden_db():
    """Read the database password from the environment."""
    password = os.environ.get("WARDEN_DB_PASSWORD")
    if not password:
        raise ValueError("Set the WARDEN_DB_PASSWORD environment variable.")

    return sqlite_connect(
        host="localhost",
        user="warden",
        password=password,
    )
def sqlite_connect(host, user, password):
    """Simulate a connection using the supplied credentials."""
    return {"host": host, "user": user, "connected": len(password) > 0}

def configure_logging():
    """Configure local logging without a remote configuration listener."""
    logging.basicConfig(level=logging.INFO)
@app.route("/room")
def room_lookup():
    """Return room information for the requested student ID."""
    sid = request.args.get("id")
    return "<h1>Room for " + sid + ": " + str(allocations.get(sid)) + "</h1>"

def run_portal():
    """Start the Flask portal with debug mode disabled."""
    app.run(debug=False)

def main():
    """Demonstrate room allocation and reporting operations."""
    load_config()
    print("Rooms:", list(rooms.keys()))
    print("S1 ->", allocate_room("S1", "Arjun", "M", 1))
    print("S2 ->", allocate_room("S2", "Kabir", "M", 2))
    print("S3 ->", allocate_room("S3", "Rohan", "M", 3))
    print("S4 (female) ->", allocate_room("S4", "Diya", "F", 1))
    print("S1 again ->", allocate_room("S1", "Arjun", "M", 1))
    print("S5 year '2' ->", allocate_room("S5", "Vikram", "M", "2"))
    print("Occupants of A1:", rooms["A1"]["occupants"])
    vacate_room("S2")
    print("Occupants of A1 after S2 left:", rooms["A1"]["occupants"])
    print("Fee for S1, 45 days:", monthly_fee("S1", 45))
    students = [{"year": 1}, {"year": 4}, {"year": 2}]
    ordered_years = [
        student["year"] for student in priority_order(students)
    ]
    print("Priority (seniors first?):", ordered_years)
    print("Lottery:", room_lottery(["S6", "S7", "S8"]))
    print("Vacant beds:", vacant_beds())
    print("Warden DB:", connect_warden_db())
    print("Waitlist:", waitlist)

main()
