from collections import defaultdict
import json


class LanguageModel:

    def __init__(self):
        self.counters = defaultdict(int)
        self.weights = None
        self.size = 0

    def load_json(self, json_path):
        (size, stat) = json.loads(open(json_path, "r").read())
        self.size, self.counters = size, stat
        self.calculate_weights()

    def store_json(self, json_path):
        with open(json_path, "w") as file:
            file.write(json.dumps((self.size, self.counters)))

    def update_statistics(self, token):
        if token in self.counters:
            self.counters[token] += 1
        else:
            self.counters[token] = 0
        self.size += 1

    def calculate_weights(self):
        self.weights = defaultdict(lambda: 0.5 / self.size)
        for item, stat in self.counters.items():
            self.weights[item] = stat / self.size
