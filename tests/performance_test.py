import timeit
import cpuinfo

from hashlib import blake2b

from nanocurrency.work import _work


def run_speed_tests():
    def pow_solve_speed_test():
        ITERATIONS = 20

        # Get supported CPU instruction sets
        cpu_flags = cpuinfo.get_cpu_info()["flags"]

        all_flags = ["avx", "sse4_1", "ssse3", "sse2"]
        supported_flags = [
            flag for flag in all_flags
            if flag in cpu_flags
        ] + ["ref"]

        for flag in supported_flags:
            elapsed = timeit.Timer(
                ("nonce = 0\n"
                 "while nonce < 1000000:\n"
                 "    nonce = _work.do_work(block_hash, nonce, (2**64)-1)"),
                ("from nanocurrency import _work_{} as _work\n"
                 "from hashlib import blake2b\n"
                 "block_hash = blake2b(\n"
                 "    b'fakeBlock', digest_size=32).digest()\n".format(flag))
            ).timeit(ITERATIONS)

            # How many hashes per second?
            rate = int((1000000 * ITERATIONS) / elapsed)

            print(
                "BLAKE2b PoW ({flag}){used} speed: {rate} hashes/s".format(
                flag=flag,
                used=" DEFAULT" if supported_flags.index(flag) == 0 else "",
                rate=rate))

    def account_gen_speed_test():
        ITERATIONS = 10

        elapsed = timeit.Timer(
            ("i = 0\n"
             "while i < 1000:\n"
             "    a = generate_account_id(seed, i)\n"
             "    b = generate_account_key_pair(seed, i)\n"
             "    i += 1"),
            ("from nanocurrency.accounts import generate_seed, generate_account_id, generate_account_key_pair\n"
             "seed = generate_seed()")
        ).timeit(ITERATIONS)

        # How many account IDs per second?
        rate = int((1000 * ITERATIONS) / elapsed)

        print("Account generation rate: {} accounts/s".format(rate))

    def block_sign_speed_test():
        ITERATIONS = 2000

        elapsed = timeit.Timer(
            ("block.signature = None\n"
             "block.sign(key_pair.private)"),
            ("from nanocurrency.blocks import Block\n"
             "from nanocurrency.accounts import generate_seed, generate_account_id, generate_account_key_pair\n"
             "seed = generate_seed()\n"
             "account_id = generate_account_id(seed, 0)\n"
             "key_pair = generate_account_key_pair(seed, 0)\n"
             "block = Block(\n"
             "    block_type='open', account=account_id,\n"
             "    source='B2EC73C1F503F47E051AD72ECB512C63BA8E1A0ACC2CEE4EA9A22FE1CBDB693F',\n"
             "    representative='xrb_1anrzcuwe64rwxzcco8dkhpyxpi8kd7zsjc1oeimpc3ppca4mrjtwnqposrs')")
        ).timeit(ITERATIONS)

        rate = int(ITERATIONS / elapsed)

        print("Block sign rate: {} blocks/s".format(rate))

    def block_verify_speed_test():
        ITERATIONS = 2000

        elapsed = timeit.Timer(
            ("block.verify_signature()"),
            ("from nanocurrency.blocks import Block\n"
             "from nanocurrency.accounts import generate_seed, generate_account_id, generate_account_key_pair\n"
             "seed = generate_seed()\n"
             "account_id = generate_account_id(seed, 0)\n"
             "key_pair = generate_account_key_pair(seed, 0)\n"
             "block = Block(\n"
             "    block_type='open', account=account_id,\n"
             "    source='B2EC73C1F503F47E051AD72ECB512C63BA8E1A0ACC2CEE4EA9A22FE1CBDB693F',\n"
             "    representative='xrb_1anrzcuwe64rwxzcco8dkhpyxpi8kd7zsjc1oeimpc3ppca4mrjtwnqposrs')\n"
             "block.sign(key_pair.private)")
        ).timeit(ITERATIONS)

        rate = int(ITERATIONS / elapsed)

        print("Block verify rate: {} blocks/s".format(rate))

    pow_solve_speed_test()
    account_gen_speed_test()
    block_sign_speed_test()
    block_verify_speed_test()
