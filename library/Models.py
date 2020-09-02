from library.DataObject import DataObject


# -- runs --

class Run(object):
    def __init__(self, data: dict):
        self.id = data['id']
        self.create_time = data['create_time']
        self.ejudge_language_id = data['ejudge_language_id']
        self.ejudge_score = data['ejudge_score']
        self.ejudge_status = data['ejudge_status']
        self.ejudge_test_num = data['ejudge_test_num']


class RunsList(DataObject):
    def __init__(self):
        self.runs = []

    def parse(self):
        for run in self.data:
            self.runs.append(Run(run))


# -- /runs --

# -- source runs --
class SourceRun(DataObject):
    def parse(self):
        self.lang_id = self.data['language_id']
        self.source = self.data['source']


# -- /source runs --

# -- tests --

class Test(object):
    def __init__(self, data: dict):
        self.max_memory_used = data['max_memory_used']
        self.real_time = data['real_time']
        self.status = data['status']
        self.string_status = data['string_status']
        self.time = data['time']


class TestsList(DataObject):
    def __init__(self):
        self.route = 'tests'
        self.tests = []

    def parse(self):
        for test in self.data.values():
            self.tests.append(Test(test))

# -- /tests --
