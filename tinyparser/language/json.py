from .. import Token, Language

json = Language({
    "0.1": (eval, (Token.NUMBER, (None, "value"))),
    "0.2": (None, (Token.STRING, (None, "value"))),
    "0.3": ("#", Token.LEFT_SQUARE_BRACKET, ("1.", "#"), Token.RIGHT_SQUARE_BRACKET),
    "0.4": ("#", Token.LEFT_CURLY_BRACKET, ("2.", "#"), Token.RIGHT_CURLY_BRACKET),

    "1.1.1": ([], "0.", (Token.COMMA, []), "1.1."),
    "1.1.2": ([], "0."),
    "1.2": [],

    "2.1.1": ({}, ("3.", ""), Token.COMMA, ("2.1.", "")),
    "2.1.2": ({}, ("3.", "")),
    "2.2": {},

    "3.0": ({}, (Token.STRING, (None, "value")), Token.COLON, ("0.", (0, "value"))),
}, Token, "0.")