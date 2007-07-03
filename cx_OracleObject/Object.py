"""Defines classes used for describing Oracle objects."""

from __future__ import generators
import cx_OracleUtils
import sys

import Statements
import Utils

class Object(object):
    """Base class for describing Oracle objects."""

    def __init__(self, environment, owner, name, type):
        self.environment = environment
        self.owner = owner
        self.ownerForOutput = Utils.NameForOutput(owner)
        self.name = name
        self.nameForOutput = Utils.NameForOutput(name)
        self.type = type


class ObjectWithComments(Object):
    """Base class for describing Oracle objects which have comments."""

    def ExportComments(self, outFile):
        cursor, isPrepared = self.environment.Cursor("TableComments")
        if not isPrepared:
            cursor.prepare("""
                    select comments
                    from %s_tab_comments
                    where owner = :owner
                      and table_name = :name
                      and comments is not null
                    order by comments""" % \
                    self.environment.ViewPrefix())
        cursor.execute(None,
                owner = self.owner,
                name = self.name)
        for comments, in cursor:
            print >> outFile, "comment on table", self.nameForOutput, "is",
            print >> outFile, "%s;" % cx_OracleUtils.QuotedString(comments)
            print >> outFile
        cursor, isPrepared = self.environment.Cursor("ColumnComments")
        if not isPrepared:
            cursor.prepare("""
                    select
                      column_name,
                      comments
                    from %s_col_comments
                    where owner = :owner
                      and table_name = :name
                      and comments is not null
                    order by column_name, comments""" % \
                    self.environment.ViewPrefix())
        cursor.execute(None,
                owner = self.owner,
                name = self.name)
        for name, comments in cursor:
            nameForOutput = "%s.%s" % \
                    (self.nameForOutput, Utils.NameForOutput(name))
            print >> outFile, "comment on column", nameForOutput, "is",
            print >> outFile, "%s;" % cx_OracleUtils.QuotedString(comments)
            print >> outFile


class ObjectWithPrivileges(Object):
    """Base class for describing Oracle objects which have privileges."""

    def __MergedPrivilegeSets(self):
        """Return a list of merged privilege sets for export."""

        # sort privileges by privilege and grantable
        granteesByPrivilege = {}
        for grantable, grantee, privilege in self.__RetrievePrivileges():
            key = (privilege, grantable)
            grantees = granteesByPrivilege.get(key)
            if grantees is None:
                grantees = granteesByPrivilege[key] = []
            grantees.append(grantee)

        # create privilege sets
        keys = granteesByPrivilege.keys()
        keys.sort()
        privilegeSets = []
        for key in keys:
            foundSet = False
            privilege, grantable = key
            grantees = granteesByPrivilege[key]
            grantees.sort()
            for setGrantable, setPrivileges, setGrantees in privilegeSets:
                if grantable == setGrantable and grantees == setGrantees:
                    foundSet = True
                    setPrivileges.append(privilege)
                    break
            if not foundSet:
                privilegeSets.append((grantable, [privilege], grantees))

        return privilegeSets

    def __RetrievePrivileges(self):
        """Retrieve the privileges from the database."""
        cursor, isPrepared = self.environment.Cursor("Privileges")
        if not isPrepared:
            if self.environment.useDbaViews:
                tableName = "dba_tab_privs"
            else:
                tableName = "all_tab_privs_made"
            cursor.prepare("""
                    select distinct
                      grantable,
                      lower(grantee),
                      lower(privilege)
                    from %s
                    where owner = :p_Owner
                      and table_name = :p_Name""" % tableName)
        cursor.execute(None,
                p_Owner = self.owner,
                p_Name = self.name)
        return cursor.fetchall()

    def __UnmergedPrivilegeSets(self):
        """Return a list of unmerged privilege sets for export."""
        privileges = self.__RetrievePrivileges()
        privileges.sort()
        return [(grantable, [privilege], [grantee])
                for grantable, grantee, privilege in privileges]

    def ExportPrivileges(self, outFile, mergeGrants):
        """Export privileges for the object to the file as SQL statements."""

        # get array of privilege sets
        if mergeGrants:
          privilegeSets = self.__MergedPrivilegeSets()
        else:
          privilegeSets = self.__UnmergedPrivilegeSets()

        # export these to the file
        for grantable, privileges, grantees in privilegeSets:
            finalClause = ";"
            if grantable == "YES":
                finalClause = "\nwith grant option;"
            if len(privileges) == 1:
                print >> outFile, "grant", privileges[0]
            else:
                clauses = Utils.ClausesForOutput(privileges, "  ", "  ", ",")
                print >> outFile, "grant"
                print >> outFile, clauses
            print >> outFile, "on", self.nameForOutput
            if len(grantees) == 1:
                print >> outFile, "to", grantees[0] + finalClause
            else:
                clauses = Utils.ClausesForOutput(grantees, "  ", "  ", ",")
                print >> outFile, "to"
                print >> outFile, clauses + finalClause
            print >> outFile


