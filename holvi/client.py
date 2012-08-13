# -*- coding: utf-8 -*-
import os
from decorator import decorator

import utils
import filecrypt
from .container import Cluster, Vault
from .dataitem import DataItem
from .connection import Connection
from holvi.exceptions import HolviAPIException

@decorator
def require_auth(fn, cls, *args, **kwargs):
    """If Client is not yet authenticated, authenticates Client before
    doing requested operation.

    """
    if not cls.connection._is_authed:
        cls.auth()
    return fn(cls, *args, **kwargs)

class Client(object):
    """Client provides interface for performing Holvi server operations.
    Client's Connection is used by Vault/Cluster and DataItem objects.

    """
    __META_VERSION__ = 1

    def __init__(self, username, auth_data, auth_method='password',
                 enc_mode=utils.ENC_NONE, enc_key=None, iv=utils.IV_DEFAULT, apikey=None,
                 server_url=utils.SERVER_DEFAULT):
        """Initializer for Client.

        :param username: username used for authenticating client connection.
        :param auth_data: password used for authenticating client connection.
        :param auth_method: auth method used for authenticating client connection.
        :param enc_mode: encryption mode used for DataItem functions.
        :param enc_key: encryption key used for DataItem functions.
        :param apikey: client's unique apikey.
        :param server_url: server to be used.

        """
        self._username = username
        self._auth_data = auth_data
        self._auth_method = auth_method
        self._apikey = apikey
        self._request_size = 2097152
        self.encryption_mode = enc_mode
        self.crypt = filecrypt.FileCrypt(enc_key, iv)
        self.connection = Connection(server_url)

    @property
    def apikey(self):
        """Returns Client's apikey"""
        return self._apikey

    @apikey.setter
    def apikey(self, value):
        """Sets apikey for Client.

        :param value: new apikey.

        Sets the new apikey and resets the connection to non-authed.
        """
        self._apikey = value
        self.connection._is_authed = False

    @property
    def server_url(self):
        """Returns Client's server url."""
        return self.connection._server_url

    @server_url.setter
    def server_url(self, value):
        """Sets server for Client.

        :param value: new server url.

        Sets the server url and resets the connection to non-authed.

        """
        self.connection._server_url = value
        self.connection._is_authed = False

    @property
    def encryption_mode(self):
        """Returns Client's encryption mode"""
        return self._encryption_mode

    @encryption_mode.setter
    def encryption_mode(self, value):
        """Sets encryption mode for Client.

        :param value: new encryption mode.

        Validates the encryption mode and sets it if valid.

        """
        if utils.validate_encryption_mode(value):
            self._encryption_mode = value

    def set_encryption_key(self, value):
        """Sets encryption key for Client.

        :param value: new encryption key.

        """
        self.crypt._crypt_key = value

    def set_iv(self, value):
        """Sets initialization vector.

        :param value: new initialization vector

        """
        self.crypt._crypt_iv = value

    def set_password(self, value):
        """Sets password for Client.

        :param value: new password.

        Changes password used for authenticating Client..
        Resets connection to non-authed.

        """
        self._auth_data = value
        self.connection._is_authed = False

    @property
    def username(self):
        """Returns Client's username"""
        return self._username

    @username.setter
    def username(self, value):
        """Sets Client's username.

        :param value: new username.

        Changes username used for authenticating Client.
        Resets connection to non-authed.

        """
        self._username = value
        self.connection._is_authed = False

    def set_request_size(self, value):
        """Sets request size used in transactions.

        :param value: new request size.

        Validates value and changes request size if valid.

        """
        value = int(value)
        if value <= 0:
            raise HolviAPIException(600, "Request size must be larger than 0")
        self._request_size = value

    def auth(self):
        """Authenticates Client connection.
        Uses Client's authentication attributes (username, auth_data, auth_method, apikey).
        for authenticating Client's connection.
        """
        self.connection.auth(self._username, self._auth_data, self._auth_method, self._apikey)

    @require_auth
    def list_vaults(self, vault_type=None, id_=None, role=None):
        """Lists vaults.

        :param vault_type: Type of vaults to be searched.
        :param id_: ID of the vault to be searched.
        :param role: User's role to the vaults to be searched ['own', 'account', 'other'].

        Queries the Holvi server for vaults using provided parameters.
        Returns a list of Vault objects.

        """
        method = "list_vaults"
        params = {
            "vault_type": vault_type,
            "id_": id_,
            "role": role
            }
        response = self.connection.make_request(method, params)
        vaults = []
        for item in response['vaults']:
            vaults.append(Vault(self, **item))
        return vaults

    @require_auth
    def list_clusters(self, parent_id):
        """Lists clusters under a parent Cluster/Vault.

        :param parent_id: ID of the parent Vault/Cluster.

        Creates a Cluster with parent_id.
        Calls for Cluster's children and returns a list of Cluster objects.
        """
        cluster = Cluster(self, id=parent_id)
        return cluster.children

    @require_auth
    def add_vault(self, vault_type, name):
        """Adds a new Vault to Holvi server.

        :param vault_type: type for Vault.
        :param name: name for the Vault.

        Sends a request to add vault to Holvi server.
        Returns the created Vault object.
        """
        method = "add_vault"
        params = {
            "vault_type": vault_type,
            "name": name
            }
        response = self.connection.make_request(method, params)
        vault_item = response['vault']
        vault = Vault(self, **vault_item)
        return vault

    @require_auth
    def add_cluster(self, name, parent_id):
        """Adds a new Cluster to Holvi server.

        :param name: name of the created cluster.
        :param parent_id: id of the parent Cluster/Vault.

        Sends a request to add cluster to Holvi server.
        Returns the created Cluster object.
        """
        method = "add_cluster"
        params = {
            "parent_id": parent_id,
            "name": name
            }
        response = self.connection.make_request(method, params)

        cluster_item = response['cluster']
        cluster = Cluster(self, **cluster_item)
        return cluster

    @require_auth
    def remove_cluster(self, cluster_id=None):
        """Removes a Cluster from Holvi server.

        :param cluster_id: id of the cluster.

        Creates a Cluster object with cluster_id.
        Calls for Cluster's remove method.

        """
        cluster = Cluster(self, id=cluster_id)
        return cluster.remove()

    @require_auth
    def remove_vault(self, vault_id=None):
        """Removes a Vault from Holvi server.

        :param vault_id: id of the cluster.

        Creates a Vault object with vault_id.
        Calls for Vault's remove method.

        """
        vault = Vault(self, id=vault_id)
        return vault.remove()

    @require_auth
    def list_dataitems(self, parent_id):
        """Returns dataitems for Cluster/Vault.

        :param parent_id: id of the Cluster/Vault.

        Creates a Cluster with parent_id.
        Calls for Cluster's dataitems and returns a list of DataItems.

        """
        cluster = Cluster(self, id=parent_id)
        return cluster.dataitems

    @require_auth
    def store_data(self, parent_id, key, p_data, method="new", offset=None):
        """Stores data to Holvi server.

        :param parent_id: id of the parent Cluster/Vault where to store data to.
        :param key: name of the dataitem where to store data to.
        :param p_data: data to be stored.
        :param method: storing method ['new', 'append', 'replace', 'patch'].
        :param offset: starting byte when using mode 'patch'.

        Creates a DataItem with parent_id and key.
        Creates a iterator for data and calls for DataItem's store_data.

        """
        dataitem = DataItem(self, parent_id, key)

        if self.encryption_mode == utils.ENC_NONE:
            data = filecrypt.FileIterator(p_data, self._request_size)
        else:
            data = self.crypt.encrypt(p_data, self._request_size)

        result = dataitem.store_data(data, method, offset)
        return result

    @require_auth
    def fetch_data(self, parent_id, key):
        """Retrieves data from Holvi server.

        :param parent_id: id of the parent Cluster/Vault where to retrieve data from.
        :param key: name of the dataitem where to retrieve data from.

        Creates a DataItem with parent_id and key.
        Returns DataItem's data.

        """
        dataitem = DataItem(self, parent_id, key)
        return dataitem.data

    @require_auth
    def get_dataitem(self, parent_id, key):
        """Retrieves dataitem information from HolviServer.

        :param parent_id: id of the parent Cluster/Vault where to retrieve information from.
        :param key: name of the dataitem where to retrieve information from.

        Creates a DataItem with parent_id and key.
        Calls for DataItem's _get_item_info to retrieve information.
        Returns the DataItem.

        """
        dataitem = DataItem(self, parent_id, key)
        dataitem._get_item_info()
        return dataitem

    @require_auth
    def remove_dataitem(self, parent_id, key):
        """Removes dataitem from Holvi server.

        :param parent_id: id of the parent Cluster/Vault where to dataitem is.
        :param key: name of the dataitem.

        Creates a DataItem object with parent_id and key.
        Calls for DataItem's remove.

        """
        dataitem = DataItem(self, parent_id, key)
        return dataitem.remove()

