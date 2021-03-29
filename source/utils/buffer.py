import numpy as np
import torch
from tqdm import tqdm
from .utils import cosine_similarity
from sklearn.decomposition import PCA

class ReplayBuffer():

    def __init__(self, obs_space, buffer_size, batch_size, seed=None):
        self.buffer_size = buffer_size
        self.batch_size = batch_size
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.rng = np.random.default_rng(seed=seed)

        self.idx = 0
        self.current_size = 0

        self.state = np.zeros((self.buffer_size, obs_space), dtype=np.float32)
        self.next_state = np.zeros((self.buffer_size, obs_space), dtype=np.float32)
        self.action = np.zeros((self.buffer_size, 1), dtype=np.uint8)
        self.reward = np.zeros((self.buffer_size, 1))
        self.not_done = np.zeros((self.buffer_size, 1))

        # norm is for special experiments, probas is uniform until updated by experiments
        self.norm = np.ones((self.buffer_size))
        self.probas = np.ones((self.buffer_size)) / self.buffer_size

    def add(self, state, action, reward, done, next_state):

        self.state[self.idx] = state
        self.next_state[self.idx] = next_state
        self.action[self.idx] = action
        self.reward[self.idx] = reward
        self.not_done[self.idx] = 1. - float(done)

        self.idx = (self.idx + 1) % self.buffer_size
        self.current_size = min(self.current_size + 1, self.buffer_size)

    def sample(self, minimum=None, maximum=None, use_probas=False):

        # we can set custom min/max to e.g. iterate over the dataset
        if minimum != None and maximum != None:
            ind = np.arange(minimum, maximum)
        else:
            ind = np.arange(0, self.current_size)

        # we can use custom sampling probabilities
        if use_probas:
            ind = self.rng.choice(ind, size=self.batch_size, replace=False, p=self.probas)
        else:
            ind = self.rng.choice(ind, size=self.batch_size, replace=False)

        return (torch.FloatTensor(self.state[ind]).to(self.device),
                torch.LongTensor(self.action[ind]).to(self.device),
                torch.FloatTensor(self.next_state[ind]).to(self.device),
                torch.FloatTensor(self.reward[ind]).to(self.device),
                torch.FloatTensor(self.not_done[ind]).to(self.device)
                )

    def set_seed(self, seed):
        self.rng = np.random.default_rng(seed=seed)

    def subset(self, minimum, maximum):
        self.state = self.state[minimum:maximum]
        self.next_state = self.next_state[minimum:maximum]
        self.action = self.action[minimum:maximum]
        self.reward = self.reward[minimum:maximum]
        self.not_done= self.not_done[minimum:maximum]

        self.idx = 0
        self.current_size = maximum - minimum

    def rand_subset(self, samples, ):
        ind = np.arange(0, self.current_size)
        ind = self.rng.choice(ind, size=samples, replace=False)

        self.state = self.state[ind]
        self.next_state = self.next_state[ind]
        self.action = self.action[ind]
        self.reward = self.reward[ind]
        self.not_done = self.not_done[ind]

        self.idx = 0
        self.current_size = samples

    #####################################
    # Special functions for experiments #
    #####################################

    def calc_density(self):
        self.probas = []


        #rand_encoder = np.random.randn(self.state.shape[1], 2)
        #state = self.state @ rand_encoder

        pca = PCA(n_components=2)
        state = pca.fit_transform(self.state)

        import matplotlib.pyplot as plt
        plt.figure()
        plt.scatter(state[:,0], state[:,1], s=1, alpha=0.1)
        plt.show()

        mesh = 100
        density = np.zeros((mesh, mesh))
        min_x, min_y = np.min(state[:,0]), np.min(state[:,1])
        max_x, max_y = np.max(state[:, 0]), np.max(state[:, 1])
        step_x = (max_x - min_x) / mesh
        step_y = (max_y - min_y) / mesh

        state_key = []

        for s in state:
            i = int((s[0] - min_x) / step_x) - 1
            j = int((s[1] - min_y) / step_y) - 1
            density[i,j] += 1

            state_key.append((i,j))

        for (i,j) in state_key:
            self.probas.append(1/density[i,j])

        self.probas = np.asarray(self.probas) / np.sum(self.probas)

    def calc_sim(self):
        self.norm = np.linalg.norm(self.state, axis=1).reshape(-1,1)
        self.probas = np.empty((self.buffer_size, self.buffer_size))
        for i in range(self.buffer_size):
            self.probas[i] = (self.state @ self.state[i].reshape(-1, 1) / self.norm / self.norm[i]).flatten()
        self.probas = np.mean(self.probas, axis=1)
        self.probas -= (np.min(self.probas))
        self.probas = 1 / (self.probas + 9e-9)
        self.probas /= np.sum(self.probas)

    def get_closest(self, new_state):
        """
        calc_sim must be called before this method!
        """
        sim = self.state @ new_state.reshape(-1,1) / self.norm / np.linalg.norm(new_state)
        return self.state[sim.argmax()]
