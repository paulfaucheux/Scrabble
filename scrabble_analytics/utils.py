import re
from collections import Counter
import numpy as np
import pandas as pd

from django.shortcuts import render
from scrabble_analytics.toolbox import get_score, MOT_TRIPLE, MOT_DOUBLE, LETTRE_TRIPLE, LETTRE_DOUBLE, DICT_LETTER, WILDCHAR
from scrabble_analytics.models import Words, SavedSearchParameters, SavedSearchResults

def get_pk_search(letters, free_letter):
    return ''.join(sorted(letters)) + ''.join([ '_' for c in range(free_letter)])

def get_clean_list_letters(list_letters):
    return [c for c in list_letters if c.isalpha()], [c for c in list_letters].count('_')

def get_parameter_value(parameter):
    filter_param = parameter.split(':')
    if len(filter_param) != 2:
        print('Error: There is more than a label and a value in the parameter')
        return None, None
    else:
        return filter_param[0].strip().lower(), filter_param[1].strip().upper()

def filtered_dataframe(df,label,value):
    if (label == 'words_starts') & (value.isalpha()):
        df = df[df['words'].str.startswith(value)]
    elif (label == 'words_ends') & (value.isalpha()):
        df = df[df['words'].str.endswith(value)]
    elif (label == 'words') & (value.isalpha()):
        list_param = str([val + "|" for val in value])
        df = df[df[label].str.contains(list_param)]
    elif (label == 'words_contains') & (value.isalpha()):
        df = df[df[label].str.contains(value)]
    elif (label == 'length') & (value.isdigit()):
        df = df[df['words'].str.len() >= float(value)]
    elif (label == 'missing') & (value.isalpha()):
        list_param = str([val + "|" for val in value])
        df = df[df[label].str.contains(list_param)]
    else:
        print('Error: The label or the value are not correct: ',label,value)
        return None
    return df

def get_dict_list_letters(list_letters):
    dict_word = dict()
    for letter in list_letters:
        if letter in dict_word:
            dict_word[letter] += 1
        else:
            dict_word[letter] = 1
    return dict_word

def check_enough_letters(word, letters, blank):
    dict_word = get_dict_list_letters(list(word))
    dict_letters = get_dict_list_letters(letters)
    missing = []
    for k,v in dict_word.items():
        if k in dict_letters:
            #print('k:{}:dict_letters[k]:{}:v:{}:blank:{}'.format(k,dict_letters[k],v,blank))
            if (dict_letters[k] + blank) < v:
                return (False,missing)
            else:
                if (v - dict_letters[k]) > 0:
                    blank -= v - dict_letters[k]
                    missing = np.append(missing,k)
                    if blank < 0:
                        return (False,missing)
        elif v > blank:
            #print('k:{}:v:{}:blank:{}'.format(k,v,blank))
            return (False, missing)
        else:
            #print('k:{}:v:{}:blank:{}'.format(k,v,blank))
            blank -= v
            missing = np.append(missing,k)
            if blank < 0:
                return (False,missing)
    return (True, missing)

def get_list_of_words(letters, free_letter):

    array_words = []
    array_missing = []
    print(letters)
    all_entries = Words.objects.all()
    for w in all_entries:
        w = w.Word_name
        if set(w).issubset(letters):
            (check, missing) = check_enough_letters(w,letters, free_letter)
            if check:
                #print('{} missing {}'.format(word,missing))
                array_words = np.append(array_words, w)
                if type(missing) is np.ndarray:
                    array_missing = np.append(array_missing, ''.join(missing))
                else:
                    array_missing = np.append(array_missing, [ '' if not missing else missing])
        elif len(list(set(w))) <= len(list(set(letters))) + free_letter:
            #print(word)
            (check, missing) = check_enough_letters(w,letters, free_letter)
            if check:
                #print('{} missing {}'.format(word,missing))
                array_words = np.append(array_words, w)
                if type(missing) is np.ndarray:
                    array_missing = np.append(array_missing, ''.join(missing))
                else:
                    array_missing = np.append(array_missing, [ '' if not missing else missing])

    df = pd.DataFrame({'words':array_words,'missing':array_missing, 'length': [len(w) for w in array_words], 'score': [ get_score(w) for w in array_words]})

    print('{}--DONE--{}--{}'.format(len(array_words),len(array_missing),len(df)))
    save_search_result(df, letters, free_letter)
    return df

