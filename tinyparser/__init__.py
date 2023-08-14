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
class input_cursor:
    def __init__(self, index=1, line=1, column=1):
        self.index = index
        self.line = line
        self.column = column
def take_from_input(input, count, cursor:input_cursor, regex=re.compile(r"\r\n|\r|\n")):
    result = input_cursor(cursor.index + count, cursor.line, cursor.column + count)
    for match in regex.finditer(input, endpos=count):
        result.line += 1
        result.column = count - match.end() + 1
    return input[:count], input[count:], result

# Standard Tokenization Scheme
@inheritable_enum
class TokenType(Enum):
    def __init__(self, pattern):
        self.pattern = re.compile(pattern)
    def __call__(self, *args, **kwargs):
        return InputToken(self, *args, **kwargs)
    @classmethod
    def exactly(cls, value):
        for token_type in cls:
            if token_type.pattern.match(value):
                return token_type(value)
        raise Exception("The string %s does not correspond to any token type in Enum %s." % (value, cls))
class Token(TokenType):
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
    STRING                  = r'^"(?P<value>([^"]|\\")*)"'
    UNKNOWN                 = r'^.'

# Abstract Syntax Tree Base Class
class AST:
    def __init__(self, *args, **kwargs):
        if args:
            setattr(self, "children", list(args))
        for key, value in kwargs.items():
            if key:
                setattr(self, key, value)

# Definition of a Language
class Language:
    def __init__(self, rules, token_class=Token, root_rule="root."
        , strip_whitespaces=" \t\r\n", default_target=AST

        # List of "target" types/values for which the intermediate dictionary is enriched with...
        , make_grammar_rule_available=[AST] # The name of the matching rule as "matching_rule"
        , make_input_tokens_available=[AST]    # The list of input tokens as "input_tokens"
    ):
        self.rules = rules
        self.token_class = token_class
        self.root_rule = root_rule
        self.strip_whitespaces = strip_whitespaces
        self.default_target = default_target
        self.make_grammar_rule_available = make_grammar_rule_available
        self.make_input_tokens_available = make_input_tokens_available

# Tokenizer
class InputToken:
    def __init__(self, type: TokenType, value=None, space_before=None, position=input_cursor, end=input_cursor):
        self.type = type
        self.verbatim = self.value = value
        self.space_before = space_before
        self.position = position
        self.end = end
def tokenize(language: Language, input: str):
    result = []
    space_before = None
    position = input_cursor()
    if language.strip_whitespaces:
        new_input = input.lstrip(language.strip_whitespaces)
        space_before, input, position = take_from_input(input, len(input)-len(new_input), position)
    while input:
        for token_type in language.token_class:
            if match := token_type.pattern.match(input):
                start = position
                _, input, position = take_from_input(input, match.end(), position)
                token = InputToken(token_type, match.group(), space_before, start, position)
                for key, value in match.groupdict().items():
                    setattr(token, key, value) # Add all named groups to the token as attributes
                result.append(token)
                break
        else:
            raise Exception("No Token matched at: %.7s..." % input)
        if language.strip_whitespaces:
            new_input = input.lstrip(language.strip_whitespaces)
            space_before, input, position = take_from_input(input, len(input)-len(new_input), position)
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
    def take_token(self, token: InputToken):
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
    def delta_tokens(self, other_state):
        return self.token_list[self.current_index:other_state.current_index]

# Parser
def parse_ex(language: Language, rule_path: str, state_reference):
    class Step:
        def __init__(self, state_reference, requirement=None, destination=None, result=None):
            self.state_reference = state_reference
            self.requirement = requirement
            self.destination = destination
            self.result = result
    history = [Step(state_reference, None, None)] # In order to enable recursion to reference the last step
    identification = None

    # Determine viable rules
    viable_rules = [(key, rule) for key, rule in language.rules.items() if key.startswith(rule_path)]

    # See, if any rule matches
    for key, rule in viable_rules:

        # rule is "(target, steps...)" or "[steps...]" just "target"
        if isinstance(rule, list):
            target = language.default_target
            steps = rule
        elif isinstance(rule, tuple):
            target, *steps = rule
        else:
            target = rule
            steps = []
        identification = key

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
                    elif isinstance(option, InputToken): # Requires a token with the supplied type
                        history[-1].result, success = history[-1].state_reference[0].take_token(option)
                    elif isinstance(option, str): # Strings require matching of other rules
                        history[-1].result, success = parse_ex(language, option, history[-1].state_reference)
                    else:
                        raise Exception("Unknown requirement in rule [%s] of type: %s" % (key, type(option)))

                    # The option did not match
                    if not success:
                        history.pop() # Destroy the hypothetical step in history
                        continue
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

            # Enrich with debug information?
            def check_entry(entry):
                if target == entry or isinstance(target, entry):
                    return True
                return issubclass(target, entry) if isclass(target) and isclass(entry) else False
            if True in [check_entry(entry) for entry in language.make_input_tokens_available]:
                result["input_tokens"] = state_reference[0].delta_tokens( history[-1].state_reference[0] )
            if True in [check_entry(entry) for entry in language.make_grammar_rule_available]:
                result["grammar_rule"] = (rule_path, identification)

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

            # h) return just the target
            elif target is not None:
                return target, True

            # h) Return the result or the results that didn't have an explicit destination (list or plain value)
            return result[None][0] if len(result[None]) == 1 else result[None] or None, True

    return None, False

# Use this
def parse(language: Language, input: str):
    parser_state = [ParserState(tokenize(language, input))]
    result = parse_ex(language, language.root_rule, parser_state)[0]
    return None if parser_state[0].current_token else result

# AST Visualizer
def print_ast(value, indent=None):
    if not indent:
        print("<root> = ", end="")
        indent = 0
    if isinstance(value, InputToken):
        print( "[" + str(value.type) + "] = '" + value.value + "'")
    elif isinstance(value, AST):
        if type(value) != AST:
            if hasattr(value, "grammar_rule"):
                print( value.__class__.__name__ + " <- [" + value.grammar_rule[1] + '] <- "' + value.grammar_rule[0] + '"')
            else:
                print( value.__class__.__name__)
        elif hasattr(value, "grammar_rule"):
            if value.grammar_rule[0] == value.grammar_rule[1]:
                print( '[' + value.grammar_rule[0] + ']')
            else:
                print( '[' + value.grammar_rule[0] + ' > ' + value.grammar_rule[1] + ']')
        else:
            print("Abstract Syntax Tree")
        for attribute, value in vars(value).items():
            if attribute == "grammar_rule":
                continue
            print("    "*indent + "    ." + attribute + " = ", end="")
            if attribute == "input_tokens" and value:
                print("from (%d:%d) to (%d:%d)" % (
                    value[0].position.line
                    , value[0].position.column
                    , value[-1].end.line
                    , value[-1].end.column
                ))
            else:
                print_ast(value, indent+1)
    elif value == []:
        print("[]")
    elif isinstance(value, list):
        print("[")
        for number, value in enumerate(value, 1):
            print("    "*indent + "    ." + str(number) + " = ", end="")
            print_ast(value, indent+1)
        print("    "*indent + "]")
    elif isinstance(value, str):
        print('"%s"' % value)
    else:
        print(value)
