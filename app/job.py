import os
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class RunningJob:
    number: int
    pid: int
    command: str


running: List[RunningJob] = []


def add(pid: int, command: str):
    last_number = running[-1].number if running else 0
    next_number = last_number + 1

    running.append(RunningJob(next_number, pid, command))

    print(f"[{next_number}] {pid}")


def remove(pid: int):
    for index, job in enumerate(running):
        if job.pid == pid:
            running.pop(index)
            break


def dump():
    most_recent_index = len(running) - 1
    previous_index = most_recent_index - 1

    indices_to_remove = []

    for index, job in enumerate(running):
        symbol = " "
        if index == most_recent_index:
            symbol = "+"
        elif index == previous_index:
            symbol = "-"

        status = "Running"
        if not _check_pid(job.pid):
            status = "Done"
            indices_to_remove.append(index)

        print(f"[{job.number}]{symbol}  {status:<20} {job.command} &")

    for index in reversed(indices_to_remove):
        running.pop(index)


def _check_pid(pid):
    _, status = os.waitpid(pid, os.WNOHANG)
    return status == 0
