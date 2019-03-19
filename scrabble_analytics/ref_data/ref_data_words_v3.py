from scrabble_analytics.models import Words, WordsSet
from scrabble_analytics.utils import get_score

f_db = r'.\scrabble_analytics\ref_data\database_liste_de_mots.txt'


Words.objects.all().delete()
WordsSet.objects.all().delete()

insert_word_list = []
i = 0
step = 0
total = 406714

with open(f_db,'r') as f:
    for line in f:
        i += 1
        data = line[:-1]
        set_data = ''.join(sorted(set([l.upper() for l in data])))
        q_ws = WordsSet.objects.filter(Wordset_name=set_data)
        if q_ws.exists():
            insert_word_list.append(Words(Word_name=data,
                Score=get_score(data),
                Word_set=  q_ws.first(),
                Word_name_len=len(data)
            ))
        else:
            q_wordsSet = WordsSet(Wordset_name=set_data)
            q_wordsSet.save()
            insert_word_list.append(Words(Word_name=data,
                Score=get_score(data),
                Word_set=  q_wordsSet,
                Word_name_len=len(data)
            ))
        if i >= step:
            print(str(i/total*100) + ' %')
            step += total / 20

Words.objects.bulk_create(insert_word_list)


#! To execute it:
#! python manage.py shell
#! exec(open(r'.\scrabble_analytics\ref_data\ref_data_words_v3.py').read())
