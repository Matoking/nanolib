from src.nanocurrency.util import rpc_request
from src.nanocurrency.blocks import Block

from .exceptions import InvalidBlock

class Node:
    """A Nano node.

    Receives a node uri for connecting remotely.
    """

    def __init__(self, uri):
        """Create Node from given parameters

        :param str uri: The node uri with IP and Port
        """

        self.uri = uri

    def account_balance(self, account):

        data = {"action"            : "account_balance",
                "account"           : account}

        return rpc_request(self.uri, data)

    def account_block_count(self, account):

        data = {"action"            : "account_block_count",
                "account"           : account}

        return rpc_request(self.uri, data)

    def account_info(self, account, representative="true", weight="true", pending="true"):

        data = {"action"            : "account_info",
                "account"           : account,
                "representative"    : representative,
                "weight"            : weight,
                "pending"           : pending}

        return rpc_request(self.uri, data)

    def account_create(self, wallet, index="1", work="false"):

        data = {"action"            : "account_balance",
                "wallet"            : wallet,
                "index"             : index,
                "work"              : work}

        return rpc_request(self.uri, data)

    def account_get(self, key):

        data = {"action"            : "account_get",
                "key"               : key}

        return rpc_request(self.uri, data)

    def account_history(self, account, count):

        data = {"action"            : "account_history",
                "account"           : account,
                "count"             : count}

        return rpc_request(self.uri, data)

    def account_list(self, wallet):

        data = {"action"            : "account_list",
                "wallet"            : wallet}

        return rpc_request(self.uri, data)

    def account_move(self, wallet, source, accounts):

        data = {"action"            : "account_move",
                "wallet"            : wallet,
                "source"            : source,
                "accounts"          : accounts}

        return rpc_request(self.uri, data)

    def account_key(self, account):

        data = {"action"            : "account_key",
                "account"           : account}

        return rpc_request(self.uri, data)

    def account_remove(self, wallet, account):

        data = {"action"            : "account_remove",
                "wallet"            : wallet,
                "account"           : account}

        return rpc_request(self.uri, data)

    def account_representative(self, account):

        data = {"action"            : "account_representative",
                "account"           : account}

        return rpc_request(self.uri, data)

    def account_representative_set(self, wallet, account, representative, work="false"):

        data = {"action"            : "account_representative_set",
                "wallet"            : wallet,
                "account"           : account,
                "representative"    : representative,
                "work"              : work}

        return rpc_request(self.uri, data)

    def account_weight(self, account):

        data = {"action"            : "account_weight",
                "account"           : account}

        return rpc_request(self.uri, data)

    def accounts_balances(self, accounts):

        data = {"action"            : "accounts_balances",
                "accounts"          : accounts}

        return rpc_request(self.uri, data)

    def accounts_create(self, wallet, count, work="false"):

        data = {"action"            : "accounts_create",
                "wallet"            : wallet,
                "count"             : count,
                "work"              : work}

        return rpc_request(self.uri, data)

    def accounts_frontiers(self, accounts):

        data = {"action"            : "accounts_frontiers",
                "accounts"          : accounts}

        return rpc_request(self.uri, data)

    def accounts_pending(self, accounts, count, threshold="0", source="false", include_active="false"):

        data = {"action"            : "accounts_pending",
                "accounts"          : accounts,
                "count"             : count,
                "threshold"         : threshold,
                "source"            : source,
                "include_active"    : include_active}

        return rpc_request(self.uri, data)

    @property
    def available_supply(self):

        data = {"action"            : "available_supply"}

        return rpc_request(self.uri, data)

    def block_info(self, hash, json_block="false"):

        data = {"action"            : "block_info",
                "hash"              : hash,
                "json_block"        : json_block}

        return rpc_request(self.uri, data)

    def blocks(self, hashes):

        data = {"action"            : "blocks",
                "hashes"            : hashes}

        return rpc_request(self.uri, data)

    def blocks_info(self, hashes, pending="false", source="false", balance="false", json_block="false"):

        data = {"action"            : "blocks_info",
                "hashes"            : hashes,
                "pending"           : pending,
                "source"            : source,
                "balance"           : balance,
                "json_block"        : json_block}

        return rpc_request(self.uri, data)

    def block_account(self, hash):

        data = {"action"            : "block_account",
                "hash"              : hash}

        return rpc_request(self.uri, data)

    def block_confirm(self, hash):

        data = {"action"            : "block_confirm",
                "hash"              : hash}

        return rpc_request(self.uri, data)

    @property
    def block_count(self):
        """
        A property that retrieves node block count

        source:
        https://github.com/nanocurrency/raiblocks/wiki/RPC-protocol#block-count

        :return: The rpc response
        :rtype: dict
        """

        data = {"action"            : "block_count"}

        return rpc_request(self.uri, data)

    @property
    def block_count_type(self):

        data = {"action"            : "block_count_type"}

        return rpc_request(self.uri, data)

    def block_hash(self, block, json_block="false"):

        data = {"action"            : "block_hash",
                "block"             : block,
                "json_block"        : json_block}

        return rpc_request(self.uri, data)

    def bootstrap(self, address, port):

        data = {"action"            : "bootstrap",
                "address"           : address,
                "port"              : port}

        return rpc_request(self.uri, data)

    def bootstrap_lazy(self, hash, force=False):

        data = {"action"            : "bootstrap_lazy",
                "hash"              : hash,
                "force"             : force}

        return rpc_request(self.uri, data)

    def bootstrap_any(self):

        data = {"action"            : "bootstrap_any"}

        return rpc_request(self.uri, data)

    def bootstrap_status(self):

        data = {"action"            : "bootstrap_status"}

        return rpc_request(self.uri, data)

    def chain(self, block, count, offset=0, reverse=False):

        data = {"action"            : "chain",
                "block"             : block,
                "count"             : count,
                "offset"            : offset,
                "reverse"           : reverse}

        return rpc_request(self.uri, data)

    def confirmation_active(self, announcements=0):

        data = {"action"            : "confirmation_active",
                "announcements"     : announcements}

        return rpc_request(self.uri, data)

    @property
    def confirmation_history(self):

        data = {"action"            : "confirmation_history"}

        return rpc_request(self.uri, data)

    def confirmation_info(self, root, contents=True, json_block="false", representatives=False):

        data = {"action"            : "confirmation_info",
                "root"              : root,
                "contents"          : contents,
                "json_block"        : json_block,
                "representatives"   : representatives}

        return rpc_request(self.uri, data)

    def confirmation_quorum(self, peer_details=False):

        data = {"action"            : "confirmation_quorum",
                "peer_details"      : peer_details}

        return rpc_request(self.uri, data)

    def delegators(self, account):

        data = {"action"            : "delegators",
                "account"           : account}

        return rpc_request(self.uri, data)

    def delegators_count(self, account):

        data = {"action"            : "delegators_count",
                "account"           : account}

        return rpc_request(self.uri, data)

    def deterministic_key(self, seed, index):

        data = {"action"            : "deterministic_key",
                "seed"              : seed,
                "index"             : index}

        return rpc_request(self.uri, data)

    @property
    def version(self):
        """
        A property that retrieves node version

        source:
        https://github.com/nanocurrency/raiblocks/wiki/RPC-protocol#retrieve-node-versions

        :return: The rpc response
        :rtype: dict
        """

        data = {"action"            : "version"}
        return rpc_request(self.uri, data)

    def process(self, block):
        """
        Broadcasts a block on network

        source:
        https://github.com/nanocurrency/raiblocks/wiki/RPC-protocol#process-block

        :param Block block: Block to be broadcasted
        :raises CantReachServer: if timeout or uri is invalid
        :return: The rpc response
        :rtype: dict
        """

        if not isinstance(block, Block):
            raise InvalidBlock("Parameter must be a Block object")

        json = block.json()

        data = {"action"            : "process",
                "block"             : json}

        return rpc_request(self.uri, data)