class UserOrRole(ObjectWithPrivileges):
    """Base class for objects which have system privileges."""

    def __GetRolePrivileges(self):
        """Retrieve the role privileges from the database."""
        cursor, isPrepared = self.environment.Cursor("RolePrivileges")
        if not isPrepared:
            cursor.prepare("""
                    select
                      admin_option,
                      lower(granted_role)
                    from dba_role_privs
                    where grantee = :grantee""")
        cursor.execute(None, grantee = self.name)
        return cursor.fetchall()

    def __GetSysPrivileges(self):
        """Retrieve the system privileges from the database."""
        cursor, isPrepared = self.environment.Cursor("SysPrivileges")
        if not isPrepared:
            cursor.prepare("""
                    select
                      admin_option,
                      lower(privilege)
                    from dba_sys_privs
                    where grantee = :grantee""")
        cursor.execute(None, grantee = self.name)
        return cursor.fetchall()

    def __MergedPrivilegeSets(self, allPrivileges):
        """Merge the privileges, if possible."""
        privilegeDict = {}
        allPrivileges.sort()
        for adminOption, privilege in allPrivileges:
            privileges = privilegeDict.get(adminOption)
            if privileges is None:
                privileges = privilegeDict[adminOption] = []
            privileges.append(privilege)
        return privilegeDict.items()

    def __UnmergedPrivilegeSets(self, allPrivileges):
        """Return a list of unmerged privilege sets for export."""
        allPrivileges.sort()
        return [(adminOption, [privilege])
                for adminOption, privilege in allPrivileges]

    def ExportPrivileges(self, outFile, mergeGrants):
        """Export privileges for the object to the file as SQL statements."""
        sysPrivs = self.__GetSysPrivileges()
        rolePrivs = self.__GetRolePrivileges()
        if mergeGrants:
            privilegeSets = self.__MergedPrivilegeSets(sysPrivs) + \
                    self.__MergedPrivilegeSets(rolePrivs)
        else:
            privilegeSets = self.__UnmergedPrivilegeSets(sysPrivs) + \
                    self.__UnmergedPrivilegeSets(rolePrivs)
        for adminOption, privileges in privilegeSets:
            finalClause = ";"
            if adminOption == "YES":
                finalClause = "\nwith admin option;"
            if len(privileges) == 1:
                print >> outFile, "grant", privileges[0]
            else:
                clauses = Utils.ClausesForOutput(privileges, "  ", "  ", ",")
                print >> outFile, "grant"
                print >> outFile, clauses
            print >> outFile, "to", self.nameForOutput + finalClause
            print >> outFile


class ObjectWithStorage(Object):
    """Base class for objects which have storage."""

    def AddStorageClauses(self, clauses, wantTablespace, wantStorage):
        """Add storage clauses to the list of clauses to be exported."""
        if wantTablespace and self.tablespaceName is not None:
            clauses.append("tablespace %s" % self.tablespaceName.lower())
        if wantStorage and self.initialExtent is not None:
            clauses.append("storage (")
            clauses.append("  initial %s next %s" % \
                    (Utils.SizeForOutput(self.initialExtent),
                     Utils.SizeForOutput(self.nextExtent)))
            if self.maxExtents == 2147483645:
                clauses.append("  minextents %d maxextents unlimited" % \
                        self.minExtents)
            else:
                clauses.append("  minextents %d maxextents %d" % \
                        (self.minExtents, self.maxExtents))
            if self.percentIncrease is not None:
                clauses.append("  pctincrease %d" % self.percentIncrease)
            clauses.append(")")

    def RetrievePartitionColumns(self):
        """Retrieve partition columns for the object."""
        cursor, isPrepared = self.environment.Cursor("PartitionColumns")
        if not isPrepared:
            cursor.prepare("""
                    select column_name
                    from %s_part_key_columns
                    where owner = :owner
                      and name = :name
                    order by column_position""" % \
                    self.environment.ViewPrefix())
        cursor.execute(None,
                owner = self.owner,
                name = self.name)
        self.partitionColumns = [n for n, in cursor]


class ObjectWithTriggers(Object):
    """Base class for objects which have triggers."""

    def Triggers(self):
        """Return an interator for the triggers associated with the object."""
        return ObjectIterator(self.environment, "AssocTriggers",
                Statements.TRIGGERS,
                "where o.table_owner = :p_Owner and o.table_name = :p_Name",
                Trigger, p_Owner = self.owner, p_Name = self.name)


