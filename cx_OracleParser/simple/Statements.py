"""Module defining statements supported by parser."""

import cx_Logging

class Statement(object):

    def __init__(self, sql):
        self.sql = sql

    def __repr__(self):
        return "<%s>" % self.__class__.__name__

    def GetLogMessage(self):
        return None

    def Process(self, cursor):
        cursor.execute(sql)
        message = self.GetLogMessage()
        if message is not None:
            cx_Logging.Trace("%s", message)


class CreateStatement(Statement):

    def __init__(self, sql, owner, name):
        self.sql = sql
        self.owner = owner
        self.name = name

    def __repr__(self):
        return "<%s %s.%s>" % (self.__class__.__name__, self.owner, self.name)

    def GetLogMessage(self):
        return "%s %s.%s created." % \
                (self.type.capitalize(), self.owner, self.name)


class CreateTableStatement(CreateStatement):
    type = "TABLE"


class CreateViewStatement(CreateStatement):
    type = "VIEW"


class GrantStatement(Statement):

    def GetLogMessage(self):
        return "Privileges granted."




class CreateConstraint(CreateStatement):

    def __init__(self, sql, owner, name, tableName):
        super(Constraint, self).__init__(sql, owner, name, self.type)
        self.tableName = tableName



class CheckConstraint(CreateConstraint):
    type = "CHECK CONSTRAINT"


class ForeignKey(CreateConstraint):
    type = "FOREIGN KEY"



class Index(Statement):
    type = "INDEX"


class Package(Statement):
    type = "PACKAGE"


class PackageBody(Statement):
    type = "PACKAGE BODY"


class PrimaryKey(CreateConstraint):
    type = "PRIMARY KEY"


class PublicSynonym(Statement):
    type = "PUBLIC SYNONYM"


class Revoke(object):

    def __init__(self, sql):
        self.sql = sql


class Role(Statement):
    type = "ROLE"


class Sequence(Statement):
    type = "SEQUENCE"


class Synonym(Statement):
    type = "SYNONYM"


class Trigger(Statement):
    type = "TRIGGER"


class Type(Statement):
    type = "TYPE"


class UniqueConstraint(CreateConstraint):
    type = "UNIQUE CONSTRAINT"


class User(Statement):
    type = "USER"


