"""Define utility functions for use with Oracle."""

import datetime
import getpass
import cx_Exceptions
import cx_Logging
import cx_OptionParser
import cx_Oracle
import cx_OracleEx
import os
import string
import sys

class CompilationErrors(cx_Exceptions.BaseException):
    message = "%(type)s %(name)s %(fragment)s compilation errors."


def CheckForErrors(cursor, objectOwner, objectName, objectType, errorFragment,
        baseLineNo = 0, logPrefix = ""):
    """Check the object for errors, and if any exist, print them."""
    cursor.execute(None,
            owner = objectOwner,
            name = objectName,
            type = objectType)
    errors = cursor.fetchall()
    if errors:
        cx_Logging.Error("%s***** ERROR *****", logPrefix)
        for line, position, text in errors:
            cx_Logging.Error("%s%s/%s\t%s", logPrefix, int(line + baseLineNo),
                    int(position), text)
        raise CompilationErrors(type = objectType.capitalize(),
                name = objectName.upper(), fragment = errorFragment)

def Connect(connectString, rolesToEnable = None):
    """Connect to the database prompting for the password if necessary."""
    pos = connectString.find(" as sysdba")
    if pos < 0:
        pos = connectString.find(" as sysoper")
        if pos < 0:
            mode = 0
        else:
            mode = cx_Oracle.SYSOPER
            connectString = connectString[:pos]
    else:
        mode = cx_Oracle.SYSDBA
        connectString = connectString[:pos]
    connectString = GetConnectString(connectString)
    connection = cx_OracleEx.Connection(connectString, mode = mode)
    if rolesToEnable is not None:
        cursor = connection.cursor()
        cursor.callproc("dbms_session.set_role", (rolesToEnable,))
    connection.trimMessage = False
    return connection


def GetConnectString(connectString):
    """Return the connect string, modified to include a password, which is
       prompted for, if necessary."""
    if "/" not in connectString:
        prompt = "Password for %s: " % connectString
        sys.stderr.write(prompt)
        password = getpass.getpass("")
        pos = connectString.find("@")
        if pos < 0:
            pos = len(connectString)
        connectString = connectString[:pos] + "/" + password + \
                connectString[pos:]
    return connectString


def QuotedString(value):
    """Return the value quoted as needed."""
    return "'%s'" % value.replace("'", "''")


def GetConstantRepr(value, binaryData = False):
    """Return the value represented as an Oracle constant."""
    if value is None:
        return "null"
    elif isinstance(value, cx_Oracle.LOB):
        value = value.read()
    if isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, str):
        if binaryData:
            parts = []
            while value:
                part = value[:35]
                value = value[35:]
                chars = [hex(ord(c))[2:].zfill(2) for c in part]
                parts.append("'%s'" % "".join(chars))
            return " ||\n      ".join(parts)
        else:
            parts = []
            lastPos = 0
            for i, char in enumerate(value):
                if not char.isalnum() and char != " " \
                        and char not in string.punctuation:
                    temp = value[lastPos:i]
                    lastPos = i + 1
                    if temp:
                        parts.append(QuotedString(temp))
                    parts.append("chr(%s)" % ord(char))
            temp = value[lastPos:]
            if temp:
                parts.append(QuotedString(temp))
            return " || ".join(parts)
    elif isinstance(value, datetime.datetime):
        return "to_date('%s', 'YYYY-MM-DD HH24:MI:SS')" % \
                value.strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(value, datetime.date):
        return "to_date('%s', 'YYYY-MM-DD')" % value.strftime("%Y-%m-%d")
    raise "Cannot convert %r to an Oracle constant representation." % value


def GetObjectInfo(connection, objectName, useDbaViews = False):
    """Return information about the object. The object is first searched in a
       case sensitive fashion and if that fails upshifts the name and tries
       again."""
    if "." in objectName:
        owner, name = objectName.split(".")
        owner = owner.upper()
    else:
        owner = connection.username.upper()
        name = objectName
    if useDbaViews:
        prefix = "dba"
    else:
        prefix = "all"
    cursor = connection.cursor()
    cursor.execute("""
            select object_type
            from %s_objects
            where owner = :owner
              and object_name = :name
              and subobject_name is null
              and instr(object_type, 'BODY') = 0""" % prefix,
            owner = owner,
            name = name)
    row = cursor.fetchone()
    if row is not None:
        return owner, name, row[0]
    elif not name.isupper():
        return GetObjectInfo(connection, objectName.upper(), useDbaViews)


