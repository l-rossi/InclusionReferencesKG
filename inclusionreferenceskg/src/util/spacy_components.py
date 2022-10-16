import logging

from spacy import Language

REFERENCE_QUALIFIER_RESOLVER_COMPONENT = "reference_qualifier_resolver_component"


@Language.component(REFERENCE_QUALIFIER_RESOLVER_COMPONENT, requires=["token._.reference", "doc._.reference_base"])
def reference_qualifier_resolver_component(doc):
    root = doc._.reference_base
    for tok in doc:
        if tok._.reference:
            for qual in tok._.reference.reference_qualifier:
                # We choose the first possible node
                targets = root.resolve_loose(qual)
                if len(targets) > 1:
                    logging.warning(f"Got more than one possible target for reference '{tok._.reference.text_content}'")

                if len(targets) < 1:
                    logging.warning(f"Got no possible target for reference '{tok._.reference.text_content}'")

                if targets:
                    tok._.reference.targets.append(targets[0])

    return doc
