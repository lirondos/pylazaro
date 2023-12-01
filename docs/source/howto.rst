How to use ``pylazaro``
========================


In order to use ``pylazaro`` you need to create an instance of the class  :class:`pylazaro.lazaro.Lazaro`. This
object will be our tagger. We can then pass any text in Spanish to the tagger through the method
:py:meth:`pylazaro.lazaro.Lazaro.analyze()`
and the
tagger will
return the lexical borrowings found in the text encoded in the object :class:`pylazaro.outputs.LazaroOutput`.


Example
*******

Here is a minimal example of how to use  ``pylazaro``:

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

Running ``pylazaro`` with other models 
*********************************************
``pylazaro`` can be run with five different types of models (see `How does pylazaro work?` in :doc:`about`):

#. `A BiLSTM-CRF model fed with subword embeddings and lexical embeddings pretrained on codeswitching data <https://huggingface.co/lirondos/anglicisms-spanish-flair-cs>`_ (this is the best performing model, and the default model used by ``pylazaro``)
#. `A BiLSTM-CRF model fed with subword embeddings and bilingual Transformer-based Spanish-English lexical embeddings <https://huggingface.co/lirondos/anglicisms-spanish-flair-bert-beto>`_ (this is the best performing model, and the default model used by ``pylazaro``)
#. `A Transformer model based on multilingual BERT <https://huggingface.co/lirondos/anglicisms-spanish-mbert>`_
#. `A Transformer model based on Spanish model BETO <https://huggingface.co/lirondos/anglicisms-spanish-beto>`_
#. A Conditional Random Field model with handcrafted features

By default, ``pylazaro`` will use the first model (BiLSTM-CRF with codeswitched embeddings), which is the best-performing model of all, but this can be modified when instantiating :class:`pylazaro.lazaro.Lazaro`:

>>> tagger_bilstm = Lazaro(model_type = 'bilstm', model_file="lirondos/anglicisms-spanish-flair-cs") # Equivalent to tagger_bilstm = Lazaro() and to tagger_bilstm = Lazaro(model_type = 'bilstm')
>>> tagger_bilstm = Lazaro(model_type = 'bilstm', model_file="lirondos/anglicisms-spanish-flair-bert-beto")
>>> tagger_bilstm = Lazaro(model_type = 'transformers', model_file="lirondos/anglicisms-spanish-mbert") # Equivalent to tagger_transformers = Lazaro(model_type = 'transformers')
>>> tagger_bilstm = Lazaro(model_type = 'transformers', model_file="lirondos/anglicisms-spanish-beto")
>>> tagger_crf = Lazaro(model_type = 'crf') # Requires extended installation

.. warning::
    In order to run the CRF model, the extended installation is required (see :doc:`install`). However, we don't recommend using the CRF model, as it is the worst-performing model of all three options (and the extended installation will significantly take more memory space).