"""Defines the environment for describing Oracle objects."""

import cx_Exceptions

from . import Object
from . import Statements
from . import Utils

__all__ = [ "Environment" ]

class Environment(object):
    """Defines environment for describing Oracle objects."""
    sourceTypes = {
            "FUNCTION" : Object.StoredProcWithPrivileges,
            "PACKAGE" : Object.StoredProcWithBody,
            "PACKAGE BODY" : Object.StoredProc,
            "PROCEDURE" : Object.StoredProcWithPrivileges,
            "TYPE" : Object.StoredProcWithBody,
            "TYPE BODY" : Object.StoredProc,
            "VIEW" : Object.ViewNoRetrieve
    }
    constraintTypes = [
            "CONSTRAINT",
            "PRIMARY KEY",
            "UNIQUE CONSTRAINT",
            "FOREIGN KEY",
            "CHECK CONSTRAINT"
    ]

    def __init__(self, connection, options):
        self.connection = connection
        self.useDbaViews = False
        self.maxLongSize = None
        self.wantViewColumns = False
        self.wantQuotas = True
        self.asOfTimestamp = None
        self.asOfScn = None
        Utils.SetOptions(self, options)
        self.cursors = {}
        self.cachedObjects = {}
        self.namesForOutput = {}
        if self.asOfTimestamp is not None:
            cursor = connection.cursor()
            cursor.execute("""
                    begin
                        dbms_flashback.enable_at_time(%s);
                    end;""" % self.asOfTimestamp)
        elif self.asOfScn is not None:
            cursor = connection.cursor()
            cursor.callproc("dbms_flashback.enable_at_system_change_number",
                    (self.asOfScn,))

    def CacheObject(self, obj):
        """Cache the object for later retrieval."""
        self.cachedObjects[(obj.owner, obj.name)] = obj

    def CachedObject(self, owner, name):
        """Returns the cached object or None if not cached."""
        return self.cachedObjects.get((owner, name))

    def Cursor(self, tag = None):
        """Return a cursor which is cached for better performance."""
        isPrepared = cursor = self.cursors.get(tag)
        if cursor is None:
            cursor = self.connection.cursor()
            if tag:
                self.cursors[tag] = cursor
        return cursor, isPrepared

    def NameForOutput(self, name):
        """Return the name to be used for output."""
        nameForOutput = self.namesForOutput.get(name)
        if nameForOutput is None:
            if name.isupper() and self.connection.IsValidOracleName(name):
                nameForOutput = name.lower()
            else:
                nameForOutput = '"%s"' % name
            self.namesForOutput[name] = nameForOutput
        return nameForOutput

    def ObjectByType(self, owner, name, type):
        """Return an object of the correct type."""
        if type in self.sourceTypes:
            return self.sourceTypes[type](self, owner, name, type)
        whereClause = "where o.owner = :owner and "
        if type == "TABLE":
            whereClause += "o.table_name = :name"
            statement = Statements.TABLES
            objectFunction = Object.Table
        elif type == "INDEX":
            whereClause += "o.index_name = :name"
            statement = Statements.INDEXES
            objectFunction = Object.Index
        elif type == "TRIGGER":
            whereClause += "o.trigger_name = :name"
            statement = Statements.TRIGGERS
            objectFunction = Object.Trigger
        elif type == "SYNONYM":
            whereClause += "o.synonym_name = :name"
            statement = Statements.SYNONYMS
            objectFunction = Object.Synonym
        elif type == "SEQUENCE":
            whereClause = "where o.sequence_owner = :owner " + \
                    "and o.sequence_name = :name"
            statement = Statements.SEQUENCES
            objectFunction = Object.Sequence
        elif type == "CONTEXT":
            whereClause = "where :owner = 'SYS' and namespace = :name"
            statement = Statements.CONTEXTS
            objectFunction = Object.Context
        elif type == "LIBRARY":
            whereClause += "o.library_name = :name"
            statement = Statements.LIBRARIES
            objectFunction = Object.Library
        elif type in self.constraintTypes:
            whereClause += "o.constraint_name = :name"
            statement = Statements.CONSTRAINTS
            objectFunction = Object.Constraint
        else:
            raise DescribeNotSupported(type = type)
        for object in Object.ObjectIterator(self, "Default_%s" % type,
                statement, whereClause, objectFunction,
                owner = owner, name = name):
            return object

    def ObjectExists(self, owner, name, type):
        """Returns a boolean indicating if the object exists."""
        if type in self.constraintTypes:
            cursor, isPrepared = self.Cursor("ConstraintExists")
            if not isPrepared:
                cursor.prepare("""
                        select count(*)
                        from %s_constraints
                        where owner = :owner
                          and constraint_name = :name""" % \
                        self.ViewPrefix())
            cursor.execute(None,
                    owner = owner,
                    name = name)
        else:
            cursor, isPrepared = self.Cursor("ObjectExists")
            if not isPrepared:
                cursor.prepare("""
                        select count(*)
                        from %s_objects
                        where owner = :owner
                          and object_name = :name
                          and object_type = :objType""" % self.ViewPrefix())
            cursor.execute(None,
                    owner = owner,
                    name = name,
                    objType = type)
        count, = cursor.fetchone()
        return (count > 0)

    def ObjectInfo(self, name):
        """Return the owner, name and type of the object if found and raise
           an exception if an object cannot be found; the first attempt is
           with the case as provided; the second attempt is with the name
           uppercased; the third attempt (if not fully qualified) is to
           attempt to find a public synonym with the given name."""
        isFullyQualified = "." in name
        if isFullyQualified:
            owner, name = name.split(".")
        else:
            cursor = self.connection.cursor()
            cursor.execute("select user from dual")
            owner, = cursor.fetchone()
        type = self.ObjectType(owner, name)
        if type is not None:
            return (owner, name, type)
        owner = owner.upper()
        name = name.upper()
        type = self.ObjectType(owner, name)
        if type is not None:
            return (owner, name, type)
        if not isFullyQualified:
            cursor = self.connection.cursor()
            cursor.execute("""
                    select
                      table_owner,
                      table_name
                    from %s_synonyms
                    where owner = 'PUBLIC'
                      and synonym_name = :name""" % self.ViewPrefix(),
                    name = name)
            row = cursor.fetchone()
            if row is not None:
                owner, name = row
                type = self.ObjectType(owner, name)
                if type is not None:
                    return (owner, name, type)
        raise ObjectNotFound(owner = self.NameForOutput(owner),
                name = self.NameForOutput(name))

    def ObjectType(self, owner, name):
        """Return the type of the object or None if no such object exists."""
        cursor = self.connection.cursor()
        cursor.execute("""
                select object_type
                from %s_objects
                where owner = :owner
                  and object_name = :name
                  and subobject_name is null
                  and instr(object_type, 'BODY') = 0""" % self.ViewPrefix(),
                owner = owner,
                name = name)
        row = cursor.fetchone()
        if row is not None:
            return row[0]

    def ServerVersion(self):
        """Return a 2-tuple of the major and minor version of the server."""
        versionParts = [int(s) for s in self.connection.version.split(".")]
        return tuple(versionParts[:2])

    def ViewPrefix(self):
        """Return the view prefix for use in the queries."""
        if self.useDbaViews:
            return "dba"
        return "all"


class DescribeNotSupported(cx_Exceptions.BaseException):
    message = "Describing objects of type '%(type)s' is not supported."


class ObjectNotFound(cx_Exceptions.BaseException):
    message = "Object %(owner)s.%(name)s not found."

