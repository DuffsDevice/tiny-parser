import tinyparser
import tinyparser.language as language

#tinyparser.print_ast( tinyparser.parse( language.regex, r"^[A-Za-z0-9._+\-\']+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$" ) )
#tinyparser.print_ast( tinyparser.parse( language.cpp, r'3;4;{"Hello";4;}' ) )
tinyparser.print_ast( tinyparser.parse( language.json, '''{
  "errors" : [ {
    "status" : 404,
    "message" : "oid batch doesn't exist."
  } ]
}''') )
