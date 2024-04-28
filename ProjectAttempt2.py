import tkinter as tk
from tkinter import scrolledtext
import random
import math

# Data Structures
class BusStop:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.neighbors = []

    def __repr__(self):
        return str(self.id)

# Route Finding Algorithm
def heuristic(a, b):
    return math.sqrt((stops[a].x - stops[b].x)**2 + (stops[a].y - stops[b].y)**2)

def heuristic_least_bus_changes(a, b):
    if a == b:
        return 0
    else:
        return len([bus_stop for bus_stop in stops.values() if b in bus_stop.neighbors])

def a_star(start, dest, mode):
    open_set = [(0, start)]
    came_from = {}
    g_score = {}
    g_score[start] = 0

    heuristic_func = heuristic_least_bus_changes if mode == "Least Bus Changes" else heuristic

    while open_set:
        current = open_set.pop(0)[1]
        if current == dest:
            return reconstruct_path(came_from, dest)

        for neighbor in stops[current].neighbors:
            tentative_g_score = g_score[current] + 1
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score = tentative_g_score + heuristic_func(neighbor, dest)
                open_set.append((f_score, neighbor))
                open_set.sort(key=lambda x: x[0])

    return None

def reconstruct_path(came_from, dest):
    path = [dest]
    while dest in came_from:
        dest = came_from[dest]
        path.append(dest)
    path.reverse()
    return path

def calculate_travel_time(route, wait_time, mode):
    travel_time = 0
    bus_changes = 0
    prev_stop = None
    bus_change_stops = []

    for stop in route:
        if prev_stop:
            travel_time += 45 / 60  # Traffic light wait time (in minutes)
            if stop not in stops[prev_stop].neighbors:
                bus_changes += 1
                bus_change_stops.append(stop)
        travel_time += 1  # Bus stop wait time (in minutes)
        prev_stop = stop

    if mode == "Fastest Route":
        travel_time += len(route) * 35 / 3600  # Travel time based on speed (in minutes)
    elif mode == "Least Bus Changes":
        travel_time += bus_changes * 5  # Bus change time (in minutes)

    travel_time += wait_time  # Wait time for the first bus

    return travel_time, bus_change_stops

