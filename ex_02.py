from source.train_online import train_online
from source.train_offline import train_offline
from multiprocessing import Pool

"""
Test Batch Constrained Q-learning
"""

# project parameters
envs = ['MiniGrid-Empty-Random-6x6-v0', 'MiniGrid-Unlock-v0', 'MiniGrid-DistShift1-v0', 'MiniGrid-SimpleCrossingS9N1-v0']
discounts = [0.95]*4
agent_types = ["SQN"]
multiple_runs = 2
# experiment parameters
experiment = 2
seed = 42
# hyperparameters for online training
behavioral = "DQN"
transitions_online = 400000
# hyperparameters for offline training
transitions_offline = 200000
batch_size = 128


def train(args):
    envid, discount = args
    """
    train_online(experiment=experiment, agent_type=behavioral, discount=discount, envid=envid,
                 transitions=transitions_online, buffer_size=50000,
                 run=1, seed=seed)
    """
    for agent in agent_types:
        for run in range(1, multiple_runs + 1):
            train_offline(experiment=experiment, envid=envid, agent_type=agent, discount=discount,
                          transitions=transitions_offline, batch_size=batch_size, use_run=1, run=run, seed=seed+run, use_remaining_reward=True)


if __name__ == '__main__':
    with Pool(len(envs), maxtasksperchild=1) as p:
        p.map(train, zip(envs, discounts))