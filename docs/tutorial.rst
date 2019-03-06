Tutorial
========

This tutorial will illustrate the usage of the `nanolib` library
by describing the steps required to open an account in the NANO network,
starting from generating an account to receiving some NANO, and then sending
it on. Naturally, you will need a small amount of NANO; you may be able to get
some for free from a NANO faucet.

Creating an account
-------------------

Most NANO wallets use a `seed`, a 256-bit value that can be used to derive a linear sequence
of multiple NANO accounts. Since the end-user only needs to store the seed in
order to recover the accounts and any currency they may contain, seeds are
used by most NANO wallets. The main reference wallet, as well as the
third-party NanoVault use a 64-character hexadecimal string as a representation
of the seed value. This library uses the same representation as well.

Start by importing the library and generating a seed using the
:func:`nanolib.blocks.generate_seed` function::

   >>> from nanolib import generate_seed
   >>> seed = generate_seed()
   >>> seed
   'd290d319ce3c2cbb675b023e5383a767415d7444975a2ea121848fc986954568'

You should now have your own seed string that's formatted like the one above.
Now, let's generate the first NANO account for this seed.

   >>> from nanolib import generate_account_id
   >>> account_id = generate_account_id(seed, 0)
   'xrb_1bum9d7gkjcca8n8acbbwiauarffa4i9qgoeey59t4t8cpffimupua6wr99u'

Now save the seed string somewhere; we're about to send a tiny amount of NANO
to this account and then send it back.

Receiving NANO
--------------

We now have a seed string and an account ID, and are almost ready to receive
some NANO into the newly created account. You can send NANO into the newly
created account using a wallet of your choice or a faucet. After NANO
has been sent to the account, take note of the block ID for the transaction
we sent: this is the unpocketed transaction we will need to refer to in
the new block we're going to create.
After that, we should have all the information we need to create a block
to receive the NANO we've sent ourselves.

.. note::

   We are assuming that Universal Blocks are used for both transactions:
   the unpocketed transaction and the transaction that receives ("pockets")
   the sent NANO. Check the transaction on `Nanode <https://www.nanode.co>`_
   and ensure it has the type **state**.

   In this example, we assume the sending block to have the ID
   `A688CF225F2F16B89E49D3153899E9B36C218672379E61A66D6495CB275392BE` and
   that the account `xrb_1bum9d7gkjcca8n8acbbwiauarffa4i9qgoeey59t4t8cpffimupua6wr99u`
   has been sent exactly 1,000,000,000,000,000,000,000,000,000,000 raw (or 1 Mnano).

..

   >>> from nanolib import Block
   >>> block = Block(
   >>>     block_type="state",
   >>>     account="xrb_1bum9d7gkjcca8n8acbbwiauarffa4i9qgoeey59t4t8cpffimupua6wr99u",
   >>>     representative="xrb_1bum9d7gkjcca8n8acbbwiauarffa4i9qgoeey59t4t8cpffimupua6wr99u",
   >>>     previous=None,
   >>>     balance=1000000000000000000000000000000,
   >>>     link="A688CF225F2F16B89E49D3153899E9B36C218672379E61A66D6495CB275392BE")

To broadcast the block in NANO and to pocket the NANO we sent ourselves,
we need to solve a proof-of-work and sign the block.
You can check for both using the attributes
:attr:`nanolib.blocks.Block.has_valid_work` and :attr:`nanolib.blocks.Block.has_valid_signature`
accordingly. Both need to be added into the block before the block is complete
and it can be broadcasted: you can check for this using the block attribute
:attr:`nanolib.blocks.Block.complete`.

We'll start by solving the proof-of-work, which is easy enough:
just call :meth:`nanolib.blocks.Block.solve_work` and wait for a few
seconds. The time to solve the proof-of-work will vary depending on your luck
and the performance of your machine.

   >>> # Does the block have valid PoW?
   >>> block.has_valid_work
   False
   >>> block.solve_work()
   True
   >>> # How about now?
   >>> block.has_valid_work
   True

