"""Module for use in patching databases by a number of means."""

import cx_Exceptions
import cx_Logging
import cx_Oracle
import cx_OracleEx
import cx_OracleParser
import datetime
import os
import sys

class Processor(object):

    def __init__(self, connection, onErrorContinue = False):
        self.connection = connection
        self.onErrorContinue = onErrorContinue

    def _LogCommand(self, command):
        separator = "-" * 66
        message = command.GetLogMessage()
        cx_Logging.Trace("%s", separator)
        cx_Logging.Trace("%s", message)
        cx_Logging.Trace("%s", separator)
        if sys.stdout.isatty() and not sys.stderr.isatty():
            now = datetime.datetime.today()
            print(now.strftime("%Y/%m/%d %H:%M:%S"), message)
            sys.stdout.flush()

    def ProcessCommand(self, command):
        self._LogCommand(command)
        command.Process(self)

    def ProcessFile(self, fileName):
        name, extension = os.path.splitext(fileName)
        if not extension:
            extension = ".sql"
            fileName += extension
        cls = CommandBase.classByExtension.get(extension and extension.lower())
        if cls is None:
            cls = ExecuteSQLCommands
        command = cls(fileName)
        self.ProcessCommand(command)


class CommandMetaClass(type):

    def __init__(cls, name, bases, classDict):
        super(CommandMetaClass, cls).__init__(name, bases, classDict)
        if cls.extension is not None:
            cls.classByExtension[cls.extension] = cls


class CommandBase(object, metaclass = CommandMetaClass):
    classByExtension = {}
    extension = None

    def __init__(self, fileName):
        self.fileName = fileName

    def GetLogMessage(self):
        return "Executing commands in %s." % self.fileName


class ExecuteSQLCommands(CommandBase):
    extension = ".sql"

    def Process(self, processor):
        connection = processor.connection
        cursor = connection.cursor()
        cursor.execute("select user from dual")
        user, = cursor.fetchone()
        parser = cx_OracleParser.SimpleParser()
        sql = open(self.fileName).read()
        connectStatementClass = parser.parser.processor.ConnectStatement
        try:
            for statement in parser.IterParse(sql, user):
                if isinstance(statement, connectStatementClass):
                    connection = cx_OracleEx.Connection(statement.user,
                            statement.password or connection.password,
                            statement.dsn or connection.dsn)
                    cursor = connection.cursor()
                    cx_Logging.Trace("%s", statement.GetLogMessage(cursor))
                    parser.parser.processor.owner = statement.user
                else:
                    try:
                        statement.Process(cursor)
                    except cx_Exceptions.BaseException as error:
                        lineNumber = statement.lineNumber
                        if isinstance(error, cx_OracleEx.DatabaseException) \
                                and error.dbErrorOffset is not None:
                            offset = error.dbErrorOffset
                            lineNumber += statement.sql[:offset].count("\n")
                        cx_Logging.Error("Error at line %s", lineNumber)
                        if not processor.onErrorContinue:
                            raise
                        cx_Logging.Error("%s", error.message)
        except cx_OracleParser.ParsingFailed as value:
            cx_Logging.Error("Parsing failed at line %s (%s...)",
                    value.arguments["lineNumber"],
                    value.arguments["remainingString"][:100])

