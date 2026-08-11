import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"

def visualize_results(maze_str, results, start, end):
    if not results:
        print("No results to visualize.")
        return

    height = len(maze_str)
    width = len(maze_str[0])
    numeric_grid = np.zeros((height, width))
    for r in range(height):
        for c in range(width):
            if maze_str[r][c] == '#':
                numeric_grid[r, c] = 0
            else:
                numeric_grid[r, c] = 1

    valid_paths = {name: data for name, data in results.items() if data.get("path")}
    if not valid_paths:
        print("No valid paths found to visualize.")
        return
    
    best_name_by_cost = min(valid_paths, key=lambda k: valid_paths[k]['cost'])
    optimal_path = valid_paths[best_name_by_cost]['path']
    print(f"\nVisualization: The lowest cost path is '{best_name_by_cost}'.")

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    print("Generating combined paths chart...")
    fig_comb, ax_comb = plt.subplots(figsize=(12, 6))
    fig_comb.subplots_adjust(right=0.75)
    
    ax_comb.imshow(numeric_grid, cmap='gray_r', origin='upper')

    colors = ['green', 'purple', 'blue', 'orange', 'cyan', 'magenta']
    color_idx = 0
    
    for name, data in valid_paths.items():
        path = data['path']
        y_coords, x_coords = zip(*path)
        
        if name == best_name_by_cost:
            continue
        else:
            ax_comb.plot(x_coords, y_coords, linestyle='-', color=colors[color_idx % len(colors)], label=name)
            color_idx += 1

    y_opt, x_opt = zip(*optimal_path)
    optimal_label = f"{best_name_by_cost} (Optimal)"
    ax_comb.plot(x_opt, y_opt, linestyle='-', color='red', linewidth=3, label=optimal_label, zorder=10)

    ax_comb.plot(start[1], start[0], 'p', markersize=12, color='lime', label='Start', zorder=11)
    ax_comb.plot(end[1], end[0], '*', markersize=15, color='gold', label='End', zorder=11)

    ax_comb.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
    ax_comb.set_title('Comparison of Final Paths')
    ax_comb.set_xticks([])
    ax_comb.set_yticks([])
    
    combined_filename = ASSETS_DIR / 'path_comparison.png'
    plt.savefig(combined_filename)
    print(f"- Combined chart saved to '{combined_filename}'")
    plt.close(fig_comb)

    print("\nGenerating individual charts...")
    for name, data in results.items():
        path = data.get("path")
        visited = data.get("visited", set())

        fig_ind, ax_ind = plt.subplots(figsize=(10, 5))
        ax_ind.imshow(numeric_grid, cmap='gray_r', origin='upper')

        if visited:
            try:
                y_visited, x_visited = zip(*visited)
                ax_ind.scatter(x_visited, y_visited, s=15, color='gray', alpha=0.3, label='Explored Nodes')
            except ValueError:
                pass

        if path:
            y_path, x_path = zip(*path)
            ax_ind.plot(x_path, y_path, marker='o', markersize=3, linestyle='-', color='cyan', label='Final Path')
        
        ax_ind.plot(start[1], start[0], 'p', markersize=12, color='lime', label='Start')
        ax_ind.plot(end[1], end[0], '*', markersize=15, color='gold', label='End')

        steps = data.get("steps", 0)
        cost = data.get("cost", float('inf'))
        
        title = f'"{name}" | Steps: {steps - 1 if steps > 0 else 0} | Cost: {cost:.2f} | Explored Nodes: {len(visited)}'
        if not path:
            title = f'"{name}" | No path found | Explored Nodes: {len(visited)}'

        ax_ind.set_title(title)
        ax_ind.set_xticks([])
        ax_ind.set_yticks([])
        ax_ind.legend(loc='upper right')
        plt.tight_layout()

        ind_filename = ASSETS_DIR / f'exploration_{name.replace(" ", "_").replace("(", "").replace(")", "").lower()}.png'
        plt.savefig(ind_filename)
        print(f"- Chart for {name} saved to '{ind_filename}'")
        plt.close(fig_ind)