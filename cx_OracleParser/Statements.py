"""Module defining statements supported by parser. Note that statements here
   are treated as objects so that they can be put in order."""

import cx_Parser

__all__ = [ "CheckConstraint", "ForeignKey", "Grant", "Index", "Package",
            "PackageBody", "PrimaryKey", "PublicSynonym", "Revoke", "Role",
            "Sequence", "StandaloneSelect", "Synonym", "Table", "Trigger",
            "Type", "UniqueConstraint", "User", "View" ]


class Statement(object):
    """Base class for all statements."""

    def __init__(self, sql, directory, owner, name, type):
        self.sql = sql
        self.owner = owner
        self.name = name
        self.type = type
        key = (owner, name)
        if key not in directory:
            directory[key] = self

    def __repr__(self):
        if self.owner is not None:
            return "<%s %s.%s>" % \
                    (self.__class__.__name__, self.owner, self.name)
        return "<%s>" % self.__class__.__name__


class Constraint(Statement):
    """Base class for all constraints."""

    def __init__(self, sql, directory, owner, name, type, tableName):
        Statement.__init__(self, sql, directory, owner, name, type)
        self.tableName = tableName

    def DependsOn(self):
        return [ (self.owner, self.tableName, "TABLE") ]


class SourceObject(Statement):
    """Base class for all "source" objects."""

    def __init__(self, sql, directory, owner, name, type, references):
        Statement.__init__(self, sql, directory, owner, name, type)
        self.references = references
        self.directory = directory

    def DependsOn(self):
        """Get the dependencies for the object. If enough components are
           available, the directory is searched for an object with the
           owner and name given; if that is not found, the current owner
           and name are attempted and finally, a public synonym is
           attempted."""
        dependencies = []
        for ref in self.references:
            if len(ref) == 3:
                depObj = self.directory.get(ref[:2])
            elif len(ref) == 2:
                depObj = self.directory.get(ref)
                if depObj is None:
                    depObj = self.directory.get((self.owner, ref[0]))
            elif len(ref) == 1:
                depObj = self.directory.get((self.owner, ref[0]))
            if depObj is not None and depObj is not self:
                depTuple = (depObj.owner, depObj.name, depObj.type)
                if depTuple not in dependencies:
                    dependencies.append(depTuple)
        return dependencies


class SynonymBase(Statement):
    """Base class for synonyms."""

    def __init__(self, sql, directory, owner, type, name, refName):
        Statement.__init__(self, sql, directory, owner, name, type)
        if len(refName) == 1:
            self.refOwner = owner
            self.refObjectName, = refName
        else:
            self.refOwner, self.refObjectName = refName

    def DependsOn(self):
        return []


class CheckConstraint(Constraint):
    """Class for check constraints."""

    def __init__(self, sql, directory, owner, name, tableName):
        Constraint.__init__(self, sql, directory, owner, name,
                "CHECK CONSTRAINT", tableName)


class ForeignKey(Constraint):
    """Class for foreign keys."""

    def __init__(self, sql, directory, owner, name, tableName,
            referencedTable):
        Constraint.__init__(self, sql, directory, owner, name, "FOREIGN KEY",
                tableName)
        if len(referencedTable) == 1:
            self.refOwner = owner
            self.refTableName, = referencedTable
        else:
            self.refOwner, self.refTableName = referencedTable

    def DependsOn(self):
        return Constraint.DependsOn(self) + \
                 [ (self.refOwner, self.refTableName, "TABLE") ]


class Grant(object):
    """Class for grants."""

    def __init__(self, sql, privileges, grantees, objectOwner = None,
            objectName = None):
        self.sql = sql
        self.privileges = privileges
        self.grantees = grantees
        self.objectOwner = objectOwner
        self.objectName = objectName

    def __repr__(self):
        if self.objectOwner is None:
            return "<%s>" % self.__class__.__name__
        return "<%s on %s.%s>" % \
                (self.__class__.__name__, self.objectOwner, self.objectName)


