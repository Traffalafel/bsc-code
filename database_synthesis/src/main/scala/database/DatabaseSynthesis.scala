package database

import org.combinators.cls.interpreter.ReflectedRepository
import org.combinators.cls.types.syntax._
import org.combinators.templating.twirl.Python
import java.io._

object DatabaseSynthesis {

  def save_inhabitant(filename:String, python:Python): Unit = {
    val writer = new PrintWriter(new File(filename))
    writer.write(python.getCode)
    writer.close()
  }

  def main(args: Array[String]): Unit = {
    if (args.length != 1) {
      println("Usage: run <path to output directory>")
      return
    }
    val output_dir = args(0)

    lazy val repository = new Repository {}
    lazy val Gamma = ReflectedRepository(repository, classLoader = this.getClass.getClassLoader)

    val results = Gamma.inhabit[Python](semanticTypes = 'Database)
    val expressions = results.interpretedTerms.values.flatMap(_._2)

    // Ensure the inhabitants output directory exists
    val create_output_dir = new File(output_dir).mkdirs()
    new File(s"$output_dir/__init__.py").createNewFile()

    var count: Int = 0
    expressions.foreach(exp => {
      count += 1
      save_inhabitant(filename = s"$output_dir/version_$count.py", exp)
    })
    println(s"Synthesized ${count} versions")

  }
}