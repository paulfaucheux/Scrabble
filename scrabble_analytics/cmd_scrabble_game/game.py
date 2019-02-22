import numpy as np
from scrabble_analytics.utils import create_scrabble_board, enter_new_word, get_letters_from_player, get_free_space, print_scrabble, get_line_constrainsts, get_list_words_associated_score, print_solution

# scrabble = create_scrabble_board()
# enter_new_word(scrabble,'tom',5,4,0)
# enter_new_word(scrabble,'osames',5,5,1)
# enter_new_word(scrabble,'miniez',8,5,0)
# enter_new_word(scrabble,'fixas',10,1,0)


# player_letters = get_letters_from_player('ksloeje')
# free_space = get_free_space(scrabble)
# list_possible_solutions = []
# dict_words = read_dict_file()

# for line_position, line in free_space:
#     #print('line: ',line)
#     board_letters = sorted(set([l for l in line if str(l).isalpha()]))
#     available_letters = sorted(set(np.hstack([player_letters,board_letters])))
#     #print('available_letters: ',available_letters)
#     #! add here the constraint on the word

#     regex_constrainst = get_line_constrainsts(scrabble,line_position,line)

#     #list_possible_words = get_possible_words(dict_words, available_letters)
#     #print('line: ',line, )
#     for word in list_possible_words:
#         #print('word: ',word)
#         score, nb_letters_required = get_position_word(line, word, player_letters, board_letters)
#         if score > 0:
#             list_possible_solutions.append([score, nb_letters_required, line, word])

scrabble = create_scrabble_board()

scrabble = create_scrabble_board()
enter_new_word(scrabble,'tom',5,4,0)
enter_new_word(scrabble,'osames',5,5,1)
enter_new_word(scrabble,'miniez',8,5,0)
enter_new_word(scrabble,'fixas',10,1,0)


player_letters = get_letters_from_player('ema')

free_space = get_free_space(scrabble)
list_possible_solutions = []
list_final_tuple = []

for line_position, line in free_space:
    board_letters = sorted(set([l for l in line if str(l).isalpha()]))
    available_letters = sorted(set(np.hstack([player_letters,board_letters])))
    print(line_position, line)
    regex_constrainst_array = get_line_constrainsts(scrabble,line_position,line,available_letters)
    list_words_score = get_list_words_associated_score(line, list(np.hstack([player_letters,board_letters])),regex_constrainst_array)
    print('list_words_score: ',list_words_score)
    if bool(list_words_score):
        list_final_tuple.append([(line_position, word, score) for word, score in list_words_score])

if bool(list_final_tuple):
    print_solution(sorted( [(pos, word, int(score)) for pos, word, score in np.vstack(list_final_tuple)],reverse=True,key=lambda x: x[2]))

print_scrabble(scrabble)


#! exec(open(r'.\scrabble_analytics\cmd_scrabble_game\game.py').read())
