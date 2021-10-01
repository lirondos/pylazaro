Usage
=====

.. _usage:

How to use pylazaro
-------------------

In order to use ``pylazaro`` you need to create an instance of the class  ``Lazaro``. This
object will be our tagger. We can then pass any text in Spanish to the tagger and the tagger will
return the lexical borrowings found in the text.

Example
-------
Here is a basic example of how to use  ``pylazaro``:

>>> from pylazaro import Lazaro
>>> tagger = Lazaro()
>>> text = "Inteligencia artificial aplicada al sector del digital health, la e-mobility, las smarts grids entre otros; favoreciendo las interacciones colaborativas."
>>> result = tagger
.analyze(text)
>>> result.get_borrowings()
[(digital health, 'ENG'), (e-mobility, 'ENG'), (smarts grids, 'ENG')]

