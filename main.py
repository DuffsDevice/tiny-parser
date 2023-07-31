import tiny_parser
import tiny_parser.language as language

tiny_parser.print_ast( tiny_parser.parse( language.cpp, "1;{3;2;};3;" ) )
