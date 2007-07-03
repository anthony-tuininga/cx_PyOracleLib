"""Defines utility functions."""

import sys

import Object
import Statements

__all__ = [ "SOURCE_TYPES", "NameForOutput", "ObjectByType", "ObjectExists",
            "ObjectType", "OrderObjects" ]

SOURCE_TYPES = {
    "FUNCTION" : Object.StoredProcWithPrivileges,
    "PACKAGE" : Object.StoredProcWithBody,
    "PACKAGE BODY" : Object.StoredProc,
    "PROCEDURE" : Object.StoredProcWithPrivileges,
    "TYPE" : Object.StoredProcWithBody,
    "TYPE BODY" : Object.StoredProc,
    "VIEW" : Object.ViewNoRetrieve
}

CONSTRAINT_TYPES = [
    "CONSTRAINT",
    "PRIMARY KEY",
    "UNIQUE CONSTRAINT",
    "FOREIGN KEY",
    "CHECK CONSTRAINT"
]

def ClausesForOutput(clauses, firstString, restString, joinString):
    """Return a list of clauses suitable for output in a SQL statement."""
    if not clauses:
        return ""
    joinString = joinString + "\n" + restString
    return firstString + joinString.join(clauses)

def DependenciesOfInterest(key, objectsOfInterest, dependencies,
        dependenciesOfInterest):
    """Return a list of dependencies on objects of interest."""
    if dependencies.has_key(key):
        for refKey in dependencies[key]:
            if objectsOfInterest.has_key(refKey):
                dependenciesOfInterest[refKey] = None
            else:
                DependenciesOfInterest(refKey, objectsOfInterest, dependencies,
                        dependenciesOfInterest)

def NameForOutput(name):
    """Return the name suitable for output in a SQL statement."""
    if name.isupper():
        return name.lower()
    else:
        return '"%s"' % name

def ObjectByType(environment, owner, name, type):
    """Return an object of the correct type."""
    if type in SOURCE_TYPES:
        return SOURCE_TYPES[type](environment, owner, name, type)
    whereClause = "where o.owner = :p_Owner and "
    if type == "TABLE":
        whereClause += "o.table_name = :p_Name"
        statement = Statements.TABLES
        objectFunction = Object.Table
    elif type == "INDEX":
        whereClause += "o.index_name = :p_Name"
        statement = Statements.INDEXES
        objectFunction = Object.Index
    elif type == "TRIGGER":
        whereClause += "o.trigger_name = :p_Name"
        statement = Statements.TRIGGERS
        objectFunction = Object.Trigger
    elif type == "SYNONYM":
        whereClause += "o.synonym_name = :p_Name"
        statement = Statements.SYNONYMS
        objectFunction = Object.Synonym
    elif type == "SEQUENCE":
        whereClause = "where o.sequence_owner = :p_Owner " + \
                "and o.sequence_name = :p_Name"
        statement = Statements.SEQUENCES
        objectFunction = Object.Sequence
    elif type == "LIBRARY":
        whereClause += "o.library_name = :p_Name"
        statement = Statements.LIBRARIES
        objectFunction = Object.Library
    elif type in CONSTRAINT_TYPES:
        whereClause += "o.constraint_name = :p_Name"
        statement = Statements.CONSTRAINTS
        objectFunction = Object.Constraint
    else:
        raise "Do not know how to describe objects of type '%s'" % type
    for object in Object.ObjectIterator(environment, "Default_%s" % type,
            statement, whereClause, objectFunction,
            p_Owner = owner, p_Name = name):
        return object

def ObjectExists(environment, owner, name, type):
    """Returns a boolean indicating if the object exists."""
    if type in CONSTRAINT_TYPES:
        cursor, isPrepared = environment.Cursor("ConstraintExists")
        if not isPrepared:
            cursor.prepare("""
                    select count(*)
                    from %s_constraints
                    where owner = :p_Owner
                      and constraint_name = :p_Name""" % \
                    environment.ViewPrefix())
        cursor.execute(None,
                p_Owner = owner,
                p_Name = name)
    else:
        cursor, isPrepared = environment.Cursor("ObjectExists")
        if not isPrepared:
            cursor.prepare("""
                    select count(*)
                    from %s_objects
                    where owner = :p_Owner
                      and object_name = :p_Name
                      and object_type = :p_Type""" % environment.ViewPrefix())
        cursor.execute(None,
                p_Owner = owner,
                p_Name = name,
                p_Type = type)
    count, = cursor.fetchone()
    return (count > 0)

