# Manipulator parameters (example values)
manipulator_params = {
    "deceleration_time": 3,  # seconds
    "immersion_path": 3240,  # mm
    "immersion_speed": 12,   # m/min
    "lifting_speed": 15,     # m/min
    "deceleration_before_immersion": 500,  # mm
    "pre_immersion_speed": 8,  # m/min
    "drip_height": 2000,  # mm
    "stop_at_drip": 1,  # 1 for Yes, 0 for No
    "pojezd": 35  # m/min
}

# Example operations data (parsed from your input)
""" operations = [
    {"id": 1, "used": True, "min_time": 90, "optimal_time": 120, "max_time": 180, "drip_time": 20, "travel": 2300},
    {"id": 2, "used": True, "min_time": 120, "optimal_time": 160, "max_time": 180, "drip_time": 0, "travel": 1900},
    {"id": 3, "used": True, "min_time": 180, "optimal_time": 220, "max_time": 240, "drip_time": 20, "travel": 1900},
    {"id": 4, "used": False, "min_time": 45, "optimal_time": 60, "max_time": 120, "drip_time": 15, "travel": 1800},
    {"id": 5, "used": True, "min_time": 45, "optimal_time": 60, "max_time": 120, "drip_time": 15, "travel": 1800},
    {"id": 6, "used": True, "min_time": 420, "optimal_time": 480, "max_time": 500, "drip_time": 20, "travel": 1800},
    {"id": 7, "used": True, "min_time": 420, "optimal_time": 480, "max_time": 500, "drip_time": 20, "travel": 1800},
    {"id": 8, "used": True, "min_time": 420, "optimal_time": 480, "max_time": 500, "drip_time": 20, "travel": 1800},
    {"id": 9, "used": True, "min_time": 420, "optimal_time": 480, "max_time": 500, "drip_time": 20, "travel": 1800},
    {"id": 10, "used": False, "min_time": 420, "optimal_time": 480, "max_time": 500, "drip_time": 20, "travel": 1800},
    {"id": 11, "used": True, "min_time": 420, "optimal_time": 480, "max_time": 500, "drip_time": 20, "travel": 1800},
    {"id": 12, "used": True, "min_time": 420, "optimal_time": 480, "max_time": 500, "drip_time": 20, "travel": 1800},
    {"id": 13, "used": True, "min_time": 420, "optimal_time": 480, "max_time": 500, "drip_time": 20, "travel": 1800},
    {"id": 14, "used": True, "min_time": 420, "optimal_time": 480, "max_time": 500, "drip_time": 20, "travel": 1800}
] """

operations = [
    {"id": 1, "used": True, "min_time": 90, "optimal_time": 120, "max_time": 180, "drip_time": 20, "travel": 2300},
    {"id": 2, "used": True, "min_time": 120, "optimal_time": 160, "max_time": 180, "drip_time": 0, "travel": 1900},
    {"id": 3, "used": True, "min_time": 180, "optimal_time": 220, "max_time": 240, "drip_time": 20, "travel": 1900},
    {"id": 4, "used": False, "min_time": 45, "optimal_time": 60, "max_time": 120, "drip_time": 15, "travel": 1800},
    {"id": 5, "used": True, "min_time": 45, "optimal_time": 60, "max_time": 120, "drip_time": 15, "travel": 1800},
    {"id": 6, "used": True, "min_time": 420, "optimal_time": 480, "max_time": 500, "drip_time": 20, "travel": 1800},
    {"id": 7, "used": True, "min_time": 420, "optimal_time": 480, "max_time": 500, "drip_time": 20, "travel": 1800},
    {"id": 8, "used": True, "min_time": 420, "optimal_time": 480, "max_time": 500, "drip_time": 20, "travel": 1800},
    {"id": 9, "used": True, "min_time": 420, "optimal_time": 480, "max_time": 500, "drip_time": 20, "travel": 1800}
]



