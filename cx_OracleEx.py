"""Define extensions to the cx_Oracle module."""

import cx_Exceptions
import cx_Logging
import cx_Oracle
import sys

class Connection(cx_Oracle.Connection):
    BFILE = cx_Oracle.BFILE
    BINARY = cx_Oracle.BINARY
    BLOB = cx_Oracle.BLOB
    CLOB = cx_Oracle.CLOB
    NCLOB = cx_Oracle.NCLOB
    DATETIME = cx_Oracle.DATETIME
    FIXED_CHAR = cx_Oracle.FIXED_CHAR
    LONG_BINARY = cx_Oracle.LONG_BINARY
    LONG_STRING = cx_Oracle.LONG_STRING
    NUMBER = cx_Oracle.NUMBER
    ROWID = cx_Oracle.ROWID
    STRING = cx_Oracle.STRING
    TIMESTAMP = cx_Oracle.TIMESTAMP
    Date = cx_Oracle.Date
    Timestamp = cx_Oracle.Timestamp
    trimMessage = logSql = True

    def cursor(self):
        cursor = Cursor(self)
        cursor.arraysize = 50
        return cursor

    def DeleteRow(self, tableName, **args):
        """Delete a row from a table."""
        whereClauses = ["%s = :%s" % (n, n) for n in args]
        statement = "delete from %s where %s" % \
                (tableName, " and ".join(whereClauses))
        cursor = self.cursor()
        cursor.execute(statement, **args)

    def ExceptionHandler(self, excType, excValue, excTraceback):
        if excType is None or excValue is None \
                or not isinstance(excValue, cx_Oracle.DatabaseError):
            exc = cx_Exceptions.GetExceptionInfo(excType, excValue,
                    excTraceback)
        else:
            exc = DatabaseException(excType, excValue, excTraceback,
                    self.trimMessage)
        exc.arguments["connection"] = repr(self)
        return exc

    def GetCurrentDate(self):
        """Return the current date according to the database."""
        cursor = self.cursor()
        cursor.execute("select sysdate from dual")
        value, = cursor.fetchone()
        return value

    def InsertRow(self, tableName, **args):
        """Insert a row into the table."""
        names = list(args.keys())
        bindNames = [":%s" % n for n in names]
        statement = "insert into %s (%s) values (%s)" % \
                (tableName, ",".join(names), ",".join(bindNames))
        cursor = self.cursor()
        cursor.execute(statement, **args)

    def IsValidOracleName(self, name):
        """Return true if the name is valid for use within Oracle."""
        cursor = cx_Oracle.Cursor(self)
        try:
            cursor.execute("select 1 as %s from dual %s" % (name, name))
            return True
        except:
            return False

    def UpdateRow(self, tableName, *whereNames, **args):
        """Update a row in the table."""
        setClauses = ["%s = :%s" % (n, n) for n in args \
                if n not in whereNames]
        whereClauses = ["%s = :%s" % (n, n) for n in whereNames]
        statement = "update %s set %s where %s" % \
                (tableName, ",".join(setClauses), " and ".join(whereClauses))
        cursor = self.cursor()
        cursor.execute(statement, **args)


class Cursor(cx_Oracle.Cursor):

    def blob(self, _value):
        """Return a BLOB variable containing the given value."""
        var = self.var(self.connection.BLOB)
        var.setvalue(0, _value)
        return var

    def clob(self, _value):
        """Return a CLOB variable containing the given value."""
        var = self.var(self.connection.CLOB)
        var.setvalue(0, _value)
        return var

    def execute(self, _sql, _args = None, **_kwargs):
        """Wrap the execute so that unhandled exceptions are handled."""
        if _args is None:
            _args = _kwargs
        try:
            if self.connection.logSql \
                    and cx_Logging.Debug("SQL\n%s", _sql or self.statement):
                if isinstance(_args, dict):
                    _output = [(k, v) for k, v in _args.items() \
                            if not k.endswith("_")]
                    _output.sort()
                else:
                    _output = enumerate(_args)
                _output = ["    %s => %r" % (n, v) for n, v in _output]
                if _output:
                    cx_Logging.Debug("BIND VARIABLES\n%s", "\n".join(_output))
            return cx_Oracle.Cursor.execute(self, _sql, _args)
        except:
            exc = self.connection.ExceptionHandler(*sys.exc_info())
            exc.details.append("SQL: %s" % _sql or self.statement)
            exc.details.append("Bind Variables:")
            if isinstance(_args, dict):
                _output = [(k, v) for k, v in _args.items() \
                        if not k.endswith("_")]
                _output.sort()
            else:
                _output = enumerate(_args)
            for name, value in _output:
                exc.details.append("  %s -> %r" % (name, value))
            raise exc

    def executeandfetch(self, _sql, _args = None, **_kwargs):
        """Execute the statement and return the cursor for iterating."""
        if _args is None:
            _args = _kwargs
        self.execute(_sql, _args)
        return self

    def executeandfetchall(self, _sql, _args = None, **_kwargs):
        """Execute the statement and return all of the rows from the cursor."""
        if _args is None:
            _args = _kwargs
        self.execute(_sql, _args)
        return self.fetchall()

    def executeandfetchone(self, _sql, _args = None, **_kwargs):
        """Execute the statement and return one and only one row. If no rows
           are found, the NoDataFound exception is raised. If too many rows
           are found, the TooManyRows exception is raised."""
        if _args is None:
            _args = _kwargs
        self.execute(_sql, _args)
        rows = self.fetchall()
        if len(rows) == 0:
            raise cx_Exceptions.NoDataFound()
        elif len(rows) > 1:
            raise cx_Exceptions.TooManyRows(numRows = len(rows))
        return rows[0]

    def executemany(self, _sql, _args):
        try:
            if self.connection.logSql \
                    and cx_Logging.Debug("SQL\n%s", _sql or self.statement):
                 _output = ["    %s" % (r,) for r in _args]
                 cx_Logging.Debug("ROWS (%s):\n%s", len(_output),
                         "\n".join(_output))
            return cx_Oracle.Cursor.executemany(self, _sql, _args)
        except:
            exc = self.connection.ExceptionHandler(*sys.exc_info())
            exc.details.append("SQL: %s" % _sql or self.statement)
            if self.rowcount > -1 and self.rowcount < len(_args):
                exc.details.append("FAILED ROW: %s" % (_args[self.rowcount],))
            exc.details.append("ROWS (%s, %s before error):" % \
                    (len(_args), self.rowcount))
            for row in _args:
                exc.details.append("    %s" % (row,))
            raise exc

    def nclob(self, _value):
        """Return a NCLOB variable containing the given value."""
        var = self.var(self.connection.NCLOB)
        var.setvalue(0, _value)
        return var


class DatabaseException(cx_Exceptions.BaseException):
    dbErrorCode = None
    dbErrorOffset = None

    def __init__(self, excType, excValue, excTraceback, trimMessage = True):
        cx_Exceptions.BaseException.__init__(self)
        self._FormatException(excType, excValue, excTraceback)
        self.message = str(excValue)
        error, = excValue.args
        if not isinstance(error, str):
            self.dbErrorCode = error.code
            try:
                self.dbErrorOffset = error.offset
            except AttributeError:
                pass
        if trimMessage and self.message.startswith("ORA-"):
            pos = self.message.find("ORA-", 1)
            if pos > 0:
                self.message = self.message[11:pos].rstrip()

