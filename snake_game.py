import pygame # for the game env
import random # for randomly placing the food
from enum import Enum 
from collections import namedtuple
import numpy as np

# 1st, initialize pygame:
pygame.init()

font = pygame.font.SysFont('arial', 25) 


# 1) reset function:
# after each game, the agent should be able to reset it and start a new game


# 2) reward

# 3) play(action) -> returns direction

# 4) track the current frame - game_iteration

# 5) change if_collision function to check if collision occurs

# enumeration instead of type code:
class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3 
    DOWN = 4
# we can now only use 1 of those 4 values - RIGHT, DOWN, etc, and not 'right' or right, 'down', etc.
# we assure that we use a correct direction.

# named tuple:
Point = namedtuple('Point', 'x, y') # 'Point' being the name of the tuple; 'x', 'y' being the members (must be in the same string)
# members can now be accessed with Point.x, Point.y
# this is a 'lightweight class' 
# no need to implement or subclass, just create an instance

# constants:
BLOCK_SIZE = 20
# the higher the number the faster your game is:
SPEED = 10
# RGB COLORS (0-255, 8 bit integers for light intensity)
BLACK = (0,0,0)
RED = (255, 0,0)
GREEN = (0,255,0)
GREEN1 = (0,255,0) #(0,0,255)
WHITEISH = (200,255,200)#(0,100,255)
WHITE = (255,255,255)
# used as pygame colors

