"""Defines the environment for describing Oracle objects."""

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

    def ViewPrefix(self):
        """Return the view prefix for use in the queries."""
        if self.useDbaViews:
            return "dba"
        return "all"