class Manipulator:
    def __init__(self, params):
        self.params = params

    def calculate_immersion_time(self):
        # Convert immersion speed from m/min to m/s
        speed_m_per_s = self.params["immersion_speed"] / 60  # Convert speed to meters per second
        # Convert immersion path from mm to meters
        immersion_path_meters = self.params["immersion_path"] / 1000  # Convert from mm to meters
        # Calculate time to immersion based on immersion path and speed
        time_to_immersion = immersion_path_meters / speed_m_per_s  # Time in seconds
        # Add deceleration time (this is an additional time added to the overall time)
        time_to_immersion += self.params["deceleration_time"]
        return time_to_immersion

    def calculate_lifting_time(self):
        # Convert lifting speed from m/min to m/s
        speed_m_per_s = self.params["lifting_speed"] / 60  # Convert speed to meters per second
        # Convert immersion path from mm to meters
        immersion_path_meters = self.params["immersion_path"] / 1000  # Convert from mm to meters
        # Calculate time to lift based on immersion path and speed
        time_to_lift = immersion_path_meters / speed_m_per_s  # Time in seconds
        return time_to_lift

    def calculate_travel_time(self, distance):
        # Convert pojezd speed from m/min to m/s
        speed_m_per_s = self.params["pojezd"] / 60  # Convert pojezd speed to meters per second
        # Convert distance from mm to meters
        distance_meters = distance / 1000  # Convert distance from mm to meters
        # Calculate the travel time (in seconds)
        travel_time_seconds = distance_meters / speed_m_per_s  # Time in seconds
        return travel_time_seconds

    def calculate_drip_time(self, operation):
        """
        Calculate the total drip time for a specific operation.
        This includes the time required to reach the drip height and any operation-specific drip time.
        """
        if operation["drip_time"] <= 0:  # If no drip time is specified, return 0
            return 0

        # Calculate the time needed to lift the manipulator to the specified drip height
        drip_height_meters = self.params["drip_height"] / 1000  # Convert drip height from mm to meters
        lifting_speed_m_per_s = self.params["lifting_speed"] / 60  # Convert lifting speed from m/min to m/s
        time_to_reach_drip_height = drip_height_meters / lifting_speed_m_per_s  # Time in seconds

        # Add operation-specific drip time
        total_drip_time = time_to_reach_drip_height + operation["drip_time"]
        return total_drip_time


def greedy_allocation(operations, manipulator_params):
    """Allocate operations to manipulators using a greedy approach with proper linking."""
    manipulators = []  # List of manipulators and their assigned operations
    current_manipulator = []  # Operations assigned to the current manipulator
    manipulator = Manipulator(manipulator_params)  # Create an instance of the Manipulator class

    for i, operation in enumerate(operations):
        if not operation["used"]:
            continue

        # If this is the first operation, start a new manipulator
        if not current_manipulator:
            current_manipulator.append(operation["id"])
            continue

        # Check if the current manipulator can continue with the next operation
        last_operation = operations[current_manipulator[-1] - 1]
        travel_time = manipulator.calculate_travel_time(last_operation["travel"])

        # Add times for immersion, lifting, and drip (if necessary)
        immersion_time = manipulator.calculate_immersion_time() if operation["drip_time"] > 0 else 0
        lifting_time = manipulator.calculate_lifting_time()
        total_time_for_current_operation = travel_time + immersion_time + lifting_time

        # Check if next operation can fit in the current manipulator's time
        if total_time_for_current_operation + operation["optimal_time"] <= last_operation["max_time"]:
            # Continue assigning the operation to the current manipulator
            current_manipulator.append(operation["id"])
        else:
            # If there's no more space in the current manipulator, add the current manipulator to the list
            manipulators.append(current_manipulator)

            # Ensure that the first operation of the new manipulator is the same as the last operation of the previous manipulator
            current_manipulator = [current_manipulator[-1]]  # Ensure the new manipulator starts with the last operation of the previous one
            current_manipulator.append(operation["id"])  # Add the current operation

    # Append the last manipulator
    if current_manipulator:
        manipulators.append(current_manipulator)

    return manipulators

# Sample run
manipulator_assignments = greedy_allocation(operations, manipulator_params)

# Format the output
print(f"Potřebný počet manipulátorů: {len(manipulator_assignments)} ks")
for i, manipulator in enumerate(manipulator_assignments, 1):
    print(f"Manipulator {i} vykonává operace: {', '.join(map(str, manipulator))}")
    
def calculate_line_takt(manipulator_assignments, operations, manipulator_params):
    """Calculate the takt time for the production line based on manipulator assignments."""
    max_takt = 0  # Initialize the takt time
    manipulator = Manipulator(manipulator_params)  # Create an instance of the Manipulator class

    for manipulator_ops in manipulator_assignments:
        total_time = 0  # Initialize the total time for this manipulator's cycle
        for i, operation_id in enumerate(manipulator_ops):
            # Get the operation details (subtract 1 from operation_id to match list indexing)
            operation = operations[operation_id - 1]

            # Travel time between operations
            if i > 0:  # If not the first operation
                last_operation = operations[manipulator_ops[i - 1] - 1]
                total_time += manipulator.calculate_travel_time(last_operation["travel"])

            # Add times for immersion, lifting, and drip (if necessary)
            if operation["drip_time"] > 0:
                total_time += manipulator.calculate_immersion_time()
                total_time += manipulator.calculate_drip_time(operation)
            total_time += manipulator.calculate_lifting_time()
            total_time += operation["optimal_time"]  # Add the operation's optimal processing time

        # Update the maximum takt time (line cycle time)
        max_takt = max(max_takt, total_time)

    return max_takt

# Calculate takt linky (line takt)
takt_linky = calculate_line_takt(manipulator_assignments, operations, manipulator_params)

# Output the results
print(f"Potřebný počet manipulátorů: {len(manipulator_assignments)} ks")
print(f"Takt linky je: {takt_linky:.2f} sekund")