from enum import Enum
from extendableenum import inheritable_enum
import re

# Tokenizer
@inheritable_enum
class TokenType(Enum):
    @staticmethod
    def strip_space_before(): return " "
    def __init__(self, pattern):
        self.pattern = re.compile(pattern)
class Token:
    def __init__(self, type: TokenType, content: str, space_before: str):
        self.type = type
        self.content = content
def tokenize(token_class, input: str):
    result = []
    space_before = None
    spaces = token_class.strip_space_before()
    if spaces:
        new_input = input.lstrip(spaces)
        space_before, input = input[:len(input)-len(new_input)], new_input
    while input:
        for token_type in token_class:
            if match := token_type.pattern.match(input):
                result.append(Token(token_type, match.group(), space_before))
                input = input[len(match.group()):]
                break
        else:
            raise Exception("No Token matched at: %.7s..." % input)
        if spaces:
            new_input = input.lstrip(spaces)
            space_before, input = input[:len(input)-len(new_input)], new_input
    return result

# Parser State
class ParserState:
    def __init__(self, token_list, current_index=0):
        self.token_list = token_list
        self.current_index = current_index
    @property
    def current_token(self):
        return self.token_list[self.current_index] if self.current_index < len(self.token_list) else None
    def take(self, *token_types):
        current_token = self.current_token
        if current_token and current_token.type in token_types:
            self.current_index += 1
            return current_token
        return None
    def fork(self):
        return ParserState(self.token_list, self.current_index)

def set_or_append(dict, key, value):
    orig_value = dict.get(key, None)
    if orig_value is not None:
        if value is not None:
            if not isinstance(value, list):
                value = [value]
            if not isinstance(orig_value, list):
                orig_value = [orig_value]
            dict[key] = [*orig_value, *value]
    else:
        dict[key] = value

# Abstract Syntax Tree Classes
class AST: pass
class Rule:
    def __init__(self, target_class:type, *pattern ):
        self.target_class = target_class
        self.pattern = pattern if pattern else []
class StandardToken(TokenType):
    DOUBLE_EQUAL            = r"^=="
    EXCLAMATION_EQUAL       = r"^!="
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
    HAT                     = r"^,"
    DOT                     = r"^\."
    IDENTIFIER              = r"^[a-zA-Z_][a-zA-Z0-9_]*\b"
    NUMBER                  = r'^[1-9][0-9]*(\.[0-9]*)?\b|\.[0-9]+\b|0\b'
    STRING                  = r'^"([^"]|\")+"'
class Language:
    def __init__(self, rules, token_class=StandardToken, root_rule="0."):
        self.rules = rules
        self.token_class = token_class
        self.root_rule = root_rule

# Parser
def parse_ex(language:dict, rule_path: str, state_reference):
    class CacheEntry:
        def __init__(self, state_reference, requirement=None, result=None):
            self.state_reference = state_reference
            self.requirement = requirement
            self.result = result
    cache = [CacheEntry(state_reference, None, None)]
    viable_rules = [(key, rule) for key, rule in language.items() if key.startswith(rule_path)]
    for key, rule in viable_rules:
        for number, requirement in enumerate(rule.pattern, 1):
            if isinstance(requirement, tuple):
                requirement = requirement[0]
            cache_usable = False
            if len(cache) > number:
                if cache[number].requirement is requirement: # Check if we can use the cache for this requirement
                    cache_usable = True
                else:
                    cache = cache[:number+1] # Truncate cache to prefix we can re-use
            if not cache_usable:
                cache.append(CacheEntry([cache[-1].state_reference[0].fork()], requirement)) # Create new cache layer
                success = False
                if isinstance(requirement, TokenType):
                    cache[-1].result = cache[-1].state_reference[0].take(requirement)
                elif isinstance(requirement, list):
                    cache[-1].result = cache[-1].state_reference[0].take(*requirement)
                elif isinstance(requirement, str): # Referring to another rule
                    cache[-1].result, success = parse_ex(language, requirement, cache[-1].state_reference)
                if cache[-1].result is None and success == False:
                    cache.pop()
                    break
        else:
            # Rule pattern matched!
            result = {"":[]}
            for number, requirement in enumerate(rule.pattern, 1):
                target_attributes = [None]
                if isinstance(requirement, tuple):
                    target_attributes = requirement[1] if isinstance(requirement[1], list) else [requirement[1]]
                for target_attribute in target_attributes:
                    intermediate_result = cache[number].result
                    attribute_transformer = None
                    if isinstance(target_attribute, tuple):
                        target_attribute, attribute_transformer = target_attribute[0], target_attribute[1]
                    if isinstance(attribute_transformer, str):
                        if isinstance(intermediate_result, dict):
                            intermediate_result = intermediate_result.get(attribute_transformer, None)
                        elif hasattr(intermediate_result, attribute_transformer):
                            intermediate_result = getattr(intermediate_result, attribute_transformer)
                    elif callable(attribute_transformer):
                        intermediate_result = attribute_transformer(intermediate_result)
                    if target_attribute == None:
                        set_or_append(result, "", intermediate_result)
                    elif target_attribute == "":
                        if isinstance(intermediate_result, dict):
                            for key, value in intermediate_result.items():
                                set_or_append(result, key, value)
                        else:
                            raise Exception("Cannot insert non-dictionary into current object at rule [%s]" % key )
                    else:
                        set_or_append(result, target_attribute, intermediate_result)
            state_reference[0] = cache[-1].state_reference[0] # Override parser state of caller function
            if rule.target_class == {}:
                return result, True
            elif rule.target_class == []:
                return result[""], True
            elif rule.target_class == "":
                return "".join([str(value) for value in result[""]]), True
            elif callable(rule.target_class):
                object_result = rule.target_class()
                for key, value in result.items():
                    if key:
                        setattr(object_result, key, value)
                return object_result, True
            else:
                return result[""][0] if len(result[""]) == 1 else result[""] or None, True
    return None, False
# Use this
def parse(language: Language, input: str):
    return parse_ex(language.rules, language.root_rule, [ParserState(tokenize(language.token_class, input))] )[0]

# Visualizer
def print_ast(ast, indent=None):
    if not indent:
        print("<root> = ", end="")
        indent = 0
    if isinstance(ast, Token):
        print( "[" + str(ast.type) + "] = '" + ast.content + "'")
    elif isinstance(ast, AST):
        print( "[" + ast.__class__.__name__ + "]")
        for attribute, value in vars(ast).items():
            print("    "*indent + "    ." + attribute + " = ", end="")
            print_ast(value, indent+1)
    elif ast == []:
        print("[]")
    elif isinstance(ast, list):
        print("[")
        for number, value in enumerate(ast, 1):
            print("    "*indent + "    ." + str(number) + " = ", end="")
            print_ast(value, indent+1)
        print("    "*indent + "]")
    else:
        print(ast)
