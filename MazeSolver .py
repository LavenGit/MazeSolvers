"""Interactive weighted maze solver: BFS, DFS, Dijkstra and A*.

Install: python -m pip install pygame
Run: python maze_solver_weighted.py

1-4 select algorithm | SPACE run/pause | R new maze | C reset search
X clear walls | +/- speed | W randomize terrain | 0/5/6/7/8 select paint brush
Left drag paint terrain; right drag erase to road. Drag start/end markers.
"""
import heapq
import random
import sys
import time
from collections import deque

import pygame

CELL = 26
COLS, ROWS = 33, 25
PANEL_W = 330
WIDTH, HEIGHT = COLS * CELL + PANEL_W, ROWS * CELL
FPS = 60
SPEEDS = [1, 2, 4, 8, 16, 32, 64, 128]
LOOP_CHANCE = 0.06

# Grid entries are terrain types, NOT search states.
ROAD, WALL, GRASS, MUD, WATER = range(5)
COST = {ROAD: 1, GRASS: 2, MUD: 5, WATER: 10}
TERRAIN = {
    ROAD: (226, 230, 237), WALL: (37, 41, 56),
    GRASS: (128, 191, 118), MUD: (171, 122, 85), WATER: (87, 150, 203),
}
BG = (18, 20, 28)
VISITED = (105, 149, 240)
FRONTIER = (94, 230, 182)
PATH = (255, 205, 60)
START_C = (35, 185, 90)
END_C = (225, 70, 70)
GRID_LINE = (70, 77, 93)
TEXT = (225, 228, 238)
DIM = (157, 163, 180)
ALGOS = ['BFS', 'DFS', 'Dijkstra', 'A*']
DIRS = ((-1, 0), (0, 1), (1, 0), (0, -1))


def neighbors(grid, pos):
    r, c = pos
    for dr, dc in DIRS:
        nr, nc = r + dr, c + dc
        if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc] != WALL:
            yield nr, nc


def generate_maze():
    """Iterative randomized DFS maze carving, then a few extra openings."""
    grid = [[WALL] * COLS for _ in range(ROWS)]
    grid[1][1] = ROAD
    stack = [(1, 1)]
    while stack:
        r, c = stack[-1]
        options = []
        for dr, dc in DIRS:
            nr, nc = r + 2 * dr, c + 2 * dc
            if 1 <= nr < ROWS - 1 and 1 <= nc < COLS - 1 and grid[nr][nc] == WALL:
                options.append((nr, nc, r + dr, c + dc))
        if options:
            nr, nc, wr, wc = random.choice(options)
            grid[wr][wc] = grid[nr][nc] = ROAD
            stack.append((nr, nc))
        else:
            stack.pop()
    for r in range(1, ROWS - 1):
        for c in range(1, COLS - 1):
            if grid[r][c] == WALL and random.random() < LOOP_CHANCE:
                grid[r][c] = ROAD
    return grid


def randomize_terrain(grid, start, end):
    """Paint only existing passages; preserve walls and endpoints."""
    for r, row in enumerate(grid):
        for c, value in enumerate(row):
            if value != WALL and (r, c) not in (start, end):
                row[c] = random.choices([ROAD, GRASS, MUD, WATER], [60, 22, 13, 5])[0]


