import unittest
import mock
import StringIO
import hashlib

import holvi.client as client
from holvi.exceptions import HolviCryptException, HolviAPIException, HolviDataItemException, HolviAuthException
from holvi.container import Cluster, Vault
from holvi.dataitem import DataItem
from holvi.filecrypt import FileIterator, CryptIterator, FileCrypt
from holvi.connection import Connection


class TestClientFunctions(unittest.TestCase):
    def setUp(self):
        self.client = client.Client('username', 'password')

    def test_add_vault(self):
        conn = mock.Mock()
        conn.make_request.return_value = {
            'vault': {
                'a': "a1",
                'b': 'b2'
            }
        }
        self.client.connection = conn

        result = self.client.add_vault('vault_type1', 'new_vault2')

        self.assertEquals(result.a, 'a1')
        self.assertEquals(result.b, 'b2')

        params = {
            'vault_type': 'vault_type1',
            'name': 'new_vault2'
        }
        conn.make_request.assert_called_once_with('add_vault', params)

    def test_add_cluster(self):
        conn = mock.Mock()
        conn.make_request.return_value = {
            'cluster': {
                    'a': 'a1',
                    'b': 'b1'
                }
            }
        self.client.connection = conn

        result = self.client.add_cluster(name="new_cluster", parent_id="1")

        self.assertEquals(result.a, 'a1')
        self.assertEquals(result.b, 'b1')
        params = {
                'name': 'new_cluster',
                'parent_id': '1'
            }
        conn.make_request.assert_called_once_with('add_cluster', params)

    @mock.patch('holvi.client.Cluster')
    def test_list_clusters(self, MockCluster):
        mock_instance = mock.Mock()
        mock_instance.children = ["Cluster1", "Cluster2"]
        MockCluster.return_value = mock_instance

        self.client.connection._is_authed = True
        result = self.client.list_clusters("1")

        MockCluster.assert_called_once_with(self.client, id="1")
        self.assertEquals(result, mock_instance.children)

    def test_list_vaults(self):
        conn = mock.Mock()
        conn.make_request.return_value = {
            "vaults": [{
                'a': 'a1',
                'b': 'b1'
                }]
            }
        self.client.connection = conn

        result = self.client.list_vaults(vault_type="type", id_="1")

        self.assertEquals(len(result), 1)
        self.assertEquals(result[0].a, 'a1')
        self.assertEquals(result[0].b, 'b1')
        params = {
            'vault_type': 'type',
            'id_': '1',
            'role': None
            }
        conn.make_request.assert_called_once_with('list_vaults', params)

    @mock.patch('holvi.client.Cluster')
    def test_list_dataitems(self, MockCluster):
        mock_instance = mock.Mock()
        mock_instance.dataitems = ["dataitem1", "dataitem2"]
        MockCluster.return_value = mock_instance

        self.client.connection._is_authed = True
        result = self.client.list_dataitems("1")

        MockCluster.assert_called_once_with(self.client, id="1")
        self.assertEquals(result, mock_instance.dataitems)

    @mock.patch('holvi.client.Cluster')
    def test_remove_cluster(self, MockCluster):
        mock_instance = mock.Mock()
        mock_instance.remove.return_value = "remove"
        MockCluster.return_value = mock_instance
        self.client.connection._is_authed = True

        result = self.client.remove_cluster("1")

        self.assertEquals(result, "remove")

    @mock.patch('holvi.client.Vault')
    def test_remove_vault(self, MockVault):
        mock_instance = mock.Mock()
        mock_instance.remove.return_value = "remove"
        MockVault.return_value = mock_instance
        self.client.connection._is_authed = True


        result = self.client.remove_vault("1")
        self.assertEquals(result, "remove")

    @mock.patch('holvi.client.DataItem')
    def test_remove_dataitem(self, MockDataItem):
        mock_instance = mock.Mock()
        mock_instance.remove.return_value = "remove"
        MockDataItem.return_value = mock_instance
        self.client.connection._is_authed = True


        result = self.client.remove_dataitem("1", "key")
        MockDataItem.assert_called_once_with(self.client, "1", "key")
        self.assertEquals(result, "remove")

    @mock.patch('holvi.client.DataItem')
    def test_fetch_data(self, MockDataItem):
        mock_instance = mock.Mock()
        mock_instance.data = "Test data"
        MockDataItem.return_value = mock_instance

        self.client.connection._is_authed = True
        result = self.client.fetch_data("1", "key")

        MockDataItem.assert_called_once_with(self.client, "1", "key")
        self.assertEquals(result, mock_instance.data)

    @mock.patch('holvi.client.DataItem')
    def test_store_data(self, MockDataItem):
        mock_instance = mock.Mock()
        mock_instance.store_data.return_value = "OK"
        MockDataItem.return_value = mock_instance

        self.client.connection._is_authed = True
        result = self.client.store_data("1", "key", "test_data")

        MockDataItem.assert_called_once_with(self.client, "1", "key")
        self.assertEquals(result, mock_instance.store_data())

        self.client.set_encryption_key('12345678901234561234567890123456')
        self.client.encryption_mode = 'ENC:AES256'
        self.client.connection._is_authed = True
        result = self.client.store_data("1", "key", "test_data")


    def test_change_encryption_mode(self):
        client = self.client

        with self.assertRaises(HolviCryptException):
            client.encryption_mode = "INVALID ENCRYPTION MODE"
        client.encryption_mode = "ENC:NONE"
        self.assertEquals(client.encryption_mode, "ENC:NONE")
        client.encryption_mode = "ENC:AES256"
        self.assertEquals(client.encryption_mode, "ENC:AES256")

    def test_change_apikey(self):
        client = self.client
        self.assertFalse(client.connection._is_authed)

        client.connection._is_authed = True
        self.assertTrue(client.connection._is_authed)

        client.apikey = "newkey"
        self.assertFalse(client.connection._is_authed)
        self.assertEquals(client.apikey, "newkey")

    def test_change_server_url(self):
        client = self.client
        self.assertFalse(client.connection._is_authed)

        client.connection._is_authed = True
        self.assertTrue(client.connection._is_authed)

        client.server_url = "newhost"
        self.assertFalse(client.connection._is_authed)
        self.assertEquals(client.server_url, "newhost")

    def test_change_encryption_key(self):
        client = self.client

        self.assertEquals(client.crypt._crypt_key, None)
        client.set_encryption_key("newkey")
        self.assertEquals(client.crypt._crypt_key, "newkey")

    def test_change_password(self):
        client = self.client
        self.assertFalse(client.connection._is_authed)

        client.connection._is_authed = True
        self.assertTrue(client.connection._is_authed)

        client.set_password("newpassword")
        self.assertFalse(client.connection._is_authed)
        self.assertEquals(client._auth_data, "newpassword")

    def test_change_username(self):
        client = self.client
        self.assertFalse(client.connection._is_authed)

        client.connection._is_authed = True
        self.assertTrue(client.connection._is_authed)

        client.username = "new-user"
        self.assertFalse(client.connection._is_authed)
        self.assertEquals(client.username, "new-user")

    def test_change_request_size(self):
        client = self.client

        client.set_request_size(1024)

        self.assertEquals(client._request_size, 1024)
        self.assertRaises(ValueError, client.set_request_size, "asdfasdf")
        self.assertRaises(TypeError, client.set_request_size, None)
        self.assertRaises(HolviAPIException, client.set_request_size, -1)

    def test_auth(self):
        conn = mock.Mock()
        self.client.connection = conn
        self.client.apikey = "apikey"

        self.client.auth()

        conn.auth.assert_called_once_with(self.client.username, self.client._auth_method,
                                          self.client._auth_data, self.client.apikey)

    def test_get_dataitem_info(self):
        conn = mock.Mock()
        self.client.connection = conn
        self.client.get_dataitem("1", "key")
        headers = {}
        headers['X-HOLVI-PARENT'] = "1"
        headers['X-HOLVI-KEY'] = "key"
        conn.make_query.assert_called_once_with(headers)


