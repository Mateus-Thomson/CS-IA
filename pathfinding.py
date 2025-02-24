import pygame as pg
import pygame.draw
from bitarray import bitarray
import math

size = 10
grid = bitarray('0110100010111101100010011011010101010110101110110011100110110001010001010000110110110100010010101000')
ps = '75-18-66-45-0000'

class A_Star(object):
    def __init__(self):
        pass

    def to_x(self, flat):
        return flat%self.size[0]
    def to_y(self, flat):
        return flat//self.size[0]

    def calc_G(self, pos):
        return math.hypot(self.to_x(self.start) - self.to_x(pos), self.to_y(self.start) - self.to_y(pos))

    def calc_H(self, pos):
        return math.hypot(self.to_x(self.end) - self.to_x(pos), self.to_y(self.end) - self.to_y(pos))

    def calc_F(self, pos):
        return self.calc_H(pos) + self.calc_G(pos)

    def fill_all_costs(self, pos):
        self.GBoard.update({f'{pos}':self.calc_G(pos)})
        self.HBoard.update({f'{pos}': self.calc_H(pos)})
        self.FBoard.update({f'{pos}': self.calc_F(pos)})

    def get_path(self, input_board, start, end, size):
        #create boards
        self.GBoard = {}
        self.HBoard = {}
        self.FBoard = {}
        self.board = input_board
        self.closedList = []
        self.path = []

        self.whitelist = [x for x in range(len(self.board))]

        self.start = start
        self.end = end
        self.cur = start

        self.size = size

        self.fill_all_costs(self.cur)
        return self.loop()

    def get_max_values(self, dct):
        av = dict(filter(lambda x: int(x[0]) not in self.closedList, dct.items()))
        return list(filter(lambda x: x[1]==min(av.values()), av.items()))

    def get_sur(self, L):
        row_clamp = (self.to_y(self.cur) * self.size[0], self.to_y(self.cur) * self.size[0] + self.size[0])
        sur = [min(max(self.cur - 1, row_clamp[0]), row_clamp[1]-1),
               min(max(self.cur + 1, row_clamp[0]), row_clamp[1]-1), self.cur + self.size[0],
               self.cur - self.size[0]]

        return list(filter(lambda x: x >= 0 and x!=self.cur and x< len(self.board) and x not in L and self.board[x] == 0 and x in self.whitelist, sur))

    def loop(self):
        while True:

            self.closedList.append(self.cur)

            valid_sur = self.get_sur(self.closedList)

            for item in valid_sur:
                self.fill_all_costs(item)

            mx = self.get_max_values(self.FBoard)
            if len(mx)!= 1:
                mx = self.get_max_values(self.HBoard)
                if len(mx) != 1:
                    mx = self.get_max_values(self.GBoard)

            if mx==[]: return []

            self.cur = int(mx[0][0])

            if self.cur == self.end:
                break

        self.closedList.append(self.cur)

        self.whitelist = self.closedList


        self.cur = self.end
        while True:
            if self.cur == self.start:
                break
            else:
                valid_sur = self.get_sur(self.path)
                if valid_sur == []:
                    self.whitelist.remove(self.cur)
                    self.cur = self.end
                    self.path=[]
                else:
                    self.path.append(self.cur)
                    HCosts = [(self.HBoard[f'{item}'], item) for item in valid_sur]
                    self.cur = max(HCosts)[1]
        self.path.append(self.cur)
        return self.path
        #[78, 77, 76, 66]

AStar = A_Star()


window = pg.display.set_mode((500,500))
m = 20

paths = []
from itertools import combinations

for set in list(combinations(ps.split('-')[:-1],2)):
    paths.append(AStar.get_path(grid, int(set[0]), int(set[1]), [size,size]))

while False:
    window.fill((60,60,60))
    for event in pg.event.get():
        if event.type == pg.QUIT:
            exit()

    for idx, item in enumerate(grid):

        x = idx%size
        y = idx//size
        color = (255*item,255*item,255*item)
        if str(idx) in ps.split('-')[:-1]:
            color = (255,0,0)
        pygame.draw.rect(window, color, (x*m+10,y*m+10,m,m))

        if idx in AStar.closedList:
            pygame.draw.rect(window, (0, 0,255), (x * m + 10, y * m + 10, m, m), 1)
        for p, path in enumerate(paths):
            if idx in path:
                pygame.draw.rect(window, (0,255,0), (x * m + 10, y * m + 10, m, m), 1)


    pygame.display.flip()
