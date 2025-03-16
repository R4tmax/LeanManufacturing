from enum import Enum
import time

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
    ("Vstup do linky", 0), # index 0
    ("Horký oplach - ponor", 2752),
    ("Postřikové odmaštění", 6016),
    ("Odmaštění – ponor I", 9626),
    ("Odmaštění – ponor II", 12338),
    ("Odmaštění – ponor III", 15069),
    ("Oplach I- ponor", 17381),
    ("Oplach II- ponor", 19706),
    ("Oplach III- ponor", 22018),
    ("Moření (kyselé čištění) – ponor", 24822),
    ("Oplach IV po moření- ponor", 27241),
    ("Oplach V po moření- ponor", 29550),
    ("Aktivace - ponor", 31859),
    ("Zn fosfátování - ponor", 34282),
    ("Oplach IV demi - ponor", 36696),
    ("Oplach V demi - ponor", 39006),
    ("Pasivace - ponor", 41323),
    ("Demi oplach - ponor", 43633),
    ("Převážecí vozík předúprava", 45955),
    ("KTL barva - ponor", 49805),
    ("UF oplach 1 - ponor", 53073),
    ("UF Oplach 2 - ponor", 55377),
    ("Demi oplach 2 - ponor", 57687),
    ("Výstup z linky", 60000) # index 23
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
    Bath(name, distance / 1000)  # convert to m
    for name, distance in bathData
]

baths[0].isSubmergable = False
baths[-1].isSubmergable = False

manipulators = [
    Manipulator(reach,startingPosition)
    for reach, startingPosition in manipData
]

work_order = [Carrier(recipe_template1.create_instance()),Carrier(recipe_template1.create_instance()),Carrier(recipe_template2.create_instance()),Carrier(recipe_template3.create_instance())]

# Print the list of Bath objects
for bath in baths:
    print(bath)

for manipulator in manipulators:
    print(manipulator)

for carrier in work_order:
    print(carrier)

### Simulation
# Simulation settings
SIMULATION_TIME = 300  # Total runtime in seconds (adjust as needed)
current_time = 0  # Global clock


def run_simulation():
    global current_time
    while current_time < SIMULATION_TIME:
        print(f"\nTime: {current_time}s")

        # Step 1: Update all manipulators
        for manipulator in manipulators:
            update_manipulator(manipulator)

        # Step 2: Update carriers in baths
        for bath in baths:
            if bath.containedCarrier:
                update_carrier_in_bath(bath)

        # Step 3: Check for next actions
        assign_new_tasks()

        # Increment time
        current_time += 1
        time.sleep(0.1)  # Simulate real-time execution (optional)


def update_manipulator(manipulator):
    """Handle movement, lifting, and releasing operations."""
    if manipulator.heldCarrier:
        step = manipulator.heldCarrier.get_current_step()
        if step and step.bathID == manipulator.position:
            # Start submersion process
            if baths[step.bathID].containedCarrier is None:
                print(
                    f"Manipulator {manipulator.ManipUUID} submerging Carrier {manipulator.heldCarrier.carUUID} at Bath {step.bathID}")
                baths[step.bathID].containedCarrier = manipulator.heldCarrier
                manipulator.heldCarrier = None
                step.completed = True  # Mark step as complete


def update_carrier_in_bath(bath):
    """Update submersion progress and handle completion."""
    carrier = bath.containedCarrier
    step = carrier.get_current_step()
    if step and not step.completed:
        step.submersionTime -= 1
        if step.submersionTime <= 0:
            print(f"Carrier {carrier.carUUID} finished processing at Bath {bath.bathUUID}")
            step.completed = True
            bath.containedCarrier = None  # Carrier is ready for pickup
            carrier.currentStepIndex += 1  # Move to next step


def assign_new_tasks():
    """Assign free manipulators to waiting carriers."""
    for manipulator in manipulators:
        if manipulator.heldCarrier is None:  # Free manipulator
            for carrier in work_order:
                step = carrier.get_current_step()
                if step and not step.completed:
                    if baths[step.bathID].containedCarrier is None:  # Empty bath
                        manipulator.move_to(step.bathID)
                        manipulator.heldCarrier = carrier
                        print(
                            f"Manipulator {manipulator.ManipUUID} picking up Carrier {carrier.carUUID} for Bath {step.bathID}")
                        return  # One task per loop


# Run the simulation
run_simulation()