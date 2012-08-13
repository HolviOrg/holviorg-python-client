.. highlight:: rst

******************************************************
Holvi.org Python Client Library Installation and usage
******************************************************

This document will briefly demonstrate you how to use Holvi.org Python Client Library.

Before you install
==================

To install and use Holvi.org Python Client library you will need `Python <http://www.python.org/>`_ version 2.7.
Client library is developed and tested using version 2.7.2.

Installation
============

To use Holvi.org Python Client Library you first need to download and install it. The installation will also include the holvi-cli command line utility for managing vaults and data items.

Installing package::

    easy_install HolviClient-1.0-py2.7.egg

To check your installation has completed succcesfully::

    python
    Python 2.7.2 (default, Jun 12 2011, 15:08:59) [MSC v.1500 32 bit (Intel)] on win32
    Type "help", "copyright", "credits" or "license" for more information.
    >> import holvi
    
If you can import holvi without errors your installation has completed succesfully.

Usage
=====

You can use Holvi.org Client directly from the command line or create your own client application by including Holvi.org
Client Library to your project.

This section will briefly demonstrate basic usage of CLI Client as well as including Holvi.org Client Library in your project.

Using Command-line interface client (CLI Client)
------------------------------------------------

Once you have installed Holvi.org Client you can use the client by typing::

    holvi-cli
    
To get help using CLI Client, you can always use -h / --help argument::
    
    holvi-cli --help

CLI parameters
--------------

Using Holvi.org CLI Client requires you to provide at least authentication credentials and action as command line parameters.
Information needed to use the Client are following:

* ``--username / -u`` *\* (Required)*
    *Your username to Holvi.org service.*
* ``--password / -p`` *\* (Required)*
    *Your account password to Holvi.org service.*
* ``--apikey / -k`` *\* (Required)*
    *API-key to Holvi.org service. You can check your API-keys from profile page.*

add-vault
~~~~~~~~~
    * ``--name / -n`` *\* (Required)*
        *Name for the new vault.*
    * ``--type / -t`` *\* (Required)*
        *Type for the new vault.*
    
    Example usage::
    
        holvi-cli --username holviuser --password holvipassword --apikey abc add-vault --name My new vault 
        --type my_application_type
        
add-cluster
~~~~~~~~~~~
    * ``--id / -id`` *\* (Required)*
        *Parent ID for the new cluster.*
    * ``--name / -n`` *\* (Required)*
        *Name for the new cluster.*
        
    Example usage::
    
        holvi-cli --username holviuser --password holvipassword --apikey abc add-cluster -id 35 -n New cluster
        
remove-vault
~~~~~~~~~~~~
* ``--id / -id`` *\* (Required)*
    *ID of the vault.*

Example usage::

    holvi-cli --username holviuser --password holvipassword --apikey abc remove-vault -id 35
        
remove-cluster
~~~~~~~~~~~~~~
* ``--id / -id`` *\* (Required)*
    *ID of the cluster.*
* ``--name / -n``
    *Name of the cluster (if given, ID is considered as parent id).*

Example usage::

    holvi-cli --username holviuser --password holvipassword --apikey abc remove-cluster -id 36
    
    holvi-cli --username holviuser --password holvipassword --apikey abc remove-cluster -n New cluster -id 35
        
remove-dataitem
~~~~~~~~~~~~~~~
* ``--id / -id`` *\* (Required)*
    *Parent ID of the data item.* 
* ``--name / -n`` *\* (Required)*
    *Name of the data item.*
 
Example usage::

    holvi-cli --username holviuser --password holvipassword --apikey abc remove-dataitem -id 35 -n my_text_file.txt
        
list-vaults
~~~~~~~~~~~
* ``--id / -id``
    *ID of the vault (search by ID).*
* ``--type / -t``
    *Type for the searched vaults (search by type).*
* ``--role / -r``
    *User's relationship to searched vaults ('own', 'account', 'other').*

Example usage::

    holvi-cli --username holviuser --password holvipassword --apikey abc list-vaults        
    
    holvi-cli --username holviuser --password holvipassword --apikey abc list-vaults --id 35
    
    holvi-cli --username holviuser --password holvipassword --apikey abc list-vaults --type my_application_type
    
    holvi-cli --username holviuser --password holvipassword --apikey abc list-vaults --role own
        
list-clusters
~~~~~~~~~~~~~
* ``--id / -id`` *\* (Required)*
    *Parent ID for listed clusters.*

Example usage::

    holvi-cli --username holviuser --password holvipassword --apikey abc list-clusters --id 35
        
list-dataitems
~~~~~~~~~~~~~~
* ``--id / -id`` *\* (Required)*
    *Parent ID for listed data items.*
       
Example usage::

    holvi-cli --username holviuser --password holvipassword --apikey abc list-dataitems --id 35
 
store
~~~~~
* ``--id / -id`` *\* (Required)*
    *Parent ID of data item.*
* ``--name / -n`` *\* (Required)*
    *Name of the data item.*
* ``--method / -m``
    *Method used for storing ('new', 'replace', 'append', 'patch') Default: 'new'.*
* ``--file / -f``
    *Input file to be used for storing.*
* ``--offset / -o``
    *If using method 'patch', starting byte for storing.*
* ``--cryptkey / -ck``
    *File containing 32 bytes long encryption key.*
 