class Constraint(Object):
    """Class for describing constraints."""

    def __init__(self, environment, row):
        owner, name, self.constraintType, self.tableName, searchCondition, \
                refOwner, refConstraintName, deleteRule, deferred, \
                deferrable = row
        Object.__init__(self, environment, owner, name, "CONSTRAINT")
        self.deferrable = (deferrable == "DEFERRABLE")
        self.initiallyDeferred = (deferred == "DEFERRED")
        self.relatedIndex = None
        if self.constraintType == "C":
            self.condition = searchCondition.strip()
        elif self.constraintType in ("P", "U"):
            self.__RetrieveColumns()
            for index in ObjectIterator(self.environment, "Index",
                    Statements.INDEXES_ANY,
                    "where o.owner = :p_Owner and o.index_name = :p_Name",
                    Index, p_Owner = self.owner, p_Name = self.name):
                self.relatedIndex = index
            environment.CacheObject(self)
        elif self.constraintType == "R":
            self.__RetrieveColumns()
            self.deleteRule = None
            if deleteRule != "NO ACTION":
                self.deleteRule = deleteRule.lower()
            self.refConstraint = environment.CachedObject(refOwner,
                    refConstraintName)
            if not self.refConstraint:
                refConstraints = list(ObjectIterator(self.environment,
                    "Constraint", Statements.CONSTRAINTS,
                    "where o.owner = :p_Owner and o.constraint_name = :p_Name",
                    Constraint, p_Owner = refOwner, p_Name = refConstraintName))
                if not refConstraints:
                    message = "Cannot fetch information about referenced " + \
                              "constraint named\n%s.%s. Grant privileges " + \
                              "or use --use-dba-views."
                    raise message % (refOwner, refConstraintName)
                self.refConstraint, = refConstraints

    def __FinalClauses(self, wantTablespace, wantStorage):
        """Return a string containing the final clauses for the constraint."""
        clause = ""
        if self.initiallyDeferred:
            clause += " initially deferred"
        elif self.deferrable:
            clause += " deferrable"
        if self.relatedIndex:
            clauses = []
            self.relatedIndex.AddStorageClauses(clauses, wantTablespace,
                    wantStorage)
            clause += Utils.ClausesForOutput(clauses, " using index ", "  ",
                    "")
        return clause

    def __RetrieveColumns(self):
        """Retrieve the columns for the constraint."""
        cursor, isPrepared = self.environment.Cursor("ConsColumns")
        if not isPrepared:
            cursor.prepare("""
                    select column_name
                    from %s_cons_columns
                    where owner = :p_Owner
                      and constraint_name = :p_Name
                    order by position""" % self.environment.ViewPrefix())
        cursor.execute(None,
                p_Owner = self.owner,
                p_Name = self.name)
        self.columns = [Utils.NameForOutput(c) for c, in cursor.fetchall()]

    def Export(self, outFile, wantTablespace, wantStorage):
        """Export the object as a SQL statement."""
        print >> outFile, "alter table", Utils.NameForOutput(self.tableName)
        print >> outFile, "add constraint %s" % self.nameForOutput
        finalClauses = self.__FinalClauses(wantTablespace, wantStorage)
        if self.constraintType == "C":
            print >> outFile, "check (%s)%s;" % (self.condition, finalClauses)
        elif self.constraintType == "P":
            clauses = Utils.ClausesForOutput(self.columns, "  ", "  ", ",")
            print >> outFile, "primary key ("
            print >> outFile, clauses
            print >> outFile, ")%s;" % finalClauses
        elif self.constraintType == "U":
            clauses = Utils.ClausesForOutput(self.columns, "  ", "  ", ",")
            print >> outFile, "unique ("
            print >> outFile, clauses
            print >> outFile, ")%s;" % finalClauses
        elif self.constraintType == "R":
            clauses = Utils.ClausesForOutput(self.columns, "  ", "  ", ",")
            print >> outFile, "foreign key ("
            print >> outFile, clauses
            refName = Utils.NameForOutput(self.refConstraint.tableName)
            if self.refConstraint.owner != self.owner:
                refName = "%s.%s" % \
                        (self.refConstraint.ownerForOutput, refName)
            print >> outFile, ") references %s (" % refName
            clauses = Utils.ClausesForOutput(self.refConstraint.columns, "  ",
                    "  ", ",")
            print >> outFile, clauses
            if self.deleteRule:
                finalClauses = " on delete %s%s" % \
                        (self.deleteRule, finalClauses)
            print >> outFile, ")%s;" % finalClauses
        print >> outFile


