import csv
import matplotlib.pyplot as plt

x_blue = []
y_blue = []
x_yellow = []
y_yellow = []

with open("small_track.csv", newline="") as f:
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

plt.figure()
if x_blue:
    plt.scatter(x_blue, y_blue, label="blue")
if x_yellow:
    plt.scatter(x_yellow, y_yellow, label="yellow")

plt.xlabel("x")
plt.ylabel("y")
plt.title("Plots du fichier small_track.csv")
plt.axis("equal")
plt.grid(True)
plt.legend()

# >>> Sauvegarde en PNG dans ton projet <<<
plt.savefig("small_track.png", dpi=300, bbox_inches="tight")

# (optionnel) afficher la fenêtre aussi
plt.show()
