"""Module for processing dependencies in SQL."""

import cx_Parser

import Statements

__all__ = [ "Processor" ]

class Processor(cx_Parser.DispatchProcessor):
    CreateIndexStatement = Statements.CreateIndexStatement
    CreatePackageStatement = Statements.CreatePackageStatement
    CreatePackageBodyStatement = Statements.CreatePackageBodyStatement
    CreatePublicSynonymStatement = Statements.CreatePublicSynonymStatement
    CreateRoleStatement = Statements.CreateRoleStatement
    CreateSequenceStatement = Statements.CreateSequenceStatement
    CreateSynonymStatement = Statements.CreateSynonymStatement
    CreateTableStatement = Statements.CreateTableStatement
    CreateTypeStatement = Statements.CreateTypeStatement
    CreateTypeBodyStatement = Statements.CreateTypeBodyStatement
    CreateUserStatement = Statements.CreateUserStatement
    CreateViewStatement = Statements.CreateViewStatement
    GrantStatement = Statements.GrantStatement
    RevokeStatement = Statements.RevokeStatement

    def __init__(self, initialOwner = None):
        self.owner = initialOwner

    def create_index_statement(self, sql, tag, start, end, children):
        owner, name = self.Dispatch(sql, children[0])
        return self.CreateIndexStatement(sql[start:end], owner, name)

    def create_package_statement(self, sql, tag, start, end, children):
        owner, name = self.Dispatch(sql, children[0])
        return self.CreatePackageStatement(sql[start:end], owner, name)

    def create_package_body_statement(self, sql, tag, start, end, children):
        owner, name = self.Dispatch(sql, children[0])
        return self.CreatePackageBodyStatement(sql[start:end], owner, name)

    def create_public_synonym_statement(self, sql, tag, start, end, children):
        name = self.Dispatch(sql, children[0])
        return self.CreatePublicSynonymStatement(sql[start:end], name)

    def create_role_statement(self, sql, tag, start, end, children):
        name = self.Dispatch(sql, children[0])
        return self.CreateRoleStatement(sql[start:end], name)

    def create_sequence_statement(self, sql, tag, start, end, children):
        owner, name = self.Dispatch(sql, children[0])
        return self.CreateSequenceStatement(sql[start:end], owner, name)

    def create_synonym_statement(self, sql, tag, start, end, children):
        owner, name = self.Dispatch(sql, children[0])
        return self.CreateSynonymStatement(sql[start:end], owner, name)

    def create_table_statement(self, sql, tag, start, end, children):
        owner, name = self.Dispatch(sql, children[0])
        return self.CreateTableStatement(sql[start:end], owner, name)

    def create_type_statement(self, sql, tag, start, end, children):
        owner, name = self.Dispatch(sql, children[0])
        return self.CreateTypeStatement(sql[start:end], owner, name)

    def create_type_body_statement(self, sql, tag, start, end, children):
        owner, name = self.Dispatch(sql, children[0])
        return self.CreateTypeBodyStatement(sql[start:end], owner, name)

    def create_user_statement(self, sql, tag, start, end, children):
        name = self.Dispatch(sql, children[0])
        return self.CreateUserStatement(sql[start:end], name)

    def create_view_statement(self, sql, tag, start, end, children):
        owner, name = self.Dispatch(sql, children[0])
        return self.CreateViewStatement(sql[start:end], owner, name)

    def grant_statement(self, sql, tag, start, end, children):
        return self.GrantStatement(sql[start:end])

    def qualified_identifier(self, sql, tag, start, end, children):
        identifiers = self.DispatchList(sql, children)
        if len(identifiers) == 2:
            owner, name = identifiers
        else:
            owner = self.owner
            name, = identifiers
        return (owner, name)

    def quoted_identifier(self, sql, tag, start, end, children):
        return sql[start + 1:end - 1]

    def revoke_statement(self, sql, tag, start, end, children):
        return self.RevokeStatement(sql[start:end])

    def unquoted_identifier(self, sql, tag, start, end, children):
        return sql[start:end].upper()

