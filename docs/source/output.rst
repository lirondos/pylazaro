Lazaro output
================
A working example of the methods available for the output produced by :doc:`tagger`:

    >>> from pylazaro import Lazaro
    >>> tagger = Lazaro()
    >>> text = "Fue un look sencillo. Se celebra un festival de 'anime'."
    >>> output = tagger.analyze(text)
    >>> output.borrowings()
    [('look', 'ENG'), ('anime', 'OTHER')]`
    >>> output.anglicisms()
    [('look', 'ENG')]
    >>> output.other_borrowings()
    [('anime', 'OTHER')]`
    >>> output.tag_per_token()
    [('Fue', 'O'), ('un', 'O'), ('look', 'B-ENG'), ('sencillo', 'O'), ('.', 'O'), ('Se', 'O'), ('celebra', 'O'), ('un', 'O'), ('festival', 'O'), ('de', 'O'), ("'", 'O'), ('anime', 'B-OTHER'), ("'", 'O'), ('.', 'O')]

.. autoclass:: pylazaro.outputs.LazaroOutput
    :members:


