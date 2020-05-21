package database

import org.combinators.cls.interpreter.combinator
import org.combinators.cls.types.syntax._
import org.combinators.templating.twirl.Python
import org.combinators.cls.types.{Taxonomy, Type}

trait Repository {

  @combinator object database {
    def apply(read:Python, write:Python, clear:Python) : Python = Python(
      s"""import os
         |class Database():
         |    def __init__(self, data_dir):
         |        self.data_dir = data_dir
         |        if not os.path.exists(data_dir):
         |            os.makedirs(data_dir)
         |
         |${read.indent.getCode}
         |
         |${write.indent.getCode}
         |
         |${clear.indent.getCode}
         |""".stripMargin)
    val semanticType: Type =
      ('StateId =>: 'StateValue) =>: // Read
      ('StateId :&: 'StateValue =>: 'Persisted) =>: // Write
      ('StateId =>: 'NotPersisted) =>: // Clear
      'Database
  }

  @combinator object read {
    def apply() : Python = Python(
      s"""def read(self, state_id):
         |    path = os.path.join(self.data_dir, state_id)
         |    file = open(path, 'r+', encoding='utf-8')
         |    content = file.read()
         |    file.close()
         |    return content
         |""".stripMargin)
    val semanticType: Type = 'StateId =>: 'StateValue
  }

  @combinator object read2 {
    def apply() : Python = Python(
      s"""def read(self, state_id):
         |    path = os.path.join(self.data_dir, state_id)
         |    file = os.open(path, os.O_RDONLY)
         |    file_length = os.stat(file).st_size
         |    file_bytes = os.read(file, file_length)
         |    os.close(file)
         |    return file_bytes.decode('utf-8')
         |""".stripMargin)
    val semanticType: Type = 'StateId =>: 'StateValue
  }

  @combinator object write {
    def apply() : Python = Python(
      s"""def write(self, state_id, state_value):
         |    path = os.path.join(self.data_dir, state_id)
         |    file = open(path, 'w+', encoding='utf-8')
         |    chars_written = file.write(state_value)
         |    file.close()
         |    return chars_written
         |""".stripMargin
    )
    val semanticType: Type = 'StateId :&: 'StateValue =>: 'Persisted
  }

  @combinator object write2 {
    def apply() : Python = Python(
      s"""def write(self, state_id, state_value):
         |    path = os.path.join(self.data_dir, state_id)
         |    fd = os.open(path, os.O_WRONLY|os.O_CREAT|os.O_TRUNC)
         |    file = os.fdopen(fd, 'w+', encoding='utf-8')
         |    chars_written = file.write(state_value)
         |    file.close()
         |    return chars_written
         |""".stripMargin
    )
    val semanticType: Type = 'StateId :&: 'StateValue =>: 'Persisted
  }

  @combinator object clear {
    def apply() : Python = Python(
      s"""def clear(self, state_id):
         |    path = os.path.join(self.data_dir, state_id)
         |    os.remove(path)
         |""".stripMargin)
    val semanticType: Type = 'StateId =>: 'NotPersisted
  }

  @combinator object clear2 {
    def apply() : Python = Python(
      s"""def clear(self, state_id):
         |    import shutil
         |    tmp_path = os.path.join(self.data_dir, "temporary")
         |    os.mkdir(tmp_path)
         |    path = os.path.join(self.data_dir, state_id)
         |    shutil.move(path, os.path.join(tmp_path, state_id))
         |    shutil.rmtree(tmp_path)
         |""".stripMargin)
    val semanticType: Type = 'StateId =>: 'NotPersisted
  }

}
