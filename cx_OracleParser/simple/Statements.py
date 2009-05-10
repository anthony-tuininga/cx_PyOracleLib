"""Module defining statements supported by parser."""

import cx_Logging

class Statement(object):

    def __init__(self, sql):
        self.sql = sql

    def __repr__(self):
        return "<%s>" % self.__class__.__name__

    def GetLogMessage(self, cursor):
        return None

    def Process(self, cursor):
        cursor.execute(sql)
        message = self.GetLogMessage(cursor)
        if message is not None:
            cx_Logging.Trace("%s", message)


class ModifyObjectStatement(Statement):

    def __init__(self, sql, name):
        self.sql = sql
        self.name = name

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, self.name)


class ModifyObjectWithOwnerStatement(ModifyObjectStatement):

    def __init__(self, sql, owner, name):
        self.sql = sql
        self.owner = owner
        self.name = name

    def __repr__(self):
        return "<%s %s.%s>" % (self.__class__.__name__, self.owner, self.name)


class DDLStatement(ModifyObjectStatement):

    def GetLogMessage(self, cursor):
        return "%s %s %s." % \
                (self.type.capitalize(), self.name, self.action)


class DDLWithOwnerStatement(ModifyObjectWithOwnerStatement):

    def GetLogMessage(self, cursor):
        return "%s %s.%s %s." % \
                (self.type.capitalize(), self.owner, self.name, self.action)


class DMLStatement(ModifyObjectStatement):

    def GetLogMessage(self, cursor):
        rowsAffected = cursor.rowcount
        modifier = "row"
        if rowsAffected != 1:
            modifier = "rows"
        return "%s %s %s in %s.%s." % \
                (self.action, rowsAffected, modifier, self.owner, self.name)


class CommentStatement(Statement):

    def GetLogMessage(self, cursor):
        return "Comment created."


class CommitStatement(Statement):

    def __init__(self):
        pass

    def Process(self, cursor):
        cursor.connection.commit()
        cx_Logging.Trace("Commit point reached.")


class ConnectStatement(Statement):

    def __init__(self, connectString):
        self.connectString = connectString
        

class CreateCheckConstraintStatement(DDLWithOwnerStatement):
    type = "CHECK CONSTRAINT"
    action = "created"


class CreateForeignKeyStatement(DDLWithOwnerStatement):
    type = "FOREIGN KEY"
    action = "created"


class CreateIndexStatement(DDLWithOwnerStatement):
    type = "INDEX"
    action = "created"


class CreatePackageStatement(DDLWithOwnerStatement):
    type = "PACKAGE"
    action = "created"


class CreatePackageBodyStatement(DDLWithOwnerStatement):
    type = "PACKAGE BODY"
    action = "created"


class CreatePrimaryKeyStatement(DDLWithOwnerStatement):
    type = "PRIMARY KEY"
    action = "created"


class CreatePublicSynonymStatement(Statement):
    type = "PUBLIC SYNONYM"

    def __init__(self, sql, name):
        self.sql = sql
        self.name = name

    def __repr__(self):
        return "<%s %s.%s>" % (self.__class__.__name__, self.name)

    def GetLogMessage(self, cursor):
        return "%s %s created." % (self.type.capitalize(), self.name)


class CreateRoleStatement(DDLStatement):
    type = "ROLE"
    action = "created"


class CreateSequenceStatement(DDLWithOwnerStatement):
    type = "SEQUENCE"
    action = "created"


class CreateSynonymStatement(DDLWithOwnerStatement):
    type = "SYNONYM"
    action = "created"


class CreateTableStatement(DDLWithOwnerStatement):
    type = "TABLE"
    action = "created"


class CreateTriggerStatement(DDLWithOwnerStatement):
    type = "TRIGGER"
    action = "created"


class CreateTypeStatement(DDLWithOwnerStatement):
    type = "TYPE"
    action = "created"


class CreateTypeBodyStatement(DDLWithOwnerStatement):
    type = "TYPE BODY"
    action = "created"


class CreateUniqueConstraintStatement(DDLWithOwnerStatement):
    type = "UNIQUE CONSTRAINT"
    action = "created"


class CreateUserStatement(DDLStatement):
    type = "USER"
    action = "created"


class CreateViewStatement(DDLWithOwnerStatement):
    type = "VIEW"
    action = "created"


class DeleteStatement(DMLStatement):
    action = "Deleted"


class GrantStatement(Statement):

    def GetLogMessage(self, cursor):
        return "Privilege(s) granted."


class InsertStatement(DMLStatement):
    action = "Inserted"


class RevokeStatement(Statement):

    def GetLogMessage(self, cursor):
        return "Privilege(s) revoked."


class RollbackStatement(Statement):

    def __init__(self):
        pass

    def Process(self, cursor):
        cursor.connection.rollback()
        cx_Logging.Trace("Rolled back.")


class UpdateStatement(DMLStatement):
    action = "Updated"