class Index(ObjectWithStorage):
    """Class for describing indexes."""

    def __init__(self, environment, row):
        owner, name, self.tableName, self.tablespaceName, uniqueness, \
                self.initialExtent, self.nextExtent, self.minExtents, \
                self.maxExtents, self.percentIncrease, indexType, \
                partitioned, temporary, compressed, self.prefixLength = row
        Object.__init__(self, environment, owner, name, "INDEX")
        self.typeModifier = None
        if uniqueness == "UNIQUE":
            self.typeModifier = "UNIQUE"
        elif indexType == "BITMAP":
            self.typeModifier = "BITMAP"
        self.__RetrieveColumns()
        self.temporary = (temporary == "Y")
        self.partitioned = (partitioned == "YES")
        self.compressed = (compressed == "ENABLED")
        if self.partitioned:
            self.__RetrievePartitionInfo()

    def __AddPartitionClauses(self, clauses, wantTablespace, wantStorage):
        """Add clauses for the partitions to the list of clauses."""
        for partition in self.partitions:
            if clauses:
                clauses[-1] += ","
            partition.AddClauses(clauses, wantTablespace, wantStorage)
        columns = [n.lower() for n in self.partitionColumns]
        if self.locality == "LOCAL":
            clauses.insert(0, "local")
        else:
            clauses.insert(0, "global partition by %s (%s)" % \
                    (self.partitionType.lower(), ", ".join(columns)))
        clauses[1] = "( " + clauses[1].lstrip()
        clauses.append(")")

    def __RetrieveColumns(self):
        """Retrieve the columns for the index."""
        cursor, isPrepared = self.environment.Cursor("IndexColumns")
        if not isPrepared:
            cursor.prepare("""
                    select column_name
                    from %s_ind_columns
                    where index_owner = :p_Owner
                      and index_name = :p_Name
                    order by column_position""" % \
                    self.environment.ViewPrefix())
        cursor.execute(None,
                p_Owner = self.owner,
                p_Name = self.name)
        self.columns = [Utils.NameForOutput(c) for c, in cursor.fetchall()]

    def __RetrievePartitionInfo(self):
        """Retrieve partition info for the table."""
        cursor, isPrepared = self.environment.Cursor("IndexPartitionInfo")
        if not isPrepared:
            cursor.prepare("""
                    select
                      partitioning_type,
                      locality
                    from %s_part_indexes
                    where owner = :owner
                      and index_name = :name""" % \
                    self.environment.ViewPrefix())
        cursor.execute(None,
                owner = self.owner,
                name = self.name)
        row = cursor.fetchone()
        if row is None:
            message = "Index %s.%s is partitioned but no row found in " + \
                      "%s_part_indexes."
            raise message % \
                    (self.owner, self.name, self.environment.ViewPrefix())
        self.partitionType, self.locality = row
        if self.locality == "LOCAL":
            partitionKeywords = None
        elif self.partitionType == "RANGE":
            partitionKeywords = "values less than"
        else:
            partitionKeywords = "values"
        self.RetrievePartitionColumns()
        self.partitions = list(ObjectIterator(self.environment,
                "IndexPartitions", Statements.INDEX_PARTITIONS,
                "where o.index_owner = :owner and o.index_name = :name",
                Partition, partitionKeywords, owner = self.owner,
                name = self.name))

    def AddStorageClauses(self, clauses, wantTablespace, wantStorage):
        """Add storage clauses to the list of clauses to be exported."""
        if self.compressed:
            clauses.append("compress %d" % self.prefixLength)
        ObjectWithStorage.AddStorageClauses(self, clauses, wantTablespace,
            wantStorage)

    def Export(self, outFile, wantTablespace, wantStorage):
        """Export the object as a SQL statement."""
        print >> outFile, "create",
        if self.typeModifier:
            print >> outFile, self.typeModifier.lower(),
        print >> outFile, self.type.lower(), self.nameForOutput
        print >> outFile, "on", Utils.NameForOutput(self.tableName), "("
        print >> outFile, "  " + ",\n  ".join(self.columns)
        clauses = []
        self.AddStorageClauses(clauses, wantTablespace, wantStorage)
        if self.partitioned:
            self.__AddPartitionClauses(clauses, wantTablespace, wantStorage)
        clauses = Utils.ClausesForOutput(clauses, " ", "  ", "")
        print >> outFile, ")%s;" % clauses
        print >> outFile


class Library(Object):
    """Class for describing libraries."""

    def __init__(self, environment, row):
        owner, name, self.filespec = row
        Object.__init__(self, environment, owner, name, "LIBRARY")

    def Export(self, outFile):
        """Export the object as a SQL statement."""
        print >> outFile, "create or replace library", self.nameForOutput, "as"
        print >> outFile, "'%s';" % self.filespec.strip()
        print >> outFile, "/"
        print >> outFile