The next step is signing the block. For that, we can use
:func:`nanolib.accounts.generate_account_private_key` to derive the private
key for the account we created earlier.

   >>> from nanolib import generate_account_private_key
   >>> private_key = generate_account_private_key('d290d319ce3c2cbb675b023e5383a767415d7444975a2ea121848fc986954568', 0)
   >>> block.sign(private_key)
   True
   >>> # Does the block have a valid signature?
   >>> block.has_valid_signature
   True

Our block is now complete and all we need to do now is broadcast it!
For this, you'll need a NANO endpoint that allows you to process JSON-formatted
blocks. The reference *NANO Node and Developer Wallet* `nano_wallet` will
work fine for this.
To broadcast the block, you can dump the block in JSON format using
:meth:`nanolib.blocks.Block.json`.

.. code-block:: python

   >>> # Is the block ready to be broadcast?
   >>> block.complete
   True
   >>> block.json()
   '{"account": "xrb_1bum9d7gkjcca8n8acbbwiauarffa4i9qgoeey59t4t8cpffimupua6wr99u", "previous": "0000000000000000000000000000000000000000000000000000000000000000", "representative": "xrb_1bum9d7gkjcca8n8acbbwiauarffa4i9qgoeey59t4t8cpffimupua6wr99u", "balance": "1000000000000000000000000000000", "link": "A688CF225F2F16B89E49D3153899E9B36C218672379E61A66D6495CB275392BE", "link_as_account": "xrb_3bnaswj7ydrpq4h6mnro94eymeue68596fwye8m8ts6osemo96oy7thigkmb", "signature": "52E44CF0CF0E093064BAAC53EAF152AB373AC5A6665D028D665ABEF17BFE32E3D03985E3DCFAB648A3156AC662CCB4D0AF47B824D3B5A3CF3BD83871901DC100", "work": "abc94d816bf7b2aa", "type": "state"}'

That big chunk of JSON string is the JSON representation of the block.
Copy it (without the surrounding single quotes) and broadcast it using your
preferred NANO client. If you are using the reference NANO node,
the function to broadcast the block is located in *Advanced* -> *Enter Block*.
After you have entered the block, check a NANO block explorer such as
`Nanode <https://www.nanode.co>`_. If everything has gone as planned,
the block explorer should display the transaction and the balance
for your newly created account.

.. note::

   If you have a local NANO node with RPC enabled, you can
   broadcast the block using the Python library `requests`.

   .. code-block:: python

      >>> import requests
      >>> r = requests.post("http://127.0.0.1:7076", json={"action": "process", "block": block.json()})
      >>> r.json()


Sending NANO
------------

Now, to complete our tutorial, let's actually send that amount somewhere.
Let's create another block that sends our NANO somewhere else; we'll call
it `block_b`.

Decide a NANO account to send some NANO to and the amount,
and then create the next block. Note that we'll have to refer to the earlier
block we made by setting the attribute :attr:`nanolib.blocks.Block.previous`
to the previous block.

.. note::

   In this example, we assume the recipient is
   `xrb_3rridbdhm8jkjyzaig6xqkfcg7oob47rk9zm5moeiququmg3t8toq66nyrs7`
   and that we're sending 500,000,000,000,000,000,000,000,000,000 raw (or 0.5 Mnano)
   to the recipient.

..

.. code-block:: python

   >>> block_b = Block(
   >>>     block_type="state",
   >>>     account=block.account,
   >>>     representative=block.representative,
   >>>     previous=block.block_hash,
   >>>     link_as_account="xrb_3rridbdhm8jkjyzaig6xqkfcg7oob47rk9zm5moeiququmg3t8toq66nyrs7",
   >>>     balance=block.balance - 500000000000000000000000000000)
   >>> block_b.solve_work()
   True
   >>> block_b.sign(private_key)
   True
   >>> block_b.json()
   '{"account": "xrb_1bum9d7gkjcca8n8acbbwiauarffa4i9qgoeey59t4t8cpffimupua6wr99u", "previous": "A7DD7571505F1EB87318AD4EECAD1E0E616C66FE9C19E694BE103F84B498553B", "representative": "xrb_1bum9d7gkjcca8n8acbbwiauarffa4i9qgoeey59t4t8cpffimupua6wr99u", "balance": "500000000000000000000000000000", "link": "E3105A56F99A328FBE88389DBC9AA716B5488B891FF31CEAC85F77DCDC1D1B55", "link_as_account": "xrb_3rridbdhm8jkjyzaig6xqkfcg7oob47rk9zm5moeiququmg3t8toq66nyrs7", "signature": "AD803874CA5031641E7336E053FB798D02D0ED2447F17F7BDD17F5008251303805CFAF947450C922EAB08984E2B1001C1AEE77B73D5FEF84D1440F8023329C00", "work": "f9f29aee55996bf1", "type": "state"}'

