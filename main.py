from enum import Enum
from collections import deque, defaultdict
"""
Code mimics the described assembly line problem and 
attempts to solve the planning and optimization issue by 
automatically solving for functional solutions of the work order,
while tracking movements of manipulators.
"""
### Object definition block
class Bath:
    """
    Definition of the bath object.
    For the purposes of this code, very little distinction is made between
    actual baths and 'special' positions within the assembly line.
    """
    next_id = 0  # Class variable for auto-incrementing ID

    def __init__(self, name, distance, submergable=True):
        self.bathUUID = Bath.next_id  # Assign auto-incremented ID
        Bath.next_id += 1  # Increment for the next instance
        self.name = name # plain text descriptor
        self.distanceToStart = distance  # Distance in m
        self.containedCarrier = None # Object of carrier held/submerged by line position
        self.isSubmergable = submergable # Flag denoting special positions in the line system such as loaders, deloaders, transport positions etc.

    def __repr__(self):
        return f"Bath(ID={self.bathUUID}, Name={self.name}, Distance={self.distanceToStart} m, currently has {self.containedCarrier} submerged)"

class ManipulatorState(Enum):
    """
    Enumeration of manipulator states.
    These are used for action decision logic within the simulation step.
    """
    IDLE = "Idle" #Manipulator does not carry a carrier and has on tasking
    MOVING = "Moving" #manipulator is changing positions
    LIFTING = "Lifting" #manipulator is lifting a frame from a submerged position
    DRIPPING = "Dripping" #manipulator has lifted a carrier and has to hold position until drip time is done
    SUBMERGING = "Submerging" #manipulator is putting a frame into a bath
    HOLDING = "Holding" #manipulator has a carrier, but possible target baths are occupied
    LOADING = "Loading" #manipulator is in a process of picking up from position bath[0] or is letting go of a carrier at baths[-1]

class Manipulator:
    """
    Manipulator class definition.
    Manipulator holds time definitions regarding operation speeds of lifting, putting down and moving the carriers.
    Take note that acceleration is not taken into account
    """
    # Constants
    LIFT_TIME = 16  # Time for lift in seconds (constant)
    SPEED = 0.6  # Speed of the manipulator (constant, 0.6 m/s)
    QUEUE_TIME = 1 # Time it takes to pickup and position baths[0] and let go at baths[-1]

    next_id = 1  # Class variable for auto-incrementing ID

    def __init__(self, reach, starting_position):
        self.ManipUUID = Manipulator.next_id # UUID
        Manipulator.next_id += 1
        self.operatingRange = reach # List of positions/operations which manipulator can service
        self.liftTime = Manipulator.LIFT_TIME # Lift/put down timer
        self.movementSpeed = Manipulator.SPEED # movement speed alongside the rail
        self.position = starting_position # Position in which manipulators 'begins' the assembly line run
        self.heldCarrier = None # Object of carrier with product to undergo varnish
        self.distance_rail = Manipulator.calculate_rail_meters(self) # Distance in meters alongside the line
        self.state = ManipulatorState.IDLE # see ManipulatorState
        self.target_position = None  # Track where the manipulator is moving (ie. to which bath the manipulator needs to get to, in order to 'solve' next procedure step for carrier
        self.operation_timer = 0 # tracks length of current manipulator state for relevant operations such as dripping

    def __repr__(self):
        return (f"Manipulator(ID={self.ManipUUID} is performing {self.state} at:"
                f" position: {self.position} and meterwise position of {self.distance_rail}m,"
                f" services operations {self.operatingRange}, currently holds the {self.heldCarrier}")

    def move_to(self, new_position):
        """
        This function is called in simulation steps whenever new carrier task becomes available
        :param new_position: target bath/destination which is desired to be reached
        :return: side effects - modify the target position attribute, immediately calls the update_movement function
        """
        if new_position in self.operatingRange:
            print(f"Manipulator {self.ManipUUID} moving from {self.position} to {new_position}")
            self.state = ManipulatorState.MOVING
            self.target_position = new_position
            self.update_movement()
        else:
            print(f"Manipulator {self.ManipUUID} cannot move to {new_position}, out of range.")

    def calculate_rail_meters(self):
        """
        :return: Distance in meters alongside the line rails given the distance listed for bath above which manipulator 'begins' operations
        """
        return baths[self.position].distanceToStart

    def update_movement(self):
        """
        Primary movement function, called in each time step for every moving manipulator during simulation step.
        Modifies distance_rail in a desired detection and handles collisions by moving idle manipulators or suspending operations when no other solution is
        available.
        :return: side effects - changes the distance_rail parameter, updates position/bath index where appropriate, handles collision detection
        """
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
                prev_manip_index = self.ManipUUID - 2
                if prev_manip_index > 1:
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


    def load_into_line(self):
        """
        Called in simulation step to handle initial carrier processing from the loader into the varnish line.
        :return: side effect - initiates movement for manipulator responsible for 'loading' a carrier into varnishing line
        """
        carrier = baths[self.position].containedCarrier
        carrier.get_current_step().completed = True
        carrier.currentStepIndex += 1
        self.heldCarrier = carrier
        baths[self.position].containedCarrier = None
        carrier.state = CarrierState.SERVICED
        self.move_to(carrier.get_current_step().bathID)

    def dismount_carrier(self):
        """
        Initiates lowering of the carriers
        """
        print(f"Manip {self.ManipUUID} offloading payload into {baths[self.target_position]}")
        self.state = ManipulatorState.SUBMERGING
        self.operation_timer = 0

    def lower_carrier(self):
        """
        Handles the process of a time dependent carrier lowering.
        Updates the carrier position/relation when appropriate and frees the manipulator
        for further tasking.
        """
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
        """
        Initiates the process of lifting carrier from bath.
        """
        print(f"Manip {self.ManipUUID} loading payload from {baths[self.target_position]}, dripping expected")
        self.operation_timer = 0
        bath = baths[self.target_position]
        carrier = bath.containedCarrier
        carrier.state = CarrierState.DRIPPING
        self.state = ManipulatorState.LIFTING


    def lift_carrier(self):
        """
        Handles the simulation of lifting the carrier from a bath, after the submerge time is fulfilled.
        When the lifting is completed, switches the states over to the dripping phase.
        """
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
        """
        Handles the dripping timeout and then sets manipulator moving towards next step in the process.
        """
        self.operation_timer += 1

        if self.operation_timer >= self.heldCarrier.get_current_step().dripTime:
            self.operation_timer = 0
            self.heldCarrier.state = CarrierState.SERVICED
            self.move_to(self.heldCarrier.get_current_step().bathID)


