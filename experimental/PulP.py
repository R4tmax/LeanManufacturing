from pulp import LpProblem, LpMinimize, LpVariable, lpSum, value

# Vstupní data (zjednodušená tabulka operací)
operations = [
    {"id": 1, "used": True, "time_min": 90, "time_opt": 120, "time_max": 180, "transfer_time": 0},
    {"id": 2, "used": True, "time_min": 120, "time_opt": 160, "time_max": 180, "transfer_time": 2300},
    {"id": 3, "used": True, "time_min": 180, "time_opt": 220, "time_max": 240, "transfer_time": 1900},
    {"id": 5, "used": True, "time_min": 45, "time_opt": 60, "time_max": 120, "transfer_time": 1800},
    {"id": 6, "used": True, "time_min": 45, "time_opt": 60, "time_max": 120, "transfer_time": 1800},
    {"id": 7, "used": True, "time_min": 420, "time_opt": 480, "time_max": 500, "transfer_time": 1800},
    {"id": 10, "used": True, "time_min": 45, "time_opt": 60, "time_max": 75, "transfer_time": 1800},
    {"id": 11, "used": True, "time_min": 45, "time_opt": 60, "time_max": 75, "transfer_time": 1800},
    {"id": 12, "used": True, "time_min": 60, "time_opt": 90, "time_max": 120, "transfer_time": 1800},
    {"id": 13, "used": True, "time_min": 300, "time_opt": 330, "time_max": 360, "transfer_time": 1800},
    {"id": 14, "used": True, "time_min": 60, "time_opt": 75, "time_max": 90, "transfer_time": 1800},
    {"id": 15, "used": True, "time_min": 60, "time_opt": 75, "time_max": 90, "transfer_time": 1800},
    {"id": 16, "used": True, "time_min": 60, "time_opt": 90, "time_max": 120, "transfer_time": 1800},
    {"id": 17, "used": True, "time_min": 60, "time_opt": 75, "time_max": 90, "transfer_time": 1800},
    {"id": 18, "used": True, "time_min": 180, "time_opt": 220, "time_max": 260, "transfer_time": 2300},
    {"id": 19, "used": True, "time_min": 60, "time_opt": 90, "time_max": 120, "transfer_time": 2300},
    {"id": 20, "used": True, "time_min": 60, "time_opt": 90, "time_max": 120, "transfer_time": 1800},
    {"id": 21, "used": True, "time_min": 60, "time_opt": 90, "time_max": 120, "transfer_time": 1800}
]

# Sort operations by ID
operations.sort(key=lambda op: op["id"])

# Manipulator parameters
manipulator_params = {
    "deceleration_time": 3,  # seconds
    "immersion_path": 2750,  # mm
    "immersion_speed": 12,   # m/min
    "lifting_speed": 15,     # m/min
    "deceleration_before_immersion": 500,  # mm
    "pre_immersion_speed": 8,  # m/min
    "drip_height": 2000,  # mm
    "stop_at_drip": 1  # 1 for Yes, 0 for No
}

# Helper function to calculate immersion and lifting time
def calculate_movement_time(path_mm, speed_m_min):
    # Convert speed to mm/s (1 m/min = 1000 mm/min = 1000/60 mm/s)
    speed_mm_s = speed_m_min * 1000 / 60
    return path_mm / speed_mm_s  # Time in seconds

# Update operation time considering movement parameters
def get_operation_time(op, manipulator_params):
    # Time for immersion
    immersion_time = calculate_movement_time(manipulator_params["immersion_path"], manipulator_params["immersion_speed"])
    
    # Time for pre-immersion deceleration
    pre_immersion_time = calculate_movement_time(manipulator_params["deceleration_before_immersion"], manipulator_params["pre_immersion_speed"])
    
    # Time for lifting
    lifting_time = calculate_movement_time(manipulator_params["immersion_path"], manipulator_params["lifting_speed"])

    # If a stop is required for drip clearance
    if manipulator_params["stop_at_drip"]:
        # Time for the stop position (drip clearance)
        stop_time = 0  # This can be adjusted if a specific stop time is given.
    else:
        stop_time = 0

    # Total operation time (based on immersion + lifting + pre-immersion deceleration)
    total_time = op["time_opt"] + op["transfer_time"] / 100 + immersion_time + lifting_time + pre_immersion_time + stop_time
    return total_time

