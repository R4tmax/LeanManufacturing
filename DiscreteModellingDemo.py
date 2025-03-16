import simpy
import random

# Simulation parameters
SIM_TIME = 6000  # Total simulation time in seconds
CARRIER_INTERVAL = 30  # Time between new carriers arriving

class Bath:
    def __init__(self, env, name):
        self.env = env
        self.name = name
        self.occupied = False  # Track if the bath is in use
        self.process = None  # Store the carrier process

    def use_bath(self, carrier, time):
        if self.occupied:
            yield self.env.timeout(0)  # If occupied, do nothing (handled in scheduling)
        else:
            print(f"{self.env.now}: Carrier {carrier.id} enters {self.name}")
            self.occupied = True
            yield self.env.timeout(time)  # Processing time
            self.occupied = False
            print(f"{self.env.now}: Carrier {carrier.id} exits {self.name}")

class Manipulator:
    def __init__(self, env, name, range_baths):
        self.env = env
        self.name = name
        self.range_baths = range_baths  # Baths this manipulator can reach
        self.held_carrier = None  # Carrier being transported
        self.busy = False  # Flag for movement
        self.action = env.process(self.run())

    def move_carrier(self, carrier, target_bath):
        if self.busy:
            return  # Ignore if currently moving
        if target_bath in self.range_baths and not target_bath.occupied:
            self.busy = True
            print(f"{self.env.now}: {self.name} moving Carrier {carrier.id} to {target_bath.name}")
            yield self.env.timeout(5)  # Simulate movement time
            self.busy = False
            yield self.env.process(target_bath.use_bath(carrier, random.randint(20, 100)))  # Process
        else:
            yield self.env.timeout(0)  # Do nothing if the bath is occupied

    def run(self):
        while True:
            yield self.env.timeout(1)  # Just keep running

class Carrier:
    def __init__(self, env, id, baths, manipulators):
        self.env = env
        self.id = id
        self.baths = baths  # List of baths to go through
        self.manipulators = manipulators
        self.process = env.process(self.move_through_line())

    def move_through_line(self):
        for bath in self.baths:
            available_manipulator = next((m for m in self.manipulators if bath in m.range_baths), None)
            if available_manipulator:
                yield self.env.process(available_manipulator.move_carrier(self, bath))
            else:
                print(f"{self.env.now}: Carrier {self.id} is waiting for a manipulator.")
                yield self.env.timeout(5)  # Wait if no manipulator available
        print(f"{self.env.now}: Carrier {self.id} has completed the process.")

# Initialize environment
env = simpy.Environment()

# Create baths
baths = [Bath(env, f"Bath {i}") for i in range(1, 6)]

# Create manipulators with specific ranges
manipulators = [
    Manipulator(env, "Manipulator 1", [baths[0], baths[1]]),
    Manipulator(env, "Manipulator 2", [baths[1], baths[2]]),
    Manipulator(env, "Manipulator 3", [baths[2], baths[3], baths[4]])
]

# Generate carriers at intervals
def generate_carriers(env, baths, manipulators):
    id_counter = 1
    while True:
        Carrier(env, id_counter, baths, manipulators)
        id_counter += 1
        yield env.timeout(CARRIER_INTERVAL)

env.process(generate_carriers(env, baths, manipulators))

# Run simulation
env.run(until=SIM_TIME)
