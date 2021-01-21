import pysubs2
from fugashi import Tagger
from jamdict import Jamdict

SUBTITLE_FILE = "test_anime.ass"
OUTPUT_FILE = "test_anime_out.ass"
POS_EXCLUDES = ["助詞", "助動詞", "空白"] # parts of speech to exclude

tagger = Tagger("-Owakati")
jmd = Jamdict()

subs = pysubs2.load(SUBTITLE_FILE)

def shouldProcess(event):
    return event.style == "JP"

for event in subs:
    if shouldProcess(event):
        text = event.plaintext
        if text != "":
            for word in tagger(text):
                if word.feature.pos1 not in POS_EXCLUDES:
                    try:
                        definition = jmd.lookup(word.feature.lemma)
                        new_text = f"{word}\t{definition.entries[0].senses[0]}"
                        subs.insert(-1, pysubs2.SSAEvent(start=event.start, end=event.end, text=new_text))
                    except (IndexError, ValueError):
                        print("Failed to get definition of", word)
subs.save(OUTPUT_FILE)