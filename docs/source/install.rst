Installation
============

.. _installation:

How to install
--------------

To install ``pylazaro``, you need to run the following commands:

.. code-block:: console

   $ pip install git+https://github.com/ConstantineLignos/quickvec.git
   $ pip install pylazaro
   $ python -m pylazaro

The last command will download several files (model files, embeddings) that are required by
``pylazaro``. Please bare in mind that these files may take a while to download and install.

Extended installation
---------------------

There is an extended version of ``pylazaro`` that runs on larger models. These
larger models can produce better results but will also take up more memory space and will take
longer to run and to install.

The basic models should suit most use cases and we recommend that you stick to the basic
installation whenever possible.
However, if you wish to run ``pylazaro`` using these larger models run the following commands:

.. code-block:: console

   $ pip install git+https://github.com/ConstantineLignos/quickvec.git
   $ pip install pylazaro
   $ python -m pylazaro larger


