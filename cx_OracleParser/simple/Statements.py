"""Module defining statements supported by parser."""

class Statement(object):

    def __init__(self, sql, owner, name):
        self.sql = sql
        self.owner = owner
        self.name = name

    def __repr__(self):
        if self.owner is not None:
            return "<%s %s.%s>" % \
                    (self.__class__.__name__, self.owner, self.name)
        return "<%s>" % self.__class__.__name__


class Constraint(Statement):

    def __init__(self, sql, owner, name, tableName):
        super(Constraint, self).__init__(sql, owner, name, self.type)
        self.tableName = tableName


class CreateView(Statement):
    type = "VIEW"


class CheckConstraint(Constraint):
    type = "CHECK CONSTRAINT"


class ForeignKey(Constraint):
    type = "FOREIGN KEY"


class Grant(object):

    def __init__(self, sql):
        self.sql = sql


class Index(Statement):
    type = "INDEX"


class Package(Statement):
    type = "PACKAGE"


class PackageBody(Statement):
    type = "PACKAGE BODY"


class PrimaryKey(Constraint):
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


class Table(Statement):
    type = "TABLE"


class Trigger(Statement):
    type = "TRIGGER"


class Type(Statement):
    type = "TYPE"


class UniqueConstraint(Constraint):
    type = "UNIQUE CONSTRAINT"


class User(Statement):
    type = "USER"


