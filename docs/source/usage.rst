=====
Usage
=====

.. _usage:

How to use pylazaro
========================

In order to use ``pylazaro`` you need to create an instance of the class  :class:`pylazaro.Lazaro`. This
object will be our tagger. We can then pass any text in Spanish to the tagger through the method
:function:`pylazaro.Lazaro.analyze()`.
and the
tagger will
return the lexical borrowings found in the text encoded in the object :class:`pylazaro.LazaroOutput`.

Example
============
Here is a minimal example of how to use  ``pylazaro``:

>>> from pylazaro import Lazaro
>>> tagger = Lazaro()
>>> text = "El sector del digital health, la e-mobility, las smarts grids entre otros."
>>> result = tagger.analyze(text)
>>> result.borrowings()
[(digital health, 'ENG'), (e-mobility, 'ENG'), (smarts grids, 'ENG')]


LazaroOutput
========================

.. class:: LazaroOutput

    .. method:: borrowings()
    Returns a list with the borrowings found in the text with their corresponding tag
    Ex: ``[('look', 'ENG'), ('online', 'ENG'), ('prime time', 'ENG')]``

    .. method:: anglicisms()
    Returns a list with the borrowings found in the text with their corresponding tag
    Ex: ``[('look', 'ENG'), ('online', 'ENG'), ('prime time', 'ENG')]``

    .. method:: other_borrowings()
    Returns a list with the borrowings found in the text with their corresponding tag
    Ex: ``[('anime', 'OTHER'), ('manga', 'OTHER')]``

    .. method:: tag_per_token()
    Returns a list with the borrowings found in the text with their corresponding tag
    Ex: ``[('Fue', 'O'), ('un', 'O'), ('look', 'B-ENG'), ('sencillo', 'O')]``
