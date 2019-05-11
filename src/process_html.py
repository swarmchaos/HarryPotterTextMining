from bs4 import BeautifulSoup
from pathlib import Path
import re

data = Path('data/htmlBooks')


def extract_text(file_path):
    with open(file_path, 'r') as file:
        soup = BeautifulSoup(file.read(), 'html.parser')
        return soup.pre.string


def write_data(text, path):
    with open(str(path), 'w+') as file:
        file.write(text)


def clean_data(text):
    ctext = re.sub(r'/', ' ', text)
    ctext = re.sub(r'P( )?a( )?g( )?e( )?\|( )?[0-9a-zA-Z]+( )?(\n)*Harry Potter [a-zA-Z ]+( )?-( )?J.K. Rowling', ' ', ctext)
#    ctext = ctext.replace('\n', ' ')
#    ctext = ctext.lower()
#    ctext = ' '.join(word.strip('"#$%&\'()*+,-/:;<=>?@[\\]^_`{|}~') for word in ctext.split())
    return ctext


if __name__ == "__main__":
    outPath = 'data/cleanedBooks/'
    for file_path in data.iterdir():
        text = extract_text(file_path)
        text = clean_data(text)
        write_data(text, outPath + file_path.name[:-14] + '.txt')
