import pygame, random, heapq
from collections import deque, namedtuple  

GRID_COL = 30
GRID_ROW = 23
CELL_SIZE = 20
WIDTH = GRID_COL * CELL_SIZE
HEIGHT = GRID_ROW * CELL_SIZE
FPS = 12

WHITE = (245, 245, 245)
BLACK = (10, 10, 10)
SNAKE_COLOR = (40, 180, 40)
SNAKE_HEAD = (20, 140, 20)
FOOD_COLOR = (200, 40, 40)
PATH_COLOR = (240, 200, 20)
OPEN_COLOR = (150, 220, 240)
CLOSED_COLOR = (200, 200, 200)
WALL_COLOR = (90, 90, 90)
BG_COLOR = (30, 30, 30)

Node = namedtuple("Node", ["f", "g", "h", "pos", "parent"])

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def neighbors(pos):
    x, y = pos
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, ny = x + dx, y + dy
        if 0 <= nx < GRID_COL and 0 <= ny < GRID_ROW:
            yield (nx, ny)

def astar(start, goal, blocked):
    open_heap = []
    open_map = {}
    closed_set = set()

    h0 = heuristic(start, goal)
    start_node = Node(h0, 0, h0, start, None)
    heapq.heappush(open_heap, (start_node.f, start_node))
    open_map[start] = start_node

    while open_heap:
        _, current = heapq.heappop(open_heap)
        if open_map.get(current.pos) is not current:
            continue

        if current.pos == goal:
            path = []
            node = current
            while node.parent is not None:
                path.append(node.pos)
                node = node.parent
            path.reverse()
            return path, set(open_map.keys()), closed_set
        
        closed_set.add(current.pos)
        del open_map[current.pos]

        for nb in neighbors(current.pos):
            if nb in blocked and nb != goal:
                continue
            if nb in closed_set:
                continue
            g2 = current.g + 1
            h2 = heuristic(nb, goal)
            f2 = g2 + h2
            existing = open_map.get(nb)
            
            if existing is None or g2 < existing.g:
                new_node = Node(f2, g2, h2, nb, current)
                heapq.heappush(open_heap, (new_node.f, new_node))
                open_map[nb] = new_node

    return None, set(open_map.keys()), closed_set


class Snake:

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Snake* Demo")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 20)
        self.reset()
        self.show_sets = True

    def reset(self):
        mid = (GRID_COL // 2, GRID_ROW // 2)
        self.snake = deque([mid, (mid[0]-1, mid[1]), (mid[0]-2, mid[1])])
        self.direction = (1, 0)
        self.place_walls()
        self.place_food()
        self.path = []
        self.open_set = set()
        self.closed_set = set()
        self.score = 0
        self.game_over = False
        self.steps_since_plan = 0

    def place_food(self):
        while True:
            pos = (random.randint(0, GRID_COL-1), random.randint(0, GRID_ROW-1))
            if pos not in self.snake and pos not in self.walls:
                self.food = pos
                break
    
    def place_walls(self):
        self.walls = set()
        wall_count = (GRID_COL * GRID_ROW) // 20
        for _ in range(wall_count):
            pos = (random.randint(0, GRID_COL-1), random.randint(0, GRID_ROW-1))
            if pos not in self.snake:
                self.walls.add(pos)

    def step(self):
        if self.game_over:
            return
        
        head = self.snake[0]

        blocked = set(self.snake)
        blocked.update(self.walls)

        replan = (not self.path) or (self.steps_since_plan > 5)
        if replan:
            path, open_set, closed_set = astar(head, self.food, blocked)
            self.open_set = open_set
            self.closed_set = closed_set
            if path:
                self.path = path
                self.steps_since_plan = 0
            else:
                self.path = []
        self.steps_since_plan += 1

        if self.path:
            next_cell = self.path.pop(0)
            dx = next_cell[0] - head[0]
            dy = next_cell[1] - head[1]
            self.direction = (dx, dy)
        else:
            moved = False
            cand_dirs = [self.direction, (1, 0), (0, 1), (-1, 0), (0, -1)]
            for d in cand_dirs:
                nx, ny = head[0] + d[0], head[1] + d[1]
                if 0 <= nx < GRID_COL and 0 <= ny < GRID_ROW and (nx, ny) not in blocked:
                    self.direction = d
                    moved = True
                    break
            if not moved:
                self.game_over = True
                return
                
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])

        if not (0 <= new_head[0] < GRID_COL and 0 <= new_head[1] < GRID_ROW):
            self.game_over = True
            return
        if new_head in self.walls:
            self.game_over = True
            return
        
        tail = self.snake[-1]
        body = set(list(self.snake)[:-1])
        if new_head in body:
            self.game_over = True
            return
        
        self.snake.appendleft(new_head)

        if new_head == self.food:
            self.score += 1
            self.place_food()
            self.steps_since_plan = 0
        else:
            self.snake.pop()

    def draw_cell(self, pos, color, border = False):
        x, y = pos
        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(self.screen, color, rect)
        if border:
            pygame.draw.rect(self.screen, BLACK, rect, 1)

    def draw(self):
        self.screen.fill(BG_COLOR)

        # Walls
        for wall in self.walls:
            self.draw_cell(wall, WALL_COLOR)
        
        if self.show_sets:
            for pos in self.open_set:
                self.draw_cell(pos, OPEN_COLOR)
            for pos in self.closed_set:
                self.draw_cell(pos, CLOSED_COLOR)
        
        for pos in self.path:
            self.draw_cell(pos, PATH_COLOR)

        self.draw_cell(self.food, FOOD_COLOR)

        for i, seg in enumerate(self.snake):
            color = SNAKE_HEAD if i == 0 else SNAKE_COLOR
            self.draw_cell(seg, color, border=True)
        
        info = f"Score: {self.score}  Length: {len(self.snake)}  Steps since plan: {self.steps_since_plan}  Show sets: {'ON' if self.show_sets else 'OFF'}"
        text = self.font.render(info, True, WHITE)
        self.screen.blit(text, (6, HEIGHT - 20))

        if self.game_over:
            go_text = self.font.render("GAME OVER! Press R to restart.", True, FOOD_COLOR)
            self.screen.blit(go_text, (WIDTH // 2 - 100, HEIGHT // 2 - 10))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset()
                    elif event.key == pygame.K_s:
                        self.show_sets = not self.show_sets

            if not self.game_over:
                self.step()
            self.draw()
        
        pygame.quit()

if __name__ == "__main__":
    Snake().run()