After that, just do the same as you did before to broadcast the block and
you're done.

Wrapping it up
--------------

To wrap up this tutorial, here's the entire process from start to finish
in a single commented Python script.

This tutorial only scraped the surface of what `nanolib` is capable
of. You can continue by reading the API documentation if you're interested
in what else the library can do.

.. code-block:: python

   from nanolib import Block, generate_account_id, generate_account_private_key

   import requests

   # Derive a NANO account from our seed
   seed = "d290d319ce3c2cbb675b023e5383a767415d7444975a2ea121848fc986954568"
   account_id = generate_account_id(seed, 0)  # xrb_1bum9d7gkjcca8n8acbbwiauarffa4i9qgoeey59t4t8cpffimupua6wr99u

   # Let's assume someone has sent NANO to this account:
   # the block for the transaction has the following properties
   # block hash = 4OODW8BOGLC8N2E4K52X8OFL8LDEWS946CP8BCJHVY2NNJ8SCRLPPBNBHZKGJIRC
   # sent amount = 1000000000000000000000000 raw
   # type = state
   #
   # To receive the NANO, let's create the following block:
   block = Block(
       # Use the new universal blocks instead of legacy blocks
       # All universal blocks have the block type 'state' regardless of whether we're
       # sending, receiving or changing the representative
       block_type="state",
       account=account_id,
       # This can be any valid NANO account, but for simplicity's sake, let's use the
       # same account. Normally, we'll want this representative to be
       # someone trustworthy.
       representative=account_id,
       # This is the very first block (genesis block) for this account's
       # blockchain, which is why 'previous' is None
       previous=None,
       # The account's initial balance will be 1000000000000000000000000 raw since this
       # is what we received. Your amount may differ; change this field
       # accordingly.
       balance=1000000000000000000000000,
       # This is the block in which someone sent us NANO
       link="A688CF225F2F16B89E49D3153899E9B36C218672379E61A66D6495CB275392BE")
   # Solve the work for this block
   block.solve_work()

   # Sign this block using the corresponding private key
   private_key = generate_account_private_key(seed, 0)
   block.sign(private_key)

   # Now, broadcast this block to receive the NANO!
   # This assumes we have a local NANO node running at port 7076 with RPC enabled,
   # and that you have the Python library 'requests' installed!
   r = requests.post(
       "http://127.0.0.1:7076",
       json={"action": "process", "block": block.json()}
   )
   print("Response {}".format(r.json()))

   # NANO RPC returns a JSON response with the block hash
   # The same hash can also be found in `block.block_hash`
   block_hash = r.json()["hash"]

   print("Received some NANO from block {}".format(block_hash))

   # Okay, we've received NANO; let's spend it!
   # We'll send half of the amount to the second account in our possession
   account_id_b = generate_account_id(seed, 1)  # xrb_3rridbdhm8jkjyzaig6xqkfcg7oob47rk9zm5moeiququmg3t8toq66nyrs7

   block_b = Block(
       block_type="state",
       account=account_id,
       representative=account_id,
       # This is the second block in our account-specific blockchain,
       # so we need to refer to the previous block
       previous=block.block_hash,
       # We're sending 500000000000000000000000 raw to our other account,
       # leaving us with 500000000000000000000000 raw in this account
       balance=block.balance - 500000000000000000000000,
       # In this case, 'link_as_account' corresponds to the recipient
       link_as_account=account_id_b)

   # Do the same process again: solve the PoW, sign it and send it...
   block_b.solve_work()
   block_b.sign(private_key)

   r = requests.post(
       "http://127.0.0.1:7076",
       json={"action": "process", "block": block_b.json()}
   )
   print("Response {}".format(r.json()))

   block_hash_b = r.json()["hash"]

   print("Sent some NANO in block {}".format(block_hash_b))
