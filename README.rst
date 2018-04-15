=========================================
Keyring Credentials Extension for Kibitzr
=========================================

Once this extension package is installed Kibitzr's ``creds`` will be augmented with ``keyring`` dictionary.
``keyring`` dictionary has following structure: ``{service: {key: value}}``.

``creds`` dictionary is available in many parts of Kibitzr checks. To access it from Python code use::

    creds['keyring']['<service>']['<key>']

When using in Jinja templates you can use the same form, or shortcut::

    creds.keyring.<service>.<key>

`Kibitzr credentials documentation`_.

`Keyring documentation`_.


Install
-------

::

    pip install kibitzr_keyring

Usage example
-------------

Add new credentials to system keyring::

    $ keyring set discover username
    Password for 'username' in 'discover': john
    $ keyring set discover password
    Password for 'password' in 'discover': doe

Use those credentials in ``kibitzr.yml``::

    checks:
      - name: Discover
        url: https://www.discover.com/
        form:
          - id: userid
            creds: keyring.discover.login
          - id: password
            creds: keyring.discover.password
        delay: 5
        transform:
            - css: .current-balance
            - text
            - changes: verbose
        notify:
            - mailgun
        error: ignore
        period: 3600
        headless: false

Run kibitzr, it will take discover credentials from system keyring.

Note
----

Tested only with GNOME Keyring under Ubuntu 16.04.
Don't hesitate to open an issue if having any problems.

.. _`Kibitzr credentials documentation`: http://kibitzr.readthedocs.io/en/latest/credentials.html
.. _`Keyring documentation`: https://github.com/jaraco/keyring