def save_search_result(df, letters, free_letter):
    pk_search = get_pk_search(letters, free_letter)
    obj_pk_search = SavedSearchParameters.objects.create(Letters_list = pk_search)
    insert_entry_list = []
    for i in range(len(df)):
        insert_entry_list.append(SavedSearchResults(Pksearch=obj_pk_search,
            Word_name=df['words'].values[i],
            Missing=df['missing'].values[i],
            Length=df['length'].values[i],
            Score=df['score'].values[i]
        ))

    SavedSearchResults.objects.bulk_create(insert_entry_list)

def get_df_saved_search_result(obj_search):
    qs = SavedSearchResults.objects.filter(Pksearch=obj_search)
    q = qs.values('Word_name','Missing','Length','Score')
    df = pd.DataFrame.from_records(q)

    return df.rename(columns={'Word_name': 'words', 'Missing': 'missing', 'Length':'length', 'Score':'score'})


def get_search_result(letters, free_letter):
    pk_search = get_pk_search(letters, free_letter+1)
    obj_search = SavedSearchParameters.objects.filter(Letters_list = pk_search)

    if not obj_search.exists():
        print('The search does not exist')
        return get_list_of_words(letters, free_letter+1)
    else:
        print('The search exists already')
        return get_df_saved_search_result(obj_search[0])

def return_error_page(request_page,msg):
    print('Error return_error_page is: ',msg)
    context = {
            'message': msg,
        }
    return render(request_page, 'errors/error.html', context)

def create_scrabble_board():
    scrabble = np.zeros((11,11),dtype=object)
    for i in range(0,11):
        for j in range(0,11):
            scrabble[i,j] = '-'

    scrabble[0,2] = MOT_TRIPLE
    scrabble[0,8] = MOT_TRIPLE
    scrabble[2,4] = LETTRE_DOUBLE
    scrabble[2,6] = LETTRE_DOUBLE
    scrabble[1,5] = MOT_DOUBLE
    scrabble[3,7] = LETTRE_TRIPLE
    scrabble[2,8] = LETTRE_TRIPLE
    scrabble[1,9] = MOT_DOUBLE
    scrabble[0,10] = LETTRE_TRIPLE
    scrabble[2,10] = MOT_TRIPLE
    scrabble[4,8] = LETTRE_DOUBLE
    scrabble[5,9] = MOT_DOUBLE
    scrabble[6,8] = LETTRE_DOUBLE
    scrabble[8,10] = MOT_TRIPLE
    scrabble[0,0] = LETTRE_TRIPLE
    scrabble[1,1] = MOT_DOUBLE
    scrabble[2,2] = LETTRE_TRIPLE
    scrabble[3,3] = LETTRE_TRIPLE
    scrabble[7,7] = LETTRE_TRIPLE
    scrabble[8,8] = LETTRE_TRIPLE
    scrabble[9,9] = MOT_DOUBLE
    scrabble[10,10] = LETTRE_TRIPLE

    for i in range(0,scrabble.shape[0]):
        for j in range(0,i):
            scrabble[i,j] = scrabble[j,i]

    return scrabble

def is_enough_space_for_word(scrabble,word,start_row,start_col,orientation):
    #orientation 0: horizontal 1:vertical
    if start_row >= scrabble.shape[0] | start_col >= scrabble.shape[1]:
        return False
    if word.isalpha():
        if orientation == 1:
            if start_row + len(word) > scrabble.shape[0]:
                return -1
            else:
                return True
        elif orientation ==0:
            if start_col + len(word) > scrabble.shape[1]:
                return False
            else:
                return True
        else:
            return False
    else:
        return False

def enter_new_word(scrabble,word,start_row,start_col,orientation):
    if is_enough_space_for_word(scrabble,word,start_row,start_col,orientation):
        if orientation == 1:
            for k in range(0,len(word)):
                scrabble[start_row+k,start_col] = word[k].upper()
            return scrabble
        else:
            for k in range(0,len(word)):
                scrabble[start_row,start_col+k] = word[k].upper()
            return scrabble
    else:
        return -1

def is_space_in_string(row):
    l = 0
    for c in row:
        if str(c).isalpha():
            l += 1
            #if l > 2:
            #    return False
        elif l == 0:
            continue
        else:
            l = 1
    if l >= 1:
        return True
    return False

def get_free_space(scrabble):
    free_space = []
    if scrabble.shape[0] != scrabble.shape[1]:
        return -1
    for i in range(0,scrabble.shape[0]):
        row = scrabble[:,i]
        col = scrabble[i,:]
        if is_space_in_string(row):
            free_space.append(('c'+str(i),row))
        if is_space_in_string(col):
            free_space.append(('r'+str(i),col))
    return free_space

def get_letters_from_player(letters):
    letters = [l.upper() for l in letters]
    return letters

