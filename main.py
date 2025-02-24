import numpy
import numpy as np
import pygame as pg
import sys, time, random

import pygame.surface
from bitarray import bitarray
from itertools import combinations

from chunk_operator import *
from pathfinding import *
from wave_collapse import *
from user_input import *

pg.font.init()

settings = \
{"chunk_size":10,
 "board_size":5,
 "m_Amt": 20,
 "m_cPower": 0.5,
 "m_pPower": 0.5,
 "init_Pop": 10,
 "crs_Amt":5,
 "crs_range": 10,
 "pop_Per_Gen": 20,
 "pop_Cap":15,
 "gen_Cap":10,
 }
settings = user_input(settings)
print(settings)

cOP = Chunk_Operator((settings["chunk_size"],settings["chunk_size"]))


imgs = cOP.create_chunk_imgs()

window = pg.display.set_mode((500,500))
tab1 = pygame.surface.Surface((500,500))
tab2 = pygame.surface.Surface((500,500))
active_tab = 1

wc = WaveChunks(cOP.size,(settings["board_size"],settings["board_size"]))
AStar = A_Star()

generation = 0
def gen_cycle():
    if cOP.chunks == bitarray(''):
        for r in range(settings['init_Pop']):
            cOP.create_chunk(wc.cr['lkL'],wc.cr['lkR'],wc.cr['lkU'],wc.cr['lkD'])

    # ---MUTATE---
    for r in range(settings['m_Amt']):
        cOP.mutate_chunk(r, settings)
    # ---LIMIT---
    cOP.chunkPs = cOP.chunkPs[:settings['pop_Cap']]
    cOP.chunks = cOP.chunks[:settings['pop_Cap'] * cOP.area()]

    # ---CROSSOVER---
    for r in range(0, settings["crs_Amt"] * 2, 2):
        cOP.crossover_chunk(r, r + 1, settings)

    # ---NEW CHUNKS---
    for _ in range(settings['pop_Per_Gen']):
        cOP.create_chunk(wc.cr['lkL'],wc.cr['lkR'],wc.cr['lkU'],wc.cr['lkD'])

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

    cOP.point_pos_fixer()
    # ---SORT and CLEAR---
    valid_chunks = bitarray('')
    valid_points = cOP.create_empty_points()
    path_nums = []
    path_lengths = []

    for idx in range(cOP.chunk_amt()):
        paths = []
        for set in list(combinations(cOP.chunkPs[idx].split('-')[:-1], 2)):
            paths.append(AStar.get_path(cOP.get_chunk(idx), int(set[0]), int(set[1]), cOP.size))
        paths = list(x for x in paths if x !=[])
        path_nums.append(len(paths))
        if paths!=[]:
            o=[]
            for path in paths:
                o.append(len(path))
            path_lengths.append((o, len(path_lengths)))
    path_lengths = sorted(path_lengths, key=lambda x:max(x[0]), reverse=True)
    for idx, num in enumerate(path_nums):
        if num != 0: valid_chunks+=cOP.get_chunk(idx)
        valid_points = np.append(valid_points, cOP.chunkPs[idx])
    cOP.chunks = valid_chunks
    cOP.chunkPs = valid_points
    cOP.reorder_chunks(list(map(lambda x:x[1],path_lengths)))

    return cOP.create_chunk_imgs()

gfont = pg.font.SysFont("Arial", 24)
def gen_text():
    return gfont.render(f'Gen: {generation}', False, (255, 255, 255))
gtext = gen_text()

other_imgs = []


while True:
    tab1.fill((0,60,60))
    tab2.fill((60, 60, 0))
    #tab 1

    if 0 in wc.board_filled:
        imgs = gen_cycle()
        generation += 1
        gtext = gen_text()

    tab1.blit(gtext, (0, window.get_height() - gtext.get_height()))
    x = 0
    y = 0
    for i, img in enumerate(imgs):
        tab1.blit(img, (x, y))
        x += cOP.size[0] * cOP.imgMlt + 2
        if x + cOP.size[0] * cOP.imgMlt > window.get_width():
            x = 0
            y += cOP.size[1] * cOP.imgMlt + 2

    if generation>settings["gen_Cap"]:
        wc.append_chunk(cOP.get_chunk(0), cOP.chunkPs[0])
        generation=0
        cOP.chunks = bitarray('')
        cOP.chunkPs = cOP.create_empty_points()
        other_imgs = wc.create_chunk_imgs()
        print(wc.cr)

        #other_imgs.append(imgs[0])

    #tab 2

    for i, o_img in enumerate(other_imgs):

        tab2.blit(o_img, ((i%wc.b_size[0])*(wc.size[0]+1)*wc.imgMlt, (i//wc.b_size[1])*(wc.size[1]+1)*wc.imgMlt))


    if not 0 in wc.board_filled:
        print(wc.board_filled)
        quit()

    for event in pg.event.get():
        if event.type == pg.QUIT:
            exit()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_d:
                cOP.remove_chunk(0)
                img = cOP.create_chunk_imgs()
            if event.key == pg.K_e:
                imgs = gen_cycle()
                generation +=1
                gtext = gen_text()
            if event.key == pg.K_1:
                active_tab = 1
            if event.key == pg.K_2:
                active_tab = 2

    if active_tab == 1:
        window.blit(tab1, (0,0))
    elif active_tab == 2:
        window.blit(tab2, (0, 0))
    pg.display.flip()


