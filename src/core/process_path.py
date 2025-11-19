import numpy as np
import math
import random
from scipy import interpolate

# Paramètres RRT*
MAX_ITER = 3000
EXPAND_DIS = 2.0
PATH_RESOLUTION = 0.5
CONNECT_CIRCLE_DIST = 50.0
SAFE_RADIUS = 0.8  # Marge de sécurité autour des plots (rayons plot + voiture)


class RRTStar:
    """ Algorithme RRT* pour la planification de trajectoire """

    class Node:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.path_x = []
            self.path_y = []
            self.parent = None
            self.cost = 0.0

    def __init__(self, start, goal, obstacle_list, rand_area,
                 expand_dis=2.0, path_resolution=0.5, goal_sample_rate=10, max_iter=500):
        self.start = self.Node(start[0], start[1])
        self.end = self.Node(goal[0], goal[1])
        self.min_rand = rand_area[0]
        self.max_rand = rand_area[1]
        self.expand_dis = expand_dis
        self.path_resolution = path_resolution
        self.goal_sample_rate = goal_sample_rate
        self.max_iter = max_iter
        self.obstacle_list = obstacle_list
        self.node_list = []

    def plan(self):
        self.node_list = [self.start]
        for i in range(self.max_iter):
            if i % 500 == 0:
                print(f"RRT* Iteration: {i}/{self.max_iter}")

            rnd_node = self.get_random_node()
            nearest_ind = self.get_nearest_node_index(self.node_list, rnd_node)
            nearest_node = self.node_list[nearest_ind]

            new_node = self.steer(nearest_node, rnd_node, self.expand_dis)

            if self.check_collision(new_node, self.obstacle_list):
                near_inds = self.find_near_nodes(new_node)
                new_node = self.choose_parent(new_node, near_inds)
                if new_node:
                    self.node_list.append(new_node)
                    self.rewire(new_node, near_inds)

        # Fin des itérations, recherche du meilleur chemin vers le but
        last_index = self.search_best_goal_node()
        if last_index is not None:
            return self.generate_course(last_index)
        return None

    def choose_parent(self, new_node, near_inds):
        if not near_inds:
            return None
        costs = []
        for i in near_inds:
            near_node = self.node_list[i]
            t_node = self.steer(near_node, new_node)
            if t_node and self.check_collision(t_node, self.obstacle_list):
                costs.append(near_node.cost + self.calc_dist(near_node, new_node))
            else:
                costs.append(float("inf"))
        min_cost = min(costs)
        if min_cost == float("inf"): return None
        min_ind = near_inds[costs.index(min_cost)]
        new_node = self.steer(self.node_list[min_ind], new_node)
        new_node.parent = self.node_list[min_ind]
        new_node.cost = min_cost
        return new_node

    def search_best_goal_node(self):
        dist_to_goal_list = [self.calc_dist_to_goal(n.x, n.y) for n in self.node_list]
        # On cherche les nœuds proches de la fin
        goal_inds = [i for i, d in enumerate(dist_to_goal_list) if d <= self.expand_dis * 2]

        safe_goal_inds = []
        for i in goal_inds:
            t_node = self.steer(self.node_list[i], self.end)
            if self.check_collision(t_node, self.obstacle_list):
                safe_goal_inds.append(i)

        if not safe_goal_inds: return None
        min_cost = min([self.node_list[i].cost for i in safe_goal_inds])
        for i in safe_goal_inds:
            if self.node_list[i].cost == min_cost: return i
        return None

    def steer(self, from_node, to_node, extend_length=float("inf")):
        new_node = self.Node(from_node.x, from_node.y)
        d, theta = self.calc_distance_and_angle(from_node, to_node)
        new_node.path_x = [new_node.x]
        new_node.path_y = [new_node.y]
        if extend_length > d: extend_length = d
        n_expand = math.floor(extend_length / self.path_resolution)
        for _ in range(n_expand):
            new_node.x += self.path_resolution * math.cos(theta)
            new_node.y += self.path_resolution * math.sin(theta)
            new_node.path_x.append(new_node.x)
            new_node.path_y.append(new_node.y)
        d, _ = self.calc_distance_and_angle(new_node, to_node)
        if d <= self.path_resolution:
            new_node.path_x.append(to_node.x)
            new_node.path_y.append(to_node.y)
            new_node.x = to_node.x
            new_node.y = to_node.y
        new_node.parent = from_node
        return new_node

    def generate_course(self, goal_ind):
        path = [[self.end.x, self.end.y]]
        node = self.node_list[goal_ind]
        while node.parent is not None:
            path.append([node.x, node.y])
            node = node.parent
        path.append([node.x, node.y])
        return path

    def calc_dist_to_goal(self, x, y):
        return math.hypot(x - self.end.x, y - self.end.y)

    def get_random_node(self):
        if random.randint(0, 100) > self.goal_sample_rate:
            rnd = self.Node(random.uniform(self.min_rand, self.max_rand),
                            random.uniform(self.min_rand, self.max_rand))
        else:
            rnd = self.Node(self.end.x, self.end.y)
        return rnd

    def get_nearest_node_index(self, node_list, rnd_node):
        dlist = [(node.x - rnd_node.x) ** 2 + (node.y - rnd_node.y) ** 2 for node in node_list]
        return dlist.index(min(dlist))

    def check_collision(self, node, obstacle_list):
        if node is None: return False
        for (ox, oy, size) in obstacle_list:
            dx_list = [ox - x for x in node.path_x]
            dy_list = [oy - y for y in node.path_y]
            d_list = [dx * dx + dy * dy for (dx, dy) in zip(dx_list, dy_list)]
            if min(d_list) <= size ** 2:
                return False
        return True

    def find_near_nodes(self, new_node):
        nnode = len(self.node_list) + 1
        r = 50.0 * math.sqrt((math.log(nnode) / nnode))
        r = min(r, self.expand_dis * 5.0)
        dist_list = [(node.x - new_node.x) ** 2 + (node.y - new_node.y) ** 2 for node in self.node_list]
        near_inds = [i for i, d in enumerate(dist_list) if d <= r ** 2]
        return near_inds

    def rewire(self, new_node, near_inds):
        for i in near_inds:
            near_node = self.node_list[i]
            edge_node = self.steer(new_node, near_node)
            if not edge_node: continue
            edge_node.cost = new_node.cost + self.calc_dist(new_node, near_node)
            if near_node.cost > edge_node.cost:
                if self.check_collision(edge_node, self.obstacle_list):
                    near_node.parent = new_node
                    near_node.cost = edge_node.cost
                    near_node.path_x = edge_node.path_x
                    near_node.path_y = edge_node.path_y

    def calc_dist(self, n1, n2):
        return math.hypot(n1.x - n2.x, n1.y - n2.y)

    def calc_distance_and_angle(self, from_node, to_node):
        dx = to_node.x - from_node.x
        dy = to_node.y - from_node.y
        return math.hypot(dx, dy), math.atan2(dy, dx)


def smooth_path(path):
    """ Lissage B-Spline """
    x = [p[0] for p in path][::-1]  # Inverser pour Start -> Goal
    y = [p[1] for p in path][::-1]

    if len(x) < 3: return list(zip(x, y))

    try:
        tck, u = interpolate.splprep([x, y], s=1.0, k=3)
        u_new = np.linspace(0, 1, num=300)  # Plus de points pour l'animation fluide
        smooth_x, smooth_y = interpolate.splev(u_new, tck)
        return list(zip(smooth_x, smooth_y))
    except:
        return list(zip(x, y))