def read_dict_file():
    # dict_words = {'EJKR':['JERKE','JERKE']
    #     ,'ACEHT':['CHATTE','TACHE','TACHEE','CACHET']
    #     , 'ACEILU': ['ACCEUIL','CALCULAI','CULAI']
    #     , 'AILU':['LUAI','LUAI']
    #     , 'ACEILSU': ['ACCEUILS','ACCEUILSS']
    #     , 'ALPU':['PAULA']
    # }
    dict_words = dict()
    for item in Words.objects.values('Word_set__Wordset_name','Word_name'):
        if item['Word_set__Wordset_name'] in dict_words.keys():
            dict_words[item['Word_set__Wordset_name']].append(item['Word_name'])
        else:
            dict_words[item['Word_set__Wordset_name']] = [item['Word_name']]
    return dict_words

#! depreciated
# def get_possible_words(dict_words, set_of_unique_letters):
#     #dict_words = read_dict_file()

#     words = []
#     for key in dict_words.keys():
#         add_key = True
#         set_of_unique_letters_temp = set_of_unique_letters
#         for l in key:
#             if l not in ''.join(set_of_unique_letters_temp):
#                 if WILDCHAR in set_of_unique_letters_temp:
#                     set_of_unique_letters_temp = np.delete(set_of_unique_letters_temp, np.where(set_of_unique_letters_temp == WILDCHAR)[0], axis=0)
#                 else:
#                     add_key = False
#                     break
#         if add_key:
#             words = np.hstack([words, dict_words[key]])
#     return words

def get_score_letters_needed_word(line, word, start_pos):
    score = 0
    existing_letters = 0
    double = 0
    triple = 0

    for i in range(0,len(word)):
        if (word[i] != line[i+start_pos])  & (not str(line[i+start_pos]).isdigit()):
            return -1, 0
        elif line[i+start_pos] == MOT_TRIPLE:
            triple += 1
        elif line[i+start_pos] == MOT_DOUBLE:
            double += 1
        elif line[i+start_pos] == LETTRE_TRIPLE:
            score += DICT_LETTER[word[i]] * 3
        elif line[i+start_pos] == LETTRE_DOUBLE:
            score += DICT_LETTER[word[i]] * 2
        elif line[i+start_pos] == word[i]:
            existing_letters += 1
        else:
            score += DICT_LETTER[word[i]]

    if triple > 0:
        score *= 3 * triple
    if double > 0:
        score *= 2 * double
    return score, len(word) - existing_letters


def get_position_word(line, word, player_letters, board_letters):
    set_letters = np.hstack([player_letters, board_letters])
    for l in word:
        if l in set_letters:
            set_letters = np.delete(set_letters, np.where(set_letters == l)[0][0], axis=0)
        elif WILDCHAR in set_letters:
            set_letters = np.delete(set_letters, np.where(set_letters == WILDCHAR)[0][0], axis=0)
        else:
            return -1, 0
    for start in range(0,len(line)-len(word)+1):
        match = 0
        for i in range(0,len(word)):
            if str(line[i+start]).isalpha():
                if str(line[i+start]) != word[i]:
                    break
                else:
                    match += 1
        if match > 0:
            if start == 0:
                if len(line) == len(word)+start:
                    return get_score_letters_needed_word(line, word, start)
                elif not str(line[len(word)+start]).isalpha():
                    return get_score_letters_needed_word(line, word, start)
            elif str(line[start-1]).isdigit():
                if len(line) == len(word)+start:
                    return get_score_letters_needed_word(line, word, start)
                elif not str(line[len(word)+start]).isalpha():
                    return get_score_letters_needed_word(line, word, start)
            else:
                return -1, 0
    return -1, 0

def print_scrabble(scrabble):
    for row in scrabble:
        line = ''
        for col in row:
            line += str(col) + ' '
        print(line)



def return_word(scrabble,row,col,direction,word):
#     direction: define where we are searching
#     0: up
#     1: down
#     2: left
#     3: right
    if (row < 0) | (col < 0):
        return word
    if (row > 10) | (col > 10):
        return word
    elif str(scrabble[row][col]).isalpha():
        if direction == 0:
            return return_word(scrabble,row-1,col,0,str(word) + str(scrabble[row][col]))
        elif direction == 1:
            return return_word(scrabble,row+1,col,1,str(word) + str(scrabble[row][col]))
        elif direction == 2:
            return return_word(scrabble,row,col-1,2,str(word) + str(scrabble[row][col]))
        elif direction == 3:
            return return_word(scrabble,row,col+1,3,str(word) + str(scrabble[row][col]))
        else:
            return -1
    else:
        return word

