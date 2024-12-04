from natasha import Segmenter, MorphVocab, NewsEmbedding, NewsMorphTagger, NewsNERTagger, Doc
from textblob import TextBlob


# Инициализация морфологического анализатора
segmenter = Segmenter()
morph_vocab = MorphVocab()
emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)

def convert_to_nominative(city: str) -> str:
    """
    Функция для преобразования названия города в именительный падеж.
    """
    doc = Doc(city)
    doc.segment(segmenter)
    doc.tag_morph(morph_tagger)
    for token in doc.tokens:
        token.lemmatize(morph_vocab)
        if token.lemma:
            return token.lemma
    return city

def contains_any_word(word_list, string):
    # Преобразуем строку и слова к нижнему регистру
    string = string.lower()
    word_list = [word.lower() for word in word_list]

    # Проверяем каждое слово из списка
    for word in word_list:
        if word in string:
            return True
    return False

def find_next_word(target_word, string):
    print('find_next_word', string, target_word)
    # Преобразуем строку и целевое слово к нижнему регистру
    string_lower = string.lower()
    target_word_lower = target_word.lower()

    target_word_nominative = convert_to_nominative(target_word_lower)

    # Разбиваем строку на слова
    words = string.split()
    words_lower = string_lower.split()

    # Ищем индекс целевого слова
    try:
        index = words_lower.index(target_word_nominative)
    except ValueError:
        return None  # Целевое слово не найдено

    # Проверяем, есть ли следующее слово
    if index + 1 < len(words):
        return words[index + 1]
    else:
        return None  # Нет следующего слова

def analyze_sentiment(text: str) -> str:
    analysis = TextBlob(text)
    if analysis.sentiment.polarity > 0:
        return 'позитивное'
    elif analysis.sentiment.polarity == 0:
        return 'нейтральное'
    else:
        return 'негативное'