class TestCluster(unittest.TestCase):
    def setUp(self):
        self.client = client.Client('username', 'password')

    def test_cluster_init(self):
        arguments = {
                'name': 'cluster_name',
                'descendants': 1,
                'dataitems': 2,
                'parent_id': 1,
                'type': 'cluster',
                'id': 2
            }
        cluster = Cluster(self.client, **arguments)
        self.assertEquals(cluster._client, self.client)
        self.assertEquals(cluster.name, "cluster_name")
        self.assertEquals(cluster.descendants, 1)
        self.assertEquals(cluster._dataitem_count, 2)
        self.assertEquals(cluster.parent_id, 1)
        self.assertEquals(cluster.id, 2)

    def test_cluster_remove(self):
        conn = mock.Mock()
        self.client.connection = conn
        arguments = {
                'name': 'cluster_name',
                'descendants': 1,
                'dataitems': 2,
                'parent_id': 1,
                'type': 'cluster',
                'id': 2
            }
        cluster = Cluster(self.client, **arguments)

        response = cluster.remove()
        self.assertEquals(response, None)
        conn.make_request.assert_called_once_with('remove_cluster', {'cluster_id': 2})

    def test_cluster_children_list(self):
        cluster1_args = {
                'name': 'cluster1',
                'descendants': 0,
                'dataitems': 0,
                'parent_id': 2,
                'type': 'cluster',
                'id': 3
                }
        cluster2_args = {
                'name': 'cluster2',
                'descendants': 1,
                'dataitems': 1,
                'parent_id': 2,
                'type': 'cluster',
                'id': 4
                }

        conn = mock.Mock()
        conn.make_request.return_value = {
                'clusters': [
                    cluster1_args,
                    cluster2_args
                ]
            }
        self.client.connection = conn
        parent_args = {
                'name': 'Parent Cluster',
                'descendants': 2,
                'dataitems': 0,
                'parent_id': 1,
                'type': 'cluster',
                'id': 2
            }

        cluster = Cluster(self.client, **parent_args)
        response = cluster.children
        self.assertEquals(len(response), 2)
        self.assertEquals(response[0].name, cluster1_args['name'])
        self.assertEquals(response[1].name, cluster2_args['name'])
        conn.make_request.assert_called_once_with('list_clusters', {'parent_id': 2})

    def test_cluster_dataitems_list(self):
        conn = mock.Mock()
        conn.make_request.return_value = {
                'dataitems': [
                    "dataitem1",
                    "dataitem2"
                ]
            }
        self.client.connection = conn
        parent_args = {
                'name': 'Parent Cluster',
                'descendants': 0,
                'dataitems': 2,
                'parent_id': 1,
                'type': 'cluster',
                'id': 2
            }

        cluster = Cluster(self.client, **parent_args)
        response = cluster.dataitems
        self.assertEquals(len(response), 2)
        self.assertEquals(response[0].name, "dataitem1")
        self.assertEquals(response[0].parent_id, cluster.id)
        self.assertEquals(response[1].name, "dataitem2")
        self.assertEquals(response[1].parent_id, cluster.id)
        conn.make_request.assert_called_once_with('list_dataitems', {'cluster_id': 2})

    def test_cluster_to_text(self):
        parent_args = {
                'name': 'Parent Cluster',
                'descendants': 0,
                'dataitems': 2,
                'parent_id': 1,
                'type': 'cluster',
                'id': 2
            }
        cluster = Cluster(self.client, **parent_args)
        response = cluster.to_text

        self.assertEquals(response, "{0}:{1}:{2}:{3}:{4}".format(
                        parent_args['id'], parent_args['name'],
                        parent_args['parent_id'], parent_args['descendants'],
                        parent_args['dataitems'])
                        )

