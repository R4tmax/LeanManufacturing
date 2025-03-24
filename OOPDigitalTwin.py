from enum import Enum
from collections import deque, defaultdict
import math


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
    IDLE = "Idle" #Manipulator does not carry a carrier and has on tasking
    MOVING = "Moving" #manipulator is changing positions
    LIFTING = "Lifting" #manipulator is lifting a frame from a submerged position
    DRIPPING = "Dripping" #manipulator has lifted a carrier and has to hold position until drip time is done
    SUBMERGING = "Submerging" #manipulator is putting a frame into a bath
    HOLDING = "Holding" #manipulator has a carrier, but possible target baths are occupied
    LOADING = "Loading" #manipulator is in a process of picking up from position bath[0] or is letting go of a carrier at baths[-1]

class Manipulator:
    # Constants
    LIFT_TIME = 16  # Time for lift in seconds (constant)
    SPEED = 0.6  # Speed of the manipulator (constant, 0.6 m/s)
    QUEUE_TIME = 1 # Time it takes to pickup and position baths[0] and let go at baths[-1]

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
        self.target_position = None  # Track where the manipulator is moving
        self.operation_timer = 0

    def __repr__(self):
        return (f"Manipulator(ID={self.ManipUUID} is performing {self.state} at:"
                f" position: {self.position} and meterwise position of {self.distance_rail}m,"
                f" services operations {self.operatingRange}, currently holds the {self.heldCarrier}")

    def move_to(self, new_position):
        if new_position in self.operatingRange:
            print(f"Manipulator {self.ManipUUID} moving from {self.position} to {new_position}")
            self.state = ManipulatorState.MOVING
            self.target_position = new_position
            self.update_movement()
        else:
            print(f"Manipulator {self.ManipUUID} cannot move to {new_position}, out of range.")

    def calculate_rail_meters(self):
        return baths[self.position].distanceToStart

    def update_movement(self):
        if self.state == ManipulatorState.MOVING and self.target_position is not None:
            target_distance = baths[self.target_position].distanceToStart

            if self.distance_rail < target_distance:  # Moving RIGHT
                self.distance_rail = min(self.distance_rail + self.SPEED, target_distance)
                self.operation_timer += 1
                next_manip_index = self.ManipUUID
                if next_manip_index >= len(manipulators):
                    return
                #print(f"Running collision analysis for {self} and {manipulators[next_manip_index]}")
                if manipulators[next_manip_index].state not in (ManipulatorState.LIFTING,ManipulatorState.SUBMERGING,ManipulatorState.DRIPPING) and self.distance_rail >= manipulators[next_manip_index].distance_rail:
                    print(f"{self.ManipUUID} is on collision rightwise course with {manipulators[next_manip_index].ManipUUID}, evasive action taken")
                    manipulators[next_manip_index].distance_rail += manipulators[next_manip_index].SPEED
                elif manipulators[next_manip_index].state in (ManipulatorState.LIFTING,ManipulatorState.SUBMERGING,ManipulatorState.DRIPPING) and self.distance_rail >= manipulators[next_manip_index].distance_rail:
                    print(f"unable to perform rightwise evasion {self.ManipUUID} holding position")
                    self.distance_rail -= self.SPEED

            elif self.distance_rail > target_distance:  # Moving LEFT
                self.distance_rail = max(self.distance_rail - self.SPEED, target_distance)
                self.operation_timer += 1
                prev_manip_index = self.ManipUUID - 1
                if prev_manip_index >= 0:
                    if manipulators[prev_manip_index].state not in (
                    ManipulatorState.LIFTING, ManipulatorState.SUBMERGING,
                    ManipulatorState.DRIPPING) and self.distance_rail <= manipulators[prev_manip_index].distance_rail and prev_manip_index != self.ManipUUID:
                        print(
                            f"{self.ManipUUID} is on collision leftwise course with {manipulators[prev_manip_index].ManipUUID}, evasive action taken")
                        manipulators[prev_manip_index].distance_rail -= manipulators[prev_manip_index].SPEED
                    elif manipulators[prev_manip_index].state in (ManipulatorState.LIFTING, ManipulatorState.SUBMERGING,
                                                                  ManipulatorState.DRIPPING) and self.distance_rail <= \
                            manipulators[prev_manip_index].distance_rail:
                        print(f"Unable to perform leftwise evasion, {self.ManipUUID} holding position")
                        self.distance_rail += self.SPEED

            # Check if we reached the destination
            if self.distance_rail == target_distance:
                self.position = self.target_position
                self.operation_timer = 0
                self.state = ManipulatorState.IDLE

    def load_into_line(self):
        carrier = baths[self.position].containedCarrier
        carrier.get_current_step().completed = True
        carrier.currentStepIndex += 1
        self.heldCarrier = carrier
        baths[self.position].containedCarrier = None
        carrier.state = CarrierState.SERVICED
        self.move_to(carrier.get_current_step().bathID)

    def dismount_carrier(self):
        print(f"Manip {self.ManipUUID} offloading payload into {baths[self.target_position]}")
        self.state = ManipulatorState.SUBMERGING
        self.operation_timer = 0

    def lower_carrier(self):
        self.operation_timer += 1

        if self.operation_timer >= self.LIFT_TIME:
            bath = baths[self.target_position]
            bath.containedCarrier = self.heldCarrier
            bath.containedCarrier.state = CarrierState.BATHING
            print(f"Manip {self.ManipUUID} offloaded payload into {baths[self.target_position]}")
            self.heldCarrier = None
            self.target_position = None
            self.state = ManipulatorState.IDLE

    def mount_carrier(self):
        print(f"Manip {self.ManipUUID} loading payload from {baths[self.target_position]}, dripping expected")
        self.operation_timer = 0
        bath = baths[self.target_position]
        carrier = bath.containedCarrier
        carrier.state = CarrierState.DRIPPING
        self.state = ManipulatorState.LIFTING


    def lift_carrier(self):
        self.operation_timer += 1

        if self.operation_timer >= self.LIFT_TIME:
            bath = baths[self.target_position]
            carrier = bath.containedCarrier
            carrier.currentStepIndex += 1
            self.state = ManipulatorState.DRIPPING
            carrier.state = CarrierState.DRIPPING
            self.heldCarrier = carrier
            bath.containedCarrier = None
            self.operation_timer = 0
            print(f"Manip {self.ManipUUID} loaded payload from {baths[self.target_position]}, dripping to commence")

    def drip_carrier(self):
        self.operation_timer += 1

        if self.operation_timer >= self.heldCarrier.get_current_step().dripTime:
            self.operation_timer = 0
            self.heldCarrier.state = CarrierState.SERVICED
            self.move_to(self.heldCarrier.get_current_step().bathID)