class RecipeStep:
    """
    Definition of a procedure component defined by target bath and required times.
    """
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
    """
    Template responsible for instantiation of
    procedure lists for carriers.
    """
    def __init__(self, name, step_definitions):
        self.name = name  # Name of the recipe template
        self.step_definitions = step_definitions  # List of (bath_id, submersion_time) tuples

    def create_instance(self):
        """Generate a new Recipe instance with unique steps."""
        steps = [RecipeStep(bath_id, submersion_time) for bath_id, submersion_time in self.step_definitions]
        return Recipe(self.name, steps)


class Recipe:
    """
    Master Recipe definition.
    Individual steps are given as list of operations (see RecipeStep)
    """
    next_id = 1  # Class variable for auto-incrementing ID
    def __init__(self, name, operations):
        self.recpUUID = Recipe.next_id  # Unique identifier for the recipe
        Recipe.next_id += 1
        self.name = name  # Name of the recipe
        self.executionList = operations  # List of RecipeStep objects

    def __repr__(self):
        return f"Recipe(ID={self.recpUUID}, Name={self.name}, Steps={len(self.executionList)})"


class CarrierState(Enum):
    """
    Definition of possible carrier states, together with manipulator states,
    they dictate the simulation decision logic
    """
    UNSERVICED = "Unserviced" # Carrier is not yet loaded into varnish line
    TO_BE_LOADED = "Loading needed" # Carrier received manipulator tasking
    BATHING = "Bathing" # Carrier is submerged in a bath
    BATH_COMPLETED = "Completed bath, dripping required" # required process line finish
    BATH_SERVICED = "Manipulator tasked for dripping" # Manipulator has been assigned to completed bath time and is about to be lifted and dripped
    SERVICED = "In transit" #
    DRIPPING = "Dripping progress" # Carrier is currently being dripped

class Carrier:
    """
    Definition of carriers 'carrying' products for varnish.
    """
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
        """
        Returns the current recipe step.
        i.e. function facilitates retrieval of current RecipeStep based on the progression
        of the manufacturing process
        """
        return self.requiredProcedure.executionList[self.currentStepIndex]

    def update_bathe_timer(self):
        """
        Called by the simulation steps to update timers on submerged carriers, checking whether
        the process is finished or not
        """
        if self.state == CarrierState.BATHING:
            self.operation_timer += 1

            if self.operation_timer >= self.get_current_step().submersionTime:
                self.state = CarrierState.BATH_COMPLETED
                self.operation_timer = 0
        else:
            raise RuntimeError("ERROR: UNEXPECTED STATE")


