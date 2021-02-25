class SplitJoin:
    def __init__(self, language_model):
        self.words = language_model.weights.keys()

    def split(self, word_parts):
        split = False
        splitted_tok = []

        for i in self.w_pos(word_parts):
            token = word_parts[i]
            if len(token) > 2:
                pos = 1
                while pos < len(token):
                    if token[:pos] in self.words and token[pos:] in self.words:
                        if token not in self.words:
                            splitted_tok = list(word_parts)
                            splitted_tok[i] = token[pos:]
                            splitted_tok.insert(i, ' ')
                            splitted_tok.insert(i, token[:pos])
                            split = True
                            break
                    pos += 1
            if split:
                break
        return splitted_tok, split

    def join(self, word_parts):
        flag = False
        w_posit = self.w_pos(word_parts)
        i = 0
        while i < len(w_posit) - 1:
            left = word_parts[w_posit[i]]
            right = word_parts[w_posit[i + 1]]
            if left not in self.words or right not in self.words:
                if left + right in self.words:
                    word_parts[w_posit[i]] = left + right
                    for pos in sorted(range(w_posit[i] + 1, w_posit[i + 1] + 1), reverse=True):
                        del word_parts[pos]
                    flag = True
            if flag:
                break
            i += 1

        return word_parts, flag

    def w_pos(self, word_parts):
        ic = 0
        words_positions = []
        for token in word_parts:
            if token.isalpha():
                words_positions.append(ic)
            ic += 1
        return words_positions

