import spacy

nlp = spacy.load('en_core_web_sm')
bookstring = ''
with open('../data/Harry Potter 1 - Sorcerer\'s Stone.txt', 'rb') as book1:
    for line in book1:
        bookstring += line.decode('utf-8', 'ignore')

print('Start Tokenization')
doc = nlp(bookstring)

print('Start going through tokens')
csv_table = 'Text, Lemma, POS, Tag, Dep, Shape, alpha, stop\n'
for token in doc:
    csv_table += f'{token.text}, {token.lemma_}, {token.pos_}, {token.tag_}, {token.dep_},\
    {token.shape_}, {token.is_alpha}, {token.is_stop}\n'

with open('../data/book1_pos_tagging.csv', 'w+') as csv_file:
    csv_file.write(csv_table)
