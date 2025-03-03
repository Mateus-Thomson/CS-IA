from scripts.libs import *
from scripts.base import *

class Chunk_Operator(Base):
    '''Operates and handles all the chunks. Every command needed to process the chunks goes here. Extends Base.'''
    def __init__(self, size):
        '''Constructs the essential variables.'''
        self.size = size
        self.chunks = bitarray('')
        self.chunkPs = self.create_empty_points()
        self.imgMlt= 5

    def area(self):
        '''Returns the area of an average chunk.'''
        return self.size[0]*self.size[1]

    def create_empty_points(self):
        '''Returns an empty numpy array for redefining points.'''
        return np.empty((0))

    def chunk_amt(self):
        '''Returns the number of chunks present.'''
        return int(len(self.chunks)/self.area())

    def point_pos_fixer(self):
        '''Bugfix --- Ensures that a point cannot overlap with a wall.'''
        for idx in range(self.chunk_amt()):
            points = self.chunkPs[idx].split('-')[:-1]
            for point in points:
                if point!='':self.set_chunk_cell_flat(idx, int(point), 0)

    def create_chunk(self, lS=None, rS=None, tS=None, dS=None):
        '''Creates a chunk. Inputs are the sides that the generated points must lock to.'''
        num = ''.join(str(random.choice([0, 1])) for _ in range(self.area()))
        self.chunks += bitarray(num) # create chunk

        l = [i for i in [lS, rS, tS, dS] if i != None]
        amt = max(random.randint(2,4)-len(l), 0)
        points = ''

        # < is locked to left, > is locked to right, ^ is locked to top, _ is locked to bottom
        locks = '<'*(lS!=None)+'>'*(rS!=None)+'^'*(tS!=None)+'_'*(dS!=None)
        locks += '0'*(4-len(locks)) # fill remaining spaces with 0
        for idx, side in enumerate(l):
            points += f'{side}-'

        for idx in range(amt):
            num = random.randint(0, self.area()-1)
            points += f'{num}-'

        points += f'{locks}'
        # example output: 4-99-65-^_00 (points are 4, 99, 65. 4 is locked to the top and 99 is locked to the bottom)

        self.chunkPs = np.append(self.chunkPs, points)


    def delete_chunk(self, index):
        '''Removes a chunk using an index.'''
        self.chunks = self.chunks[:index*self.area()] + self.chunks[index*self.area()+(self.area()):]
        self.chunkPs = np.delete(self.chunkPs, index)
    def create_chunk_imgs(self):
        '''Creates chunk images.'''
        imgs = []
        for idx in range(self.chunk_amt()):
            img = pygame.surface.Surface((self.size[0], self.size[1]))

            # draw walls
            for y in range(self.size[1]):
                for x in range(self.size[0]):
                    img.set_at((x,y), (255,255,255) if self.get_chunk_cell(idx,y,x) else (0,0,0))

            #draw points
            points = self.chunkPs[idx].split('-')
            points = self.remove_empties(points)
            for point in list(int(i) for i in points[:-1]):
                img.set_at((point%self.size[0],point//self.size[1]), (255,0,0))

            imgs.append(pygame.transform.scale(img, (self.size[0]*self.imgMlt, self.size[1]*self.imgMlt)))

        return imgs

    def get_chunk(self, index):
        '''Inputs an index and outputs chunk.'''
        return self.chunks[(index)*self.area():(index+1)*self.area()]

    def get_chunk_cell(self, index, row, col):
        '''Inputs an index and position and outputs chunk cell.'''
        add = index * self.area()
        return self.chunks[row*self.size[0]+col+add]

    def get_chunk_cell_flat(self, index, flat):
        '''Inputs an index and flat position and outputs chunk cell.'''
        add = index * self.area()
        return self.chunks[add + flat]

    def set_chunk(self, index, val):
        '''Inputs an index and value and redefines a chunk.'''
        self.chunks[index*self.area():(index+1)*self.area()] = bitarray(val)

    def set_chunk_cell(self, index, row, col, val):
        '''Inputs an index, position, and value, and redefines a chunk cell.'''
        add = index * self.area()
        self.chunks[row*self.size[0]+col+add] = val

    def set_chunk_cell_flat(self, index, flat, val):
        '''Inputs an index, flat position, and value, and redefines a chunk cell.'''
        add = index * self.area()
        self.chunks[add + flat] = val

    def reorder_chunks(self, orderList):
        '''Inputs an order list and reorders chunks based aforementioned list.'''
        copyChunk = self.chunks.copy()
        for idx,item in enumerate(orderList):
            self.set_chunk(idx, copyChunk[(item)*self.area():(item+1)*self.area()])

    def crossover_chunk(self, idx1, idx2, settings):
        '''Stitches two chunks together at a random point in the middle, and then adds it as an entirely new chunk.'''
        sep_point = int(self.area() / 2) + random.randint(-settings["crs_range"], settings["crs_range"])
        points = []
        lp1 = self.chunkPs[idx1].split('-')
        lp2 = self.chunkPs[idx2].split('-')
        lock = ''

        # combine the points
        for r, point in enumerate(lp1[:-1]):
            if point!='' and int(point) < sep_point and r<len(lp1[-1]):
                points.append(point)
                lock += lp1[-1][r]
        for r, point in enumerate(lp2[:-1]):
            if point!='' and int(point) >= sep_point and r<len(lp2[-1]):
                points.append(point)
                lock += lp2[-1][r]

        # combine the chunks
        crs_chunk = self.get_chunk(idx1)[:sep_point]+self.get_chunk(idx2)[sep_point:]
        self.chunks += crs_chunk
        self.chunkPs = np.append(self.chunkPs, '-'.join(points)+'-'+lock)

    def mutate_chunk(self, index, settings):
        '''Creates a copy of a chunk, mutates it, and then adds it.'''
        chunk = self.get_chunk(index)
        points = self.chunkPs[index].split('-')

        # weights for mutation
        weights = [1-settings['m_cPower'],settings['m_cPower']]

        # create a chunk where 1 is designated for cells that will flip between wall and air
        m_num = ''.join(str(random.choices([0, 1], weights=weights)[0]) for _ in range(self.area()))
        mutate_chunk = bitarray(m_num)

        # creates a chunk copy
        self.chunks += chunk

        # switches the cells last chunk (the new chunk) using mutate chunk as a loopup table
        for idx, cell in enumerate(chunk):
            if mutate_chunk[idx]==1:
                self.set_chunk_cell_flat(-1, idx, not self.get_chunk_cell_flat(-1, idx))
        points = self.remove_empties(points)

        # go through each point and randomly decide to mutate its position (unless its locked to a certain side)
        for idx, point in enumerate(list(int(i) for i in points[:-1])):
            weights = [1-settings['m_pPower'],settings['m_pPower'],settings['m_pPower'],settings['m_pPower'],settings['m_pPower']]
            if points[-1][idx] in ['>','<','^','_']:
                weights[1:5] = [0,0,0,0]
            h = point+random.choices([0, 1,-1,self.size[0], -self.size[0]], weights=weights)[0]
            points[idx] = f'{min(max(0, h), self.area()-1)}'
        self.chunkPs = np.append(self.chunkPs, '-'.join(points))
