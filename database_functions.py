import sqlite3


class DatabaseFunctions:
    def __init__(self):
        self.conn = sqlite3.connect("dictionary.db")
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        sql_script = """
        CREATE TABLE IF NOT EXISTS "context" (
        "id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        "sentence"	TEXT,
        "text_id"	INTEGER);

        CREATE TABLE IF NOT EXISTS "corpora" (
        "id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        "corpus_name"	TEXT,
        "update_link"	TEXT);

        CREATE TABLE IF NOT EXISTS "corpora_texts" (
        "id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        "header"	TEXT,
        "content"	TEXT,
        "corpus_id"	INTEGER,
        "modif" INTEGER,
        "link"	TEXT,
        "ner_positions" TEXT);

        CREATE TABLE IF NOT EXISTS "terms" (
        "id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        "term"	TEXT,
        "definition"	TEXT,
        "term_wordforms"	TEXT,
        "freq"	INTEGER,
        "tran_term_id"	INTEGER);

        CREATE TABLE IF NOT EXISTS "terms_ner" (
        "id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        "term"	TEXT,
        "definition"	TEXT,
        "term_wordforms"	TEXT,
        "freq"	INTEGER,
        "tran_term_id"	INTEGER);

        CREATE TABLE IF NOT EXISTS "wordform_context_relation" (
        "wordform_id"	INTEGER,
        "context_id"	INTEGER);

        CREATE TABLE IF NOT EXISTS "wordform_context_relation_ner" (
        "wordform_id"	INTEGER,
        "context_id"	INTEGER);

        CREATE TABLE IF NOT EXISTS "wordforms" (	
        "id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        "wordform"	TEXT,
        "term_id"	INTEGER,
        "freq"	INTEGER);

        CREATE TABLE IF NOT EXISTS "wordforms_ner" (	
        "id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        "wordform"	TEXT,
        "term_id"	INTEGER,
        "freq"	INTEGER);

        CREATE TABLE IF NOT EXISTS "named_entities" (	
        "id"	INTEGER NOT NULL PRIMARY KEY,
        "entity"	TEXT,
        "entity_type"	TEXT,
        "ner_freq"  INTEGER);
        """
        self.cursor.executescript(sql_script)
        self.conn.commit()

    # функції передоброблення: додавання словоформ до бази та визначення
    # кількості вживань для словоформ

    # видобути словоформи з поля term_wordforms таблиці термінів
    def get_wordforms_from_terms_table(self, table_name):
        sql_command = """SELECT id, term_wordforms
                         FROM {0} """.format(table_name)
        self.cursor.execute(sql_command)
        result = self.cursor.fetchall()
        return result

    # заповнення поля словоформ в таблиці термінів
    def update_wordforms_in_terms_table(self, lex, wordforms, table_name):
        sql_command = """
        UPDATE {0}
        SET term_wordforms = "{1}"
        WHERE term = "{2}" """.format(table_name, wordforms, lex)
        self.cursor.execute(sql_command)
        self.conn.commit()

    # додати нові словоформи до таблиці словоформ
    def add_new_wordforms_to_db(self, data, table_name):
        self.cursor.execute("BEGIN TRANSACTION")
        for record in data:
            sql_command = """INSERT INTO {0}(wordform, term_id) 
                             VALUES(?,?)""".format(table_name)
            self.cursor.execute(sql_command, record)
        self.conn.commit()

    # видобути словоформи та їх id з таблиці wordforms
    def get_wordforms_and_ids_from_wordforms_table(self, table_name):
        sql_command = """
        SELECT id, wordform
        FROM {0}""".format(table_name)
        self.cursor.execute(sql_command)
        result = self.cursor.fetchall()
        return result

    # видобути словоформи з таблиці wordforms
    def get_wordforms_from_wordforms_table(self, table_name):
        sql_command = """
        SELECT wordform
        FROM {0}""".format(table_name)
        self.cursor.execute(sql_command)
        result = self.cursor.fetchall()
        result = [x[0] for x in result]
        return result

    # кінець функцій передоброблення

    # запит для фільтрації таблиці частотного словника
    def get_frequency_dict(self, select_statement, criteria):
        sql_command = """{0} WHERE {1}""".format(select_statement, criteria)
        self.cursor.execute(sql_command)
        result = self.cursor.fetchall()
        return result

    # визначення словоформ та їх частот за вказаною лексемою
    def get_wordform_frequencies(self, term, terms_table, wordforms_table):
        sql_command = """
        SELECT DISTINCT {2}.wordform, {2}.freq
        FROM {2}
        WHERE {2}.id
        IN
        (
            SELECT {2}.id
            FROM {2} JOIN {1}
            ON {2}.term_id={1}.id
            WHERE {1}.term = "{0}"
        )
        AND {2}.freq > 0
        ORDER BY freq DESC
        """.format(term, terms_table, wordforms_table)
        self.cursor.execute(sql_command)
        result = self.cursor.fetchall()
        return result

    # отримати тлумачне визначення вказаного терміну
    def get_term_definition(self, term, table_name):
        sql_command = """
        SELECT definition FROM {0} WHERE term="{1}" """.format(table_name, term)
        self.cursor.execute(sql_command)
        result = self.cursor.fetchone()
        return result[0]

    # функції для конкордансу:

    # додати контексти конкордансу до таблиці контекстів
    def add_new_contexts_to_db(self, data):
        self.cursor.execute("BEGIN TRANSACTION")
        for record in data:
            sql_command = """
            INSERT INTO context(sentence, text_id) VALUES(?,?)"""
            self.cursor.execute(sql_command, record)
        self.conn.commit()

    # додати відношення словоформа-контекст
    def add_new_wordform_context_relations_to_db(self, data, table_name):
        self.cursor.execute("BEGIN TRANSACTION")
        for record in data:
            sql_command = """INSERT INTO {0} (wordform_id, context_id) 
                             VALUES(?,?)""".format(table_name)
            self.cursor.execute(sql_command, record)
        self.conn.commit()

    # Видобути усі контексти конкордансу
    def get_contexts(self):
        sql_command = """SELECT id, sentence FROM context"""
        self.cursor.execute(sql_command)
        result = self.cursor.fetchall()
        return result

    def get_contexts_to_process(self, modif=0):
        sql_command = """SELECT context.id, context.sentence, context.text_id
        FROM context
        JOIN corpora_texts ON corpora_texts.id = context.text_id
        WHERE corpora_texts.modif = {0} """.format(modif)
        self.cursor.execute(sql_command)
        result = self.cursor.fetchall()
        return result

    # знаходження контекстів конкордансу вказаного терміну
    def get_contexts_of_given_term(self, term, terms_table, wordforms_table,
                                   wordform_context_relation_table,
                                   last_ukr_term_num):
        sql_command = """
        SELECT f1, f2, f3 FROM
        (
            SELECT context.text_id as f1, context.sentence as f2,
            context.id as f3, corpora_texts.corpus_id,
                CASE WHEN
                ({1}.id < {5} AND corpora_texts.corpus_id IN (2,4,5,6)) OR 
                ({1}.id > {4} AND corpora_texts.corpus_id IN (1,3))
                THEN 1 ELSE 0
            END AS my_field
            FROM context
            JOIN {3}
            ON context.id = {3}.context_id
            JOIN {2}
            ON {2}.id = {3}.wordform_id
            JOIN {1} ON {1}.id = {2}.term_id
            JOIN corpora_texts ON context.text_id = corpora_texts.id
            WHERE {1}.term = "{0}"
            GROUP BY {3}.context_id
            HAVING my_field = 1
        )""".format(term, terms_table, wordforms_table,
                    wordform_context_relation_table, last_ukr_term_num,
                    last_ukr_term_num + 1)
        self.cursor.execute(sql_command)
        result = self.cursor.fetchall()
        return result

    # Видобути усі дані з таблиці зв'язків словоформ та контекстів
    def get_wordform_context_relations(self, table_name):
        sql_command = """SELECT * FROM {0}""".format(table_name)
        self.cursor.execute(sql_command)
        result = self.cursor.fetchall()
        return result

    # Кінець функцій для конкордансу

    # заголовок, текст корпусу й індекс позицій іменованих сутностей
    # за вказаним id тексту
    def get_text_by_id(self, id_):
        sql_command = """
        SELECT header, content, ner_positions
        FROM corpora_texts WHERE id={0} """.format(id_)
        self.cursor.execute(sql_command)
        result = self.cursor.fetchone()
        return result

    # видобути всі тексти з бази (без поля заголовків)
    def get_all_texts_from_corpus(self, modif=0):
        sql_command = """SELECT id, content
                         FROM corpora_texts
                         WHERE modif={0} """.format(modif)
        self.cursor.execute(sql_command)
        result = self.cursor.fetchall()
        return result

    # оновлення частот для лексем / словоформ
    def update_frequency(self, table, frequencies):
        self.cursor.execute("BEGIN TRANSACTION")
        for record in frequencies:
            sql = """
            UPDATE {0}
            SET freq="{2}"
            WHERE id="{1}" """.format(table, *record)
            self.cursor.execute(sql)
        self.conn.commit()

    # визначити словоформи вказаного терміну
    def get_wordforms_by_term(self, term, terms_table, wordforms_table):
        sql_command = """
        SELECT {2}.wordform
        FROM {2}
        WHERE {2}.id
        IN
        (
            SELECT {2}.id
            FROM {2} JOIN {1}
            ON {2}.term_id={1}.id
            WHERE {1}.term = "{0}"    
        )
        """.format(term, terms_table, wordforms_table)
        self.cursor.execute(sql_command)
        result = self.cursor.fetchall()
        result = [str(x[0]) for x in result]
        return result

    def get_term_id_by_given_term(self, term, table_name):
        sql_command = """SELECT id FROM {0}
                         WHERE term = "{1}" """.format(table_name, term)
        self.cursor.execute(sql_command)
        result = self.cursor.fetchone()
        return result[0]

    def get_all_corpora_names_and_links(self):
        sql_command = """SELECT corpus_name, update_link FROM corpora """
        self.cursor.execute(sql_command)
        result = self.cursor.fetchall()
        return result

    def get_all_article_links_from_corpus(self, corpus_id):
        sql_command = """SELECT link FROM corpora_texts
        WHERE corpus_id = {0} """.format(corpus_id)
        self.cursor.execute(sql_command)
        result = self.cursor.fetchall()
        result = [str(x[0]) for x in result]
        return result

    def add_downloaded_texts_to_corpus(self, data):
        self.cursor.execute("BEGIN TRANSACTION")
        for record in data:
            sql_command = """
            INSERT INTO corpora_texts(header, content, link, corpus_id, modif)
            VALUES(?,?,?,?,?)"""
            self.cursor.execute(sql_command, record)
        self.conn.commit()

    def get_corpus_update_link(self, corpus_id):
        sql_command = """SELECT update_link FROM corpora
        WHERE id = {0} """.format(corpus_id)
        self.cursor.execute(sql_command)
        result = self.cursor.fetchall()
        result = [str(x[0]) for x in result]
        return result

    def get_term_by_its_id(self, id_, terms_table):
        sql_command = """SELECT term FROM {0} 
                         WHERE id = {1} """.format(terms_table, id_)
        self.cursor.execute(sql_command)
        result = self.cursor.fetchone()
        return result[0]

    def get_translation_term_id(self, term_id, table_name):
        sql_command = """SELECT tran_term_id FROM {0}
        WHERE id = {1} """.format(table_name, term_id)
        self.cursor.execute(sql_command)
        result = self.cursor.fetchone()
        return result[0]

    # видобути всі терміни з таблиці terms
    def get_all_terms_and_their_ids(self, terms_table):
        sql_command = """SELECT id, term FROM {0} """.format(terms_table)
        self.cursor.execute(sql_command)
        result = self.cursor.fetchall()
        return result

    def get_term_definition_by_term_id(self, id_, terms_table):
        # знайти тлумачення терміну за вказаним id терміну
        sql_command = """SELECT definition FROM {0}
        WHERE id={1} """.format(terms_table, id_)
        self.cursor.execute(sql_command)
        result = self.cursor.fetchone()
        return result[0]

    def get_context_by_its_id(self, id_):
        # знайти контекст за його id
        sql_command = """SELECT sentence FROM context
        WHERE id={0} """.format(id_)
        self.cursor.execute(sql_command)
        result = self.cursor.fetchone()
        return result[0]

    def add_new_named_entities(self, records):
        self.cursor.execute("BEGIN TRANSACTION")
        for record in records:
            sql = """
            INSERT INTO
            named_entities(id, entity,entity_type,ner_freq)
            VALUES(?,?,?,?)"""
            self.cursor.execute(sql, record)
        self.conn.commit()

    def update_corpora_with_ner_data(self, records):
        self.cursor.execute("BEGIN TRANSACTION")
        for record in records:
            sql = """
            UPDATE corpora_texts
            SET ner_positions="{1}"
            WHERE corpora_texts.id="{0}" """.format(*record)
            self.cursor.execute(sql)
        self.conn.commit()

    def select_named_entities_types(self, list_of_ids):
        sql_command = """SELECT named_entities.id, named_entities.entity_type
        FROM named_entities
        WHERE named_entities.id IN ({0}) """.format(list_of_ids)
        self.cursor.execute(sql_command)
        result = self.cursor.fetchall()
        return result

    def select_named_entities(self):
        sql_command = """SELECT named_entities.id, named_entities.entity,
        named_entities.entity_type, named_entities.ner_freq
        FROM named_entities """
        self.cursor.execute(sql_command)
        result = self.cursor.fetchall()
        return result

    def drop_table(self, table_name):
        sql_command = ""
        sql_command += "DROP TABLE IF EXISTS '{}'; ".format(table_name)
        self.cursor.executescript(sql_command)
        self.conn.commit()

    def update_modif(self, old_value, new_value):
        sql = """
        UPDATE corpora_texts
        SET modif={1}
        WHERE modif={0} """.format(old_value, new_value)
        self.cursor.execute(sql)
        self.conn.commit()
