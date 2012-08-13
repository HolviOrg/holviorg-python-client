# -*- coding: utf-8 -*-

from holvi.dataitem import DataItem
from holvi.exceptions import HolviAPIException

class Cluster(object):
    """ Cluster provides methods for handling clusters.

    """
    def __init__(self, client, **kwargs):
        """Initializer for Cluster

        :param client: Client used by Cluster methods.
        :param kwargs: Attributes for the cluster.

        """
        if 'dataitems' in kwargs:
            self._dataitem_count = kwargs.pop('dataitems')
        else:
            self._dataitem_count = 0
        self.__dict__.update(kwargs)
        self._client = client

    def remove(self):
        """removes cluster using it's own id"""
        method = "remove_cluster"
        params = {
            "cluster_id": self.id
            }
        response = self._client.connection.make_request(method, params)
        return

    @property
    def children(self):
        """Lists child Clusters directly under the cluster.

        Queries the Holvi server with cluster's own ID and returns a list of child Clusters.

        """
        method = "list_clusters"
        params = {
            "parent_id": self.id
            }
        response = self._client.connection.make_request(method, params)

        clusters = []
        for item in response['clusters']:
            clusters.append(Cluster(self._client, **item))
        return clusters

    @property
    def dataitems(self):
        """Lists DataItems (dataitems) directly under the cluster.

        Queries the Holvi server with cluster's own ID and returns a list of DataItems.

        """
        method = "list_dataitems"
        params = {
            "cluster_id": self.id
            }
        response = self._client.connection.make_request(method, params)

        data_items = []
        for item in response['dataitems']:
            data_items.append(DataItem(self._client, self.id, item))
        return data_items

    @property
    def to_text(self):
        """Returns textual representation of the cluster.

        """
        return "{0}:{1}:{2}:{3}:{4}".format(self.id, self.name, self.parent_id, self.descendants, self._dataitem_count)


class Vault(Cluster):
    """Vault provides methods for handling vaults.

    """
    def __init__(self, client, **kwargs):
        """Vault initializer.

        :param client: Client used by Vault methods.

        """
        Cluster.__init__(self, client, **kwargs)

    def remove(self):
        """Removes vault using it's own ID.

        """
        method = "remove_vault"
        params = {
            "vault_id": self.id
            }
        self._client.connection.make_request(method, params)
        return

    @property
    def to_text(self):
        """Return textual representation of the vault.

        """
        return "{0}:{1}:{2}:{3}:{4}".format(self.id, self.name, self.vault_type, self.descendants, self._dataitem_count)


