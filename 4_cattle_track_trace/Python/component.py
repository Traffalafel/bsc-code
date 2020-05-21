import os
class Component():
    def __init__(self, data_dir):
        self.data_dir = data_dir
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

    def read(self, filename):
        path = os.path.join(self.data_dir, filename)
        file = open(path, 'r+', encoding='utf-8')
        content = file.read()
        file.close()
        return content

    def write(self, filename, grain_state):
        path = os.path.join(self.data_dir, filename)
        fd = os.open(path, os.O_WRONLY|os.O_CREAT|os.O_TRUNC)
        file = os.fdopen(fd, 'w+', encoding='utf-8')
        chars_written = file.write(grain_state)
        file.close()
        return chars_written

    def clear(self, filename):
        path = os.path.join(self.data_dir, filename)
        os.remove(path)
