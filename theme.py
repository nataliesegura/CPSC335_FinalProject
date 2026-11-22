"""theme.py - GridRestore: restoring power after a windstorm.
Turns the theme's data into the inputs that core.py expects."""
import json, os

THEME = "GridRestore"
TITLE = "GridRestore"
TAGLINE = "Power restoration planner after a Southern California windstorm"
DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "outages.json")

RECORD = "outage"                 # what one record is called
ID_FIELD = "outage_id"
LOOKUP_FIELD, LOOKUP_LABEL = "meter_id", "Customer meter ID"
COLUMNS = ["outage_id", "meter_id", "site_type", "customers", "repair_hours", "reported", "area"]

SORT_LABEL = "Report time"
SEARCH_PROMPT = "Show outages reported at or after (HH:MM)"
SEARCH_DEFAULT = "19:00"

HEAP_TITLE = "Dispatch queue: most urgent outage first"
HEAP_RULE = "Priority = site type (Hospital > Fire station > School > Business > Homes), then more customers, then earlier report."

PLAN_TITLE = "Plan one crew shift"
CAPACITY_LABEL, CAPACITY_UNIT = "Shift length", "hours"
CAPACITY_DEFAULT, CAPACITY_MIN, CAPACITY_MAX = 8, 3, 14
POOL_DEFAULT = 30          # how many top-priority outages the planner considers
WEIGHT_LABEL, VALUE_LABEL = "Repair hours", "Restoration points"

ROOT_LABEL = "Main Substation"
ROAD_LABEL = "crew drive time (minutes)"
NETWORK_TITLE = "Power-line network"
MST_TEXT = "Cheapest set of power lines that keeps every neighborhood connected to the substation (cost in $1,000s)."
BREAK_TEXT = "A line breaks. Which neighborhoods lose power?"

TEXT_TITLE = "Customer message scanner"
TEXT_HELP = "Scan customer texts for danger words so dangerous outages jump the queue."

TOUR_TITLE = "One crew's route through its outages"
TOUR_TEXT = "Start at the substation, visit every chosen outage area, return. Finding the shortest order is the Traveling Salesman Problem (NP-hard)."


def load(path=DATA_FILE):
    with open(path) as f:
        data = json.load(f)
    names = {n["id"]: n["name"] for n in data["nodes"]}
    for r in data["records"]:
        r["area"] = names[r["node"]]
    return data


def to_minutes(hhmm):
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def sort_value(rec):
    return to_minutes(rec["reported"])


def priority(rec):
    return (rec["priority_rank"], -rec["customers"], to_minutes(rec["reported"]))


def priority_reason(rec):
    return f"{rec['site_type']}, {rec['customers']} customer(s), reported {rec['reported']}"


CRITICAL_BONUS = {1: 500, 2: 300, 3: 150, 4: 0, 5: 0}   # hospital, fire station, school get extra points


def restoration_points(rec):
    """Value of fixing one outage = customers restored + a bonus for critical sites."""
    return rec["customers"] + CRITICAL_BONUS[rec["priority_rank"]]


def plan_items(records):
    return [{"id": r[ID_FIELD], "weight": r["repair_hours"], "value": restoration_points(r)} for r in records]


def describe(rec):
    return (f"{rec['outage_id']} at {rec['area']}: {rec['site_type'].lower()}, "
            f"{rec['customers']} customers, about {rec['repair_hours']} h to repair, reported {rec['reported']}.")