class Search:
    """Generator-driven search: one expanded node per visual step."""
    def __init__(self, algo, grid, start, end):
        self.algo, self.grid, self.start, self.end = algo, grid, start, end
        self.visited, self.frontier, self.parent = set(), set(), {start: None}
        self.found = self.finished = False
        self.path = []
        self.path_cost = None
        self.compute_time = 0.0
        self.gen = {
            'BFS': self._bfs, 'DFS': self._dfs,
            'Dijkstra': self._dijkstra, 'A*': self._astar,
        }[algo]()

    def step(self):
        if self.finished:
            return
        t = time.perf_counter()
        try:
            next(self.gen)
        except StopIteration:
            self.finished = True
            if self.found:
                cur = self.end
                while cur is not None:
                    self.path.append(cur)
                    cur = self.parent[cur]
                self.path.reverse()
                self.path_cost = sum(COST[self.grid[r][c]] for r, c in self.path[1:])
        self.compute_time += time.perf_counter() - t

    def _bfs(self):
        queue = deque([self.start])
        self.frontier.add(self.start)
        while queue:
            cur = queue.popleft()
            self.frontier.discard(cur)
            self.visited.add(cur)
            if cur == self.end:
                self.found = True
                return
            for nxt in neighbors(self.grid, cur):
                if nxt not in self.parent:
                    self.parent[nxt] = cur
                    queue.append(nxt)
                    self.frontier.add(nxt)
            yield

    def _dfs(self):
        stack = [self.start]
        discovered = {self.start}
        self.frontier.add(self.start)
        while stack:
            cur = stack.pop()
            self.frontier.discard(cur)
            self.visited.add(cur)
            if cur == self.end:
                self.found = True
                return
            for nxt in neighbors(self.grid, cur):
                if nxt not in discovered:
                    discovered.add(nxt)
                    self.parent[nxt] = cur
                    stack.append(nxt)
                    self.frontier.add(nxt)
            yield

    def _dijkstra(self):
        yield from self._best_first(use_heuristic=False)

    def _astar(self):
        yield from self._best_first(use_heuristic=True)

    def _best_first(self, use_heuristic):
        def heuristic(p):
            # Minimum terrain cost is 1, so Manhattan is admissible and consistent.
            return abs(p[0] - self.end[0]) + abs(p[1] - self.end[1]) if use_heuristic else 0

        counter = 0
        heap = [(heuristic(self.start), 0, counter, self.start)]
        best_g = {self.start: 0}
        self.frontier.add(self.start)
        while heap:
            _, g, _, cur = heapq.heappop(heap)
            if cur in self.visited or g != best_g[cur]:
                continue
            self.visited.add(cur)
            self.frontier.discard(cur)
            if cur == self.end:
                self.found = True
                return
            for nxt in neighbors(self.grid, cur):
                new_g = g + COST[self.grid[nxt[0]][nxt[1]]]
                if new_g < best_g.get(nxt, float('inf')):
                    best_g[nxt] = new_g
                    self.parent[nxt] = cur
                    counter += 1
                    heapq.heappush(heap, (new_g + heuristic(nxt), new_g, counter, nxt))
                    self.frontier.add(nxt)
            yield


