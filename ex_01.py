from source.train_online import train_online
from source.train_offline import train_offline
from source.offline_ds_evaluation.evaluator import Evaluator
from source.offline_ds_evaluation.latex import create_latex_table
from multiprocessing import Pool
import os
import pickle
import numpy as np


# project parameters
envs = ['CartPole-v1', 'Acrobot-v1', "MiniGrid-LavaGapS6-v0", "MiniGrid-SimpleCrossingS9N1-v0"]
discounts = [0.99, 0.99, 0.95, 0.95]
buffer_types = ["er", "fully", "random"]
agent_types = ["BC", "BVE", "EVMCP", "DQN", "QRDQN", "REM", "BCQ", "CRR", "CQL"]
multiple_runs = 5
# experiment parameters
experiment = 1
seed = 42
# hyperparameters for online training
behavioral = "DQN"
transitions_online = 100000
# hyperparameters for offline training
transitions_offline = 2 * transitions_online
batch_size = 8
lr = [1e-4] * len(agent_types)
# parameters for evaluation
random_rewards = [0, -500, 0, 0]
optimal_rewards = [500, -75, 0.95, 0.961]


def create_ds(args):
    envid, discount = args

    train_online(experiment=experiment, agent_type=behavioral, discount=discount, envid=envid,
                 transitions=transitions_online, buffer_size=50000,
                 run=1, seed=seed)

def train(args):
    envid, discount = args

    for run in range(1, multiple_runs + 1):
        for a, agent in enumerate(agent_types):
            for bt in range(len(buffer_types)):
                train_offline(experiment=experiment, envid=envid, agent_type=agent, buffer_type=buffer_types[bt],
                              discount=discount, transitions=transitions_offline, batch_size=batch_size, lr=lr[a],
                              use_run=1, run=run, seed=seed+run, use_remaining_reward=(agent == "EVMCP"))

def assess_ds(args):
    use_run = 1
    envid, buffer_type, random_reward, optimal_reward = args

    with open(os.path.join("data", f"ex{experiment}", f"{envid}_run{use_run}_{buffer_type}.pkl"), "rb") as f:
        buffer = pickle.load(f)

    os.makedirs(os.path.join("results", "ds_eval"), exist_ok=True)
    evaluator = Evaluator(envid, buffer_type, buffer.state, buffer.action, buffer.reward, np.invert(buffer.not_done))

    path = os.path.join("results", "ds_eval", f"{envid}_{buffer_type}")
    return evaluator.evaluate(path, random_reward, optimal_reward, epochs=2)

if __name__ == '__main__':
    # assess all datasets
    results = []
    for e, env in enumerate(envs):
        for buffer in buffer_types:
            results.append(assess_ds((env, buffer, random_rewards[e], optimal_rewards[e])))

    for i in range(0, len(envs) * len(buffer_types), len(buffer_types)):
        texpath = os.path.join("results", "ds_eval", f"{results[i][0]}.tex")
        print(texpath)
        create_latex_table(texpath, results[i:i + len(buffer_types)])
