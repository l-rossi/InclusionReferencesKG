import coreferee
import spacy
import textacy.spacier.utils
from spacy import displacy
from spacy.tokens import Token

from inclusionreferenceskg.src.document_parsing.document_tree_parser import DocumentTreeParser
from inclusionreferenceskg.src.document_parsing.node.article import Article
from inclusionreferenceskg.src.document_parsing.node.node_traversal import pre_order
from inclusionreferenceskg.src.document_parsing.node.paragraph import Paragraph
from inclusionreferenceskg.src.kg_creation.sentence_analysing.phrase_extractor import PhraseExtractor
from inclusionreferenceskg.src.kg_creation.sentence_analysing.util import get_main_verbs_of_sent

spacy.prefer_gpu()
# We need to use coreferee so that PyCharm does not tidy up the reference.
if not coreferee:
    print("Could not import coreferee for anaphora resolution.")


def main():
    with open("./resources/eu_documents/gdpr.txt", encoding="utf-8") as f:
        gdpr_text = f.read()

    gdpr = DocumentTreeParser().parse_document("GDPR", gdpr_text)

    article6 = gdpr.resolve_loose([Article(number=49), Paragraph(number=1)])[0]

    txt = ""
    for node in pre_order(article6):
        if node.content:
            txt += node.content + "\n"

    nlp = spacy.load("en_core_web_trf", disable=["ner"])

    # nlp = spacy.load("en_core_web_sm", disable=["ner"])

    # reference_detector_component
    # nlp.add_pipe(ReferenceDetector.as_spacy_pipe_component(GoldStandardReferenceDetector()), before="ner")
    nlp.add_pipe('coreferee')
    # nlp.add_pipe(RegexReferenceDetector.SPACY_COMPONENT_NAME, config={})
    # nlp.add_pipe(GoldStandardReferenceDetector.SPACY_COMPONENT_NAME, config={}, after="parser")
    # nlp.add_pipe("noun_phrase_component", before="ner")
    # nlp.remove_pipe("ner")

    # print(nlp.analyze_pipes(pretty=True))

    """
The dog shall eat and digest the cat.
The dog shall eat the cat and digest it.
The dog shall eat the cat and digest the pizza.
The dog shall eat and digest the cat and the pizza.
The dog shall eat, play with and digest the cat.
The dog and the cat and the kid shall play.

The cat is not green.
The cat is not green, is it?
The cat isn't green.
The cat is not not green.

The dog, which is green, is blue.
The dog that ate the cat is purple.
    """

    # Temporal vs conditional then?
    # doc = nlp("""
    #     The dog eats the cat.
    #     The dog eats the cat that is green.
    #     If the dog likes the cat it will eat it.
    #     Where the dog likes the cat it will eat it.
    #     Where I like the cat I will eat it.
    #     In such cases, the dog will eat the cat.
    #     Then the dog will eat the cat.
    #     Then the dog will eat the cat referred to in article 3.
    #     The dog, the cat and the kid are red.
    # """)

    doc = nlp("The data subject has given consent to one of the following")

    # for token in doc:
    #    print(token, token.pos_, token.tag_)
    """for sent in doc.sents:
        phrases = PhraseExtractor().extract_from_sentence(sent)
        for phrase in phrases:
            phrase.pprint()"""

    print(textacy.spacier.utils.get_main_verbs_of_sent(doc))
    print(get_main_verbs_of_sent(doc))

    """count_dep = defaultdict(int)
    for token in doc:
        if token.tag_ == "REF":
            count_dep[token.dep_] += 1

    tot = sum(count_dep.values())
    for k, v in sorted(count_dep.items(), key=lambda x: x[1], reverse=True):
        print(f"{k}: {v} ({v / tot})")"""

    # for tok in doc:
    #    print(tok, tok.pos_, tok.tag_, tok.ent_type_)

    pe = PhraseExtractor()

    for sent in doc.sents:
        print(sent)
        for phrase in pe.extract_from_sentence(sent):
            phrase.pprint()

    displacy.serve(doc, "dep", options={"colors": {"REFERENCE": "red", "PROPER_NOUN": "cyan"}})


# TODO Remove
if __name__ == "__main__":
    Token.set_extension("reference", default=None)
    main()