def IdentifierRepr(identifier):
    """Return the representation of an identifier. In Oracle this means that
       if the identifier is all uppercase, it can be returned as is; otherwise,
       double quotes must be placed around it."""
    if identifier.isupper():
        return identifier
    return '"%s"' % identifier


def PrepareErrorsCursor(connection, viewPrefix = "all"):
    """Prepare a cursor for retrieving errors from the database."""
    cursor = connection.cursor()
    cursor.prepare("""
            select
              line,
              position,
              text
            from %s_errors
            where owner = :owner
              and name = :name
              and type = :type
            order by sequence""" % viewPrefix)
    cursor.setinputsizes(owner = connection.STRING,
            name = connection.STRING, type = connection.STRING)
    return cursor


def RecompileInvalidObjects(connection, includeSchemas, excludeSchemas = [],
        raiseError = True, logPrefix = "", connectAsOwner = False):
    """Recompile all invalid objects in the schemas requested."""

    # determine whether or not to use dba views or not
    if len(includeSchemas) == 1 and not excludeSchemas \
            and connection.username.upper() == includeSchemas[0]:
        singleSchema = True
        viewPrefix = "all"
    else:
        singleSchema = False
        viewPrefix = "dba"

    # prepare a cursor to determine if object is still invalid
    invalidCursor = connection.cursor()
    invalidCursor.prepare("""
            select count(*)
            from %s_objects
            where owner = :owner
              and object_name = :name
              and object_type = :type
              and status = 'INVALID'""" % viewPrefix)
    invalidCursor.setinputsizes(owner = connection.STRING,
            name = connection.STRING, type = connection.STRING)

    # prepare a cursor to determine the errors for stored source
    errorsCursor = PrepareErrorsCursor(connection, viewPrefix)

    # fetch all of the invalid objects
    numErrors = 0
    numCompiled = 0
    compileCursor = connection.cursor()
    cursor = connection.cursor()
    cursor.arraysize = 25
    cursor.execute("""
            select
              owner,
              object_name,
              object_type
            from %s_objects
            where status = 'INVALID'
              and object_type != 'UNDEFINED'
            order by owner""" % viewPrefix)
    for owner, name, type in cursor.fetchall():

        # ignore if this schema should be ignored
        if includeSchemas and owner not in includeSchemas:
            continue
        if excludeSchemas and owner in excludeSchemas:
            continue

        # ignore if prior compiles have made this object valid
        invalidCursor.execute(None,
                owner = owner,
                name = name,
                type = type)
        invalid, = invalidCursor.fetchone()
        if not invalid:
            continue

        # perform compile
        numCompiled += 1
        if singleSchema:
            compileName = name
        else:
            compileName = "%s.%s" % (owner, name)
        cx_Logging.Trace("%sCompiling %s (%s)...", logPrefix, compileName,
                type)
        parts = type.lower().split()
        statement = "alter " + parts[0] + " " + compileName + " compile"
        if len(parts) > 1:
            statement += " " + parts[1]
        if connectAsOwner and connection.username.upper() != owner:
            connection = cx_OracleEx.Connection(owner, connection.password,
                    connection.dsn)
            compileCursor = connection.cursor()
        compileCursor.execute(statement)
        try:
            CheckForErrors(errorsCursor, owner, name, type, "has",
                    logPrefix = logPrefix)
        except:
            if raiseError:
                raise
            numErrors += 1

    # all done
    if numErrors:
        cx_Logging.Trace("%sAll objects compiled: %s error(s).", logPrefix,
                numErrors)
    elif numCompiled:
        cx_Logging.Trace("%sAll objects compiled successfully.", logPrefix)
    else:
        cx_Logging.Trace("%sNo invalid objects to compile.", logPrefix)


def SchemaOption(name = "schema"):
    """Option for specifying the schema to connect to."""
    return cx_OptionParser.Option("--%s" % name, required = 1,
            default = os.environ.get("ORA_USERID"), metavar = "SCHEMA",
            help = "use this connect string to connect to the database")


def WhereClause(columnName, compareValue, nullable, equals):
    """Return a where clause."""
    if equals and nullable:
        clause = "(%(columnName)s = %(compareValue)s or " + \
                 "%(columnName)s is null and %(compareValue)s is null)"
    elif equals:
        clause = "%(columnName)s = %(compareValue)s"
    elif nullable:
        clause = "(%(columnName)s != %(compareValue)s or " + \
                 "%(columnName)s is null and " + \
                 "%(compareValue)s is not null or " + \
                 "%(columnName)s is not null and %(compareValue)s is null)"
    else:
        clause = "%(columnName)s != %(compareValue)s"
    args = dict(columnName = IdentifierRepr(columnName),
            compareValue = compareValue)
    return clause % args

