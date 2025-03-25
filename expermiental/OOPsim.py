def initialize_manipulators(num_manipulators):
    """
    Initializes the manipulators and their assigned baths.
    Each manipulator has a list of baths, operations, and time tracking variables.
    """
    manipulators = {}

    for i in range(1, num_manipulators + 1):
        manipulator_name = f"M{i}"
        manipulators[manipulator_name] = {"baths": [], "operations": {}, "full_time": 0, "distance": 0}

    return manipulators

# Initialize bath parameters
def initialize_baths():
    """
    Initializes the parameters for each bath, including immersion time, drain time, and distance.
    Some baths are marked as not used.
    """
    return {
        "Lázeň 1": {"used": True, "immersion_time": 120, "drain_time": 20, "distance": 2300},
        "Lázeň 2": {"used": True, "immersion_time": 160, "drain_time": 0, "distance": 1900},
        "Lázeň 3": {"used": True, "immersion_time": 220, "drain_time": 20, "distance": 1900},
        "Lázeň 4": {"used": False, "immersion_time": None, "drain_time": None, "distance": 1000},
        "Lázeň 5": {"used": True, "immersion_time": 60, "drain_time": 15, "distance": 1800},
        "Lázeň 6": {"used": True, "immersion_time": 60, "drain_time": 15, "distance": 1800},
        "Lázeň 7": {"used": True, "immersion_time": 480, "drain_time": 20, "distance": 1800},
        "Lázeň 8": {"used": False, "immersion_time": None, "drain_time": None, "distance": 1000},
        "Lázeň 9": {"used": True, "immersion_time": 60, "drain_time": 15, "distance": 1800},
        "Lázeň 10": {"used": False, "immersion_time": None, "drain_time": None, "distance": 1000},
        "Lázeň 11": {"used": True, "immersion_time": 60, "drain_time": 15, "distance": 1800},
        "Lázeň 12": {"used": True, "immersion_time": 90, "drain_time": 20, "distance": 1800},
        "Lázeň 13": {"used": True, "immersion_time": 330, "drain_time": 20, "distance": 1800},
        "Lázeň 14": {"used": True, "immersion_time": 75, "drain_time": 15, "distance": 1800},
        "Lázeň 15": {"used": True, "immersion_time": 75, "drain_time": 15, "distance": 1800},
        "Lázeň 16": {"used": True, "immersion_time": 90, "drain_time": 20, "distance": 1800},
        "Lázeň 17": {"used": True, "immersion_time": 75, "drain_time": 15, "distance": 1800},
        "Lázeň 18": {"used": True, "immersion_time": 220, "drain_time": 20, "distance": 2300},
        "Lázeň 19": {"used": True, "immersion_time": 90, "drain_time": 1, "distance": 2300},
        "Lázeň 20": {"used": True, "immersion_time": 90, "drain_time": 1, "distance": 1800},
        "Lázeň 21": {"used": True, "immersion_time": 90, "drain_time": 1, "distance": 1800},
    }

def assign_baths_to_manipulators():
    """
    Assigns baths to manipulators dynamically. Each manipulator gets a portion of the available baths,
    with some manipulators potentially getting an extra bath if there is a remainder.
    The last bath from the previous manipulator is added as the first bath for the next manipulator.
    """
    baths = initialize_baths()  # Initialize bath parameters
    manipulators = initialize_manipulators(9)  # Initialize manipulator parameters

    # Get a list of all baths
    all_baths = list(baths.keys())
    num_baths = len(all_baths)  # Number of baths
    num_manipulators = len(manipulators)  # Number of manipulators

    # Dynamically distribute baths among manipulators
    baths_per_manipulator = num_baths // num_manipulators  # How many baths each manipulator gets
    remainder = num_baths % num_manipulators  # How many extra baths remain after division

    start_index = 0
    for i, manipulator in enumerate(manipulators.keys()):
        # Calculate how many baths the current manipulator gets
        if i < remainder:
            # If there is a remainder, the first manipulators get one more bath
            end_index = start_index + baths_per_manipulator + 1
        else:
            end_index = start_index + baths_per_manipulator

        # Assign baths to the current manipulator
        manipulators[manipulator]["baths"] = all_baths[start_index:end_index]

        # For each manipulator except the first, add the last bath from the previous manipulator as the first bath
        if i > 0:
            manipulators[manipulator]["baths"] = [manipulators[list(manipulators.keys())[i - 1]]["baths"][-1]] + \
                                                 manipulators[manipulator]["baths"]

        # Set the index for the next manipulator
        start_index = end_index

    return manipulators, baths  # Return the updated manipulators and baths

