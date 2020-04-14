package fileStorage

import org.combinators.cls.interpreter.ReflectedRepository
import org.combinators.cls.types.syntax._
import org.combinators.templating.twirl.Python

// sample code showing how to directly invoke, without web service.
object FileStorage {

  def main(args: Array[String]): Unit = {

    lazy val repository = new Repository {}
    lazy val Gamma = ReflectedRepository(repository, classLoader = this.getClass.getClassLoader)

    val results = Gamma.inhabit[Python]('FileStorage)

    // Print different inhabitations
    results.interpretedTerms
      .values.flatMap(_._2)
      .foreach(exp => println(exp))

  }
}