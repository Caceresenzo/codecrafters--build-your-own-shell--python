import typing

END = "\0"
SPACE = " "
SINGLE = "'"

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
            else:
                self._builder += character
        
        if self._builder:
            strings.append(self._builder)
        
        return strings
    
    def _single_quote(self):
        while (character := self._next()) != END and character != SINGLE:
            self._builder += character

    def _next(self):
        return next(self._iterator, END)