class Lob(ObjectWithStorage):
    """Class for describing LOB segments."""

    def __init__(self, environment, row):
        owner, name, self.tableName, self.segmentName, self.inRow = row
        Object.__init__(self, environment, owner, name, "LOB")
        self.__RetrieveSegment()

    def __RetrieveSegment(self):
        """Retrieve the segment information from the database."""
        cursor, isPrepared = self.environment.Cursor("LobSegments")
        if not isPrepared:
            statement = """
                    select
                      tablespace_name,
                      initial_extent,
                      next_extent,
                      min_extents,
                      max_extents,
                      pct_increase\n"""
            if self.environment.useDbaViews:
                statement += "from dba_segments\n"
            else:
                statement += "from user_segments\n"
            statement += "where segment_type = 'LOBSEGMENT' " + \
                "and segment_name = :p_SegmentName"
            if self.environment.useDbaViews:
                statement += " and owner = :p_Owner"
            cursor.prepare(statement)
        if self.environment.useDbaViews:
            cursor.execute(None,
                    p_SegmentName = self.segmentName,
                    p_Owner = self.owner)
        else:
            cursor.execute(None,
                    p_SegmentName = self.segmentName)
        row = cursor.fetchone()
        if not row:
            raise "Unable to locate LOB segment %s" % self.name
        self.tablespaceName, self.initialExtent, self.nextExtent, \
                self.minExtents, self.maxExtents, self.percentIncrease = row

    def AddClauses(self, clauses, wantTablespace, wantStorage):
        """Add clauses for exporting as a SQL statement to the list."""
        subClauses = []
        self.AddStorageClauses(subClauses, wantTablespace, wantStorage)
        if self.inRow != "YES":
            subClauses.append("disable storage in row")
        if subClauses:
            clauses.append("lob (%s)" % self.nameForOutput)
            clauses.append("  store as (")
            for clause in subClauses:
                clauses.append("    " + clause)
            clauses.append("  )")


class Partition(ObjectWithStorage):
    """Class for describing partitions."""

    def __init__(self, environment, row, partitionKeywords):
        owner, name, self.highValue, self.tablespaceName, self.initialExtent, \
                self.nextExtent, self.minExtents, self.maxExtents, \
                self.percentIncrease = row
        self.partitionKeywords = partitionKeywords
        Object.__init__(self, environment, owner, name, "PARTITION")

    def AddClauses(self, clauses, wantTablespace, wantStorage):
        """Add clauses for exporting as a SQL statement to the list."""
        subClauses = []
        self.AddStorageClauses(subClauses, wantTablespace, wantStorage)
        if self.partitionKeywords is not None:
            clauses.append("  partition %s %s (%s)" % \
                    (self.nameForOutput, self.partitionKeywords, \
                     self.highValue))
        else:
            clauses.append("  partition %s" % self.nameForOutput)
        for clause in subClauses:
            clauses.append("      " + clause)


class Role(UserOrRole):
    """Class for describing roles."""

    def __init__(self, environment, row):
        name, passwordRequired = row
        super(Role, self).__init__(environment, "SYSTEM", name, "ROLE")
        self.passwordRequired = (passwordRequired == "YES")

    def Export(self, outFile):
        """Export the object as a SQL statement."""
        if self.passwordRequired:
            clause = " identified by password;"
        else:
            clause = ";"
        print >> outFile, "create role", self.nameForOutput + clause
        print >> outFile


class Sequence(ObjectWithPrivileges):
    """Class for describing roles."""

    def __init__(self, environment, row):
        owner, name, self.minValue, self.maxValue, self.incrementBy, \
                self.cycleFlag, self.orderFlag, self.cacheSize, \
                self.lastNumber = row
        Object.__init__(self, environment, owner, name, "SEQUENCE")

    def Export(self, outFile, includeValue):
        """Export the object as a SQL statement."""
        options = []
        if includeValue and self.lastNumber != "1":
            options.append("start with %s" % self.lastNumber)
        if self.minValue != "1":
            options.append("minvalue %s" % self.minValue)
        if self.maxValue != "9" * 27:
            options.append("maxvalue %s" % self.maxValue)
        if self.incrementBy != "1":
            options.append("increment by %s" % self.incrementBy)
        if self.cycleFlag != "N":
            options.append("cycle")
        if self.cacheSize == "0":
            options.append("nocache")
        elif self.cacheSize != "20":
            options.append("cache %s" % self.cacheSize)
        if self.orderFlag != "N":
            options.append("order")
        optionsString = "".join(["\n  " + o for o in options])
        print >> outFile, "create sequence",
        print >> outFile, self.nameForOutput + optionsString + ";"
        print >> outFile


