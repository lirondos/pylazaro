==================
Installation guide
==================

.. _installation:

How to install
==============

To install ``pylazaro``, you simply need to run the following command:

.. code-block:: console

   $ pip install pylazaro

.. note::
    ``pylazaro`` requires Python 3.8 or newer and has been tested up to Python 3.12.

.. note::
    ``pylazaro`` pins upper bounds on ``flair``, ``torch`` and ``transformers``. The
    released BiLSTM checkpoints cannot be unpickled by ``flair`` 0.14 or newer, so
    installing a newer ``flair`` alongside ``pylazaro`` will break the default model.

Extended installation
======================

There is an extended installation option for ``pylazaro``. This extended installation is needed if you want to run the CRF model for Lazaro (see section 3.1 from `this paper  <https://aclanthology.org/2022.acl-long.268/>`_). However, it is unlikely that you will ever need to run that model, as the CRF model is the worst performing model of all models offered through the library. The extended installation is probably only useful for research or development purposes, but not for final users.

If you still wish to install the extended version, see below the commands you need to run. 

.. warning::
    This extended installation will take up more memory space and will take some time to install. The
    basic installation should suit most use cases and we recommend that you stick to the basic
    installation whenever possible.

.. code-block:: console

   $ pip install pylazaro
   $ python -m pylazaro extended
   $ python -m spacy download es_core_news_md

The model and the embeddings are downloaded to a per-user data directory
(``%LOCALAPPDATA%\pylazaro`` on Windows, ``~/.cache/pylazaro`` elsewhere), so they
survive reinstalls and upgrades of ``pylazaro``. Set the ``PYLAZARO_HOME`` environment
variable to download them somewhere else.

.. note::
    If you ran the extended installation with ``pylazaro`` 1.1.21 or earlier, the files
    live inside the package folder in ``site-packages``. That location is still used
    when it already contains the files, so you do not need to download them again.

How to uninstall
============================

To uninstall ``pylazaro``, simply run:

.. code-block:: console

   $ pip uninstall pylazaro
   

If you installed the extended version, running ``pip uninstall pylazaro`` will not suffice: the model and the embeddings are downloaded after installation and ``pip`` does not know about them. You will also need to remove the data directory.

.. code-block:: console

   $ rm -r ~/.cache/pylazaro          # Linux and macOS
   > rmdir /s %LOCALAPPDATA%\pylazaro  # Windows

If you performed the extended installation with ``pylazaro`` 1.1.21 or earlier, the files are in ``pylazaro``'s package folder inside ``site-packages`` instead.



