import simpy
from ortools.sat.python import cp_model

### Step 1: Define the Optimization Model (OR-Tools) ###
class LacquerOptimization:
    def __init__(self, num_frames, num_manipulators, bath_times, travel_times):
        self.model = cp_model.CpModel()
        self.num_frames = num_frames
        self.num_manipulators = num_manipulators
        self.bath_times = bath_times  # Time required in each bath
        self.travel_times = travel_times  # Time to move between baths

        # Decision Variables: When each frame enters each bath
        self.start_times = {}
        for f in range(num_frames):
            for b in range(len(bath_times)):
                self.start_times[(f, b)] = self.model.NewIntVar(0, 1000, f"start_f{f}_b{b}")

        # Manipulator movement variables
        self.manipulator_use = {}
        for m in range(num_manipulators):
            for f in range(num_frames):
                self.manipulator_use[(m, f)] = self.model.NewBoolVar(f"manipulator_{m}_frame_{f}")

        # Constraints: Frames must move in sequence
        for f in range(num_frames):
            for b in range(1, len(bath_times)):
                self.model.Add(self.start_times[(f, b)] >= self.start_times[(f, b - 1)] + bath_times[b - 1])

        # Constraints: Manipulator travel time
        for f in range(num_frames):
            for b in range(1, len(bath_times)):
                self.model.Add(self.start_times[(f, b)] >= self.start_times[(f, b - 1)] + travel_times[b - 1])

        # Collision Avoidance: No two frames in the same bath at the same time
        for b in range(len(bath_times)):
            for f1 in range(num_frames):
                for f2 in range(f1 + 1, num_frames):
                    self.model.AddAbsEquality(
                        self.start_times[(f1, b)] - self.start_times[(f2, b)],
                        self.model.NewIntVar(0, 1000, f"time_diff_f{f1}_f{f2}_b{b}")
                    )

        # Objective: Minimize overall takt time (last frame exit time)
        self.takt_time = self.model.NewIntVar(0, 1000, "takt_time")
        for f in range(num_frames):
            self.model.Add(self.takt_time >= self.start_times[(f, len(bath_times) - 1)] + bath_times[-1])
        self.model.Minimize(self.takt_time)

    def solve(self):
        solver = cp_model.CpSolver()
        status = solver.Solve(self.model)
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            schedule = {}
            for f in range(self.num_frames):
                schedule[f] = []
                for b in range(len(self.bath_times)):
                    start_time = solver.Value(self.start_times[(f, b)])
                    schedule[f].append((b, start_time))
            return schedule, solver.Value(self.takt_time)
        else:
            return None, None

### Step 2: Simulate Movement in SimPy ###
class LacquerSimulation:
    def __init__(self, env, schedule, bath_times):
        self.env = env
        self.schedule = schedule
        self.bath_times = bath_times

    def frame_process(self, frame_id):
        """SimPy process for moving a frame through the baths."""
        for bath_id, start_time in self.schedule[frame_id]:
            yield self.env.timeout(start_time - self.env.now)  # Wait for the scheduled start time
            print(f"Frame {frame_id} enters bath {bath_id} at time {self.env.now}")
            yield self.env.timeout(self.bath_times[bath_id])  # Simulate bath processing time
            print(f"Frame {frame_id} exits bath {bath_id} at time {self.env.now}")

    def run(self):
        """Start SimPy processes for all frames."""
        for frame_id in self.schedule:
            self.env.process(self.frame_process(frame_id))

### Run the Optimization and Simulation ###
if __name__ == "__main__":
    # Example input data
    num_frames = 3
    num_manipulators = 2
    bath_times = [90, 120, 180]  # Time in each bath
    travel_times = [20, 30, 40]  # Travel times between baths

    # Step 1: Solve optimization problem
    optimizer = LacquerOptimization(num_frames, num_manipulators, bath_times, travel_times)
    schedule, takt_time = optimizer.solve()

    if schedule:
        print("Optimal Schedule:", schedule)
        print("Minimum Takt Time:", takt_time)

        # Step 2: Run the simulation
        env = simpy.Environment()
        simulation = LacquerSimulation(env, schedule, bath_times)
        simulation.run()
        env.run()
    else:
        print("No feasible schedule found!")
