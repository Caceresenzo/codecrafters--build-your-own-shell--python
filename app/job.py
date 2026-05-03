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

    for index, job in enumerate(running):
        symbol = " "
        if index == most_recent_index:
            symbol = "+"
        elif index == previous_index:
            symbol = "-"

        print(f"[{job.number}]{symbol}  Running                 {job.command} &")
