import dataclasses
import enum
import io
import typing

END = "\0"
SPACE = " "
SINGLE = "'"
DOUBLE = '"'
BACKSLASH = "\\"
GREATER_THAN = ">"
PIPE = "|"


class StandardNamedStream(enum.Enum):
    UNKNOWN = -1
    OUTPUT = 1
    ERROR = 2

    def from_fd(x: int):
        if x == 1:
            return StandardNamedStream.OUTPUT

        if x == 2:
            return StandardNamedStream.ERROR

        return StandardNamedStream.UNKNOWN


@dataclasses.dataclass()
class Redirect:
    stream_name: StandardNamedStream
    path: str
    append: bool


@dataclasses.dataclass()
class Command:
    arguments: typing.List[str]
    redirects: typing.List[Redirect]

    @property
    def program(self):
        return self.arguments[0]


class LineParser:

    def __init__(self, line: str):
        self._line = line
        self._index = -1

        self._commands: typing.List[Command] = []

        self._arguments: typing.List[str] = []
        self._redirects: typing.List[Redirect] = []

    def parse(self):
        while (argument := self.next_argument()) is not None:
            self._arguments.append(argument)

        if self._arguments:
            self._commands.append(Command(
                self._arguments,
                self._redirects,
            ))

        return self._commands

    def next_argument(self):
        builder = io.StringIO()

        while (character := self._next()) != END:
            if character == SPACE:
                if builder.tell():
                    return builder.getvalue()
            elif character == SINGLE:
                self._single_quote(builder)
            elif character == DOUBLE:
                self._double_quote(builder)
            elif character == BACKSLASH:
                self._backslash(builder, False)
            elif character == GREATER_THAN:
                self._redirect(StandardNamedStream.OUTPUT)
            elif character == PIPE:
                self._pipe()
            else:
                if character.isdigit() and self._peek() == GREATER_THAN:
                    self._next()
                    self._redirect(StandardNamedStream.from_fd(int(character)))
                else:
                    builder.write(character)

        if builder.tell():
            return builder.getvalue()

        return None

    def _single_quote(self, builder: io.StringIO):
        while (character := self._next()) != END and character != SINGLE:
            builder.write(character)

    def _double_quote(self, builder: io.StringIO):
        while (character := self._next()) != END and character != DOUBLE:
            if character == BACKSLASH:
                self._backslash(builder, True)
            else:
                builder.write(character)

    def _backslash(self, builder: io.StringIO, in_quote: bool):
        character = self._next()
        if character == END:
            return

        if in_quote:
            mapped = self._map_backlash_character(character)

            if mapped != END:
                character = mapped
            else:
                builder.write(BACKSLASH)

        builder.write(character)

    def _map_backlash_character(self, character: str):
        if character in [DOUBLE, BACKSLASH]:
            return character

        return END

    def _redirect(self, stream_name: StandardNamedStream):
        append = self._peek() == GREATER_THAN
        if append:
            self._next()

        path = self.next_argument()

        self._redirects.append(Redirect(
            stream_name,
            path,
            append,
        ))

    def _pipe(self):
        self._commands.append(Command(
            self._arguments,
            self._redirects,
        ))

        self._arguments = []
        self._redirects = []

    def _next(self):
        self._index += 1

        return self._get_at(self._index)

    def _peek(self):
        return self._get_at(self._index + 1)

    def _get_at(self, index: int):
        if index >= len(self._line):
            return END

        return self._line[index]
