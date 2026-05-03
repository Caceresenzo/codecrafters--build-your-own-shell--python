from abc import ABC
from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from io import StringIO
from typing import Dict, List

from . import variable

END = "\0"
SPACE = " "
SINGLE = "'"
DOUBLE = '"'
BACKSLASH = "\\"
GREATER_THAN = ">"
PIPE = "|"
AMPERSAND = "&"
DOLLAR = "$"


class StandardNamedStream(Enum):
    UNKNOWN = -1
    OUTPUT = 1
    ERROR = 2

    def from_fd(x: int):
        if x == 1:
            return StandardNamedStream.OUTPUT

        if x == 2:
            return StandardNamedStream.ERROR

        return StandardNamedStream.UNKNOWN


@dataclass
class Redirect:
    stream_name: StandardNamedStream
    path: "Argument"
    append: bool


@dataclass
class Argument:
    parts: List["ArgumentPart"]

    def resolve(self, variables: Dict[str, str]):
        builder = StringIO()

        for part in self.parts:
            if isinstance(part, LiteralPart):
                builder.write(part.value)
            elif isinstance(part, VariablePart):
                builder.write(variables.get(part.name, ""))
            else:
                raise NotImplementedError()

        return builder.getvalue()

    def __str__(self):
        return self.resolve(variable.store)


class ArgumentPart(ABC):
    ...


@dataclass
class LiteralPart(ArgumentPart):
    value: str


@dataclass
class VariablePart(ArgumentPart):
    name: str


@dataclass
class Command:
    raw_arguments: List[Argument]
    redirects: List[Redirect]
    is_job: bool = False

    @cached_property
    def arguments(self):
        return [
            str(argument)
            for argument in self.raw_arguments
        ]

    @property
    def program(self):
        return self.arguments[0]


class LineParser:

    def __init__(self, line: str):
        self._line = line
        self._index = -1

        self._commands: List[Command] = []
        self._arguments: List[ArgumentPart] = []

        self._argument_parts: List[ArgumentPart] = []
        self._redirects: List[Redirect] = []
        self._is_job = False

    def parse(self):
        while (argument := self.next_argument()) is not None:
            self._arguments.append(argument)

        if self._arguments:
            self._pipe()

        return self._commands

    def _append_literal(self, character: str):
        last_part = self._argument_parts[-1] if self._argument_parts else None

        if isinstance(last_part, LiteralPart):
            last_part.value += character
        else:
            self._argument_parts.append(LiteralPart(character))
    
    def _to_argument(self):
        argument = Argument(self._argument_parts)
        self._argument_parts = []

        return argument

    def next_argument(self):
        while (character := self._next()) != END:
            if character == SPACE:
                if self._argument_parts:
                    return self._to_argument()
            elif character == SINGLE:
                self._single_quote()
            elif character == DOUBLE:
                self._double_quote()
            elif character == BACKSLASH:
                self._backslash(False)
            elif character == GREATER_THAN:
                self._redirect(StandardNamedStream.OUTPUT)
            elif character == PIPE:
                self._pipe()
            elif character == DOLLAR:
                self._variable()
            elif character == AMPERSAND:
                # TODO Reject double ampersand
                self._is_job = True
            else:
                if character.isdigit() and self._peek() == GREATER_THAN:
                    self._next()
                    self._redirect(StandardNamedStream.from_fd(int(character)))
                else:
                    self._append_literal(character)

        if self._argument_parts:
            return self._to_argument()

        return None

    def _single_quote(self):
        while (character := self._next()) != END and character != SINGLE:
            self._append_literal(character)

    def _double_quote(self):
        while (character := self._next()) != END and character != DOUBLE:
            if character == BACKSLASH:
                self._backslash(True)
            else:
                self._append_literal(character)

    def _backslash(self, in_quote: bool):
        character = self._next()
        if character == END:
            return

        if in_quote:
            mapped = self._map_backlash_character(character)

            if mapped != END:
                character = mapped
            else:
                self._append_literal(BACKSLASH)

        self._append_literal(character)

    def _map_backlash_character(self, character: str):
        if character in [DOUBLE, BACKSLASH]:
            return character

        return END

    def _redirect(self, stream_name: StandardNamedStream):
        append = self._peek() == GREATER_THAN
        if append:
            self._next()

        argument = self.next_argument()

        self._redirects.append(Redirect(
            stream_name,
            argument,
            append,
        ))

    def _pipe(self):
        if self._argument_parts:
            self._arguments.append(self._to_argument())

        self._commands.append(Command(
            self._arguments,
            self._redirects,
            self._is_job,
        ))

        self._arguments = []
        self._argument_parts = []
        self._redirects = []
        self._is_job = False

    def _variable(self):
        builder = StringIO()

        while (character := self._peek()) != END and (character.isalnum() or character == "_"):
            builder.write(self._next())

        name = builder.getvalue()
        self._argument_parts.append(VariablePart(name))

    def _next(self):
        self._index += 1

        return self._get_at(self._index)

    def _peek(self):
        return self._get_at(self._index + 1)

    def _get_at(self, index: int):
        if index >= len(self._line):
            return END

        return self._line[index]
