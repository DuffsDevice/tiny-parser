from .. import Token, Language

json = Language({
    "0.1": (eval, (Token.NUMBER, (None, "value"))),
    "0.2": (None, (Token.STRING, (None, "value"))),
    "0.3": ("#", Token.LEFT_CURLY_BRACKET, ("1.", "#"), Token.RIGHT_CURLY_BRACKET),
    "0.4": ("#", Token.LEFT_SQUARE_BRACKET, ("3.", "#"), Token.RIGHT_SQUARE_BRACKET),

    "1.0": ({}, ("2.", ""), Token.COMMA, ("1.", "")),
    "1.1": ({}, ("2.", "")),
    "1.2": {},

    "2.0": ({}, (Token.STRING, (None, "value")), Token.COLON, ("0.", (0, "value"))),

    "3.0": ([], "0.", (Token.COMMA, []), "3."),
    "3.1": ([], "0."),
    "3.2": [],
})