"""
In this section of the code, input parameters of the code are entered and 
then processed by object constructors.
"""
### Data & condition definition

"""
Specification of the line baths and distances.
Indexes of baths are assigned automatically based on the input order.
"""
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

"""
Specifies desired manipulators, their assigned range, and starting position.
"""
manipData = [
    ([0,1,2,3,4,5], 0 ),
    ([4,5,6,7,8,9,10],  5 ),
    ([8,9,10,11,12,13], 9 ),
    ([12,13,14,15,16,17], 14 ),
    ([17,18,19,20,21,22,23], 18 )
]

"""
Defines individual recipes which need to be processed during the assembly line run. 
Take note that the name definition is of no consequence and just helps to navigate the printed outputs. 
The definitions of individual steps is a list of tuple pairs position(bathID) <-> submerge time.  
"""
recipe_template1 = RecipeTemplate("Test1", [(0, 0), (5, 1), (10, 3),  (12,5), (17,3), (23, 0)])
recipe_template2 = RecipeTemplate("Test2", [(0, 0), (5, 4), (10, 3), (12,5), (17,3), (23, 0)])
recipe_template3 = RecipeTemplate("Test3", [(0, 0), (5, 4), (10,2), (12,5) ,(17, 3), (23, 0)])
recipe_template4 = RecipeTemplate("Test4", [(0,0),(4,50),(8,60),(13,13),(17,10),(23,0)])


### Collection Instantiation & readback
"""
Object instantiation is handled in this block.
"""
baths = [
    Bath(name, distance / 1000, submergable=flag)  # converts to m from original measurement unit
    for name, distance, flag in bathData
]


manipulators = [
    Manipulator(reach,startingPosition)
    for reach, startingPosition in manipData
]

"""
Carrier definition corresponds to the 'list' of carriers/products which need to be serviced (and their accompanying procedure).
This is then converted to a stack data structure under the FIFO ruleset.
"""
carrier_definition = [Carrier(recipe_template1.create_instance()),Carrier(recipe_template4.create_instance()),Carrier(recipe_template2.create_instance()),Carrier(recipe_template3.create_instance()),Carrier(recipe_template1.create_instance())]
carriers_to_move = len(carrier_definition)
work_order = deque(list(reversed(carrier_definition)))
finished_carriers = deque()

"""
Code runs this function before proceeding to the simulation step. 
Terminates if the configuration is unsolvable.
"""
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


"""
Auxiliary printing functions
"""
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
    """
    In this function, for each manipulator in a line, a state is checked
    and a corresponding function is called to update and/or switch operations.
    """
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
    """
    In this function, each bath is checked against its respective manipulator operating range twice.
    First, whether a loader has a new carrier available, secondly, whether carrier is ready to be lifted and proceed to a new step.
    Furthermore,  bathing timers are updated from this function call.
    """
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
"""
Simulation step of the program. 
The primary simulation loop first handles initial and exit stack states,
the loop is popping new carrier into a line every time the first slot of the line is available, until there are
carriers to be processed.

Finally the update_simulation function is called which by extension refers to check_baths and move_manipulators functions.
As such, on every simulation loop iteration (which by design corresponds to one second) every manipulator and bath is checked for potential
task allocations and status updates. 

Choice of the time unit is mostly arbitrary, but changing it would require recalculating (or adding a dynamic mechanism for doing so) relevant datum parameters. 
Since each validation is automatic, the overhead on manipulator assignments is very low. 
It is up to debate, whether the approach isn't "too greedy" from the optimization perspective. 
"""
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

        if len(deque_times) > 1:
            time_diffs = [deque_times[i] - deque_times[i - 1] for i in range(1, len(deque_times))]
            avg_time_between = sum(time_diffs) / len(time_diffs)
        else:
            avg_time_between = 0  # Default to 0 if there aren't enough values


        print(
            f"Whole cycle completed in {step_counter}s, average time between carrier dequeing is {avg_time_between:.2f}s")
        print("Loader state: " + str(work_order))
        print("Off loader state: " + str(finished_carriers))

    #overflow control
    if step_counter > 10000:
        is_work_order_done = True
        provide_states()
        print(carriers_to_move, len(finished_carriers))
        print("Simulation exceeds safe runtime, terminating")
        print("This indicates some unexpected error")


