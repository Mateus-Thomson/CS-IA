
class Base():
    def flat_to_x(self, flat, size):
        '''Inputs a flat number and size and outputs its x coord.'''
        return flat % size[0]

    def flat_to_y(self, flat, size):
        '''Inputs a flat number and size  and outputs its y coord.'''
        return flat // size[0]

    def flat_to_coord(self, flat, size):
        '''Inputs a flat number and size  and outputs its 2d position.'''
        return (self.flat_to_x(flat,size), self.flat_to_y(flat,size))

    def coord_to_flat(self, coord, size):
        '''Inputs a 2d coord and size  and outputs its flat position.'''
        return coord[0]+coord[1]*size[0]

    def remove_empties(self, list):
        '''Removes the empty entities in a list'''
        return [x for x in list if x!='']