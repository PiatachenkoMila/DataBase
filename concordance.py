import re

from database_functions import DatabaseFunctions
from splitter import TextSplitter


class Concordance:
    def __init__(self, ner_mode=False):
        self.dbf = DatabaseFunctions()
        self.ner_mode = ner_mode

    # функція для формування словника {словоформа: id словоформи}
    def generate_wordforms_dict(self):
        if self.ner_mode:
            table_name = "wordforms_ner"
        else:
            table_name = "wordforms"
        ids_dict = dict()
        list_of_words = \
            self.dbf.get_wordforms_and_ids_from_wordforms_table(table_name)
        for i in range(len(list_of_words)):
            id_ = list_of_words[i][0]
            word = list_of_words[i][1]
            ids_dict[word] = id_
        return ids_dict

    # розбиття корпусу на речення та додавання контекстів до бази
    def add_concordance_contexts_to_db(self, data):
        # знайдемо контексти, які вже є в базі
        contexts_and_ids = self.dbf.get_contexts()
        if len(contexts_and_ids) > 0:
            contexts_already_in_db = list(zip(*contexts_and_ids))[1]
        else:
            contexts_already_in_db = []
        # будемо зберігати пари {речення - id тексту},
        # а потім додамо ці пари до таблиці контекстів
        contexts = []
        ts = TextSplitter()
        data_len = len(data)
        print("Splitting into sentences")
        for index, record in enumerate(data):
            print(index + 1, data_len)
            text_id = record[0]
            content = record[1]
            # розбиття на речення
            sentences = ts.split_text(content, 0)
            for sentence in sentences:
                if sentence != "":
                    # контекст додається у випадку, коли його ще немає у базі
                    if sentence not in contexts_already_in_db:
                        contexts.append((sentence, text_id))
        # додавання контекстів до бази
        self.dbf.add_new_contexts_to_db(contexts)

    # визначення зв'язків словоформа - контекст
    def wordform_context_relation(self):
        if self.ner_mode:
            table_name = "wordform_context_relation_ner"
        else:
            table_name = "wordform_context_relation"
        # знайдемо зв'язки, які вже додано до бази
        relations_already_in_db = \
            self.dbf.get_wordform_context_relations(table_name)
        relations = []  # список для збереження зв'язків словоформа - контекст
        # з бази даних дістаємо контексти та їх id
        contexts_from_db = self.dbf.get_contexts_to_process(modif=2)
        # формуємо словник словоформ бази у форматі {словоформа: id словоформи)
        wordforms_from_db = self.generate_wordforms_dict()
        # w - словоформа, w_id - її id
        print("Wordform-context relation")
        counter = 1
        data_len = len(wordforms_from_db.items())
        for w, w_id in wordforms_from_db.items():
            print(counter, data_len)
            # регулярний вираз для виявлення словоформи у реченні
            p = "{0}{1}{0}".format(r"\b", w)
            for record in contexts_from_db:
                context_id = record[0]
                sentence = record[1]
                find = re.findall(p, sentence.lower())
                # якщо словоформу знайдено у реченні
                if len(find) > 0:
                    relation_to_insert = (w_id, context_id)
                    if relation_to_insert not in relations_already_in_db:
                        # додаємо зв'язок словоформи та контексту до списку
                        # relations, якщо його ще не додано до бази
                        relations.append(relation_to_insert)
            counter += 1
        # додавання зв'язків до бази
        self.dbf.add_new_wordform_context_relations_to_db(relations, table_name)

    def make_concordance(self):
        if not self.ner_mode:
            all_texts = self.dbf.get_all_texts_from_corpus(modif=2)
            self.add_concordance_contexts_to_db(all_texts)
        self.wordform_context_relation()
        if self.ner_mode:
            self.dbf.update_modif(old_value=2, new_value=3)
