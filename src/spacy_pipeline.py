import spacy
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize
from collections import Counter
import json
import operator
from tqdm import tqdm
import neuralcoref
from pathlib import Path
import re
from unidecode import unidecode

books = {1: 'Book 1 - The Philosopher\'s Stone.txt',
         2: 'Book 2 - The Chamber of Secrets.txt',
         3: 'Book 3 - The Prisoner of Azkaban.txt',
         4: 'Book 4 - The Goblet of Fire.txt',
         5: 'Book 5 - The Order of the Phoenix.txt',
         6: 'Book 6 - The Half Blood Prince.txt',
         7: 'Book 7 - The Deathly Hallows.txt'}


def createBookString(book_no: int) -> str:
    print(f'Extracting bookstring for book {book_no}')
    bookstring = ''
    with open(f'../data/cleanedBooks/{books[book_no]}', 'r') as book1:
        bookstring = unidecode(book1.read())
    return bookstring


def isNoise(token, noisy_pos_tags=['PROP'], min_token_len=3):
    is_noise = False
    if token.pos_ in noisy_pos_tags:
        is_noise = True
    elif token.is_stop:
        is_noise = True
    elif len(token) <= min_token_len:
        is_noise = True
    return is_noise


def cleanUp(token, lower=True):
    if lower:
        token = token.lower()
    return token.strip()


def NER_tagging():
    for i in range(1, 8):
        bookstring = createBookString(i)
        booklen = len(bookstring)
        parts = [bookstring[:int(booklen/4)], bookstring[int(booklen/4):int(2*booklen/4)], bookstring[int(2*booklen/4):int(3*booklen/4)], bookstring[int(3*booklen/4):]]
        ents_dict = {}
        nlp = spacy.load('en')
        nlp.max_length = 65000000
        neuralcoref.add_to_pipe(nlp)
        book_processed = ''
        for part in parts:
            book_nlp = nlp(part)

            labels = set([w.label_ for w in book_nlp.ents])
            for label in labels:
                print(f'Label: {label}')
                entities = [cleanUp(e.string, lower=False)
                            for e in book_nlp.ents if label == e.label_]
                if label not in ents_dict.keys():
                    ents_dict[label] = []
                ents_dict[label] += entities
            book_processed += book_nlp._.coref_resolved
        with open(f'../data/book_{i}_coref.txt', 'w+') as book:
            book.write(book_processed)
        with open(f'../data/NER_book_{i}.json', 'w+') as jsonfile:
            jsonfile.write(json.dumps(ents_dict, indent=2, sort_keys=True))


def merge_NER():
    ner_dict = {}
    for i in tqdm(range(1, 8)):
        with open(f'../data/NER_book_{i}.json') as json_file:
            ner_json = json.load(json_file)
        for key, values in ner_json.items():
            if key in ner_dict.keys():
                ner_dict[key] += list(set(values))
            else:
                ner_dict[key] = values
    with open(f'../data/NER_overall.json', 'w+') as ner_ovr:
        ner_ovr.write(json.dumps(ner_dict, indent=2))


def evaluate(tag: str):
    TP = 0
    FP = 0
    FN = 0
    with open(f'../data/NER_overall_majority_vote.json') as ner_file:
        ner_dict = json.load(ner_file)
        content_list = ner_dict[tag]
        char_file = open('../data/characters_unique.txt')
        characters = []
        chars_found = []
        characters = list(set([line.replace('\n', '').strip()
                               for line in char_file.readlines()]))

        print(f'Number of Characters:{len(characters)}')
        not_found = []
        for line in characters:
            if ' ' in line:
                single_names = line.split()
                single_names += [line]
            else:
                single_names = [line]
            first_found = False
            ch_list = content_list
            for idx, elem in enumerate(ch_list):
                found = []
                for name in single_names:
                    if name == elem:
                        found.append(True)
                        break

                if len(found) > 0:
                    if not first_found:
                        TP += 1
                        first_found = True
                    del content_list[idx]
                if idx == len(ch_list)-1 and not first_found:
                    FN += 1
                    not_found.append(line)
        FP = len(content_list)
    print(f'TP: {TP} -- FP: {FP} -- FN: {FN}')
    print(f'Characters not found: {not_found}')
    FP_str = ''
    for char in content_list:
        FP_str += char + '\n'
    with open('../data/NER_FP_Persons.txt', 'w+') as FP_persons:
        FP_persons.write(FP_str)

    recall = TP/(TP+FN)
    precision = TP/(TP+FP)
    f1 = 2*(precision*recall)/(precision+recall)
    return f1


def majority_vote():
    with open('../data/NER_overall.json') as ner:
        ner_dict = json.load(ner)
        word_dict = {}
        for key in ner_dict.keys():
            ner_tags = ner_dict[key]
            for word in ner_tags:
                if not word in word_dict.keys():
                    word_dict[word] = {key: 1}
                elif key not in word_dict[word].keys():
                    word_dict[word][key] = 1
                else:
                    word_dict[word][key] += 1
        new_ner_dict = {key: [] for key in ner_dict.keys()}
        for word, ner_counters in word_dict.items():
            max_occuring_tag = max(ner_counters.items(),
                                   key=operator.itemgetter(1))[0]
            new_ner_dict[max_occuring_tag].append(word)
        with open('../data/NER_overall_majority_vote.json', 'w+') as majority:
            majority.write(json.dumps(new_ner_dict, indent=2))


def extract_chapters():
    with open('../data/chapters/chapterList.txt', 'r') as chaptersList:
        chapters = set([chapter.strip().upper() for chapter in chaptersList.readlines()])
    bookpath = Path('../data')
    for bp in bookpath.iterdir():
        if 'coref' in bp.name:
            with open(str(bp), 'r') as book:
                bookstr = book.read()
                chapter_dict = {}
                paragraphs = []
                cur_chapter = None
                for line in bookstr.split('\n\n'):
                    stripped = line.strip()
                    if stripped in chapters:
                        if cur_chapter is not None:
                            chapter_dict[cur_chapter] = paragraphs
                            paragraphs = []
                        cur_chapter = stripped
                        continue
                    paragraphs.append(line)
                with open(f'../data/chapters/{bp.name[:-4]}.json', 'w+') as json_book:
                    json_book.write(json.dumps(chapter_dict, indent=4))


if __name__ == "__main__":
    extract_chapters()
