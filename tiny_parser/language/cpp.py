from .. import Rule, StandardToken, Language, AST

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
    "0.1": Rule( Program , ("10.", "statements") , ("1.", "statements") ),
    "0.2": Rule( Program , ("10.", "statements") ),
    "1.1": Rule( [] , "10." , "1." ),
    "1.2": Rule( [] , "10." ),

    # Statement
    "10.1": Rule( Statement , StandardToken.SEMICOLON ),
    "10.2": Rule( StatementBlock , StandardToken.LEFT_CURLY_BRACKET , StandardToken.RIGHT_CURLY_BRACKET ),
    "10.2": Rule( StatementBlock , StandardToken.LEFT_CURLY_BRACKET , ("1.", "statements") , StandardToken.RIGHT_CURLY_BRACKET ),
    "10.3": Rule( ExpressionStatement , ("20.", "expression") , StandardToken.SEMICOLON ),

    # Expression
    "20.1": Rule( BinaryOperation , ("21.", "left") , ([StandardToken.PLUS, StandardToken.MINUS], "type") , ("20.", "right") ),
    "20.2": Rule( None , "21." ),
    "21.1": Rule( BinaryOperation , ("22.", "left") , ([StandardToken.TIMES, StandardToken.DIVIDES], "type") , ("21.", "right") ),
    "21.2": Rule( None , "22." ),
    "22.1": Rule( UnaryOperation , ([StandardToken.MINUS, StandardToken.PLUS, StandardToken.DOUBLE_PLUS, StandardToken.DOUBLE_MINUS], "type") , ("22.", "operand") ),
    "22.2": Rule( UnaryOperation , ("23.", "operand"), ([StandardToken.DOUBLE_PLUS, StandardToken.DOUBLE_MINUS], "type") ),
    "22.3": Rule( None , "23." ),
    "23.1": Rule( None , StandardToken.LEFT_PARENTHESIS , "20." , StandardToken.RIGHT_PARENTHESIS ),
    "23.2": Rule( None , "24." ),
    "24.1": Rule( Literal , (StandardToken.LITERAL, ("value", "content")) ),
    "24.2": Rule( Identifier , (StandardToken.IDENTIFIER, ("name", "content")) ),
}
cpp = Language(cpp_grammar)
