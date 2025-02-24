import random

from bitarray import bitarray

from chunk_operator import *
class WaveChunks(Chunk_Operator):
    def __init__(self, c_size, b_size):
        Chunk_Operator.__init__(self,c_size)

        self.board_filled = bitarray('0'*(b_size[0]*b_size[1]))
        self.chunks = bitarray('0'*(c_size[0]*c_size[1])*(b_size[0]*b_size[1]))
        self.chunkPs = np.full((b_size[0]*b_size[1]), 'x'*(len(f'{self.chunk_amt()}')*4+8))
        self.cur_chunk = 0
        self.b_size = b_size

        self.free_spaces = {}

        self.cr = {
            "lkL":None,
            "lkR":(c_size[0]-1)+(random.randint(0,c_size[1]-1)*c_size[0]),
            "lkU":None,
            "lkD":self.area()-random.randint(1,c_size[0]),
        }
        print(self.size)

    def find_empty_chunks(self):
        empties = []
        for i,item in enumerate(self.board_filled):
            if item == 0: empties.append(i)
        return empties
    def make_new_request(self):
        add_spaces = {}
        if self.cr['lkL']:
            add_spaces.update({f'{self.cur_chunk - 1}': {"lkR":self.cr['lkL']+(self.size[0]-1)}})
        if self.cr['lkR']:
            add_spaces.update({f'{self.cur_chunk + 1}': {"lkL": self.cr['lkR']-(self.size[0]-1)}})
        if self.cr['lkU']:
            add_spaces.update({f'{self.cur_chunk-self.b_size[0]}': {"lkD": self.cr['lkU']+self.area()-self.size[0]-1}})
        if self.cr['lkD']:
            add_spaces.update({f'{self.cur_chunk + self.b_size[0]}': {"lkU": self.cr['lkD']-self.area()+self.size[0]-1}})

        for space in add_spaces:

            if int(space)<self.b_size[0]*self.b_size[1] and self.board_filled[int(space)] == 0:
                if space in self.free_spaces.keys():
                    self.free_spaces[space] = add_spaces[space] | self.free_spaces[space]
                else:
                    self.free_spaces.update({space: add_spaces[space]})

        choices = list(self.free_spaces.keys())
        if choices!=[]:
            self.cur_chunk = int(random.choice(choices))
            new_cr = self.free_spaces[str(self.cur_chunk)]
        else:
            choices=self.find_empty_chunks()
            if choices==[]:
                choices = [0]
            self.cur_chunk = random.choice(choices)
            new_cr = {"lkL": None,"lkR": None,"lkU": None,"lkD": None,}

        self.cr = {"lkL": None,"lkR": None,"lkU": None,"lkD": None,}

        add_locks = random.randint(1,2)
        for space in new_cr:
            self.cr[space] = new_cr[space]

        keys = list(self.cr.keys())
        random.shuffle(keys)

        for space in dict([(key, self.cr[key]) for key in keys]):
            if self.cr[space] ==None and add_locks>0:
                if space=='lkL' and self.cur_chunk%self.b_size[0]!=0:
                    self.cr[space]=(random.randint(0,self.size[1]-1)*self.size[0])
                    add_locks -= 1
                elif space=='lkR' and (self.cur_chunk+1)%self.b_size[0]!=0:
                    self.cr[space]=(self.size[0]-1)+(random.randint(0,self.size[1]-1)*self.size[0])
                    add_locks -= 1
                elif space=='lkU' and self.cur_chunk>self.b_size[0]-1:
                    self.cr[space] = random.randint(0, self.size[0] - 1)
                    add_locks -= 1
                elif space=='lkD' and self.cur_chunk<self.area()-self.b_size[0]+1:
                    self.cr[space]=self.area()-random.randint(1,self.size[0]-1)
                    add_locks-=1

        if str(self.cur_chunk) in self.free_spaces.keys():
            self.free_spaces.pop(str(self.cur_chunk))
    def append_chunk(self, new_chunk, point):
        self.set_chunk(self.cur_chunk, new_chunk)
        self.board_filled[self.cur_chunk] = 1
        self.chunkPs[self.cur_chunk] = point

        self.make_new_request()

    def create_chunk_imgs(self):
        imgs = []
        for idx in range(self.b_size[0]*self.b_size[1]):
            img = pygame.surface.Surface((self.size[0], self.size[1]))
            if self.board_filled[idx]==1:
                img.fill((255,255,255))

                for y in range(self.size[1]):
                    for x in range(self.size[0]):
                        if  self.get_chunk_cell(idx, y, x):
                            img.set_at((x, y),(60,40,40))

                        img.set_at((x, y), (255, 255, 255) if self.get_chunk_cell(idx, y, x)==1 else (0, 0, 0))

                points = self.chunkPs[idx].split('-')
                #print(self.chunkPs[idx])
                img.set_at((0,0), (255, 0, 0))

                for point in list(int(i) for i in points[:-1]):
                    img.set_at((point % self.size[0], point // self.size[1]), (255, 0, 0))
            imgs.append(pygame.transform.scale(img, (self.size[0] * self.imgMlt, self.size[1] * self.imgMlt)))

        return imgs

wc = WaveChunks((10,10),(5,5))
