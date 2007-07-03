import cx_OptionParser
import cx_OracleParser

parser = cx_OptionParser.OptionParser("TestParser")
parser.AddOption("--production-name", default = "file",
        help = "the name of the production to look for")
parser.AddArgument("fileName", required = True,
        help = "the name of the file to parse")
options = parser.Parse()

parser = cx_OracleParser.Parser()
try:
    result = parser.Parse(file(options.fileName).read().strip(), "dummy",
            productionName = options.productionName)
    print "Result:", result
except cx_OracleParser.ParsingFailed, value:
    print "Parsing failed at position:", value.arguments["pos"]
    print "Remaining string:", value.arguments["remainingString"]

