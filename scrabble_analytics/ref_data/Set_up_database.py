list_of_files = ['database_liste_de_mots.txt', 'db_word_list.txt', 'db_set_list.txt']
word_file = open(list_of_files[0],'r')
db_word = open(list_of_files[1],'a')
db_set = open(list_of_files[2],'a')
dict_set = dict()

def is_new_set(new_set,list_existing_sets):
    # if not list_existing_sets:
    #     return True
    # for existing_set in list_existing_sets:
    #     if len(new_set) != len(existing_set):
    #         return True
    #     for i in range(0,len(existing_set)):
    #         if existing_set[i].upper() != new_set[i].upper():
    #             return True
    #     return False
    # return False
    return False if new_set in list_existing_sets else True

for line in word_file:
    word = line[:-1]
    set_letters = sorted(set([l.upper() for l in word]))
    if is_new_set(''.join(set_letters), list(dict_set.values())):
        dict_set[len(dict_set)] = ''.join(set_letters)
        db_word.write(str(len(dict_set)) + '\t' + word + '\n')
        db_set.write(str(len(dict_set)) + '\t' + ''.join(set_letters) + '\n')
    else:
        val = ''.join(set_letters)
        for k,v in dict_set.items():
            if v == val:
                db_word.write(str(k) + '\t' + word + '\n')
                break



word_file.close()
db_word.close()
db_set.close()

for file_path in list_of_files:
    with open(file_path,'r') as f:
        print(file_path,': ',len(f.readlines()))
