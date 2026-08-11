from algorithms import *
from utils import *
from communication import *
from visualization import *

real_maze_str = [
    "#####################",
    "# # #     #     # # #",
    "# # # ##### ##### # #",
    "#    S    #      E  #",
    "#####   ### ### #####",
    "# #     # # # # #   #",
    "# ### ### # # # # # #",
    "#               # # #",
    "# ### ### ##### ### #",
    "# #   #       #     #",
    "#####################",
]

def main():
    print("--- STARTING MAZE SOLVER ---")

    start = find_point(real_maze_str, 'S')
    end = find_point(real_maze_str, 'E')

    if start is None:
        print("ERROR: Could not find start point 'S' in the maze matrix.")
        return
    if end is None:
        print("ERROR: Could not find end point 'E' in the maze matrix.")
        return

    print(f"Maze loaded. Start: {start}, End: {end}.")

    algorithms_dict = {
        "BFS": lambda maze, start_node, end_node: find_path_bfs(maze, start_node, end_node),
        "DFS": lambda maze, start_node, end_node: find_path_dfs(maze, start_node, end_node),
        "Dijkstra (Simple)": lambda maze, start_node, end_node: find_path_dijkstra(maze, start_node, end_node, turn_cost=0),
        "A* (Simple)": lambda maze, start_node, end_node: find_path_a_star(maze, start_node, end_node, turn_cost=0),
        "Dijkstra (Turn Penalty)": lambda maze, start_node, end_node: find_path_dijkstra(maze, start_node, end_node, turn_cost=1.5),
        "A* (Turn Penalty)": lambda maze, start_node, end_node: find_path_a_star(maze, start_node, end_node, turn_cost=1.5),
        "Flood Fill": lambda maze, start_node, end_node: find_path_flood_fill(maze, start_node, end_node),
        "Wall Follower (Right)": lambda maze, start_node, end_node: find_path_wall_follower_right(maze, start_node, end_node),
        "Wall Follower (Left)": lambda maze, start_node, end_node: find_path_wall_follower_left(maze, start_node, end_node),
    }

    results = {}
    for name, algorithm_func in algorithms_dict.items():
        print(f"\nExecuting algorithm: {name}...")
        path, visited, cost = algorithm_func(real_maze_str, start, end)
        
        if path:
            print(f"-> SUCCESS! {name} found a path with {len(path) - 1} moves.")
            results[name] = {
                "path": path,
                "visited": visited,
                "steps": len(path),
                "cost": cost,  
                "instructions": convert_path_to_instructions(path)
            }
        else:
            print(f"-> {name} did not find a path, but explored {len(visited)} nodes.")

    if results:
        print("\n--- STARTING VISUALIZATION PHASE ---")
        visualize_results(real_maze_str, results, start, end)

    print("\n--- RESULTS RANKING (best to worst by COST) ---")
    
    ranking = sorted(results.items(), key=lambda item: item[1]['cost'])
    
    for i, (name, data) in enumerate(ranking):
        steps = data['steps']
        total_cost = data['cost']
        instructions = data['instructions']
        print(f" {i}. Algorithm: {name}")
        print(f"    Steps: {steps-1} | Total Cost: {total_cost:.2f} | Instructions: {len(instructions)}")
        print(f"    Instructions: {instructions}")

    handle_arduino_communication(ranking)
    
    print("\n--- PROJECT FINISHED ---")

if __name__ == "__main__":
    main()