def get_list_of_allowed_letters(first_part_word,last_part_word,board_letters):
    letters = []
    #print('query: ',first_part_word,'_',last_part_word,' len: ',1+len(first_part_word)+len(last_part_word))
    regex_to_apply = '^'+first_part_word+'[' + ','.join(board_letters)+']'+last_part_word+'$'
    #print('regex_to_apply: ',regex_to_apply)
    for item in Words.objects.filter(Word_name__regex=regex_to_apply).values('Word_name'):
        letters.append(item['Word_name'][len(first_part_word)])
    return list(set(letters))

def get_line_constrainsts(scrabble,line_position,line,available_letters):
    allowed_letters = ['['+','.join(list(set(available_letters)))+']?' for i in range(0,11)]
    if line_position[0] == 'c':
        for row in range(0,11):
            if str(scrabble[row,int(line_position[1:])]).isalpha():
                allowed_letters[row] = '['+str(scrabble[row,int(line_position[1:])])+']'
            else:
                first_part_word = return_word(scrabble,row,int(line_position[1:])-1,2,'')
                last_part_word = return_word(scrabble,row,int(line_position[1:])+1,3,'')
                if (bool(first_part_word)) | (bool(last_part_word)):
                    list_letters_authorized = get_list_of_allowed_letters(first_part_word,last_part_word,available_letters)
                    if bool(list_letters_authorized):
                        allowed_letters[row] = '['+','.join(list_letters_authorized) + ']?'
                    else:
                        allowed_letters[row] = '[-1]'
        return allowed_letters
    elif line_position[0] == 'r':
        for col in range(0,11):
            if str(scrabble[int(line_position[1:]),col]).isalpha():
                allowed_letters[col] = '['+str(scrabble[int(line_position[1:]),col])+']'
            else:
                first_part_word = return_word(scrabble,int(line_position[1:])-1,col,0,'')
                first_part_word = first_part_word[::-1] # Reverse the string
                last_part_word = return_word(scrabble,int(line_position[1:])+1,col,1,'')
                if (bool(first_part_word)) | (bool(last_part_word)):
                    list_letters_authorized = get_list_of_allowed_letters(first_part_word,last_part_word,available_letters)
                    if bool(list_letters_authorized):
                        allowed_letters[col] = '['+','.join(list_letters_authorized) + ']?'
                    else:
                        allowed_letters[col] = '[-1]'
        return allowed_letters
    else:
        return -1

def get_start_end(list_constraints):
    mask = ''.join(['0' if '?' in item else '1' for item in list_constraints])
    mask = '10' + mask + '01'
    list_start = []
    list_end = []
    ans = [''.join(list_constraints)]
    for i in range(0,len(mask)):
        if mask[i:i+2] == '10':
            list_start.append(i)
        if mask[i-2:i] == '01':
            list_end.append(i+2)
    if len(list_start) > 2:
        for start,end in tuple(zip(list_start, list_end)):
            if not all([True if '[-1]' in i else False for i in list_constraints[start:end] if ('?' not in i)]):
                ans.append(''.join(list_constraints[start:end]))
    return ans

def validWord(word, letterList):
    word2, word1 = Counter(word), Counter(letterList)
    return all(word2[k] <= word1.get(k, 0) for k in word2)

def find(s, ch):
    return [i for i, ltr in enumerate(s) if ltr == ch]

def get_list_words_associated_score(line,available_letters_all,regex_constrainst_array):
    list_words = []
    list_score = []
    i_constraint = 0
    for constraint in get_start_end(regex_constrainst_array):
        print('constraint: ',constraint)
        for item in Words.objects.filter(Word_name__regex= r'^' + constraint + r'$').values('Word_name'):
            if validWord(item['Word_name'], available_letters_all):
                if i_constraint > 0:
                    i_constraint -= 1
                anchor_index, anchor_value = [(i, ltr) for i, ltr in enumerate(line) if str(ltr).isalpha()][i_constraint]
                word_indexes = find(item['Word_name'],anchor_value)
                for w_index in word_indexes:
                    if w_index < anchor_index:
                        if (len(item['Word_name']) - w_index + anchor_index) < 11:
                            start_index = anchor_index - w_index
                            score = get_score_letters_needed_word(line,item['Word_name'],start_index)[0]
                            if score > 0:
                                list_score.append(score)
                                list_words.append(item['Word_name'])
        i_constraint += 1
    return tuple(zip(list_words,list_score))

def print_solution(data):
    if bool(data):
        for line, word, score in data:
            print(line + '\t' + str(score) + '\t' + word)