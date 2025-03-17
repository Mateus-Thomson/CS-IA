from scripts.libs import *
from scripts.chunk_operator import *
from scripts.pathfinding import *

class WaveChunks(Chunk_Operator):
    '''Operates the wave collapse algorithm. Extends Chunk_Operator.'''
    def __init__(self, c_size, b_size):
        '''Constructs the essential variables and initalizes the Chunk_Operator Extension.'''
        Chunk_Operator.__init__(self,c_size)

        self.board_filled = bitarray('0'*(b_size[0]*b_size[1]))
        self.chunks = bitarray('0'*(c_size[0]*c_size[1])*(b_size[0]*b_size[1]))
        self.chunkPs = np.full((b_size[0]*b_size[1]), 'x'*(len(f'{self.size[0]*self.size[1]}')*4+20))
        self.cur_chunk = 0
        # size of the board. (basically how many chunks the board is made out of)
        self.b_size = b_size
        # NOTE: self.b_size = board_size, self.size = chunk_size

        self.free_spaces = {}

        self.cr = {
            "lkL":None,
            "lkR":(c_size[0]-1)+(random.randint(0,c_size[1]-1)*c_size[0]),
            "lkU":None,
            "lkD":self.area()-random.randint(1,c_size[0]),
        }

        self.ex_chunk = bitarray('')
        self.cur_comb = 0
        self.optimal_path = []
        self.optimal_length = 0
        self.optimal_route = []
        self.final_comb = None

    def full_size(self):
        '''Returns the full size of the board.'''
        return [self.size[0]*self.b_size[0],self.size[1]*self.b_size[1]]

    def find_empty_chunks(self):
        '''Returns the positions of empty chunks.'''
        empties = []
        for i,item in enumerate(self.board_filled):
            if item == 0: empties.append(i)
        return empties

    def make_new_request(self):
        '''Creates a new request for the next chunk generation to follow.'''

        # create all possible spaces
        add_spaces = {}
        if self.cr['lkL']:
            add_spaces.update({f'{self.cur_chunk - 1}': {"lkR":self.cr['lkL']+(self.size[0]-1)}})
        if self.cr['lkR']:
            add_spaces.update({f'{self.cur_chunk + 1}': {"lkL": self.cr['lkR']-(self.size[0]-1)}})
        if self.cr['lkU']:
            add_spaces.update({f'{self.cur_chunk-self.b_size[0]}': {"lkD": self.cr['lkU']+self.area()-self.size[0]-1}})
        if self.cr['lkD']:
            add_spaces.update({f'{self.cur_chunk + self.b_size[0]}': {"lkU": self.cr['lkD']-self.area()+self.size[0]-1}})

        # ensure that the spaces are valid
        for space in add_spaces:
            if int(space)<self.b_size[0]*self.b_size[1] and self.board_filled[int(space)] == 0:
                if space in self.free_spaces.keys():
                    self.free_spaces[space] = add_spaces[space] | self.free_spaces[space]
                else:
                    self.free_spaces.update({space: add_spaces[space]})


        choices = list(self.free_spaces.keys())
        if choices!=[]: # randomly chose what lock to use
            self.cur_chunk = int(random.choice(choices))
            new_cr = self.free_spaces[str(self.cur_chunk)]
        else: # if there are no locks just create a chunk without it
            choices=self.find_empty_chunks()
            if choices==[]:
                choices = [0]
            self.cur_chunk = random.choice(choices)
            new_cr = {"lkL": None,"lkR": None,"lkU": None,"lkD": None,}

        self.cr = {"lkL": None,"lkR": None,"lkU": None,"lkD": None,}

        # add new locks on top of the existing ones
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
        '''Add a new chunk to the board and call for a new request.'''
        self.set_chunk(self.cur_chunk, new_chunk)
        self.board_filled[self.cur_chunk] = 1
        self.chunkPs[self.cur_chunk] = point

        self.make_new_request()

    def export_chunk(self, imgs, settings):
        '''Creates a final chunk to export. Also creates the combinations needed to find hence path.'''

        # create export_chunk
        self.ex_chunk = bitarray('')
        export_points  = []
        render_exchunk = pygame.surface.Surface(self.full_size())
        for i, img in enumerate(imgs):
            t_img = pygame.transform.scale(img, (img.get_width() / self.imgMlt, img.get_height() / self.imgMlt))
            render_exchunk.blit(t_img,((i % self.b_size[0]) * (self.size[0]), (i // self.b_size[1]) * (self.size[1])))
        for y in range(render_exchunk.get_height()):
            for x in range(render_exchunk.get_width()):
                if render_exchunk.get_at((x,y))==(255,255,255): self.ex_chunk+='1'
                else:self.ex_chunk+='0'
        for y in range(render_exchunk.get_height()):
            for x in range(render_exchunk.get_width()):
                if render_exchunk.get_at((x,y))==(255,0,0):
                    self.ex_chunk[self.coord_to_flat([x,y], self.full_size())] = 0
                    export_points.append([x,y])
                    render_exchunk.set_at((x,y), (0, 0, 0))

        # create combinations
        self.final_comb  = combinations(export_points, 2)

        # skip combinations that are too close to each other.
        skips = set()
        for com in self.final_comb :
            if (math.dist(com[0],com[1])) < settings["minDist"]:
                skips.add(tuple(com[0]))
        for skip in skips:
            export_points.remove(list(skip))

        # shuffle and limit the remaining combinations
        self.final_comb  = list(combinations(export_points, 2))
        random.shuffle(self.final_comb)
        self.final_comb  = self.final_comb[:settings["maxComp"]]

        return render_exchunk



wc = WaveChunks((10,10),(5,5))
