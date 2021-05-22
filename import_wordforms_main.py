import argparse

from wordforms_freq_dict import Wordforms

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--wordforms-file', type=str,
                        default='WORDFORMS.txt',
                        help='path to wordforms txt file')
    parser.add_argument('--wordforms-file-ner', type=str,
                        default='WORDFORMS_ner.txt',
                        help='path to wordforms with ner txt file')
    args = parser.parse_args()
    Wordforms(ner_mode=False).wordforms(args.wordforms_file)
    Wordforms(ner_mode=True).wordforms(args.wordforms_file_ner)
