"""Define utility functions for use with Oracle."""

import datetime
import getpass
import cx_OptionParser
import cx_Oracle
import cx_OracleEx
import os
import string
import sys

def CheckForErrors(cursor, objectOwner, objectName, objectType, errorFragment,
        baseLineNo = 0):
    """Check the object for errors, and if any exist, print them."""
    cursor.execute(None,
            owner = objectOwner,
            name = objectName,
            type = objectType)
    errors = cursor.fetchall()
    if errors:
        print >> sys.stderr, "***** ERROR *****"
        for line, position, text in errors:
            print >> sys.stderr, str(int(line + baseLineNo)) + "/" + \
                    str(int(position)) + "\t" + text
        sys.stderr.flush()
        message = "%s %s %s compilation errors." % \
                (objectType.capitalize(), objectName.upper(), errorFragment)
        raise message

def Connect(connectString, rolesToEnable = None):
    """Connect to the database prompting for the password if necessary."""
    connection = cx_OracleEx.Connection(GetConnectString(connectString))
    if rolesToEnable is not None:
        cursor = connection.cursor()
        cursor.callproc("dbms_session.set_role", (rolesToEnable,))
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


def GetConstantRepr(value):
    """Return the value represented as an Oracle constant."""
    if value is None:
        return "null"
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, basestring):
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


def PrepareErrorsCursor(connection, viewPrefix):
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


def RecompileInvalidObjects(connection, includeSchemas, excludeSchemas,
        password, raiseError):
    """Recompile all invalid objects in the schemas requested."""

    # determine whether or not to use dba views or not
    if len(includeSchemas) == 1 and not excludeSchemas \
            and connection.username.upper() == includeSchemas[0]:
        prevOwner = includeSchemas[0]
        viewPrefix = "all"
        compileConnection = connection
        compileCursor = connection.cursor()
    else:
        prevOwner = None
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

        # switch schemas, if applicable
        if owner != prevOwner:
            prevOwner = owner
            print >> sys.stderr, "Connecting to", owner
            sys.stderr.flush()
            compileConnection = cx_OracleEx.Connection(owner, password,
                    connection.dsn)
            compileCursor = compileConnection.cursor()

        # perform compile
        numCompiled += 1
        print >> sys.stderr, "  Compiling", name.lower(), "(" + type + ")..."
        sys.stderr.flush()
        parts = type.lower().split()
        statement = "alter " + parts[0] + " " + name.lower() + " compile"
        if len(parts) > 1:
            statement += " " + parts[1]
        compileCursor.execute(statement)
        try:
            CheckForErrors(errorsCursor, owner, name, type, "has")
        except:
            if raiseError:
                raise
            numErrors += 1

    # all done
    if numErrors:
        print >> sys.stderr, "All objects compiled:", numErrors, "error(s)."
    elif numCompiled:
        print >> sys.stderr, "All objects compiled successfully."
    else:
        print >> sys.stderr, "No invalid objects to compile."
    sys.stderr.flush()


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