class RecipeStep:
    DRIP_TIME = 20 # set to constant for now
    next_id = 0
    def __init__(self, bid, submersion_time):
        self.step_identifier = self.next_id
        RecipeStep.next_id += 1
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


class CarrierState(Enum):
    UNSERVICED = "Unserviced"
    TO_BE_LOADED = "Loading needed"
    BATHING = "Bathing"
    BATH_COMPLETED = "Completed bath, dripping required"
    BATH_SERVICED = "Manipulator tasked for dripping"
    SERVICED = "In transit"
    DRIPPING = "Dripping progress"

class Carrier:
    next_id = 1
    def __init__(self, procedure):
        self.carUUID = Carrier.next_id  # Unique identifier for the recipe
        Carrier.next_id += 1   # Unique identifier for the carrier
        self.requiredProcedure = procedure  # The Recipe the carrier follows
        self.currentStepIndex = 0  # Keeps track of the current step in the recipe
        self.state = CarrierState.UNSERVICED  # Default state
        self.operation_timer = 0 # keeps track of bathing time before switching states

    def __repr__(self):
        return f"Carrier(ID={self.carUUID}, Current Step: {self.currentStepIndex},state {self.state} ,Recipe: {self.requiredProcedure.name})"

    def get_current_step(self):
        """Returns the current recipe step."""
        return self.requiredProcedure.executionList[self.currentStepIndex]

    def update_bathe_timer(self):
        if self.state == CarrierState.BATHING:
            self.operation_timer += 1

            if self.operation_timer >= self.get_current_step().submersionTime:
                self.state = CarrierState.BATH_COMPLETED
                self.operation_timer = 0
        else:
            raise RuntimeError("ERROR: UNEXPECTED STATE")



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
    ([0,1,2,3,4,5], 0 ),
    ([4,5,6,7,8,9,10],  5 ),
    ([8,9,10,11,12,13], 9 ),
    ([12,13,14,15,16,17], 14 ),
    ([17,18,19,20,21,22,23], 18 )
]

