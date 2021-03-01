import os
import gym
import pickle
import torch
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt

from source.buffer import ReplayBuffer
from source.agents.dqn import DQN
from source.agents.rem import REM
from source.agents.hqn import HQN

seed = 42
batch_size = 256
buffer_size = 20000
transitions = 20000
show_every = 5
train_every = 1
train_start_iter = batch_size

env = gym.make('CartPole-v1')
obs_space = len(env.observation_space.high)
agent = DQN(obs_space, env.action_space.n, seed=seed)
buffer = ReplayBuffer(obs_space, buffer_size, batch_size, seed=seed)
# load saved buffer
with open(os.path.join("data", "buffer.pkl"), "rb") as f:
    buffer = pickle.load(f)
    buffer.calc_sim()
    buffer.calc_probas()

# seeding
env.seed(seed)
torch.manual_seed(seed)

all_rewards = []
ep_reward = 0
values = []

for iter in tqdm(range(transitions)):
    #minimum = max(0, iter - buffer_size)
    #maximum = max(batch_size, iter)
    minimum = 0
    maximum = 20000

    agent.train(buffer, minimum, maximum)

    if (iter+1) % show_every == 0:
        done = False
        state = env.reset()
        while not done:
            action, value = agent.policy(state, eval=True)
            state, reward, done, _ = env.step(action)
            #state = buffer.get_closest(state)
            ep_reward += reward
            values.append(value)

        all_rewards.append(ep_reward)
        print(f"cur_reward: ", ep_reward, "| mean reward: ", round(np.mean(all_rewards[-100:]),2),
                                          " | values: ", round(np.nanmean(values), 2))

        ep_reward = 0
        values = []

# mean rewards
mean_rewards = []
for i in range(len(all_rewards)):
    from_ = max(0, i-100)
    mean_rewards.append(np.mean(all_rewards[from_:i]))

plt.figure(figsize=(8, 6))
plt.ylabel("Reward")
plt.xlabel("Episodes")
plt.plot(range(len(all_rewards)), all_rewards, label="reward")
plt.plot(range(len(mean_rewards)), mean_rewards, label="mean reward")
plt.legend()
plt.show()