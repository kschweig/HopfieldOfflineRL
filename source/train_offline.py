import os
import pickle
import torch
import numpy as np
from tqdm import tqdm
from torch.utils.tensorboard import SummaryWriter
from .utils.evaluation import evaluate
from .utils.utils import get_agent, make_env


def train_offline(experiment, envid, agent_type="DQN", buffer_type="er", discount=0.95, transitions=200000, batch_size=128,
                  use_run=1, run=1, seed=42,
                  use_subset=False, lower=None, upper=None,
                  use_progression=False, buffer_size=None,
                  use_remaining_reward=False):

    # over how many episodes do we take average and how much gradient updates to next
    mean_over = 100
    evaluate_every = 100

    env = make_env(envid)
    obs_space = len(env.observation_space.high)
    agent = get_agent(agent_type, obs_space, env.action_space.n, discount, seed)

    # load saved buffer
    with open(os.path.join("data", f"ex{experiment}", f"{envid}_run{use_run}_{buffer_type}.pkl"), "rb") as f:
        buffer = pickle.load(f)

    # configure buffer
    buffer.batch_size = batch_size

    #######################
    # experiment specific #
    #######################

    if use_remaining_reward: buffer.calc_remaining_reward(discount=discount)
    if use_subset: buffer.subset(lower, upper)

    #######################

    # seeding
    env.seed(seed)
    np.random.seed(seed)
    buffer.set_seed(seed)
    torch.manual_seed(seed)

    writer = SummaryWriter(log_dir=os.path.join("runs", f"ex{experiment}", f"{envid}_{buffer_type}_{agent_type}_run{run}"))

    all_rewards = []

    for iter in tqdm(range(transitions), desc=f"{agent_type} ({envid}) {buffer_type}, run {run}"):
        if use_progression:
            minimum = max(0, iter - buffer_size)
            maximum = max(batch_size, iter)
        else:
            minimum = None
            maximum = None

        agent.train(buffer, writer, maximum, minimum)

        if (iter+1) % evaluate_every == 0:
            all_rewards = evaluate(env, agent, writer, all_rewards, over_episodes=mean_over)

    # mean rewards
    mean_rewards = []
    for i in range(1, len(all_rewards)):
        from_ = max(0, i-mean_over)
        mean_rewards.append(np.mean(all_rewards[from_:i]))

    return agent