About ``pylazaro``
======================

What is ``pylazaro``?
---------------------------
``pylazaro`` is a Python library that automatically detects unassimilated lexical borrowings (or `loanwords <https://en.wikipedia.org/wiki/Loanword>`_) in Spanish text, i.e. words from other languages that are used in Spanish without orthographic adaptation, such as `app`, `lawfare`, `fake news` or `machine learning`. 

``pylazaro`` focuses particularly on borrowings that come from English (a.k.a. `anglicisms <https://en.wikipedia.org/wiki/Anglicism>`_), although it can also detect some borrowings from other languages (such as Japanese, French or Basque). 

How does ``pylazaro`` work?
---------------------------------
``pylazaro`` takes Spanish text as input an returns the borrowings found in the text. Borrowings from English will be labeled as ``ENG``, borrowings from other languages will be labeled as ``OTHER``. What lies at the core of ``pylazaro`` is a machine learning model that has been trained for the task of detecting unassimilated lexical borrowings from Spanish newspapers. 

``pylazaro`` can be run with three different types of models: 

#. `A BiLSTM-CRF model fed with subword embeddings and lexical embeddings pretrained on codeswitching data <https://huggingface.co/lirondos/anglicisms-spanish-flair-cs>`_ (this is the best performing model, and the default model used by ``pylazaro``)
#. `A Transformer model based on multilingual BERT <https://huggingface.co/lirondos/anglicisms-spanish-mbert>`_
#. A Conditional Random Field model with handcrafted features

By default, ``pylazaro`` uses the first model (BiLSTM-CRF), which is the best-performing model of all three, but this can be modified at will (see :doc:`howto`).  

For information about the creation of these models, training data and experimental results see the following paper: 

* Elena Álvarez-Mellado and Constantine Lignos. 2022. `Detecting Unassimilated Borrowings in Spanish: An Annotated Corpus and Approaches to Modeling <https://aclanthology.org/2022.acl-long.268/>`_. In `Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics` (Volume 1: Long Papers), pages 3868–3888, Dublin, Ireland. Association for Computational Linguistics.


What is the point of ``pylazaro`` package?
---------------------------------------------
The models behind ``pylazaro`` (the BiLSTM-CRF and the Transformer-based model) have been publicly released and can already be accessed `through HuggingFace modelhub <https://huggingface.co/models?other=arxiv:2203.16169>`_. So one could ask what the point of ``pylazaro`` is. The purpose of ``pylazaro`` is to offer a single interface for all available models for borrowing detection. 

Let's say that we are using the `Transformer-based model <https://huggingface.co/lirondos/anglicisms-spanish-mbert>`_ using the `Transformers library <https://github.com/huggingface/transformers/>`_, but we want to try the `BiLSTM-CRF model <https://huggingface.co/lirondos/anglicisms-spanish-flair-cs>`_ , which produces better results. This would require changing all of our Python code and adapt it to `Flair library <https://github.com/flairNLP/flair/>`_, which is the library used by the BiLSTM-CRF model. This is a pain if we want to keep switching between models. And it will only get worse if new models based on different third-party packages are released. This scenario was precisely what I encountered doing my own PhD research. The purpose of ``pylazaro`` is therefore to offer a single interface for all borrowing detection models for Spanish that allows for switching between models smoothly.

In addition, using the Transformers library or Flair may be trivial for experienced programers, but it may not be that simple for novice Python users. ``pylazaro`` also seeks to offer an easy way to use these borrowing detection models for people who work on Linguistics and that may not be expert Python users.

I want to detect borrowings in Spanish text. Will ``pylazaro`` be suitable for my project?
-----------------------------------------------------------------------------------------------
Maybe. The models behind ``pylazaro`` have been trained and tuned for detecting a particular type of borrowing (unassimilated anglicisms) in a very specific setting (Spanish newspaper articles). If your use case is similar to that,  ``pylazaro`` may be suitable. 

But if you are looking to detect, let's say, othographically adapted borrowings (such as `fútbol` or `espóiler`) or apply it to a very different type of text (such as tweets or other social media text) it may not work fine. 

Also, bear in mind that all of these models are far from being perfect and they can easily make mistakes. The BiLSTM-CRF model (which is the best-performing model so far and the one that ``pylazaro`` uses by default) produced and F1 score of 85.76 during evaluation.

Where can I check the code, the models or the data behind ``pylazaro``?
-----------------------------------------------------------------------------------------------
* The code behind ``pylazaro`` is available on `GitHub <https://github.com/lirondos/pylazaro>`_.
* The dataset used to train ``pylazaro`` is the `COALAS corpus <https://github.com/lirondos/coalas>`_.
* The two best-performing models behind ``pylazaro`` are also available through `HuggingFace model hub <https://huggingface.co/models?other=arxiv:2203.16169>`_.
* The paper that describes the creation of the dataset and models is available in the `ACL anthology <https://aclanthology.org/2022.acl-long.268/>`_.
 


Why is it called `pylazaro`?
---------------------------------
The name of this package (and of the whole project that motivates it) is a tribute to the Spanish linguist `Lázaro Carreter <https://en.wikipedia.org/wiki/Fernando_L%C3%A1zaro_Carreter>`_, whose prescriptivist columns against the usage of the anglicisms in the Spanish press were extremely popular in Spain during the 1980s and the 1990s.

Who develops ``pylazaro``?
---------------------------------
``pylazaro`` is built and maintained by `Elena Álvarez Mellado <https://lirondos.github.io/>`_, a (computational) linguist based in Spain.

How can I reach the maintainer?
---------------------------------
If you have any questions, find any bugs or want to share anything with me, feel free to reach me at ealvarezmellado [@] gmail.com or ping me on Twitter `@lirondos <https://twitter.com/lirondos>`_.