recipe_template1 = RecipeTemplate("Test1", [(0, 0), (5, 1), (10, 3),  (12,5), (17,3), (23, 0)])
recipe_template2 = RecipeTemplate("Test2", [(0, 0), (5, 4), (10, 3), (12,5), (17,3), (23, 0)])
recipe_template3 = RecipeTemplate("Test3", [(0, 0), (5, 4), (10,2), (12,5) ,(17, 3), (23, 0)])
recipe_template4 = RecipeTemplate("Test4", [(0,0),(4,50),(8,60),(13,13),(17,10),(23,0)])


### Collection Instantiation & readback
baths = [
    Bath(name, distance / 1000, submergable=flag)  # convert to m
    for name, distance, flag in bathData
]


manipulators = [
    Manipulator(reach,startingPosition)
    for reach, startingPosition in manipData
]

#,Carrier(recipe_template1.create_instance())
carrier_definition = [Carrier(recipe_template1.create_instance()),Carrier(recipe_template4.create_instance()),Carrier(recipe_template2.create_instance()),Carrier(recipe_template3.create_instance())]
carriers_to_move = len(carrier_definition)
work_order = deque(list(reversed(carrier_definition)))
finished_carriers = deque()


def validate_work_order(manipulator_list, workorder_definition):
    # Map of which manipulators can reach which baths
    reachable_positions = {}
    for manipulator in manipulator_list:
        reachable_positions[manipulator.ManipUUID] = set(manipulator.operatingRange)  # Store as a set for faster lookup

    # Map of required bath positions for each carrier
    required_positions = defaultdict(list)
    for carrier in workorder_definition:
        for step in carrier.requiredProcedure.executionList:
            required_positions[carrier.carUUID].append(step.bathID)

    print("Reachable Positions:", reachable_positions)
    print("Required Positions:", required_positions)

    # Validation logic
    is_solvable = True
    for carrier_id, bath_sequence in required_positions.items():
        # Check start and end bath validity
        if bath_sequence[0] != 0 or bath_sequence[-1] != 23:
            print(f"Carrier {carrier_id} is invalid: does not start at bath[0] or end at bath[23]")
            is_solvable = False
            continue

        # Check if there is a valid connection between baths
        for i in range(len(bath_sequence) - 1):
            bath_a = bath_sequence[i]
            bath_b = bath_sequence[i + 1]
            if not any(bath_a in manipulator and bath_b in manipulator for manipulator in reachable_positions.values()):
                print(f"Carrier {carrier_id} is invalid: No manipulator can move from bath[{bath_a}] to bath[{bath_b}]")
                is_solvable = False
                break
        else:
            print(f"Carrier {carrier_id} is valid!")

    if not is_solvable:
        print("The initial bath and workorder definition is unsolvable, terminating")
        exit(1)


