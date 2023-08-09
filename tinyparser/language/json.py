from .. import StandardToken, Language

json = Language({
    "0.1": (eval, (StandardToken.NUMBER, (None, "value"))),
    "0.2": (None, (StandardToken.STRING, (None, "value"))),
    "0.3": ("#", StandardToken.LEFT_CURLY_BRACKET, ("1.", "#"), StandardToken.RIGHT_CURLY_BRACKET),
    "0.4": ("#", StandardToken.LEFT_SQUARE_BRACKET, ("3.", "#"), StandardToken.RIGHT_SQUARE_BRACKET),

    "1.0": ({}, ("2.", ""), StandardToken.COMMA, ("1.", "")),
    "1.1": ({}, ("2.", "")),
    "1.2": {},

    "2.0": ({}, (StandardToken.STRING, (None, "value")), StandardToken.COLON, ("0.", (0, "value"))),

    "3.0": ([], "0.", (StandardToken.COMMA, []), "3."),
    "3.1": ([], "0."),
    "3.2": [],
})
