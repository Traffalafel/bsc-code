import os
class Database():
    def __init__(self, data_dir):
        self.data_dir = data_dir
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

    def read(self, state_id):
        path = os.path.join(self.data_dir, state_id)
        file = os.open(path, os.O_RDONLY)
        file_length = os.stat(file).st_size
        file_bytes = os.read(file, file_length)
        os.close(file)
        return file_bytes.decode('utf-8')

    def write(self, state_id, state_value):
        path = os.path.join(self.data_dir, state_id)
        file = open(path, 'w+', encoding='utf-8')
        chars_written = file.write(state_value)
        file.close()
        return chars_written

    def clear(self, state_id):
        import shutil
        tmp_path = os.path.join(self.data_dir, "temporary")
        os.mkdir(tmp_path)
        path = os.path.join(self.data_dir, state_id)
        shutil.move(path, os.path.join(tmp_path, state_id))
        shutil.rmtree(tmp_path)
