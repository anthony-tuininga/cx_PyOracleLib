"""Defines the environment for describing Oracle objects."""

import cx_Exceptions
import Utils

__all__ = [ "Environment" ]

class Environment(object):
    """Defines environment for describing Oracle objects."""

    def __init__(self, connection, options):
        self.connection = connection
        self.useDbaViews = False
        self.maxLongSize = None
        Utils.SetOptions(self, options)
        self.cursors = {}
        self.cachedObjects = {}

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
            cursor.arraysize = 25
            if tag:
                self.cursors[tag] = cursor
        return cursor, isPrepared

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
            owner = self.connection.username.upper()
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
        raise ObjectNotFound(owner = owner, name = name)

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

    def ViewPrefix(self):
        """Return the view prefix for use in the queries."""
        if self.useDbaViews:
            return "dba"
        return "all"


class ObjectNotFound(cx_Exceptions.BaseException):
    message = "Object %(owner)s.%(name)s not found."

