"""Submodule for handling the parsing of files containing Oracle objects."""

import cx_Exceptions
import cx_OracleParser.simple
import cx_OracleParser.full
import cx_Parser

__all__ = [ "Parser", "SimpleParser", "ParsingFailed" ]


class ParsingFailed(cx_Exceptions.BaseException):
    message = "Parsing failed at character %(pos)s"


class Parser(object):

    def __init__(self):
        self.parser = cx_Parser.Parser(cx_OracleParser.full.GRAMMAR,
                cx_OracleParser.full.Processor())

    def Parse(self, string, owner = None, productionName = "file"):
        self.parser.processor.owner = owner
        remainingString, results = self.parser.Parse(string, productionName)
        if results is None or remainingString:
            pos = len(string) - len(remainingString)
            raise ParsingFailed(pos = pos, string = string, owner = owner,
                    productionName = productionName,
                    remainingString = remainingString)
        return results


class SimpleParser(Parser):

    def __init__(self):
        self.parser = cx_Parser.Parser(cx_OracleParser.simple.GRAMMAR,
                cx_OracleParser.simple.Processor())

