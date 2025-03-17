from scripts.libs import *
from scripts.base import *

class A_Star(Base):
    '''Class responsible for finding the best path from one point to another.'''

    def calc_G(self, pos):
        '''Calculate G cost (distance from start to input pos).'''
        return math.dist(self.flat_to_coord(self.start,self.size), self.flat_to_coord(pos,self.size))

    def calc_H(self, pos):
        '''Calculate H cost (distance from end to input pos).'''
        return math.dist(self.flat_to_coord(self.end,self.size), self.flat_to_coord(pos,self.size))

    def calc_F(self, pos):
        '''Calculate F cost (H + G cost).'''
        return self.calc_H(pos) + self.calc_G(pos)

    def fill_all_costs(self, pos):
        '''Find the G,H, and F cost for input pos and add it to their respective boards.'''
        self.GBoard.update({f'{pos}':self.calc_G(pos)})
        self.HBoard.update({f'{pos}': self.calc_H(pos)})
        self.FBoard.update({f'{pos}': self.calc_F(pos)})

    def initialize(self,input_board, start, end, size):
        '''Intializes all needed variables before searching for a path.'''
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

    def get_path(self, input_board, start, end, size):
        '''Returns a path from one point to another.'''
        # initialize
        self.initialize(input_board, start, end, size)

        # get costs for current position
        self.fill_all_costs(self.cur)

        # find path
        return self.loop()

    def get_max_values(self, dct):
        '''Gets a list of the max values in an input dict.'''
        av = dict(filter(lambda x: int(x[0]) not in self.closedList, dct.items()))
        return list(filter(lambda x: x[1]==min(av.values()), av.items()))

    def get_sur(self, L):
        '''Gets the surrounding nodes around the current nodes, excluding the ones in input L.'''
        row_clamp = (self.flat_to_y(self.cur,self.size) * self.size[0], self.flat_to_y(self.cur,self.size) * self.size[0] + self.size[0])
        sur = [min(max(self.cur - 1, row_clamp[0]), row_clamp[1]-1),
               min(max(self.cur + 1, row_clamp[0]), row_clamp[1]-1), self.cur + self.size[0],
               self.cur - self.size[0]]

        return list(filter(lambda x: x >= 0 and x!=self.cur and x< len(self.board) and x not in L and self.board[x] == 0 and x in self.whitelist, sur))

    def loop(self):
        '''The loop that goes through the process of finding the path.'''
        while True: # finding start to end through closedList
            self.closedList.append(self.cur)

            # find surrounding nodes not already in closedList
            valid_sur = self.get_sur(self.closedList)

            # fill costs for each surrounding node
            for item in valid_sur:
                self.fill_all_costs(item)


            mx = self.get_max_values(self.FBoard) # get the max values of FBoard
            if len(mx)!= 1:
                mx = self.get_max_values(self.GBoard)  # if there's more than one max FCost, get the max values of GBoard
                if len(mx) != 1:
                    mx = self.get_max_values(self.HBoard) # if theres more than one max GCost, get the max values of HBoard

            if mx==[]: return []  # if there are no max values to be found, that means that there's no valid path.

            self.cur = int(mx[0][0]) # set cur to max value (disregards if there's more than one max HCost, simply picks the first one available

            if self.cur == self.end: # break the loop if current node is the end node. Means the closedList has reached the end.
                break

        self.closedList.append(self.cur) # adds current node (aka end) to closedList so its complete
        self.whitelist = self.closedList # creates whitelist


        self.cur = self.end
        while True: # goes through closedList again to find the final path
            if self.cur == self.start: # path is complete
                break
            else:
                valid_sur = self.get_sur(self.path)
                if valid_sur == []: # if valid_sur == [], it means it's a dead end and that that point should no longer be on the whitelist.
                    self.whitelist.remove(self.cur)
                    self.cur = self.end
                    self.path=[] # reset the path and try again
                else:
                    self.path.append(self.cur) # add current node to path
                    GCosts = [(self.GBoard[f'{item}'], item) for item in valid_sur]
                    self.cur = min(GCosts)[1] # new node equals the lowest GCost
        self.path.append(self.cur)
        return self.path

