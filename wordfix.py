import re
from math import log
from os import path

"""
Word Fix
========
Fix all the misspelled words and space related mistakes in your document. Incorrect words and mistakenly inserted or omitted space within words are a very common issue with OCR.

The package has three functions: split, join, fix.
- Use fix() if you want all the errors to be automatically identified and corrected accordingly.
- Use fix_space() if you want to correct all space related mistakes
- Use split() if you only need to split incorrect words.
- Use join() if you only need to join incorrect words.
- Use spell() if you only need to correct spelling mistakes.

Usage
-----
python
>>> import wordfix as wf
>>> wf.split("theviews of physicianspracticing in relevantclinical areas.")
'the views of physicians practicing in relevant clinical areas.'

>>> wf.join("Agre ement betw een Anth em a nd")
'Agreement between Anthem and'

>>> wf.spell("anb Reuemue Oodes cr tbcir suooessors.")
'and Revenue Codes or their successors.'

>>> wf.fix('''T he co des includebutare not li m ite d to, AmericanMedical Association CurrentProcedural Termino logy ("CPT®-4"),
 CMS Healthcare CommonProcedure Coding System ("HCPCS"), International Classification of Diseases, 10th Revision,
  Clinical Modification ("ICD-10-CM"), National Drug Code ("NDC"), and Revenue Codes or their successors.''')

'The codes include but are not limited to, American Medical Association Current Procedural Terminology ("CPT®-4"),
 CMS Healthcare Common Procedure Coding System ("HCPCS"), International Classification of Diseases, 10th Revision,
  Clinical Modification ("ICD-10-CM"), National Drug Code ("NDC"), and Revenue Codes or their successors.'


Features
--------
Not only words, you can directly pass an entire document text to the fix method.
The package will handle the punctuations properly.

You can add or remove any words as per the language/domain to the dictionary file(en_words_cleaned.txt) located at the data directory.
"""
from symspellpy import SymSpell, Verbosity

