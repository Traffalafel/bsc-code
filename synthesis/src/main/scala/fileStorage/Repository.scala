package fileStorage

import org.combinators.cls.interpreter.combinator
import org.combinators.cls.types.syntax._
import org.combinators.templating.twirl.Python
import org.combinators.cls.types.Type

trait Repository {

  @combinator object filenameVar {
    def apply() = "filename"
    val semanticType: Type = 'FilenameVar
  }

  // todo: Grain key validation
  @combinator object main {
    def apply(read: Python, write: Python, clear: Python) = Python(
      s"""import os
         |class Component():
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
    val semanticType: Type = 'Read =>: 'Write =>: 'Clear =>: 'FileStorage
  }

  @combinator object read1 {
    def apply() = Python(
      s"""def read(self, filename):
         |    path = os.path.join(self.data_dir, filename)
         |    file = os.open(path, os.O_RDONLY)
         |    file_length = os.stat(file).st_size
         |    file_bytes = os.read(file, file_length)
         |    os.close(file)
         |    return file_bytes.decode('utf-8')
         |""".stripMargin)
    val semanticType: Type = 'Read
  }

  @combinator object read2 {
    def apply() = Python(
      s"""def read(self, filename):
         |    path = os.path.join(self.data_dir, filename)
         |    file = open(path, 'r+', encoding='utf-8')
         |    content = file.read()
         |    file.close()
         |    return content
         |""".stripMargin)
    val semanticType: Type = 'Read
  }

  @combinator object write1 {
    def apply() = Python(
      s"""def write(self, filename, grain_state):
         |    path = os.path.join(self.data_dir, filename)
         |    fd = os.open(path, os.O_WRONLY|os.O_CREAT|os.O_TRUNC)
         |    file = os.fdopen(fd, 'w+', encoding='utf-8')
         |    chars_written = file.write(grain_state)
         |    file.close()
         |    return chars_written
         |""".stripMargin
    )
    val semanticType: Type = 'Write
  }

  @combinator object write2 {
    def apply() = Python(
      s"""def write(self, filename, grain_state):
         |    path = os.path.join(self.data_dir, filename)
         |    file = open(path, 'w+', encoding='utf-8')
         |    chars_written = file.write(grain_state)
         |    file.close()
         |    return chars_written
         |""".stripMargin
    )
    val semanticType: Type = 'Write
  }

  @combinator object clear1 {
    def apply() = Python(
      s"""def clear(self, filename):
         |    path = os.path.join(self.data_dir, filename)
         |    os.remove(path)
         |""".stripMargin)
    val semanticType: Type = 'Clear
  }

  @combinator object clear2 {
    def apply() = Python(
      s"""def clear(self, filename):
         |    path = os.path.join(self.data_dir, filename)
         |    os.remove(path)
         |""".stripMargin)
    val semanticType: Type = 'Clear
  }

}
