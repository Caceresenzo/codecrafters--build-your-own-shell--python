from typing import Dict

store: Dict[str, str] = {}


def set(name: str, value: str):
    store[name] = value


def get(name: str):
    return store.get(name)

skipped = 0

def is_valid_identifier(name: str):
    global skipped
    skipped += 1
    if skipped == 3:
        import sys
        print(f"`{name}`", file=sys.stderr)

    first = name[0]

    if not (first.isalpha() or first == "_"):
        return False

    return all(
        character.isalnum() or character == "_"
        for character in name
    )