class TestVault(unittest.TestCase):
    def setUp(self):
        self.client = client.Client('username', 'password')

    def test_vault_init(self):
        arguments = {
                'name': 'cluster_name',
                'descendants': 1,
                'vault_type': 'test_type',
                'dataitems': 2,
                'type': 'test_type',
                'id': 1
            }
        vault = Vault(self.client, **arguments)
        self.assertEquals(vault._client, self.client)
        self.assertEquals(vault.name, "cluster_name")
        self.assertEquals(vault.descendants, 1)
        self.assertEquals(vault._dataitem_count, 2)
        self.assertEquals(vault.id, 1)

    def test_vault_remove(self):
        conn = mock.Mock()
        self.client.connection = conn
        arguments = {
                'name': 'cluster_name',
                'descendants': 1,
                'vault_type': 'test_type',
                'dataitems': 2,
                'type': 'test_type',
                'id': 1
            }
        vault = Vault(self.client, **arguments)

        result = vault.remove()
        self.assertEquals(result, None)
        conn.make_request.assert_called_once_with('remove_vault', {'vault_id': 1})

    def test_vault_to_text(self):
        parent_args = {
                'name': 'cluster_name',
                'descendants': 1,
                'vault_type': 'test_type',
                'dataitems': 2,
                'type': 'test_type',
                'id': 1
            }
        vault = Vault(self.client, **parent_args)

        response = vault.to_text

        self.assertEquals(response, "{0}:{1}:{2}:{3}:{4}".format(
                        parent_args['id'], parent_args['name'],
                        parent_args['vault_type'], parent_args['descendants'],
                        parent_args['dataitems'])
                        )


