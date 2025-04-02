from idlelib.pyparse import trans
from json import JSONDecodeError

import pandas as pd
import json

from pathlib import Path

# setup
pd.options.mode.copy_on_write = True
pd.set_option('display.max_columns', None)


# end setup


def transform_json_to_flat_csv(fp: Path):
    """Transforms the given json file into a csv with the data flattened"""

    ofp, dfp = str(fp), str(fp).split('.')[0] + '.csv'

    with open(ofp) as f:
        d = json.load(f)

    df = pd.DataFrame(d['measurements'])

    def transform_location(location: dict) -> list:
        """Transforms origin from nested dict into list with x, y, z, and r values"""
        key = 'home'
        if key in location.keys():
            val = location[key]
            x, y, z, r = val['x'], val['y'], val['z'], val['r']
            return [x, y, z, r]
        else:

            return location[list(location.keys())[0]]

    df['origin_key'] = df.loc[:, 'origin'].transform(lambda x: list(x.keys())[0])
    df['origin'] = df.loc[:, 'origin'].transform(lambda x: transform_location(location=x))
    df['origin_x'] = df.loc[:, 'origin'].transform(lambda x: x[0])
    df['origin_y'] = df.loc[:, 'origin'].transform(lambda x: x[1])
    df['origin_z'] = df.loc[:, 'origin'].transform(lambda x: x[2])
    df['origin_r'] = df.loc[:, 'origin'].transform(lambda x: x[3])

    df['dest_key'] = df.loc[:, 'dest'].transform(lambda x: list(x.keys())[0])
    df['dest'] = df.loc[:, 'dest'].transform(lambda x: transform_location(location=x))
    df['dest_x'] = df.loc[:, 'dest'].transform(lambda x: x[0])
    df['dest_y'] = df.loc[:, 'dest'].transform(lambda x: x[1])
    df['dest_z'] = df.loc[:, 'dest'].transform(lambda x: x[2])
    df['dest_r'] = df.loc[:, 'dest'].transform(lambda x: x[3])

    df['distance_mm'] = df.loc[:, 'distance_mm'].transform(lambda x: x if len(x) == 0 else x.split('\r')[0])

    df.to_csv(dfp, index=False)


if __name__ == '__main__':
    # get all file_paths in scanner data dir
    scanner_root = Path('./scanner_data/')
    # get all json files in all subdirectories
    # NOTE: we're assuming all the subdirectories contain data files,
    #       and all the files are json and in the same format.
    scanner_files = [f for x in scanner_root.iterdir() if x.is_dir() for f in x.iterdir() if
                     f.is_file() and str(f).endswith('.json')]

    print(scanner_files)

    for scanner_file in scanner_files:
        try:
            transform_json_to_flat_csv(scanner_file)
        except JSONDecodeError as e:
            print('error in file:', scanner_file)
            print(e)
