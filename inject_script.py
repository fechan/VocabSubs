from vocabinjector import VocabInjector

SUBTITLE_FILE = "test_anime.ass"
OUTPUT_FILE = "test_anime_out.ass"
POS_EXCLUDES = ["助詞", "助動詞", "空白"] # parts of speech to exclude
VOCAB_MAX_APPEARANCES = 5 # after this number, stop showing its definition
MAX_GLOSS_TERMS = 2 # -1 for all terms. (The gloss "する: to do, to wear" has 2 terms)

def should_process(event):
    """Return true if we want to generate a vocab list from this subtitle event

    event -- pysubs2 subtitle event
    """
    return event.style == "JP"

injector = VocabInjector(pos_excludes = POS_EXCLUDES, vocab_max_appearances = VOCAB_MAX_APPEARANCES,
            max_gloss_terms = MAX_GLOSS_TERMS, sub_filter = should_process)
injector.insert_vocab_lists(SUBTITLE_FILE, OUTPUT_FILE)