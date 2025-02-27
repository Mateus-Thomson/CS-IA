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
        self.chunkPs = self.create_empty_points()
        self.imgMlt= 5
    def area(self):
        return self.size[0]*self.size[1]

    def create_empty_points(self):
        return np.empty((0), dtype=f'<S{len(f'{self.chunk_amt()}')*4+8}')

    def dtype(self):
        return f'<S{len(f'{self.chunk_amt()}')*4+8}'

    def chunk_amt(self):
        return int(len(self.chunks)/self.area())
    def point_pos_fixer(self):
        for idx in range(self.chunk_amt()):
            points = self.chunkPs[idx].split('-')[:-1]
            for point in points:
                self.set_chunk_cell_flat(idx, int(point), 0)

            #self.chunkPs[idx] = '-'.join(points) + '-' + self.chunkPs[idx][:-4]
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

        for idx in range(amt):
            num = random.randint(0, self.area()-1)
            points += f'{num}-'

        points += f'{locks}'

        self.chunkPs = np.append(self.chunkPs, points)


    def delete_chunk(self, index):
        self.chunks = self.chunks[:index*self.area()] + self.chunks[index*self.area()+(self.area()):]
        self.chunkPs = np.delete(self.chunkPs, index)
    def create_chunk_imgs(self):
        imgs = []
        for idx in range(self.chunk_amt()):
            img = pygame.surface.Surface((self.size[0], self.size[1]))

            for y in range(self.size[1]):
                for x in range(self.size[0]):
                    img.set_at((x,y), (255,255,255) if self.get_chunk_cell(idx,y,x) else (0,0,0))

            points = self.chunkPs[idx].split('-')

            try:
                for point in list(int(i) for i in points[:-1]):
                    img.set_at((point%self.size[0],point//self.size[1]), (255,0,0))
            except ValueError:
                print('oopsiepoopsie2')
            imgs.append(pygame.transform.scale(img, (self.size[0]*self.imgMlt, self.size[1]*self.imgMlt)))

        return imgs
    def remove_chunk(self, index):
        self.chunks[(index) * self.area():(index + 1) * self.area()] = bitarray('')
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

    def to_2d_point(self, flat):
        return [int(flat)%self.size[0], int(flat)//self.size[0]]
    def to_flat_point(self, tuple):
        return tuple[0]+tuple[1]*self.size[0]
    def crossover_chunk(self, idx1, idx2, settings):
        #adds a chunk that crosses over two other chunks
        sep_point = int(self.area() / 2) + random.randint(-settings["crs_range"], settings["crs_range"])
        points = []
        lp1 = self.chunkPs[idx1].split('-')
        lp2 = self.chunkPs[idx2].split('-')
        lock = ''
        for r, point in enumerate(lp1[:-1]):
            if point!='' and int(point) < sep_point:
                points.append(point)
                lock += lp1[-1][r]
        for r, point in enumerate(lp2[:-1]):
            if int(point) >= sep_point:
                points.append(point)
                lock += lp2[-1][r]

        crs_chunk = self.get_chunk(idx1)[:sep_point]+self.get_chunk(idx2)[sep_point:]
        self.chunks += crs_chunk
        self.chunkPs = np.append(self.chunkPs, '-'.join(points)+'-'+lock)

    def mutate_chunk(self, index, settings):
        #mutates an existing chunk and appends it
        chunk = self.get_chunk(index)
        points = self.chunkPs[index].split('-')

        weights = [1-settings['m_cPower'],settings['m_cPower']]
        m_num = ''.join(str(random.choices([0, 1], weights=weights)[0]) for _ in range(self.area()))

        mutate_chunk = bitarray(m_num)

        self.chunks += chunk

        for idx, cell in enumerate(chunk):
            if mutate_chunk[idx]==1:
                self.set_chunk_cell_flat(-1, idx, not self.get_chunk_cell_flat(-1, idx))

        try:
            for idx, point in enumerate(list(int(i) for i in points[:-1])):
                weights = [1-settings['m_pPower'],settings['m_pPower'],settings['m_pPower'],settings['m_pPower'],settings['m_pPower']]
                if points[-1][idx] in ['>','<','^','_']:
                    weights[1:5] = [0,0,0,0]
                h = point+random.choices([0, 1,-1,self.size[0], -self.size[0]], weights=weights)[0]
                points[idx] = f'{min(max(0, h), self.area()-1)}'
        except ValueError:
            print("oopsiepoopsie3")
        self.chunkPs = np.append(self.chunkPs, '-'.join(points))
