class BorTree:
    class Candidate:
        def __init__(self, word, error_weight, language_weight):
            self.word = word
            self.error_weight = error_weight
            self.language_weight = language_weight

        def __repr__(self):
            return str(self.__dict__)

    class Node:
        def __init__(self, c):
            self.c = c
            self.children = []
            self.end_of_word = False
            self.language_weight = 0

    def __init__(self, error_model, language_model):
        self.main_node = self.Node(None)
        self.best_list = []
        self.error_model = error_model
        self.language_model = language_model

    def generate(self, word, max_number_of_candidates=5, max_sum_of_weights=10, part=1):
        self.max_num_cand = max_number_of_candidates
        self.weight_sum_mx = max_sum_of_weights
        self.best_list = []
        self.find_candidates(word, part=part)
        return self.best_list

    def fit(self):
        for word, weight in self.language_model.weights.items():
            node = self.main_node
            for c in word:
                c_in_child = False
                for child in node.children:
                    if child.c == c:
                        node = child
                        c_in_child = True
                        break
                if not c_in_child:
                    new_node = self.Node(c)
                    node.children.append(new_node)
                    node = new_node
            node.language_weight = weight
            node.end_of_word = True

    def can_be_added(self, weight, part=1):
        a = len(self.best_list) <= part * self.max_num_cand
        return a and weight < self.weight_sum_mx

    def find_candidates(self, prefix, result='', root=None, weight=0, part=1):  # returns number of occurencies

        if root is None:
            root = self.main_node
        node = root

        if len(prefix) >= 1:
            c = prefix[0]

            for child in node.children:
                if child.c != c:
                    fix = child.c

                    additional_weight = self.error_model.weights[''][fix]
                    if self.can_be_added(weight + additional_weight, part):
                        self.find_candidates(prefix, result + fix, child, weight + additional_weight, part)

                    additional_weight = self.error_model.weights[c][fix]
                    if self.can_be_added(weight + additional_weight, part):
                        self.find_candidates(prefix[1:], result + fix, child, weight + additional_weight, part)

                else:

                    self.find_candidates(prefix[1:], result + c, child, weight, part)

                    additional_weight = self.error_model.weights[''][c]
                    if self.can_be_added(weight + additional_weight, part):
                        self.find_candidates(
                            prefix, result + c, child, weight + additional_weight, part)

            additional_weight = self.error_model.weights[c]['']
            w = weight + additional_weight
            if self.can_be_added(w):
                self.find_candidates(prefix[1:], result, node, w, part)
        else:
            if node.end_of_word:
                candidate = self.Candidate(result, weight, node.language_weight)
                new_candidate = True
                for cand in self.best_list:
                    if cand.word == candidate.word:
                        new_candidate = False
                        cand.language_weight = max(candidate.language_weight, cand.language_weight)
                        cand.error_weight = min(
                            candidate.error_weight, cand.error_weight)
                if new_candidate:
                    if len(self.best_list) <= self.max_num_cand:
                        self.best_list.append(candidate)

