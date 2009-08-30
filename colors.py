#!/usr/bin/env python

LIGHTBLACK =     "\x1B[30;1m"
LIGHTRED =       "\x1B[31;1m"
LIGHTGREEN =     "\x1B[32;1m"
LIGHTYELLOW =    "\x1B[33;1m"
LIGHTBLUE =      "\x1B[34;1m"
LIGHTMAGENTA =   "\x1B[35;1m"
LIGHTCYAN =      "\x1B[36;1m"
LIGHTWHITE =     "\x1B[37;1m"
BLACK =     "\x1B[30;22m"
RED =       "\x1B[31;22m"
GREEN =     "\x1B[32;22m"
YELLOW =    "\x1B[33;22m"
BLUE =      "\x1B[34;22m"
MAGENTA =   "\x1B[35;22m"
CYAN =      "\x1B[36;22m"
WHITE =     "\x1B[37;22m"
CLEAR =     "\x1B[0m"

colors = {
    'LIGHTBLACK' : LIGHTBLACK,
    'LIGHTRED' : LIGHTRED,
    'LIGHTGREEN' : LIGHTGREEN,
    'LIGHTYELLOW' : LIGHTYELLOW,
    'LIGHTBLUE' : LIGHTBLUE,
    'LIGHTMAGENTA' : LIGHTMAGENTA,
    'LIGHTCYAN' : LIGHTCYAN,
    'LIGHTWHITE' : LIGHTWHITE,
    'BLACK' : BLACK,
    'RED' : RED,
    'GREEN' : GREEN,
    'YELLOW' : YELLOW,
    'BLUE' : BLUE,
    'MAGENTA' : MAGENTA,
    'CYAN' : CYAN,
    'WHITE' : WHITE,
    'CLEAR' : CLEAR,
}

nocolors = {
    'LIGHTBLACK' : "",
    'LIGHTRED' : "",
    'LIGHTGREEN' : "",
    'LIGHTYELLOW' : "",
    'LIGHTBLUE' : "",
    'LIGHTMAGENTA' : "",
    'LIGHTCYAN' : "",
    'LIGHTWHITE' : "",
    'BLACK' : "",
    'RED' : "",
    'GREEN' : "",
    'YELLOW' : "",
    'BLUE' : "",
    'MAGENTA' : "",
    'CYAN' : "",
    'WHITE' : "",
    'CLEAR' : "",
}


if __name__ == "__main__":
    for name,color in colors.iteritems():
        print color, name, CLEAR
    
