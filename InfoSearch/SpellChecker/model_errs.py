import Levenshtein
import numpy as np
from collections import defaultdict
import json

def flatten_dictionary(dictionary):
    values = []
    for d in dictionary.values():
        for v in d.values():
            values.append(v)
    return values


class ErrorModel:
    def __init__(self):
        self.counters = defaultdict(lambda: defaultdict(int))

    def update_statistics(self, y_true, y_pred):
        operations = Levenshtein.opcodes(y_true, y_pred)
        for op in operations:
            name = op[0]
            i1, i2 = op[1], op[2]

            if name == 'delete':
                for c in y_true[i1:i2]:
                    self.counters[c][''] += 1
                continue
            j1, j2 = op[3], op[4]
            if name == 'insert':
                for c in y_pred[j1:j2]:
                    self.counters[''][c] += 1
                continue
            if name == 'replace':
                for i in range(len(y_true[i1:i2])):
                    c1 = y_true[i1:i2][i]
                    c2 = y_pred[j1:j2][i]
                    self.counters[c1][c2] += 1
                continue

    def calculate_weights(self):
        tmp_dict = flatten_dictionary(self.counters)

        freq_arr = np.sort(tmp_dict)[::-1]
        weight_arr = np.log1p(freq_arr).astype(float)[::-1]
        freq_of_w = dict()
        for i in range(len(freq_arr)):
            freq_of_w[freq_arr[i]] = weight_arr[i]
        default_weight = np.max(weight_arr)
        self.weights = defaultdict(lambda: defaultdict(lambda: default_weight))
        for el in self.counters.items():
            for k2 in el[1].keys():
                self.weights[el[0]][k2] = \
                    freq_of_w[self.counters[el[0]][k2]]

    def load_json(self, json_path):
        stat = json.loads(open(json_path, "r").read())
        self.counters = stat
        self.calculate_weights()

    def store_json(self, json_path):
        with open(json_path, "w") as file:
            file.write(json.dumps((self.counters)))

