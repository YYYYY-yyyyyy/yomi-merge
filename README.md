# Tool for merging yomichan dictionaries

## usage

```bash
./merge.py --policy <policy> input_dict_1 input_dict_2 ... input_dict_n output_dict
```

replace `<policy>` with either `or` or `and` the first one will only add entries from the latter dicts IF it's not present in a dict already merged while the latter will merge all definition from all dicts.


## deps

- zipfile
- tqdm