class TestDataItem(unittest.TestCase):

    def setUp(self):
        self.client = client.Client('username', 'password')
        self.keyname = "keyname"
        self.parent_id = 1

    def test_dataitem_init(self):
        dataitem = DataItem(self.client, self.parent_id, self.keyname)

        self.assertEquals(dataitem.name, self.keyname)
        self.assertEquals(dataitem.parent_id, self.parent_id)

    def test_fetch_data(self):
        headers = {}
        headers['X-HOLVI-KEY'] = self.keyname
        headers['X-HOLVI-PARENT'] = self.parent_id

        conn = mock.Mock()
        conn.make_transaction.return_value = mock.Mock(headers = {'X-HOLVI-HASH': "4321"})
        self.client.connection = conn

        dataitem = DataItem(self.client, self.parent_id, self.keyname)
        response = dataitem.data

        self.assertEquals(response['checksum'], "4321")
        self.assertEquals(type(response['data']), FileIterator)
        conn.make_transaction.assert_called_once_with(headers, "/fetch")

        self.client.set_encryption_key("12345678901234561234567890123456")
        self.client.encryption_mode = "ENC:AES256"
        response = dataitem.data
        self.assertEquals(type(response['data']), CryptIterator)

    def test_store_data(self):
        test_data = StringIO.StringIO("Some test data to be sent to server")
        md5 = hashlib.md5()
        md5.update(test_data.read())
        test_data.seek(0)
        headers = {}
        headers['X-HOLVI-STORE-MODE'] = "new"
        headers['X-HOLVI-KEY'] = self.keyname
        headers['X-HOLVI-PARENT'] = self.parent_id
        headers['X-HOLVI-META'] = 'v1:ENC:NONE::'
        headers['Content-Type'] = 'application/octet-stream'
        headers['X-HOLVI-HASH'] = md5.hexdigest()
        headers['Content-Length'] = len(test_data.read())
        test_data.seek(0)

        conn = mock.Mock()
        conn.make_transaction.return_value = "OK"
        self.client.connection = conn

        dataitem = DataItem(self.client, self.parent_id, self.keyname)
        response = dataitem.store_data(test_data, "new", offset=None)
        self.assertEquals(response, "OK")
        conn.make_transaction.assert_called_with(headers, '/store', 'Some test data to be sent to server')

        conn.reset_mock()
        test_data.seek(0)
        self.client.set_encryption_key("12345678901234561234567890123456")
        self.client.encryption_mode = "ENC:AES256"
        headers['X-HOLVI-META'] = 'v1:ENC:AES256::'

        response = dataitem.store_data(test_data, method="new", offset=None)
        self.assertEquals(response, "OK")
        conn.make_transaction.assert_called_with(headers, '/store', 'Some test data to be sent to server')

        with self.assertRaises(HolviDataItemException):
            dataitem.store_data(test_data, "new", offset=None)

        conn.reset_mock()
        test_data.seek(0)
        file_iter = FileIterator(test_data, 4)
        test_md5 = hashlib.md5()
        test_md5.update('ver')
        self.client.set_encryption_key("")
        self.client.encryption_mode = "ENC:NONE"
        headers['X-HOLVI-META'] = 'v1:ENC:NONE::'
        headers['X-HOLVI-HASH'] = test_md5.hexdigest()
        headers['Content-Length'] = 3
        headers['X-HOLVI-STORE-MODE'] = "append"
        response = dataitem.store_data(file_iter, "new", offset=None)
        self.assertEquals(response, "OK")
        self.assertEquals(conn.make_transaction.mock_calls[8], mock.call(headers, '/store', 'ver'))

    def test_store_with_patch(self):
        test_data = StringIO.StringIO("Some test data to be sent to server")
        md5 = hashlib.md5()
        md5.update(test_data.read())
        test_data.seek(0)
        headers = {}
        headers['X-HOLVI-STORE-MODE'] = "patch"
        headers['X-HOLVI-KEY'] = self.keyname
        headers['X-HOLVI-PARENT'] = self.parent_id
        headers['X-HOLVI-META'] = 'v1:ENC:NONE::'
        headers['Content-Type'] = 'application/octet-stream'
        headers['X-HOLVI-HASH'] = md5.hexdigest()
        headers['X-HOLVI-OFFSET'] = 13
        headers['Content-Length'] = len(test_data.read())
        test_data.seek(0)

        conn = mock.Mock()
        conn.make_transaction.return_value = "OK"
        self.client.connection = conn

        dataitem = DataItem(self.client, self.parent_id, self.keyname)
        response = dataitem.store_data(test_data, "patch", offset=13)
        self.assertEquals(response, "OK")
        conn.make_transaction.assert_called_with(headers, '/store', 'Some test data to be sent to server')
        conn.reset_mock()
        test_data.seek(0)
        test_md5 = hashlib.md5()
        test_md5.update('ver')
        headers['X-HOLVI-HASH'] = test_md5.hexdigest()
        headers['X-HOLVI-OFFSET'] = 13 + len(test_data.read()) - 4 # start offset + len(content) - len(chunksize)
        headers['Content-Length'] = 3
        test_data.seek(0)
        file_iter = FileIterator(test_data, 4)
        response = dataitem.store_data(file_iter, "patch", offset=13)
        self.assertEquals(response, "OK")
        self.assertEquals(conn.make_transaction.mock_calls[8], mock.call(headers, '/store', 'ver'))

    def test_dataitem_length(self):
        conn = mock.Mock()
        conn.make_query.return_value = {
                                    'Content-Length': 1234,
                                    'Last-Modified': "01-01-2000",
                                    'X-HOLVI-HASH': "4321",
                                    'X-HOLVI-META': "metainfo"
                                    }
        self.client.connection = conn

        headers = {}
        headers['X-HOLVI-PARENT'] = self.parent_id
        headers['X-HOLVI-KEY'] = self.keyname

        dataitem = DataItem(self.client, self.parent_id, self.keyname)
        response = dataitem.length

        self.assertEquals(response, 1234)
        self.assertIsNotNone(dataitem.key_length)
        conn.make_query.assert_called_once_with(headers)

    def test_dataitem_checksum(self):
        conn = mock.Mock()
        conn.make_query.return_value = {
                                    'Content-Length': 1234,
                                    'Last-Modified': "01-01-2000",
                                    'X-HOLVI-HASH': "4321",
                                    'X-HOLVI-META': "metainfo"
                                    }
        self.client.connection = conn

        headers = {}
        headers['X-HOLVI-PARENT'] = self.parent_id
        headers['X-HOLVI-KEY'] = self.keyname

        dataitem = DataItem(self.client, self.parent_id, self.keyname)
        response = dataitem.checksum

        self.assertEquals(response, "4321")
        self.assertIsNotNone(dataitem.key_hash)
        conn.make_query.assert_called_once_with(headers)

    def test_dataitem_last_modified(self):
        conn = mock.Mock()
        conn.make_query.return_value = {
                                    'Content-Length': 1234,
                                    'Last-Modified': "01-01-2000",
                                    'X-HOLVI-HASH': "4321",
                                    'X-HOLVI-META': "metainfo"
                                    }
        self.client.connection = conn

        headers = {}
        headers['X-HOLVI-PARENT'] = self.parent_id
        headers['X-HOLVI-KEY'] = self.keyname

        dataitem = DataItem(self.client, self.parent_id, self.keyname)
        response = dataitem.last_modified

        self.assertEquals(response, "01-01-2000")
        self.assertIsNotNone(dataitem.key_last_modified)
        conn.make_query.assert_called_once_with(headers)

    def test_dataitem_meta(self):
        conn = mock.Mock()
        conn.make_query.return_value = {
                                    'Content-Length': 1234,
                                    'Last-Modified': "01-01-2000",
                                    'X-HOLVI-HASH': "4321",
                                    'X-HOLVI-META': "metainfo"
                                    }
        self.client.connection = conn

        headers = {}
        headers['X-HOLVI-PARENT'] = self.parent_id
        headers['X-HOLVI-KEY'] = self.keyname

        dataitem = DataItem(self.client, self.parent_id, self.keyname)
        response = dataitem.meta

        self.assertEquals(response, "metainfo")
        self.assertIsNotNone(dataitem.key_meta)
        conn.make_query.assert_called_once_with(headers)

    def test_dataitem_remove(self):
        conn = mock.Mock()
        self.client.connection = conn

        dataitem = DataItem(self.client, self.parent_id, self.keyname)
        dataitem.remove()
        params = {
                'cluster_id': dataitem.parent_id,
                'key': dataitem.name
            }
        conn.make_request.assert_called_once_with('remove_dataitem', params)

