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

    def IterParse(self, string, owner = None):
        lineNumber = 1
        productionName = "statement"
        self.parser.processor.owner = owner
        while string:
            remainingString, results = self.parser.Parse(string,
                    productionName)
            pos = len(string) - len(remainingString)
            if results is None:
                raise ParsingFailed(pos = pos, string = string,
                        owner = self.parser.processor.owner,
                        productionName = productionName,
                        lineNumber = lineNumber,
                        remainingString = remainingString)
            statement, = results
            statement.lineNumber += lineNumber - 1
            lineNumber += len(string[:pos].splitlines())
            string = remainingString
            yield statement

