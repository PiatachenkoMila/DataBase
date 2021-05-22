from wordforms_freq_dict import Wordforms

if __name__ == '__main__':
    Wordforms(ner_mode=False).init_concordance()
    Wordforms(ner_mode=True).init_concordance()