class StoredProc(Object):
    """Class for describing stored procedures, functions, packages, types."""

    def __init__(self, environment, owner, name, type):
        Object.__init__(self, environment, owner, name, type)
        self.__Retrieve()

    def __Retrieve(self):
        """Retrieve the information from the database."""
        cursor, isPrepared = self.environment.Cursor("Source")
        if not isPrepared:
            cursor.prepare("""
                    select text
                    from %s_source
                    where owner = :p_Owner
                      and name = :p_Name
                      and type = :p_Type
                    order by line""" % self.environment.ViewPrefix())
        cursor.execute(None,
                p_Owner = self.owner,
                p_Name = self.name,
                p_Type = self.type)
        self.source = "".join([t for t, in cursor.fetchall()]).strip()

    def Export(self, outFile):
        """Export the object as a SQL statement."""
        print >> outFile, "create or replace", self.source
        print >> outFile, "/"
        print >> outFile


class StoredProcWithPrivileges(StoredProc, ObjectWithPrivileges):
    """Base class for stored procedures with privileges."""
    pass


class StoredProcWithBody(StoredProcWithPrivileges):
    """Base class for stored procedures with bodies."""

    def Body(self):
        """Return the body for the package or type, if it exists."""
        type = self.type + " BODY"
        if Utils.ObjectExists(self.environment, self.owner, self.name, type):
            return Utils.ObjectByType(self.environment, self.owner, self.name,
                    type)


class Synonym(Object):
    """Class for describing synonyms."""

    def __init__(self, environment, row):
        owner, name, self.objectOwner, self.objectName, self.dbLink = row
        if owner == "PUBLIC":
            if self.objectOwner:
                owner = self.objectOwner
            Object.__init__(self, environment, owner, name, "PUBLIC SYNONYM")
        else:
            Object.__init__(self, environment, owner, name, "SYNONYM")

    def Export(self, outFile):
        """Export the object as a SQL statement."""
        name = Utils.NameForOutput(self.objectName)
        if self.objectOwner:
            name = "%s.%s" % (Utils.NameForOutput(self.objectOwner), name)
        if self.dbLink:
            name += "@%s" % self.dbLink.lower()
        print >> outFile, "create", self.type.lower(), self.nameForOutput,
        print >> outFile, "for"
        print >> outFile, name + ";"
        print >> outFile


