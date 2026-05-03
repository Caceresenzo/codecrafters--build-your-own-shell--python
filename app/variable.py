from typing import Dict

store: Dict[str, str] = {}


def set(name: str, value: str):
    store[name] = value


def get(name: str):
    return store.get(name)

def is_valid_identifier(name: str):
    import sys
    print(f"`{name}`", file=sys.stderr)
    first = name[0]

    if not (first.isalpha() or first == "_"):
        return False

    return all(
        character.isalnum() or character == "_"
        for character in name
    )