Example usage::

    holvi-cli --username holviuser --password holvipassword --apikey abc store -id 35 -n my_text_file.txt 
    --file C:\my_text_file.txt 
    
    holvi-cli --username holviuser --password holvipassword --apikey abc store -id 35 -n my_text_file.txt 
    --file C:\my_text_file.txt --method replace

    holvi-cli --username holviuser --password holvipassword --apikey abc store -id 35 -n my_text_file.txt 
    --file C:\my_text_file.txt --cryptkey C:\my_cryptkey_file --method replace
    
    ECHO sample input| holvi-cli --username holviuser --password holvipassword --apikey abc store -id 35 -n echo_input.txt 
      
fetch
~~~~~
* ``--id / -id`` *\* (Required)*
    *Parent ID of data item.*
* ``--name / -n`` *\* (Required)*
    *Name of the data item.*
* ``--file / -f``
    *Output file to be used for writing retrieved data.*
* ``--cryptkey / -ck``
    *File containing 32 bytes long decryption key.*
* ``--info / -i``
    *Retrieve only data item information (content length, checksum, etc.)*

Example usage::

    holvi-cli --username holviuser --password holvipassword --apikey abc fetch -id 35 -n my_text_file.txt 
    --file C:\my_text_file_output.txt 
    
    holvi-cli --username holviuser --password holvipassword --apikey abc fetch -id 35 -n my_text_file.txt > my_txt_file_output.txt
    
    holvi-cli --username holviuser --password holvipassword --apikey abc fetch -id 35 -n my_encrypted_text.txt 
    -ck C:\my_cryptkey_file > my_decrypted_text.txt
        
Including Holvi.org Library in your project
-------------------------------------------
Holvi.org Client Library can be used in your own projects by simply importing it::
    
    python
    Python 2.7.2 (default, Jun 12 2011, 15:08:59) [MSC v.1500 32 bit (Intel)] on win32
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import holvi
    >>> client = holvi.Client(username="username", auth_data="password", apikey="apikey")
    
Add vault
~~~~~~~~~
Vaults can be added by providing type and name for vault::

    >>> vault = client.add_vault(vault_type="my_application_type", name="New vault")
    >>> vault.id
    1
    
Add cluster
~~~~~~~~~~~
Clusters can be added by providing name and parent ID::
    >>> cluster = client.add_cluster(name="New cluster", parent_id=1)
    >>> cluster.id
    2
    
Store / Fetch data
~~~~~~~~~~~~~~~~~~
Data can be stored / fetched by providing the ID of the Vault or Cluster where dataitem is located and the name of the dataitem.
Data itself needs to be `File-like objects <http://docs.python.org/library/stdtypes.html#file-objects>`_

Storing and fetching data::

    >>> client.store_data(parent_id = 1, key = "dataitem_name", p_data = StringIO.StringIO('Example data'))
    'OK'
    dataitem = client.get_dataitem(parent_id=1, key="dataitem_name")
    >>> dataitem.meta
    'v1:ENC:NONE::' 
    >>> dataitem.data
    {'checksum': 'c13b2bc2027489c3398a3113f47c800a', 'data': <holvi.filecrypt.FileIterator object at ...>}
    >>> response = client.fetch_data(parent_id = 1, key = "dataitem_name")
    >>> print response
    {'checksum': 'c13b2bc2027489c3398a3113f47c800a', 'data': <holvi.filecrypt.FileIterator object at ...>}
    >>> for data in response['data']:
    ...     print data
    Example data
    >>> response['data']._md5.hexdigest()
    'c13b2bc2027489c3398a3113f47c800a'
    
Encryption enabled storing and fetching data::

    >>> client.set_encryption_key('12345678901234567890123456789012')
    >>> client.encryption_mode = 'ENC:AES256'
    >>> client.store_data(parent_id = 1, key = "dataitem_name", p_data = StringIO.StringIO('Example data'), method='replace')
    >>> dataitem = client.get_dataitem(parent_id=1, key="dataitem_name")
    >>> dataitem.meta
    'v1:ENC:AES256'
    >>> dataitem.data
    {'checksum': '84b38ae24dd7386227f636b5111434e2', 'data': <holvi.filecrypt.CryptIterator object at ...>}
    >>> response = client.fetch_data(parent_id = 1, key = "dataitem_name")
    >>> print response
    {'checksum': '84b38ae24dd7386227f636b5111434e2', 'data': <holvi.filecrypt.CryptIterator object at ...>}
    >>> for data in response['data']:
    ...     print data
    Example data
    >>> response['data']._md5.hexdigest()
    '84b38ae24dd7386227f636b5111434e2'
    
Removing cluster
~~~~~~~~~~~~~~~~
Cluster can be removed by providing ID of the cluster::

    >>> client.remove_cluster(cluster_id = 2)

Removing vault
~~~~~~~~~~~~~~
Vault can be removed by providing ID of the vault (but be careful)::

    >>> client.remove_vault(vault_id = 1)
    
Removing dataitem
~~~~~~~~~~~~~~~~~
Dataitem can be removed by providing ID::
    >>> client.remove_dataitem(parent_id=1, key="dataitem_name")
    
Listing dataitems, cluster and vaults
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Vault can be listed without any parameters. Possible parameters are *vault_type*, *id_*, and *role*. These are used for filtering vaults::

    >>> vaults = client.list_vaults()
    [<holvi.container.Vault object at ...>]
    
Listing clusters needs parent ID as parameter::

    >>> clusters = client.list_clusters(parent_id=1)
    [<holvi.container.Cluster object at ...>]
    
Listing dataitems needs parent ID as parameter::

    >>> dataitems = client.list_dataitems(parent_id=1)
    [<holvi.dataitem.DataItem object at ...>]
    
More information
~~~~~~~~~~~~~~~~
For more details about Client API please refer to :doc:`library`
