import time

WALL_CHAR = '#'
PATH_CHAR = ' '
START_CHAR = 'S'
END_CHAR = 'E'

WALL = 1
PATH = 0
START = 2
END = 3

DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
DIR_TO_IDX = {(-1, 0): 0, (0, 1): 1, (1, 0): 2, (0, -1): 3}

def parse_maze(maze_str_list):
    numeric_map = []
    start_pos = None
    end_pos = None
    height = len(maze_str_list)
    width = len(maze_str_list[0]) if height > 0 else 0

    for r_idx, row_str in enumerate(maze_str_list):
        if len(row_str) != width:
            raise ValueError("Rows must have the same length.")
        row_num = []
        for c_idx, char in enumerate(row_str):
            if char == WALL_CHAR:
                row_num.append(WALL)
            elif char == PATH_CHAR:
                row_num.append(PATH)
            elif char == START_CHAR:
                row_num.append(START)
                start_pos = (r_idx, c_idx)
            elif char == END_CHAR:
                row_num.append(END)
                end_pos = (r_idx, c_idx)
            else:
                row_num.append(WALL)
        numeric_map.append(row_num)

    if not start_pos or not end_pos:
        raise ValueError("The maze must have a start point 'S' and end point 'E'.")
        
    return numeric_map, start_pos, end_pos, height, width

def create_graph_from_maze(maze_str_list):
    graph = {}
    height = len(maze_str_list)
    width = len(maze_str_list[0])
    
    for r in range(1, height, 2):
        for c in range(1, width, 2):
            current_node = (r, c)
            graph[current_node] = []
            
            if r > 0 and maze_str_list[r - 1][c] != '#':
                graph[current_node].append((r - 2, c))
            if r < height - 1 and maze_str_list[r + 1][c] != '#':
                graph[current_node].append((r + 2, c))
            if c > 0 and maze_str_list[r][c - 1] != '#':
                graph[current_node].append((r, c - 2))
            if c < width - 1 and maze_str_list[r][c + 1] != '#':
                graph[current_node].append((r, c + 2))
    return graph
    
def find_point(maze, char):
    for r, row in enumerate(maze):
        for c, cell in enumerate(row):
            if cell == char:
                return (r, c)
    return None

def convert_path_to_instructions(path):
    if not path or len(path) < 2:
        return []

    instructions = []
    current_orientation = 2  

    for i in range(len(path) - 1):
        current = path[i]
        next_node = path[i+1]

        dr, dc = next_node[0] - current[0], next_node[1] - current[1]

        if dr == 2: target_orientation = 2
        elif dr == -2: target_orientation = 0
        elif dc == 2: target_orientation = 1
        elif dc == -2: target_orientation = 3
        else: continue

        diff = (target_orientation - current_orientation + 4) % 4
        
        if diff == 1:
            instructions.append('R')
        elif diff == 3:
            instructions.append('L')
        elif diff == 2:
            instructions.append('R')
            instructions.append('R')
        
        instructions.append('F')
        current_orientation = target_orientation
        
    return "".join(instructions)

def measure_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        print(f"Function '{func.__name__}' took {end_time - start_time:.6f} seconds.")
        return result
    return wrapper