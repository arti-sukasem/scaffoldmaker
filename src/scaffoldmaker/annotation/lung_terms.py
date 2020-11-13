"""
Common resource for lung annotation terms.
"""

# convention: preferred name, preferred id, followed by any other ids and alternative names
lung_terms = [
    ("lower lobe of the left lung", "UBERON:0008953"),
    ("upper lobe of the left lung", "UBERON:0008952")

]

def get_bladder_term(name : str):
    """
    Find term by matching name to any identifier held for a term.
    Raise exception if name not found.
    :return ( preferred name, preferred id )
    """
    for term in lung_terms:
        if name in term:
            return ( term[0], term[1] )
    raise NameError("Lung annotation term '" + name + "' not found.")
