import numpy as np
import pandas as pd
from django.shortcuts import render
from scrabble_analytics.toolbox import get_score
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
