import pysubs2
from fugashi import Tagger
from jamdict import Jamdict

SUBTITLE_FILE = "test_anime.ass"
OUTPUT_FILE = "test_anime_out.ass"
POS_EXCLUDES = ["助詞", "助動詞", "空白"] # parts of speech to exclude
VOCAB_MAX_APPEARANCES = 5 # after this number, stop showing its definition

def should_process(event):
    """Return true if we want to generate a vocab list from this subtitle event

    event -- pysubs2 subtitle event
    """
    return event.style == "JP"

tagger = Tagger("-Owakati")
jmd = Jamdict()

subs = pysubs2.load(SUBTITLE_FILE)
vocab_occurrences = {} # looks like {"lemma": int}

for event in subs:
    if should_process(event):
        text = event.plaintext
        if text == "": continue

        event_seen_words = []
        for word in tagger(text):
            if word.feature.pos1 in POS_EXCLUDES: continue

            try:
                lemma = word.feature.lemma
                if (lemma not in event_seen_words and (lemma not in vocab_occurrences or
                        vocab_occurrences[lemma] < VOCAB_MAX_APPEARANCES)):
                    definition = jmd.lookup(lemma)
                    definition = definition.entries[0].senses[0]
                    definition = ", ".join([str(term) for term in definition.gloss])

                    new_text = f"{word}\t{definition}"
                    print("Inserting", new_text)
                    subs.insert(-1, pysubs2.SSAEvent(start=event.start, end=event.end, text=new_text))
                else:
                    print(f"Not inserting {word} because it appears too many times")

                event_seen_words.append(lemma)
                if lemma in vocab_occurrences:
                    vocab_occurrences[lemma] += 1
                else:
                    vocab_occurrences[lemma] = 1
            except (IndexError, ValueError):
                print("Failed to get definition of", word)
subs.save(OUTPUT_FILE)