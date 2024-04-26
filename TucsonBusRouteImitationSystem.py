import tkinter as tk
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

def a_star(start, dest):
    open_set = [(0, start)]
    came_from = {}
    g_score = {}
    g_score[start] = 0

    while open_set:
        current = open_set.pop(0)[1]
        if current == dest:
            return reconstruct_path(came_from, dest)

        for neighbor in stops[current].neighbors:
            tentative_g_score = g_score[current] + 1
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score = tentative_g_score + heuristic(neighbor, dest)
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

# Travel Time Calculation
def calculate_travel_time(route):
    travel_time = 0
    bus_changes = 0
    prev_stop = None

    for stop in route:
        if prev_stop:
            travel_time += 45 / 60  # Traffic light wait time (in minutes)
            if stop not in stops[prev_stop].neighbors:
                bus_changes += 1
        travel_time += 1  # Bus stop wait time (in minutes)
        prev_stop = stop

    travel_time += len(route) * 35 / 3600  # Travel time based on speed (in minutes)
    travel_time += bus_changes * 5  # Bus change time (in minutes)

    return travel_time

# GUI
class BusRouteGUI(tk.Tk):
    def __init__(self, stops):
        super().__init__()
        self.title("Tucson Suntran")
        self.geometry("800x600")

        self.frame = tk.Frame(self)
        self.frame.pack(pady=20)

        self.start_label = tk.Label(self.frame, text="Starting Location:")
        self.start_label.grid(row=0, column=0)
        self.start_entry = tk.Entry(self.frame)
        self.start_entry.grid(row=0, column=1)

        self.dest_label = tk.Label(self.frame, text="Final Destination:")
        self.dest_label.grid(row=1, column=0)
        self.dest_entry = tk.Entry(self.frame)
        self.dest_entry.grid(row=1, column=1)

        self.go_button = tk.Button(self.frame, text="GO", command=self.find_route)
        self.go_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.canvas = tk.Canvas(self, width=600, height=600)
        self.canvas.pack()

        self.result_label = tk.Label(self, text="")
        self.result_label.pack()

        self.stops = stops
        self.draw_bus_stops()  # Draw bus stops on the canvas

        # Bindings
        self.go_button.bind("<Return>", lambda event: self.find_route())
        self.bind("<Escape>", lambda event: self.attributes("-fullscreen", False))
        self.canvas.bind("<Motion>", self.show_stop_id)
        self.canvas.bind("<Leave>", self.hide_stop_id)  # Detect mouse leaving canvas

    def find_route(self):
        start = int(self.start_entry.get())
        dest = int(self.dest_entry.get())

        if start not in self.stops or dest not in self.stops:
            self.result_label.config(text="Invalid locations")
            return

        route = a_star(start, dest)
        if route:
            travel_time = calculate_travel_time(route)
            self.draw_route(route, start, dest)
            self.result_label.config(text=f"Optimal route: {' -> '.join(map(str, route))}\nTotal travel time: {travel_time:.2f} minutes")
        else:
            self.result_label.config(text="No route found")

    def draw_route(self, route, start, dest):
        self.canvas.delete("route")  # Clear only the route lines
        self.canvas.delete("start")  # Clear the start stop marker
        self.canvas.delete("end")  # Clear the end stop marker

        for i in range(len(route) - 1):
            start_stop = self.stops[route[i]]
            end_stop = self.stops[route[i + 1]]
            self.canvas.create_line(start_stop.x * 2 + 2.5, start_stop.y * 2 + 2.5, end_stop.x * 2 + 2.5, end_stop.y * 2 + 2.5, fill="red", width=2, tags="route")

        # Highlight the start and end stops
        self.canvas.create_oval(self.stops[start].x * 2, self.stops[start].y * 2, self.stops[start].x * 2 + 5, self.stops[start].y * 2 + 5, fill="green", tags="start")
        self.canvas.create_oval(self.stops[dest].x * 2, self.stops[dest].y * 2, self.stops[dest].x * 2 + 5, self.stops[dest].y * 2 + 5, fill="blue", tags="end")

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

# Main Function
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
        for other_stop in sorted_stops[:45]:  # Consider only the nearest 45 stops
            if other_stop != stop:
                neighbors.append(other_stop.id)
        stop.neighbors = neighbors

    return stops

if __name__ == "__main__":
    stops = initialize_stops()
    app = BusRouteGUI(stops)
    app.mainloop()
