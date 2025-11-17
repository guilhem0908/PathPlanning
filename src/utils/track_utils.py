import csv


def load_track(csv_path):
    cones = []
    try:
        with open(csv_path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                tag = row["tag"]
                x = float(row["x"])
                y = float(row["y"])
                cones.append({
                    "tag": tag,
                    "x": x,
                    "y": y,
                })
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found {csv_path!r}")
    return cones


def compute_world_bounds(cones, margin = 2.0):
    xs = [c["x"] for c in cones]
    ys = [c["y"] for c in cones]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    return min_x - margin, max_x + margin, min_y - margin, max_y + margin,