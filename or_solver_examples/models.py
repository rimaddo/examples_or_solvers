import logging
from dataclasses import dataclass
from math import sqrt
from typing import List, Optional

from key_store import KeyStore, get_keys

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


@dataclass(frozen=True)
class Location:
    x: int
    y: int
    name: Optional[str] = None


@dataclass(frozen=True)
class Trip:
    start: Location
    end: Location

    @property
    def distance(self) -> float:
        return 0 if self.start == self.end else sqrt(
            pow(self.start.x - self.end.x,  2)
            + pow(self.start.y - self.end.y, 2)
        )


@dataclass(frozen=True)
class Data:
    locations: KeyStore[Location]
    start_location_name: Optional[str] = None

    @property
    def trips(self) -> KeyStore[Trip]:
        return KeyStore(
            keys=get_keys(Trip),
            objects=[
                Trip(start=start, end=end)
                for start in self.locations
                for end in self.locations
                if start != end
            ]
        )

    @property
    def num_locations(self) -> int:
        return len(self.locations)

    @property
    def start_location(self) -> Location:
        return (
            self.locations[0]
            if self.start_location_name is None
            else self.locations.get_one(name=self.start_location_name)
        )


@dataclass(frozen=True)
class Solution:
    time: float
    status: str
    feasible: bool
    objective: Optional[int]
    trips: Optional[KeyStore[Trip]]

    def summary(self) -> None:
        log.info(f"Solve returned status {self.status} in {self.time} seconds")
        if self.feasible:
            log.info(f"Objective {self.objective} for {len(self.trips)} trips")

    def ordered_locations(self, start: Location) -> List[Location]:
        next_location = start
        ordered_locations = [next_location]

        while next_location is not None and len(ordered_locations) < (len(self.trips) + 2):
            next_location = next(
                trip.end
                for trip in self.trips.get(start=next_location)
            )
            ordered_locations.append(next_location)
            if next_location == start:
                break

        return ordered_locations
