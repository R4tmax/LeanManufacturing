class Bath:
    next_id = 0  # Class variable for auto-incrementing ID

    def __init__(self, name, distance):
        self.bathUUID = Bath.next_id  # Assign auto-incremented ID
        Bath.next_id += 1  # Increment for the next instance
        self.name = name
        self.distanceToStart = distance  # Distance in cm

    def __repr__(self):
        return f"Bath(ID={self.bathUUID}, Name={self.name}, Distance={self.distanceToStart} cm)"


class Manipulator:
    def __init__(self, uuid, reach, lift, speed):
        self.ManipUUID = uuid
        self.operatingRange = reach
        self.liftSpeed = lift
        self.movementSpeed = speed


class Recipe:
    def __init__(self, uuid,name,operations):
        self.recpUUID = uuid
        self.name = name
        self.executionList = operations


class Carrier:
    def __init__(self, uuid, procedure):
        self.carUUID = uuid
        self.requiredProcedure = procedure


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
]

# Creating the list of Bath objects
baths = [
    Bath(name, (distance // 10) // 10)  # Round down to nearest 10, then convert to cm
    for name, distance in bathData
]

# Print the list of Bath objects
for bath in baths:
    print(bath)