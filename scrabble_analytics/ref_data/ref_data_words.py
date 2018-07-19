from scrabble_analytics.models import WordsObject

filename = r'.\scrabble_analytics\ref_data\database_liste_de_mots.txt'
f = open(filename, 'r')
for word in f:
    WordsObject(Word_name=word).save()
f.close()
