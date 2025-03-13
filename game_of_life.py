import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random
from matplotlib.colors import ListedColormap

WORLD_SIZE = 125
EPOCHS = 1000
ALIVE = 1
DEAD = 0
HUNTER = 2
HUNGER_LIMIT = 10
init_p = [0.001, 0.4, 0.599]  # Probabilities for [HUNTER, ALIVE, DEAD]
HUNTER_REPRO_RATE = 2
CANIBALISM_INTERVAL = 3

world = np.random.choice([ALIVE, DEAD], size=(WORLD_SIZE, WORLD_SIZE), p=[0.5, 0.5])
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
    left = (x - 1) % WORLD_SIZE
    right = (x + 1) % WORLD_SIZE
    up = (y - 1) % WORLD_SIZE
    down = (y + 1) % WORLD_SIZE
    
    neighbors = [(left, up), (x, up), (right, up), (left, y), (right, y), (left, down), (x, down), (right, down)]

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
                if world[nx, ny] == DEAD: # Ensure no other hunter is already there
                    possible_positions.append((nx, ny))
                if world[nx, ny] == HUNTER and hunger_levels[x, y] > HUNGER_LIMIT-CANIBALISM_INTERVAL:
                    possible_positions = [(nx, ny)]
                    world[nx, ny] = DEAD
                    hunger_levels[x, y] = 0
                    break

            new_x, new_y = random.choice(possible_positions)
            world[x, y] = DEAD
            world[new_x, new_y] = HUNTER
            hunger_levels[new_x, new_y] = hunger_levels[x, y]
            hunger_levels[x, y] = 0

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
    
    return new_world, new_hunger_levels

def update(frame):
    global world, hunger_levels
    world, hunger_levels = reproduce(world, hunger_levels)
    im.set_data(world)
    return [im]

if __name__ == '__main__':
    fig, ax = plt.subplots()
    world = np.random.choice([HUNTER, ALIVE, DEAD], size=(WORLD_SIZE, WORLD_SIZE), p=init_p)
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
    
    cmap = ListedColormap(['white', 'green', 'red'])
    im = ax.imshow(world, vmin=0, vmax=2, cmap=cmap, interpolation='bilinear')
    ani = animation.FuncAnimation(fig, update_world, frames=EPOCHS, interval=100, repeat=False)
    
    plt.show()
