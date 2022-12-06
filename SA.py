import joblib
import pymorphy2
import re



loaded_model = joblib.load('dumpsvc.sav')

lemmatizer = pymorphy2.MorphAnalyzer()


def textnormalization(text, lemmatizer=pymorphy2.MorphAnalyzer()):
    ''' Приведение русского текста к нормальной форме'''

    text = text.lower()
    text = re.sub("ё", "е", text)
    text = re.sub("[^а-я]+", " ", text)
    while "  " in text:
        text = re.sub("  ", " ", text)
    text = text.split(' ')
    atext = ''
    for tx in text:
        txt = lemmatizer.normal_forms(tx)
        atext = atext + ' ' + txt[0]
    if atext[0] == ' ':
        atext = atext[1:]
    if atext[-1] == ' ':
        atext = atext[:-1]
    # print(atext)
    return atext

n = int(input('Сколько будет отзывов?'))
sen = []

for i in range(n):
    otz = input(f'Введите отзыв номер {i+1}:')
    sen.append(otz)


for s in sen:
    sn = textnormalization(s, lemmatizer)
    print('Отзыв:', s)
    o = loaded_model.predict([sn])[0]
    if o==0:
        print('Отзыв отрицательный' )
    else:
        print('Отзыв положительный' )
