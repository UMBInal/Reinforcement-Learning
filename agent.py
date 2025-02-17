import torch 
import random 
import numpy as np 
from game import SnakeGameAI, Direction, Point
from collections import deque # double-ended queue - data structure for storing the memories

# CONSTANT PARAMS:

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001 # LEARNING RATE

class Agent:

    '''
    -game 
    -model 
    Training:
    * state = get_state(game)
    * action = get_move(state):
        -model.predict()
    * reward, game_over, score = game.play_step(action)
    * new_state = get_state(game)
    * remember 
    * model.train()
    '''
    # we need to store the game and the model in this class

    def __init__(self):
        # store params:
        self.n_games = 0 # keep track of the games played
        self.epsilon = 0 # param to control the randomness 
        self.gamma = 0 # the DISCOUNT RATE
        self.memory = deque(maxlen=MAX_MEMORY) # store memories up to 100,000; 
        # if the limit is exceeded remove elements from the left of the deque, calling popleft()
        # TODO: model, trainer
        self.model = None # TODO
        self.trainer = None # TODO 

    # calculate the state
    def get_state(self, game):
        # 11 states recall.
        head = game.snake[0]
        point_l = Point(head.x - 20, head.y)
        point_r = Point(head.x + 20, head.y)
        point_u = Point(head.x, head.y - 20)
        point_d = Point(head.x, head.y + 20)

        dir_l =  game.direction == Direction.LEFT
        dir_r = game.direction == Direction.RIGHT
        dir_u = game.direction == Direction.UP
        dir_d = game.direction == Direction.DOWN
        
        # the 11 states:
        state = [
            # Danger straight
            (dir_r and game.is_collision(point_r)) or 
            (dir_l and game.is_collision(point_l)) or 
            (dir_u and game.is_collision(point_u)) or 
            (dir_d and game.is_collision(point_d)),

            # Danger right
            (dir_u and game.is_collision(point_r)) or 
            (dir_l and game.is_collision(point_u)) or 
            (dir_r and game.is_collision(point_d)) or 
            (dir_d and game.is_collision(point_l)),

            # Danger left
            (dir_r and game.is_collision(point_u)) or 
            (dir_l and game.is_collision(point_d)) or 
            (dir_u and game.is_collision(point_l)) or 
            (dir_d and game.is_collision(point_r)), 

            # Move direction

            dir_l,
            dir_r,
            dir_u,
            dir_d,

            # Food location
            game.food.x < game.head.x, # food left
            game.food.x > game.head.x, # food right
            game.food.y < game.head.y, # food up
            game.food.y > game.head.y # food down
        ]

        return np.array(state, dtype=int)

    # remembers 
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) # the deque has an append method 
        # popleft() if MAX_MEMORY is reached

        
    # 2 different train functions:
    def train_long_memory(self):
        # get variables from the memory (a batch of them, e.g. 1000 samples from memory)
        # first check if we have 1000 samples in memory:
        if self.memory > BATCH_SIZE: # have random sample if true
            mini_sample = random.sample(self.memory, BATCH_SIZE) 
            # returns a list of tuples
        else:
            # if we don't have 1000 samples yet, then take all of the memories:
            mini_sample = self.memory 

        states, actions, rewards, next_states, dones = zip(*mini_sample) # puts every state, actions, etc together
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    # with only 1 step:
    def train_short_memory(self, state, action, reward, next_state, done):
        # optimization:
        self.trainer.train_step(state, action, reward, next_state, done) # train for 1 game step 


    def get_action(self, state):
        # do random moves in the beginning: tradeoff betweent exploration(random moves to explore the environtment) and exploitation(less randomness, exploit the agent model) 
        self.epsilon = 80 - self.n_games # depends on the number of games, hardcoded here
        final_move = [0,0,0]
        if random.randint(0,200) < self.epsilon:
            move = random.randint(0, 2) # gives a random value 0, 1 , or 2
            final_move[move] = 1 
            # the smaller the epsilon gets, the less random moves we have !!!
        else:
            state0 = torch.tensor(state, dtype = torch.float)
            # can be a raw value, take argmax of the tensor
            prediction = self.model.predict(state0) # predict the action based on 1 state
            move = torch.argmax(prediction).item() # now a single integer
            final_move[move] = 1

        return final_move

# global function train:

'''        
    Training:
    * state = get_state(game)
    * action = get_move(state):
        -model.predict()
    * reward, game_over, score = game.play_step(action)
    * new_state = get_state(game)
    * remember 
    * model.train()
'''
def train():
    plot_scores = [] # list to keep track of the scores and plotting later
    plot_mean_scores = [] # tracking the average scores
    total_score = 0 # total score, starts with 0
    record = 0 # best score, starts with 0 
    agent = Agent() # the agent
    game = SnakeGameAI() # the game 

    while True: # runs forever until script is closed
        # get old/current state
        state_old = agent.get_state(game) 

        # get move based on the current state:
        final_move = agent.get_action(state_old)

        # perform the move and get new state:
        reward, done, score = game.play_step(final_move)

        # get the new state:
        state_new = agent.get_state(game)

        # train the short memory of the agent (for only 1 step)
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        # remember:
        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            # train the long memory = replay memory/experience replay - trains on ALL THE PREVIOUS GAMES!
            # plot the results too
            # 1st reset the game:
            game.reset()
            # increase the number of games the agent has played:
            agent.n_games += 1
            agent.train_long_memory()

            if score > record:
                record = score 
                # TODO: agent.model.save()

            print('Game: ', agent.n_games, ' Score: ', score, ' Record: ', record)

            # TODO: plot 

if __name__ == 'main':
    train()