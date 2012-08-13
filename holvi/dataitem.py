# -*- coding: utf-8 -*-

import utils
import filecrypt
import hashlib
from holvi.exceptions import HolviDataItemException


class DataItem(object):
    """DataItem provides methods for handling data.

    """
    def __init__(self, client, parent_id, key):
        """Initializer for DataItem.

        :param client: Client used by DataItem methods.
        :param parent_id: ID number of the Vault/Cluster where the DataItem is in.
        :param key: Name of the dataitem.

        """
        self._client = client
        self.parent_id = parent_id
        self.name = key
        self.key_length = None
        self.key_last_modified = None
        self.key_hash = None
        self.key_meta = None
        self.key_data = None
        self._info_retrieved = False


    @property
    def data(self):
        """Returns a dict that contains DataItem checksum and data.
        Queries the Holvi server with dataitems's parent ID and returns a dictionary.
        Dictionary contains keys 'data' and 'checksum'.

        """
        headers = {}
        headers['X-HOLVI-KEY'] = self.name
        headers['X-HOLVI-PARENT'] = self.parent_id
        url_suffix = "/fetch"
        data = None

        response = self._client.connection.make_transaction(headers, url_suffix)

        checksum = response.headers.get('X-HOLVI-HASH')
        if self._client.encryption_mode == utils.ENC_AES256:
            self.key_data = self._client.crypt.decrypt(response, self._client._request_size)
        else:
            self.key_data = filecrypt.FileIterator(response, self._client._request_size)

        return {'data': self.key_data,
                'checksum': checksum}

    def store_data(self, data, method, offset):
        """Stores data to Holvi server.

        :param data: File-like object to be stored.
        :param method: Storing method ['new', 'replace', 'patch', 'append'].
        :param offset: Starting byte when using method 'patch'.

        """
        headers = {}
        headers['X-HOLVI-STORE-MODE'] = method
        headers['X-HOLVI-KEY'] = self.name
        headers['X-HOLVI-PARENT'] = self.parent_id
        headers['X-HOLVI-META'] = 'v{meta_version}:{enc}::'.format(meta_version=str(self._client.__META_VERSION__),
                                                                       enc=self._client._encryption_mode)

        if method == 'patch':
            headers['X-HOLVI-OFFSET'] = offset

        headers['Content-Type'] = 'application/octet-stream'

        url_suffix = "/store"
        respone = None
        result = None

        try:
            data_chunk = data.next()
            md5 = hashlib.md5()
            md5.update(data_chunk)
            headers['X-HOLVI-HASH'] = md5.hexdigest()
            headers['Content-Length'] = len(data_chunk)
            self._client.connection.make_transaction(headers, url_suffix, data_chunk)
        except StopIteration:
            raise HolviDataItemException(700, "Empty content")

        for data_chunk in data:
            md5 = hashlib.md5()
            md5.update(data_chunk)
            headers['X-HOLVI-HASH'] = md5.hexdigest()
            headers['Content-Length'] = len(data_chunk)
            if method != 'patch':
                headers['X-HOLVI-STORE-MODE'] = 'append'
            elif method == 'patch':
                offset += len(data_chunk)
                headers['X-HOLVI-OFFSET'] = offset
            self._client.connection.make_transaction(headers, url_suffix, data_chunk)

        return "OK"

    @property
    def length(self):
        """Returns DataItem length (size).

        """
        if not self._info_retrieved:
            self._get_item_info()
        return self.key_length

    @property
    def checksum(self):
        """Returns DataItem checksum.

        """
        if not self._info_retrieved:
            self._get_item_info()
        return self.key_hash

    @property
    def last_modified(self):
        """Returns DataItem last modified date.

        """
        if not self._info_retrieved:
            self._get_item_info()
        return self.key_last_modified

    @property
    def meta(self):
        """Returns DataItem metadata.

        """
        if not self._info_retrieved:
            self._get_item_info()
        return self.key_meta

    def remove(self):
        """Removes dataitem using it's parent_id and name (key).

        """
        method = "remove_dataitem"
        params = {
            'cluster_id': self.parent_id,
            'key': self.name
            }
        response = self._client.connection.make_request(method, params)

    def _get_item_info(self):
        """Queries Holvi server for DataItem information.

        """
        headers = {}
        headers['X-HOLVI-PARENT'] = self.parent_id
        headers['X-HOLVI-KEY'] = self.name
        response = self._client.connection.make_query(headers)
        self.key_length = response.get('Content-Length', None)
        self.key_last_modified = response.get('Last-Modified', None)
        self.key_hash = response.get('X-HOLVI-HASH', None)
        self.key_meta = response.get('X-HOLVI-META', None)
        self._info_retrieved = True
