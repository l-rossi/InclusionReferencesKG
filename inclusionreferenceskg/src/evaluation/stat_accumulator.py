class StatAccumulator:
    """
    A class for accumulating statistics and calculating the F1 score.
    """
    def __init__(self):
        self.false_negatives = 0
        self.false_positives = 0
        self.n_detected_references = 0
        self.n_expected_references = 0

    def true_positives(self):
        return self.n_expected_references - self.false_negatives

    def precision(self):
        return self.true_positives() / self.n_detected_references

    def recall(self):
        return self.true_positives() / self.n_expected_references

    def f1(self):
        return 2 / (1 / self.recall() + 1 / self.precision())