def ObjectType(environment, owner, name):
    """Return the type of the object, or None if the object does not exist."""
    cursor, isPrepared = environment.Cursor()
    cursor.execute("""
            select object_type
            from %s_objects
            where owner = :p_Owner
              and object_name = :p_Name
              and subobject_name is null
              and instr(object_type, 'BODY') = 0""" % environment.ViewPrefix(),
            p_Owner = owner,
            p_Name = name)
    row = cursor.fetchone()
    if row is not None:
        return row[0]

def OrderObjects(objects, dependencies):
    """Put the objects in the order necessary for creation without errors."""

    # initialize the mapping that indicates which items this object depends on
    iDependOn = {}
    dependsOnMe = {}
    for key in objects:
        iDependOn[key] = {}
        dependsOnMe[key] = {}

    # populate a mapping which indicates all of the dependencies for an object
    mappedDependencies = {}
    for owner, name, type, refOwner, refName, refType in dependencies:
        key = (owner, name, type)
        refKey = (refOwner, refName, refType)
        subDict = mappedDependencies.get(key)
        if subDict is None:
            subDict = mappedDependencies[key] = {}
        subDict[refKey] = None

    # now populate the mapping that indicates which items this object depends on
    # note that an object may depend on an object which is not in the list of
    # interest, but it itself depends on an object which is in the list so the
    # chain of dependencies is traversed until no objects of interest are found
    for key in iDependOn:
        refKeys = {}
        DependenciesOfInterest(key, iDependOn, mappedDependencies, refKeys)
        for refKey in refKeys:
            iDependOn[key][refKey] = None
            dependsOnMe[refKey][key] = None

    # order the items until no more items left
    outputObjs = {}
    orderedObjs = []
    while iDependOn:

        # acquire a list of items which do not depend on anything
        references = {}
        keysToOutput = {}
        for key, value in iDependOn.items():
            if not value:
                owner, name, type = key
                if owner not in keysToOutput:
                    keysToOutput[owner] = []
                keysToOutput[owner].append(key)
                del iDependOn[key]
            else:
                for refKey in value:
                    owner, name, type = refKey
                    if owner not in references:
                        references[owner] = 0
                    references[owner] += 1

        # detect a circular reference and avoid an infinite loop
        if not keysToOutput:
            keys = iDependOn.keys()
            keys.sort()
            for key in keys:
                print >> sys.stderr, "%s.%s (%s)" % key
                refKeys = iDependOn[key].keys()
                refKeys.sort()
                for refKey in refKeys:
                    print >> sys.stderr, "    %s.%s (%s)" % refKey
            raise "Circular reference detected!"

        # for each owner that has something to describe
        while keysToOutput:

            # determine the owner with the most references
            outputOwner = ""
            maxReferences = 0
            keys = references.keys()
            keys.sort()
            for key in keys:
                value = references[key]
                if value > maxReferences and key in keysToOutput:
                    maxReferences = value
                    outputOwner = key
            if not outputOwner:
                for key in keysToOutput:
                    outputOwner = key
                    break

            # remove this owner from the list
            keys = keysToOutput[outputOwner]
            del keysToOutput[outputOwner]
            if outputOwner in references:
                del references[outputOwner]

            # process this list, removing dependencies and adding additional
            # objects
            tempKeys = keys
            keys = []
            while tempKeys:
                nextKeys = []
                tempKeys.sort()
                for key in tempKeys:
                    refKeys = dependsOnMe[key].keys()
                    refKeys.sort()
                    for refKey in dependsOnMe[key]:
                        del iDependOn[refKey][key]
                        if not iDependOn[refKey]:
                            owner, name, type = refKey
                            if owner == outputOwner:
                                del iDependOn[refKey]
                                nextKeys.append(refKey)
                            elif owner in keysToOutput:
                                del iDependOn[refKey]
                                keysToOutput[owner].append(refKey)
                keys += tempKeys
                tempKeys = nextKeys

            # output the list of objects that have their dependencies satisfied
            for key in keys:
                if key not in outputObjs:
                    orderedObjs.append(key)
                    outputObjs[key] = None

    # return the ordered list
    return orderedObjs

def SetOptions(obj, options):
    """Set values from the options on the command line."""
    if options:
        for attribute in dir(options):
            if attribute.startswith("_"):
                continue
            if hasattr(obj, attribute):
                value = getattr(options, attribute)
                if isinstance(value, list):
                    value = [s for v in value for s in v.split(",")]
                setattr(obj, attribute, value)

def SizeForOutput(size):
    """Return the size suitable for output in a SQL statement. Note that a
       negative size is assumed to be unlimited."""
    if size < 0:
        return "unlimited"
    kilobytes, remainder = divmod(size, 1024)
    if not remainder:
        megabytes, remainder = divmod(kilobytes, 1024)
        if not remainder:
            return "%gm" % megabytes
        else:
            return "%gk" % kilobytes
    else:
        return "%g" % size

