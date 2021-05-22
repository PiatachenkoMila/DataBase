import re


class TextSplitter:
    @staticmethod
    def multiple_symbols(s, text):
        pattern = "[" + s + "<stop>]{2,}"
        find_multiple_dots = re.findall(pattern, text)
        for md in find_multiple_dots:
            if "<stop>" not in md:
                continue
            else:
                d_list = md.split("<stop>")
                md1 = ""
                for symbol in d_list:
                    md1 += symbol
                md1 += "<stop>"
                text = text.replace(md, md1)
        return text

    @staticmethod
    def split_text(text, param):
        # param = 1 => split on words
        # param = 0 => split on sentences
        emails = r'[\w\.-]+@[\w\.-]+'
        caps = "([A-Z|А|Б|В|Г|Ґ|Д|Е|Є|Ж|З|И|І|Ї|Й|К|Л|М|Н|О|П|Р|С|Т|У|Ф|Х|Ц|Ч|Ш|Щ|Ь|Ю|Я|])"
        prefixes = "(Mr|St|Mrs|Ms|Dr|Дж|Англ|англ|тис|мол| с| м)[.]"
        suffixes = "(Inc|Ltd|Jr|Sr|Co|Bros)"
        starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
        acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
        websites = "[.](com|net|org|io|gov)"
        digits = "([0-9])"
        quotes_pattern1 = '«([^«]*)»'
        quotes_pattern2 = '"([^"]*)"'
        quotes_pattern3 = '“([^“]*)”'
        braces_pattern1 = '\(([^(]*)\)'
        braces_pattern2 = '\{([^{]*)\}'
        braces_pattern3 = '\[([^[]*)\]'
        dash_pattern = '\s+\-([^-]*\?\s+\-)+'
        million_pattern = "млн\.\s*[a-zа-яіїєґ\(\"]+"
        billion_pattern = "млрд\.\s*[a-zа-яіїєґ\(\"]+"
        text = " " + text + "  "
        find_em = re.findall(emails, text)
        for em in find_em:
            if "." in em:
                em1 = em.replace(".", "<email>")
                text = text.replace(em, em1)
        find_mil_bil = []
        find_million = re.findall(million_pattern, text)
        find_billion = re.findall(billion_pattern, text)
        find_mil_bil.extend(find_million)
        find_mil_bil.extend(find_billion)
        for em in find_mil_bil:
            if "." in em:
                em1 = em.replace(".", "<prd>")
                text = text.replace(em, em1)
        find_qt1 = re.findall(quotes_pattern1, text)
        find_qt2 = re.findall(quotes_pattern2, text)
        find_qt3 = re.findall(quotes_pattern3, text)
        find_qt = list()
        find_qt.extend(find_qt1)
        find_qt.extend(find_qt2)
        find_qt.extend(find_qt3)
        for em in find_qt:
            last = em
            if "." in em:
                em1 = last.replace(".", "<quotedot>")
                text = text.replace(last, em1)
                last = em1
            if "!" in em:
                em2 = last.replace("!", "<quoteexc>")
                text = text.replace(last, em2)
                last = em2
            if "?" in em:
                em3 = last.replace("?", "<quoteques>")
                text = text.replace(last, em3)
        find_br1 = re.findall(braces_pattern1, text)
        find_br2 = re.findall(braces_pattern2, text)
        find_br3 = re.findall(braces_pattern3, text)
        find_braces = list()
        find_braces.extend(find_br1)
        find_braces.extend(find_br2)
        find_braces.extend(find_br3)
        for em in find_braces:
            last = em
            if "." in em:
                em1 = last.replace(".", "<bracedot>")
                text = text.replace(last, em1)
                last = em1
            if "!" in em:
                em2 = last.replace("!", "<braceexc>")
                text = text.replace(last, em2)
            if "?" in em:
                em3 = last.replace("?", "<braceques>")
                text = text.replace(last, em3)
        find_dash = re.findall(dash_pattern, text)
        for em in find_dash:
            last = em
            if "." in em:
                em1 = last.replace(".", "<dashdot>")
                text = text.replace(last, em1)
                last = em1
            if "!" in em:
                em2 = last.replace("!", "<dashexc>")
                text = text.replace(last, em2)
            if "?" in em:
                em3 = last.replace("?", "<dashques>")
                text = text.replace(last, em3)
        text = text.replace("\n", " <endl>")
        text = re.sub(prefixes, "\\1<prd>", text)
        text = re.sub(websites, "<prd>\\1", text)
        if "E! online" in text:
            text = text.replace("E! online", "E<braceexc> online")
        if "н.е." in text:
            text = text.replace("н.е.", "н<prd>е<prd>")
        if "н. е." in text:
            text = text.replace("н. е.", "н<prd> е<prd>")
        if "т.д." in text:
            text = text.replace("т.д.", "т<prd>д<prd>")
        if "т. д." in text:
            text = text.replace("т. д.", "т<prd> д<prd>")
        if "Ph.D" in text:
            text = text.replace("Ph.D.", "Ph<prd>D<prd>")
        if "a.m" in text:
            text = text.replace("a.m", "a<prd>m<prd>")
        if "a. m" in text:
            text = text.replace("a. m", "a<prd> m<prd>")
        if "p.m" in text:
            text = text.replace("p.m", "p<prd>m<prd>")
        if "p. m" in text:
            text = text.replace("p. m", "p<prd> m<prd>")
        text = re.sub("\s" + caps + "[.] ", " \\1<prd> ", text)
        text = re.sub(acronyms + " " + starters, "\\1<stop> \\2", text)
        text = re.sub(caps + "[.]" + caps + "[.]" + caps + "[.]", "\\1<prd>\\2<prd>\\3<prd>", text)
        text = re.sub(caps + "[.]" + caps + "[.]", "\\1<prd>\\2<prd>", text)
        text = re.sub(" " + suffixes + "[.] " + starters, " \\1<stop> \\2", text)
        text = re.sub(" " + suffixes + "[.]", " \\1<prd>", text)
        text = re.sub(" " + caps + "[.]", " \\1<prd>", text)
        text = re.sub(digits + "[.]" + digits, "\\1<prd>\\2", text)
        if "”" in text:
            text = text.replace(".”", "”.")
        if "\"" in text:
            text = text.replace(".\"", "\".")
        if "!" in text:
            text = text.replace("!\"", "\"!")
        if "?" in text:
            text = text.replace("?\"", "\"?")
        text = text.replace(".", ".<stop>")
        text = text.replace("?", "?<stop>")
        text = text.replace("!", "!<stop>")
        text = text.replace("<email> ", ".<stop> ")
        endl_pattern = '<stop>\s*<endl>'
        find_endl = re.findall(endl_pattern, text)
        for em in find_endl:
            em1 = '<stop>'
            text = text.replace(em, em1)
        text = text.replace(" <endl>", "<stop>")
        text_for_words = text
        text_for_words = text_for_words.replace("’.<stop>", "’..<stop>")
        text_for_words = text_for_words.replace(".<stop>", "<stop>")
        text_for_words = text_for_words.replace("!<stop>", "<stop>")
        text_for_words = text_for_words.replace("?<stop>", "<stop>")
        prepare_sentences = text_for_words.split("<stop>")
        words_in_sentences = list()
        for k in range(len(prepare_sentences)):
            prepare_sentences[k] = prepare_sentences[k].replace("<quotedot>", "")
            prepare_sentences[k] = prepare_sentences[k].replace("<quoteexc>", "")
            prepare_sentences[k] = prepare_sentences[k].replace("<quoteques>", "")
            prepare_sentences[k] = prepare_sentences[k].replace("<bracedot>", "")
            prepare_sentences[k] = prepare_sentences[k].replace("<braceexc>", "")
            prepare_sentences[k] = prepare_sentences[k].replace("<braceques>", "")
            prepare_sentences[k] = prepare_sentences[k].replace("<dashdot>", "")
            prepare_sentences[k] = prepare_sentences[k].replace("<dashexc>", "")
            prepare_sentences[k] = prepare_sentences[k].replace("<dashques>", "")
            prepare_sentences[k] = prepare_sentences[k].replace("<prd>", ".")
            prepare_sentences[k] = prepare_sentences[k].replace("- ", "")
            prepare_sentences[k] = prepare_sentences[k].replace("’.", "")
            prepare_sentences[k] = prepare_sentences[k].replace("’,", " ")
            prepare_sentences[k] = prepare_sentences[k].replace("’ ", " ")
            prepare_sentences[k] = prepare_sentences[k].replace(".", "")
            prepare_sentences[k] = prepare_sentences[k].replace("!", "")
            prepare_sentences[k] = prepare_sentences[k].replace("?", "")
            prepare_sentences[k] += ' '
            prepare_sentences[k] = prepare_sentences[k].replace(" '", " ")
            prepare_sentences[k] = prepare_sentences[k].replace("' ", " ")
            prepare_sentences[k] = prepare_sentences[k].replace("<email>", ".")
            list_of_words_in_sentence = re.split(r'[|^‘;«“\\—&#$”»{\}\[\]:(),\s]\s*', prepare_sentences[k])
            j = 0
            while j < (len(list_of_words_in_sentence)):
                if list_of_words_in_sentence[j] == '':
                    list_of_words_in_sentence.remove(list_of_words_in_sentence[j])
                    j -= 1
                j += 1
            if len(list_of_words_in_sentence) > 0:
                for i in range(len(list_of_words_in_sentence)):
                    if list_of_words_in_sentence[i] != "":
                        if list_of_words_in_sentence[i][-1] == '"':
                            list_of_words_in_sentence[
                                i] = list_of_words_in_sentence[i][:-1]
                        if list_of_words_in_sentence[i] != "":
                            if list_of_words_in_sentence[i][0] == '"':
                                list_of_words_in_sentence[
                                    i] = list_of_words_in_sentence[i][1:]
                words_in_sentences.extend(list_of_words_in_sentence)
        text = text.replace("<quotedot>", ".")
        text = text.replace("<quoteexc>", "!")
        text = text.replace("<quoteques>", "?")
        text = text.replace("<bracedot>", ".")
        text = text.replace("<braceexc>", "!")
        text = text.replace("<braceques>", "?")
        text = text.replace("<dashdot>", ".")
        text = text.replace("<dashexc>", "!")
        text = text.replace("<dashques>", "?")
        text = TextSplitter.multiple_symbols("\.", text)
        text = TextSplitter.multiple_symbols("\?", text)
        text = TextSplitter.multiple_symbols("!", text)
        text = text.replace("<prd>", ".")
        text = text.replace("<email>", ".")
        sentences = text.split("<stop>")
        sentences = [s.strip() for s in sentences]
        if '' in sentences:
            sentences.remove('')
        if param == 0:
            return sentences
        return words_in_sentences
