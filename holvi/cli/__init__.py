# -*- coding: utf-8 -*-
import sys
import argparse
import io
import StringIO
import holvi
import hashlib
import urllib2

from holvi.exceptions import HolviException

def main(argv=sys.argv):

    parser = argparse.ArgumentParser(description='Holvi.org Python CLI Client', usage="holvi-cli -u USERNAME -p PASSWORD -k APIKEY [-s SERVER] ACTION [options]")
    parser.add_argument('--version', action='version', version='Holvi.org CLI Client 1.0')
    auth_group = parser.add_argument_group('authentication')
    auth_group.add_argument('--user', '-u', action="store", required=True, help="username to be used for authentication")
    auth_group.add_argument('--password', '-p', action="store", required=True, help="password to be used for authentication")
    auth_group.add_argument('--apikey', '-k', action="store", required=True, help="client's API-key")
    auth_group.add_argument('--server', '-s', action="store", default=holvi.utils.SERVER_DEFAULT, help="server to be used (default: https://my.holvi.org/)")

    cmd_parsers = parser.add_subparsers(title='available actions')

    add_vault_parser = cmd_parsers.add_parser('add-vault', help="add a new vault")
    add_vault_parser.add_argument('--name', '-n', required=True, help="name for the new vault")
    add_vault_parser.add_argument('--type', '-t', required=True, help="application type for the new vault")
    add_vault_parser.set_defaults(func=add_vault)

    add_cluster_parser = cmd_parsers.add_parser('add-cluster', help="add a new cluster")
    add_cluster_parser.add_argument('--name', '-n', required=True, help="name for the new cluster")
    add_cluster_parser.add_argument('--id', '-id', required=True, help="parent id for the new cluster")
    add_cluster_parser.set_defaults(func=add_cluster)

    remove_vault_parser = cmd_parsers.add_parser('remove-vault', help="remove vault")
    remove_vault_parser.add_argument('--id', '-id', required=True, help="id of the vault")
    remove_vault_parser.set_defaults(func=remove_vault)

    remove_cluster_parser = cmd_parsers.add_parser('remove-cluster', help="remove cluster")
    remove_cluster_parser.add_argument('--id', '-id', required=True, help="id of the cluster")
    remove_cluster_parser.add_argument('--name', '-n', help="name of the cluster")
    remove_cluster_parser.set_defaults(func=remove_cluster)

    remove_dataitem_parser = cmd_parsers.add_parser('remove-dataitem', help="remove data item")
    remove_dataitem_parser.add_argument('--id', '-id', required=True, help="parent id")
    remove_dataitem_parser.add_argument('--name', '-n', required=True, help="name of the data item")
    remove_dataitem_parser.set_defaults(func=remove_dataitem)

    list_vaults_parser = cmd_parsers.add_parser('list-vaults', help="list vaults")
    list_vaults_parser.add_argument('--role', '-r', choices=('account', 'own', 'other'), help='relationship to vault: own / account / other')
    list_vaults_parser.add_argument('--id', '-id', help="id of the searched vault")
    list_vaults_parser.add_argument('--type', '-t', help="application type of the searched vault")
    list_vaults_parser.set_defaults(func=list_vaults)

    list_clusters_parser = cmd_parsers.add_parser('list-clusters', help="list clusters")
    list_clusters_parser.add_argument('--id', '-id', required=True, help="parent id") # Help message?
    list_clusters_parser.set_defaults(func=list_clusters)

    list_dataitems_parser = cmd_parsers.add_parser('list-dataitems', help="list data items")
    list_dataitems_parser.add_argument('--id', '-id', required=True, help="identifier of the parent vault or cluster")
    list_dataitems_parser.set_defaults(func=list_dataitems)

    store_data_parser = cmd_parsers.add_parser('store', help="store data item")
    store_data_parser.add_argument('--id', '-id', required=True, help="identifier of the parent vault or cluster")
    store_data_parser.add_argument('--name', '-n', required=True, help="data item name")
    store_data_parser.add_argument('--method', '-m', choices=('new', 'replace', 'append', 'patch'), default='new', help="storing method")
    store_data_parser.add_argument('--file', '-f', type=argparse.FileType('rb'), help="file containing the data to be stored")
    store_data_parser.add_argument('--offset', '-o', type=int, help="byte offset")
    encryption_group = store_data_parser.add_mutually_exclusive_group(required=True)
    encryption_group.add_argument('--cryptkey', '-ck', type=argparse.FileType('rb'), help="path to cipher key file (filesize of 32 bytes required for AES256)")
    encryption_group.add_argument('--no-encryption', '-nocrypt', action="store_true", default=False, help="disable encryption")
    store_data_parser.add_argument('--initvector', '-iv', type=argparse.FileType('rb'), default=None, help="path to initialization vector file (filesize of 16 bytes required for AES256), IV defaults to a value of 0x31323334353637383930313233343536.")
    store_data_parser.set_defaults(func=store_data)

    fetch_data_parser = cmd_parsers.add_parser('fetch', help='fetch data item')
    fetch_data_parser.add_argument('--id', '-id', required=True, help="identifier of the vault or cluster containing the data item") # Help message?
    fetch_data_parser.add_argument('--name', '-n', required=True, help="data item name")
    fetch_data_parser.add_argument('--file', '-f', type=argparse.FileType('wb', 0), help="file to write the retrieved data into")
    fetch_data_parser.add_argument('--cryptkey', '-ck', type=argparse.FileType('rb'), help="path to cipher key file (filesize of 32 bytes required for AES256)")
    fetch_data_parser.add_argument('--info', '-i', action="store_true", default=False, help="retrieve data item information only")
    fetch_data_parser.add_argument('--initvector', '-iv', type=argparse.FileType('rb'), default=None, help="path to initialization vector file (filesize of 16 bytes required for AES256), IV defaults to a value of 0x31323334353637383930313233343536.")
    fetch_data_parser.set_defaults(func=fetch_data)

    param_group = parser.add_argument_group('parameters')
    param_group.add_argument('--verbose', '-v', action="store_true", default=False, help="enable progress printing")

    args = parser.parse_args()

    client = holvi.Client(username=args.user, auth_data=args.password, apikey=args.apikey, server_url=args.server)

    try:
        args.func(args, client)
    except HolviException as e:
        print >> sys.stderr, e
        sys.exit(-1)
    except urllib2.URLError as e:
        if hasattr(e, 'reason'):
            print >> sys.stderr, e.reason
        elif hasattr(e, 'code'):
            print >> sys.stderr, e.code, e.msg
        sys.exit(-1)

