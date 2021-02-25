#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import operator
import re
from string import punctuation
from algo_bor import BorTree
from model_errs import ErrorModel
from model_language import LanguageModel
from model_split_join import SplitJoin

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

english = {"th", "he", "an", "nd", "in", "er", "ha", "re", "of", "or", "hi", "at", "ou", "en", "to", "al", "is", "ll",
           "on", "it", "es", "se", "nt", "ed", "ve", "ar", "sh", "ng", "ea", "ho", "st", "me", "be", "le", "as", "fo",
           "ne", "un", "te", "sa", "lo", "wi", "rd", "ai", "no", "il", "et", "ri", "el", "ro", "wh", "de", "ch", "ma",
           "om", "d,", "us", "ee", "em", "ut", "ot", "so", ":1", "am", "we", "co", "wa", "s,", "ur", "id", "im", "ra",
           "ay", "e,", "ey", "ca", "ke", "ld", "ti", "go", "ce", "la", "ir", "ow", "ns", "av", "li", "gh", "mo", "ad",
           "ic", "ei", "rs", "da", ":2", "ye", "od", "ie", "pe", "ss"}

russian = {"но", "ст", "ра", "на", "ро", "то", "ал", "ов", "пр", "не", "по", "го", "ко", "ор", "ва", "ос", "ен", "ре",
           "ны", "та", "ни", "ом", "ли", "ел", "ль", "ав", "ка", "ол", "ер", "ан", "ин", "ат", "де", "ог", "во", "ми",
           "ый", "ем", "ла", "те", "он", "ес", "от", "со", "ск", "да", "ил", "ве", "ас", "ит", "ть", "ло", "и,", "ак",
           "ди", "од", "ам", "ри", "ле", "ет", "мо", "ти", "тр", "за", "ой", "ки", "нн", "ви", "ру", "ся", "об", "ар",
           "же", "че", "бо", "ег", "се", "ий", "им", "до", "кр", "ез", "вы", "ме", "из", "ьн", "га", "ик", "ма", "ым",
           "ши", "лс", "ей", "тв", "ир", "ис", "ул", "бе", "ци", "их"}

en = 'QWERTYUIOP{}ASDFGHJKL:"ZXCVBNM<>?~' + "qwertyuiop[]asdfghjkl;'zxcvbnm,.`"
ru = 'ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,Ё' + "йцукенгшщзхъфывапролджэячсмитьбюё"
ru_to_en = str.maketrans(ru, en)
en_to_ru = str.maketrans(en, ru)


def get_N_gram(word, N_GRAM = 3):
    new_set = set()
    for i in range(len(word) - (N_GRAM - 1)):
        new_set.add(word[i:i + N_GRAM])
    return new_set

def fix_query(query):
    tokens = re.split('([' + punctuation + ' ' + '])', query)
    candidate = fix_tokens(tokens)

    layout = ''
    for word in query.split():
        new = word
        rus = new.translate(en_to_ru)
        new = word
        eng = new.translate(ru_to_en)

        if len(get_N_gram(rus) & russian) < len(get_N_gram(eng) & english):
            adder = eng
        else:
            adder = rus
        layout += ' ' + adder
    switch = layout != query
    if not switch:
        joins = split_join.join(tokens)
        if joins[1]:
            joined_candidate = fix_tokens(joins[0])
            if joined_candidate.error_weight < candidate.error_weight:
                return joined_candidate.word
        else:
            splits = split_join.split(tokens)
            if splits[1] == False:
                return candidate.word
            split_candidate = fix_tokens(splits[0])
            return split_candidate.word

    return layout



def fix_tokens(tokens):
    result = ''
    language_weight = 0
    error_weight = 0
    for t in tokens:
        if not re.match('[' + punctuation + ' ' + ']*$', t):
            global tree
            candidates = tree.generate(
                t, max_number_of_candidates=20, max_sum_of_weights=2, part=0.7)
            if len(candidates) != 0:
                candidates.sort(key=operator.attrgetter('language_weight'))
                candidates.sort(key=operator.attrgetter('error_weight'))
                fixed = sorted(candidates[:max(1, len(candidates) // 8)],
                               key=operator.attrgetter('language_weight'))[-1]
            else:
                fixed = Candidate(word=t, language_weight=0, error_weight=0)
            t = fixed.word
            language_weight += fixed.language_weight
            error_weight += fixed.error_weight
        result += t

    return Candidate(word=result, language_weight=language_weight, error_weight=error_weight)

if __name__ == '__main__':
    punctuation = re.escape(punctuation)

    language_model = LanguageModel()
    language_model.load_json('model_language.json')

    split_join = SplitJoin(language_model)

    error_model = ErrorModel()
    error_model.load_json('model_errs.json')

    tree = BorTree(error_model, language_model)
    tree.fit()

    while 1:
        try:
            query = input()
        except EOFError:
            break
        max_counter = 3
        for iterations_counter in range(max_counter):
            new_query = fix_query(query)
            if new_query == query:
                break
            query = new_query
        print(new_query.strip())
