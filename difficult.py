import csv
import matplotlib.pyplot as plt

x_blue = []
y_blue = []
x_yellow = []
y_yellow = []
x_orange = []
y_orange = []
x_start = []
y_start = []

with open("hairpins_increasing_difficulty.csv", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        x = float(row["x"])
        y = float(row["y"])
        tag = row["tag"].lower()

        if tag == "blue":
            x_blue.append(x)
            y_blue.append(y)
        elif tag == "yellow":
            x_yellow.append(x)
            y_yellow.append(y)
        elif tag == "big_orange":
            x_orange.append(x)
            y_orange.append(y)
        elif tag == "car_start":
            x_start.append(x)
            y_start.append(y)

plt.figure()

if x_blue:
    plt.scatter(x_blue, y_blue, label="blue")
if x_yellow:
    plt.scatter(x_yellow, y_yellow, label="yellow")
if x_orange:
    plt.scatter(x_orange, y_orange, label="big_orange")
if x_start:
    plt.scatter(x_start, y_start, label="car_start")

plt.xlabel("x")
plt.ylabel("y")
plt.title("hairpins_increasing_difficulty")
plt.axis("equal")
plt.grid(True)
plt.legend()

# Sauvegarde en PNG dans le projet
plt.savefig("hairpins_increasing_difficulty.png", dpi=300, bbox_inches="tight")

# Optionnel : afficher aussi
plt.show()
