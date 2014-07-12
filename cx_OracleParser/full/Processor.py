"""Module for processing dependencies in SQL."""

import cx_Exceptions
import cx_Parser

from . import Statements

__all__ = [ "Processor" ]

class Processor(cx_Parser.DispatchProcessor):
    systemIdentifiers = """
            ascii binary_integer boolean ceil char chr count date decode dual
            floor greatest instr last_day least length lower lpad ltrim max min
            next_day null number nvl pls_integer raise_application_error
            replace round rpad rtrim sql substr sum to_char to_number to_date
            trim trunc upper varchar2"""

    def __init__(self):
        self.owner = None
        self.__directory = {}
        self.__identifiers = []
        self.__AddScope()
        self.__ClearExternalReferences()
        for identifier in self.systemIdentifiers.split():
            self.__AddIdentifier(identifier.upper())

    def __AddIdentifier(self, identifier):
        """Adds an identifier to the current scope."""
        self.__AddQualifiedIdentifier((identifier,))

    def __AddQualifiedIdentifier(self, identifier):
        """Adds a qualified identifier to the current scope."""
        identifier = tuple(identifier)
        self.__identifiers[-1][identifier] = None
        if identifier in self.__externalReferences:
            del self.__externalReferences[identifier]

    def __AddReference(self, identifier, ignoreUnqualified = False):
        """Add a reference to an identifier."""
        if ignoreUnqualified and len(identifier) == 1:
            return
        if identifier in self.__externalReferences:
            return
        identifiers = [identifier[:n + 1] for n in range(len(identifier))]
        for scope in self.__identifiers:
            for identifier in identifiers:
                if identifier in scope:
                    return
        self.__externalReferences[identifier] = None

    def __AddScope(self):
        """Add a level of scope."""
        self.__identifiers.append({})

    def __ClearExternalReferences(self):
        """Clear the external references defined."""
        self.__externalReferences = {}

    def __ExternalReferences(self):
        """Return a sorted list of external references."""
        childValues = list(self.__externalReferences.keys())
        childValues.sort()
        return childValues

    def __IsIdentifier(self, tag):
        """Return true if the tag is for an identifier."""
        return tag in ("unquoted_identifier", "quoted_identifier")

    def __LocalIdentifiers(self):
        """Return a sorted list of local identifiers."""
        childValues = list(self.__identifiers[-1].keys())
        childValues.sort()
        return childValues

    def __RemoveScope(self):
        """Remove a level of scope."""
        self.__identifiers.pop()

    def argument(self, sql, tag, start, end, children):
        childTag, childValue = self.DispatchList(sql, children)[0]
        self.__AddIdentifier(childValue)

    def array_declaration(self, sql, tag, start, end, children):
        results = self.DispatchList(sql, children)
        childTag, childValue = results[1]
        self.__AddIdentifier(childValue)

    def check_constraint(self, sql, tag, start, end, children):
        results = self.DispatchList(sql, children)
        childTag, (constraintName, tableName) = results[0]
        return Statements.CheckConstraint(sql[start:end], self.__directory,
                self.owner, constraintName, tableName)

    def common_definition(self, sql, tag, start, end, children):
        childTag, childValue = self.Dispatch(sql, children[0])
        self.__AddIdentifier(childValue)
        self.__AddScope()
        self.DispatchList(sql, children)[1:]

    def constraint_common_clause(self, sql, tag, start, end, children):
        results = self.DispatchList(sql, children)
        childTag, tableName = results[2]
        childTag, constraintName = results[5]
        return tag, (constraintName, tableName)

    def create_index_statement(self, sql, tag, start, end, children):
        indexName, tableName = [v for t, v in self.DispatchList(sql, children)
                if self.__IsIdentifier(t)]
        return Statements.Index(sql[start:end], self.__directory, self.owner,
                indexName, tableName)

    def create_package_statement(self, sql, tag, start, end, children):
        self.__ClearExternalReferences()
        self.__AddScope()
        isPackage = True
        for childTag, childValue in self.DispatchList(sql, children):
            if self.__IsIdentifier(childTag):
                objectName = childValue
                self.__AddIdentifier(childValue)
            if childTag == "KW_body":
                isPackage = False
        if isPackage:
            obj = Statements.Package(sql[start:end], self.__directory,
                    self.owner, objectName, self.__ExternalReferences(),
                    self.__LocalIdentifiers())
        else:
            package = self.__directory.get((self.owner, objectName))
            if package is None:
                raise MissingPackageHeader(objectName = objectName)
            for identifier in package.identifiers:
                self.__AddQualifiedIdentifier(identifier)
            obj = Statements.PackageBody(sql[start:end], self.__directory,
                    self.owner, objectName, self.__ExternalReferences())
        self.__RemoveScope()
        return obj

    def create_role_statement(self, sql, tag, start, end, children):
        tag, name = self.DispatchList(sql, children)[2]
        return Statements.Role(sql[start:end], self.__directory, name)

    def create_sequence_statement(self, sql, tag, start, end, children):
        childTag, name = self.DispatchList(sql, children)[2]
        return Statements.Sequence(sql[start:end], self.__directory,
                self.owner, name)

    def create_synonym_statement(self, sql, tag, start, end, children):
        results = self.DispatchList(sql, children)
        childTag, childValue = results[1]
        if childTag == "KW_public":
            childTag, name = results[3]
            childTag, refName = results[5]
            return Statements.PublicSynonym(sql[start:end], self.__directory,
                name, refName)
        else:
            childTag, name = results[2]
            childTag, refName = results[4]
            return Statements.Synonym(sql[start:end], self.__directory,
                self.owner, name, refName)

    def create_table_statement(self, sql, tag, start, end, children):
        name, = [v for t, v in self.DispatchList(sql, children)
                if self.__IsIdentifier(t)]
        return Statements.Table(sql[start:end], self.__directory, self.owner,
                name)

    def create_trigger_statement(self, sql, tag, start, end, children):
        name, tableName = [v for t, v in self.DispatchList(sql, children)
                if self.__IsIdentifier(t)]
        return Statements.Trigger(sql[start:end], self.__directory, self.owner,
                name)

    def create_type_statement(self, sql, tag, start, end, children):
        self.__ClearExternalReferences()
        self.__AddScope()
        for childTag, childValue in self.DispatchList(sql, children):
            if self.__IsIdentifier(childTag):
                self.__AddIdentifier(childValue)
        name, = self.__LocalIdentifiers()[0]
        references = self.__ExternalReferences()
        self.__RemoveScope()
        return Statements.Type(sql[start:end], self.__directory, self.owner,
            name, references)

    def create_user_statement(self, sql, tag, start, end, children):
        tag, name = self.DispatchList(sql, children)[2]
        return Statements.User(sql[start:end], self.__directory, name)

    def create_view_statement(self, sql, tag, start, end, children):
        self.__ClearExternalReferences()
        self.__AddScope()
        for childTag, childValue in self.DispatchList(sql, children):
            if self.__IsIdentifier(childTag):
                self.__AddIdentifier(childValue)
        viewName, = self.__LocalIdentifiers()[0]
        references = self.__ExternalReferences()
        self.__RemoveScope()
        return Statements.View(sql[start:end], self.__directory, self.owner,
            viewName, references)

    def cursor_definition(self, sql, tag, start, end, children):
        self.DispatchList(sql, children)
        self.__RemoveScope()
        return tag, []

    def data_type(self, sql, tag, start, end, children):
        for childTag, childValue in self.DispatchList(sql, children):
            if childTag == "qualified_identifier":
                self.__AddReference(childValue)

    def delete_statement(self, sql, tag, start, end, children):
        for childTag, childValue in self.DispatchList(sql, children):
            if childTag == "qualified_identifier":
                self.__AddReference(childValue)

    def for_clause(self, sql, tag, start, end, children):
        childTag, childValue = self.DispatchList(sql, children)[0]
        self.__AddIdentifier(childValue)

    def foreign_key_constraint(self, sql, tag, start, end, children):
        results = self.DispatchList(sql, children)
        childTag, (constraintName, tableName) = results[0]
        childTag, referencedTable = results[5]
        return Statements.ForeignKey(sql[start:end], self.__directory,
                self.owner, constraintName, tableName, referencedTable)

    def from_clause(self, sql, tag, start, end, children):
        for childTag, childValue in self.DispatchList(sql, children):
            if childTag == "qualified_identifier":
                self.__AddReference(childValue)
            elif self.__IsIdentifier(childTag):
                self.__AddIdentifier(childValue)

    def function_declaration(self, sql, tag, start, end, children):
        self.DispatchList(sql, children)
        self.__RemoveScope()
        return tag, []

    def function_expression(self, sql, tag, start, end, children):
        childTag, childValue = self.DispatchList(sql, children)[0]
        self.__AddReference(childValue)

    def grant_statement(self, sql, tag, start, end, children):
        items = self.DispatchList(sql, children)
        if items[2][0] == "KW_to":
            privileges = items[1][1]
            grantees = items[3][1]
            return Statements.Grant(sql[start:end], privileges, grantees)
        else:
            privileges = items[1][1]
            objectTuple = items[3][1]
            grantees = items[5][1]
            if len(objectTuple) == 1:
                objectOwner = self.owner
                objectName, = objectTuple
            else:
                objectOwner, objectName = objectTuple
            return Statements.Grant(sql[start:end], privileges, grantees,
                    objectOwner, objectName)

    def identifier_list(self, sql, tag, start, end, children):
        return tag, [v for t, v in self.DispatchList(sql, children)]

    def identifier_modifier(self, sql, tag, start, end, children):
        return tag, None

    def insert_statement(self, sql, tag, start, end, children):
        childTag, childValue = self.DispatchList(sql, children)[2]
        self.__AddReference(childValue)

    def primary_key_constraint(self, sql, tag, start, end, children):
        results = self.DispatchList(sql, children)
        childTag, (constraintName, tableName) = results[0]
        return Statements.PrimaryKey(sql[start:end], self.__directory,
                self.owner, constraintName, tableName)

    def prior_expression(self, sql, tag, start, end, children):
        childTag, childValue = self.DispatchList(sql, children)[-1]
        self.__AddReference(childValue, ignoreUnqualified = True)

    def privilege(self, sql, tag, start, end, children):
        return tag, " ".join(sql[start:end].split())

    def privilege_list(self, sql, tag, start, end, children):
        return tag, [v for t, v in self.DispatchList(sql, children)]

    def procedure_declaration(self, sql, tag, start, end, children):
        results = self.DispatchList(sql, children)
        self.__RemoveScope()
        return tag, []

    def qualified_identifier(self, sql, tag, start, end, children):
        identifiers = [v for t, v in self.DispatchList(sql, children) if v]
        return tag, tuple(identifiers)

    def quoted_identifier(self, sql, tag, start, end, children):
        return tag, sql[start+1:end-1]

    def record_declaration(self, sql, tag, start, end, children):
        results = self.DispatchList(sql, children)
        childTag, childValue = results[1]
        self.__AddIdentifier(childValue)

    def return_clause(self, sql, tag, start, end, children):
        results = self.DispatchList(sql, children)
        childTag, childValue = results[1]
        self.__AddReference(childValue)

    def revoke_statement(self, sql, tag, start, end, children):
        items = self.DispatchList(sql, children)
        if items[2][0] == "KW_from":
            privileges = items[1][1]
            grantees = items[3][1]
            return Statements.Revoke(sql[start:end], privileges, grantees)
        else:
            privileges = items[1][1]
            objectTuple = items[3][1]
            grantees = items[5][1]
            if len(objectTuple) == 1:
                objectOwner = self.owner
                objectName, = objectTuple
            else:
                objectOwner, objectName = objectTuple
            return Statements.Revoke(sql[start:end], privileges, grantees,
                    objectOwner, objectName)

    def select_into_statement(self, sql, tag, start, end, children):
        self.select_statement(sql, tag, start, end, children)

    def select_statement(self, sql, tag, start, end, children):
        self.__AddScope()
        for child in children:
            childTag, start, end, subChildren = child
            if childTag == "from_clause_list":
                self.Dispatch(sql, child)
        for child in children:
            childTag, start, end, subChildren = child
            if childTag != "from_clause_list":
                self.Dispatch(sql, child)
        self.__RemoveScope()
        return tag, None

    def simple_declaration(self, sql, tag, start, end, children):
        childTag, childValue = self.DispatchList(sql, children)[0]
        self.__AddIdentifier(childValue)

    def standalone_select_statement(self, sql, tag, start, end, children):
        self.__ClearExternalReferences()
        self.__AddScope()
        for childTag, childValue in self.DispatchList(sql, children):
            if self.__IsIdentifier(childTag):
                self.__AddIdentifier(childValue)
        references = self.__ExternalReferences()
        self.__RemoveScope()
        return Statements.StandaloneSelect(sql[start:end], self.__directory,
                references)

    def subtype_declaration(self, sql, tag, start, end, children):
        results = self.DispatchList(sql, children)
        childTag, childValue = results[1]
        self.__AddIdentifier(childValue)
        childTag, childValue = results[-1]
        if childTag == "range_clause":
            childTag, childValue = results[-2]
        self.__AddReference(childValue)

    def unique_constraint(self, sql, tag, start, end, children):
        results = self.DispatchList(sql, children)
        childTag, (constraintName, tableName) = results[0]
        return Statements.UniqueConstraint(sql[start:end], self.__directory,
                self.owner, constraintName, tableName)

    def unquoted_identifier(self, sql, tag, start, end, children):
        return tag, sql[start:end].upper()

    def update_statement(self, sql, tag, start, end, children):
        childTag, childValue = self.DispatchList(sql, children)[1]
        self.__AddReference(childValue)


class MissingPackageHeader(cx_Exceptions.BaseException):
    message = "Missing header for package '%(objectName)s'"

