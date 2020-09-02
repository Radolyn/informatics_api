class Example(object):
    def __init__(self, input_data, output_data):
        self.input = input_data
        self.output = output_data


class Problem(object):
    def __init__(self, id):
        self.id = id
        self.description = 'Не указано'
        self.input_data = 'Не указано'
        self.output_data = 'Не указано'
        self.examples = []
