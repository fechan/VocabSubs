import pysubs2
from fugashi import Tagger
from jamdict import Jamdict

tagger = Tagger("-Owakati")
jmd = Jamdict()

subs = pysubs2.load("test_anime.ass")

text = subs[50].plaintext
for word in tagger(text):
    definition = jmd.lookup(word.feature.lemma)
    print(definition.entries[0].senses[0])
    print(word, word.feature.lemma, sep="\t")

