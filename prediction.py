
class Prediction():
    def __init__(self, decor_type, dataset, label):
        self.decor_type = decor_type
        self.dataset = dataset
        self.label = label

    def get_decor(self):
        return self.decor_type

    def get_dataset(self):
        return self.dataset

    def get_label(self):
        return self.label
