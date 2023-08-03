from enum import Enum
from inspect import isclass
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
    def take(self, token_type):
        current_token = self.current_token
        if current_token and current_token.type == token_type:
            self.current_index += 1
            return current_token, True
        return None, False
    def fork(self):
        return ParserState(self.token_list, self.current_index)

def ensure_list(value):
    return value if isinstance(value, list) else [value]
def set_or_append(dict, key, value):
    orig_value = dict.get(key, None)
    if orig_value is not None:
        if value is not None:
            value = ensure_list(value)
            orig_value = ensure_list(orig_value)
            dict[key] = [*orig_value, *value]
    else:
        dict[key] = value

# Abstract Syntax Tree Classes
class AST: pass
class Rule:
    def __init__(self, target, *steps ):
        self.target = target
        self.steps = steps if steps else []
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
    class Step:
        def __init__(self, state_reference, requirement=None, destination=None, result=None):
            self.state_reference = state_reference
            self.requirement = requirement
            self.destination = destination
            self.result = result
    history = [Step(state_reference, None, None)] # In order to enable recursion to reference the last step

    # Determine viable rules
    rules = [(key, rule) for key, rule in language.items() if key.startswith(rule_path)]

    # See, if any rule matches
    for key, rule in rules:
        for step_number, step in enumerate(rule.steps, 1):

            # A step can be a tuple "(step, destination)"
            destination = None
            if isinstance(step, tuple):
                step, destination = step[0], step[1]

            # The step can actually be a list "(step-option-1, step-option-2, etc.)"
            for option in ensure_list(step):

                # Each step option can itself be a tuple "(step, destination-override)"
                actual_destination = destination
                if isinstance(option, tuple):
                    option, actual_destination = option[0], option[1] # You can also specify a destination per option

                # Determine, whether we have a saved history of the current step being matched
                if len(history) > step_number and history[step_number].requirement is option:
                    history[step_number].destination = actual_destination # The destination might change, but we don't need to reexecute
                else:
                    # Rewrite history from the present forwards
                    history = [
                        *history[:step_number+1] # history before this step
                        , Step([history[-1].state_reference[0].fork()], option, actual_destination)
                    ]

                    # Match according to type of requirement
                    if isinstance(option, TokenType): # Requires a token of the supplied type
                        history[-1].result, success = history[-1].state_reference[0].take(option)
                    elif isinstance(option, str): # Strings require mathcing of other rules
                        history[-1].result, success = parse_ex(language, option, history[-1].state_reference)
                    else:
                        raise Exception("Unknown requirement in rule [%s] of type: %s" % (key, type(option)))

                    # The option did not match
                    if not success:
                        history.pop() # Destroy the hypothetical step in history
                        continue

                # The option matched
                break

            else:
                break # If we didn't find one (no inner "break" was activated)
        else: # The whole rule matched!

            result = {None:[]}
            for step in history[1:]:
                for destination in ensure_list(step.destination):

                    # The destination can actually be a tuple "(destination, transformer)"
                    transformer = None
                    if isinstance(destination, tuple):
                        destination, transformer = destination[0], destination[1]

                        # Apply the transformer to result depending on the type of transformer
                        if isinstance(transformer, str):
                            if isinstance(step.result, dict):
                                step.result = step.result.get(transformer, None)
                            elif hasattr(step.result, transformer):
                                step.result = getattr(step.result, transformer)
                        elif callable(transformer):
                            step.result = transformer(step.result)

                    # Send to destination
                    if destination == None:
                        set_or_append(result, None, step.result)
                    elif destination == "":
                        if isinstance(step.result, dict):
                            for key, value in step.result.items():
                                set_or_append(result, key, value)
                        else:
                            raise Exception("Cannot insert non-dictionary into current object at rule [%s]" % key )
                    elif destination != False:
                        set_or_append(result, destination, step.result)

            # Override the parser state of the parent function, so it knows where to continue parsing
            state_reference[0] = history[-1].state_reference[0]

            # a) Return the dictionary
            if isinstance(rule.target, dict):
                if result[None] == []: # If we didn't collect elements without destination, remove the key 'None'
                    return {key: value for key, value in result.items() if key is not None}, True
                else:
                    return result, True

            # b) Return the results that didn't have an explicit destination (as list)
            elif rule.target == []:
                return result[None], True

            # c) Return the results that didn't have an explicit destination (converted to string and concatenated)
            elif rule.target == "":
                return "".join([str(value) for value in result[None]]), True

            # d) Construct an object of the supplied class and pass the dict as named arguments to constructor
            elif isclass(rule.target) and "__init__" in vars(rule.target):
                return rule.target(*result[None], **{key: value for key, value in result.items() if key is not None}), True

            # e) Create an object of the supplied class and let the dictionary set its attributes
            elif isclass(rule.target):
                object_result = rule.target()
                for key, value in result.items():
                    if key:
                        setattr(object_result, key, value)
                return object_result, True

            # f) Call a function with the resulting dictionary as named parameters
            elif callable(rule.target):
                return rule.target(*result[None], **{key: value for key, value in result.items() if key is not None}), True

            # b) Return the result or the results that didn't have an explicit destination (list or plain value)
            return result[None][0] if len(result[None]) == 1 else result[None] or None, True

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
