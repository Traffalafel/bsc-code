package fileStorage

import com.github.javaparser.ast.CompilationUnit
import com.github.javaparser.ast.`type`.{Type => JType}
import com.github.javaparser.ast.expr.Expression
import org.combinators.cls.interpreter.combinator
import org.combinators.cls.types.syntax._
import org.combinators.templating.twirl.{Java, Python}
import org.combinators.cls.types.Type

trait Repository {

  @combinator object filenameVar {
    def apply() = "filename"
    val semanticType: Type = 'FilenameVar
  }

  // todo: Grain key validation
  @combinator object main {
    def apply(read: Python, write: Python) = Python(
      s"""class GrainFileStorage:
         |${read.indent.getCode}
         |${write.indent.getCode}
         |""".stripMargin)
    val semanticType: Type = 'Read =>: 'Write =>: 'FileStorage
  }

  @combinator object readFile1 {
    def apply() = Python(
      s"""def read(filename):
         |    import os
         |    try:
         |        file = os.open(filename, os.O_RDONLY)
         |        file_length = os.stat(file).st_size
         |        file_bytes = os.read(file, file_length)
         |        os.close(file)
         |        return file_bytes.decode('utf-8')
         |     except e:
         |        return ''
         |""".stripMargin)
    val semanticType: Type = 'Read
  }

  @combinator object readFile2 {
    def apply() = Python(
      s"""def read(filename):
         |    try:
         |        file = open(filename, 'r+')
         |        content = file.read()
         |        file.close()
         |        return content
         |    except e:
         |        return ''
         |""".stripMargin)
    val semanticType: Type = 'Read
  }

  @combinator object write_os {
    def apply() = Python(
      s"""def write(filename, value):
         |    try:
         |        file = open(filename, 'w+')
         |        file.write(value)
         |        file.close()
         |    except e:
         |        return
         |""".stripMargin
    )
    val semanticType: Type = 'Write
  }

  @combinator object write2 {
    def apply() = Python(
      s"""def write(filename, value)
         |    try:
         |        file = os.open(filename, os.O_WRONLY)
         |        os.write(file, value)
         |        os.close(file)
         |    except e:
         |        return
         |""".stripMargin
    )
    val semanticType: Type = 'Write
  }

}