# implementing the SnakeGame() class:
class SnakeGameAI: # agent controlled game now

    # init function gets width, height (default 640x480 pixels)
    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h 
        # init display
        self.display = pygame.display.set_mode((self.w, self.h)) # pass as tuple the dimensions of the display
        pygame.display.set_caption('Snake') # screen caption, not necessary tho
        self.clock = pygame.time.Clock() # keeping track of time
        self.reset()

    def reset(self):
        # WE REFACTOR THIS INTO A RESET FUNCTION:

        # init game state (place food/initial snake/direction (right in this case))
        self.direction = Direction.RIGHT # could use strings like 'r' for rights, etc, but this is ERROR PRONE - TYPE CODE!
        # use ENUMERATION !

        # store the position of the head:
        # we could use a list, storing list[0] = x-coordinate; list[1] = y-coordinate (starting at w,h - middle?) 
        # we could use a list, but that is ERROR PRONE
        # instead, we use a NAME TUPLE - which assign a meaning to each position in a tuple
        # allowing for a more readable and self documenting code
        self.head = Point(self.w/2, self.h/2) # we have to store the coordinates inside of the display, starting in the middle

        # creating and storing the snake itself in a list:
        # need 3 coordinates: 
        # head, another Point (at the same y coordinate but a bit to the left), 
        # we don't just want to say Point.x - 1, 
        # since the snake needs to be bigger than just 1 pixel
        # for this, we create a constant BLOCK_SIZE
        # and say x - 1xBLOCK_SIZE (1 block size to the left),
        # and lastly, 
        # 3rd coordinate is y 
        self.snake = [self.head, Point(self.head.x - BLOCK_SIZE, self.head.y),
                    self.head, Point(self.head.x - (2*BLOCK_SIZE), self.head.y)] # [body][head] initial snake shape

        # for the game state,
        # we keep track of game score 
        self.score = 0 
        # food:
        self.food = None
        # initially want to randomly place food
        # use a helper function
        self._place_food()
        self.frame_iteration = 0 # 0 in the beginning




    # place food helper method:
    def _place_food(self): # use a helper method to reuse later

        # we want to randomly have a coordinate inside the display dimensions
        # random xy-coordinate between values 0 to rounded number of blocks that can be placed in the display, 
        # i.e between 0 and width, height
        # gives us random food positions in the screen that are multiples of the block size
        x = random.randint(0, (self.w - BLOCK_SIZE)//BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.food = Point(x,y) # create a Point out of this with x,y
        # CAREFUL!
        # We don't want to place the food inside the snake
        # thus, we check
        if self.food in self.snake: # if food is in the list
            # call the function again, recursively, creating 2 new random variables
            self._place_food()


    # play step function:
    def play_step(self, action):
        # consists of several steps:
        self.frame_iteration += 1
        # 1. collect user input (what key the user pressed)
        for event in pygame.event.get(): 
            # event listener from the user for events
            # that happened inside 1 play step
            if event.type == pygame.QUIT:
                pygame.quit()
                quit() # to exit the python program

        
        # 2. move the snake
        # update the head
        self._move(action) # move the head of the snake, insert into the snake list
        self.snake.insert(0, self.head) # insert at the beginning 

        # 3. check if game over, quit if true
        # check 2 things: if we hit the boundary or the snake's tail
        reward = 0
        game_over = False

        # reward: 
        # eat food + 10
        # game over - 10
        # else 0

        if self._is_collision() or self.frame_iteration > 100*(len(self.snake)): # or if nothing happens for too long
            game_over= True
            reward = -10 
            return reward, game_over, self.score

        # 4. place new food or just move the snake (finalize the move step)
        if self.head == self.food:
            self.score+= 1
            reward = 10
            self._place_food()
            # remove the last block as we move or rather shift it:
        else:
            self.snake.pop()

        # 5. update the pygame ui and clock (will do this 1st to see stuff at first)
        # helper functions
        self._update_ui()
        self.clock.tick(SPEED) # let's us control the speed of the game - how fast the frame updates
        # 6. return if game over and score 
        
        # game_over = False 
        return reward, game_over, self.score
    
    def _is_collision(self, pt = None):

        if pt is None:
            pt = self.head
        if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0: # check if edges are hit
            return True 
        if pt in self.snake[1:]: # exclude the snake's head, start at idx 1
            return True  

        return False

    # update ui helper
    def _update_ui(self):
        # implement pygame function
        self.display.fill(BLACK) # fill the screen with black
        # order is IMPORTANT!

        # now draw the snake
        # iterate over all the points in the snake:
        for pt in self.snake:
            pygame.draw.rect(self.display, GREEN1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE)) # draw on the display for every point, 
            # use color blue, and draw a rectangle for the snake (in position x,y) of size BLOCK_SIZE^2
            # draw another smaller rectangle in another color and moved a bit:
            pygame.draw.rect(self.display, WHITEISH, pygame.Rect(pt.x+4, pt.y+4, 12, 12))

        # drawing the food:
        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))

        # draw the score in the upper left:
        # need to create a font 1st
        text = font.render('Score: ' + str(self.score), True, WHITE)
        # putting the text on the display:
        self.display.blit(text, [0,0]) # place in upper left

        # lastly:
        pygame.display.flip() # update the full display 'surface' to the screen
        # this is important, otherwise can't see the changes

    def _move(self, action):
        # [straight, right, left]
        # clockwise order of all possible directions:

        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]

        # get idx of current direction
        idx = clock_wise.index(self.direction) 

        # check the different possible states

        if np.array_equal(action, [1,0,0]):
            new_dir = clock_wise[idx] # keep current direction
        elif np.array_equal(action, [0,1,0]): # right turn
            next_idx = (idx + 1) % 4 # if at the end (u), do the next one
            new_dir = clock_wise[next_idx] # right turn r->d -> l -> u 
        else: # np.array_equal(action, [0,0,1]):
            next_idx = (idx - 1) % 4 # meaning we go counter clockwise
            # left turn r-> u -> l -> d 
            new_dir = clock_wise[next_idx]


        self.direction = new_dir

        # extract x,y:
        x = self.head.x 
        y = self.head.y 
        # check direction:
        if self.direction == Direction.RIGHT: 
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT: 
            x -= BLOCK_SIZE
        elif self.direction == Direction.UP: 
            y -= BLOCK_SIZE
        elif self.direction == Direction.DOWN: # BECAUSE WE START AT 0 AT THE TOP, WE ADD  
            y += BLOCK_SIZE

        self.head = Point(x,y)


# NO LONGER NEEDED:
# if we run the script as the main process, then:
# if __name__=='__main__':

#     # create a snake game:
#     game = SnakeGameAI()

#     # game loop:
#     while True: # initially and endless loop
#         game_over, score = game.play_step() # this will be a function

#         if game_over == True:
#             break 

#     print('Final Score: ', score)

#     # we want to check if game over then break
#     # break if game over 


#     # print the final score

#     # call pygame.quit() - closing all the modules