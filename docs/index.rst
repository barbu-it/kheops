

.. image:: ../logo/kheops_brand.png
    :target: https://amoffat.github.com/sh
    :alt: Logo


Khéops documentation
=======================================================

.. contents:: Table of Contents

.. currentmodule:: kheops


Welcome in Khéops documentation.


Khéops is a tool that can be used to lookup a key value pair, that is to say, given a key it will give back the appropriate value. This is certainly nothing special or new, but the crucial difference here is the way in which the data is looked up. Rather than just querying a flat data source and returning the value for a requested key, when doing a hierarchical lookup we perform multiple queries against a configured hierarchy, transcending down to the next layer in the hierarchy until we find an answer. The end result is that we can define key value pairs on a global basis but then override them under certain conditions based on the hierarchical resolution by placing that key value pair further up the hierarchy for a particular condition.



Content
==================

.. toctree::
   :maxdepth: 3
   :caption: Contents:
   :glob:

   docs/app/index.rst
   docs/learn/index.rst
   docs/guide/index.rst
   Python API <api/modules.rst>


Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


