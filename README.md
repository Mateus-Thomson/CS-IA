## Installs
* pip install bitarray==3.0.0
* pip install numpy==2.2.1
* pip install pygame-ce==2.5.2
## Settings

* chunk_size | INT
  * Dictates the size of each individual chunk on the board.
* board_size | INT
  * Dictates the size of the board.
* m_Amt | INT
  * Dictates how many mutated copies will be added per generation
* m_cPower | FLOAT
  * Chance for an individual cell to mutate and switch between wall and air.
* m_pPower | FLOAT
  * Chance for a point to move its position when mutating.
* init_Pop | INT
  * The starting population that is created for generation 1.
* crs_Amt | INT
  * The amount of crossovers created every generation.
* crs_range | INT
  * Defines the bounds of the splitting point when a crossover is being created. (Branches out from the center)
* pop_Per_Gen | INT
  * The amount of entirely new chunks added every generation
* pop_Cap | INT
  * Caps out the population at a certain number, cutting off chunks that don't peform as well. 
* gen_Cap | INT
  * The amount of generations that occur before the best chunk is used.
* minDist | INT
  * The minimum distance the start and end point can be when dictating the final path (Increase this number for bigger boards.)
* maxComp | INT
  * The maximum ammount of comparisons taken when searching for a final path. 

USE THE 1, 2, and 3 KEYS TO CHANGE TABS ONCE YOU CONFIRM YOUR SETTINGS.

## Formats
* json | JSON
  * Will output a dictionary containing chunks, points, flat_points, size, and time taken
* txt | TXT
  * Will output a txt file containing chunks, points, flat_points, size, and time taken
* image | PNG
  * Will output a png file showing the full board and the points.
* txtboard | txt
  * Will output a txt file only containing the full board as a paragraph of strings
  * 1=wall, 0=air, 2=point
* listboard
  * Will output a json file only containing the full boardas a list
  * 1=wall, 0=air, 2=point