class Index(Statement):
    """Class for indexes."""

    def __init__(self, sql, directory, owner, name, tableName):
        Statement.__init__(self, sql, directory, owner, name, "INDEX")
        self.tableName = tableName

    def DependsOn(self):
        return [ (self.owner, self.tableName, "TABLE") ]


class Package(SourceObject):
    """Class for packages."""

    def __init__(self, sql, directory, owner, name, references, identifiers):
        SourceObject.__init__(self, sql, directory, owner, name, "PACKAGE",
                references)
        self.identifiers = identifiers


class PackageBody(SourceObject):
    """Class for package bodies."""

    def __init__(self, sql, directory, owner, name, references):
        SourceObject.__init__(self, sql, directory, owner, name,
                "PACKAGE BODY", references)

    def DependsOn(self):
        return [(self.owner, self.name, "PACKAGE")] + \
                SourceObject.DependsOn(self)


class PrimaryKey(Constraint):
    """Class for primary keys."""

    def __init__(self, sql, directory, owner, name, tableName):
        Constraint.__init__(self, sql, directory, owner, name, "PRIMARY KEY",
                tableName)


class PublicSynonym(SynonymBase):
    """Class for public synonyms."""

    def __init__(self, sql, directory, name, refName):
        SynonymBase.__init__(self, sql, directory, "PUBLIC", "PUBLIC SYNONYM",
            name, refName)


class Revoke(object):
    """Class for revokes."""

    def __init__(self, sql, privileges, grantees, objectOwner = None,
            objectName = None):
        self.sql = sql
        self.privileges = privileges
        self.grantees = grantees
        self.objectOwner = objectOwner
        self.objectName = objectName

    def __repr__(self):
        if self.objectOwner is None:
            return "<%s>" % self.__class__.__name__
        return "<%s on %s.%s>" % \
                (self.__class__.__name__, self.objectOwner, self.objectName)


class Role(Statement):
    """Class for roles."""

    def __init__(self, sql, directory, name):
        Statement.__init__(self, sql, directory, "SYSTEM", name, "ROLE")

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, self.name)

    def DependsOn(self):
        return []


class Sequence(Statement):
    """Class for tables."""

    def __init__(self, sql, directory, owner, name):
        Statement.__init__(self, sql, directory, owner, name, "SEQUENCE")

    def DependsOn(self):
        return []


class StandaloneSelect(SourceObject):
    """Class for standalone select statements."""

    def __init__(self, sql, directory, references):
        SourceObject.__init__(self, sql, directory, None, None, "SELECT",
                references)


class Synonym(SynonymBase):
    """Class for synonyms."""

    def __init__(self, sql, directory, owner, name, refName):
        SynonymBase.__init__(self, sql, directory, owner, "SYNONYM", name,
            refName)


class Table(Statement):
    """Class for tables."""

    def __init__(self, sql, directory, owner, name):
        Statement.__init__(self, sql, directory, owner, name, "TABLE")

    def DependsOn(self):
        return []


class Trigger(Statement):
    """Class for triggers."""

    def __init__(self, sql, directory, owner, name):
        Statement.__init__(self, sql, directory, owner, name, "TRIGGER")

    def DependsOn(self):
        return []


class Type(SourceObject):
    """Class for types."""

    def __init__(self, sql, directory, owner, name, references):
        SourceObject.__init__(self, sql, directory, owner, name, "TYPE",
                references)

class UniqueConstraint(Constraint):
    """Class for unique constraints."""

    def __init__(self, sql, directory, owner, name, tableName):
        Constraint.__init__(self, sql, directory, owner, name,
                "UNIQUE CONSTRAINT", tableName)

class User(Statement):
    """Class for users."""

    def __init__(self, sql, directory, name):
        Statement.__init__(self, sql, directory, "SYSTEM", name, "USER")

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, self.name)

    def DependsOn(self):
        return []


class View(SourceObject):
    """Class for views."""

    def __init__(self, sql, directory, owner, name, references):
        SourceObject.__init__(self, sql, directory, owner, name, "VIEW",
                references)