class TestConnection(unittest.TestCase):
    def setUp(self):
        self.username = "username"
        self.password = "password"
        self.auth_method = "password"
        self.apikey = "apikey"
        self.server = "server"

    def test_connection_init(self):
        connection = Connection(self.server)
        self.assertEquals(connection._server_url, self.server)

    @mock.patch.object(Connection, 'make_request')
    def test_connection_auth(self, mock_method):
        mock_method.return_value = {'result': 'success'}
        params = {
            'username': self.username,
            'auth_data': self.password,
            'auth_method': self.auth_method,
            'apikey': self.apikey
            }
        connection = Connection(self.server)
        self.assertFalse(connection._is_authed)

        connection.auth(self.username, self.password, self.auth_method, self.apikey)
        connection.make_request.assert_called_once_with("auth", params)
        self.assertTrue(connection._is_authed)

        mock_method.return_value = {'result': 'exception',
                                    'exception': {
                                        'message': 'Auth',
                                        'id': 1,
                                        'type': 'HolviAuthException'
                                        }
                                    }
        mock_method.reset_mock()
        with self.assertRaises(HolviAuthException):
            connection.auth(self.username, self.password, self.auth_method, self.apikey)
        connection.make_request.assert_called_once_with("auth", params)
        self.assertFalse(connection._is_authed)

    @mock.patch('urllib2.build_opener')
    @mock.patch('json.JSONDecoder')
    def test_connection_make_request(self, MockJSONDecoder, MockUrllib):
        mock_instance1 = mock.Mock()
        mock_instance1.open.return_value = StringIO.StringIO("Test response")
        MockUrllib.return_value = mock_instance1

        mock_instance2 = mock.Mock()
        mock_instance2.decode.return_value = {'result': 'success'}
        MockJSONDecoder.return_value = mock_instance2

        connection = Connection(self.server)
        response = connection.make_request('method', 'params')
        self.assertEquals({'result': 'success'}, response)
        mock_instance1.open.assert_called_once_with(self.server + '/api/1.0/json', '{"params": "params", "method": "method"}')
        mock_instance2.decode.assert_called_once_with("Test response")

    @mock.patch('urllib2.urlopen')
    def test_connection_make_transaction(self, MockUrllib):
        mock_instance1 = mock.Mock()
        mock_instance1.headers = {'X-HOLVI-RESULT': 'OK'}
        MockUrllib.return_value = mock_instance1
        headers = {}
        headers['Test-header'] = 'value'

        connection = Connection(self.server)
        response = connection.make_transaction(headers, '/fetch')
        self.assertEquals(MockUrllib.call_args[0][0].headers, headers)
        self.assertEquals(response.headers['X-HOLVI-RESULT'], 'OK')

        mock_instance1.headers = {'X-HOLVI-RESULT': 'ERROR: 404 Not found'}
        with self.assertRaises(HolviDataItemException):
            response = connection.make_transaction(headers, '/fetch')

    @mock.patch('urllib2.urlopen')
    def test_connection_make_query(self, MockUrllib):
        mock_instance1 = mock.Mock()
        mock_instance1.headers = {'X-HOLVI-RESULT': 'OK'}
        MockUrllib.return_value = mock_instance1
        headers = {}
        headers['Test-header'] = 'value'

        connection = Connection(self.server)
        response = connection.make_query(headers)
        self.assertEquals(MockUrllib.call_args[0][0].headers, headers)
        self.assertEquals(response['X-HOLVI-RESULT'], 'OK')

        mock_instance1.headers = {'X-HOLVI-RESULT': 'ERROR: 404 Not found'}
        with self.assertRaises(HolviDataItemException):
            response = connection.make_query(headers)

        mock_instance1.headers = {'X-HOLVI-RESULT': 'ERROR: 404 Not found'}


