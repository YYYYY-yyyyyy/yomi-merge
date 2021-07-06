#!/usr/bin/env python

import argparse
import os
import json
from typing import Any
from tqdm.auto import tqdm
from collections import defaultdict
import zipfile


class Index:
    def __init__(self, title='', revision ='', author=''):
        self.title = title
        self.format = 3
        self.revision = revision
        self.author = author
    def serializable (self):
        return {
            'title': self.title,
            'format': self.format,
            'revision': self.revision,
            'author': self.author
        }



useful_inflections = {'v2g-k', 'v2d-k', 'v2z-k', 'v2d-s', 'v2g-s', 'v2y-k', 'v2h-k', 'v2h-s', 'v2r-k', 'v2a-s',
 'v2k-k', 'adj-i', 'adj-t', 'v2y-s', 'v2m-k', 'v4', 'v2t-s', 'v2z-s',
 'v2r-s', 'v1', 'v2b-s', 'v2m-s', 'vs', 'v2k-s', 'v2w-k', 'v5', 'vr', 'v2n-s', 'v2b-k',
 'vz', 'v2t-k', 'v2w-s', 'v2s-s', 'vk'}
class Row:
    def __init__(self, term, reading, definition_tag, inflection_rule, frequency, definition, sequence_number, tag):
        inflection_rule: str
        self.term = term
        self.reading = reading
        self.definition_tag = definition_tag
        self.inflection_rule = set([i for i in inflection_rule.split() if len(i) > 0])
        self.frequency = frequency
        self.definition: list[Any] = definition
        self.sequence_number = sequence_number
        self.tag = tag
    def serializable(self):
        return [self.term, self.reading, self.definition_tag, ' '.join(self.inflection_rule),
                self.frequency, self.definition, self.sequence_number, self.tag]

def mkey(row: Row):
    return (row.term, row.reading)

def main(input_dicts, output_dict, policy):
    policy_or = policy == 'or'
    policy_and = policy == 'and'
    print('runing with policy ', policy)
    index = Index()
    data = defaultdict(lambda: [])
    for d in tqdm(input_dicts):
        print(d)
        with zipfile.ZipFile(d, "r") as zf:
            broken = 5
            entries = 0
            for fn in zf.namelist():
                if fn == 'index.json':
                    with zf.open(fn) as fd:
                        ci = json.load(fd)
                        # print(ci)
                        index.title = f'{index.title} {policy} {ci["title"]}' if index.title != '' else ci['title']
                        index.revision = f'{index.revision} {policy} {ci["revision"]}' if index.revision != '' else ci["revision"]
                        author = f'''{ci['author'] if 'author' in ci else 'null'} ({ci['title']})'''
                        index.author = f'{index.author}; {author}' if index.revision != '' else author

                elif fn.startswith('term_bank'):
                    with zf.open(fn) as fd:
                        rows = json.load(fd)
                        for row in rows:
                            r = Row(*row)
                            key = mkey(r)
                            if (policy == 'or' and key not in data) or (policy == 'and'):
                                data[key].append(r)
                            # if r.term == '読む':
                            #     print(r.serializable())
                            if r.inflection_rule == 'v1 v5' and broken > 0:
                                broken -= 1
                                print(r.serializable())

                        entries += len(rows)

            # print('with ', entries, ' entries')
    index.title = f'({index.title})'
    index.revision = f'({index.revision})'

    fixed_data = []
    for (k, v) in data.items():
        v: list[Row]
        supper_row = v[0]
        if policy_and:
            for row in v[1:]:
                supper_row.definition.extend(row.definition)
                supper_row.inflection_rule = supper_row.inflection_rule.union(row.inflection_rule)
                for attr in ['definition_tag', 'sequence_number', 'tag']:
                    if getattr(supper_row, attr) in [None, '', 0]:
                        setattr(supper_row, attr, getattr(row, attr))
                # for attr in ['definition_tag', 'tag']:
                #     if getattr(row, attr) != getattr(supper_row, attr):
                #         print(attr, supper_row.term, supper_row.reading, getattr(supper_row, attr), getattr(row, attr))
        fixed_data.append(supper_row)
        if supper_row.term == '読む':
            print(r.serializable())
    fixed_data = sorted(fixed_data, key=lambda x: x.frequency, reverse=True)
    fixed_data = list(map(Row.serializable, fixed_data))
    with zipfile.ZipFile(output_dict, "w"
            #, compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as zf:
        with zf.open('index.json', "w") as fd:
            fd.write(json.dumps(index.serializable(), ensure_ascii=False).encode('utf8'))
        print(index.serializable())
        i = 0
        f_count = 1
        while i < len(fixed_data) - 1:
            ni = min(i + 10000, len(fixed_data))
            with zf.open(f'term_bank_{f_count}.json', 'w') as fd:
                fd.write(json.dumps(fixed_data[i: ni], ensure_ascii=False, sort_keys=True, indent=2).encode('utf8'))
            i = ni
            f_count += 1

    print('with ', len(fixed_data), ' entries')
parser = argparse.ArgumentParser(description='merge dicts')
parser.add_argument('dictionary', type=str, nargs='+',
                    help='path of dictionaries to merge')
parser.add_argument('output', help='where to save the result')
parser.add_argument('--policy', type=str, default='or')

args = parser.parse_args()
main(args.dictionary, args.output, args.policy)