validate_work_order(manipulators,carrier_definition)

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
def move_manipulators():
    for manipulator in manipulators:
        if manipulator.state == ManipulatorState.MOVING:
            manipulator.update_movement()

        if manipulator.state == ManipulatorState.SUBMERGING:
            manipulator.lower_carrier()
            continue

        if manipulator.state == ManipulatorState.LIFTING:
            manipulator.lift_carrier()
            continue

        if manipulator.state == ManipulatorState.DRIPPING:
            manipulator.drip_carrier()
            continue

        if manipulator.position == 0 and baths[0].containedCarrier is not None and baths[0].containedCarrier.state.TO_BE_LOADED and manipulator.heldCarrier is None:
            manipulator.load_into_line()

        elif manipulator.position == manipulator.target_position and baths[manipulator.position].containedCarrier is None:
            manipulator.dismount_carrier()

        elif manipulator.position == manipulator.target_position and manipulator.heldCarrier is None and baths[manipulator.position].containedCarrier.state == CarrierState.BATH_SERVICED:
            manipulator.mount_carrier()


def check_baths():
    for manipulator in manipulators:
        for bath in baths:
            if bath.bathUUID in manipulator.operatingRange and bath.containedCarrier and bath.containedCarrier.state == CarrierState.UNSERVICED and manipulator.state == ManipulatorState.IDLE:
                print(f"Tasking manip {manipulator.ManipUUID} with servicing {bath.containedCarrier} at bath{bath}")
                bath.containedCarrier.state = CarrierState.TO_BE_LOADED
                manipulator.move_to(bath.bathUUID)
                continue

    for bath in baths:
        if bath.containedCarrier is not None and bath.containedCarrier.state == CarrierState.BATHING:
            bath.containedCarrier.update_bathe_timer()

    for manipulator in manipulators:
        for bath in baths:
            if bath.bathUUID in manipulator.operatingRange and bath.containedCarrier and bath.containedCarrier.state == CarrierState.BATH_COMPLETED and manipulator.state == ManipulatorState.IDLE:
                carrier = bath.containedCarrier  # Fetch the carrier inside the bath
                next_step_index = carrier.currentStepIndex + 1  # Predict next step index

                # Ensure next_step_index is within range
                if next_step_index < len(carrier.requiredProcedure.executionList):
                    next_bath_step = carrier.requiredProcedure.executionList[next_step_index].bathID
                    if next_bath_step in manipulator.operatingRange:
                        print(f"Tasking manip {manipulator.ManipUUID} with servicing {carrier} at bath {bath}")
                        carrier.state = CarrierState.BATH_SERVICED
                        manipulator.move_to(bath.bathUUID)
                    else:
                        print(
                            f"Manipulator {manipulator.ManipUUID} cannot service next target {next_bath_step} for {carrier}")
                else:
                    print(f"Carrier {carrier} has no further steps in its process.")


def update_simulation():
    move_manipulators()
    check_baths()

### Simulation
is_work_order_done = False
is_work_order_processed = False
step_counter = 0 # one step is equal to one second
deque_times = []

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
        deque_times.append(step_counter)

    update_simulation()

    step_counter += 1
    print(step_counter)

    if len(finished_carriers) >= carriers_to_move:
        is_work_order_done = True
        provide_states()
        print("Workorder processed successfully!")

    #overflow control
    if step_counter > 10000:
        is_work_order_done = True
        provide_states()
        print(carriers_to_move, len(finished_carriers))
        print("Simulation exceeds safe runtime, terminating")

if len(deque_times) > 1:
    time_diffs = [deque_times[i] - deque_times[i - 1] for i in range(1, len(deque_times))]
    avg_time_between = sum(time_diffs) / len(time_diffs)
else:
    avg_time_between = 0  # Default to 0 if there aren't enough values

print("Primary run completed")
print(f"Whole cycle completed in {step_counter}s, average time between carrier dequeing is {avg_time_between:.2f}s")
print("Loader state: " + str(work_order))
print("Off loader state: " + str(finished_carriers))
