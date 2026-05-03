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
    for job in running:
        print(f"[{job.number}]+  Running                 {job.command} &")
