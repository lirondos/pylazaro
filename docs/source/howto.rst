How to use pylazaro
==================


In order to use ``pylazaro`` you need to create an instance of the class  :class:`pylazaro.lazaro.Lazaro`. This
object will be our tagger. We can then pass any text in Spanish to the tagger through the method
:py:meth:`pylazaro.lazaro.Lazaro.analyze()`.
and the
tagger will
return the lexical borrowings found in the text encoded in the object :class:`pylazaro.outputs.LazaroOutput`.


Example
*******

Here is a minimal example of how to use  ``pylazaro``:

>>> from pylazaro import Lazaro
>>> tagger = Lazaro()
>>> text = "El sector del digital health, la e-mobility, las smarts grids entre otros."
>>> result = tagger.analyze(text)
>>> result.borrowings()
[(digital health, 'ENG'), (e-mobility, 'ENG'), (smarts grids, 'ENG')]

