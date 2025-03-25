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