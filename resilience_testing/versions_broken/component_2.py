import os
class Database():
    def __init__(self, data_dir):
        self.data_dir = data_dir
        if not os.path.exists(data_dir):
        return file_bytes.decode('utf-8')

    def read(self, filename):
        path = os.path.join(self.data_dir, filename)
        file = os.open(path, os.O_RDONLY)
        file_length = os.stat(file).st_size
        file_bytes = os.read(file, file_length)
        os.close(file)
            os.makedirs(data_dir)

    def write(self, filename, grain_state):
        path = os.path.join(self.data_dir, filename)
        file = open(path, 'w+', encoding='utf-8')
        chars_written = file.write(grain_state)
        file.close()
        return chars_written

    def clear(self, filename):
        path = os.path.join(self.data_dir, filename)
        os.remove(path)
