import numpy
import numpy as np
import pygame as pg
import sys, time, random

import pygame.surface
from bitarray import bitarray

class Chunk_Operator(object):
    def __init__(self, size):
        self.size = size
        self.chunks = bitarray('')
        self.chunkPs = np.empty((0), dtype=f'<S{len(f'{self.chunk_amt()}')*4+8}')
        self.imgMlt= 5

        self.mutate_settings = \
            {"pointMutate":[0.75, 0.25, 0.25, 0.25, 0.25],
             "chunkMutate":[0.9,0.1]}
    def area(self):
        return self.size[0]*self.size[1]

    def chunk_amt(self):
        return int(len(self.chunks)/self.area())
    def create_chunk(self, lS=None, rS=None, tS=None, dS=None):
        num = ''.join(str(random.choice([0, 1])) for _ in range(self.area()))
        self.chunks += bitarray(num)

        l = [i for i in [lS, rS, tS, dS] if i != None]
        amt = max(random.randint(2,4)-len(l), 0)
        points = ''
        c_idx = self.chunk_amt()-1

        # < is locked to left, > is locked to right, ^ is locked to top, _ is locked to bottom

        locks = '<'*(lS!=None)+'>'*(rS!=None)+'^'*(tS!=None)+'_'*(dS!=None)
        locks += '0'*(4-len(locks))
        for idx, side in enumerate(l):
            points += f'{side}-'
            self.set_chunk_cell_flat(c_idx, side, 0)

        for idx in range(amt):
            num = random.randint(0, self.area()-1)
            points += f'{num}-'
            self.set_chunk_cell_flat(c_idx, num, 0)

        points += f'{locks}'
        self.chunkPs = np.append(self.chunkPs, points)

    def create_chunk_imgs(self):
        imgs = []
        for r in range(self.chunk_amt()):
            img = pygame.surface.Surface((self.size[0], self.size[1]))

            for y in range(self.size[1]):
                for x in range(self.size[0]):
                    img.set_at((x,y), (255,255,255) if self.get_chunk_cell(r,y,x) else (0,0,0))

            points = self.chunkPs[r].split('-')

            for point in list(int(i) for i in points[:-1]):
                img.set_at((point//self.size[0],point%self.size[1]), (255,0,0))
            imgs.append(pygame.transform.scale(img, (self.size[0]*self.imgMlt, self.size[1]*self.imgMlt)))

        return imgs
    def get_chunk(self, index):
        return self.chunks[(index)*self.area():(index+1)*self.area()]
    def get_chunk_row(self, index, row):
        add = index * self.area()
        return self.chunks[row*self.size[0]+add:(row+1)*self.size[0]+add]
    def get_chunk_col(self, index, col):
        add = index * self.area()
        return self.chunks[col*self.size[1]+add::self.size[1]-1+add]
    def get_chunk_cell(self, index, row, col):
        add = index * self.area()
        return self.chunks[row*self.size[0]+col+add]
    def get_chunk_cell_flat(self, index, pos):
        add = index * self.area()
        return self.chunks[add + pos]
    def set_chunk(self, index, val):
        self.chunks[index*self.area():(index+1)*self.area()] = bitarray(val)
    def set_chunk_row(self, index, row, val):
        add = index * self.area()
        self.chunks[row*self.size[0]+add:(row+1)*self.size[0]+add] = bitarray(val)
    def set_chunk_col(self, index, col, val):
        add = index * self.area()
        self.chunks[add+col:add+self.area():self.size[1]-1] = bitarray(val)
    def set_chunk_cell(self, index, row, col, val):
        add = index * self.area()
        self.chunks[row*self.size[0]+col+add] = val

    def set_chunk_cell_flat(self, index, pos, val):
        add = index * self.area()
        self.chunks[add + pos] = val
    def reorder_chunks(self, orderList):
        copyChunk = self.chunks.copy()
        for idx,item in enumerate(orderList):
            self.set_chunk(idx, copyChunk[(item)*self.area():(item+1)*self.area()])

    def mutate_chunk(self, index):
        chunk = self.get_chunk(index)
        weights = self.mutate_settings["chunkMutate"]
        m_num = ''.join(str(random.choices([0, 1], weights=weights)[0]) for _ in range(self.area()))

        mutate_chunk = bitarray(m_num)

        for idx, cell in enumerate(chunk):
            if mutate_chunk[idx]==1:
                self.set_chunk_cell_flat(index, idx, not self.get_chunk_cell_flat(index, idx))

        points = self.chunkPs[index].split('-')


        for idx, point in enumerate(list(int(i) for i in points[:-1])):
            weights = self.mutate_settings["pointMutate"].copy()
            if points[-1][idx] in ['>','<']:
                weights[0:2] = 0,0
            if points[-1][idx] in ['^','_']:
                weights[2:4] = 0,0

            h = point+random.choices([0, 1,-1,self.size[0], -self.size[0]], weights=weights)[0]
            points[idx] = f'{min(max(0, h), self.area()-1)}'

        self.chunkPs[index] = '-'.join(points)
cOP = Chunk_Operator((10,10))


for r in range(100):
    cOP.create_chunk()

imgs = cOP.create_chunk_imgs()

window = pg.display.set_mode((500,500))

imgs = cOP.create_chunk_imgs()

def gen_cycle():
    #---SORT---
    sortArray = np.empty(shape=(cOP.chunk_amt(), 2), dtype=np.uint32)

    for idx, item in enumerate(sortArray):
        sortArray[idx] = [cOP.get_chunk(idx).count(1), idx]

    sortArgs = sortArray[:, 0].argsort(kind='quicksort')

    sortArray = sortArray[sortArgs]
    cOP.chunkPs = cOP.chunkPs[sortArgs]

    cOP.reorder_chunks(sortArray[:, 1])
    #---MUTATE---

    #---CROSSOVERS---

    imgs = cOP.create_chunk_imgs()
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
                sortArray = np.empty(shape=(cOP.chunk_amt(), 2), dtype=np.uint32)

                for idx, item in enumerate(sortArray):
                    sortArray[idx] = [cOP.get_chunk(idx).count(1), idx]

                sortArgs = sortArray[:, 0].argsort(kind='quicksort')

                sortArray = sortArray[sortArgs]
                cOP.chunkPs = cOP.chunkPs[sortArgs]

                cOP.reorder_chunks(sortArray[:,1])
                imgs = cOP.create_chunk_imgs()
            if event.key == pg.K_m:
                for idx in range(cOP.chunk_amt()):
                    cOP.mutate_chunk(idx)
                imgs = cOP.create_chunk_imgs()

    pg.display.flip()


