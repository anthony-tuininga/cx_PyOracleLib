"""Module defining statements supported by parser."""

import cx_Logging
import cx_OracleUtils

class Statement(object):
    message = None

    def __init__(self, sql, lineNumber):
        self.sql = sql
        self.lineNumber = lineNumber
        self.terminator = ";\n\n"

    def __repr__(self):
        return "<%s>" % self.__class__.__name__

    def Execute(self, cursor):
        cursor.execute(self.sql)

    def GetLogMessage(self, cursor):
        return self.message

    def Process(self, cursor):
        self.Execute(cursor)
        message = self.GetLogMessage(cursor)
        if message is not None:
            cx_Logging.Trace("%s", message)

    def Sql(self):
        return self.sql + self.terminator


class ObjectStatement(Statement):

    def __init__(self, sql, lineNumber, type, name, owner = None):
        super(ObjectStatement, self).__init__(sql, lineNumber)
        self.type = type
        self.name = name
        self.owner = owner

    def __repr__(self):
        if self.owner is None:
            return "<%s %s (%s)>" % \
                    (self.__class__.__name__, self.name, self.type.upper())
        return "<%s %s.%s (%s)>" % \
                (self.__class__.__name__, self.owner, self.name,
                 self.type.upper())

    def GetLogMessage(self, cursor):
        if self.owner is None or self.type in ("user", "public synonym"):
            return "%s %s %s." % \
                    (self.type.capitalize(), self.name, self.action)
        return "%s %s.%s %s." % \
                (self.type.capitalize(), self.owner, self.name, self.action)


class DMLStatement(ObjectStatement):

    def __init__(self, sql, lineNumber, owner, name):
        super(ObjectStatement, self).__init__(sql, lineNumber)
        self.owner = owner
        self.name = name

    def __repr__(self):
        return "<%s %s.%s>" % (self.__class__.__name__, self.owner, self.name)

    def GetLogMessage(self, cursor):
        rowsAffected = cursor.rowcount
        modifier = "row"
        if rowsAffected != 1:
            modifier = "rows"
        if self.owner is None and self.name is None:
            objectName = "anonymous view"
        else:
            objectName = "%s.%s" % (self.owner, self.name)
        return "%s %s %s in %s." % \
                (self.action.capitalize(), rowsAffected, modifier, objectName)


class AlterObjectStatement(ObjectStatement):
    action = "altered"


class AnonymousPlsqlBlock(Statement):
    message = "PL/SQL procedure successfully completed."


class CommentStatement(Statement):
    message = "Comment created."


class CommitStatement(Statement):
    message = "Commit point reached."

    def Execute(self, cursor):
        cursor.connection.commit()


class ConnectStatement(Statement):

    def __init__(self, sql, lineNumber, user, password = None, dsn = None):
        super(ConnectStatement, self).__init__(sql, lineNumber)
        self.user = user
        self.password = password
        self.dsn = dsn

    def GetLogMessage(self, cursor):
        return "Connected to %s" % self.user


class CreateObjectStatement(ObjectStatement):
    action = "created"

    def __init__(self, *args, **kwargs):
        super(CreateObjectStatement, self).__init__(*args, **kwargs)
        if self.type in ("package", "package body", "trigger", "type"):
            self.terminator = "\n/\n\n"

    def Execute(self, cursor):
        sql = self.sql
        lines = sql.splitlines()
        if lines[0].endswith("wrapped"):
            sql = sql + "\n"
        cursor.execute(sql)
        cursor = cx_OracleUtils.PrepareErrorsCursor(cursor.connection)
        cx_OracleUtils.CheckForErrors(cursor, self.owner, self.name,
                self.type.upper(), self.action + " with", self.lineNumber - 1)


class CreateConstraintStatement(CreateObjectStatement):

    def __init__(self, sql, lineNumber, type, owner, name, tableName):
        super(CreateConstraintStatement, self).__init__(sql, lineNumber, type,
                name, owner)
        self.tableName = tableName


class DropObjectStatement(ObjectStatement):
    action = "dropped"


class DeleteStatement(DMLStatement):
    action = "deleted"


class GrantStatement(Statement):
    message = "Privilege(s) granted."


class InsertStatement(DMLStatement):
    action = "inserted"


class RenameObjectStatement(ObjectStatement):
    action = "renamed"

    def __init__(self, sql, lineNumber, name):
        super(RenameObjectStatement, self).__init__(sql, lineNumber, "object",
                name)


class RevokeStatement(Statement):
    message = "Privilege(s) revoked."


class RollbackStatement(Statement):
    message = "Rolled back."

    def Execute(self, cursor):
        cursor.connection.rollback()


class TruncateObjectStatement(ObjectStatement):
    action = "truncated"

    def __init__(self, sql, lineNumber, owner, name):
        super(TruncateObjectStatement, self).__init__(sql, lineNumber, "table",
                name, owner)


class UpdateStatement(DMLStatement):
    action = "Updated"

