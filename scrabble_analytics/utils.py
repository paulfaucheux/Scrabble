from scrabble_analytics.toolbox import get_score
from scrabble_analytics.models import WordsObject

import numpy as np
import pandas as pd



def get_clean_list_letters(list_letters):
    return [c for c in list_letters if c.isalpha()], [c for c in list_letters].count('_') 


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
    print(free_letter)
    all_entries = [] #WordsObject.objects.all()
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

    return df