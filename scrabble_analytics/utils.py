from scrabble_analytics.toolbox import get_score
from scrabble_analytics.models import Words, SavedSearchParameters, SavedSearchResults

import numpy as np
import pandas as pd

def get_pk_search(letters, free_letter):
    return ''.join(sorted(letters)) + ''.join([ '_' for c in range(free_letter)])

def get_clean_list_letters(list_letters):
    return [c for c in list_letters if c.isalpha()], [c for c in list_letters].count('_') 

def check_param_label(label):
    return True if label == 'word' or label == 'missing' else False

def check_param_value(label):
    return True if len(label) > 0 and label.isalpha() else False

def get_additional_param(filter_param):
    if len(filter_param) > 1 and check_param_label(filter_param[0].strip()) and check_param_value(filter_param[1].strip()):
        return filter_param[0].strip(), filter_param[1].strip()
    return None, None

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
        w = w.Word_name[:-1]
        if len(w) <= 10:
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
    print(df.columns)
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
    obj_result = SavedSearchResults.objects.filter(Pksearch=obj_search)
    columns = ['words', 'missing', 'length', 'score']
    df = pd.DataFrame(np.empty(shape=[len(obj_result),len(columns)], dtype=str), columns=columns)
    i = 0
    for obj in obj_result:
        df.loc[i,'words'] = obj.Word_name
        df.loc[i,'missing'] = obj.Missing
        df.loc[i,'length'] = obj.Length
        df.loc[i,'score'] = obj.Score
        i += 1
    return df


def get_search_result(letters, free_letter):
    pk_search = get_pk_search(letters, free_letter)
    obj_search = SavedSearchParameters.objects.filter(Letters_list = pk_search)
    if len(obj_search) == 0:
        print('does not search exists')
        return get_list_of_words(letters, free_letter+1)
    else:
        print('search exists')
        return get_df_saved_search_result(obj_search[0]) 

