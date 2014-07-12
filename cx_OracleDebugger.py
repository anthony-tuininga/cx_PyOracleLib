"""Return messages from a DBMS pipe."""

import cx_Exceptions
import cx_Logging
import cx_Oracle

class CannotReceiveMessage(cx_Exceptions.BaseException):
    message = "Unable to receive message: return value is %(returnValue)d"


class UnhandledProtocol(cx_Exceptions.BaseException):
    message = 'Unhandled protocol "%(protocol)s"'


class UnhandledService(cx_Exceptions.BaseException):
    message = 'Unhandled service "%(serviceName)s"'


def Enable(connection, pipeName = None):
    """Enable debugging messages on the given pipe."""
    cursor = connection.cursor()
    if pipeName is None:
        pipeName = cursor.callfunc("dbms_pipe.unique_session_name",
                cx_Oracle.STRING)
    cursor.callproc("pkg_Debug.Enable", (pipeName,))
    cx_Logging.Debug("logging messages to pipe %s", pipeName)
    return pipeName


def LogMessages(connection, pipeName):
    """Log messages using the cx_Logging module."""
    cx_Logging.Debug("logging messages from pipe %s", pipeName)
    debugConnection = cx_Oracle.Connection(connection.username,
            connection.password, connection.tnsentry, threaded = True)
    for message in MessageGenerator(debugConnection, pipeName):
        cx_Logging.Trace("%s", message)


def MessageGenerator(connection, pipeName):
    """Generator function which returns messages as they are received and
       terminates only when a shutdown request is received."""

    # prepare a cursor for acquiring the service
    serviceCursor = connection.cursor()
    serviceCursor.prepare("""
            begin
              :returnValue := dbms_pipe.receive_message(:pipeName);
              dbms_pipe.unpack_message(:protocol);
              dbms_pipe.unpack_message(:returnPipeName);
              dbms_pipe.unpack_message(:serviceName);
            end;""")
    serviceBindVars = serviceCursor.setinputsizes(
            pipeName = cx_Oracle.STRING,
            returnValue = cx_Oracle.NUMBER,
            protocol = cx_Oracle.STRING,
            returnPipeName = cx_Oracle.STRING,
            serviceName = cx_Oracle.STRING)
    pipeNameVar = serviceBindVars["pipeName"]
    pipeNameVar.setvalue(0, pipeName)
    returnValueVar = serviceBindVars["returnValue"]
    protocolVar = serviceBindVars["protocol"]
    serviceNameVar = serviceBindVars["serviceName"]

    # prepare a cursor for logging messages
    loggingCursor = connection.cursor()
    loggingCursor.prepare("""
            begin
              dbms_pipe.unpack_message(:lastPartOfMessage);
              dbms_pipe.unpack_message(:message);
            end;""")
    loggingBindVars = loggingCursor.setinputsizes(
            lastPartOfMessage = cx_Oracle.NUMBER,
            message = cx_Oracle.STRING)
    lastPartOfMessageVar = loggingBindVars["lastPartOfMessage"]
    messageVar = loggingBindVars["message"]

    # process logging requests until a shutdown request is found
    messageParts = []
    while True:
        serviceCursor.execute(None)
        returnValue = returnValueVar.getvalue()
        if returnValue:
            raise CannotReceiveMessage(returnValue = returnValue)
        serviceName = serviceNameVar.getvalue()
        if serviceName == "Shutdown":
            yield "*** TERMINATING ***"
            break
        if serviceName != "LogMessage":
            raise UnhandledService(serviceName = serviceName)
        protocol = protocolVar.getvalue()
        if protocol != "2":
            raise UnhandledProtocol(protocol = protocol)
        loggingCursor.execute(None)
        part = messageVar.getvalue()
        if part is not None:
            messageParts.append(part)
        if lastPartOfMessageVar.getvalue():
            yield "".join(messageParts)
            messageParts = []


def Shutdown(connection, pipeName):
    """Shutdown debugging messages on the given pipe."""
    cursor = connection.cursor()
    cursor.callproc("pkg_Debug.Shutdown", (pipeName,))

