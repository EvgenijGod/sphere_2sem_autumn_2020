from re import escape
from string import punctuation
import pandas as pd
from model_errs import ErrorModel
from model_language import LanguageModel
import re


def read(file_name):
    with open(file_name, 'r', encoding='utf-8') as f:
        content = f.readlines()
        final = []
        for l in content:
            final.append(l.strip('\n'))
        content = final

    return content


def flatten_dictionary(dictionary):
    values = []
    for d in dictionary.values():
        for v in d.values():
            values.append(v)
    return values


def replace(got, punctuation, second=True):
    if second:
        q_to_w_flat = []
        for f in got:
            for s in f:
                q_to_w_flat.append(s)
        return got, q_to_w_flat
    else:
        return got


def make_err_model(init_q, fixed_q, ):
    err_mod = ErrorModel()
    for j in range(len(init_q)):
        y_true, y_pred = init_q[j], fixed_q[j]
        number_of_words = min(len(y_true), len(y_pred))
        i = 0
        while i < number_of_words:
            err_mod.update_statistics(y_true[i], y_pred[i])
            i += 1

    err_mod.calculate_weights()
    err_mod.store_json('model_errs.json')


def make_lang_model(fixed_query):
    language_model = LanguageModel()

    for fixed in fixed_query:
        for word in fixed:
            language_model.update_statistics(word)

    language_model.calculate_weights()

    language_model.store_json('model_language.json')


if __name__ == '__main__':
    queries = read('queries_all.txt')
    queries_new = []
    for q in queries:
        queries_new.append(q.split('\t'))
    punctuation = escape(punctuation)

    original_queries = []
    fixed_queries = []
    for q in queries_new:
        f = s = 0
        q[f] = re.sub('[' + punctuation + ']', '', q[f]).split()
        if q.__len__() == 2:
            s = 1
            q[s] = re.sub('[' + punctuation + ']', '', q[s]).split()

        original_queries.append(q[f])
        fixed_queries.append(q[s])

    fixed_q_w = replace(fixed_queries, punctuation, False)
    orig_q_w = replace(original_queries, punctuation, False)

    make_err_model(orig_q_w,
                   fixed_q_w, )

    make_lang_model(fixed_q_w)

