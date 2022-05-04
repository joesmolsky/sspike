Supernova
=========

.. autoclass:: sspike.supernova.Supernova
    :members:
    :noindex:

Usage example:

.. code-block:: python

    from sspike.supernova import Supernova

    model = 'Nakazato_2013'
    progenitor = {'mass':  20,
                  'metal': 0.02,
                  't_rev': 300}
    transformation = 'NoTransformation'
    distance = 5.0
    sn = Supernova(model, progenitor, transformation, distance)