class Table(ObjectWithStorage, ObjectWithTriggers, ObjectWithPrivileges, \
        ObjectWithComments):
    """Class for describing tables."""

    def __init__(self, environment, row):
        owner, name, self.tablespaceName, self.initialExtent, \
                self.nextExtent, self.minExtents, self.maxExtents, \
                self.percentIncrease, temporary, partitioned, duration, \
                iotType = row
        Object.__init__(self, environment, owner, name, "TABLE")
        self.temporary = (temporary == "Y")
        self.partitioned = (partitioned == "YES")
        self.indexOrganized = (iotType == "IOT")
        if self.temporary:
            if duration == "SYS$TRANSACTION":
                self.onCommitAction = "delete"
            else:
                self.onCommitAction = "preserve"
        self.__RetrieveColumns()
        if self.partitioned:
            self.__RetrievePartitionInfo()

    def __AddLobClauses(self, clauses, wantTablespace, wantStorage):
        """Add clauses for the LOBS to the list of clauses."""
        for lob in self.lobs:
            lob.AddClauses(clauses, wantTablespace, wantStorage)

    def __AddPartitionClauses(self, clauses, wantTablespace, wantStorage):
        """Add clauses for the partitions to the list of clauses."""
        for partition in self.partitions:
            if clauses:
                clauses[-1] += ","
            partition.AddClauses(clauses, wantTablespace, wantStorage)
        columns = [Utils.NameForOutput(n) for n in self.partitionColumns]
        clauses.insert(0, "partition by %s (%s)" % \
                (self.partitionType.lower(), ", ".join(columns)))
        clauses[1] = "( " + clauses[1].lstrip()
        clauses.append(")")

    def __ColumnClause(self, row):
        """Return a clause for exporting a column as a SQL statement."""
        name, dataType, nullable, precision, scale, length, defaultValue = row
        if dataType == "NUMBER" and precision is None and scale is not None:
            dataType = "integer"
        clause = Utils.NameForOutput(name).ljust(32) + dataType.lower()
        if precision:
            clause += "(%d" % int(precision)
            if scale:
                clause += ", %d" % int(scale)
            clause += ")"
        elif dataType.find("CHAR") >= 0 or dataType == "RAW":
            clause += "(%d)" % int(length)
        if defaultValue:
            clause += "\n    default %s" % defaultValue.strip()
        if nullable == "N":
            clause += " not null"
        return clause

    def __RetrieveColumns(self):
        """Retrieve the columns for the table from the database."""
        cursor, isPrepared = self.environment.Cursor("TableColumns")
        if not isPrepared:
            cursor.prepare("""
                    select
                      column_name,
                      data_type,
                      nullable,
                      data_precision,
                      data_scale,
                      nvl(char_col_decl_length, data_length),
                      data_default
                    from %s_tab_columns
                    where owner = :p_Owner
                      and table_name = :p_Name
                    order by column_id""" % self.environment.ViewPrefix())
        cursor.execute(None,
                p_Owner = self.owner,
                p_Name = self.name)
        self.columns = cursor.fetchall()
        self.lobs = []
        lobColumns = [c[0] for c in self.columns if c[1] in ("CLOB", "BLOB")]
        if lobColumns:
            self.lobs = list(ObjectIterator(self.environment, "Lobs",
                    Statements.LOBS,
                    "where o.owner = :p_Owner and o.table_name = :p_Name", Lob,
                    p_Owner = self.owner, p_Name = self.name))

    def __RetrievePartitionInfo(self):
        """Retrieve partition info for the table."""
        cursor, isPrepared = self.environment.Cursor("PartitionInfo")
        if not isPrepared:
            cursor.prepare("""
                    select partitioning_type
                    from %s_part_tables
                    where owner = :owner
                      and table_name = :name""" % \
                    self.environment.ViewPrefix())
        cursor.execute(None,
                owner = self.owner,
                name = self.name)
        row = cursor.fetchone()
        if row is None:
            message = "Table %s.%s is partitioned but no row found in " + \
                      "%s_part_tables."
            raise message % \
                    (self.owner, self.name, self.environment.ViewPrefix())
        self.partitionType, = row
        partitionKeywords = "values"
        if self.partitionType == "RANGE":
            partitionKeywords = "values less than"
        self.RetrievePartitionColumns()
        self.partitions = list(ObjectIterator(self.environment,
                "TablePartitions", Statements.TABLE_PARTITIONS,
                "where o.table_owner = :owner and o.table_name = :name",
                Partition, partitionKeywords, owner = self.owner,
                name = self.name))

    def Constraints(self, constraintType = None):
        """Return an interator for the constraints for the table."""
        cursorName = "TableConstraints"
        whereClause = "where o.owner = :p_Owner and o.table_name = :p_Name"
        if constraintType is not None:
            cursorName = "TablePrimaryKey"
            whereClause += " and o.constraint_type = '%s'" % constraintType
        elif self.indexOrganized:
            cursorName = "TableConstraintsNoPrimaryKey"
            whereClause += " and o.constraint_type != 'P'"
        return ObjectIterator(self.environment, cursorName,
                Statements.CONSTRAINTS, whereClause, Constraint,
                p_Owner = self.owner, p_Name = self.name)

    def Export(self, outFile, wantTablespace, wantStorage):
        """Export the object as a SQL statement."""
        clauses = [self.__ColumnClause(c) for c in self.columns]
        if self.indexOrganized:
            primaryKey, = self.Constraints('P')
            colClauses = Utils.ClausesForOutput(primaryKey.columns, "    ",
                    "    ", ",")
            clauses.append("constraint %s primary key (\n%s\n  )" % \
                    (primaryKey.nameForOutput, colClauses))
        clauses = Utils.ClausesForOutput(clauses, "  ", "  ", ",")
        print >> outFile, "create",
        if self.temporary:
            print >> outFile, "global temporary",
        print >> outFile, self.type.lower(), self.nameForOutput, "("
        print >> outFile, clauses
        clauses = []
        if self.temporary:
            clauses.append("on commit %s rows" % self.onCommitAction)
        if self.indexOrganized:
            clauses.append("organization index")
            primaryKey.relatedIndex.AddStorageClauses(clauses, wantTablespace,
                    wantStorage)
        else:
            self.AddStorageClauses(clauses, wantTablespace, wantStorage)
        if self.lobs:
            self.__AddLobClauses(clauses, wantTablespace, wantStorage)
        if self.partitioned:
            self.__AddPartitionClauses(clauses, wantTablespace, wantStorage)
        clauses = Utils.ClausesForOutput(clauses, " ", "  ", "")
        print >> outFile, ")%s;" % clauses
        print >> outFile

    def Indexes(self):
        """Return an iterator for the indexes for the table."""
        return ObjectIterator(self.environment, "TableIndexes",
                Statements.INDEXES,
                "where o.owner = :p_Owner and o.table_name = :p_Name",
                Index, p_Owner = self.owner, p_Name = self.name)

    def ReferencedConstraints(self):
        """Return an iterator for the referencing constraints for the table."""
        clause = """,
                  %s_constraints p
                where p.owner = :p_Owner
                  and p.table_name = :p_Name
                  and p.constraint_type in ('P', 'U')
                  and o.r_owner = p.owner
                  and o.r_constraint_name = p.constraint_name""" % \
                self.environment.ViewPrefix()
        return ObjectIterator(self.environment, "ReferencedConstraints",
                Statements.CONSTRAINTS, clause, Constraint,
                p_Owner = self.owner, p_Name = self.name)

