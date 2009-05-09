"""Module for processing dependencies in SQL."""

import cx_Parser

import Statements

__all__ = [ "Processor" ]

class Processor(cx_Parser.DispatchProcessor):
    CreateTableStatement = Statements.CreateTableStatement
    CreateViewStatement = Statements.CreateViewStatement
    GrantStatement = Statements.GrantStatement

    def __init__(self, initialOwner = None):
        self.owner = initialOwner

    def create_table_statement(self, sql, tag, start, end, children):
        owner, name = self.Dispatch(sql, children[0])
        return self.CreateTableStatement(sql[start:end], owner, name)

    def create_view_statement(self, sql, tag, start, end, children):
        owner, name = self.Dispatch(sql, children[0])
        return self.CreateViewStatement(sql[start:end], owner, name)

    def grant_statement(self, sql, tag, start, end, children):
        return self.GrantStatement(sql[start:end])

    def quoted_identifier(self, sql, tag, start, end, children):
        return sql[start + 1:end - 1]

    def unquoted_identifier(self, sql, tag, start, end, children):
        return sql[start:end].upper()

    def qualified_identifier(self, sql, tag, start, end, children):
        identifiers = self.DispatchList(sql, children)
        if len(identifiers) == 2:
            owner, name = identifiers
        else:
            owner = self.owner
            name, = identifiers
        return (owner, name)

