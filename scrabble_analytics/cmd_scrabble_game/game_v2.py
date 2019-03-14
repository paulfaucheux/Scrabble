import re
import numpy as np

from scrabble_analytics.toolbox import MOT_TRIPLE, MOT_DOUBLE, LETTRE_TRIPLE, LETTRE_DOUBLE, DICT_LETTER
from scrabble_analytics.utils import get_clean_list_letters, get_search_result
from scrabble_analytics.models import Words



class Scrabble:
    def __init__(self):
        self.scrabble_board = self.create_scrabble_board()
        self.scrabble_constraints = self.create_scrabble_constraints()

    def create_scrabble_board(self, *args, **kwargs):
        scrabble_board = np.zeros((11,11),dtype=object)
        for i in range(0,11):
            for j in range(0,11):
                scrabble_board[i,j] = '-'


        scrabble_board[0,2] = MOT_TRIPLE
        scrabble_board[0,8] = MOT_TRIPLE
        scrabble_board[2,4] = LETTRE_DOUBLE
        scrabble_board[2,6] = LETTRE_DOUBLE
        scrabble_board[1,5] = MOT_DOUBLE
        scrabble_board[3,7] = LETTRE_TRIPLE
        scrabble_board[2,8] = LETTRE_TRIPLE
        scrabble_board[1,9] = MOT_DOUBLE
        scrabble_board[0,10] = LETTRE_TRIPLE
        scrabble_board[2,10] = MOT_TRIPLE
        scrabble_board[4,8] = LETTRE_DOUBLE
        scrabble_board[5,9] = MOT_DOUBLE
        scrabble_board[6,8] = LETTRE_DOUBLE
        scrabble_board[8,10] = MOT_TRIPLE
        scrabble_board[0,0] = LETTRE_TRIPLE
        scrabble_board[1,1] = MOT_DOUBLE
        scrabble_board[2,2] = LETTRE_TRIPLE
        scrabble_board[3,3] = LETTRE_TRIPLE
        scrabble_board[7,7] = LETTRE_TRIPLE
        scrabble_board[8,8] = LETTRE_TRIPLE
        scrabble_board[9,9] = MOT_DOUBLE
        scrabble_board[10,10] = LETTRE_TRIPLE

        for i in range(0,scrabble_board.shape[0]):
            for j in range(0,i):
                scrabble_board[i,j] = scrabble_board[j,i]

        return scrabble_board

    def create_scrabble_constraints(self, *args, **kwargs):
        scrabble_constraints = np.zeros((11,11),dtype=object)
        for i in range(0,11):
            for j in range(0,11):
                scrabble_constraints[i,j] = '.'
        for i in range(0,scrabble_constraints.shape[0]):
            for j in range(0,i):
                scrabble_constraints[i,j] = scrabble_constraints[j,i]
        return scrabble_constraints

    def is_enough_space_for_word(self,word,start_row,start_col,is_vertical):
        #orientation 0: horizontal 1:vertical
        if start_row >= self.scrabble_board.shape[0] | start_col >= self.scrabble_board.shape[1]:
            return False
        if word.isalpha():
            if is_vertical:
                if start_row + len(word) > self.scrabble_board.shape[0]:
                    return -1
                else:
                    return True
            else:
                if start_col + len(word) > self.scrabble_board.shape[1]:
                    return False
                else:
                    return True
        else:
            return False

    def enter_new_word(self,word,start_row,start_col,is_vertical):
        if self.is_enough_space_for_word(word,start_row,start_col,is_vertical):
            if is_vertical:
                for k,v in enumerate(word):
                    self.scrabble_board[start_row+k,start_col] = v.upper()
                    self.scrabble_constraints[start_row+k,start_col] = v.upper()
            else:
                for k,v in enumerate(word):
                    self.scrabble_board[start_row,start_col+k] = v.upper()
                    self.scrabble_constraints[start_row,start_col+k] = v.upper()
            self.update_constraints(word,start_row,start_col,is_vertical)
            return True
        else:
            return False

    def update_constraints(self,new_word,start_row,start_col,is_vertical):
        new_word = new_word.upper()
        regex = '(.)' + new_word.upper()
        starts = list(set([re.findall(regex,word['Word_name'])[0] for word in Words.objects.filter(Word_name__regex=new_word).values('Word_name') if re.search(regex,word['Word_name'])]))
        regex = new_word.upper() + '(.)'
        ends = list(set([re.findall(regex,word['Word_name'])[0] for word in Words.objects.filter(Word_name__regex=new_word).values('Word_name') if re.search(regex,word['Word_name'])]))
        if is_vertical:
            if start_row > 0:
                if str(self.scrabble_constraints[start_row-1][start_col]) == '.':
                    if bool(starts):
                        self.scrabble_constraints[start_row-1][start_col] = starts
                    else:
                        self.scrabble_constraints[start_row-1][start_col] = '0'
                elif not str(self.scrabble_board[start_row-1][start_col]).isalpha():
                    existing = self.scrabble_constraints[start_row-1][start_col]
                    new_constraint = list(set(existing).intersection(starts))
                    if bool(new_constraint):
                        self.scrabble_constraints[start_row-1][start_col] = new_constraint
                    else:
                        self.scrabble_constraints[start_row-1][start_col] = '0'
            if start_row+len(new_word) < 11:
                if str(self.scrabble_constraints[start_row+len(new_word)][start_col]) == '.':
                    if bool(ends):
                        self.scrabble_constraints[start_row+len(new_word)][start_col] = ends
                    else:
                        self.scrabble_constraints[start_row+len(new_word)][start_col] = '0'
                elif not str(self.scrabble_board[start_row+len(new_word)][start_col]).isalpha():
                    existing = self.scrabble_constraints[start_row+len(new_word)][start_col]
                    new_constraint = list(set(existing).intersection(ends))
                    if bool(new_constraint):
                        self.scrabble_constraints[start_row+len(new_word)][start_col] = new_constraint
                    else:
                        self.scrabble_constraints[start_row+len(new_word)][start_col] = '0'
        else:
            if start_col > 0:
                if str(self.scrabble_constraints[start_row][start_col-1]) == '.':
                    if bool(starts):
                        self.scrabble_constraints[start_row][start_col-1] = starts
                    else:
                        self.scrabble_constraints[start_row][start_col-1] = '0'
                elif not str(self.scrabble_board[start_row][start_col-1]).isalpha():
                    existing = self.scrabble_constraints[start_row][start_col-1]
                    new_constraint = list(set(existing).intersection(starts))
                    if bool(new_constraint):
                        self.scrabble_constraints[start_row][start_col-1] = new_constraint
                    else:
                        self.scrabble_constraints[start_row][start_col-1] = '0'
            if start_col+len(new_word) < 11:
                if str(self.scrabble_constraints[start_row][start_col+len(new_word)]) == '.':
                    if bool(ends):
                        self.scrabble_constraints[start_row][start_col+len(new_word)] = ends
                    else:
                        self.scrabble_constraints[start_row][start_col+len(new_word)] = '0'
                elif not str(self.scrabble_board[start_row][start_col+len(new_word)]).isalpha():
                    existing = self.scrabble_constraints[start_row][start_col+len(new_word)]
                    new_constraint = list(set(existing).intersection(ends))
                    if bool(new_constraint):
                        self.scrabble_constraints[start_row][start_col+len(new_word)] = list(set(existing).intersection(ends))
                    else:
                        self.scrabble_constraints[start_row][start_col+len(new_word)] = '0'

    def check_character(self,line, letter, letter_pos):
        i=1
        ans = letter
        while str(line[letter_pos-i]).isalpha():
            ans += str(line[letter_pos-i])
            i += 1
        ans = ans[::-1]
        i=1
        while str(line[letter_pos+i]).isalpha():
            ans += str(line[letter_pos+i])
            i += 1
        return Words.objects.filter(Word_name=ans).exists()

    def is_word_location_valid(self,index,start_pos,is_vertical,word):
        if is_vertical:
            if start_pos > 0:
                if str(self.scrabble_board[start_pos-1][index]).isalpha():
                    return False
            if start_pos+len(word) < 11:
                if str(self.scrabble_board[start_pos+len(word)][index]).isalpha():
                    return False
            for i, v in enumerate(word):
                if (start_pos > 0) & (index>0):
                    if str(self.scrabble_constraints[start_pos + i][index -1 ]) != '.':
                        # there is a constraint
                        if str(self.scrabble_board[start_pos + i][index -1 ]).isalpha():
                            # constraint is existing letter
                            if not self.check_character(self.scrabble_board[start_pos +i ][:],v,index):
                                return False
                        else:
                            # constraint is restricted list of values
                            if not v in self.scrabble_constraints[start_pos + i][index -1 ]:
                                return False
                if (start_pos+len(word) < 11) & (index+1) < 11:
                    if str(self.scrabble_constraints[start_pos + i][index + 1]) != '.':
                        if str(self.scrabble_constraints[start_pos + i][index + 1]).isalpha():
                            if not self.check_character(self.scrabble_board[start_pos +i ][:],v,index):
                                return False
                        else:
                            if not v in self.scrabble_constraints[start_pos + i][index + 1]:
                                return False
        else:
            if (start_pos > 0) & (index>0):
                if str(self.scrabble_board[index][start_pos-1]).isalpha():
                    return False
            if (start_pos+len(word) < 11) & (index+1) < 11:
                if str(self.scrabble_board[index][start_pos+len(word)]).isalpha():
                    return False
            for i,v in enumerate(word):
                if start_pos > 0:
                    if str(self.scrabble_constraints[index + 1 ][start_pos + i]) != '.':
                        if str(self.scrabble_board[index + 1 ][start_pos + i]).isalpha():
                            if not self.check_character([self.scrabble_board[j][start_pos+i] for j in range(0,11)],v,index):
                                return False
                        else:
                            if not v in self.scrabble_constraints[index + 1][start_pos + i]:
                                return False
                if start_pos+len(word) < 11:
                    if str(self.scrabble_constraints[index - 1][start_pos + i]) != '.':
                        if str(self.scrabble_constraints[index - 1][start_pos + i]).isalpha():
                            if not self.check_character([self.scrabble_board[j][start_pos+i] for j in range(0,11)],v,index):
                                return False
                        else:
                            if not v in self.scrabble_constraints[index - 1][start_pos + i]:
                                return False
        return True

    def get_best_words_line(self,index,is_vertical,df_words):
        ans = []
        for start_pos in range(0,11-1):
            for word_len in range(2,11-start_pos):
                if is_vertical:
                    if any([str(w).isalpha() for w in [self.scrabble_board[i][index] for i in range(start_pos,start_pos+word_len)]]):
                        line_letters = list(set([str(w) for w in [self.scrabble_board[i][index] for i in range(start_pos,start_pos+word_len)] if str(w).isalpha()]))
                        for word in df_words[(df_words['length'] == word_len) & (df_words['missing'].str.contains('['+','.join(line_letters)+']', regex=True, na=False))]['words'].values:
                            regex = ''.join([str(w) for w in [self.scrabble_constraints[i][index] for i in range(start_pos,start_pos+word_len)]])
                            if re.search(regex,str(word)):
                                if self.is_word_location_valid(index,start_pos,is_vertical,word):
                                    ans.append((word,self.get_word_score(index,True,word, start_pos)))

                else:
                    if any([str(w).isalpha() for w in self.scrabble_board[index][start_pos:start_pos+word_len]]):
                        line_letters = list(set([str(w) for w in self.scrabble_board[index][start_pos:start_pos+word_len] if str(w).isalpha()]))
                        for word in df_words[(df_words['length'] == word_len) & (df_words['missing'].str.contains('['+','.join(line_letters)+']', regex=True, na=False))]['words'].values:
                            regex = ''.join([str(w) for w in self.scrabble_constraints[index][start_pos:start_pos+word_len]])
                            if re.search(regex,word):
                                if self.is_word_location_valid(index,start_pos,is_vertical,word):
                                    ans.append((word,self.get_word_score(index,False,word, start_pos)))

        return ans

    def get_all_best_words(self,df_words):
        ans = []
        for index in range(0,11):
            if any([str(w).isalpha() for w in self.scrabble_board[:][index]]):
                for word, score in self.get_best_words_line(index,True,df_words):
                    ans.append(('C'+str(index),word,score))
            if any([str(w).isalpha() for w in self.scrabble_board[index][:]]):
                for word, score in self.get_best_words_line(index,False,df_words):
                    ans.append(('C'+str(index),word,score))
        return list(sorted(ans,key=lambda x: x[2],reverse=True))

    def get_word_score(self, index, is_vertical, word, start_pos):
        score = 0
        existing_letters = 0
        double = 0
        triple = 0
        if is_vertical:
            line = [self.scrabble_board[i][index] for i in range(0,11)]
        else:
            line = self.scrabble_board[index][:]
        for i,v in enumerate(word):
            if (v != line[i+start_pos])  & (str(line[i+start_pos]).isalpha()):
                return -1
            elif line[i+start_pos] == MOT_TRIPLE:
                score += DICT_LETTER[v]
                triple += 1
            elif line[i+start_pos] == MOT_DOUBLE:
                score += DICT_LETTER[v]
                double += 1
            elif line[i+start_pos] == LETTRE_TRIPLE:
                score += DICT_LETTER[v] * 3
            elif line[i+start_pos] == LETTRE_DOUBLE:
                score += DICT_LETTER[v] * 2
            elif line[i+start_pos] == v:
                existing_letters += 1
                score += DICT_LETTER[v]
            else:
                score += DICT_LETTER[v]
        if triple > 0:
            score *= 3 * triple
        if double > 0:
            score *= 2 * double
        if len(word) > 7:
            score += 35
        return score


scrabble = Scrabble()
scrabble.enter_new_word('cotes',5,1,False)#=0
scrabble.enter_new_word('fohn',4,2,True)
scrabble.enter_new_word('jodles',0,5,True)
scrabble.enter_new_word('parjure',0,2,False)
scrabble.enter_new_word('mis',8,0,False)

print(scrabble.create_scrabble_board)

list_letters = 'qbetksa'
letters, free_letter = get_clean_list_letters(list_letters.upper())
df = get_search_result(letters, free_letter)
dict_length_words = df.set_index('length')['words'].groupby('length').apply(list).to_dict()

for solution in scrabble.get_all_best_words(df[['length','words','missing']]):
    print(solution)

#! exec(open(r'.\scrabble_analytics\cmd_scrabble_game\game_v2.py').read())
