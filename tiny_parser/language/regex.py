from .. import Rule, Language, AST, TokenType

# C++
class Pattern(AST): pass
class Option(Pattern): pass
class CharacterSet(Pattern): pass
class CharacterRange(Pattern): pass
class Mutliplier(Pattern): pass
class OneOrMoreTimes(Mutliplier): pass
class ZeroOrMoreTimes(Mutliplier): pass
class SpecificTimes(Mutliplier): pass
class RangeTimes(Mutliplier): pass
class Group(Pattern): pass
class Character(Pattern): pass
class EscapeCharacter(Character): pass
class StartToken(Character): pass
class EndToken(Character): pass
class RegexToken(TokenType):
    GROUP_OPEN              = r"^\("
    GROUP_CLOSE             = r"^\)"
    LIST_OPEN               = r"^\["
    LIST_CLOSE              = r"^\]"
    CURLY_OPEN              = r"^\{"
    CURLY_CLOSE             = r"^\}"
    STAR_MULTIPLIER         = r"^\*"
    PLUS_MULTIPLIER         = r"^\+"
    OPTION                  = r"^\|"
    BACKSLASH               = r"^\\."
    ESCAPED_CHARACTER       = r"^\\(?P<character>.)"
    COMMA                   = r"^,"
    HAT                     = r"^\^"
    DOLLAR                  = r"^\$"
    DASH                    = r"^-"
    DIGIT                   = r"^[0-9]"
    GENERAL_CHARACTER       = r"^."

regex_grammar = {
    "0.1": Rule( Option , ("10.", "options") , RegexToken.OPTION , ("1.", "options") ),
    "0.2": Rule( None , "10." ),
    "1.1": Rule( None , ("10.", "options") , RegexToken.OPTION , ("1.", "options" ) ),
    "1.2": Rule( None , "10." ),

    "10.1": Rule( Pattern , ("20.", "parts") , ("11.", "parts") ),
    "10.2": Rule( None , "20." ),
    "11.1": Rule( None , "20." , "11." ),
    "11.2": Rule( None , "20." ),

    "20.1": Rule( OneOrMoreTimes , ("30.", "parts") , RegexToken.PLUS_MULTIPLIER ),
    "20.2": Rule( ZeroOrMoreTimes , ("30.", "parts") , RegexToken.STAR_MULTIPLIER ),
    "20.3": Rule( SpecificTimes , ("30.", "parts") , RegexToken.CURLY_OPEN , ("21.", "times") , RegexToken.CURLY_CLOSE ),
    "20.4": Rule( RangeTimes , ("30.", "parts") , RegexToken.CURLY_OPEN , ("21.", "minimum") , RegexToken.COMMA , ("21.", "maximum") , RegexToken.CURLY_CLOSE ),
    "20.5": Rule( None , "30." ),
    "21.1": Rule( "" , (RegexToken.DIGIT, (None, "value")) , "21." ),
    "21.2": Rule( None ),

    "30.1": Rule( Group , RegexToken.GROUP_OPEN , RegexToken.GROUP_CLOSE ),
    "30.2": Rule( Group , RegexToken.GROUP_OPEN , ("0.", "value") , RegexToken.GROUP_CLOSE ),
    "30.3": Rule( None , "40." ),

    "40.1": Rule( CharacterSet , RegexToken.LIST_OPEN , ("41.", "includes") , RegexToken.LIST_CLOSE ),
    "40.2": Rule( CharacterSet , RegexToken.LIST_OPEN , ("41.", "includes") , RegexToken.HAT , ("41.", "excludes") , RegexToken.LIST_CLOSE ),
    "40.3": Rule( None , "50." ),
    "41.1": Rule( [] , "42." , "41."),
    "41.2": Rule( [] , "42." ),
    "41.3": Rule( [] ),
    "42.1": Rule( CharacterRange , ("43.", "from") , RegexToken.DASH , ("43.", "to") ),
    "42.2": Rule( [] , "43." ),
    "43.1": Rule( Character , (RegexToken.GROUP_OPEN, ("value", "value")) ),
    "43.2": Rule( Character , (RegexToken.GROUP_CLOSE, ("value", "value")) ),
    "43.3": Rule( Character , (RegexToken.LIST_OPEN, ("value", "value")) ),
    "43.4": Rule( Character , (RegexToken.CURLY_OPEN, ("value", "value")) ),
    "43.5": Rule( Character , (RegexToken.CURLY_CLOSE, ("value", "value")) ),
    "43.6": Rule( Character , (RegexToken.STAR_MULTIPLIER, ("value", "value")) ),
    "43.7": Rule( Character , (RegexToken.PLUS_MULTIPLIER, ("value", "value")) ),
    "43.8": Rule( Character , (RegexToken.OPTION, ("value", "value")) ),
    "43.9": Rule( Character , (RegexToken.COMMA, ("value", "value")) ),
    "43.10": Rule( Character , (RegexToken.DIGIT, ("value", "value")) ),
    "43.11": Rule( Character , (RegexToken.GENERAL_CHARACTER, ("value", "value")) ),
    "43.12": Rule( EscapeCharacter , (RegexToken.ESCAPED_CHARACTER, ("value", "character")) ),

    "50.2": Rule( Character , (RegexToken.COMMA, ("value", "value")) ),
    "50.1": Rule( Character , (RegexToken.DASH, ("value", "value")) ),
    "50.3": Rule( Character , (RegexToken.DIGIT, ("value", "value")) ),
    "50.4": Rule( StartToken , (RegexToken.HAT, ("value", "value")) ),
    "50.5": Rule( EndToken , (RegexToken.DOLLAR, ("value", "value")) ),
    "50.6": Rule( Character , (RegexToken.GENERAL_CHARACTER, ("value", "value")) ),
    "50.7": Rule( EscapeCharacter , (RegexToken.ESCAPED_CHARACTER, ("value", "character")) ),
}
regex = Language(regex_grammar, RegexToken)
