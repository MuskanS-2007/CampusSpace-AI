"""Reserved for the next milestone: a justified, evaluated ML model.

We are deliberately not fitting a classifier yet. The request table has status labels,
but those labels are not confirmed room assignments, so predicting status alone does
not solve room matching. First inspect label semantics, leakage risks, and whether a
valid prediction target can be defined from these synthetic records.
"""

def train_model():
    raise NotImplementedError("ML target and evaluation design will be finalized after dataset audit.")
