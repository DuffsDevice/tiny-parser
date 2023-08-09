# tiny-parser
[![Licence](https://img.shields.io/badge/licence-BSD--3-e20000.svg)](https://github.com/DuffsDevice/tiny-parser/blob/master/LICENCE)

tiny-parser is a python library enabling you write arbitrary use-case specific parsers within a couple of minutes.
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
    "0.3": ("#", StandardToken.LEFT_CURLY_BRACKET, ("1.", "#"), StandardToken.RIGHT_CURLY_BRACKET),
    "0.4": ("#", StandardToken.LEFT_SQUARE_BRACKET, ("3.", "#"), StandardToken.RIGHT_SQUARE_BRACKET),
    "1.1.0": ({}, ("2.", ""), StandardToken.COMMA, ("1.1.", "")),
    "1.1.1": ({}, ("2.", "")),
    "1.2": {},
    "2.0": ({}, (StandardToken.STRING, (None, "value")), StandardToken.COLON, ("0.", (0, "value"))),
    "3.0": ([], "0.", (StandardToken.COMMA, []), "3."),
    "3.1": ([], "0."),
    "3.2": [],
})
```
That's it. Nothing more.

If you'd like to parse some json now, you can do this through:
```python
print(tinyparser.parse(json, '{"Hello": ["test", 4, {"what":30}]}'))
# Output: {'Hello': ['test', 4, {'what': 30}]}
```
