from enum import Enum
from extendableenum import inheritable_enum
import re

# Tokenizer
@inheritable_enum
class TokenType(Enum):
    def __init__(self, pattern):
        self.pattern = re.compile(pattern)
class Token:
    def __init__(self, type: TokenType, content: str):
        self.type = type
        self.content = content
def tokenize(token_class, input: str):
    result = []
    while input:
        match = None
        for token_type in token_class:
            if match := token_type.pattern.match(input):
                result.append(Token(token_type, match.group()))
                input = input[len(match.group()):]
                break
        else:
            raise Exception("No Token matched at: %.7s..." % input)
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
    if orig_value:
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
        self.pattern = pattern

# Parser
def parse_ex(language:dict, rule_path: str, state_reference):
    class CacheEntry:
        def __init__(self, state_reference, requirement=None, result=None):
            self.state_reference = state_reference
            self.requirement = requirement
            self.result = result
    cache = [CacheEntry(state_reference, None, None)]
    viable_rules = [rule for key, rule in language.items() if key.startswith(rule_path)]
    for rule in viable_rules:
        result_dict = {}
        anonymous_results = []
        cache_usage = 1
        for requirement in rule.pattern:
            target_attributes = None
            if isinstance(requirement, tuple):
                requirement, target_attributes = requirement[0], requirement[1] if isinstance(requirement[1], list) else [requirement[1]]
            # Check if we can use the cache for this requirement
            cache_usable = False
            if len(cache) > cache_usage:
                if cache[cache_usage].requirement is requirement:
                    cache_usable = True
                else:
                    cache = cache[:cache_usage+1] # Truncate cache to prefix we can re-use
            if not cache_usable:
                cache.append(CacheEntry([cache[-1].state_reference[0].fork()], requirement)) # Create new cache layer
                if isinstance(requirement, TokenType):
                    cache[-1].result = cache[-1].state_reference[0].take(requirement)
                elif isinstance(requirement, list):
                    cache[-1].result = cache[-1].state_reference[0].take(*requirement)
                elif isinstance(requirement, str): # Referring to another rule
                    cache[-1].result = parse_ex(language, requirement, cache[-1].state_reference)
                if not cache[-1].result:
                    cache.pop()
                    break
            if isinstance(target_attributes, list):
                if target_attributes and isinstance(cache[cache_usage].result, dict):
                    for key, value in cache[cache_usage].result.items():
                        set_or_append(result_dict, key, value)
                else:
                    for target_attribute in target_attributes:
                        set_or_append(result_dict, target_attribute, cache[cache_usage].result)
            else:
                anonymous_results.append(cache[cache_usage].result)
            cache_usage += 1
        else:
            state_reference[0] = cache[-1].state_reference[0] # Override parser state of caller function
            if rule.target_class:
                object_result = rule.target_class()
                for key, value in result_dict.items():
                    setattr(object_result, key, value)
                return object_result
            elif result_dict:
                return result_dict
            elif anonymous_results:
                return anonymous_results[0] if len(anonymous_results) == 1 else anonymous_results
    return None
def parse(token_class, language:dict, input: str, root_rule="root"):
    return parse_ex(language, root_rule, [ParserState(tokenize(token_class, input))] )

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
    elif isinstance(ast, list):
        print( "[" if list else "[]" )
        for number, value in enumerate(ast, 1):
            print("    "*indent + "    ." + str(number) + " = ", end="")
            print_ast(value, indent+1)
    else:
        print( "None")
