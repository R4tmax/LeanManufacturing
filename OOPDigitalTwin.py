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

class ManipulatorState(Enum):
    IDLE = "Idle"
    MOVING = "Moving"
    LIFTING = "Lifting"
    SUBMERGING = "Submerging"
    HOLDING = "Holding"

class Manipulator:
    # Constants
    LIFT_TIME = 16  # Time for lift in seconds (constant)
    SPEED = 0.6  # Speed of the manipulator (constant, 0.6 m/s)

    next_id = 1  # Class variable for auto-incrementing ID

    def __init__(self, reach, starting_position):
        self.ManipUUID = Manipulator.next_id
        Manipulator.next_id += 1
        self.operatingRange = reach
        self.liftTime = Manipulator.LIFT_TIME
        self.movementSpeed = Manipulator.SPEED
        self.position = starting_position
        self.heldCarrier = None
        self.distance_rail = Manipulator.calculate_rail_meters(self)
        self.state = ManipulatorState.IDLE

    def __repr__(self):
        return (f"Manipulator(ID={self.ManipUUID} is performing {self.state} at:"
                f" position: {self.position} and meterwise position of {self.distance_rail}m,"
                f" services operations {self.operatingRange}, currently holds the {self.heldCarrier}")

    def move_to(self, new_position):
        """Move manipulator to a new position."""
        if new_position in self.operatingRange:
            print(f"Manipulator {self.ManipUUID} moving from {self.position} to {new_position}")
            self.position = new_position
        else:
            print(f"Manipulator {self.ManipUUID} cannot move to {new_position}, out of range.")

    def calculate_rail_meters(self):
        return baths[self.position].distanceToStart


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
    next_id = 1  # Class variable for auto-incrementing ID
    def __init__(self, name, operations):
        self.recpUUID = Recipe.next_id  # Unique identifier for the recipe
        Recipe.next_id += 1
        self.name = name  # Name of the recipe
        self.executionList = operations  # List of RecipeStep objects

    def __repr__(self):
        return f"Recipe(ID={self.recpUUID}, Name={self.name}, Steps={len(self.executionList)})"



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
        return self.requiredProcedure.executionList[self.currentStepIndex]



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
    ([0,1,2,3,5], 0 ),
    ([4,5,6,7,8,9,10],  5 ),
    ([8,9,10,11,12,13], 9 ),
    ([12,13,14,15,16,17], 14 ),
    ([17,18,19,20,21,22,23], 18 )
]

recipe_template1 = RecipeTemplate("Test1", [(0, 0), (5, 120), (10, 30),  (12,50), (17,300), (23, 0)])
recipe_template2 = RecipeTemplate("Test2", [(0, 0), (5, 400), (10, 300), (12,50), (17,300), (23, 0)])
recipe_template3 = RecipeTemplate("Test3", [(0, 0), (5, 400), (10,25), (12,50) ,(17, 300), (23, 0)])


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
carriers_to_move = len(carrier_definition)
work_order = deque(list(reversed(carrier_definition)))
finished_carriers = deque()

def print_collection(collection):
    for item in collection:
        print(item)


def provide_states():
    print_collection(baths)
    print_collection(manipulators)
    print_collection(carrier_definition)
    print_collection(work_order)

provide_states()

### non object function definitions
def move_carriers():
    """Moves carriers using manipulators."""
    for manipulator in manipulators:
        # If the manipulator is holding a carrier, drop it at the next bath
        if manipulator.heldCarrier:
            carrier = manipulator.heldCarrier
            current_step = carrier.get_current_step()
            next_bath_id = current_step.bathID  # The next bath the carrier needs to go to

            if next_bath_id in manipulator.operatingRange:  # Can the manipulator reach it?
                print(f"Manipulator {manipulator.ManipUUID} moving Carrier {carrier.carUUID} to Bath {next_bath_id}")

                # Drop carrier in the bath
                if not baths[next_bath_id].containedCarrier is None:
                    print("bath occupied, holding")
                    continue

                baths[next_bath_id].containedCarrier = carrier
                manipulator.heldCarrier = None
            else:
                print(
                    f"Manipulator {manipulator.ManipUUID} cannot move Carrier {carrier.carUUID} to Bath {next_bath_id}, out of range.")

        # If the manipulator is not holding anything, check for a carrier to pick up
        else:
            for bath in baths:
                if bath.bathUUID in manipulator.operatingRange and bath.containedCarrier:
                    carrier = bath.containedCarrier
                    carrier.currentStepIndex += 1
                    bath.containedCarrier = None
                    manipulator.heldCarrier = carrier
                    # Move to the next step in the recipe
                    print(
                        f"Manipulator {manipulator.ManipUUID} picked up Carrier {carrier.carUUID} from Bath {bath.bathUUID}")
                    break  # Only pick one carrier at a time


### Simulation
is_work_order_done = False
is_work_order_processed = False
step_counter = 0 # one step is equal to one second

while not is_work_order_done:

    if baths[0].containedCarrier is None and is_work_order_processed is False:
        print("Loader ready")
        carrier = work_order.pop()
        print(f"Carrier: {carrier}, is now at line entry point")
        baths[0].containedCarrier = carrier
        if len(work_order) == 0:
            is_work_order_processed = True

    if not baths[-1].containedCarrier is None:
        finished_carriers.append(baths[-1].containedCarrier)
        baths[-1].containedCarrier = None

    move_carriers()



    step_counter += 1
    print(step_counter)

    if len(finished_carriers) >= carriers_to_move:
        is_work_order_done = True
        print("Workorder processed!")

    #overflow control
    if step_counter > 50:
        is_work_order_done = True
        print("Simulation exceeds safe runtime, terminating")

print(work_order)
print(finished_carriers)
provide_states()