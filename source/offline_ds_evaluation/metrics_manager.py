class MetricsManager:

    def __init__(self, experiment):

        self.experiment = experiment

        self.data = dict()

    def append(self, new_data: list()):
        # environment and Buffer type as identifier
        self.data["/".join(new_data[:2])] = new_data[2:]

    def get_data(self, env, buffer_type):
        return self.data["/".join([env, buffer_type])]
