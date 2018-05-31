# coding:utf-8

import random
import pickle
import config as cfg


class QLearn:
    # Q-learning:
    #    Q(s, a) += alpha * (reward(s,a) + gamma * max(Q(s', a') - Q(s,a))
    #
    #    - alpha is the learning rate.
    #    - gamma is the value of the future reward.
    def __init__(self, actions, alpha=cfg.alpha, gamma=cfg.gamma, epsilon=cfg.epsilon):
        self.q = {}
        self.alpha = alpha
        self.gamma = gamma
        self.actions = actions
        self.epsilon = epsilon  # explore const
        self.load_memory()
        
    def get_utility(self, state, action):
        return self.q.get((state, action), 0.0)

    # choose optimal action based on state
    def choose_action(self, state):
        # try random action once in a while to explore new paths
        if random.uniform(0.0,1.0) < self.epsilon:
            q = [self.get_utility(state, act) for act in self.actions]
            max_utility = min(q)

            # choose random one from the best actions
            if q.count(max_utility) > 1 and q.count(max_utility) < 4:
                best_actions = [self.actions[i] for i in range(len(self.actions)) if q[i] != max_utility]
                action = random.choice(best_actions)
            else:
                action = self.actions[q.index(max_utility)]
        else:
            q = [self.get_utility(state, act) for act in self.actions]
            max_utility = max(q)

            # choose random one from the best actions
            if q.count(max_utility) > 1:
                best_actions = [self.actions[i] for i in range(len(self.actions)) if q[i] == max_utility]
                action = random.choice(best_actions)
            else:
                action = self.actions[q.index(max_utility)]
        return action

    # memorize the utility
    def memorize(self):
        with open("resources/memory.txt","wb") as f:
            pickle.dump(self.q, f)

    # load memory
    def load_memory(self):
        try:
            f = open("resources/memory.txt","rb")
        except:
            return

        with f:
            self.q = pickle.load(f)

    # learn
    def learn(self, state1, action, state2, reward):
        old_utility = self.q.get((state1, action), None)
        if old_utility is None:
            self.q[(state1, action)] = reward
        # update utility
        else:
            next_max_utility = max([self.get_utility(state2, a) for a in self.actions])
            self.q[(state1, action)] = old_utility + self.alpha * (reward + self.gamma * next_max_utility - old_utility)
        print (self.q)
