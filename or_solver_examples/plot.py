import matplotlib.pyplot as plt
from key_store import KeyStore

from or_solver_examples.models import Location, Trip


def plot(start_location: Location, trips: KeyStore[Trip]) -> None:
    # Setup start
    trip = trips.get_one_or_none(start=start_location)
    x, y = [start_location.x], [start_location.y]

    while trip is not None or len(x) <= len(trips):
        # Iterate whilst there is a subsequent trip and the number
        # or trips is within the expected length of the whole journey.

        # Get the next trip that starts where the previous ended.
        trip = trips.get_one_or_none(start=trip.end)
        x.append(trip.start.x)
        y.append(trip.start.y)

        if trip.end == start_location:
            # Once you re-reach the start, add a connection back to
            # it and then break the loop.
            x.append(trip.end.x)
            y.append(trip.end.y)
            break

    # Plot result.
    plt.plot(x, y)
    plt.show()
