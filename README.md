# 🧩 MazeSolvers – Weighted Maze Solver

An interactive maze-solving application built with **Python and Pygame**. I created this project to explore how different pathfinding algorithms work and compare how they find their way through a maze.

The application lets users generate random mazes, customize obstacles and terrain, and watch algorithms search for a path in real time.

## 🚀 Features

- **Four pathfinding algorithms:** BFS, DFS, Dijkstra, and A*
- **Random maze generation** with different layouts
- **Weighted terrain:** Roads, grass, mud, and water have different movement costs
- **Interactive editing:** Add or remove walls, change terrain, and move the start and end points
- **Step-by-step visualization:** Watch visited nodes, frontier nodes, and the final path
- **Performance tracking:** Compare visited nodes, path length, total path cost, and algorithm execution time
- **Adjustable speed:** Control how quickly each algorithm runs

## 🧠 Algorithms

| Algorithm | Description |
|---|---|
| BFS | Finds the shortest path based on the number of steps |
| DFS | Explores paths using depth-first search but does not guarantee the shortest path |
| Dijkstra | Finds the path with the lowest total movement cost |
| A* | Uses a heuristic to find a minimum-cost path efficiently |

## 🛠️ Technologies Used

- **Python 3**
- **Pygame**
- **Data Structures:** Queues, stacks, sets, dictionaries, and priority queues
- **Algorithms:** Graph traversal, shortest-path search, and maze generation

## 💻 Installation and Setup

### 1. Clone the Repository

Open PowerShell or a terminal and run:

```bash
git clone https://github.com/LavenGit/MazeSolvers.git
cd MazeSolvers
```

### 2. Install Pygame

Make sure Python 3 is installed, then run:

```bash
python -m pip install pygame
```

### 3. Run the Application

```bash
python "MazeSolver .py"
```

The Pygame window should open, displaying the maze and algorithm controls.

## 🎮 Controls

| Key / Action | Function |
|---|---|
| `1` | Select BFS |
| `2` | Select DFS |
| `3` | Select Dijkstra |
| `4` | Select A* |
| `Space` | Start or pause the search |
| `R` | Generate a new maze |
| `C` | Reset the current search |
| `W` | Randomize terrain |
| `X` | Clear walls |
| `+ / -` | Increase or decrease search speed |
| `0` | Select road brush |
| `5` | Select wall brush |
| `6` | Select grass brush |
| `7` | Select mud brush |
| `8` | Select water brush |
| Left-click and drag | Paint terrain or move start/end points |
| Right-click and drag | Erase terrain to road |

## 🌱 Terrain Costs

Different terrain types affect the total cost of a path.

| Terrain | Movement Cost |
|---|---|
| Road | 1 |
| Grass | 2 |
| Mud | 5 |
| Water | 10 |
| Wall | Cannot be crossed |

BFS finds a path with the fewest steps, while Dijkstra and A* consider movement costs to find the least expensive route.

## 📊 Performance Metrics

While running an algorithm, the application displays:

- **Visited:** Number of explored cells
- **Frontier:** Number of cells waiting to be explored
- **Path Length:** Number of steps in the solution
- **Path Cost:** Total movement cost of the solution
- **Algorithm Time:** Time spent executing the search algorithm

These metrics help compare how the algorithms perform on different maze layouts.

## 📌 About This Project

This project helped me strengthen my understanding of graph algorithms, Python programming, object-oriented programming, and data structures. It also gave me hands-on experience building an interactive application and visualizing how algorithms make decisions.

---

**Built with Python and Pygame.**
