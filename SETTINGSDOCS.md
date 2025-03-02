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




