import numpy as np
import pandas as pd
import random as rd
import re

from itertools import islice
from random import randint, choice


df = pd.read_csv('chars.csv')
df['character'] = df['character'].apply(lambda x: x[0].upper() + x[1:])
df['name_length'] = df['character'].apply(lambda x: len(x))


def random_chunk(li, min_chunk=3, max_chunk=9):
    it = iter(li)
    while True:
        nxt = ''.join(list(islice(it, randint(min_chunk, max_chunk))))
        if nxt:
            yield nxt
        else:
            break


def what_a_code(string) -> str:
    string_list = string.split('\n')
    # print('String List:', string_list)

    strinG_list = list()

    for strinG in string_list:
        splitted = strinG.split()

        very_new_lists = list()
        for y in splitted:
            new_lists = list(random_chunk(y))
            # print(new_lists)

            for x in range(len(new_lists)):
                choices = df.loc[df['name_length'] == len(new_lists[x])]['character'].values.tolist()
                if not choices and len(new_lists[x]) == 1:
                    choices = ['~']    
                elif not choices and len(new_lists[x]) == 2:
                    choices = ['TH']
                new_lists[x] = np.random.choice(choices)

            rd.shuffle(new_lists)
            news = ''.join(new_lists)
            very_new_lists.append(news)

        newstring = strinG
        for x, y in enumerate(splitted):
            pattern = splitted[x]
            replacement = very_new_lists[x]
            newstring = re.sub(pattern, replacement, newstring, count=1)

        strinG_list.append(newstring)

    return ''.join(strinG_list)