import numpy
import numpy as np
import pygame as pg
import sys, time, random

import pygame.surface
from bitarray import bitarray
from itertools import combinations

from chunk_operator import *
from pathfinding import *

cOP = Chunk_Operator((10,10))

settings = \
{"m_Amt": 3,
 "m_cPower": 0.1,
 "m_pPower": 0.25,
 "init_Pop": 2,
 "crs_Amt":1,
 "crs_range": 10,
 "pop_Per_Gen": 5,
 "gen_Cap":50
 }


for r in range(settings['init_Pop']):
    cOP.create_chunk()

imgs = cOP.create_chunk_imgs()

window = pg.display.set_mode((500,500))


AStar = A_Star()
def gen_cycle():
    # ---CROSSOVER---
    for r in range(0, settings["crs_Amt"] * 2, 2):
        cOP.crossover_chunk(r, r + 1, settings)

    # ---MUTATE---
    for r in range(settings['m_Amt']):
        cOP.mutate_chunk(r, settings)

    # ---NEW CHUNKS---
    for _ in range(settings['pop_Per_Gen']):
        cOP.create_chunk()

    # --- REMOVE DUPLICATES ---
    new_points = np.empty((0), dtype=cOP.dtype())
    possible_dupes = []
    for r, points in enumerate(cOP.chunkPs):
        if points not in new_points:
            new_points = np.append(new_points, points)
        else:
            x = int(np.where(new_points == points)[0][0])
            possible_dupes.append([r, x])

    actual_dupes = []
    for dupe in possible_dupes:
        if cOP.get_chunk(dupe[0])==cOP.get_chunk(dupe[1]):
            actual_dupes.append(dupe[0])
    for dupe in actual_dupes:
        cOP.delete_chunk(dupe)

    # ---SORT and CLEAR---
    sortArray = np.empty(shape=(cOP.chunk_amt(), 2), dtype=np.uint32)
    for idx, item in enumerate(sortArray):
        #value that it sorts by
        paths = []
        for set in list(combinations(cOP.chunkPs[idx].split('-')[:-1], 2)):
            paths.append(AStar.get_path(cOP.get_chunk(idx), int(set[0]), int(set[1]), cOP.size))
            print(set)

        print(len(paths)-paths.count([]))

        sortArray[idx] = [paths.count([]), idx]


    sortArgs = sortArray[:, 0].argsort(kind='quicksort')

    sortArray = sortArray[sortArgs]
    cOP.chunkPs = cOP.chunkPs[sortArgs]

    cOP.reorder_chunks(sortArray[:, 1])

    # ---LIMIT---
    cOP.chunkPs = cOP.chunkPs[:settings['gen_Cap']]
    cOP.chunks = cOP.chunks[:settings['gen_Cap']*cOP.area()]

    return cOP.create_chunk_imgs()

while True:
    window.fill((60,60,60))

    x = 0
    y = 0
    for i, img in enumerate(imgs):
        window.blit(img, (x,y))
        x+= cOP.size[0]*cOP.imgMlt+2
        if x+cOP.size[0]*cOP.imgMlt > window.get_width():
            x=0
            y += cOP.size[1]*cOP.imgMlt+2


    for event in pg.event.get():
        if event.type == pg.QUIT:
            exit()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_e:
                imgs = gen_cycle()


    pg.display.flip()


