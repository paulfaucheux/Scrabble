

letter_value = {
    'a' : 1,#
    'b' : 5,#
    'c' : 4,#
    'd' : 3,#
    'e' : 1,#
    'f' : 5,#
    'g' : 5,#
    'h' : 5,#
    'i' : 1,#
    'j' : 10,#
    'k' : 10,#
    'l' : 2,#
    'm' : 4,#
    'n' : 1,#
    'o' : 1,#
    'p' : 4,#
    'q' : 10,#
    'r' : 1,#
    's' : 1,#
    't' : 1,#
    'u' : 2,#
    'v' : 8,#
    'w' : 10,#
    'x' : 10,#
    'y' : 10,#
    'z' : 10,#
}

def get_score(word):
    score = 0
    for c in word:
        score += letter_value[c.lower()]
    if len(word) >= 8:
        score += 50
    return score