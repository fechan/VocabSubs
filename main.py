import pysubs2
from fugashi import Tagger
from jamdict import Jamdict

SUBTITLE_FILE = "test_anime.ass"
OUTPUT_FILE = "test_anime_out.ass"
POS_EXCLUDES = ["助詞", "助動詞", "空白"] # parts of speech to exclude
VOCAB_MAX_APPEARANCES = 3 # after this number, stop showing its definition

def shouldProcess(event):
    return event.style == "JP"

tagger = Tagger("-Owakati")
jmd = Jamdict()

subs = pysubs2.load(SUBTITLE_FILE)

for event in subs:
    if shouldProcess(event):
        text = event.plaintext
        if text != "":
            for word in tagger(text):
                if word.feature.pos1 not in POS_EXCLUDES: #TODO: don't add words we've already seen (or make a global variable option)
                    try:
                        definition = jmd.lookup(word.feature.lemma)
                        definition = definition.entries[0].senses[0]
                        definition = ", ".join([str(term) for term in definition.gloss])

                        new_text = f"{word}\t{definition}"
                        print("Inserting", new_text)
                        subs.insert(-1, pysubs2.SSAEvent(start=event.start, end=event.end, text=new_text))
                    except (IndexError, ValueError):
                        print("Failed to get definition of", word)
subs.save(OUTPUT_FILE)