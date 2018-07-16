from scrabble_analytics.models import Word

filename = r'.\scrabble_analytics\ref_data\database_liste_de_mots.txt'
f = open(filename, 'r')
for word in f:
    Word(Word_name=word).save()
f.close()
