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
    ``pylazaro`` works best on Python 3.8. We don't recommend installing ``pylazaro`` on Python 3.10, as it may result in some incompatibilities (related to the ``sentencepiece`` package).

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

How to uninstall
============================

To uninstall ``pylazaro``, simply run:

.. code-block:: console

   $ pip uninstall pylazaro
   

If you installed the extended version, running ``pip unistall pylazaro`` will not suffice. You will also need to navigate to ``pylazaro``'s package folder in your ``site-package`` folder and remove all remaining files (model and embeddings).

.. code-block:: console

   $ rm -r site-package/pylazaro



