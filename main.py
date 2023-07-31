from tiny_parser import Rule, TokenType, AST
import tiny_parser

# C++ Math language
class Program(AST): pass
class Statement(AST): pass
class StatementBlock(Statement): pass
class ExpressionStatement(Statement): pass
class BinaryOperation(AST): pass
class UnaryOperation(AST): pass
class MemberAccess(AST): pass
class Literal(AST): pass
class Identifier(AST): pass
class CppToken(TokenType):
    DOUBLE_EQUAL            = r"^=="
    NOT_EQUAL               = r"^!="
    LESS_EQUAL              = r"^<="
    GREATER_EQUAL           = r"^>="
    AND_EQUAL               = r"^&="
    OR_EQUAL                = r"^\|="
    XOR_EQUAL               = r"^\^="
    PLUS_EQUAL              = r"^\+="
    MINUS_EQUAL             = r"^-="
    TIMES_EQUAL             = r"^\*="
    DIVIDES_EQUAL           = r"^/="
    DOUBLE_AND              = r"^&&"
    DOUBLE_OR               = r"^\|\|"
    DOUBLE_PLUS             = r"^\+\+"
    DOUBLE_MINUS            = r"^--"
    PLUS                    = r"^\+"
    MINUS                   = r"^-"
    TIMES                   = r"^\*"
    DIVIDES                 = r"^/"
    POWER                   = r"^\^"
    LESS                    = r"^<"
    GREATER                 = r"^>"
    LEFT_PARENTHESIS        = r"^\("
    RIGHT_PARENTHESIS       = r"^\)"
    LEFT_SQUARE_BRACKET     = r"^\["
    RIGHT_SQUARE_BRACKET    = r"^\]"
    LEFT_CURLY_BRACKET      = r"^\{"
    RIGHT_CURLY_BRACKET     = r"^\}"
    SEMICOLON               = r"^;"
    COLON                   = r"^:"
    COMMA                   = r"^,"
    DOT                     = r"^\."
    IDENTIFIER              = r"^[a-zA-Z_][a-zA-Z0-9_]*\b"
    LITERAL                 = r"^[1-9][0-9]*(\.[0-9]*)?\b|\.[0-9]+\b|0\b"
CppGrammar = {
    # Statement Blocks
    "0.1": Rule( Program , ("10.", "statements") , ("1.", "statements") ),
    "0.2": Rule( Program , ("10.", "statements") ),
    "1.1": Rule( None , ("10.", "statements") , ("1.", "statements") ),
    "1.2": Rule( None , ("10.", "statements") ),

    # Statement
    "10.1": Rule( Statement , CppToken.SEMICOLON ),
    "10.2": Rule( StatementBlock , CppToken.LEFT_CURLY_BRACKET , CppToken.RIGHT_CURLY_BRACKET ),
    "10.2": Rule( StatementBlock , CppToken.LEFT_CURLY_BRACKET , ("1.1.", "statements") , CppToken.RIGHT_CURLY_BRACKET ),
    "10.3": Rule( ExpressionStatement , ("20.", "expression") , CppToken.SEMICOLON ),

    # Expression
    "20.1": Rule( BinaryOperation , ("21.", "left") , ([CppToken.PLUS, CppToken.MINUS], "type") , ("20.", "right") ),
    "20.2": Rule( None , "21." ),
    "21.1": Rule( BinaryOperation , ("22.", "left") , ([CppToken.TIMES, CppToken.DIVIDES], "type") , ("21.", "right") ),
    "21.2": Rule( None , "22." ),
    "22.1": Rule( UnaryOperation , ([CppToken.MINUS, CppToken.PLUS, CppToken.DOUBLE_PLUS, CppToken.DOUBLE_MINUS], "type") , ("22.", "operand") ),
    "22.2": Rule( UnaryOperation , ("23.", "operand"), ([CppToken.DOUBLE_PLUS, CppToken.DOUBLE_MINUS], "type") ),
    "22.3": Rule( None , "23." ),
    "23.1": Rule( None , CppToken.LEFT_PARENTHESIS , "20." , CppToken.RIGHT_PARENTHESIS ),
    "23.2": Rule( None , "24." ),
    "24.1": Rule( Literal , (CppToken.LITERAL, "value") ),
    "24.2": Rule( Identifier , (CppToken.IDENTIFIER, "name") ),
}

tiny_parser.print_ast( tiny_parser.parse( CppToken , CppGrammar, "1;{3;2;};3;" , "0") )
