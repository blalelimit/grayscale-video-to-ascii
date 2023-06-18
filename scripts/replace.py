import pandas as pd
import os
import re

from itertools import islice
from random import randint, choice, shuffle


df = pd.read_csv(os.path.join(os.getcwd(), 'inputs', 'csv', '2hu.csv')) # 2hu.csv
df['character'] = df['character'].apply(lambda x: x[0].upper() + x[1:])
df['name_length'] = df['character'].apply(lambda x: len(x))

MIN_CHUNK = df['name_length'].min()
MAX_CHUNK = df['name_length'].max()

df = pd.concat((df, pd.DataFrame({'character': ['~', 'TH'], 'name_length': [1, 2]}))).reset_index(drop=True)
dict_chars = df.groupby('name_length')['character'].apply(list).to_dict()   # converts grouped name_length to dictionary
# dictionary format is {1: ['~'], 2: ['TH'], 3: ['Ran', 'Aya'], 4: ['Chen', 'Tewi', 'Hina', 'Elly']}


def random_chunk_replacements(li, min_chunk=MIN_CHUNK, max_chunk=MAX_CHUNK):
    it = iter(li)
    while True:
        nxt = ''.join(list(islice(it, randint(min_chunk, max_chunk))))
        if nxt:
            nxt = choice(dict_chars.get(len(nxt)))
            yield nxt
        else:
            break


def replace_ascii_to_words(frame) -> str:
    input_frame = frame.split('\n') # removes empty spaces (the areas with no ASCCI)
    output_frame = list()

    for frame_line in input_frame:
        input_line = frame_line.split()
        output_line = list()
        
        # for each splitted line in frame_line, replace with chunks (which have replaced items, in this case character names)
        for line in input_line:
            new_line = list(random_chunk_replacements(line))    # generates chunks (with replaced items)
            shuffle(new_line)    # shuffles line
            output_line.append(''.join(new_line))   # replacement line

        # for each splitted line in frame_line (input_line), replace with output_line[x]
        for x in range(len(input_line)):
            pattern = input_line[x]
            replacement = output_line[x]
            frame_line = re.sub(pattern, replacement, frame_line, count=1)

        output_frame.append(frame_line)

    return ''.join(output_frame)