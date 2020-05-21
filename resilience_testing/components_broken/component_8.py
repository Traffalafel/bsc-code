import os
class Database():
    def __init__(self, data_dir):
        self.data_dir = data_dir
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

    def read(self, filename):
        path = os.path.join(self.data_dir, filename)
        file = os.open(path, os.O_RDONLY)
        file_length = os.stat(file).st_size
        file_bytes = os.read(file, file_length)
        os.close(file)
        return file_bytes.decode('utf-8')

    def write(self, filename, grain_state):
        path = os.path.join(self.data_dir, filename)
        file = os.fdopen(fd, 'w+', encoding='utf-8')
        chars_written = file.write(grain_state)
        file.close()
        return chars_written

    def clear(self, filename):
        import shutil
        tmp_path = os.path.join(self.data_dir, "temporary")
        os.mkdir(tmp_path)
        path = os.path.join(self.data_dir, filename)
        shutil.move(path, os.path.join(tmp_path, filename))
        shutil.rmtree(tmp_path)
