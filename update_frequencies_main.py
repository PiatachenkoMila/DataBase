from wordforms_freq_dict import Wordforms

if __name__ == '__main__':
    Wordforms(ner_mode=False).frequencies()
    Wordforms(ner_mode=True).frequencies()
