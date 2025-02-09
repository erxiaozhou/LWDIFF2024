import random
from typing import  List
import numpy as np


def choose_action_with_epsilon_greedy(actions: List[str], epsilon: float, scores: List[float]):
    if isinstance(scores, np.ndarray):
        scores = scores.tolist()
    if random.random() < epsilon:
        return choose_action_randomly(actions)
    else:
        return choose_action_by_scores(actions, scores)


def choose_action_randomly(actions: List[str]):
    if len(actions) == 1:
        return actions[0], 0
    action_index = random.randint(0, len(actions)-1)
    return actions[action_index], action_index


def choose_action_by_scores(actions: List[str], scores: List[float]):
    assert len(actions) == len(scores)
    if len(actions) == 1:
        return actions[0], 0
    max_score = max(scores)
    max_score_indexs = [i for i, score in enumerate(
        scores) if score == max_score]
    action_index = random.choice(max_score_indexs)
    return actions[action_index], action_index