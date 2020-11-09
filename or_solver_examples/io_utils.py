from typing import Callable

from or_solver_examples.data import load_data_from_tsp_file


def run_example_from_file(run_example: Callable, *args, **kwargs) -> None:
    data = load_data_from_tsp_file(*args, **kwargs)
    run_example(data=data)
