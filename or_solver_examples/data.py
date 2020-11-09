import sys
from typing import List

from key_store import KeyStore, get_keys

from or_solver_examples.models import Data, Location


def clean_tsp_line(line: str) -> List[int]:
    line = line.replace('\n', '')
    string_line = line.split(' ')
    try:
        int_line = [int(item) for item in string_line]
        return int_line
    except ValueError:
        pass


def load_data_from_tsp_file(filename: str) -> Data:

    # Load raw data
    raw_data = []
    with open(filename) as file:
        for line in file:
            clean_item = clean_tsp_line(line=line)
            if clean_item is not None:
                raw_data.append(clean_item)

    # Load into data object
    locations = KeyStore(
        keys=get_keys(Location),
        objects=[
            Location(name=name, x=x, y=y)
            for (name, x, y) in raw_data
        ],
    )

    return Data(locations=locations)


if __name__ == "__main__":
    load_data_from_tsp_file(*sys.argv[1:])
