import os
class Database():
    def __init__(self, data_dir):
        self.data_dir = data_dir
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

    def read(self, state_id):
        path = os.path.join(self.data_dir, state_id)
        file = open(path, 'r+', encoding='utf-8')
        content = file.read()
        file.close()
        return content

    def write(self, state_id, state_value):
        path = os.path.join(self.data_dir, state_id)
        file = open(path, 'w+', encoding='utf-8')
        chars_written = file.write(state_value)
        file.close()
        return chars_written

    def clear(self, state_id):
        path = os.path.join(self.data_dir, state_id)
        os.remove(path)
