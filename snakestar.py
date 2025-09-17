import pygame, random, heapq
from collections import deque, namedtuple  

Node = namedtuple("node", ["f", "g", "h", "pos", "parent"])

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

