from scripts.wave_collapse import *
from scripts.user_input import *
from scripts.cycle import *

pg.font.init()

# create default settings
settings = \
{"chunk_size":10,
 "board_size":5,
 "m_Amt": 40,
 "m_cPower": 0.1,
 "m_pPower": 0.1,
 "init_Pop": 10,
 "crs_Amt":10,
 "crs_range": 20,
 "pop_Per_Gen": 30,
 "pop_Cap":15,
 "gen_Cap":100,
 "minDist":4,
 "maxComp":500,
 }

# call user input window
settings, format = user_input(settings)

# initalize chunk operator
cOP = Chunk_Operator((settings["chunk_size"],settings["chunk_size"]))

# create image lists
imgs = cOP.create_chunk_imgs()
other_imgs = []

# initialize window and tabs
window = pg.display.set_mode((500,500))
tabs = [pygame.surface.Surface((500,500)) for x in range(3)]

# set current tab to 0
active_tab = 0

# initialize wave collapse algorithm
wc = WaveChunks(cOP.size,(settings["board_size"],settings["board_size"]))

# initialize A* algorithm
AStar = A_Star()

# initialize generation cycle
cycle = Cycle()

# create generation text
gtext = cycle.gen_text()

while True:
    # fill tab bgs
    tabs[0].fill((0,120,120))
    tabs[1].fill((120, 120, 0))
    tabs[2].fill((120, 0, 120))

    # keep up the generation cycle as long as the board has spaces
    if 0 in wc.board_filled:
        cOP, imgs = cycle.generation(AStar, wc, cOP, settings)
        cycle.cur_gen += 1
        gtext = cycle.gen_text()

    # render gen text to tab[0]
    tabs[0].blit(gtext, (0, window.get_height() - gtext.get_height()))

    # render chunk images on tab[0]
    x = 0
    y = 0
    for i, img in enumerate(imgs):
        n_img = img.copy()
        paths = []

        tabs[0].blit(n_img, (x, y))
        x += cOP.size[0] * cOP.imgMlt + 2
        if x + cOP.size[0] * cOP.imgMlt > window.get_width():
            x = 0
            y += cOP.size[1] * cOP.imgMlt + 2

    # end chunk generation when gen_cap is exceeded
    if cycle.cur_gen>=settings["gen_Cap"]:
        cOP, wc, other_imgs = cycle.gen_end(cOP, wc)

    # render board images on tab[1]
    for i, o_img in enumerate(other_imgs):
        tabs[1].blit(o_img, ((i%wc.b_size[0])*(wc.size[0])*wc.imgMlt, (i//wc.b_size[1])*(wc.size[1])*wc.imgMlt))

    # start the search for the final path if the board is full
    if not 0 in wc.board_filled and not cycle.final:
        cycle.final=True
        cycle.render = wc.export_chunk(other_imgs, settings)

    # loop for searching for the final path
    if cycle.final:
        cycle.final_path_loop(format, tabs, wc, AStar)

    # keys for switching between tabs
    for event in pg.event.get():
        if event.type == pg.QUIT:
            quit()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_1:
                active_tab = 0
            if event.key == pg.K_2:
                active_tab = 1
            if event.key == pg.K_3:
                active_tab = 2

    # render current tab
    window.blit(tabs[active_tab], (0,0))

    pg.display.flip()



