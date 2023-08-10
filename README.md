# tiny-parser
[![Licence](https://img.shields.io/badge/licence-BSD--3-e20000.svg)](https://github.com/DuffsDevice/tiny-parser/blob/master/LICENCE)

tiny-parser is a python library enabling you to write arbitrary use-case specific parsers within a couple of minutes.
It comes with a collection of language defintions, that I started to write.

## Examples

### JSON
In this example, the goal would be to write a parser that can read a json file and convert it into the corresponding python object.
The language definition using tiny-parser looks like this:

```python
from tinyparser import Rule, StandardToken, Language

json = Language({
    "0.1": (eval, (StandardToken.NUMBER, (None, "value"))),
    "0.2": (None, (StandardToken.STRING, (None, "value"))),
    "0.3": ("#", StandardToken.LEFT_SQUARE_BRACKET, ("1.", "#"), StandardToken.RIGHT_SQUARE_BRACKET),
    "0.4": ("#", StandardToken.LEFT_CURLY_BRACKET, ("2.", "#"), StandardToken.RIGHT_CURLY_BRACKET),
    "1.1.1": ([], "0.", (StandardToken.COMMA, []), "1.1."),
    "1.1.2": ([], "0."),
    "1.2": [],
    "2.1.0": ({}, ("3.", ""), StandardToken.COMMA, ("2.1.", "")),
    "2.1.1": ({}, ("3.", "")),
    "2.2": {},
    "3.0": ({}, (StandardToken.STRING, (None, "value")), StandardToken.COLON, ("0.", (0, "value"))),
})
```
That's it. Nothing more.

If you'd like to parse some json now, you can do this through:
```python
print(tinyparser.parse(json, '{"Hello": ["test", 4, {"what":30}]}'))
# Output: {'Hello': ['test', 4, {'what': 30}]}
```

## Documentation

### The Grammar Dictionary
The first constructor argument to the class `tinyparser.Language` is the grammar - a python dictionary containing all grammar rules.
Each dictionary key maps a specific identification to a rule definition.

```python
grammmar = {
    "0.1": (foo, bar)
    , "1.1": (faz, baz)
    , "1.2": (far, boo)
    # And so on...
}
```

#### Rule Identifications
In principle, you can name your rules the way you like. For most cases however, you'll want a hierachical key structure.
By doing this, you can reference groups of rules and thus enable disjunctions.
This is, because tiny-parser rule references will match every rule that starts with a certain prefix.
For example, a rule reference of "1." will match all rules with a dictionary key starting with "1.", such as "1.0", "1.1.1" or "1.1.2".

You would also be allowed to use words for the rule identifications, but keep in mind:
longer identifications take longer to compare (if speed should be an issue).

### Rule Definitions
Rule definitions are of the form `(target, steps...)` (a tuple containing the definition arguments).
If a rule is defined to match _nothing_ (the empty string), you may also just specify `target` (not using a tuple).

#### Steps
The precise types of targets one can specify are going to be explained in one of the next sections.
This chapter will be all about the matching steps, i.e. _what_ you can match.

Usually, language grammars come in different formats: BNF, EBNF, graphical control flow etc.
Common to all of them is, what they are made of:
a) Tokens (i.e. string content matching some part of the input), e.g. "[", "&&" or "const", and
b) References to other rules.
