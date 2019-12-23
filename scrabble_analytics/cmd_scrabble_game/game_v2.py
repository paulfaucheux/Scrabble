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

    def update_constraint_cell(self,row,col,constraint):
        if str(self.scrabble_constraints[row][col]) == '.':
            if bool(constraint):
                self.scrabble_constraints[row][col] = constraint
            else:
                self.scrabble_constraints[row][col] = '0'
        elif not str(self.scrabble_board[row][col]).isalpha():
            existing = self.scrabble_constraints[row][col]
            new_constraint = list(set(existing).intersection(constraint))
            if bool(new_constraint):
                self.scrabble_constraints[row][col] = new_constraint
            else:
                self.scrabble_constraints[row][col] = '0'
        return True


    def get_list_previous_next_letters(self,line,start_pos,letter):
        list_previous = []
        list_next = []
        constraint = ''
        for i in range(0,11):
            if (str(line[i]).isalpha()) & (i < start_pos):
                constraint += str(line[i])
            elif (not str(line[i]).isalpha()) & (i < start_pos):
                constraint = ''
            elif (str(line[i]).isalpha()) & (i > start_pos):
                constraint += str(line[i])
            elif i == start_pos:
                constraint += letter
            else:
                break

        regex_start = '(.)' + constraint.upper()
        regex_end = constraint.upper() +'(.)'
        q_words = Words.objects.filter(Word_name__contains=constraint.upper()).values('Word_name')
        for word in q_words:
            for ans in re.findall(regex_start,word['Word_name']):
                list_previous.append(ans)
            for ans in re.findall(regex_end,word['Word_name']):
                list_next.append(ans)

        return list(set(list_previous)), list(set(list_next))

    def update_constraints(self,new_word,start_row,start_col,is_vertical):
        new_word = new_word.upper()
        regex = '(.)' + new_word.upper()
        starts = list(set([re.findall(regex,word['Word_name'])[0] for word in Words.objects.filter(Word_name__regex=new_word).values('Word_name') if re.search(regex,word['Word_name'])]))
        regex = new_word.upper() + '(.)'
        ends = list(set([re.findall(regex,word['Word_name'])[0] for word in Words.objects.filter(Word_name__regex=new_word).values('Word_name') if re.search(regex,word['Word_name'])]))
        if is_vertical:
            if start_row > 0:
                self.update_constraint_cell(start_row-1, start_col, starts)
            if start_row+len(new_word) < 11:
                self.update_constraint_cell(start_row+len(new_word),start_col,ends)
        else:
            if start_col > 0:
                self.update_constraint_cell(start_row,start_col-1,starts)
            if start_col+len(new_word) < 11:
                self.update_constraint_cell(start_row,start_col+len(new_word),ends)
        for k,v in enumerate(new_word):
            if is_vertical:
                if (start_col > 0) | (start_col+1 < 11):
                    list_previous, list_next = self.get_list_previous_next_letters(self.scrabble_board[start_row+k][:],start_col,v)
                if start_col > 0:
                    self.update_constraint_cell(start_row+k, start_col-1, list_previous)
                if start_col+1 < 11:
                    self.update_constraint_cell(start_row+k,start_col+1,list_next)
            else:
                if (start_col > 0) | (start_col+1 < 11):
                    list_previous, list_next = self.get_list_previous_next_letters([self.scrabble_board[i][start_col+k] for i in range(0,11)],start_col,v)
                if start_row + 1 < 11:
                    self.update_constraint_cell(start_row+1,start_col+k,list_next)
                if start_row > 0:
                    self.update_constraint_cell(start_row-1,start_col+k,list_previous)

    def check_character(self,line, letter, letter_pos):
        i=1
        ans = letter
        if letter_pos > 0:
            while str(line[letter_pos-i]).isalpha():
                ans += str(line[letter_pos-i])
                if letter_pos-i > 0:
                    i += 1
                else:
                    break
            ans = ans[::-1]
        i=1
        if letter_pos+i < 10:
            while str(line[letter_pos+i]).isalpha():
                ans += str(line[letter_pos+i])
                if letter_pos+i < 10:
                    i += 1
                else:
                    break
        return Words.objects.filter(Word_name=ans).exists()

    def is_word_location_valid(self,index,start_pos,is_vertical,word):
        if is_vertical:
            if start_pos > 0:
                if str(self.scrabble_board[start_pos-1][index]).isalpha():
                    return False
            if start_pos+len(word) < 11:
                if str(self.scrabble_board[start_pos+len(word)][index]).isalpha():
                    return False

            for k, v in enumerate(word):
                if self.scrabble_board[start_pos + k][index] == v:
                    continue
                if (start_pos+k < 11) & (index >0):
                    if str(self.scrabble_constraints[start_pos + k][index -1]) != '.':
                        # there is a constraint
                        if str(self.scrabble_board[start_pos + k][index -1 ]).isalpha():
                            # constraint is existing letter So I check whether there is a double word
                            if not self.check_character(self.scrabble_board[start_pos + k ][:],v,index):
                                return False

                if (start_pos+k < 11) & (index+1 < 11):
                    if str(self.scrabble_constraints[start_pos + k][index + 1]) != '.':
                        # there is a constraint
                        if str(self.scrabble_constraints[start_pos + k][index + 1]).isalpha():
                            # constraint is existing letter So I check whether there is a double word
                            if not self.check_character(self.scrabble_board[start_pos + k ][:],v,index):
                                return False
        else:
            if start_pos > 0:
                if str(self.scrabble_board[index][start_pos-1]).isalpha():
                    #print('Error: there is a letter before the word')
                    return False
            if start_pos+len(word) < 11:
                if str(self.scrabble_board[index][start_pos+len(word)]).isalpha():
                    #print('Error: there is a letter after the word')
                    return False
            for k,v in enumerate(word):
                if self.scrabble_board[index][start_pos + k] == v:
                    continue
                if (start_pos+k < 11) & (index+1 < 11):
                    if str(self.scrabble_constraints[index + 1 ][start_pos + k]) != '.':
                        # there is a constraint
                        if str(self.scrabble_board[index + 1 ][start_pos + k]).isalpha():
                            # constraint is existing letter So I check whether there is a double word
                            if not self.check_character([self.scrabble_board[j][start_pos+k] for j in range(0,11)],v,index):
                                return False

                if (start_pos+k < 11) & (index >0):
                    if str(self.scrabble_constraints[index - 1][start_pos + k]) != '.':
                        # there is a constraint
                        if str(self.scrabble_constraints[index - 1][start_pos + k]).isalpha():
                            # constraint is existing letter So I check whether there is a double word
                            if not self.check_character([self.scrabble_board[j][start_pos+k] for j in range(0,11)],v,index):
                                return False

        return True

    def get_best_words_line(self,index,is_vertical,df_words):
        ans = []
        for start_pos in range(0,11-1):
            for word_len in list(set(df_words[df_words['length']<(12-start_pos)]['length'].values)):
                if is_vertical:
                    if any([str(w).isalpha() for w in [self.scrabble_board[i][index] for i in range(start_pos,start_pos+word_len)]]):
                        line_letters = list(set([str(w) for w in [self.scrabble_board[i][index] for i in range(start_pos,start_pos+word_len)] if str(w).isalpha()]))
                        for word in df_words[(df_words['length'] == word_len) & (df_words['missing'].str.contains('['+','.join(line_letters)+']', regex=True, na=False))]['words'].values:
                            regex = ''.join([str(w) for w in [self.scrabble_constraints[i][index] for i in range(start_pos,start_pos+word_len)]])
                            if re.search(regex,str(word)):
                                if self.is_word_location_valid(index,start_pos,is_vertical,word):
                                    ans.append((word,self.get_word_score(index,True,word, start_pos)))
                    elif any([str(w) != '.' for w in [self.scrabble_constraints[i][index] for i in range(start_pos,start_pos+word_len)]]):
                        for word in df_words[(df_words['length'] == word_len) & (df_words['missing'] == '')]['words'].values:
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
                    elif any([str(w) != '.' for w in self.scrabble_constraints[index][start_pos:start_pos+word_len]]):
                        for word in df_words[(df_words['length'] == word_len) & (df_words['missing'] == '')]['words'].values:
                            regex = ''.join([str(w) for w in self.scrabble_constraints[index][start_pos:start_pos+word_len]])
                            if re.search(regex,word):
                                if self.is_word_location_valid(index,start_pos,is_vertical,word):
                                    ans.append((word,self.get_word_score(index,False,word, start_pos)))

        return ans

    def get_all_best_words(self,df_words):
        ans = []
        for index in range(0,11):
            if any([str(w) != '.' for w in self.scrabble_constraints[:][index]]):
                for word, score in self.get_best_words_line(index,True,df_words):
                    ans.append(('C'+str(index),word,score))
            if any([str(w) != '.' for w in self.scrabble_constraints[index][:]]):
                for word, score in self.get_best_words_line(index,False,df_words):
                    ans.append(('R'+str(index),word,score))
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
        for k,v in enumerate(word):
            if (v != line[k+start_pos])  & (str(line[k+start_pos]).isalpha()):
                return -1
            elif line[k+start_pos] == MOT_TRIPLE:
                score += DICT_LETTER[v]
                triple += 1
            elif line[k+start_pos] == MOT_DOUBLE:
                score += DICT_LETTER[v]
                double += 1
            elif line[k+start_pos] == LETTRE_TRIPLE:
                score += DICT_LETTER[v] * 3
            elif line[k+start_pos] == LETTRE_DOUBLE:
                score += DICT_LETTER[v] * 2
            elif line[k+start_pos] == v:
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

    def print_board(self):
        print('board')
        for i in range(0,11):
            print(' '.join([str(self.scrabble_board[i][j]) for j in range(0,11)]))

    def print_constraints(self):
        print('constraints: ')
        for i in range(0,11):
            print(' '.join([str(self.scrabble_constraints[i][j]) for j in range(0,11)]))

    def print_best_words_order(self,list_letters):
        letters, free_letter = get_clean_list_letters(list_letters.upper())
        df = get_search_result(letters, free_letter)
        for solution in scrabble.get_all_best_words(df[['length','words','missing']])[:20]:
            print(solution)


scrabble = Scrabble()
scrabble.enter_new_word('test',5,4,False)
scrabble.enter_new_word('fieront',3,5,True)
scrabble.enter_new_word('kitsch',3,7,True)
scrabble.enter_new_word('djinn',8,1,False)
scrabble.enter_new_word('jeu',8,2,True)
scrabble.enter_new_word('ays',8,8,True)
scrabble.enter_new_word('epieux',5,10,True)
scrabble.print_board()

scrabble.print_best_words_order('lrgnlba')


#! exec(open(r'.\scrabble_analytics\cmd_scrabble_game\game_v2.py').read())
