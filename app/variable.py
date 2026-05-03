from typing import Dict

store: Dict[str, str] = {}


def set(name: str, value: str):
    store[name] = value


def get(name: str):
    return store.get(name)
