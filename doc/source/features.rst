Synapse Admin API Coverage
==========================

Below table shows which Synapse Admin APIs are used by their corresponding
``synadm`` commands. To add a newly released or otherwise missing API, edit
`features.csv`_ and submit a `pull request`_. If you happen to miss a feature
in ``synadm`` for an API that is already tracked here, file a `feature request
issue`_ or even better, a `pull request`_ implementing the feature.

Account Validity API
--------------------

.. csv-table:: Admin API vs Command Overview
   :file: features_account_validity.csv
   :header-rows: 1
   :class: longtable
   :widths: 1 1

Delete Group API
----------------

.. csv-table:: Admin API vs Command Overview
   :file: features_delete_group.csv
   :header-rows: 1
   :class: longtable
   :widths: 1 1


.. _features.csv:
   https://github.com/JOJ0/synadm/tree/master/doc/source/features.csv
.. _feature request issue:
   https://github.com/JOJ0/synadm/issues/new
.. _pull request:
   https://github.com/JOJ0/synadm/blob/dev/CONTRIBUTING.md#submitting-your-work
