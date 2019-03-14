DICT_LETTER = {
    'A' : 1,#
    'B' : 5,#
    'C' : 4,#
    'D' : 3,#
    'E' : 1,#
    'F' : 5,#
    'G' : 5,#
    'H' : 5,#
    'I' : 1,#
    'J' : 10,#
    'K' : 10,#
    'L' : 2,#
    'M' : 4,#
    'N' : 1,#
    'O' : 1,#
    'P' : 4,#
    'Q' : 10,#
    'R' : 1,#
    'S' : 1,#
    'T' : 1,#
    'U' : 2,#
    'V' : 8,#
    'W' : 10,#
    'X' : 10,#
    'Y' : 10,#
    'Z' : 8,#
}
MOT_TRIPLE = 6
MOT_DOUBLE = 5
LETTRE_TRIPLE = 4
LETTRE_DOUBLE = 3

ALPHABET = list(DICT_LETTER.keys())

def get_score(word):
    score = 0
    for c in word:
        score += DICT_LETTER[c.upper()]
    if len(word) >= 8:
        score += 50
    return score
