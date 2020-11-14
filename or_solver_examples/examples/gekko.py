import logging
import sys
from time import time
from typing import Union

from key_store import KeyStore, get_keys
from gekko import GEKKO

from or_solver_examples import THRESHOLD
from or_solver_examples.io_utils import run_example_from_file
from or_solver_examples.models import Data, Solution, Trip
from or_solver_examples.plot import plot

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def get_gekko_var_value(var: GEKKO.Var) -> Union[float, int]:
    """Given a gekko variable which sometimes returns a list and others a
    number, return value without list given either  option"""
    try:
        return var.value[0]
    except:
        return  var.value


def run_gekko(data: Data, show_plot: bool = True) -> Solution:
    cumulative_duration = 0

    # ---------------------------- Model ------------------------------------- #
    model = GEKKO()
    model.options.SOLVER = 1

    # --------------------------- Variables ---------------------------------- #
    start = time()
    trip_vars = {
        trip: model.Var(name=f"TripVar({trip.start.name}_to_{trip.end.name})", integer=True, lb=0, ub=1)
        for trip in data.trips
    }
    log.info(f"Variables: Added {len(trip_vars)} trip vars.")

    no_sub_tour_vars = {
        location: model.Var(name=f"NoSubTourVar({location})", integer=True)
        for location in data.locations
    }
    log.info(f"Variables: Added {len(no_sub_tour_vars)} no sub tour vars.")

    duration = round(time() - start, 6)
    cumulative_duration += duration
    log.info(f"Variables: Total time {duration} seconds")

    # --------------------------- Constraints -------------------------------- #
    start = time()
    for location in data.locations:
        # - Exactly one movement into each location
        model.Equation(
            sum(
                trip_vars[trip]
                for trip in data.trips.get(start=location)
                if trip.end != location
            ) == 1
        )

        # - Exactly one movement out of each location
        model.Equation(
            sum(
                trip_vars[trip]
                for trip in data.trips.get(end=location)
                if trip.start != location
            ) == 1
        )

    log.info(f"Constraints: Added {data.num_locations * 2} constraints to visit each location once.")

    objective = 0
    for trip in data.trips:
        if trip.start != data.start_location and trip.end != data.start_location:
            model.Equation(
                no_sub_tour_vars[trip.start] - (data.num_locations + 1) * trip_vars[trip]
                >=
                no_sub_tour_vars[trip.end] - data.num_locations
            )

        # Add the distance of the trip by the if it is used
        objective += trip_vars[trip] * trip.distance

    log.info(f"Constraints: Added {len(data.trips)} no sub tour constraints.")

    duration = round(time() - start, 6)
    cumulative_duration += duration
    log.info(f"Constraints: Total time {duration} seconds")

    # ----------------------------- Objective -------------------------------- #
    start = time()
    model.Obj(objective)

    duration = round(time() - start, 6)
    cumulative_duration += duration
    log.info(f"Objective: Total time {duration} seconds")

    # ------------------------------ Solve ----------------------------------- #
    start = time()
    model.solve()

    duration = round(time() - start, 6)
    cumulative_duration += duration
    log.info(f"Solve: Total time {duration} seconds")

    # --------------------------- Get Solution ------------------------------- #
    feasible = bool(model.options.SOLVESTATUS)
    status = "Optimal" if feasible else "Unsuccessful"
    objective = model.options.OBJFCNVAL
    trips = KeyStore(
        keys=get_keys(Trip),
        objects=[
            trip
            for trip, var in trip_vars.items()
            if get_gekko_var_value(var) >= THRESHOLD
        ]
    )
    solution = Solution(
        time=cumulative_duration,
        status=status,
        feasible=feasible,
        objective=objective,
        trips=trips,
    )
    solution.summary()
    if feasible and show_plot:
        plot(
            trips=trips,
            start_location=data.start_location,
        )

    return solution


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Expecting one filename and not further cli args")
        exit()
    filename = sys.argv[1]
    run_example_from_file(run_example=run_gekko, filename=filename)
