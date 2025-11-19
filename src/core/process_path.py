import math

def generate_dummy_path():
    path = []
    # Génère une courbe sinusoïdale
    for i in range(600):
        t = i * 0.01
        x = t * 4 - 20  # Étale le chemin sur l'axe X (de -20 à +100 environ)
        y = 10 * math.sin(t) # Oscillation sur l'axe Y
        path.append((x, y))
    return path