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