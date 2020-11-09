from math import sqrt

import pytest
from key_store import KeyStore, get_keys

from or_solver_examples.models import Data, Location, Trip

LOCATION_1 =  Location(x=1, y=1)
LOCATION_2 = Location(x=1, y=3)
LOCATION_3 = Location(x=3, y=1)


@pytest.mark.parametrize(
    "trip, expected_distance",
    [
        # Horizontal
        (
            Trip(start=LOCATION_1, end=Location(x=1, y=3)),
            2,
        ),
        # # Vertical
        (
            Trip(start=LOCATION_1, end=Location(x=3, y=1)),
            2,
        ),
        # Diagonal
        (
            Trip(start=LOCATION_1, end=Location(x=3, y=3)),
            sqrt(8),
        ),
    ],
)
def test_trip_distance(trip: Trip, expected_distance: float) -> None:
    assert trip.distance == expected_distance


def test_data_trips():
    data = Data(
        locations=KeyStore(
            keys=get_keys(Location),
            objects=[
                LOCATION_1,
                LOCATION_2,
                LOCATION_3,
            ],
        )
    )
    trip_pairs = [
        (LOCATION_1, LOCATION_2),
        (LOCATION_2, LOCATION_1),
        (LOCATION_1, LOCATION_3),
        (LOCATION_3, LOCATION_1),
        (LOCATION_2, LOCATION_3),
        (LOCATION_3, LOCATION_2),
    ]
    for trip in data.trips:
        trip_pair = (trip.start, trip.end)
        assert trip_pair in trip_pairs
        trip_pairs.remove(trip_pair)
    assert len(trip_pairs) == 0, f"expected no remaining trip pairs got {trip_pairs}"
