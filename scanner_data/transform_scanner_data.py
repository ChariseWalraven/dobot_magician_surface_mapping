import json
import pandas as pd

from pathlib import Path

# setup
pd.options.mode.copy_on_write = True
pd.set_option('display.max_columns', None)
# end setup


def transform_json_to_flat_csv(fp: Path):
    """Transforms the given json file into a csv with the data flattened instead of nested"""
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

    # flatten origin key, x, y, z, and r coordinates
    df['origin_key'] = df.loc[:, 'origin'].transform(lambda x: list(x.keys())[0])
    df['origin'] = df.loc[:, 'origin'].transform(lambda x: transform_location(location=x))
    df['origin_x'] = df.loc[:, 'origin'].transform(lambda x: x[0])
    df['origin_y'] = df.loc[:, 'origin'].transform(lambda x: x[1])
    df['origin_z'] = df.loc[:, 'origin'].transform(lambda x: x[2])
    df['origin_r'] = df.loc[:, 'origin'].transform(lambda x: x[3])

    # flatten destination key, x, y, z, and r coordinates
    df['dest_key'] = df.loc[:, 'dest'].transform(lambda x: list(x.keys())[0])
    df['dest'] = df.loc[:, 'dest'].transform(lambda x: transform_location(location=x))
    df['dest_x'] = df.loc[:, 'dest'].transform(lambda x: x[0])
    df['dest_y'] = df.loc[:, 'dest'].transform(lambda x: x[1])
    df['dest_z'] = df.loc[:, 'dest'].transform(lambda x: x[2])
    df['dest_r'] = df.loc[:, 'dest'].transform(lambda x: x[3])

    # clean up return characters in distance measurement
    df['distance_mm'] = df.loc[:, 'distance_mm'].transform(lambda x: x if len(x) == 0 else x.split('\r')[0])
    if 'duration_micros' in df.columns.tolist():
        df['duration_micros'] = df.loc[:, 'distance_mm'].transform(lambda x: x if len(x) == 0 else x.split('\r')[0])

    df.to_csv(dfp, index=False)


if __name__ == '__main__':
    # get all file_paths in scanner data dir
    scanner_data_root = Path('./scanner_data')
    # get all json files in all subdirectories in directory 'scanner_data'
    # NOTE: we're assuming all the subdirectories contain data files
    # Exclude these files:
    excluded_files = [
        'scanner_data/20_05_2025/data_20_05_2025_14_52_28.json',
        'scanner_data/20_05_2025/data_20_05_2025_14_44_09.json',
    ]

    excluded_dirs = [
        'scanner_data/07_05_2025',
        'scanner_data/23_04_2025',
        'scanner_data/06_02_2025',
        'scanner_data/12_02_2025'
    ]

    # get all subdirectories in root data directory
    scanner_data_dirs = [d for d in scanner_data_root.iterdir() if d.is_dir() if str(d) not in excluded_dirs]

    # get all json files in all subdirectories
    scanner_data_files = [f for d in scanner_data_dirs for f in d.iterdir() if
                          f.is_file() and str(f).endswith('.json') and str(f) not in excluded_files]

    print(f'Transforming {len(scanner_data_files)} files.')
    for (i, scanner_file) in enumerate(scanner_data_files):
        try:
            print(f'Transforming file ({i+1}): {scanner_file}')
            transform_json_to_flat_csv(scanner_file)
        except json.JSONDecodeError as e:
            print('error in file:', scanner_file)
            print(e)

    print('Done transforming data.')
