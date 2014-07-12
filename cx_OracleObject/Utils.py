"""Defines utility functions."""

import cx_Exceptions
import sys

__all__ = [ "OrderObjects" ]

def ClausesForOutput(clauses, firstString, restString, joinString):
    """Return a list of clauses suitable for output in a SQL statement."""
    if not clauses:
        return ""
    joinString = joinString + "\n" + restString
    return firstString + joinString.join(clauses)

def DependenciesOfInterest(key, objectsOfInterest, dependencies,
        dependenciesOfInterest):
    """Return a list of dependencies on objects of interest."""
    if key in dependencies:
        for refKey in dependencies[key]:
            if refKey in objectsOfInterest:
                dependenciesOfInterest[refKey] = None
            else:
                DependenciesOfInterest(refKey, objectsOfInterest, dependencies,
                        dependenciesOfInterest)

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
        for key, value in list(iDependOn.items()):
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
            keys = list(iDependOn.keys())
            keys.sort()
            for key in keys:
                print("%s.%s (%s)" % key, file = sys.stderr)
                refKeys = list(iDependOn[key].keys())
                refKeys.sort()
                for refKey in refKeys:
                    print("    %s.%s (%s)" % refKey, file = sys.stderr)
            raise CircularReferenceDetected()

        # for each owner that has something to describe
        while keysToOutput:

            # determine the owner with the most references
            outputOwner = ""
            maxReferences = 0
            keys = list(references.keys())
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
                    refKeys = list(dependsOnMe[key].keys())
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


class CircularReferenceDetected(cx_Exceptions.BaseException):
    message = "Circular reference detected!"

