Welcome to ``pylazaro``'s documentation!
============================================

What is ``pylazaro``
********************
``pylazaro`` is a Python library that automatically detects lexical borrowings (or loanwords) in Spanish text, particularly  borrowings that come from English (a.k.a. anglicisms), such as `app`, `lawfare`, `fake news` or `machine learning`. 

Learn more about the motivation and the backstage of the project at :doc:`about`.

Example
*******

Here is a minimal example of how to install and use ``pylazaro``:

.. code-block:: console

   $ pip install pylazaro


>>> from pylazaro import Lazaro
>>> tagger = Lazaro()
>>> text = "Inteligencia artificial aplicada al sector del blockchain, la e-mobility y las smarts grids entre otros; favoreciendo las interacciones colaborativas."
>>> result = tagger.analyze(text)
>>> result.borrowings_to_tuple()
[('blockchain', 'en'), ('e-mobility', 'en'), ('smarts grids', 'en')]
>>> output.borrowings_to_dict()
[{'borrowing': 'blockchain', 'language': 'en', 'start_pos': 6, 'end_pos': 7}, {'borrowing': 'e-mobility', 'language': 'en', 'start_pos': 9, 'end_pos': 10}, {'borrowing': 'smarts grids', 'language': 'en', 'start_pos': 12, 'end_pos': 14}]
>>> result.tag_per_token()
[('Inteligencia', 'O'), ('artificial', 'O'), ('aplicada', 'O'), ('al', 'O'), ('sector', 'O'), ('del', 'O'), ('blockchain', 'B-ENG'), (',', 'O'), ('la', 'O'), ('e-mobility', 'B-ENG'), ('y', 'O'), ('las', 'O'), ('smarts', 'B-ENG'), ('grids', 'I-ENG'), ('entre', 'O'), ('otros', 'O'), (';', 'O'), ('favoreciendo', 'O'), ('las', 'O'), ('interacciones', 'O'), ('colaborativas', 'O'), ('.', 'O')]

Check out the :doc:`install` for further information on how to install ``pylazaro``.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   install
   howto
   tagger
   output
   borrowing
   token
   about




Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
