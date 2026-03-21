import numpy as np

class PuzzleModel:
    @staticmethod
    def get_pos(val, goal):
        res = np.where(goal == val)
        return res[0][0], res[1][0]

    @staticmethod
    def h_misplaced(state, goal):
        return np.sum((state != goal) & (state != 0))

    @staticmethod
    def h_manhattan(state, goal):
        dist = 0
        for i in range(state.shape[0]):
            for j in range(state.shape[1]):
                val = state[i, j]
                if val != 0:
                    gr, gc = PuzzleModel.get_pos(val, goal)
                    dist += abs(i - gr) + abs(j - gc)
        return dist

    @staticmethod
    def h_custom(state, goal):
        manhattan = PuzzleModel.h_manhattan(state, goal)
        conflicts = 0
        if state[-1, -1] != 0: conflicts += 2
        return manhattan + conflicts