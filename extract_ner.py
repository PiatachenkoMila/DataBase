#!/usr/bin/python
# -*- coding: utf-8 -*-

import stanza  # імпорт бібліотеки stanza, що здійснює розпізнавання сутностей
# імпорт torch - бібліотеки машинного навчання, з якою працюють
# NER-моделі
import torch
# імпорт модуля з класом функцій для роботи з базою даних
from database_functions import DatabaseFunctions
# defaultdict - тип словника, в якому можна вказати тип для значення словника
from collections import defaultdict
# бібліотека time - для замірів часу виконання програми
from time import time


def determine_language(text):
    # визначення мови тексту
    try:
        eng_abc_range = range(65, 123)  # інтервал Unicode-символів англ. літер
        # інтервал Unicode-символів, в якому наявні всі укр. літери
        ukr_abc_range = range(1028, 1170)
        for c in text:
            # якщо хоча б символ з укр. алфавіту - мова укр.
            if ord(c) in ukr_abc_range:
                return "uk"
        # інакше мова - англ
        return "en"
    # в разі виникнення помилки з обробленням тексту - мова англійська
    except ValueError:
        return "en"


def main_ner():
    start_time = time()
    # виведення на екран версії PyTorch, що використовується
    print("PyTorch version", torch.__version__)
    # змінна, у якій зберігається частотний словник іменованих сутностей
    ner_freq = defaultdict(int)
    # word_int_dict - словник словників: {ім.сутн.:{тип сутності:id сутності}}
    word_int_dict = defaultdict(dict)
    # оголошення екземпляру класу для бази даних
    dbf = DatabaseFunctions()
    # виклик функції створення таблиць
    # (таблиця створюється, коли її ще не створено)
    dbf.create_tables()
    # вміст таблиці named_entities у базі даних
    entities_in_db = dbf.select_named_entities()
    for record_from_db in entities_in_db:
        # наповнення даними з таблиці named_entities
        word_int_dict[record_from_db[1]][record_from_db[2]] = record_from_db[0]
        # наповнення частотного словника іменованих сутностей
        ner_freq[record_from_db[0]] = record_from_db[3]
    # завантаження текстів з корпусу
    all_texts = dbf.get_all_texts_from_corpus(modif=0)
    # завантаження англійської моделі для розпізнавання сутностей
    stanza.download('en')
    # завантаження української моделі
    stanza.download('uk')
    # спеціальна змінна, яка ініціалізує модель для української мови
    nlp_ua = stanza.Pipeline(lang='uk',  # мова
                             processors='tokenize,ner',  # перелік обробників
                             ner_model_path='uk_languk_nertagger.pt',  # модель
                             ner_forward_charlm_path="",
                             ner_backward_charlm_path="")
    # ініціалізація моделі англійської мови
    nlp_en = stanza.Pipeline(lang='en', processors='tokenize,ner')
    # лічильник потрібний для того, щоб визначити id поточної іменованої сутн.
    counter = len(entities_in_db)
    le = len(all_texts)
    updating_rows = []
    for text_index, id_and_text in enumerate(all_texts):
        # заміна символа кінця рядка на символ пробіл
        text = id_and_text[1].replace("\n", " ")
        # виведення на екран індексу текста, що наразі обробляється
        print("{0}/{1}".format(text_index + 1, le))
        # словник зі списком індексів позицій іменованих сутностей
        positions_dict = defaultdict(list)
        # визначення мови
        language = determine_language(id_and_text[1])
        # застосування необхідної stanza-моделі відповідно до мови тексту
        if language == 'en':
            doc = nlp_en(text)
        else:
            doc = nlp_ua(text)
        for entity in doc.entities:
            try:
                # перевірка, чи дана іменована сутність з таким типом вже
                # була додана до словника
                word_int_dict[entity.text][entity.type]
            except KeyError:
                counter += 1  # збільшення лічильника на одиницю
                # додавання нової іменованої сутності до словника
                word_int_dict[entity.text][entity.type] = counter
            # видобування збереженого id збереженої іменованої сутності
            id_of_entity = word_int_dict[entity.text][entity.type]
            # додавання позицій іменованої сутності до словника індексу позицій
            positions_dict[id_of_entity].append([entity.start_char,
                                                 entity.end_char])
            ner_freq[id_of_entity] += 1  # підрахунок частоти даної ім. сутності
        # оброблення індексу позицій іменованої сутності до вигляду текстового
        # рядка
        positions_as_string = parse_positions_dict(positions_dict)
        # збереження до списку: id тексту в таблиці corpora_texts та рядок
        # індексу позицій буде збережено до поля ner_positions
        updating_rows.append((id_and_text[0], positions_as_string))
    recs = []
    # збір даних із словника word_int_dict, зведення до вигляду структури
    # таблиці named_entities
    for entity, v in word_int_dict.items():
        for entity_type, entity_id in v.items():
            recs.append((entity_id, entity, entity_type, ner_freq[entity_id]))
    dbf.drop_table("named_entities")  # видалення старої версії таблиці
    dbf.create_tables()  # таблиця named_entities створюється заново
    # збереження нових даних до таблиці named_entities
    dbf.add_new_named_entities(recs)
    # збереження індексу позиції до поля ner_positions таблиці corpora_texts
    dbf.update_corpora_with_ner_data(updating_rows)
    # оновлення ідентифікатора modif - розпізнавання іменованих сутностей
    # для даних текстів
    dbf.update_modif(old_value=0, new_value=1)
    end_time = time()  # завершення відліку часу
    # Виведення на екран інформації про час виконання
    print("Elapsed time {0} seconds".format(str(end_time - start_time)))
    print("Done")


def parse_positions_dict(dict_of_ner_positions):
    # зміна result - результат оброблення індексу у вигляді текстового рядка
    result = "["
    # для кожного елемента у словнику
    for index_i, (entity_id, list_of_positions) in \
            enumerate(dict_of_ner_positions.items()):
        # додавання id сутності
        result += str(entity_id) + ":"
        # розглядається список позицій даної іменованої сутності
        for position_index, position in enumerate(list_of_positions):
            # додається позиція (індекс_поч.поз., індекс_кінц.поз.)
            result += "({0},{1})".format(*position)
            # коли позиція в списку не є останньою,
            # потрібно вставити роздільник |
            if position_index < len(list_of_positions) - 1:
                result += "|"
            else:
                result += ";"  # коли позиція остання в списку - роздільник ;
    result += "]"
    return result


if __name__ == '__main__':
    main_ner()
