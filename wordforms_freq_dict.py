import re

from concordance import Concordance
from database_functions import DatabaseFunctions
from splitter import TextSplitter


class Wordforms:
    def __init__(self, ner_mode=False):
        self.dbf = DatabaseFunctions()
        self.ner_mode = ner_mode

    # прочитання txt-файлу зі словоформами
    @staticmethod
    def read_from_file(filename):
        with open(filename, 'r', encoding='windows-1251') as f_in:
            data = f_in.read()
            f_in.close()
        return data

    @staticmethod
    # оброблення для додавання словоформ до поля term_wordforms таблиці термінів
    def process_file(data):
        new_chars = [34, 96]
        lines = data.split("\n")
        res = dict()
        for line in lines:
            if line != "":
                lex_and_wforms = line.split(":")
                lex = lex_and_wforms[0].lower()
                wforms = lex_and_wforms[1].lower()
                split_wordforms = wforms.split(";")
                new_wordform = []
                split_wordforms.append(lex)
                for w in split_wordforms:
                    if chr(39) in w:
                        for c in new_chars:
                            new_wordform.append(w.replace(chr(39), chr(c)))
                res[lex] = (lex + ";" + wforms + ";" + ";".join(new_wordform))
                res[lex] = res[lex].replace('"', '""')
                res[lex] = res[lex].replace(";;", ";")
        return res

    # оновлення словоформ в полі term_wordforms таблиці термінів
    def update_wordforms(self, data):
        if self.ner_mode:
            table_name = "terms_ner"
        else:
            table_name = "terms"
        for key in data.keys():
            self.dbf.update_wordforms_in_terms_table(key, data[key], table_name)

    # додавання нових словоформ до таблиці wordforms
    def process_wordforms(self):
        wordforms_to_insert = []
        # залежно від вибраного режиму, вказується назва таблиці, з якої буде
        # прочитано список словоформ термінів
        if self.ner_mode:
            terms_table_name = "terms_ner"
        else:
            terms_table_name = "terms"
        # Видобування списків словоформ термінів з відповідної таблиці
        # (id терміна, список його словоформ, розділений крапкою з комою)
        wordforms_list_of_specific_term = \
            self.dbf.get_wordforms_from_terms_table(terms_table_name)
        # Назва таблиці словоформ, де буде збережено словоформи
        if self.ner_mode:
            wordforms_table_name = "wordforms_ner"
        else:
            wordforms_table_name = "wordforms"
        # словоформи, які наявні в таблиці словоформ
        wordforms_already_in_db = \
            self.dbf.get_wordforms_from_wordforms_table(wordforms_table_name)
        for i in range(len(wordforms_list_of_specific_term)):
            # розглядається список словоформ певного терміна із таблиці термінів
            id_ = wordforms_list_of_specific_term[i][0]  # id терміна
            # перевіряється, чи в полі списку словоформ значення не NULL
            if wordforms_list_of_specific_term[i][1] is not None:
                # список словоформ подається як список окремих словоформ
                lex_and_wordforms = \
                    wordforms_list_of_specific_term[i][1].split(";")
                # розглядається кожна словоформа із списку словоформ
                for j in range(len(lex_and_wordforms)):
                    wordform = lex_and_wordforms[j]
                    # якщо словоформа не перебуває в таблиці словоформ,
                    # дана словоформа додається до таблиці з відповідним id
                    # терміна
                    if wordform != "" and wordform not in \
                            wordforms_already_in_db:
                        wordforms_to_insert.append((wordform, id_))
                    # словоформа поділяється на окремі слова
                    split_wform = wordform.split()
                    if len(split_wform) > 1:  # якщо слів в словоформі декілька
                        # відбувається заміна символа пробіла на символ
                        # нероздільного пробіла
                        new_wf = wordform.replace(chr(32), chr(160))
                        # якщо таку словоформу ще не додано
                        if new_wf != "" and new_wf not in \
                                wordforms_already_in_db:
                            # додається словоформа, слова якої розділено
                            # нероздільним пробілом
                            wordforms_to_insert.append((new_wf, id_))
        # збереження словоформ у відповідній таблиці словоформ бази даних
        self.dbf.add_new_wordforms_to_db(wordforms_to_insert,
                                         wordforms_table_name)

    def save_frequencies_to_db(self, frequency_dict, table_name):
        freqs = [(id_, frequency_dict[id_]) for id_ in frequency_dict.keys()]
        self.dbf.update_frequency(table_name, freqs)

    def wordforms(self, wordforms_file_name):
        data = self.process_file(self.read_from_file(wordforms_file_name))
        self.update_wordforms(data)
        self.process_wordforms()

    def frequencies(self):
        print("Loading texts from corpora")
        texts = self.dbf.get_all_texts_from_corpus(modif=1)
        if not texts:
            print("All texts have already been processed.")
            return
        texts = list(zip(*texts))[1]
        print("Texts to lower")
        texts_lower = [x.lower() for x in texts]
        corpus = "\n".join(texts).lower()
        ts = TextSplitter()
        if self.ner_mode:
            select_statement = "SELECT * FROM wordforms_ner"
        else:
            select_statement = "SELECT * FROM wordforms"
        all_wordforms = self.dbf.get_frequency_dict(select_statement, "1")
        single_wordforms_dict = dict()
        double_wordforms_dict = dict()
        # lexemes_id_dict - словник у форматі {id словоформи: id лексеми}
        lexemes_id_dict = dict()
        print("Splitting wordforms into single and double")
        for i in range(len(all_wordforms)):
            w_id = all_wordforms[i][0]
            wordform = all_wordforms[i][1]
            if chr(160) in wordform:
                continue
            lexemes_id_dict[w_id] = all_wordforms[i][2]
            split_wform = wordform.split()
            if len(split_wform) > 1:
                double_wordforms_dict[w_id] = split_wform
            else:
                single_wordforms_dict[w_id] = wordform
        count_double = 1
        print("Processing double wordforms")
        all_double = len(double_wordforms_dict.items())
        for key, value in double_wordforms_dict.items():
            try:
                print(count_double, all_double)
                print("Key:", key, "Value:", value)
                pattern = re.compile(r"{0}{1}{0}".format(r"\b",
                                                         "\s+".join(value)))
                matched = re.findall(pattern, corpus)
                if len(matched) > 0:
                    for m in range(len(matched)):
                        for i in range(len(texts_lower)):
                            texts_lower[i] = texts_lower[i].replace(matched[m],
                                                                    "_".join(value))
                double_wordforms_dict[key] = "_".join(value)
                count_double += 1
            except re.error:
                count_double += 1
        split_words = list()
        for i, t in enumerate(texts_lower):
            print("Splitting texts to words {}/{}".format(str(i + 1),
                                                          len(texts_lower)))
            split_words.extend(ts.split_text(t, 1))
        # словники у форматі {id: кількість вживань}
        freq_dict_wordforms = dict()
        freq_dict_lexemes = dict()
        print("Counting single wordforms")
        all_single = len(single_wordforms_dict.keys())
        counter = 1
        for w_id in single_wordforms_dict.keys():
            print(counter, all_single)
            w_form = single_wordforms_dict[w_id]
            freq = split_words.count(w_form)
            freq_dict_wordforms[w_id] = freq
            lex_id = lexemes_id_dict[w_id]
            if lex_id not in freq_dict_lexemes.keys():
                freq_dict_lexemes[lex_id] = 0
            freq_dict_lexemes[lex_id] += freq
            counter += 1
        all_double = len(double_wordforms_dict.keys())
        counter = 1
        print("Counting double wordforms")
        for w_id in double_wordforms_dict.keys():
            print(counter, all_double)
            w_form = double_wordforms_dict[w_id]
            freq = split_words.count(w_form)
            freq_dict_wordforms[w_id] = freq
            lex_id = lexemes_id_dict[w_id]
            if lex_id not in freq_dict_lexemes.keys():
                freq_dict_lexemes[lex_id] = 0
            freq_dict_lexemes[lex_id] += freq
            counter += 1
        print("Saving")
        for i in range(len(all_wordforms)):
            w_id = all_wordforms[i][0]
            lexemes_id_dict[w_id] = all_wordforms[i][2]
            if all_wordforms[i][3] is not None:
                freq_dict_wordforms[w_id] += all_wordforms[i][3]
                freq_dict_lexemes[lexemes_id_dict[w_id]] += all_wordforms[i][3]
        if self.ner_mode:
            wordforms_table = "wordforms_ner"
            terms_table = "terms_ner"
        else:
            wordforms_table = "wordforms"
            terms_table = "terms"
        self.save_frequencies_to_db(freq_dict_wordforms, wordforms_table)
        self.save_frequencies_to_db(freq_dict_lexemes, terms_table)
        if self.ner_mode:
            self.dbf.update_modif(old_value=1, new_value=2)

    def init_concordance(self):
        c = Concordance(self.ner_mode)
        c.make_concordance()

    @staticmethod
    def correct_alphabet_sorting(dictionary, reverse, invert):
        import locale
        locale.setlocale(locale.LC_ALL, "")
        dictionary = [list(x) for x in dictionary]
        if invert:
            for i in range(len(dictionary)):
                # Інвертуємо кожну словосполуку
                dictionary[i][0] = dictionary[i][0][::-1]
        sorted_dict = sorted(dictionary, key=lambda x: locale.strxfrm(x[0]),
                             reverse=reverse)
        if invert:
            for i in range(len(sorted_dict)):
                # Інвертуємо кожну словосполуку
                sorted_dict[i][0] = sorted_dict[i][0][::-1]
        return sorted_dict
