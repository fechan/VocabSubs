import pysubs2
from fugashi import Tagger
from jamdict import Jamdict

class VocabInjector:
    def __init__(self, pos_excludes = [], vocab_max_appearances = -1, appearances_carryover = False,
            max_gloss_terms = -1, sub_filter = lambda x: True, lemma_excludes = []):
        """Construct a VocabInjector, used for injecting vocab lists into subtitle files

        Keyword arguments:
        pos_excludes -- parts of speech to exclude (default: exclude nothing)
        vocab_max_appearances -- max times a word should have its definition appear (default: no maximum)
        appearances_carryover -- whether the # of appearances a word has should carry over multiple files (default: False)
        max_gloss_terms -- max # of terms in a definition ("する: to do, to wear" has 2 terms) (default: no maximum)
        sub_filter -- function determining if a subtitle event should be processed (default: accept everyting)
        lemma_excludes -- lemmas to exclude from being defined (default: exclude nothing)
        """
        self.pos_excludes = pos_excludes
        self.vocab_max_appearances = vocab_max_appearances
        self.appearances_carryover = appearances_carryover
        self.max_gloss_terms = max_gloss_terms
        self.sub_filter = sub_filter
        self.lemma_excludes = set(lemma_excludes)

        self.vocab_occurrences = {} # looks like {"lemma": int}
        self.vocab_cache = {} # looks like {"lemma": "definition"}

        self.tagger = Tagger("-Owakati")
        self.jmd = Jamdict()

    def insert_vocab_lists(self, subtitle_file, output_file):
        """Uses the input subtitle file to output a version that also contains a vocab list.

        subtitle_file -- filename of the input sub file
        output_file -- filename of the output file
        """
        subs = pysubs2.load(subtitle_file)
        for event in subs:
            if self.sub_filter(event):
                text = event.plaintext
                if text == "": continue

                event_seen_words = []
                for word in self.tagger(text):
                    if word.feature.pos1 in self.pos_excludes: continue

                    try:
                        lemma = word.feature.lemma
                        if lemma in self.lemma_excludes:
                            print(f"Skipping {word} because its lemma ({lemma}) appears in the lemma exclude list")
                        elif lemma in event_seen_words:
                            print(f"Skipping {word} because it appears more than once in this event")
                        elif (self.vocab_max_appearances > -1 and # -1 for no maximum
                                lemma in self.vocab_occurrences and # lemma has appeared
                                self.vocab_occurrences[lemma] >= self.vocab_max_appearances):
                            print(f"Skipping {word} because it appeared too many times in this file")
                        else:
                            if lemma in self.vocab_cache:
                                definition = self.vocab_cache[lemma]
                            else:
                                definition = self.jmd.lookup(lemma)
                                definition = definition.entries[0].senses[0]
                                if self.max_gloss_terms > -1:
                                    definition = definition.gloss[:self.max_gloss_terms]
                                else:
                                    definition = definition.gloss
                                definition = ", ".join([str(term) for term in definition])
                                self.vocab_cache[lemma] = definition

                            new_text = f"{word}\t{definition}"
                            print("Inserting", new_text)
                            subs.insert(-1, pysubs2.SSAEvent(start=event.start, end=event.end, text=new_text))

                        event_seen_words.append(lemma)
                        if lemma in self.vocab_occurrences:
                            self.vocab_occurrences[lemma] += 1
                        else:
                            self.vocab_occurrences[lemma] = 1
                    except (IndexError, ValueError):
                        print("Failed to get definition of", word)
        subs.save(output_file)
        if not self.appearances_carryover:
            self.vocab_occurrences = {}

    def add_definition(self, lemma, definition):
        """Add a lemma and its definition to the vocab cache.
        This will force the injector to use the added definition rather than the one in the database
        and will be exempt from being shortened by max_gloss_terms
        
        lemma -- the lemma to be defined
        definition -- the definition of the lemma
        """
        self.vocab_cache[lemma] = definition

    def set_lemma_excludes(self, lemma_excludes):
        """Set the lemma exclude list.
        The injector will not define lemmas included in the exclude list.

        lemma_excludes -- list of lemmas to exclude
        """
        self.lemma_excludes = set(lemma_excludes)