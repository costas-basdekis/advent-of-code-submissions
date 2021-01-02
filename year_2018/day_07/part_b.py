#!/usr/bin/env python3
import string

import utils

from year_2018.day_07 import part_a


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        1265
        """
        _, time_to_completion = ParallelResolver\
            .from_requirements_text(_input)\
            .get_parallel_resolution_order(5, 60)

        return time_to_completion


class ParallelResolver(part_a.Resolver):
    def get_parallel_resolution_order(self, worker_count, base_duration):
        """
        >>> ParallelResolver.from_tuples([
        ...     ('A', 'C'), ('F', 'C'), ('B', 'A'), ('D', 'A'), ('E', 'B'),
        ...     ('E', 'D'), ('E', 'F')]).get_parallel_resolution_order(1, 0)[0]
        [['C', 'A', 'B', 'D', 'F', 'E']]
        >>> ParallelResolver.from_tuples([
        ...     ('A', 'C'), ('F', 'C'), ('B', 'A'), ('D', 'A'), ('E', 'B'),
        ...     ('E', 'D'), ('E', 'F')]).get_parallel_resolution_order(2, 0)
        ([['C', 'A', 'B', 'D', 'E'], ['F']], 15)
        """
        requirements_map = self.get_requirements_map()
        remaining = set(requirements_map)
        workers_order = [[] for _ in range(worker_count)]
        workers_time_to_completion = [0 for _ in range(worker_count)]
        steps_assigned = set()
        steps_completed = set()
        time_passed = 0
        time_to_completion_by_step = {}
        while remaining:
            # print("~" * 20)
            free_workers = [
                worker_index
                for worker_index, worker_time_to_completion
                in enumerate(workers_time_to_completion)
                if worker_time_to_completion <= time_passed
            ]
            free_steps = sorted(
                step
                for step in remaining
                if step not in steps_assigned
                and all(
                    prerequisite in steps_completed
                    for prerequisite in requirements_map[step]
                )
            )
            # print("Time passed", time_passed)
            # print("Workers time to completion", workers_time_to_completion)
            # print("Free workers", free_workers)
            # print("Steps time to completion", time_to_completion_by_step)
            # print("Free steps", free_steps)
            if not free_workers or not free_steps:
                steps_in_progress = steps_assigned - steps_completed
                if not steps_in_progress:
                    return Exception(
                        "No free steps remaining but other steps are")
                min_next_time_to_completion = min(
                    time_to_completion_by_step[step]
                    for step in steps_in_progress
                )
                next_steps_to_completion = [
                    step
                    for step in steps_in_progress
                    if time_to_completion_by_step[step]
                    == min_next_time_to_completion
                ]
                steps_completed.update(next_steps_to_completion)
                for step in next_steps_to_completion:
                    del time_to_completion_by_step[step]
                time_passed = min_next_time_to_completion
                # print("Time advanced to", time_passed)
                continue
            next_step = free_steps[0]
            remaining.remove(next_step)
            steps_assigned.add(next_step)
            next_free_worker = free_workers[0]
            worker_order = workers_order[next_free_worker]
            time_to_completion_by_step[next_step] = \
                time_passed + self.get_step_duration(next_step, base_duration)
            worker_order.append(next_step)
            workers_time_to_completion[next_free_worker] = \
                time_passed + self.get_step_duration(next_step, base_duration)
            # print(f"Assign {next_step} to {next_free_worker}")

        return workers_order, max(workers_time_to_completion)

    def get_step_duration(self, step, base_duration):
        """
        >>> ParallelResolver([]).get_step_duration('A', 60)
        61
        >>> ParallelResolver([]).get_step_duration('B', 60)
        62
        >>> ParallelResolver([]).get_step_duration('Z', 60)
        86
        """
        return base_duration + string.ascii_uppercase.index(step) + 1


challenge = Challenge()
challenge.main()
