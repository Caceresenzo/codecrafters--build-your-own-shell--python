import typing

END = "\0"
SPACE = " "
SINGLE = "'"
DOUBLE = '"'
BACKSLASH = "\\"


class LineParser:

    def __init__(self, line: str):
        self._iterator = iter(line)
        self._builder = ""

    def parse(self):
        strings: typing.List[str] = []

        while (character := self._next()) != END:
            if character == SPACE:
                if self._builder:
                    strings.append(self._builder)
                    self._builder = ""
            elif character == SINGLE:
                self._single_quote()
            elif character == DOUBLE:
                self._double_quote()
            elif character == BACKSLASH:
                self._backslash(False)
            else:
                self._builder += character

        if self._builder:
            strings.append(self._builder)

        return strings

    def _single_quote(self):
        while (character := self._next()) != END and character != SINGLE:
            self._builder += character

    def _double_quote(self):
        while (character := self._next()) != END and character != DOUBLE:
            if character == BACKSLASH:
                self._backslash(True)
            else:
                self._builder += character

    def _backslash(self, in_quote: bool):
        character = self._next()
        if character == END:
            return

        if in_quote:
            mapped = self._map_backlash_character(character)

            if mapped != END:
                character = mapped
            else:
                self._builder += BACKSLASH

        self._builder += character

    def _map_backlash_character(self, character: str):
        if character in [DOUBLE, BACKSLASH]:
            return character

        return END

    def _next(self):
        return next(self._iterator, END)
