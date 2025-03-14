import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random
from matplotlib.colors import ListedColormap

# Parameters
WORLD_SIZE = 125
EPOCHS = 1000
HUNGER_LIMIT = 11
init_p = [0.001, 0.2, 0.799]  # Probabilities for [HUNTER, ALIVE, DEAD]
HUNTER_REPRO_RATE = 1
CANIBALISM_INTERVAL = 3
interpolation = 'nearest'
HUNTER_SPAWNER_PROB = 0.001
CELL_SPAWNER_PROB = 0.01

# Celltypes
DEAD = 0
ALIVE = 1
HUNTER = 2
BORDER = 3
HUNTER_SPAWNER = 4
CELL_SPAWNER = 5


world = np.random.choice([ALIVE, DEAD], size=(WORLD_SIZE, WORLD_SIZE), p=[0.3, 0.7])
hunger_levels = np.zeros((WORLD_SIZE, WORLD_SIZE), dtype=int)

def count_neighbors(world, x, y):
    cnt_nbrs = 0
    left = (x - 1) % WORLD_SIZE
    right = (x + 1) % WORLD_SIZE
    up = (y - 1) % WORLD_SIZE
    down = (y + 1) % WORLD_SIZE
    
    neighbors = [(left, up), (x, up), (right, up), (left, y), (right, y), (left, down), (x, down), (right, down)]
    
    for nx, ny in neighbors:
        if world[nx, ny] == ALIVE:
            cnt_nbrs += 1
    
    return cnt_nbrs

def eat_neighbors_and_reproduce_or_starve(world, hunger_levels, x, y):
    found_Food = False
    neighbors = get_neighbours(x, y)

    possible_snacks = []
    for nx, ny in neighbors:
        if world[nx, ny] == ALIVE:
            possible_snacks.append((nx, ny))
            #world[nx, ny] = HUNTER
            #hunger_levels[nx, ny] = 0  # Reset hunger of new hunter
            found_Food = True
            #cur_repro += 1
    
    for cur_repro in range(HUNTER_REPRO_RATE):
        if found_Food:
            new_x, new_y = random.choice(possible_snacks)
            world[new_x, new_y] = HUNTER
            hunger_levels[new_x, new_y] = 0

    if found_Food:
        hunger_levels[x, y] = 0  # Reset hunger if hunter eats
    else:
        hunger_levels[x, y] += 1
        
        if hunger_levels[x, y] >= HUNGER_LIMIT:
            world[x, y] = DEAD  # Kill hunter if it starves
        else:
            # Move to another spot if no food was found
            possible_positions = []
            possible_positions.append((x, y))
            for nx, ny in neighbors:   
                if world[nx, ny] == DEAD: # Ensure no other hunter and no border is already there
                    possible_positions.append((nx, ny))
                elif world[nx, ny] == HUNTER and hunger_levels[x, y] > HUNGER_LIMIT-CANIBALISM_INTERVAL:
                    possible_positions = [(nx, ny)]
                    world[nx, ny] = DEAD
                    hunger_levels[x, y] = 0
                    break

            new_x, new_y = random.choice(possible_positions)
            world[x, y] = DEAD
            world[new_x, new_y] = HUNTER
            hunger_levels[new_x, new_y] = hunger_levels[x, y]
            hunger_levels[x, y] = 0

def get_neighbours(x, y):
    left = (x - 1) % WORLD_SIZE
    right = (x + 1) % WORLD_SIZE
    up = (y - 1) % WORLD_SIZE
    down = (y + 1) % WORLD_SIZE
    
    neighbors = [(left, up), (x, up), (right, up), (left, y), (right, y), (left, down), (x, down), (right, down)]
    return neighbors

def reproduce(world, hunger_levels):
    new_world = np.copy(world)
    new_hunger_levels = np.copy(hunger_levels)
    
    for x in range(WORLD_SIZE):
        for y in range(WORLD_SIZE):
            if world[x, y] == HUNTER:
                eat_neighbors_and_reproduce_or_starve(new_world, new_hunger_levels, x, y)
            else:
                cnt_nbrs = count_neighbors(world, x, y)
                if world[x, y] == ALIVE:
                    if cnt_nbrs < 2 or cnt_nbrs > 3:
                        new_world[x, y] = DEAD
                elif world[x, y] == DEAD:
                    if cnt_nbrs == 3:
                        new_world[x, y] = ALIVE
                elif world[x, y] == HUNTER_SPAWNER:
                    if np.random.rand() < HUNTER_SPAWNER_PROB:
                        neighbours = get_neighbours(x, y)
                        poss_pos = []
                        for nx, ny in neighbours:
                            if world[nx, ny] == DEAD:
                                poss_pos.append((nx, ny))
                        
                        if len(poss_pos) > 0:
                            for _ in range(random.choice(range(len(poss_pos)))):
                                new_x, new_y = random.choice(poss_pos)
                                new_world[new_x, new_y] = HUNTER
                                new_hunger_levels[new_x, new_y] = 0

                elif world[x, y] == CELL_SPAWNER:
                    if np.random.rand() < CELL_SPAWNER_PROB:
                        neighbours = get_neighbours(x, y)
                        poss_pos = []
                        for nx, ny in neighbours:
                            if world[nx, ny] == DEAD:
                                poss_pos.append((nx, ny))
                        
                        if len(poss_pos) > 0:
                            for _ in range(random.choice(range(len(poss_pos)))): # Spawn a random amount of new cells at the same time
                                new_x, new_y = random.choice(poss_pos)
                                new_world[new_x, new_y] = ALIVE
    
    return new_world, new_hunger_levels

def update(frame):
    global world, hunger_levels
    world, hunger_levels = reproduce(world, hunger_levels)
    im.set_data(world)
    return [im]

if __name__ == '__main__':
    fig, ax = plt.subplots()
    world = np.random.choice([HUNTER, ALIVE, DEAD], size=(WORLD_SIZE, WORLD_SIZE), p=init_p)
    #world = np.zeros((WORLD_SIZE, WORLD_SIZE), dtype=int)
    np.fill_diagonal(world, ALIVE)
    #fill reverse diagonal
    np.fill_diagonal(np.fliplr(world), ALIVE)
    world[25, :int(WORLD_SIZE/2)-25] = BORDER
    world[25, int(WORLD_SIZE/2)+25:] = BORDER
    world[-25, :int(WORLD_SIZE/2)-25] = BORDER
    world[-25, int(WORLD_SIZE/2)+25:] = BORDER
    world[25, :int(WORLD_SIZE/2)-15]= HUNTER_SPAWNER
    world[0:25, 0:25]= np.random.choice([CELL_SPAWNER, DEAD], size=(25, 25), p=[0.05, 0.95])

    #world = np.random.choice([ALIVE, DEAD], size=(WORLD_SIZE, WORLD_SIZE), p=[0.2, 0.8])
    # set upper triagonal to hunters
    #for i in range(WORLD_SIZE):
    #    for j in range(i, WORLD_SIZE):
    #        world[i, j] = HUNTER
    


    hunger_levels = np.zeros((WORLD_SIZE, WORLD_SIZE), dtype=int)
    
    def update_world(_):
        global world, hunger_levels
        world, hunger_levels = reproduce(world, hunger_levels)
        im.set_array(world)
        return [im]
    
    cmap = ListedColormap(['white', 'green', 'red', 'black', 'purple', 'blue'])
    im = ax.imshow(world, vmin=0, vmax=5, cmap=cmap, interpolation=interpolation)
    ani = animation.FuncAnimation(fig, update_world, frames=EPOCHS, interval=100, repeat=False)
    
    plt.show()
