registered = {}


def register(program: str, handler_path: str):
    registered[program] = handler_path


def get_handler(program: str):
    return registered.get(program)
