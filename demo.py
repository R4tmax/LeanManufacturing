import simpy
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from ortools.sat.python import cp_model
import numpy as np


class LacquerOptimization:
    def __init__(self, num_frames, bath_times, travel_times):
        self.model = cp_model.CpModel()
        self.num_frames = num_frames
        self.bath_times = bath_times
        self.travel_times = travel_times
        self.start_times = {}
        for f in range(num_frames):
            for b in range(len(bath_times)):
                self.start_times[(f, b)] = self.model.NewIntVar(0, 1000, f"start_f{f}_b{b}")
        for f in range(num_frames):
            for b in range(1, len(bath_times)):
                self.model.Add(self.start_times[(f, b)] >= self.start_times[(f, b - 1)] + bath_times[b - 1])
                self.model.Add(self.start_times[(f, b)] >= self.start_times[(f, b - 1)] + travel_times[b - 1])
        self.takt_time = self.model.NewIntVar(0, 1000, "takt_time")
        for f in range(num_frames):
            self.model.Add(self.takt_time >= self.start_times[(f, len(bath_times) - 1)] + bath_times[-1])
        self.model.Minimize(self.takt_time)

    def solve(self):
        solver = cp_model.CpSolver()
        status = solver.Solve(self.model)
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            schedule = {f: [(b, solver.Value(self.start_times[(f, b)])) for b in range(len(self.bath_times))] for f in
                        range(self.num_frames)}
            return schedule, solver.Value(self.takt_time)
        return None, None


class LacquerSimulation:
    def __init__(self, env, schedule, bath_times, update_func):
        self.env = env
        self.schedule = schedule
        self.bath_times = bath_times
        self.update_func = update_func

    def frame_process(self, frame_id):
        for bath_id, start_time in self.schedule[frame_id]:
            yield self.env.timeout(start_time - self.env.now)
            self.update_func(frame_id, bath_id, self.env.now)
            yield self.env.timeout(self.bath_times[bath_id])

    def run(self):
        for frame_id in self.schedule:
            self.env.process(self.frame_process(frame_id))


def visualize_simulation(schedule, bath_times):
    fig, ax = plt.subplots()
    num_frames = len(schedule)
    num_baths = len(bath_times)
    positions = {f: -1 for f in schedule}
    colors = plt.cm.viridis(np.linspace(0, 1, num_frames))
    bars = [ax.barh(f, 1, left=0, color=colors[f]) for f in range(num_frames)]

    def update(frame_id, bath_id, time):
        positions[frame_id] = bath_id

    def animate(i):
        for f in range(num_frames):
            bars[f][0].set_x(positions[f])

    env = simpy.Environment()
    simulation = LacquerSimulation(env, schedule, bath_times, update)
    simulation.run()
    env.run()
    ani = animation.FuncAnimation(fig, animate, frames=100, interval=200)
    ax.set_xlim(-1, num_baths)
    ax.set_ylim(-1, num_frames)
    ax.set_xlabel("Bath ID")
    ax.set_ylabel("Frame ID")
    ax.set_title("Lacquer Line Simulation")
    plt.show()


if __name__ == "__main__":
    num_frames = 3
    bath_times = [90, 120, 180]
    travel_times = [20, 30, 40]
    optimizer = LacquerOptimization(num_frames, bath_times, travel_times)
    schedule, takt_time = optimizer.solve()
    if schedule:
        print("Optimal Schedule:", schedule)
        print("Minimum Takt Time:", takt_time)
        visualize_simulation(schedule, bath_times)
    else:
        print("No feasible schedule found!")