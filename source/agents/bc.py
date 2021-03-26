from source.agents.agent import Agent
import numpy as np
from source.evaluation import entropy
import os
import torch
import torch.nn as nn
from source.networks.actor import Actor


class BehavioralCloning(Agent):

    def __init__(self,
                 obs_space,
                 action_space,
                 discount,
                 seed=None):
        super(BehavioralCloning, self).__init__(obs_space, action_space, discount, seed)

        # Number of training iterations
        self.iterations = 0

        # loss function
        self.ce = nn.CrossEntropyLoss()

        # Explicit Policy
        self.actor = Actor(obs_space, action_space).to(self.device)

        # Optimization
        self.lr = 0.001
        self.optimizer = torch.optim.Adam(params=self.actor.parameters(), lr=self.lr)

    def get_name(self) -> str:
        return "BC"

    def policy(self, state, eval=False):
        with torch.no_grad():
            state = torch.FloatTensor(state).to(self.device)
            actions = self.actor(state).cpu()

            return torch.argmax(actions).item(), np.nan, entropy(actions)

    def train(self, buffer, writer, minimum=None, maximum=None, use_probas=False):
        # Sample replay buffer
        state, action, _, _, _ = buffer.sample(minimum, maximum, use_probas)

        # log state distribution
        if self.iterations % 1000 == 0:
            writer.add_histogram("train/states", state, self.iterations)

        # predict action the behavioral policy would take
        pred_action = self.actor.forward(state)

        # calculate CE-loss
        loss = self.ce(pred_action, action.squeeze(1))

        # log cross entropy loss
        writer.add_scalar("train/CE-loss", torch.mean(loss).detach().cpu().item(), self.iterations)

        # Optimize the policy
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        self.iterations += 1

    def determinancy(self):
        return 0.0

    def save_state(self) -> None:
        torch.save(self.actor.state_dict(), os.path.join("models", self.get_name() + "_actor.pt"))
        torch.save(self.optimizer.state_dict(), os.path.join("models", self.get_name() + "_optim.pt"))

    def load_state(self) -> None:
        self.actor.load_state_dict(torch.load(os.path.join("models", self.get_name() + "_actor.pt")))
        self.optimizer.load_state_dict(torch.load(os.path.join("models", self.get_name() + "_optim.pt")))
