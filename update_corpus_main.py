import traceback

from corpus_update import CorpusUpdate
from database_functions import DatabaseFunctions


class Program:
    def __init__(self):
        self.dbf = DatabaseFunctions()

    def updating_selected_corpus(self, corpus_id, corpus_class):
        try:
            if corpus_id == 1:
                newest_id = input(
                    "Enter id of the newest article in news blog: ")
                oldest_id = input(
                    "Enter id of the oldest article in news blog that you want to download: ")
                try:
                    newest_id = int(newest_id)
                    oldest_id = int(oldest_id)
                    corpus_class.download_articles(newest_id, oldest_id)
                except ValueError:
                    print("Enter value is not an integer number")
            else:
                if corpus_id == 2:
                    try:
                        last_page = corpus_class.last_page_num()
                        print("Last page at website:", last_page)
                    except ValueError:
                        print("Last page at website: <undefined>")
                start_page = input("Enter start page: ")
                end_page = input("Enter end page: ")
                try:
                    start_page = int(start_page)
                    end_page = int(end_page)
                    corpus_class.download_articles(start_page, end_page)
                except ValueError:
                    print("Enter value is not an integer number")
            article_links_from_db = self.dbf. \
                get_all_article_links_from_corpus(corpus_id)
            new_articles_links = set(corpus_class.articles_links). \
                difference(set(article_links_from_db))
            if corpus_id != 1:
                corpus_class.get_articles(new_articles_links)

            # Saving to database
            new_articles = corpus_class.articles.copy()
            for x in new_articles:
                x.append(corpus_id)
                x.append(0)
            self.dbf.add_downloaded_texts_to_corpus(new_articles)
            print("Update was successful.")
        except Exception as e:
            print("Unable to update.\n" + str(e) + traceback.format_exc())


def main():
    p = Program()
    print("Corpora update program")
    print("(Type 0 to exit)")
    print("Select corpus to update")
    corpora = p.dbf.get_all_corpora_names_and_links()
    for i, (corpus_name, update_link) in enumerate(corpora):
        print("{0}: {1} {2}".format(i + 1, corpus_name,
                                    update_link if update_link is not None
                                    else ""))
    while True:
        choice = input()
        try:
            choice = int(choice)
            if choice == 0:
                exit(0)
            elif 1 <= choice <= len(corpora):
                update = CorpusUpdate(choice)
                corpus = update.which_corpus_to_update()
                if corpus is None:
                    print(
                        "Unable to update this corpus. Choose a different one")
                else:
                    p.updating_selected_corpus(choice, corpus)
                break
            else:
                print("Incorrect number entered, try again")
        except ValueError:
            print("Entered value is not an integer number, try again.")


if __name__ == '__main__':
    main()