class TestFileHandling(unittest.TestCase):

    def test_crypt_iterator(self):
        original_data = StringIO.StringIO("test data to be iterated")

        with self.assertRaises(HolviCryptException):
            enc_iterator = FileCrypt('Invalidkey', '1234567890123456')
            encrypt = enc_iterator.encrypt(original_data, 1)

        with self.assertRaises(HolviCryptException):
            enc_iterator = FileCrypt('12345678901234561234567890123456', 'InvalidIV')
            encrypt = enc_iterator.encrypt(original_data, 1)

        with self.assertRaises(HolviCryptException):
            enc_iterator = FileCrypt('Invalidkey', 'InvalidIV')
            encrypt = enc_iterator.encrypt(original_data, 1)

        enc_iterator = FileCrypt('12345678901234561234567890123456', '1234567890123456')

        data_enc_out = StringIO.StringIO()
        encrypt = enc_iterator.encrypt(original_data, 1)
        for data in encrypt:
            data_enc_out.write(data)

        data_enc_out.seek(0)
        self.assertNotEqual(original_data.read(), data_enc_out.read())
        data_enc_out.seek(0)

        data_dec_out = StringIO.StringIO()

        with self.assertRaises(HolviCryptException):
            dec_iterator = FileCrypt('Invalidkey', '1234567890123456')
            decrypt = dec_iterator.decrypt(data_enc_out, 1)

        with self.assertRaises(HolviCryptException):
            dec_iterator = FileCrypt('12345678901234561234567890123456', 'InvalidIV')
            decrypt = dec_iterator.decrypt(data_enc_out, 1)

        with self.assertRaises(HolviCryptException):
            dec_iterator = FileCrypt('Invalidkey', 'InvalidIV')
            decrypt = dec_iterator.decrypt(data_enc_out, 1)

        dec_iterator = FileCrypt('12345678901234561234567890123456', '1234567890123456')
        decrypt = dec_iterator.decrypt(data_enc_out, 1)

        for data in decrypt:
            data_dec_out.write(data)

        original_data.seek(0), data_dec_out.seek(0)
        self.assertEquals(original_data.read(), data_dec_out.read())

    def test_file_iterator(self):
        original_data = StringIO.StringIO("test data to be iterated")

        file_iterator = FileIterator(original_data, 1)

        iter_out = StringIO.StringIO()
        for data in file_iterator:
            iter_out.write(data)

        original_data.seek(0), iter_out.seek(0)
        self.assertEquals(original_data.read(), iter_out.read())
