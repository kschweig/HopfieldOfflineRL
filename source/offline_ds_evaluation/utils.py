import numpy as np
import torch.nn.functional as F


def entropy(values):
    probs = F.softmax(values, dim=1).detach().cpu().numpy()
    return -np.sum(probs * np.log(probs), axis=1)

def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / np.linalg.norm(v1) / np.linalg.norm(v2)

class BColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'