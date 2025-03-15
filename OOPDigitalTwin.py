### Object definition
class Bath:
    next_id = 0  # Class variable for auto-incrementing ID

    def __init__(self, name, distance):
        self.bathUUID = Bath.next_id  # Assign auto-incremented ID
        Bath.next_id += 1  # Increment for the next instance
        self.name = name
        self.distanceToStart = distance  # Distance in m

    def __repr__(self):
        return f"Bath(ID={self.bathUUID}, Name={self.name}, Distance={self.distanceToStart} m)"


class Manipulator:
    # Constants
    LIFT_TIME = 16  # Time for lift in seconds (constant)
    SPEED = 0.6  # Speed of the manipulator (constant, 0.6 m/s)

    next_id = 0  # Class variable for auto-incrementing ID

    def __init__(self, reach, startingPosition):
        self.ManipUUID = Manipulator.next_id
        Manipulator.next_id += 1
        self.operatingRange = reach
        self.liftTime = Manipulator.LIFT_TIME
        self.movementSpeed = Manipulator.SPEED
        self.position = startingPosition

    def __repr__(self):
        return f"Manipulator(ID={self.ManipUUID}, Located at position: {self.position}, services operations {self.operatingRange}"


class Recipe:
    def __init__(self, uuid,name,operations):
        self.recpUUID = uuid
        self.name = name
        self.executionList = operations


class Carrier:
    def __init__(self, uuid, procedure):
        self.carUUID = uuid
        self.requiredProcedure = procedure

### Data definition

bathData = [
    ("Vstup do linky", 0),
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
    ("Výstup z linky", 60000)
]

manipData = [
    ([0,1,2,3,4], 0 ),
    ([4,5,6,7,8],  5 ),
    ([8,9,10,11,12], 9 ),
    ([13,14,15,16,17], 14 ),
    ([17,18,19,20,21,22,23], 18 )
]

### Instantiation
baths = [
    Bath(name, distance / 1000)  # convert to m
    for name, distance in bathData
]

manipulators = [
    Manipulator(reach,startingPosition)
    for reach, startingPosition in manipData
]

# Print the list of Bath objects
for bath in baths:
    print(bath)

for manipulator in manipulators:
    print(manipulator)
