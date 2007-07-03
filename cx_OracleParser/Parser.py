"""Submodule for handling the parsing of files containing Oracle objects."""

import cx_Exceptions
import cx_Parser

import Dependency
import Grammar

__all__ = [ "Parser", "ParsingFailed" ]


class ParsingFailed(cx_Exceptions.BaseException):
    message = "Parsing failed at character %(pos)s"


class Parser:
    """Parser for parsing Oracle statements."""

    def __init__(self):
        self.__parser = cx_Parser.Parser(Grammar.GRAMMAR,
                Dependency.Processor())

    def Parse(self, string, owner = None, productionName = "file"):
        """Parse the string and return the results."""
        self.__parser.processor.owner = owner
        remainingString, results = self.__parser.Parse(string, productionName)
        if results is None or remainingString:
            pos = len(string) - len(remainingString)
            raise ParsingFailed(pos = pos, string = string, owner = owner,
                    productionName = productionName,
                    remainingString = remainingString)
        return results

