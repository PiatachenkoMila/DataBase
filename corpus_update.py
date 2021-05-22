from database_functions import DatabaseFunctions
from web_scrapers.cinemablend_com import CinemaBlendArticles
from web_scrapers.kinofilms_ua import KinofilmsArticles
from web_scrapers.kinoteatr_ua import KinoteatrArticles
from web_scrapers.moviestape_net import MoviestapeArticles


class CorpusUpdate:
    def __init__(self, corpus_id):
        self.dbf = DatabaseFunctions()
        self.corpus_id = corpus_id
        self.corpus_update_link = self.dbf. \
            get_corpus_update_link(self.corpus_id)[0]
        moviestape = MoviestapeArticles()
        cinemablend = CinemaBlendArticles()
        kinofilms = KinofilmsArticles()
        kinoteatr = KinoteatrArticles()
        self.corpora = [moviestape, cinemablend, kinofilms, kinoteatr]

    def which_corpus_to_update(self):
        for corpus in self.corpora:
            if self.corpus_update_link == corpus.page1_url:
                return corpus
        return None
