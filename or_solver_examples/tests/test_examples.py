from typing import Callable, List, Tuple

import pytest
from key_store import KeyStore, get_keys

from or_solver_examples.examples.gekko import run_gekko
from or_solver_examples.examples.pulp import run_pulp
from or_solver_examples.models import Data, Location

LOCATION_1 = Location(name="Location One", x=1, y=1)
LOCATION_2 = Location(name="Location Two", x=2, y=1)
LOCATION_3 = Location(name="Location Three", x=3, y=4)
LOCATION_4 = Location(name="Location Four", x=4, y=4)

START_LOCATION = LOCATION_1

SINGLE_ROUTE_LOCATIONS = [
    LOCATION_1,
    LOCATION_2,
    LOCATION_3,
]
SINGLE_ROUTE_ORDERED_LOCATIONS = [
    # Two options because can go around in either direction
    [
        LOCATION_1,
        LOCATION_3,
        LOCATION_2,
        LOCATION_1,
    ],
    [
        LOCATION_1,
        LOCATION_2,
        LOCATION_3,
        LOCATION_1,
    ],
]

"""
    Location objects are arranged as follows;
    
    y x ->  1   2   3   4
    1      L1  L2
    2
    3
    4              L3  L4
    
    This means that if it was possible it would be better to have two
    sub-tours containing L1 and L2 then L3 and L4, however this should
    be prevented.
"""
POSSIBLE_SUB_TOUR_LOCATIONS = [
    LOCATION_1,
    LOCATION_2,
    LOCATION_3,
    LOCATION_4
]
POSSIBLE_SUB_TOUR_ORDERED_LOCATIONS = [
    [
        LOCATION_1,
        LOCATION_2,
        LOCATION_3,
        LOCATION_4,
        LOCATION_1,
    ],
    [
        LOCATION_1,
        LOCATION_3,
        LOCATION_4,
        LOCATION_2,
        LOCATION_1,
    ],
]


@pytest.mark.parametrize(
    "solve_runner, locations, ordered_location_options",
    [
        (run_pulp, SINGLE_ROUTE_LOCATIONS, SINGLE_ROUTE_ORDERED_LOCATIONS),
        (run_pulp, POSSIBLE_SUB_TOUR_LOCATIONS, POSSIBLE_SUB_TOUR_ORDERED_LOCATIONS),
        (run_gekko, SINGLE_ROUTE_LOCATIONS, SINGLE_ROUTE_ORDERED_LOCATIONS),
        (run_gekko, POSSIBLE_SUB_TOUR_LOCATIONS, POSSIBLE_SUB_TOUR_ORDERED_LOCATIONS),
    ],
)
def test_run_solve(solve_runner: Callable, locations: List[Location], ordered_location_options: List[Location]) -> None:
    data = Data(
        locations=KeyStore(
            keys=get_keys(Location),
            objects=locations,
        ),
        start_location_name=START_LOCATION.name,
    )
    solution = solve_runner(data=data, show_plot=False)

    assert solution.feasible is True

    if solution.feasible:
        ordered_locations = solution.ordered_locations(start=START_LOCATION)
        assert ordered_locations in ordered_location_options
