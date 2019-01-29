from scrabble_analytics.models import Words, WordsSet
from scrabble_analytics.utils import get_score

f_set = r'.\scrabble_analytics\ref_data\db_set_list.txt'
f_word = r'.\scrabble_analytics\ref_data\db_word_list.txt'

Words.objects.all().delete()
WordsSet.objects.all().delete()

insert_set_list = []
dict_set_words = dict()
with open(f_set,'r') as f:
    for line in f:
        data = line[:-1].split('\t')
        insert_set_list.append(WordsSet(Wordset_name=data[1]))
        dict_set_words[data[0]] = data[1]

WordsSet.objects.bulk_create(insert_set_list)

insert_word_list = []
with open(f_word,'r') as f:
    for line in f:
        data = line[:-1].split('\t')
        insert_word_list.append(Words(Word_name=data[1],
            Length=len(data[1]),
            Score=get_score(data[1]),
            Word_set=  WordsSet.objects.filter(Wordset_name = dict_set_words[data[0]]).first()
            ))

Words.objects.bulk_create(insert_word_list)

#! To execute it:
#! python manage.py shell
#! exec(open(r'.\scrabble_analytics\ref_data\ref_data_words_v2.py').read())
