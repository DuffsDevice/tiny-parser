from .. import Token, Language, AST

# C++
class Program(AST): pass
class Statement(AST): pass
class StatementBlock(Statement): pass
class ExpressionStatement(Statement): pass
class BinaryOperation(AST): pass
class UnaryOperation(AST): pass
class MemberAccess(AST): pass
class Literal(AST): pass
class Identifier(AST): pass
cpp_grammar = {
    # Statement Blocks
    "0.1": ( Program , ("10.", "statements") , ("1.", "statements") ),
    "0.2": ( Program , ("10.", "statements") ),
    "1.1": ( [] , "10." , "1." ),
    "1.2": ( [] , "10." ),

    # Statement
    "10.1": ( Statement , Token.SEMICOLON ),
    "10.2": ( StatementBlock , Token.LEFT_CURLY_BRACKET , Token.RIGHT_CURLY_BRACKET ),
    "10.2": ( StatementBlock , Token.LEFT_CURLY_BRACKET , ("1.", "statements") , Token.RIGHT_CURLY_BRACKET ),
    "10.3": ( ExpressionStatement , ("20.", "expression") , Token.SEMICOLON ),

    # Expression
    "20.1": ( BinaryOperation , ("21.", "left") , ([Token.PLUS, Token.MINUS], "type") , ("20.", "right") ),
    "20.2": ( None , "21." ),
    "21.1": ( BinaryOperation , ("22.", "left") , ([Token.TIMES, Token.DIVIDES], "type") , ("21.", "right") ),
    "21.2": ( None , "22." ),
    "22.1": ( UnaryOperation , ([Token.MINUS, Token.PLUS, Token.DOUBLE_PLUS, Token.DOUBLE_MINUS], "type") , ("22.", "operand") ),
    "22.2": ( UnaryOperation , ("23.", "operand"), ([Token.DOUBLE_PLUS, Token.DOUBLE_MINUS], "type") ),
    "22.3": ( None , "23." ),
    "23.1": ( None , Token.LEFT_PARENTHESIS , "20." , Token.RIGHT_PARENTHESIS ),
    "23.2": ( None , "24." ),
    "24.1": ( Literal , (Token.NUMBER, ("value", "value")) ),
    "24.2": ( Literal , (Token.STRING, ("value", "value")) ),
    "24.3": ( Identifier , (Token.IDENTIFIER, ("name", "value")) ),
}
cpp = Language(cpp_grammar)