def add_vault(args, client):
    vault = client.add_vault(vault_type=args.type, name=args.name)
    if vault:
        print >> sys.stdout, "vault_id:vault_name:vault_type:descendants:dataitems"
        print >> sys.stdout, vault.to_text

def add_cluster(args, client):
    cluster = client.add_cluster(name=args.name, parent_id=args.id)
    if cluster:
        print >> sys.stdout, "cluster_id:cluster_name:parent_id:descendants:dataitems"
        print >> sys.stdout, cluster.to_text

def remove_vault(args, client):
    client.remove_vault(vault_id = args.id)

def remove_cluster(args, client):
    if not args.name:
        client.remove_cluster(cluster_id=args.id)
    else:
        clusters = client.list_clusters(parent_id=args.id)
        for cluster in clusters:
            if cluster.name == args.name:
                cluster.remove()
                break

def remove_dataitem(args, client):
    client.remove_dataitem(parent_id=args.id, key=args.name)

def list_vaults(args, client):
    vaults = client.list_vaults(vault_type=args.type, id_=args.id, role=args.role)
    print >> sys.stdout, "vault_id:vault_name:vault_type:descendants:dataitems"
    for vault in vaults:
        print >> sys.stdout, vault.to_text

def list_clusters(args, client):
    clusters = client.list_clusters(parent_id=args.id)
    print >> sys.stdout, "cluster_id:cluster_name:parent_id:descendants:dataitems"
    for cluster in clusters:
        print >> sys.stdout, cluster.to_text

def list_dataitems(args, client):
    dataitems = client.list_dataitems(parent_id=args.id)
    for dataitem in dataitems:
        print dataitem.name

def store_data(args, client):
    if not args.no_encryption:
        cryptkey = bytearray(args.cryptkey.read())
        if args.initvector:
            iv = args.initvector.read()
        else:
            iv = holvi.utils.IV_DEFAULT
        enc_mode = holvi.utils.ENC_AES256
    else:
        cryptkey = None
        iv = holvi.utils.IV_DEFAULT
        enc_mode = holvi.utils.ENC_NONE

    client.set_encryption_key(cryptkey)
    client.set_iv(iv)
    client.encryption_mode = enc_mode

    data = None
    if args.file:
        data = args.file
    else:
        data = sys.stdin
    if args.verbose:
        print >> sys.stdout, "Sending data"
    response = client.store_data(parent_id=args.id, key=args.name, method=args.method, p_data=data, offset=args.offset)
    if args.verbose:
        print >> sys.stdout, response
    data.close()

def fetch_data(args, client):
    if args.cryptkey:
        cryptkey = bytearray(args.cryptkey.read())
        enc_mode = holvi.utils.ENC_AES256
    else:
        cryptkey = None
        enc_mode = holvi.utils.ENC_NONE

    if args.initvector:
        iv = args.initvector.read()
    else:
        iv = holvi.utils.IV_DEFAULT

    client.set_encryption_key(cryptkey)
    client.set_iv(iv)
    client.encryption_mode = enc_mode

    data = None
    response = None
    if args.verbose:
        print >> sys.stdout, "Fetching data"
    if not args.info:
        try:
            response = client.fetch_data(parent_id=args.id, key=args.name)
        except:
            args.file.close()
    else:
        dataitem = client.get_dataitem(parent_id=args.id, key=args.name)
        print >> sys.stdout, "Name", dataitem.name
        print >> sys.stdout, "Content length", dataitem.length
        print >> sys.stdout, "Hash", dataitem.checksum
        print >> sys.stdout, "Meta", dataitem.meta
        print >> sys.stdout, "Last modified", dataitem.last_modified

    if response:
        if args.file:
            output_file = args.file
            for data in response['data']:
                output_file.write(data)
            output_file.close()
        else:
            for data in response['data']:
                sys.stdout.write(data)
        if args.verbose:
            if response['checksum'] == response['data']._md5.hexdigest():
                print >> sys.stdout, "OK"
            else:
                print >> sys.stdout, "Checksums mismatched"

if __name__ == '__main__': main()

