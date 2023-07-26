from tiny_parser import Rule, TokenType, AST
import tiny_parser

# C++ Math language
class Statement(AST): pass
class Programm(AST): pass
class BinaryOperation(AST): pass
class UnaryOperation(AST): pass
class Literal(AST): pass
class Identifier(AST): pass
class CppToken(TokenType):
    DOUBLE_PLUS             = r"^\+\+"
    DOUBLE_MINUS            = r"^--"
    PLUS                    = r"^\+"
    MINUS                   = r"^-"
    TIMES                   = r"^\*"
    DIVIDES                 = r"^/"
    POWER                   = r"^\^"
    LESS_EQUAL              = r"^<="
    GREATER_EQUAL           = r"^>="
    LESS                    = r"^<"
    GREATER                 = r"^>"
    LEFT_PARENTHESIS        = r"^\("
    RIGHT_PARENTHESIS       = r"^\)"
    LEFT_SQUARE_BRACKET     = r"^\["
    RIGHT_SQUARE_BRACKET    = r"^\]"
    SEMICOLON               = r"^;"
    COLON                   = r"^:"
    COMMA                   = r"^,"
    DOT                     = r"^\."
    IDENTIFIER              = r"^[a-zA-Z_][a-zA-Z0-9_]*\b"
    LITERAL                 = r"^[1-9][0-9]*(\.[0-9]*)?\b|\.[0-9]+\b|0\b"
CppGrammar = {
    "0.1": Rule( BinaryOperation , ("1", "left") , ([CppToken.PLUS, CppToken.MINUS], "type") , ("0", "right") ),
    "0.2": Rule( None , "1" ),
    "1.1": Rule( BinaryOperation , ("2", "left") , ([CppToken.TIMES, CppToken.DIVIDES], "type") , ("1", "right") ),
    "1.2": Rule( None , "2" ),
    "2.1": Rule( UnaryOperation , ([CppToken.MINUS, CppToken.PLUS, CppToken.DOUBLE_PLUS, CppToken.DOUBLE_MINUS], "type") , ("2", "operand") ),
    "2.2": Rule( UnaryOperation , ("3", "operand"), ([CppToken.DOUBLE_PLUS, CppToken.DOUBLE_MINUS], "type") ),
    "2.3": Rule( None , "3" ),
    "3.1": Rule( None , CppToken.LEFT_PARENTHESIS , "0" , CppToken.RIGHT_PARENTHESIS ),
    "3.2": Rule( None , "4" ),
    "4.1": Rule( Literal , (CppToken.LITERAL, "value") ),
    "4.2": Rule( Identifier , (CppToken.IDENTIFIER, "name") ),
}

tiny_parser.print_ast( tiny_parser.parse( CppToken , CppGrammar, "1+2+3" , "0") )
