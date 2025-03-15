import simpy
from ortools.sat.python import cp_model
import numpy as np


class LacquerOptimization:
    def __init__(self, num_frames, num_manipulators, bath_data, manipulator_data):
        self.model = cp_model.CpModel()
        self.num_frames = num_frames
        self.num_manipulators = num_manipulators
        self.bath_data = bath_data  # List of dicts with bath details
        self.manipulator_data = manipulator_data  # Dict with movement constraints
        self.start_times = {}
        self.travel_times = {bath['id']: bath['transfer_time'] for bath in bath_data}

        # Define decision variables for when each frame enters each bath
        for f in range(num_frames):
            for bath in bath_data:
                self.start_times[(f, bath['id'])] = self.model.NewIntVar(0, 10000, f"start_f{f}_b{bath['id']}")

        # Ensure sequence constraints per frame
        for f in range(num_frames):
            for i in range(1, len(bath_data)):
                prev_bath = bath_data[i - 1]['id']
                curr_bath = bath_data[i]['id']
                self.model.Add(
                    self.start_times[(f, curr_bath)] >= self.start_times[(f, prev_bath)] + bath_data[i - 1]['min_time'])
                self.model.Add(
                    self.start_times[(f, curr_bath)] >= self.start_times[(f, prev_bath)] + self.travel_times[prev_bath])

        # Manipulator constraints (avoiding collisions)
        for b in bath_data:
            for f1 in range(num_frames):
                for f2 in range(f1 + 1, num_frames):
                    self.model.AddAbsEquality(
                        self.start_times[(f1, b['id'])] - self.start_times[(f2, b['id'])],
                        self.model.NewIntVar(0, 10000, f"diff_f{f1}_f{f2}_b{b['id']}")
                    )

        # Objective function: minimize overall takt time
        self.takt_time = self.model.NewIntVar(0, 10000, "takt_time")
        for f in range(num_frames):
            last_bath_id = bath_data[-1]['id']
            self.model.Add(self.takt_time >= self.start_times[(f, last_bath_id)] + bath_data[-1]['max_time'])
        self.model.Minimize(self.takt_time)

    def solve(self):
        solver = cp_model.CpSolver()
        status = solver.Solve(self.model)
        if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            schedule = {f: [(b['id'], solver.Value(self.start_times[(f, b['id'])])) for b in self.bath_data] for f in
                        range(self.num_frames)}
            return schedule, solver.Value(self.takt_time)
        return None, None


# Example Data
bath_data = [
    {"id": 1, "name": "Entry", "min_time": 0, "max_time": 0, "drip_time": 0, "transfer_time": 0},
    {"id": 2, "name": "Hot Rinse", "min_time": 360, "max_time": 360, "drip_time": 30, "transfer_time": 2752},
    {"id": 3, "name": "Spray Degreasing", "min_time": 352, "max_time": 360, "drip_time": 30, "transfer_time": 3264},
    {"id": 4, "name": "Degreasing I", "min_time": 344, "max_time": 360, "drip_time": 30, "transfer_time": 3610},
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

if __name__ == "__main__":
    num_frames = 3
    num_manipulators = 3
    optimizer = LacquerOptimization(num_frames, num_manipulators, bath_data, manipulator_data)
    schedule, takt_time = optimizer.solve()
    if schedule:
        print("Optimal Schedule:", schedule)
        print("Minimum Takt Time:", takt_time)
    else:
        print("No feasible schedule found!")
