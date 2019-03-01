from collections import Counter
import re
import numpy as np
import pandas as pd

from django.shortcuts import render
from scrabble_analytics.toolbox import get_score, MOT_TRIPLE, MOT_DOUBLE, LETTRE_TRIPLE, LETTRE_DOUBLE, DICT_LETTER, ALPHABET
from scrabble_analytics.models import Words, SavedSearchParameters, SavedSearchResults

def get_pk_search(letters, free_letter):
    return ''.join(sorted(letters)) + ''.join([ '_' for c in range(free_letter)])

def get_clean_list_letters(list_letters):
    return ''.join([c for c in list_letters if c.isalpha()]), [c for c in list_letters].count('_')

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

def get_list_free_letters_options(free_letter):
    ans = []
    previous_letter_1 = previous_letter_2 = ''

    if free_letter == 3:
        for letter_3 in ALPHABET:
            for letter_2 in ALPHABET:
                if previous_letter_2 == letter_3:
                    break
                else:
                    for letter_1 in ALPHABET:
                        if previous_letter_1 == letter_2:
                            break
                        else:
                            ans.append(letter_1+letter_2+letter_3)
                        previous_letter_1 = letter_1
            previous_letter_2 = letter_2
    elif free_letter == 2:
        for letter_2 in ALPHABET:
            for letter_1 in ALPHABET:
                if previous_letter_1 == letter_2:
                    break
                else:
                    ans.append(letter_1+letter_2)
                previous_letter_1 = letter_1
    elif free_letter == 1:
        for letter in ALPHABET:
            ans.append(letter)
    return ans

def get_list_words(letters,free_letter):
    df = pd.DataFrame()
    qs = Words.objects.all().values('Word_name')
    qs_list = [word['Word_name'] for word in qs]
    free_letter_options = get_list_free_letters_options(free_letter)
    for free_letter_option in free_letter_options:
        available_letters = letters + free_letter_option
        letters_available_unique = ''.join(list(set(available_letters)))
        letters_available_duplicates_unique = letters_available_unique
        duplicate_letters = dict()
        count_search = 0
        for letter in available_letters:
            count = available_letters.count(letter)
            if count > 1:
                duplicate_letters[letter] = count
                letters_available_duplicates_unique = letters_available_duplicates_unique.replace(letter,'')
            count_search += count
            if count_search >= len(available_letters):
                break
        if bool(duplicate_letters):
            special_part = ''.join([ '(?!(.*'+str(k)+'){'+str(v+1) + '})' for k,v in duplicate_letters.items()])
            regex = r'^(?!.*([' + letters_available_duplicates_unique + r']).*\1)(' +special_part + ')[' + letters_available_unique + r']*$'
        else:
            regex = r'^(?!.*(.).*\1)[' + available_letters + r']*$'

        df_temp = pd.DataFrame()

        df_temp['words'] = [word for word in qs_list if re.search(regex,word)]
        df_temp['missing'] = ''.join(free_letter_option)
        df = df.append(df_temp)

    df['length'] = df['words'].str.len()
    df['score'] = df['words'].apply(lambda x: get_score(x))

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
        return get_list_words(letters, free_letter+1)
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
            for k,v in enumerate(word):
                scrabble[start_row+k,start_col] = word[k].upper()
            return scrabble
        else:
            for k,v in enumerate(word):
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
        elif l == '-':
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


def get_score_letters_needed_word(line, word, start_pos):
    score = 0
    existing_letters = 0
    double = 0
    triple = 0

    for i,v in enumerate(word):
        if (word[i] != line[i+start_pos])  & (str(line[i+start_pos]).isalpha()):
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
            score += DICT_LETTER[word[i]]
        else:
            score += DICT_LETTER[word[i]]

    if triple > 0:
        score *= 3 * triple
    if double > 0:
        score *= 2 * double
    return score, len(word) - existing_letters

def print_scrabble(scrabble):
    for row in scrabble:
        line = ''
        for col in row:
            line += str(col) + ' '
        print(line)

