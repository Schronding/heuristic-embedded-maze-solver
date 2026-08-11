from collections import deque
import heapq

START, END, WALL, PATH = 'S', 'E', '#', ' '

def _get_grid_neighbors(node, maze):
    neighbors, (r, c) = [], node
    height, width = len(maze), len(maze[0])
    if r > 0 and maze[r - 1][c] != WALL: neighbors.append((r - 2, c))
    if r < height - 1 and maze[r + 1][c] != WALL: neighbors.append((r + 2, c))
    if c > 0 and maze[r][c - 1] != WALL: neighbors.append((r, c - 2))
    if c < width - 1 and maze[r][c + 1] != WALL: neighbors.append((r, c + 2))
    return neighbors

def find_path_bfs(maze, start, end):
    queue = deque([(start, [start])])
    visited = {start}
    while queue:
        node, path = queue.popleft()
        if node == end: 
            return path, visited, len(path)
        for neighbor in _get_grid_neighbors(node, maze):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    return None, visited, float('inf')

def find_path_dfs(maze, start, end):
    stack = [(start, [start])]
    visited = {start}
    while stack:
        node, path = stack.pop()
        if node == end: 
            return path, visited, len(path)
        for neighbor in _get_grid_neighbors(node, maze):
            if neighbor not in visited:
                visited.add(neighbor)
                stack.append((neighbor, path + [neighbor]))
    return None, visited, float('inf')

def find_path_dijkstra(maze, start, end, turn_cost=0):
    pq = [(0, start, [start], None)]
    visited_costs = {}
    while pq:
        cost, node, path, prev_dir = heapq.heappop(pq)
        if (node, prev_dir) in visited_costs and visited_costs[(node, prev_dir)] <= cost: continue
        visited_costs[(node, prev_dir)] = cost
        if node == end:
            return path, set(n[0] for n in visited_costs), cost
        for neighbor in _get_grid_neighbors(node, maze):
            dr, dc = neighbor[0] - node[0], neighbor[1] - node[1]
            if dr == 2: curr_dir = 2
            elif dr == -2: curr_dir = 0
            elif dc == 2: curr_dir = 1
            else: curr_dir = 3
            move_cost = 1
            penalty = turn_cost if prev_dir is not None and curr_dir != prev_dir else 0
            new_cost = cost + move_cost + penalty
            heapq.heappush(pq, (new_cost, neighbor, path + [neighbor], curr_dir))
    return None, set(n[0] for n in visited_costs), float('inf')

def _manhattan_heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def find_path_a_star(maze, start, end, turn_cost=0):
    pq = [(_manhattan_heuristic(start, end), 0, start, [start], None)]
    visited_costs = {}
    while pq:
        _, g_cost, node, path, prev_dir = heapq.heappop(pq)
        if (node, prev_dir) in visited_costs and visited_costs[(node, prev_dir)] <= g_cost: continue
        visited_costs[(node, prev_dir)] = g_cost
        if node == end:
            return path, set(n[0] for n in visited_costs), g_cost
        for neighbor in _get_grid_neighbors(node, maze):
            dr, dc = neighbor[0] - node[0], neighbor[1] - node[1]
            if dr == 2: curr_dir = 2
            elif dr == -2: curr_dir = 0
            elif dc == 2: curr_dir = 1
            else: curr_dir = 3
            move_cost = 1
            penalty = turn_cost if prev_dir is not None and curr_dir != prev_dir else 0
            new_g_cost = g_cost + move_cost + penalty
            if (neighbor, curr_dir) not in visited_costs or new_g_cost < visited_costs[(neighbor, curr_dir)]:
                f_cost = new_g_cost + _manhattan_heuristic(neighbor, end)
                heapq.heappush(pq, (f_cost, new_g_cost, neighbor, path + [neighbor], curr_dir))
    return None, set(n[0] for n in visited_costs), float('inf')

def find_path_flood_fill(maze, start, end):
    distances = [[-1 for _ in row] for row in maze]
    queue = deque([(end, 0)])
    if distances[end[0]][end[1]] == -1:
        distances[end[0]][end[1]] = 0
    visited_ff = {end}
    while queue:
        node, dist = queue.popleft()
        for neighbor in _get_grid_neighbors(node, maze):
            if distances[neighbor[0]][neighbor[1]] == -1:
                visited_ff.add(neighbor)
                distances[neighbor[0]][neighbor[1]] = dist + 1
                queue.append((neighbor, dist + 1))
    if distances[start[0]][start[1]] == -1: return None, visited_ff
    path = [start]
    curr_node = start
    while curr_node != end:
        found_next = False
        for neighbor in _get_grid_neighbors(curr_node, maze):
            if distances[neighbor[0]][neighbor[1]] == distances[curr_node[0]][curr_node[1]] - 1:
                path.append(neighbor)
                curr_node = neighbor
                found_next = True
                break
        if not found_next: return None, visited_ff, float('inf')
    return path, visited_ff, len(path)

def _wall_follower(maze, start, end, hand_direction):
    dirs = [(-2, 0), (0, 2), (2, 0), (0, -2)]
    pos, orientation = start, 2 
    path = [pos]
    
    hand_turn = 1 if hand_direction == 'right' else -1
    max_steps = len(maze) * len(maze[0]) * 2 

    for _ in range(max_steps):
        if pos == end:
            return path, set(path), len(path)

        feel_orientation = (orientation + hand_turn + 4) % 4
        
        r_wall, c_wall = pos[0] + dirs[feel_orientation][0]//2, pos[1] + dirs[feel_orientation][1]//2
        if not (0 <= r_wall < len(maze) and 0 <= c_wall < len(maze[0])):
             return None, set(path), float('inf')
        
        wall_beside = maze[r_wall][c_wall] == WALL
        
        if wall_beside:
            r_front, c_front = pos[0] + dirs[orientation][0]//2, pos[1] + dirs[orientation][1]//2
            if not (0 <= r_front < len(maze) and 0 <= c_front < len(maze[0])):
                return None, set(path), float('inf')

            if maze[r_front][c_front] != WALL:
                pos = (pos[0] + dirs[orientation][0], pos[1] + dirs[orientation][1])
                path.append(pos)
            else:
                orientation = (orientation - hand_turn + 4) % 4
        else:
            orientation = feel_orientation
            pos = (pos[0] + dirs[orientation][0], pos[1] + dirs[orientation][1])
            path.append(pos)
            
    return None, set(path), float('inf')

def find_path_wall_follower_right(maze, start, end):
    return _wall_follower(maze, start, end, 'right')

def find_path_wall_follower_left(maze, start, end):
    return _wall_follower(maze, start, end, 'left')