class WordModel(object):
    def __init__(self, joiner, splitter, speller):
        with open(speller) as f:
        # with open(joiner) as f:
            # self.vocab = set(f.read().split())
            self.vocab = set([i.split()[0] for i in f.read().split()])

        # Build a cost dictionary, assuming Zipf's law and cost = -math.log(probability).
        with open(splitter) as f:
            words = [i.split()[0] for i in f.read().split()]
        self._wordcost = dict((k, log((i + 1) * log(len(words)))) for i, k in enumerate(words))
        self._maxword = max(len(x) for x in words)
        # self._SPLIT_WORD = re.compile("[^a-zA-Z0-9']+")
        self._SPLIT_WORD = re.compile(r"\s+")
        self._SPLIT_PHRASE = re.compile(r"(\s*[^\w '\-]+\s*)")

        self.sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
        self.sym_spell.load_dictionary(speller, term_index=0, count_index=1)



    ## Methods for joining
    def join_whole(self, s):
        ## Tries to join all the words together, does not check for subsets
        words = re.split(self._SPLIT_WORD, s)
        joined_word = "".join(words).strip()

        #TODO check only if the first letter capitalized word is correct. Discard all camcelcase words
        if (not all([w in self.vocab for w in words])) and joined_word.lower() in self.vocab:
            return joined_word, True
        else:
            return s, False

    def join_linear_progressive(self, s):
        final_text = ""
        while s:
            joined = False
            words = re.split(self._SPLIT_WORD, s)
            for i in range(2, len(words) + 1):
                ## check if the first i words can be joined
                if self.join_whole(" ".join(words[:i]))[1]:
                    final_text += self.join_whole(" ".join(words[:i]))[0] + " "
                    ## remove the first i words from s and stores them in final_text
                    s = " ".join(words[i:])
                    joined = True
                    break
            if not joined:
                final_text += words[0] + " "
                s = " ".join(words[1:])

        return final_text.strip()

    def join(self, s):
        joined = self.join_linear_progressive(s)
        while s != joined:
            s = joined
            joined = self.join_linear_progressive(joined)
        return joined


    ### Methods for splitting
    def split(self, s):
        """Uses dynamic programming to infer the location of spaces in a string without spaces."""
        l = []
        for x in self._SPLIT_WORD.split(s):
            if (len(x) > 1 and x.isupper()) or not x.isalpha():
                l.append(x)
            else:
                l.append(self._split_phrase(x))

        out = ""
        for w in l:
            if isinstance(w, str):
                out += w+" "
            else:
                out += " ".join(w)+" "

        # l = [self._split_phrase(x) for x in self._SPLIT_WORD.split(s)]
        # return " ".join([item for sublist in l for item in sublist])
        return out.strip()

    def _split_phrase(self, s):
        '''Created this method from http://stackoverflow.com/a/11642687/
        '''
        # Find the best match for the i first characters, assuming cost has
        # been built for the i-1 first characters.
        # Returns a pair (match_cost, match_length).
        if s in self._wordcost.keys():
            return s # if the word exist in dict then do not split

        def best_match(i):
            candidates = enumerate(reversed(cost[max(0, i - self._maxword):i]))
            return min((c + self._wordcost.get(s[i - k - 1:i].lower(), 9e999), k + 1) for k, c in candidates)

        # Build the cost array.
        cost = [0]
        for i in range(1, len(s) + 1):
            c, k = best_match(i)
            cost.append(c)

        # Backtrack to recover the minimal-cost string.
        out = []
        i = len(s)
        while i > 0:
            c, k = best_match(i)
            assert c == cost[i]
            # Apostrophe and digit handling
            newToken = True
            if not s[i - k:i] == "'":  # ignore a lone apostrophe
                if len(out) > 0:
                    # re-attach split 's and split digits
                    if out[-1] == "'s" or (s[i - 1].isdigit() and out[-1][0].isdigit()):  # digit followed by digit
                        out[-1] = s[i - k:i] + out[-1]  # combine current token with previous token
                        newToken = False

            if newToken:
                out.append(s[i - k:i])

            i -= k

        for i in out:
            if i not in self._wordcost.keys():
                return s
        return reversed(out)

    ## Methods for spell correction
    def spell(self, phrase):
        words = self._SPLIT_WORD.split(phrase)
        out = []
        for w in words:
            if (len(w) > 1 and w.isupper()) or not w.isalpha():
                out.append(w)
            else:
                suggestion = self.sym_spell.lookup(w, Verbosity.TOP,
                                        include_unknown=True, transfer_casing=True)[0].term
                if suggestion.lower() == w.lower():
                    out.append(w)
                else:
                    out.append(suggestion)

        return " ".join(out)

    ## Tokenize the phrases or subsentences and handle punctuations separately
    def fix_para(self, para, func):
        '''Split the paragraph(multiple sentences) into phrases using the splitter tokens(fullstop/comma etc)
        and then apply join and split at each phrases. After that join them back with the original splitter tokens'''
        phrases = self._SPLIT_PHRASE.split(para)
        # print(phrases)
        out = ""
        for ph in phrases:
            if not self._SPLIT_PHRASE.match(ph):
                # out += self.split(self.join_phrase(ph))
                out += func(ph)
            else:
                out += ph

        return out



DATA_DIR = './data'
long_list = path.join(DATA_DIR, 'en_words_cleaned.txt')
freq_ordered = path.join(DATA_DIR, 'frequency_dictionary_en_82_765.txt')

model = WordModel(joiner=long_list, splitter=freq_ordered, speller=freq_ordered)


## Class methods
def split(s):
    return model.fix_para(s.strip(), model.split)

def join(s):
    return model.fix_para(s.strip(), model.join)

def spell(s):
    return model.fix_para(s.strip(), model.spell)

def fix_space(s):
    return model.fix_para(s.strip(), lambda x: model.split(model.join(x)))

def fix(s):
    return model.fix_para(s.strip(), lambda x: model.split(model.spell(model.join(x))))
    # return model.fix_para(s.strip(), lambda x: model.spell(model.split(model.join(x))))


if __name__ == "__main__":
    import time, difflib
    # print(join("hos pi tal"))
    # print(split("verybadweather"))
    txt = '''T he co des includebutare not li m ite d to, AmericanMedical Association CurrentProcedural Termino logy ("CPT®-4"),
     CMS Healthcare CommonProcedure Coding System ("HCPCS"), International Classification of Diseases, 10th Revision,
     Clinical Modification ("ICD-10-CM"), National Drug Code ("NDC"), anb Reuemue Oodes cr tbcir suooessors.'''

    start_time = time.time()
    print(txt, "\n_____________________")
    fixed = fix(txt)
    print(fixed)
    print("Execution time: ", time.time() - start_time, fixed == txt)
