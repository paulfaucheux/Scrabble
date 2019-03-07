import numpy as np
from scrabble_analytics.utils import create_scrabble_board, enter_new_word, get_letters_from_player, get_free_space, print_scrabble, get_line_constrainsts, get_list_words_associated_score, print_solution

scrabble = create_scrabble_board()
scrabble = enter_new_word(scrabble,'bravee',5,1,0)
scrabble = enter_new_word(scrabble,'aciera',1,2,1)
scrabble = enter_new_word(scrabble,'oriya',7,0,0)
scrabble = enter_new_word(scrabble,'wad',1,1,0)
scrabble = enter_new_word(scrabble,'coxales',2,2,0)
scrabble = enter_new_word(scrabble,'zone',6,0,1)



print_scrabble(scrabble)

player_letters = get_letters_from_player('qonjnso')

free_space = get_free_space(scrabble)
list_possible_solutions = []
list_final_tuple = []

for line_position, line in free_space:
    print(line_position, line)
    regex_constrainst_array = get_line_constrainsts(scrabble,line_position,line,player_letters)
    list_words_score = get_list_words_associated_score(line
        , list(np.hstack([player_letters,sorted(set([l for l in line if str(l).isalpha()]))]))
        ,regex_constrainst_array)
    if bool(list_words_score):
        list_final_tuple.append([(line_position, word, score) for word, score in list_words_score])

if bool(list_final_tuple):
    print_solution(sorted( [(pos, word, int(score)) for pos, word, score in np.vstack(list_final_tuple)],reverse=True,key=lambda x: x[2]))




#! exec(open(r'.\scrabble_analytics\cmd_scrabble_game\game.py').read())