class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Weighted Maze Solver | BFS / DFS / Dijkstra / A*')
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('consolas,menlo,dejavusansmono,monospace', 15)
        self.big = pygame.font.SysFont('consolas,menlo,dejavusansmono,monospace', 22, bold=True)
        self.small = pygame.font.SysFont('consolas,menlo,dejavusansmono,monospace', 12)
        self.algo = 'Dijkstra'
        self.brush = WALL
        self.speed_i = 3
        self.start, self.end = (1, 1), (ROWS - 2, COLS - 2)
        self.grid = generate_maze()
        randomize_terrain(self.grid, self.start, self.end)
        self.search = None
        self.state = 'idle'
        self.path_shown = 0
        self.drag = None
        self.buttons = []

    def clear_search(self):
        self.search, self.state, self.path_shown = None, 'idle', 0

    def new_maze(self):
        self.grid = generate_maze()
        self.start, self.end = (1, 1), (ROWS - 2, COLS - 2)
        randomize_terrain(self.grid, self.start, self.end)
        self.clear_search()

    def toggle_run(self):
        if self.state in ('idle', 'finished'):
            self.clear_search()
            self.search = Search(self.algo, self.grid, self.start, self.end)
            self.state = 'running'
        elif self.state == 'running':
            self.state = 'paused'
        else:
            self.state = 'running'

    def set_algo(self, algo):
        self.algo = algo
        self.clear_search()

    def cell_at(self, pos):
        x, y = pos
        r, c = y // CELL, x // CELL
        return (r, c) if 0 <= r < ROWS and 0 <= c < COLS else None

    def mouse_down(self, pos, button):
        if button == 1:
            for rect, algo in self.buttons:
                if rect.collidepoint(pos):
                    self.set_algo(algo)
                    return
        cell = self.cell_at(pos)
        if cell is None:
            return
        if button == 3:
            self.drag = ('paint', ROAD)
        elif button == 1 and cell == self.start:
            self.drag = ('start', None)
        elif button == 1 and cell == self.end:
            self.drag = ('end', None)
        elif button == 1:
            self.drag = ('paint', self.brush)
        else:
            return
        self.apply_drag(cell)

    def apply_drag(self, cell):
        if cell is None or self.drag is None:
            return
        mode, value = self.drag
        r, c = cell
        if mode == 'start' and cell != self.end and self.grid[r][c] != WALL:
            if self.start != cell:
                self.start = cell
                self.clear_search()
        elif mode == 'end' and cell != self.start and self.grid[r][c] != WALL:
            if self.end != cell:
                self.end = cell
                self.clear_search()
        elif mode == 'paint' and cell not in (self.start, self.end):
            if self.grid[r][c] != value:
                self.grid[r][c] = value
                self.clear_search()

    def handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    return False
                elif e.key == pygame.K_SPACE:
                    self.toggle_run()
                elif e.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                    self.set_algo(ALGOS[e.key - pygame.K_1])
                elif e.key == pygame.K_r:
                    self.new_maze()
                elif e.key == pygame.K_c:
                    self.clear_search()
                elif e.key == pygame.K_w:
                    randomize_terrain(self.grid, self.start, self.end)
                    self.clear_search()
                elif e.key == pygame.K_x:
                    self.grid = [[ROAD] * COLS for _ in range(ROWS)]
                    for r in range(ROWS):
                        self.grid[r][0] = self.grid[r][-1] = WALL
                    for c in range(COLS):
                        self.grid[0][c] = self.grid[-1][c] = WALL
                    self.clear_search()
                elif e.key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
                    self.speed_i = min(self.speed_i + 1, len(SPEEDS) - 1)
                elif e.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    self.speed_i = max(self.speed_i - 1, 0)
                elif e.key in (pygame.K_0, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8):
                    self.brush = {pygame.K_0: ROAD, pygame.K_5: WALL, pygame.K_6: GRASS,
                                  pygame.K_7: MUD, pygame.K_8: WATER}[e.key]
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button in (1, 3):
                self.mouse_down(e.pos, e.button)
            elif e.type == pygame.MOUSEBUTTONUP and e.button in (1, 3):
                self.drag = None
            elif e.type == pygame.MOUSEMOTION and self.drag:
                self.apply_drag(self.cell_at(e.pos))
        return True

    def update(self):
        if self.state == 'running':
            for _ in range(SPEEDS[self.speed_i]):
                self.search.step()
                if self.search.finished:
                    self.state = 'finished'
                    break
        elif self.state == 'finished' and self.search and self.search.found:
            self.path_shown = min(self.path_shown + 2, len(self.search.path))

    def text(self, msg, x, y, color=TEXT, font=None):
        self.screen.blit((font or self.font).render(str(msg), True, color), (x, y))

    def draw_grid(self):
        s = self.search
        path = set(s.path[:self.path_shown]) if s else set()
        for r in range(ROWS):
            for c in range(COLS):
                p = (r, c)
                tile = self.grid[r][c]
                color = TERRAIN[tile]
                if p == self.start:
                    color = START_C
                elif p == self.end:
                    color = END_C
                elif p in path:
                    color = PATH
                elif s and p in s.frontier:
                    color = FRONTIER
                elif s and p in s.visited:
                    color = VISITED
                rect = (c * CELL, r * CELL, CELL, CELL)
                pygame.draw.rect(self.screen, color, rect)
                if tile != WALL:
                    pygame.draw.rect(self.screen, GRID_LINE, rect, 1)
                    if tile in (GRASS, MUD, WATER) and p not in path and p not in (self.start, self.end):
                        # Small cost label remains visible even after search overlay.
                        cost_label = self.small.render(str(COST[tile]), True, (25, 28, 36))
                        self.screen.blit(cost_label, cost_label.get_rect(center=(c * CELL + CELL//2, r * CELL + CELL//2)))

    def draw_panel(self):
        x = COLS * CELL + 14
        pygame.draw.rect(self.screen, BG, (COLS * CELL, 0, PANEL_W, HEIGHT))
        self.text('WEIGHTED MAZE', x, 12, font=self.big)
        self.buttons = []
        for i, name in enumerate(ALGOS):
            bx = x + (i % 2) * 152
            by = 50 + (i // 2) * 35
            rect = pygame.Rect(bx, by, 143, 29)
            pygame.draw.rect(self.screen, (65, 107, 220) if name == self.algo else TERRAIN[WALL], rect, border_radius=5)
            self.text(f'{i+1}: {name}', bx + 9, by + 5)
            self.buttons.append((rect, name))

        s = self.search
        status = {'idle': 'Ready', 'running': 'Searching...', 'paused': 'Paused',
                  'finished': 'Done' if s and s.found else 'No path'}[self.state]
        metrics = [
            ('Status', status), ('Speed', f'{SPEEDS[self.speed_i]} steps/frame'),
            ('Visited', len(s.visited) if s else '-'),
            ('Frontier', len(s.frontier) if s else '-'),
            ('Path length', len(s.path)-1 if s and s.finished and s.found else '-'),
            ('Path cost', s.path_cost if s and s.finished and s.found else '-'),
            ('Algo time', f'{s.compute_time*1000:.2f} ms' if s else '-'),
        ]
        for i, (name, value) in enumerate(metrics):
            y = 130 + 25*i
            self.text(name, x, y, DIM)
            self.text(value, x+137, y)

        self.text('TERRAIN / PAINT BRUSH', x, 317, font=self.font)
        choices = [('0 Road', ROAD), ('5 Wall', WALL), ('6 Grass', GRASS),
                   ('7 Mud', MUD), ('8 Water', WATER)]
        for i, (name, tile) in enumerate(choices):
            bx = x + (i % 2)*152
            by = 343 + (i // 2)*25
            pygame.draw.rect(self.screen, TERRAIN[tile], (bx, by+1, 17, 17))
            self.text(f'{name} ({COST.get(tile, "X")})', bx+23, by, PATH if self.brush == tile else DIM)

        self.text('SEARCH COLORS', x, 429)
        for i, (name, color) in enumerate([('Start', START_C), ('End', END_C),
                                            ('Frontier', FRONTIER), ('Visited', VISITED),
                                            ('Solution', PATH)]):
            bx = x + (i % 2)*152
            by = 451 + (i // 2)*23
            pygame.draw.rect(self.screen, color, (bx, by+1, 15, 15))
            self.text(name, bx+21, by, DIM)

        self.text('SPACE run/pause   R new maze', x, 533, DIM, self.small)
        self.text('C reset   X clear   W new terrain', x, 550, DIM, self.small)
        self.text('+/- speed   1-4 algorithm', x, 567, DIM, self.small)
        self.text('Left drag paint / move S or E', x, 584, DIM, self.small)
        self.text('Right drag erase to road', x, 601, DIM, self.small)
        self.text('BFS: fewest steps | Dijkstra/A*: least cost', x, 624, DIM, self.small)

    def run(self):
        while self.handle_events():
            self.update()
            self.screen.fill(BG)
            self.draw_grid()
            self.draw_panel()
            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()


if __name__ == '__main__':
    App().run()
