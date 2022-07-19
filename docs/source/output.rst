Lazaro output
================
A working example of the methods available for the output produced by :doc:`tagger`:

    >>> from pylazaro import Lazaro
    >>> tagger = Lazaro()
    >>> text = "Fue un look sencillo. Se celebra un festival de 'anime'."
    >>> output = tagger.analyze(text)
    >>> output.borrowings_to_tuple()
    [('look', 'en'), ('anime', 'other')]
    >>> output.anglicisms_to_tuple()
    [('look', 'en')]
    >>> output.other_to_tuple()
    [('anime', 'other')]
    >>> output.borrowings_to_dict()
    [{'borrowing': 'look', 'language': 'en', 'start_pos': 2, 'end_pos': 3}, {'borrowing': 'anime', 'language': 'other', 'start_pos': 11, 'end_pos': 12}]
    >>> output.anglicisms_to_dict()
    [{'borrowing': 'look', 'language': 'en', 'start_pos': 2, 'end_pos': 3}]
    >>> output.other_to_dict()
    [{'borrowing': 'anime', 'language': 'other', 'start_pos': 11, 'end_pos': 12}]
    >>> output.tag_per_token()
    [('Fue', 'O'), ('un', 'O'), ('look', 'B-ENG'), ('sencillo', 'O'), ('.', 'O'), ('Se', 'O'), ('celebra', 'O'), ('un', 'O'), ('festival', 'O'), ('de', 'O'), ("'", 'O'), ('anime', 'B-OTHER'), ("'", 'O'), ('.', 'O')]

.. autoclass:: pylazaro.outputs.LazaroOutput
    :members:


