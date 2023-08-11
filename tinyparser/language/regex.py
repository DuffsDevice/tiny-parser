from .. import Language, AST, TokenType

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
    "0.1": ( Option , ("10.", "options") , RegexToken.OPTION , ("1.", "options") ),
    "0.2": ( None , "10." ),
    "1.1": ( None , ("10.", "options") , RegexToken.OPTION , ("1.", "options" ) ),
    "1.2": ( None , "10." ),

    "10.1": ( Pattern , ("20.", "parts") , ("11.", "parts") ),
    "10.2": ( None , "20." ),
    "11.1": ( None , "20." , "11." ),
    "11.2": ( None , "20." ),

    "20.1": ( OneOrMoreTimes , ("30.", "parts") , RegexToken.PLUS_MULTIPLIER ),
    "20.2": ( ZeroOrMoreTimes , ("30.", "parts") , RegexToken.STAR_MULTIPLIER ),
    "20.3": ( SpecificTimes , ("30.", "parts") , RegexToken.CURLY_OPEN , ("21.", "times") , RegexToken.CURLY_CLOSE ),
    "20.4": ( RangeTimes , ("30.", "parts") , RegexToken.CURLY_OPEN , ("21.", "minimum") , RegexToken.COMMA , ("21.", "maximum") , RegexToken.CURLY_CLOSE ),
    "20.5": ( None , "30." ),
    "21.1": ( "" , (RegexToken.DIGIT, (None, "value")) , "21." ),
    "21.2": ( None ),

    "30.1": ( Group , RegexToken.GROUP_OPEN , RegexToken.GROUP_CLOSE ),
    "30.2": ( Group , RegexToken.GROUP_OPEN , ("0.", "value") , RegexToken.GROUP_CLOSE ),
    "30.3": ( None , "40." ),

    "40.1": ( CharacterSet , RegexToken.LIST_OPEN , ("41.", "includes") , RegexToken.LIST_CLOSE ),
    "40.2": ( CharacterSet , RegexToken.LIST_OPEN , ("41.", "includes") , RegexToken.HAT , ("41.", "excludes") , RegexToken.LIST_CLOSE ),
    "40.3": ( None , "50." ),
    "41.1": ( [] , "42." , "41."),
    "41.2": ( [] , "42." ),
    "41.3": ( [] ),
    "42.1": ( CharacterRange , ("43.", "from") , RegexToken.DASH , ("43.", "to") ),
    "42.2": ( [] , "43." ),
    "43.1": ( Character , (RegexToken.GROUP_OPEN, ("value", "value")) ),
    "43.2": ( Character , (RegexToken.GROUP_CLOSE, ("value", "value")) ),
    "43.3": ( Character , (RegexToken.LIST_OPEN, ("value", "value")) ),
    "43.4": ( Character , (RegexToken.CURLY_OPEN, ("value", "value")) ),
    "43.5": ( Character , (RegexToken.CURLY_CLOSE, ("value", "value")) ),
    "43.6": ( Character , (RegexToken.STAR_MULTIPLIER, ("value", "value")) ),
    "43.7": ( Character , (RegexToken.PLUS_MULTIPLIER, ("value", "value")) ),
    "43.8": ( Character , (RegexToken.OPTION, ("value", "value")) ),
    "43.9": ( Character , (RegexToken.COMMA, ("value", "value")) ),
    "43.10": ( Character , (RegexToken.DIGIT, ("value", "value")) ),
    "43.11": ( Character , (RegexToken.GENERAL_CHARACTER, ("value", "value")) ),
    "43.12": ( EscapeCharacter , (RegexToken.ESCAPED_CHARACTER, ("value", "character")) ),

    "50.2": ( Character , (RegexToken.COMMA, ("value", "value")) ),
    "50.1": ( Character , (RegexToken.DASH, ("value", "value")) ),
    "50.3": ( Character , (RegexToken.DIGIT, ("value", "value")) ),
    "50.4": ( StartToken , (RegexToken.HAT, ("value", "value")) ),
    "50.5": ( EndToken , (RegexToken.DOLLAR, ("value", "value")) ),
    "50.6": ( Character , (RegexToken.GENERAL_CHARACTER, ("value", "value")) ),
    "50.7": ( EscapeCharacter , (RegexToken.ESCAPED_CHARACTER, ("value", "character")) ),
}
regex = Language(regex_grammar, RegexToken, "0.", None)