# Calculate travel time between baths based on distance and acceleration model
def travel_time(distance):
    """
    Calculates the travel time based on the distance between two baths, considering acceleration and deceleration.
    """
    distance = distance / 1000  # Convert distance to kilometers
    v_max = 1  # Maximum speed in m/s
    t_acc = 2  # Acceleration time in seconds
    a = v_max / t_acc  # Acceleration value
    s1 = 0.5 * a * t_acc ** 2  # Distance covered during acceleration
    s3 = s1  # Same distance for deceleration

    # If the distance is greater than the sum of acceleration and deceleration distances
    if distance > (s1 + s3):
        s2 = distance - (s1 + s3)  # Constant speed travel
        t2 = s2 / v_max
        t_acc_time = t_acc  # Time spent accelerating
        t_dec_time = t_acc  # Time spent decelerating
    else:
        # If the distance is smaller than the sum of acceleration and deceleration distances
        t_acc_time = (2 * distance / a) ** 0.5  # Time for acceleration and deceleration
        t2 = 0  # No constant speed phase
        t_dec_time = t_acc_time  # Symmetric deceleration time

    # Total time is sum of all phases
    total_time = t_acc_time + t2 + t_dec_time
    return total_time

# Simulate the movement of manipulators between baths
def process_bath_entry(manip, i, bath, next_bath, data, baths, time, distance):
    """
    Handles the logic for entering a bath, calculating travel time, and updating operations.
    """
    data["operations"][time] = f"Arrival at {bath}"  # Log the arrival at the bath
    if manip == "M1" or i > 0:
        # If manipulator M1 or moving between multiple baths
        time += travel_time(baths[bath]["distance"] + distance)  # Calculate and add travel time
        data["distance"] += baths[bath]["distance"] + distance  # Add distance to the total
    else:
        # If it's the first bath for manipulator M1
        time += travel_time(baths[next_bath]["distance"] + distance)  # Add travel time to the next bath
    return time, 0  # Reset distance after arrival

def process_immersion(bath, data, time):
    """
    Handles immersion into the bath, adding necessary time steps.
    """
    data["operations"][time] = f"Immersion in {bath}"  # Log immersion start
    time += 16  # Additional time for immersion process
    data["operations"][time] = f"Time in {bath}"  # Log the time spent in bath
    return time

def process_removal(bath, data, time, is_last):
    """
    Handles removal and draining operations.
    """
    if not is_last:
        # If not the last bath, handle removal and draining
        time += baths[bath]["immersion_time"]  # Add immersion time
        data["operations"][time] = f"Removal from {bath}"  # Log removal
        time += 16  # Additional time for removal
        data["operations"][time] = f"Draining after {bath}"  # Log draining start
        time += baths[bath]["drain_time"]  # Add drain time
    else:
        # If it is the last bath, just remove without draining
        data["operations"][time] = f"Removal from {bath}"
        time += 16  # Additional time for removal
    return time

# Simulate the movement and operations of manipulators through the baths
def simulate_manipulators(manipulators, baths):
    """
    Simulates the movement and operations of manipulators through the baths.
    """
    for manip, data in manipulators.items():
        time = 0
        distance = 0
        for i, bath in enumerate(data["baths"]):
            if baths[bath]["used"]:
                # If bath is used, process the entry, immersion, and removal
                next_bath = data["baths"][i + 1] if i + 1 < len(data["baths"]) else None
                time, distance = process_bath_entry(manip, i, bath, next_bath, data, baths, time, distance)
                time = process_immersion(bath, data, time)
                time = process_removal(bath, data, time, is_last=(i == len(data["baths"]) - 1))
            else:
                # If bath is not used, just add distance
                distance += baths[bath]["distance"]

        data["operations"][time] = "Return trip"  # Log return trip
        time += travel_time(data["distance"])  # Add return travel time
        data["operations"][time] = "Completed"  # Log completion
        data["full_time"] = time  # Set full operation time

# Synchronize operations to ensure all manipulators finish at the same time
def synchronize_operations(manipulators):
    """
    Synchronizes the operations of all manipulators to ensure they finish at the same time.
    """
    max_full_time = max(data["full_time"] for data in manipulators.values())  # Find the maximum time
    for manip, data in manipulators.items():
        time_diff = max_full_time - data["full_time"]  # Calculate the time difference
        if time_diff > 0:
            # If there is a difference, adjust the times
            data["operations"] = {t + time_diff: op for t, op in data["operations"].items()}
            data["operations"][0] = f"Waiting until {max_full_time} s"  # Log the waiting period
        data["full_time"] = max_full_time  # Update full time to match
    return max_full_time, len(manipulators) * max_full_time

# Print out the operation timeline for each manipulator
def print_operations(manipulators, max_full_time):
    """
    Prints the operation timeline for each manipulator and the cycle and takt times.
    """
    for manip, data in manipulators.items():
        print(f"\nManipulator: {manip}")
        for t, op in sorted(data["operations"].items()):
            print(f"{round(t, 2):>6} s → {op}")  # Print time and operation
    print("\nCycle time:", len(manipulators) * max_full_time)  # Print total cycle time
    print("Takt time:", max_full_time)  # Print takt time


# Main script execution
manipulators, baths = assign_baths_to_manipulators()
simulate_manipulators(manipulators, baths)  # Simulate manipulator operations
max_full_time, cycle_time = synchronize_operations(manipulators)  # Synchronize and get the max time
print_operations(manipulators, max_full_time)  # Print final operation timelines


