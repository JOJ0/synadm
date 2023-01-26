
Scripting Examples
==================

This chapter should give some ideas on how ``synadm`` commands can be combinend
to achieve functionality that is not directly covered by a single ``synadm``
command.

A handy command line tool to filter and postprocess json data is ``jq``. Some of
the examples in this chapter use it. Most Linux distros have it readily
available in their main repos. Read `jq`s exhaustive man page to learn what's
possible.

Piping through ``jq`` prints out formatted and valid JSON data:

.. code-block:: shell

    $ synadm -o json media list -u testuser1 | jq 
    {
      "media": [
        {
          "media_id": "zdkkcUmbHPoPKkvCyFMTDNOB",
          "media_type": "application/pdf",
          "media_length": 3235323,
          "upload_name": "some_document.pdf",
          "created_ts": "2021-04-16 07:59:10",
          "last_access_ts": null,
          "quarantined_by": "@admin:example.org",
          "safe_from_quarantine": false
        },
        {
          "media_id": "ZTxHWcvUUBSuSTNixMGEzeyj",
          "media_type": "application/pdf",
          "media_length": 8875938,
          "upload_name": "another_document.pdf",
          "created_ts": "2021-04-16 07:58:54",
          "last_access_ts": null,
          "quarantined_by": null,
          "safe_from_quarantine": false
        }
      ],
      "total": 2
    }

The top-level JSON object contains a JSON array ``media`` which can be looped
throuh with the ``jq`` syntax ``.media[]``. To access specific properties of each
array item we could use a shell loop like this:

.. code-block:: shell

    $ for ID in `synadm -o json media list -u testuser1 | jq '.media[].media_id'`; do echo $ID; done
    "zdkkcUmbHPoPKkvCyFMTDNOB"
    "ZTxHWcvUUBSuSTNixMGEzeyj"

The ID's we get could be passed to another ``synadm`` command, for example to
remove those from quarantine.

.. code-block:: shell

    $ for ID in `synadm -o json media list -u testuser1 | jq '.media[].media_id'`; do synadm media unquarantine -i $ID; done
