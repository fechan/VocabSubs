from vocabinjector import VocabInjector
import json

SUBTITLE_FILE = "test_anime.ass"
OUTPUT_FILE = "test_anime_out.ass"
POS_EXCLUDES = ["助詞", "助動詞", "空白"] # parts of speech to exclude
VOCAB_MAX_APPEARANCES = 5 # after this number, stop showing its definition
MAX_GLOSS_TERMS = 2 # -1 for all terms. (The gloss "する: to do, to wear" has 2 terms)

LAST_GENKI_LESSON = 16 # we won't define words from this lesson and lessons before it

def should_process(event):
    """Return true if we want to generate a vocab list from this subtitle event

    event -- pysubs2 subtitle event
    """
    return event.style == "JP"

injector = VocabInjector(pos_excludes = POS_EXCLUDES, vocab_max_appearances = VOCAB_MAX_APPEARANCES,
            max_gloss_terms = MAX_GLOSS_TERMS, sub_filter = should_process)

lemma_excludes = ["楽"]
with open("genki_vocab.json") as f:
    genki_vocab = json.load(f)
    for word in genki_vocab:
        has_kanji = len(word["Kanji"]) > 0
        lemma = word["Kanji"] if has_kanji else word["Kana"]
        lemma = lemma.replace("〜", "")
        meaning = word["Meaning"]
        injector.add_definition(lemma, f"({word['Kana']}) {meaning}" if has_kanji else meaning)
        if word["Lesson"] <= LAST_GENKI_LESSON:
            lemma_excludes.append(lemma)

injector.set_lemma_excludes(lemma_excludes)
injector.insert_vocab_lists(SUBTITLE_FILE, OUTPUT_FILE)