# coding:utf-8

# -----World Setting------
graphic_file = 'resources/world.txt'
grid_width = 50
wall_color = '#D3D3D3'
guard_color = '#000000'
thief_color = '#06B1C8'
escape_color = '#DAA72A'
speed = 500

# -----Learning Parameters---
alpha = 0.1    # learning rate
gamma = 0.9    # importance of next action
epsilon = 0.01  # exploration chance


# ------Reward and Punishment----
ESCAPE = 50
CAUGHT = -100
MOVE_REWARD = -1