# Update operations with adjusted times based on manipulator parameters
for op in operations:
    op["adjusted_time"] = get_operation_time(op, manipulator_params)

# Model optimalizace
model = LpProblem("Optimal_Manipulator_Assignment", LpMinimize)

# Maximální počet manipulátorů, který budeme uvažovat (očekáváme menší počet manipulátorů)
max_manipulators = 10  # Limit manipulators to a reasonable number

# Rozhodovací proměnné pro přiřazení operací k manipulátorům
X = [[LpVariable(f"x_{m}_{o['id']}", cat="Binary") for o in operations] for m in range(max_manipulators)]

# Cíl: minimalizovat počet manipulátorů
used_manipulators = [LpVariable(f"used_{m}", cat="Binary") for m in range(max_manipulators)]
model += lpSum(used_manipulators), "Minimize_Manipulators"

# Každá operace musí být přiřazena přesně jednomu manipulátorovi
for j, op in enumerate(operations):
    model += lpSum(X[m][j] for m in range(max_manipulators)) == 1

# Omezení pro každý manipulátor: musí vykonávat souvislou posloupnost operací (sekvenční pořadí)
for m in range(max_manipulators):
    for j in range(1, len(operations)):
        model += X[m][j] >= X[m][j - 1], f"Sequential_Order_{m}_{j}"

# Použitý manipulátor musí být aktivován
for m in range(max_manipulators):
    for j in range(len(operations)):
        model += X[m][j] <= used_manipulators[m]

# Constraint to limit the number of operations per manipulator (balanced load)
max_operations_per_manipulator = len(operations) // max_manipulators + 1  # This allows a balanced load
for m in range(max_manipulators):
    model += lpSum(X[m][j] for j in range(len(operations))) <= max_operations_per_manipulator, f"Max_Operations_Per_Manipulator_{m}"

# Přidání podmínky pro minimální čas cyklu (takt linky)
takt_time = LpVariable("Takt_Time", lowBound=0, cat="Continuous")
model += takt_time >= lpSum((X[m][j] * op["adjusted_time"]) for m in range(max_manipulators) for j, op in enumerate(operations))

# Minimalizace taktu linky
model += takt_time, "Minimize_Cycle_Time"

# Přidání podmínky pro minimální počet manipulátorů
model += lpSum(used_manipulators) >= 1, "Min_Manipulator_Count"

# Řešení modelu
model.solve()

# Výstup výsledků
num_used = sum(1 for m in range(max_manipulators) if value(used_manipulators[m]) == 1)
print(f"Potřebný počet manipulátorů: {num_used}")

# Sběr operací přiřazených manipulátorům
manipulator_assignments = []
for m in range(max_manipulators):
    assigned_ops = [op["id"] for j, op in enumerate(operations) if value(X[m][j]) == 1]
    if assigned_ops:
        manipulator_assignments.append((m + 1, len(assigned_ops), min(assigned_ops), max(assigned_ops)))

# Seřazení manipulátorů podle ID a operací podle ID
manipulator_assignments.sort(key=lambda x: x[0])  # Sort manipulators by ID

# Zobrazení výsledků
for m, num_ops, start_op, end_op in manipulator_assignments:
    print(f"Manipulator {m}: operace {start_op} - {end_op} ({num_ops} operací)")

print(f"Minimální dosažitelný čas s daným počtem manipulátorů: {value(takt_time):.2f} s")
