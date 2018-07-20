from scrabble_analytics.models import Words
from scrabble_analytics.utils import get_score

filename = r'.\scrabble_analytics\ref_data\database_liste_de_mots.txt'
f = open(filename, 'r')

insert_list = []
for word in f:
    insert_list.append(Words(Word_name=word,
        Length=len(word),
        Score=get_score(word)
    ))
Words.objects.bulk_create(insert_list)


f.close()