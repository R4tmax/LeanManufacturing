# Import necessary libraries
from ortools.sat.python import cp_model

# Re-run the updated class with the correct imports
class LacquerOptimizationWithRecipes:
    def __init__(self, num_frames, num_manipulators, bath_data, manipulator_data, frame_recipes):
        self.model = cp_model.CpModel()
        self.num_frames = num_frames
        self.num_manipulators = num_manipulators
        self.bath_data = {b["id"]: b for b in bath_data}  # Bath details by ID
        self.manipulator_data = manipulator_data  # Movement constraints
        self.frame_recipes = frame_recipes  # Recipe assigned per frame

        self.start_times = {}
        self.travel_times = {bath["id"]: bath["transfer_time"] for bath in bath_data}

        # Define decision variables for when each frame enters each bath (based on its assigned recipe)
        for f, recipe in frame_recipes.items():
            for bath_id, time_in_bath in recipe:  # Recipe defines bath sequence and required time
                self.start_times[(f, bath_id)] = self.model.NewIntVar(0, 10000, f"start_f{f}_b{bath_id}")

        # Ensure sequence constraints per frame (frames must move in order)
        for f, recipe in frame_recipes.items():
            for i in range(1, len(recipe)):
                prev_bath_id, prev_time = recipe[i - 1]
                curr_bath_id, curr_time = recipe[i]

                # Ensure frame enters the next bath after finishing the previous one and traveling the distance
                self.model.Add(self.start_times[(f, curr_bath_id)] >=
                               self.start_times[(f, prev_bath_id)] + prev_time + self.travel_times[prev_bath_id])

        # Manipulator constraints (avoid collisions in the same bath at the same time)
        for bath_id in self.bath_data:
            for f1 in range(num_frames):
                for f2 in range(f1 + 1, num_frames):
                    if bath_id in [b[0] for b in frame_recipes[f1]] and bath_id in [b[0] for b in frame_recipes[f2]]:
                        self.model.AddAbsEquality(
                            self.start_times[(f1, bath_id)] - self.start_times[(f2, bath_id)],
                            self.model.NewIntVar(0, 10000, f"diff_f{f1}_f{f2}_b{bath_id}")
                        )

        # Objective function: minimize overall takt time
        self.takt_time = self.model.NewIntVar(0, 10000, "takt_time")
        for f, recipe in frame_recipes.items():
            last_bath_id, last_time = recipe[-1]
            self.model.Add(self.takt_time >= self.start_times[(f, last_bath_id)] + last_time)

        self.model.Minimize(self.takt_time)

    def solve(self):
        solver = cp_model.CpSolver()
        status = solver.Solve(self.model)
        if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            schedule = {f: [(b[0], solver.Value(self.start_times[(f, b[0])])) for b in self.frame_recipes[f]] for f in range(self.num_frames)}
            return schedule, solver.Value(self.takt_time)
        return None, None

# Example Data
bath_data = [
    {"id": 1, "name": "Entry", "transfer_time": 0},
    {"id": 2, "name": "Hot Rinse", "transfer_time": 2752},
    {"id": 3, "name": "Spray Degreasing", "transfer_time": 3264},
    {"id": 4, "name": "Degreasing I", "transfer_time": 3610},
]

manipulator_data = {
    "speed_m_per_s": 0.583,
    "lift_speed_m_per_s": 0.2,
    "acceleration_s": 2,
    "lift_acceleration_s": 1,
    "zones": {
        1: ["Entry", "Operation 3"],
        2: ["Operation 3", "Operation 7"],
        3: ["Operation 7", "Operation 11"]
    }
}

# Example frame recipes (Receptura) - Each frame follows a specific sequence of baths with a defined time
frame_recipes = {
    0: [(1, 0), (2, 360), (4, 344)],  # Frame 0 follows a specific recipe
    1: [(1, 0), (3, 352), (4, 344)],  # Frame 1 has a different process
    2: [(1, 0), (2, 360), (3, 352)],  # Frame 2 follows another variant
}

# Run the updated optimizer
num_frames = 3
num_manipulators = 3
optimizer = LacquerOptimizationWithRecipes(num_frames, num_manipulators, bath_data, manipulator_data, frame_recipes)
schedule, takt_time = optimizer.solve()

print(schedule, takt_time)

