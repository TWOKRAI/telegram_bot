import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense

# Загрузка данных
with open('greetings.txt', 'r', encoding='utf-8') as file:
    text = file.read().lower()

# Токенизация текста
tokenizer = Tokenizer(char_level=True)
tokenizer.fit_on_texts([text])
total_chars = len(tokenizer.word_index)

# Преобразование текста в последовательности
input_sequences = []
for line in text.split('\n'):
    token_list = tokenizer.texts_to_sequences([line])[0]
    for i in range(1, len(token_list)):
        n_gram_sequence = token_list[:i+1]
        input_sequences.append(n_gram_sequence)

# Паддинг последовательностей
max_sequence_len = max([len(x) for x in input_sequences])
input_sequences = np.array(tf.keras.preprocessing.sequence.pad_sequences(input_sequences, maxlen=max_sequence_len, padding='pre'))

# Подготовка данных для обучения
xs, labels = input_sequences[:,:-1], input_sequences[:,-1]
ys = to_categorical(labels, num_classes=total_chars + 1)

# Создание модели
model = Sequential()
model.add(Embedding(total_chars + 1, 10, input_length=max_sequence_len-1))
model.add(LSTM(150, return_sequences=True))
model.add(LSTM(100))
model.add(Dense(total_chars + 1, activation='softmax'))

# Компиляция модели
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# Обучение модели
model.fit(xs, ys, epochs=100, verbose=1)

# Генерация текста
def generate_text(seed_text, next_words=100, temperature=1.0):
    for _ in range(next_words):
        token_list = tokenizer.texts_to_sequences([seed_text])[0]
        token_list = tf.keras.preprocessing.sequence.pad_sequences([token_list], maxlen=max_sequence_len-1, padding='pre')
        predicted_probs = model.predict(token_list, verbose=0)[0]
        predicted_probs = np.log(predicted_probs) / temperature
        predicted_probs = np.exp(predicted_probs)
        predicted_probs = predicted_probs / np.sum(predicted_probs)
        predicted = np.random.choice(len(predicted_probs), p=predicted_probs)
        output_word = ""
        for word, index in tokenizer.word_index.items():
            if index == predicted:
                output_word = word
                break
        seed_text += output_word
    return seed_text

# Пример использования
name = "Иван"
seed_text = ""
generated_text = generate_text(seed_text, next_words=50, temperature=1.2)
generated_text = generated_text.replace("[NAME]", name)
print(generated_text)