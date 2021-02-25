import numpy as np
import pandas as pd

import re

from pymystem3 import Mystem
from bs4 import BeautifulSoup

def smooth(stor, urls):
    total = 0
    neg_idf = []
    for word in stor:
        inv_doc_freq = np.log(urls.shape[0] - stor[word] + 0.5)
        inv_doc_freq -= np.log(stor[word] + 0.5)

        total += inv_doc_freq
        if inv_doc_freq < 0:
            neg_idf.append(word)

        stor[word] = inv_doc_freq
    for word in neg_idf:
        stor[word] = 0.25 * total / len(stor)


if __name__ == "__main__":
    all_q = pd.read_csv('/data/queries.numerate.txt', sep='	', header=None)
    urls = pd.read_csv('/data/urls.numerate.txt', sep='	', header=None)
    samples = pd.read_csv('/data/sample.technosphere.ir1.textrelevance.submission.txt')
    docid_df = pd.read_csv('/data/ids.txt')
    docid_df.index = docid_df['DocumentId']
    docid_df = docid_df.drop(columns=['DocumentId'])
    docid_df.head()
    title_len = 0
    headers_len = 0
    body_len = 0

    stem = Mystem()
    for doc_id in range(1, urls.shape[0] + 1):
        with open('content/content/' + docid_df.iloc[doc_id - 1]['DocumentName'], errors='ignore') as read_file:
            lines = list(read_file)
        html = "".join(lines[1:])

        with open('tmp_file/{}.txt'.format(doc_id), 'w') as f:
            soup = BeautifulSoup(html)
            main_part = soup.get_text('\n', True).lower()
            main_part = re.findall(r'[A-Za-zА-Яа-я0-9]+', main_part)
            main_part = ' '.join([stem.lemmatize(word)[0] for word in main_part])
            f.write(main_part)

            soup = BeautifulSoup(html)
            title = ' '.join(e.get_text() for e in soup.find_all('title')).lower()
            title = re.findall(r'[A-Za-zА-Яа-я0-9]+', title)
            title = ' '.join([stem.lemmatize(word)[0] for word in title])
            f.write(title + '\n')

            head_part = ' '.join([e.get_text() for e in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]).lower()
            head_part = re.findall(r'[A-Za-zА-Яа-я0-9]+', head_part)
            head_part = ' '.join([stem.lemmatize(word)[0] for word in head_part])
            f.write(head_part + '\n')

    posses = {}

    for query_id in range(1, all_q.shape[0] + 1):
        rows_df = samples.loc[samples['QueryId'] == query_id]
        for row in rows_df.iterrows():
            doc_id = row[1]['DocumentId']
            posses[query_id].append(doc_id)

    for pos in range(1, len(posses)):
        posses[pos] = posses[pos] + posses[pos - 1]

    title_dict = {}
    header_dict = {}
    body_dict = {}

    for docs in range(1, urls.shape[0] + 1):
        with open('tmp_file/{}.txt'.format(docs), errors='ignore') as f:
            title = re.findall(r'[A-Za-zА-Яа-я0-9]+', f.readline().lower())
            title_len += len(title)
            processed = set()
            for word in title:
                if word not in processed:
                    title_dict[word] += 1
                    processed.add(word)

            head_part = re.findall(r'[A-Za-zА-Яа-я0-9]+', f.readline().lower())
            headers_len += len(head_part)
            for word in head_part:
                if word not in processed:
                    header_dict[word] += 1
                    processed.add(word)

            main_part = re.findall(r'[A-Za-zА-Яа-я0-9]+', f.read().lower())
            body_len += len(main_part)
            for word in main_part:
                if word not in processed:
                    body_dict[word] += 1
                    processed.add(word)

    smooth(title_dict, urls)
    smooth(body_dict, urls)
    smooth(header_dict, urls)


    def scorer(first_id, doc_id):
        title_num = {}
        header_num = {}
        body_num = {}
        with open('tmp_file/{}.txt'.format(doc_id)) as file:
            for word in re.findall(r'[A-Za-zА-Яа-я0-9]+', file.readline().lower()):
                if word in title_num:
                    title_num[word] += 1
                else:
                    title_num[word] = 1
            for word in re.findall(r'[A-Za-zА-Яа-я0-9]+', file.readline().lower()):
                if word in header_num:
                    header_num[word] += 1
                else:
                    header_num[word] = 1
            for word in re.findall(r'[A-Za-zА-Яа-я0-9]+', file.read().lower()):
                if word in body_num:
                    body_num[word] += 1
                else:
                    body_num[word] = 1

        scores = [0, 0, 0]
        k = 2
        b = 0.75
        for word in re.findall(r'[A-Za-zА-Яа-я0-9]+', ' '.join(stem.lemmatize(all_q.iloc[first_id - 1][1].lower()))):
            scores[0] += title_dict[word] * (title_num[word] * (k + 1)) / (
                    title_num[word] + k * (1 - b * (1 - len(title) / (title_len / urls.shape[0]))))
            scores[1] += header_dict[word] * (header_num[word] * (k + 1)) / (
                    header_num[word] + k * (1 - b * (1 - len(head_part) / (headers_len / urls.shape[0]))))
            scores[2] += body_dict[word] * (body_num[word] * (k + 1)) / (
                    body_num[word] + k * (1 - b * (1 - len(main_part) / (body_len / urls.shape[0]))))
        return 1.2 * scores[1] + 3 * scores[0] + 1.5 * scores[2]


    final_ids = []
    final_doc_ids = []

    for query in range(1, all_q.shape[0] + 1):
        query_scores = {}
        for doc_id in posses[query]:
            query_scores[doc_id] = scorer(query, doc_id)
        query_scores = sorted(query_scores.items(), key=lambda x: x[1], reverse=True)
        for i in query_scores:
            final_ids.append(query)
            final_doc_ids.append(i[0])

    final = pd.DataFrame({
        'QueryId': final_ids,
        'DocumentId': final_doc_ids
    })

    final.to_csv('baseline.txt', index=False)
