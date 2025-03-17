from enum import Enum
import time
from collections import deque

### Object definition
class Bath:
    next_id = 0  # Class variable for auto-incrementing ID

    def __init__(self, name, distance, submergable=True):
        self.bathUUID = Bath.next_id  # Assign auto-incremented ID
        Bath.next_id += 1  # Increment for the next instance
        self.name = name
        self.distanceToStart = distance  # Distance in m
        self.containedCarrier = None
        self.isSubmergable = submergable

    def __repr__(self):
        return f"Bath(ID={self.bathUUID}, Name={self.name}, Distance={self.distanceToStart} m, currently has {self.containedCarrier} submerged)"


class Manipulator:
    # Constants
    LIFT_TIME = 16  # Time for lift in seconds (constant)
    SPEED = 0.6  # Speed of the manipulator (constant, 0.6 m/s)

    next_id = 0  # Class variable for auto-incrementing ID

    def __init__(self, reach, starting_position):
        self.ManipUUID = Manipulator.next_id
        Manipulator.next_id += 1
        self.operatingRange = reach
        self.liftTime = Manipulator.LIFT_TIME
        self.movementSpeed = Manipulator.SPEED
        self.position = starting_position
        self.heldCarrier = None

    def __repr__(self):
        return f"Manipulator(ID={self.ManipUUID}, Located at position: {self.position}, services operations {self.operatingRange}, currently holds the {self.heldCarrier}"

    def move_to(self, new_position):
        """Move manipulator to a new position."""
        if new_position in self.operatingRange:
            print(f"Manipulator {self.ManipUUID} moving from {self.position} to {new_position}")
            self.position = new_position
        else:
            print(f"Manipulator {self.ManipUUID} cannot move to {new_position}, out of range.")


class RecipeStep:
    DRIP_TIME = 20 # set to constant for now
    def __init__(self, bid, submersion_time):
        self.bathID = bid  # The bath to use in this step
        self.submersionTime = submersion_time  # Time to submerge the product
        self.dripTime = RecipeStep.DRIP_TIME  # Time to drip before moving on
        self.completed = False  # Flag to track completion

    def __repr__(self):
        return f"RecipeStep(Bath: {self.bathID}, Submersion: {self.submersionTime}s, Drip: {self.dripTime}s, Completed: {self.completed})"

class RecipeTemplate:
    def __init__(self, name, step_definitions):
        self.name = name  # Name of the recipe template
        self.step_definitions = step_definitions  # List of (bath_id, submersion_time) tuples

    def create_instance(self):
        """Generate a new Recipe instance with unique steps."""
        steps = [RecipeStep(bath_id, submersion_time) for bath_id, submersion_time in self.step_definitions]
        return Recipe(self.name, steps)


class Recipe:
    next_id = 0  # Class variable for auto-incrementing ID
    def __init__(self, name, operations):
        self.recpUUID = Recipe.next_id  # Unique identifier for the recipe
        Recipe.next_id += 1
        self.name = name  # Name of the recipe
        self.executionList = operations  # List of RecipeStep objects

    def __repr__(self):
        return f"Recipe(ID={self.recpUUID}, Name={self.name}, Steps={len(self.executionList)})"


class ManipulatorState(Enum):
    IDLE = "Idle"
    MOVING = "Moving"
    LIFTING = "Lifting"
    HOLDING = "Holding"


class Carrier:
    next_id = 1
    def __init__(self, procedure):
        self.carUUID = Carrier.next_id  # Unique identifier for the recipe
        Carrier.next_id += 1   # Unique identifier for the carrier
        self.requiredProcedure = procedure  # The Recipe the carrier follows
        self.currentStepIndex = 0  # Keeps track of the current step in the recipe
        self.state = ManipulatorState.IDLE  # Default state

    def __repr__(self):
        return f"Carrier(ID={self.carUUID}, Current Step: {self.currentStepIndex}, Recipe: {self.requiredProcedure.name})"


    def get_current_step(self):
        """Returns the current recipe step."""
        if self.currentStepIndex < len(self.requiredProcedure.executionList):
            return self.requiredProcedure.executionList[self.currentStepIndex]
        return None


### Data & condition definition

bathData = [
    ("Vstup do linky", 0, False), # index 0
    ("Horký oplach - ponor", 2752, True),
    ("Postřikové odmaštění", 6016, True),
    ("Odmaštění – ponor I", 9626, True),
    ("Odmaštění – ponor II", 12338, True),
    ("Odmaštění – ponor III", 15069, True),
    ("Oplach I- ponor", 17381,True),
    ("Oplach II- ponor", 19706, True),
    ("Oplach III- ponor", 22018,True),
    ("Moření (kyselé čištění) – ponor", 24822,  True),
    ("Oplach IV po moření- ponor", 27241, True),
    ("Oplach V po moření- ponor", 29550, True),
    ("Aktivace - ponor", 31859, True),
    ("Zn fosfátování - ponor", 34282, True),
    ("Oplach IV demi - ponor", 36696, True),
    ("Oplach V demi - ponor", 39006, True),
    ("Pasivace - ponor", 41323, True),
    ("Demi oplach - ponor", 43633, True),
    ("Převážecí vozík předúprava", 45955,True),
    ("KTL barva - ponor", 49805, True),
    ("UF oplach 1 - ponor", 53073, True),
    ("UF Oplach 2 - ponor", 55377, True),
    ("Demi oplach 2 - ponor", 57687, True),
    ("Výstup z linky", 60000, False) # index 23
]

manipData = [
    ([0,1,2,3,4], 0 ),
    ([4,5,6,7,8],  5 ),
    ([8,9,10,11,12], 9 ),
    ([13,14,15,16,17], 14 ),
    ([17,18,19,20,21,22,23], 18 )
]

recipe_template1 = RecipeTemplate("Test1", [(0, 0), (5, 120), (10, 30), (23, 0)])
recipe_template2 = RecipeTemplate("Test2", [(0, 0), (5, 400), (10, 300), (23, 0)])
recipe_template3 = RecipeTemplate("Test3", [(0, 0), (6, 400), (17, 300), (23, 0)])


### Collection Instantiation & readback
baths = [
    Bath(name, distance / 1000, submergable=flag)  # convert to m
    for name, distance, flag in bathData
]


manipulators = [
    Manipulator(reach,startingPosition)
    for reach, startingPosition in manipData
]

carrier_definition = [Carrier(recipe_template1.create_instance()),Carrier(recipe_template1.create_instance()),Carrier(recipe_template2.create_instance()),Carrier(recipe_template3.create_instance())]
work_order = deque(list(reversed(carrier_definition)))

def print_collection(collection):
    for item in collection:
        print(item)


def provide_states():
    print_collection(baths)
    print_collection(manipulators)
    print_collection(carrier_definition)
    print_collection(work_order)

provide_states()

### Simulation
is_work_order_done = False
step_counter = 0 # one step is equal to one second
baths[0].containedCarrier = work_order.pop()

while not is_work_order_done:
    print(baths[0])
    step_counter+=1
    print(step_counter, is_work_order_done)
    if step_counter == 2:
        is_work_order_done = True
