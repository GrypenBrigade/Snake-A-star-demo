# Snake-A-star-demo

## Using A* algorithm for Snake pathfinding use case

A good example for the A* algorithm is for controlling a snake to eat food, while at the same time avoiding the snake's increasing length.

**How to use**

1. Download pygame through ``pip install pygame``
2. Run snakestar.py

### Code Snippets

A* Algorithm

```
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
```

Jerome Estomago Talaro BSCS501 AI