def get_constraint_item(isColumn,line_position,current_position,scrabble,line,available_letters):
    current_line = list(scrabble[:][current_position] if isColumn else scrabble[current_position][:])
    current_line = [str(item) for item in current_line]
    prefixes = re.findall(r'([A-Z]*['+str(line[current_position])+r'])[A-Z0-9\-]{'+str(10-line_position)+'}',''.join(current_line))
    suffixes = re.findall(r'[A-Z\-0-9]{'+str(line_position)+'}(['+str(line[current_position])+'][A-Z]*)',''.join(current_line))
    constraints = []
    letters = []
    for prefix in prefixes:
        for suffix in suffixes:
            if (len(prefix) > 1) & (len(suffix) > 1):
                constraint = prefix[:-1] + '['+','.join(list(set(available_letters)))+']{1}' + suffix[1:]
            elif (len(prefix) > 1) & (len(suffix) <= 1):
                constraint = prefix[:-1] + '['+','.join(list(set(available_letters)))+']{1}'
            elif (len(prefix) <= 1) & (len(suffix) > 1):
                constraint = '['+','.join(list(set(available_letters)))+']{1}' + suffix[1:]
            else:
                return [],False
            #print('prefix: ',prefix,' suffix: ',suffix)
            #print('constraint: ',constraint)
            constraints.append((constraint,len(prefix)-1))
    for constraint, letters_position in constraints:
        for item in Words.objects.filter(Word_name__regex=r'^'+constraint+'$').values('Word_name'):
            letters.append(item['Word_name'][letters_position])
    return [str(ltr) for ltr in list(set(letters)) if re.search('[A-Z]{1}',ltr)],True

def get_line_constrainsts(scrabble,line_position,line,available_letters):
    line_constraints = ['['+','.join(list(set(available_letters)))+']?' for i in range(0,11)]
    for current_position in range(0,11):
        if str(line[current_position]).isalpha():
            line_constraints[current_position] = '['+ str(line[current_position]) + r']{1}'
            continue
        elif line_position[0] == 'c':
            constraint_list_letters, flag = get_constraint_item(True,int(line_position[1]),current_position,scrabble,line,available_letters)
        elif line_position[0] == 'r':
            constraint_list_letters, flag = get_constraint_item(False,int(line_position[1]),current_position,scrabble,line,available_letters)
        else:
            raise ValueError('neither col nor row')
        if flag:
            if bool(constraint_list_letters):
                line_constraints[current_position] = '['+ ','.join(constraint_list_letters) + ']{1}'
            else:
                line_constraints[current_position] = '[-1]'
        else:
            continue

    return line_constraints

def split_constraints(list_constraints):
    ans = []
    current_list = []
    for item in list_constraints:
        if '[-1]' in item:
            if bool(current_list):
                ans.append(current_list)
                current_list = []
        else:
            current_list.append(item)
    if bool(current_list):
        ans.append(current_list)
    return ans

def get_constraints_per_line(list_main_constraints):
    ans = []
    for sublist_constraint in split_constraints(list_main_constraints):
        mask = ''.join(['0' if '{1}' not in sublist_constraint[i] else str(i+1) for i in range(0,len(sublist_constraint))])
        #print('mask: ',mask)
        string = '10' + mask + '01'
        matches = re.finditer(r'(?=([1-9]{1}[0]{1}[0]*[1-9]+[0]*[0]{1}[1-9]{1}))',string)
        results = [match.group(1)[2:-2] for match in matches]
        #print('results: ',results)
        for result in results:
            no_zero_val_index = int([match.span()[1]-1 for match in re.finditer(r'[1-9]{1}',result)][0])
            no_zero_val_value = int([match.group() for match in re.finditer(r'[1-9]{1}',result)][0])
            start_pos = no_zero_val_value-no_zero_val_index-1 if no_zero_val_value-no_zero_val_index-1 >= 0 else no_zero_val_value-no_zero_val_index-1 + 10
            ans.append(''.join(sublist_constraint[(start_pos):(start_pos+len(result))]))
    return list(set(np.hstack(ans))) if bool(ans) else []


def validWord(word, letterList):
    word2, word1 = Counter(word), Counter(letterList)
    return all(word2[k] <= word1.get(k, 0) for k in word2)

def find(s, ch):
    return [i for i, ltr in enumerate(s) if ltr == ch]

def get_list_words_associated_score(line,available_letters_all,regex_list_constrainsts):
    list_words = []
    list_score = []
    for constraint in get_constraints_per_line(regex_list_constrainsts):
        for item in Words.objects.filter(Word_name__regex= r'^' + constraint + r'$').values('Word_name'):
            if validWord(item['Word_name'], available_letters_all):
                for i in range(0,11-len(item['Word_name'])):
                    match = 0
                    for start in range(0,len(item['Word_name'])):
                        if str(line[i+start]).isalpha():
                            if str(line[i+start]) == item['Word_name'][start]:
                                match += 1
                                start_index = i
                            else:
                                continue
                    if match > 0:
                        score = get_score_letters_needed_word(line,item['Word_name'],start_index)[0]
                        if score > 0:
                            list_score.append(score)
                            list_words.append(item['Word_name'])
                        break
    return tuple(zip(list_words,list_score))

def print_solution(data):
    if bool(data):
        for line, word, score in data:
            print(line + '\t' + str(score) + '\t' + word)
