from gettext import translation

from scripts.libs import *
from scripts.base import *

class Cycle(Base):
    '''Operates and handles all generation commands. Extends Base.'''
    def __init__(self):
        '''Constructs the essential variables.'''
        self.cur_gen = 0
        self.font = pg.font.SysFont("Arial", 24)
        self.start_time = time.time()

        self.final = False
        self.render = None
        self.exported = False

    def gen_text(self):
        '''Creates text showing the current generation.'''
        text = self.font.render(f'Gen: {self.cur_gen}', False, (255,255,255))
        surf = pygame.surface.Surface(text.get_size())
        surf.blit(text, (0,0))
        return surf

    def mutate(self, cOP, settings):
        '''Makes copies of existing chunks and mutates them'''
        for r in range(settings['m_Amt']):
            cOP.mutate_chunk(r, settings)
        return cOP

    def limit(self, cOP, settings):
        '''Caps the population at a certain number.'''
        cOP.chunkPs = cOP.chunkPs[:settings['pop_Cap']]
        cOP.chunks = cOP.chunks[:settings['pop_Cap'] * cOP.area()]
        return cOP

    def crossover(self,cOP, settings):
        '''Makes copies of existing chunks and stitches pairs of them together.'''
        for r in range(0, min(settings["crs_Amt"] * 2, cOP.chunk_amt()), 2):
            cOP.crossover_chunk(r, r + 1, settings)
        return cOP

    def new_chunks(self, cOP, wc, amount):
        '''Creates a population of entirely new chunks.'''
        for _ in range(amount):
            cOP.create_chunk(wc.cr['lkL'],wc.cr['lkR'],wc.cr['lkU'],wc.cr['lkD'])
        return cOP

    def remove_dups(self, cOP):
        '''Removes reoccuring chunks'''
        new_points = np.empty((0))
        possible_dupes = [] # first searches through points
        # checking points first instead of the full board saves time
        for r, points in enumerate(cOP.chunkPs):
            if points not in new_points:
                new_points = np.append(new_points, points)
            else:
                x = int(np.where(new_points == points)[0][0])
                possible_dupes.append([r, x])

        actual_dupes = [] # looks at the actual boards to confirm that the boards a dup
        for dupe in possible_dupes:
            if cOP.get_chunk(dupe[0]) == cOP.get_chunk(dupe[1]):
                actual_dupes.append(dupe[0])
        for dupe in actual_dupes:
            cOP.delete_chunk(dupe)

        return cOP

    def sort_and_clear(self, AStar, cOP):
        '''Sorts the chunks and clears ones that don't have any possible direct path.'''
        valid_chunks = bitarray('')
        valid_points = cOP.create_empty_points()
        path_nums = []
        path_lengths = []

        for idx in range(cOP.chunk_amt()):
            paths = []
            for com in list(combinations(cOP.chunkPs[idx].split('-')[:-1], 2)): # gets the path for every combination of points
                if '' not in com: # bugfix --- sometimes the points would glitch and show up as an empty string. This remedies that.
                    paths.append(AStar.get_path(cOP.get_chunk(idx), int(com[0]), int(com[1]), cOP.size))
                else: print("No point found!")

            paths = list(x for x in paths if x != []) # lists all paths that exists. excludes paths that don't.
            path_nums.append(len(paths))

            if paths != []:
                o = []
                for path in paths:
                    o.append(len(path))
                path_lengths.append((o, len(path_lengths))) # this is used for sorting later
        path_lengths = sorted(path_lengths, key=lambda x: max(x[0]), reverse=True)

        for idx, num in enumerate(path_nums):
            if num != 0: # if a path doesn't have 0 steps (aka: if it exists), then its valid.
                valid_chunks += cOP.get_chunk(idx)
                valid_points = np.append(valid_points, cOP.chunkPs[idx])

        cOP.chunks = valid_chunks
        cOP.chunkPs = valid_points
        cOP.reorder_chunks(list(map(lambda x: x[1], path_lengths))) # sorts by path length
        return cOP


    def generation(self, AStar, wc, cOP, settings):
        '''Generation cycle, goes through each step of evolving one generation into the next, and then outputs the result.'''
        # --- CREATE INITAL POPULATION ---
        if cOP.chunks == bitarray(''):
            cOP = self.new_chunks(cOP, wc, settings['init_Pop'])

        # ---CROSSOVER---
        cOP = self.crossover(cOP, settings)

        # ---MUTATE---
        cOP = self.mutate(cOP, settings)

        # ---NEW CHUNKS---
        cOP = self.new_chunks(cOP, wc, settings['pop_Per_Gen'])

        # bugfix --- fixes points sometimes overlapping with walls
        cOP.point_pos_fixer()

        # ---SORT and CLEAR---
        cOP = self.sort_and_clear(AStar, cOP)

        # --- REMOVE DUPLICATES ---
        cOP = self.remove_dups(cOP)

        # ---LIMIT---
        cOP = self.limit(cOP, settings)

        return cOP, cOP.create_chunk_imgs()

    def create_walls(self, cOP):
        '''Creates walls on the sides that don't have access points'''
        split = cOP.chunkPs[0].split('-')
        l = []

        if '^' not in split[-1]: l += [x for x in range(cOP.size[0])]
        if '_' not in split[-1]: l += [cOP.area() - x for x in range(cOP.size[0])]
        if '<' not in split[-1]: l += [x for x in range(0, cOP.size[1], cOP.size[0])]
        if '>' not in split[-1]: l += [cOP.size[0] - 1 + x for x in range(0, cOP.size[1], cOP.size[0])]
        for cell in l:
            cOP.set_chunk_cell_flat(0, cell, 1)
            if str(cell) in split:
                split.remove(str(cell))
        cOP.chunkPs[0] = '-'.join(split)
        return cOP

    def gen_end(self, cOP, wc):
        '''After the Gen Cap has been hit, use the top chunk and add it to the wc (wave collapse) board. Afterwards, generate a new request. '''
        cOP = self.create_walls(cOP)
        wc.append_chunk(cOP.get_chunk(0), cOP.chunkPs[0])
        self.cur_gen = 0
        cOP.chunks = bitarray('')
        cOP.chunkPs = cOP.create_empty_points()
        other_imgs = wc.create_chunk_imgs()
        return cOP, wc, other_imgs

    def paths_text(self, wc):
        '''Creates text showing the current paths.'''
        text = self.font.render(f'{wc.cur_comb}/{len(wc.final_comb)}   MaxPath: {wc.optimal_length}', False, (255, 255, 255))
        surf = pygame.surface.Surface(text.get_size())
        surf.blit(text, (0, 0))
        return surf

    def final_path_loop(self, format, tabs, wc, AStar):
        '''Draw and find the best path in the completed board, and then export it.'''

        tabs[2].blit(pygame.transform.scale(self.render, (
        self.render.get_width() * wc.imgMlt, self.render.get_height() * wc.imgMlt)), (0, 0)) # draws current board

        text = self.paths_text(wc)
        tabs[2].blit(text, (0, tabs[2].get_height() - text.get_height())) # draws current statistics

        if wc.cur_comb < len(wc.final_comb):
            for com in wc.optimal_path: # un-highlight current best path
                self.render.set_at(com, (0, 0, 0))
            com = wc.final_comb[wc.cur_comb]
            path = AStar.get_path(wc.ex_chunk, self.coord_to_flat(com[0],wc.full_size()), self.coord_to_flat(com[1],wc.full_size()),
                                  wc.full_size())
            if len(path) > wc.optimal_length: # change optimal path if new path is better
                wc.optimal_path = [com[0], com[1]]
                wc.optimal_length = len(path)
                wc.optimal_route = path
            wc.cur_comb += 1
            for com in wc.optimal_path:
                self.render.set_at(com, (255, 0, 0)) # highlight current best path
        else:
            for p in wc.optimal_route[1:-1]:
                self.render.set_at(self.flat_to_coord(p,wc.full_size()), (100, 30, 30))
            if not self.exported:
                self.exported = True
                self.export(format, wc, self.render)

    def export(self, format, wc, render):
        '''Export the board based on the selected format.'''

        time_taken = time.time() - self.start_time

        s = time_taken % (24 * 3600)
        h = s // 3600
        s %= 3600
        m = s // 60
        s %= 60

        full_export = {"chunk": wc.ex_chunk.to01(), "points": wc.optimal_path,
                       "flat_points": [self.coord_to_flat(wc.optimal_path[0], wc.full_size()), self.coord_to_flat(wc.optimal_path[1], wc.full_size())],
                       "size": wc.full_size(), "time_taken": f'{h}h {m}m {s}s'}

        if format in ["txtboard", "image", "listboard"]: # remove path visibility
            ex_render = render.copy()
            for y in range(ex_render.get_height()):
                for x in range(ex_render.get_width()):
                    if render.get_at((x, y)) not in [(0,0,0), (255,0,0), (255,255,255)]:
                        ex_render.set_at((x,y), (0,0,0))

        if format in ["txtboard", "listboard"]: # simplier exports need to be formatted correctly
            string = ""
            for y in range(ex_render.get_height()):
                for x in range(ex_render.get_width()):
                    if [x,y] in full_export["points"]:
                        string+="2"
                    else:
                        string+= f'{int(ex_render.get_at((x,y))!=(0,0,0))}'
                string += "\n"

            if format== "listboard":
                lst = [[int(v) for v in l] for l in [list(x) for x in string.split('\n')]]
                with open('export.json', 'w') as f:
                    f.write(pprint.pformat(lst, compact=True))
            else: # txtboard
                with open('export.txt', 'w') as f: f.write(string)
        elif format == "image":
            pg.image.save(ex_render, 'export.png')

        elif format == "txt":
            with open('export.txt', 'w') as f:
                f.write(
                    f"chunk:\n{full_export["chunk"]}\npoints:\n{full_export["points"]}\nflat_points:\n{full_export["flat_points"]}\nsize:\n{full_export["size"]}\ntime_taken:\n{full_export["time_taken"]}\n")

        else: # json
            with open('export.json', 'w') as f:
                f.write(pprint.pformat(full_export, compact=True).replace("'", '"'))

