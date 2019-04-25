import spacy
import nltk
from nltk.stem.snowball import *

from nltk.corpus import stopwords
stopwords_en = set(stopwords.words('english'))

nlp = spacy.load('en_core_web_lg')
bookstring = ''
with open('../data/Harry Potter 1 - Sorcerer\'s Stone.txt', 'rb') as book1:
    for line in book1:
        bookstring += line.decode('utf-8', 'ignore')


print('Start Tokenization')
bookstring = bookstring.replace('\n', '')
doc = nltk.word_tokenize(bookstring)

print('Start Stemming')
stemmer = SnowballStemmer('english')
stemmed_book = ''
for token in doc:
    stemmed_book += stemmer.stem(token) + ' '

print('Start Stop word removal')
stop_word_book = ''
for word in stemmed_book.split(' '):
    if word in stopwords_en:
        continue
    stop_word_book += word + ' '

print('Start POS tagging')
nlp_doc = nlp(stemmed_book)
csv_string = 'TEXT, LEMMA, POS, TAG, DEP, SHAPE, ALPHA, STOP\n'
for token in nlp_doc:
    csv_string += f'{token.text}, {token.lemma_}, {token.pos_}, {token.tag_}, {token.dep_},\
    {token.shape_}, {token.is_alpha}, {token.is_stop} \n'

print('Start NER')
ent_doc = nlp(bookstring)
ent_doc_stemmed = nlp(stemmed_book)
csv_pos = 'TEXT, LEMMA, POS, TAG, DEP, SHAPE, ALPHA, STOP\n'
csv_ner = 'TEXT, START_CHAR, END_CHAR, ENT_LABEL\n'
csv_ner_stemmed = 'TEXT, START_CHAR, END_CHAR, ENT_LABEL\n'

for ent in ent_doc.ents:
    csv_ner += f'{ent.text}, {ent.start_char}, {ent.end_char}, {ent.label_}\n'

for ent in ent_doc:
    csv_pos += f'{ent.text}, {ent.lemma_}, {ent.pos_}, {ent.tag_}, {ent.dep_},\
    {ent.shape_}, {ent.is_alpha}, {ent.is_stop}\n'

for ent in ent_doc_stemmed.ents:
    csv_ner_stemmed += f'{ent.text}, {ent.start_char}, {ent.end_char}, {ent.label_}\n'


with open('../data/book1_stopped.txt', 'w+') as stemmed_file:
    stemmed_file.write(stop_word_book)

with open('../data/book1_stemmed.txt', 'w+') as stemmed_file:
    stemmed_file.write(stemmed_book)

with open('../data/book1_stemmed_POS.csv', 'w+') as stemmed_file:
    stemmed_file.write(csv_string)

with open('../data/book1_NER.csv', 'w+') as stemmed_file:
    stemmed_file.write(csv_ner)

with open('../data/book1_stemmed_NER.csv', 'w+') as stemmed_file:
    stemmed_file.write(csv_ner_stemmed)

with open('../data/book1_POS.csv', 'w+') as stemmed_file:
    stemmed_file.write(csv_pos)
