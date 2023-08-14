# tiny-parser
[![Licence](https://img.shields.io/badge/licence-BSD--3-e20000.svg)](https://github.com/DuffsDevice/tiny-parser/blob/master/LICENCE)

tiny-parser enables you to **write arbitrary use-case specific parsers within minutes**.

It ships with a collection of predefined language defintions I started to write.

## Example: Parsing JSON
Defining the grammar of JSON using tiny-parser looks like this:

```python
from tinyparser import Rule, Token, Language

json = Language({
    "root.number.": [Token.NUMBER],
    "root.string.": [Token.STRING],
    "root.list.": [Token.LEFT_SQUARE_BRACKET, "list.", Token.RIGHT_SQUARE_BRACKET],
    "root.object.": [Token.LEFT_CURLY_BRACKET, "object.", Token.RIGHT_CURLY_BRACKET],
    "list.nonempty.multiple.": ["root.", Token.COMMA, "list.nonempty."],
    "list.nonempty.single.": ["root."],
    "list.empty.": [],
    "object.nonempty.multiple.": ["attribute.", Token.COMMA, "object.nonempty."],
    "object.nonempty.single.": ["attribute."],
    "object.empty.": [],
    "attribute.": [Token.STRING, Token.COLON, "root."],
})
```
**That's it!**


If you'd like to parse some json now, you can do this through:
```python
# Parse input into ast
ast = tinyparser.parse(json, '{"Hello": "World"}')

# Inspection:
tinyparser.print_ast(ast)

""" Output:
<root> = [root. > root.object.]
    .children = [
        .1 = [Token.LEFT_CURLY_BRACKET] = '{'
        .2 = [object. > object.nonempty.single.]
            .children = [
                .1 = [attribute.]
                    .children = [
                        .1 = [Token.STRING] = 'Hello'
                        .2 = [Token.COLON] = ':'
                        .3 = [root. > root.string.]
                            .children = [
                                .1 = [Token.STRING] = 'World'
                            ]
                    ]
            ]
        .3 = [Token.RIGHT_CURLY_BRACKET] = '}'
    ]
"""
```

While this parsing result has all necessary information, it also contains unnecessary information.
To improve this, tiny-parser allows you to **post-process intermediate parsing results** to enable the pretty datastructure of your choice.
Whether its custom classes, dictionaries, lists... you name it.

Since JSON is primarily a data-description language, why shouldn't we immediately return the content as python datastructure!?
In order to do this, our language grammar needs some meta information on how
to process each rule (don't worry, everything you'll see will be explained later):

```python
json = Language({
    "root.number.": (eval, (Token.NUMBER, (None, "value"))),
    "root.string.": (None, (Token.STRING, (None, "value"))),
    "root.list.": ("#", Token.LEFT_SQUARE_BRACKET, ("list.", "#"), Token.RIGHT_SQUARE_BRACKET),
    "root.object.": ("#", Token.LEFT_CURLY_BRACKET, ("object.", "#"), Token.RIGHT_CURLY_BRACKET),
    "list.nonempty.multiple.": ([], "root.", (Token.COMMA, []), "list.nonempty."),
    "list.nonempty.single.": ([], "root."),
    "list.empty.": ([]),
    "object.nonempty.multiple.": ({}, ("attribute.", ""), Token.COMMA, ("object.nonempty.", "")),
    "object.nonempty.single.": ({}, ("attribute.", "")),
    "object.empty.": ({}),
    "attribute.": ({}, (Token.STRING, (None, "value")), Token.COLON, ("root.", 0)),
})
```

Now we can do:
```python
# Prints: {'Hello': 'World'}
print( tinyparser.parse(json, '{"Hello" : "World"}') )
```

# Documentation

## 1.   Specifying the Grammar
The first constructor argument to the class `tinyparser.Language` is the grammar - a python dictionary containing all grammar rules.
Each dictionary key maps a specific identification to a rule definition.

```python
grammmar = {
    "root.option-A": ["number."]
    , "root.option-B": ["string."]
    , "number.": [Token.NUMBER]
    , "string.": [Token.STRING]
    # And so on...
}
```

### 1.1 Rule Identifications
In principle, you can name your rules the way you like. For most cases however, you'll want a hierachical key structure.
By doing this, you can reference groups of rules and thus enable disjunctions.
This is, because tiny-parser rule references will match every rule that starts with a certain prefix.
For example, a rule reference of `"expression."` will match all rules with a dictionary key starting with `expression.` , such as `expression.empty.` , `expression.nonempty.single.` or `expression.nonemtpy.multiple.` .

By convention, all rule identifications should end in the separation character you use (in our case `.`). This is, because references should not have to care, if they reference a group of rules or a single rule (separation of _Interface_ from _Implementation_).

**Note:** For educational purposes, all rule identifications are words. When you ship your code and/or  parsing speed is needed, numbers would suite the purpose just as well, but are quicker in parsing time. That is, the shorter your identifications, the quicker tiny-parser can resolve each reference.

### 1.2 Rule Definitions
Rule definitions are either of the form `[steps...]` or `(target, steps...)`.
If a rule is defined to match _nothing_ (the empty string) and therefore has no steps, you may just specify `target` (neither wrapped inside a tuple nor list). I.e., you may as well pass `None` .

### 1.3 Steps
This chapter will be all about the matching steps, i.e. _what_ you can match.

Usually, language grammars come in different formats: BNF, EBNF, graphical control flow etc.
Common to all of them is, what they are made of:
1. **Tokens** (i.e. string content matching some part of the input), e.g. `}` or `&&` or `const`, and
2. **References** to other rules.

Essentially, the "steps" you will pass as arguments to the definition of each rule will mostly consist of these two things,
references to other rules and tokens that you want to read from the input.

### 1.4 Parsing Tokens
tiny-parser will parse your input in two stages: 1. tokenization, 2. rule matching.
Tokenization is a common preparation step in parsing. Most compilers and source code analysis tools do this.
Breaking up the input into it's atomic components (tokens) happens, because it eases the process of rule matching immensely.

Tokenization happens linearly from the beginning of the input to the end.
You can compare this process to the process of identifying the "building blocks" of written english within a given sentence:
1. **words** (made of characters of the english alphabet, terminated by everything that's not of the english alphabet),
2. **dots**,
3. **dashes**,
4. **parentheses**,
5. **numbers** (starting with a digit, terminated by everything thats neither a number nor a decimal dot).

You can probably already see, how this eases the further comprehension of some input string.

tiny-parser by default employs a basic tokenization that will suffice for many occasions.
It's defined by the enum `tinyparser.Token`, deriving from the class `tinyparser.TokenType`.

This basic tokenization will allow you to match certain tokens, just by passing the enum member of the token type you'd like to match.
For example the rule :

```python
"root.parentheses.empty.": [Token.LEFT_PARENTHESIS, Token.RIGHT_PARENTHESIS]
```
has two steps that together match "()", even with whitespaces in between "(  )".

### 1.5 Matching exact Tokens
In some cases, merely specifying the type of token that you want to match is not precise enough.
To match a token with specific content, for example the identifier `func`, you can do this with the function `exactly`:

```python
"root.function.": [Token.exactly("func"), Token.IDENTIFIER]
```

### 1.6 Referencing Rules

You reference rules (or groups of rules) simply by writing their identification or common prefix as a string. For parsing a simple list of numbers, each separated by a comma, you'd write:

```python
grammmar = {
    "list.nonempty.multiple.": ["list-element.", Token.COMMA, "list.nonempty."]
    , "list.nonempty.single.": ["list-element."]
    , "list.nonempty.single.": []
    , "list-element.": [Token.NUMBER]
}
```

### 1.7 Step Alternatives

### 1.8 Step Destinations

### 1.9 Step Result Transformers

### 1.10 Custom Targets

The `target` of a rule specifies its return value once its matched of the rule - so to speak.

# Reference

### Complete list of Standard Tokens

| Token Name  | Regular Expression  |
| ----------- | ------------------ |
| NEWLINE | \\r\\n\|\\r\|\\n |
| DOUBLE_EQUAL | == |
| EXCLAMATION_EQUAL | != |
| LESS_EQUAL | <= |
| GREATER_EQUAL | >= |
| AND_EQUAL | &= |
| OR_EQUAL | \|= |
| XOR_EQUAL | \^= |
| PLUS_EQUAL | \+= |
| MINUS_EQUAL | -= |
| TIMES_EQUAL | \*= |
| DIVIDES_EQUAL | /= |
| DOUBLE_AND | && |
| DOUBLE_OR | \\\|\\\| |
| DOUBLE_PLUS | \\+\\+ |
| DOUBLE_MINUS | -- |
| PLUS | \\+ |
| MINUS | - |
| TIMES | \* |
| DIVIDES | / |
| POWER | \\^ |
| LESS | < |
| GREATER | > |
| LEFT_PARENTHESIS | \\( |
| RIGHT_PARENTHESIS | \\) |
| LEFT_SQUARE_BRACKET | \\[ |
| RIGHT_SQUARE_BRACKET | \\] |
| LEFT_CURLY_BRACKET | \\{ |
| RIGHT_CURLY_BRACKET | \\} |
| SEMICOLON | ; |
| COLON | : |
| COMMA | , |
| HAT | \\^ |
| DOT | \\. |
| IDENTIFIER | [a-zA-Z_][a-zA-Z0-9_]*\b |
| NUMBER | (\\+\|-)?([1-9][0-9]*(\\.[0-9]*)?\\b\|\\.[0-9]+\\b\|0\\b) |
| STRING | "(?P\<value\>([^"]\|\\\\")+)"
| UNKNOWN | .