class Trigger(Object):
    """Class for describing tables."""

    def __init__(self, environment, row):
        owner, name, self.tableName, self.description, self.whenClause, \
                actionType, body = row
        Object.__init__(self, environment, owner, name, "TRIGGER")
        if self.whenClause:
            self.whenClause = self.whenClause.replace("\0", "").strip()
        self.body = body.replace("\0", "").strip()
        if actionType == "CALL":
            self.body = "call %s" % self.body
            if self.body.endswith(";"):
                self.body = self.body[:-1]

    def Export(self, outFile):
        """Export the object as a SQL statement."""
        print >> outFile, "create or replace trigger", self.description.strip()
        if self.whenClause:
            print >> outFile, "when (%s)" % self.whenClause
        print >> outFile, self.body
        print >> outFile, "/"
        print >> outFile


class User(UserOrRole):
    """Class for describing users."""

    def __init__(self, environment, row):
        name, defaultTablespace, temporaryTablespace = row
        Object.__init__(self, environment, "SYSTEM", name, "USER")
        self.defaultTablespace = Utils.NameForOutput(defaultTablespace)
        self.temporaryTablespace = Utils.NameForOutput(temporaryTablespace)
        self.__RetrieveTablespaceQuotas()

    def __RetrieveTablespaceQuotas(self):
        """Retrieve the tablespace quotas for the user from the database."""
        cursor, isPrepared = self.environment.Cursor("TablespaceQuotas")
        if not isPrepared:
            cursor.prepare("""
                    select
                      tablespace_name,
                      max_bytes
                    from dba_ts_quotas
                    where username = :p_Name""")
        cursor.execute(None, p_Name = self.name)
        self.quotas = cursor.fetchall()
        self.quotas.sort()

    def Export(self, outFile):
        """Export the object as a SQL statement."""
        quotaClauses = ["\n  quota %s on %s" % \
                (Utils.SizeForOutput(s), Utils.NameForOutput(t)) \
                for t, s in self.quotas]
        finalClause = "".join(quotaClauses) + ";"
        print >> outFile, "create user", self.nameForOutput,
        print >> outFile, "identified by password"
        print >> outFile, "  default tablespace", self.defaultTablespace
        print >> outFile, "  temporary tablespace",
        print >> outFile, self.temporaryTablespace + finalClause
        print >> outFile


class View(ObjectWithTriggers, ObjectWithPrivileges, ObjectWithComments):
    """Class for describing views."""

    def __init__(self, environment, row):
        owner, name, self.text = row
        Object.__init__(self, environment, owner, name, "VIEW")

    def Export(self, outFile):
        """Export the object as a SQL statement."""
        print >> outFile, "create or replace view", self.nameForOutput, "as"
        print >> outFile, self.text.strip() + ";"
        print >> outFile


class ViewNoRetrieve(View):
    """Class for describing views without having described it first."""

    def __init__(self, environment, owner, name, type):
        cursor = PreparedCursor(environment, "View", Statements.VIEWS,
                "where o.owner = :p_Owner and o.view_name = :p_Name")
        cursor.execute(None, p_Owner = owner, p_Name = name)
        row = cursor.fetchone()
        View.__init__(self, environment, row)


def ObjectIterator(environment, tag, statement, whereClause, classFactory,
        *args, **keywordArgs):
    """Return an iterator for iterating through a list of objects one at a
       time without requiring all of the objects to be in memory at once."""
    cursor = PreparedCursor(environment, tag, statement, whereClause)
    cursor.execute(None, **keywordArgs)
    for row in cursor:
        yield classFactory(environment, row, *args)

def PreparedCursor(environment, tag, statement, whereClause):
    """Return a prepared cursor with the given statement."""
    cursor, isPrepared = environment.Cursor(tag)
    if not isPrepared:
        args = {
                "p_ViewPrefix" : environment.ViewPrefix(),
                "p_WhereClause" : whereClause
        }
        statement = statement % args
        if environment.maxLongSize is not None:
            cursor.setoutputsize(environment.maxLongSize)
        cursor.prepare(statement)
    return cursor