# GUI
class BusRouteGUI(tk.Tk):
    def __init__(self, stops):
        super().__init__()
        self.title("Tucson Suntran")
        self.geometry("1000x650")

        self.frame = tk.Frame(self)
        self.frame.pack(pady=20, side=tk.LEFT)

        self.start_label = tk.Label(self.frame, text="Starting Location:")
        self.start_label.grid(row=0, column=0)
        self.start_entry = tk.Entry(self.frame)
        self.start_entry.grid(row=0, column=1)

        self.dest_label = tk.Label(self.frame, text="Final Destination:")
        self.dest_label.grid(row=1, column=0)
        self.dest_entry = tk.Entry(self.frame)
        self.dest_entry.grid(row=1, column=1)

        self.mode_label = tk.Label(self.frame, text="Select Route Type:")
        self.mode_label.grid(row=2, column=0)
        self.mode_var = tk.StringVar(self.frame, "Fastest Route")
        self.mode_menu = tk.OptionMenu(self.frame, self.mode_var, "Fastest Route", "Least Bus Changes")
        self.mode_menu.grid(row=2, column=1)

        self.go_button = tk.Button(self.frame, text="GO", command=self.find_route)
        self.go_button.grid(row=3, column=0, columnspan=2, pady=10)

        self.bus_label = tk.Label(self.frame, text="Search Bus Route (1-49):")
        self.bus_label.grid(row=4, column=0)
        self.bus_entry = tk.Entry(self.frame)
        self.bus_entry.grid(row=4, column=1)

        self.bus_button = tk.Button(self.frame, text="Find Bus Route", command=self.find_bus_route)
        self.bus_button.grid(row=5, column=0, columnspan=2, pady=10)

        self.clear_button = tk.Button(self.frame, text="Clear", command=self.clear_routes)
        self.clear_button.grid(row=6, column=0, columnspan=2, pady=10)

        self.canvas = tk.Canvas(self, width=600, height=600)
        self.canvas.pack(side=tk.LEFT)

        self.result_text = scrolledtext.ScrolledText(self, width=40, height=20)
        self.result_text.pack(padx=10, pady=10, side=tk.RIGHT)

        self.stops = stops
        self.draw_bus_stops()  # Draw bus stops on the canvas
        self.bus_markers = {}  # Dictionary to store bus markers
        self.bus_change_stops = []  # List to store bus change stops

        # Bindings
        self.go_button.bind("<Return>", lambda event: self.find_route())
        self.bind("<Escape>", lambda event: self.attributes("-fullscreen", False))
        self.canvas.bind("<Motion>", self.show_stop_id)
        self.canvas.bind("<Leave>", self.hide_stop_id)  # Detect mouse leaving canvas

    def find_route(self):
        start = int(self.start_entry.get())
        dest = int(self.dest_entry.get())
        mode = self.mode_var.get()

        if start not in self.stops or dest not in self.stops:
            self.result_text.config(state=tk.NORMAL)
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "Invalid locations")
            self.result_text.config(state=tk.DISABLED)
            return

        route = a_star(start, dest, mode)

        if route:
            wait_time = calculate_first_bus_wait_time(route, start)
            travel_time, self.bus_change_stops = calculate_travel_time(route, wait_time, mode)
            self.draw_route(route, start, dest)
            route_info = f"Optimal route: {' -> '.join(map(str, route))}\nTotal travel time: {travel_time:.2f} minutes\nWait time for first bus: {wait_time:.2f} minutes\nStops visited: {len(route)}\nTraffic lights passed: {len(route) - 1}\nBus changes: {len(set(route)) - 1}\n"
            self.result_text.config(state=tk.NORMAL)
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, route_info)
            self.result_text.config(state=tk.DISABLED)
        else:
            self.result_text.config(state=tk.NORMAL)
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "No route found")
            self.result_text.config(state=tk.DISABLED)

    def find_bus_route(self):
        bus_number = self.bus_entry.get()
        if bus_number.isdigit():
            bus_number = int(bus_number)
            self.highlight_bus_route(bus_number)

    def draw_route(self, route, start, dest):
        self.canvas.delete("route")  # Clear only the route lines
        self.canvas.delete("start")  # Clear the start stop marker
        self.canvas.delete("end")  # Clear the end stop marker
        self.canvas.delete("bus_change")  # Clear previous bus change markers

        for i in range(len(route) - 1):
            start_stop = self.stops[route[i]]
            end_stop = self.stops[route[i + 1]]
            self.canvas.create_line(start_stop.x * 2 + 2.5, start_stop.y * 2 + 2.5, end_stop.x * 2 + 2.5, end_stop.y * 2 + 2.5, fill="red", width=2, tags="route")

        # Highlight the start and end stops
        self.canvas.create_oval(self.stops[start].x * 2, self.stops[start].y * 2, self.stops[start].x * 2 + 5, self.stops[start].y * 2 + 5, fill="green", tags="start")
        self.canvas.create_oval(self.stops[dest].x * 2, self.stops[dest].y * 2, self.stops[dest].x * 2 + 5, self.stops[dest].y * 2 + 5, fill="blue", tags="end")

        # Highlight bus change stops
        for stop_id in self.bus_change_stops:
            stop = self.stops[stop_id]
            self.canvas.create_oval(stop.x * 2, stop.y * 2, stop.x * 2 + 5, stop.y * 2 + 5, fill="yellow", tags="bus_change")

    def draw_bus_stops(self):
        for stop in self.stops.values():
            self.canvas.create_oval(stop.x * 2, stop.y * 2, stop.x * 2 + 5, stop.y * 2 + 5, fill="black", tags=f"stop_{stop.id}")

    def show_stop_id(self, event):
        item = self.canvas.find_closest(event.x, event.y)[0]
        tags = self.canvas.gettags(item)
        if "stop_" in "".join(tags):
            stop_id = int("".join(tags).split("_")[1])
            self.canvas.delete("stop_label")  # Remove existing labels
            if 0 <= event.x < self.canvas.winfo_width() and 0 <= event.y < self.canvas.winfo_height():  # Check if mouse pointer is within canvas boundaries
                self.canvas.create_text(event.x, event.y, text=stop_id, fill="orange", tags="stop_label")

    def hide_stop_id(self, event):
        self.canvas.delete("stop_label")  # Remove stop labels when mouse leaves canvas

    def highlight_bus_route(self, bus_number):
        self.canvas.delete("bus_route")  # Clear previously highlighted bus route
        self.canvas.delete("bus_marker")  # Clear previous bus markers

        # Get the bus route
        route_stops = [stop for stop in self.stops.values() if bus_number in stop.neighbors]

        if not route_stops:
            return

        # Draw the bus route
        for i in range(len(route_stops) - 1):
            start_stop = route_stops[i]
            end_stop = route_stops[i + 1]
            self.canvas.create_line(start_stop.x * 2 + 2.5, start_stop.y * 2 + 2.5, end_stop.x * 2 + 2.5, end_stop.y * 2 + 2.5, fill="purple", width=2, tags="bus_route")

        # Simulate the bus's current location (start on one side, end on another)
        current_stop = random.choice(route_stops)
        current_stop_coords = (current_stop.x * 2 + 2.5, current_stop.y * 2 + 2.5)
        self.canvas.create_text(current_stop_coords, text="X", fill="red", tags="bus_marker")

    def clear_routes(self):
        self.canvas.delete("route")  # Clear route lines
        self.canvas.delete("start")  # Clear start marker
        self.canvas.delete("end")  # Clear end marker
        self.canvas.delete("bus_route")  # Clear bus route lines
        self.canvas.delete("bus_marker")  # Clear bus markers
        self.canvas.delete("bus_change")  # Clear bus change markers

def initialize_stops():
    # Initialize bus stops with random coordinates
    stops = {}
    for i in range(1, 2219):
        x = random.randint(0, 299)
        y = random.randint(0, 299)
        stops[i] = BusStop(i, x, y)

    # Assign neighbors to each bus stop based on distance
    for stop in stops.values():
        neighbors = []
        sorted_stops = sorted(stops.values(), key=lambda s: math.sqrt((stop.x - s.x)**2 + (stop.y - s.y)**2))
        for other_stop in sorted_stops[:40]:  # Consider only the nearest 40 stops
            if other_stop != stop:
                neighbors.append(other_stop.id)
        stop.neighbors = neighbors

    return stops

def calculate_first_bus_wait_time(route, start):
    # Calculate travel time for the first bus to reach the user's starting stop
    wait_time = 0
    current_stop_index = 0
    for i, stop in enumerate(route):
        if stop == start:
            current_stop_index = i
            break
    for i in range(current_stop_index, len(route)):
        wait_time += 1  # Bus stop wait time (in minutes)
    wait_time += len(route[current_stop_index:]) * 35 / 3600  # Travel time based on speed (in minutes)
    return wait_time

if __name__ == "__main__":
    stops = initialize_stops()
    app = BusRouteGUI(stops)
    app.mainloop()
