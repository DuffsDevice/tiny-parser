from enum import Enum
from inspect import isclass
from extendableenum import inheritable_enum
import re

# Miscellaneous
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
def take_from_input(input, count, line, column, regex=re.compile(r"\r\n|\r|\n")):
    column += count
    for match in regex.finditer(input, endpos=count):
        line += 1
        column = count - match.end() + 1
    return input[:count], input[count:], line, column

# Tokenizer
@inheritable_enum
class TokenType(Enum):
    def __init__(self, pattern):
        self.pattern = re.compile(pattern)
    def __call__(self, *args, **kwargs):
        return Token(self, *args, **kwargs)
class Token:
    def __init__(self, type: TokenType, value=None, space_before=None, line=None, column=None):
        self.type = type
        self.verbatim = self.value = value
        self.space_before = space_before
        self.line = line
        self.column = column
def tokenize(token_class, input: str, strip_whitespaces=None):
    result = []
    space_before = None
    line = 1
    column = 1
    if strip_whitespaces:
        new_input = input.lstrip(strip_whitespaces)
        space_before, input, line, column = take_from_input(input, len(input)-len(new_input), line, column)
    while input:
        for token_type in token_class:
            if match := token_type.pattern.match(input):
                token = Token(token_type, match.group(), space_before, line, column)
                _, input, line, column = take_from_input(input, match.end(), line, column)
                for key, value in match.groupdict().items():
                    setattr(token, key, value) # Add all named groups to the token as attributes
                result.append(token)
                break
        else:
            raise Exception("No Token matched at: %.7s..." % input)
        if strip_whitespaces:
            new_input = input.lstrip(strip_whitespaces)
            space_before, input, line, column = take_from_input(input, len(input)-len(new_input), line, column)
    return result

# Parser State
class ParserState:
    def __init__(self, token_list, current_index=0):
        self.token_list = token_list
        self.current_index = current_index
    @property
    def current_token(self):
        return self.token_list[self.current_index] if self.current_index < len(self.token_list) else None
    def take_type(self, token_type: TokenType):
        current_token = self.current_token
        if current_token and current_token.type == token_type:
            self.current_index += 1
            return current_token, True
        return None, False
    def take_token(self, token: Token):
        current_token, success = self.take_type(token.type)
        if success:
            if isinstance(token.value, str) and current_token.value == token.value:
                return current_token, True
            elif isinstance(token.value, re.Pattern) and token.value.match(current_token.value):
                return current_token, True
            else:
                self.current_index -= 1
        return None, False
    def fork(self):
        return ParserState(self.token_list, self.current_index)

# Parser
def parse_ex(rules:dict, rule_path: str, state_reference):
    class Step:
        def __init__(self, state_reference, requirement=None, destination=None, result=None):
            self.state_reference = state_reference
            self.requirement = requirement
            self.destination = destination
            self.result = result
    history = [Step(state_reference, None, None)] # In order to enable recursion to reference the last step

    # Determine viable rules
    viable_rules = [(key, rule) for key, rule in rules.items() if key.startswith(rule_path)]

    # See, if any rule matches
    for key, rule in viable_rules:

        # rule is tuple "(target, steps...)" or just "target"
        target, *steps = rule if isinstance(rule, tuple) else (rule,)

        for step_number, step in enumerate(steps, 1):

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
                        history[-1].result, success = history[-1].state_reference[0].take_type(option)
                    elif isinstance(option, Token): # Requires a token with the supplied type
                        history[-1].result, success = history[-1].state_reference[0].take_token(option)
                    elif isinstance(option, str): # Strings require matching of other rules
                        history[-1].result, success = parse_ex(rules, option, history[-1].state_reference)
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
                    elif isinstance(destination, int): # Take the nth result in the 'None' entry
                        set_or_append(result, result[None][destination], step.result)
                    elif destination != False:
                        set_or_append(result, destination, step.result)

            # Override the parser state of the parent function, so it knows where to continue parsing
            state_reference[0] = history[-1].state_reference[0]

            # a) Return the dictionary
            if isinstance(target, dict):
                if result[None] == [] or (None not in target): # If we didn't collect elements without destination, remove the key 'None'
                    return {key: value for key, value in result.items() if key is not None}, True
                else:
                    return result, True

            # b) Return the results that didn't have an explicit destination (as list)
            elif target == []:
                return result[None], True

            # c) Return the results that didn't have an explicit destination (converted to string and concatenated)
            elif target == "":
                return "".join([str(value) for value in result[None]]), True

            # d) Return the field with the supplied name
            elif isinstance(target, str):
                return result.get(target, None), True

            # e) Construct an object of the supplied class and pass the dict as named arguments to constructor
            elif isclass(target) and "__init__" in vars(target):
                return target(*result[None], **{key: value for key, value in result.items() if key is not None}), True

            # f) Create an object of the supplied class and let the dictionary set its attributes
            elif isclass(target):
                object_result = target()
                for key, value in result.items():
                    if key:
                        setattr(object_result, key, value)
                return object_result, True

            # g) Call a function with the resulting dictionary as named parameters
            elif callable(target):
                return target(*result[None], **{key: value for key, value in result.items() if key is not None}), True

            # h) Return the result or the results that didn't have an explicit destination (list or plain value)
            return result[None][0] if len(result[None]) == 1 else result[None] or None, True

    return None, False

# Visualizer
def print_ast(ast, indent=None):
    if not indent:
        print("<root> = ", end="")
        indent = 0
    if isinstance(ast, Token):
        print( "[" + str(ast.type) + "] = '" + ast.value + "'")
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
    elif isinstance(ast, str):
        print('"%s"' % ast)
    else:
        print(ast)

# Abstract Syntax Tree Classes
class AST: pass
class StandardToken(TokenType):
    NEWLINE                 = r"^\r\n|\r|\n"
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
    NUMBER                  = r'^(\+|-)?([1-9][0-9]*(\.[0-9]*)?\b|\.[0-9]+\b|0\b)'
    STRING                  = r'^"(?P<value>([^"]|\\")+)"'
class Language:
    def __init__(self, rules, token_class=StandardToken, root_rule="0.", strip_whitespaces=" \t\r\n"):
        self.rules = rules
        self.token_class = token_class
        self.root_rule = root_rule
        self.strip_whitespaces = strip_whitespaces

# Use this
def parse(language: Language, input: str):
    parser_state = [ParserState(tokenize(language.token_class, input, language.strip_whitespaces))]
    result = parse_ex(language.rules, language.root_rule, parser_state )[0]
    return None if parser_state[0].current_token else result
