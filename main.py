import pysubs2
from fugashi import Tagger
from jamdict import Jamdict

SUBTITLE_FILE = "test_anime.ass"
POS_EXCLUDES = ["助詞", "助動詞", "空白"] # parts of speech to exclude

tagger = Tagger("-Owakati")
jmd = Jamdict()

subs = pysubs2.load(SUBTITLE_FILE)

for event in subs:
    if event.style == "JP": # TODO: this is subtitle specific; should make a more flexible filter
        text = event.plaintext
        if text != "":
            for word in tagger(text):
                try:
                    if word.feature.pos1 not in POS_EXCLUDES:
                        definition = jmd.lookup(word.feature.lemma)
                        print(word, word.feature.pos1, definition.entries[0].senses[0], sep="\t")
                except:
                    print("Failed to get definition of", word)