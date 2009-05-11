"""Module defining statements supported by parser."""

import cx_Logging

class Statement(object):
    message = None

    def __init__(self, sql):
        self.sql = sql

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


class ObjectStatement(Statement):

    def __init__(self, sql, type, name, owner = None):
        self.sql = sql
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
        if self.owner is None:
            return "%s %s %s." % \
                    (self.type.capitalize(), self.name, self.action)
        return "%s %s.%s %s." % \
                (self.type.capitalize(), self.owner, self.name, self.action)


class DMLStatement(ObjectStatement):

    def __init__(self, sql, owner, name):
        self.sql = sql
        self.owner = owner
        self.name = name

    def __repr__(self):
        return "<%s %s.%s>" % (self.__class__.__name__, self.owner, self.name)

    def GetLogMessage(self, cursor):
        rowsAffected = cursor.rowcount
        modifier = "row"
        if rowsAffected != 1:
            modifier = "rows"
        return "%s %s %s in %s.%s." % \
                (self.action.capitalize(), rowsAffected, modifier, self.owner,
                 self.name)


class AlterObjectStatement(ObjectStatement):
    action = "altered"


class CommentStatement(Statement):
    message = "Comment created."


class CommitStatement(Statement):
    message = "Commit point reached."

    def Execute(self, cursor):
        cursor.connection.commit()


class ConnectStatement(Statement):

    def __init__(self, user, password = None, dsn = None):
        self.user = user
        self.password = password
        self.dsn = dsn

    def GetLogMessage(self, cursor):
        return "Connected to %s" % self.user


class CreateObjectStatement(ObjectStatement):
    action = "created"


class DropObjectStatement(ObjectStatement):
    action = "dropped"


class DeleteStatement(DMLStatement):
    action = "deleted"


class GrantStatement(Statement):
    message = "Privilege(s) granted."


class InsertStatement(DMLStatement):
    action = "inserted"


class RevokeStatement(Statement):
    message = "Privilege(s) revoked."


class RollbackStatement(Statement):
    message = "Rolled back."

    def Execute(self, cursor):
        cursor.connection.rollback()


class UpdateStatement(DMLStatement):
    action = "Updated"

