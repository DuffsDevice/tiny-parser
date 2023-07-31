import tiny_parser
import tiny_parser.language as language

#tiny_parser.print_ast( tiny_parser.parse( language.regex, r"^[A-Za-z0-9._+\-\']+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$" ) )
tiny_parser.print_ast( tiny_parser.parse( language.cpp, r'3;4;{"Hello";4;}' ) )
