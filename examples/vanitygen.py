"""
A script to generate vanity NANO addresses.

Example commands:
# Print the help
$ python vanitygen.py --help

# Search for an account ID containing the phrase 'nano' using 8 threads
$ python vanitygen.py -t 8 nano

# Search for an account ID with the prefix 'nano' using 8 threads
# (this will take a long time)
$ python vanitygen.py -t 8 --only-prefix nano

NOTE: This implementation is a lot slower than a native implementation, and
      is provided as an example of how to use the 'nanolib' Python
      library
"""

import multiprocessing
import random
import argparse
import sys
import time

from nanolib import get_account_id


ALLOWED_CHARS = "13456789abcdefghijkmnopqrstuwxyz"
ITERATIONS_PER_RUN = 1000


def convert_phrase(phrase):
    phrase = phrase.replace("v", "w").replace("2", "").replace("l", "1")

    for char in phrase:
        if char not in ALLOWED_CHARS:
            print("Forbidden character {} found in phrase".format(char))
            sys.exit(1)

    return phrase


def search_for_id(phrase, only_prefix):
    i = random.SystemRandom().randint(0, (2**256)-1)
    phrase_length = len(phrase)

    iterations = 0

    start_time = time.time()

    while iterations < ITERATIONS_PER_RUN and i < 2**256:
        private_key = "{0:0{1}x}".format(i, 64)
        account_id = get_account_id(private_key=private_key)

        match = False

        if only_prefix:
            # Account has to start with the phrase
            match = account_id[5:5+phrase_length] == phrase
        else:
            # Any place is OK
            match = phrase in account_id

        if match:
            # Found it!
            return {
                "found": True,
                "private_key": private_key,
                "account_id": account_id
            }

        iterations += 1
        i += 1

    end_time = time.time()

    return {
        "found": False,
        "rate": iterations / (end_time - start_time)
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Find a NANO account ID containing the given phrase")

    parser.add_argument(
        "-t", type=int, default=1,
        help="Amount of threads used for searching")

    parser.add_argument(
        "--only-prefix", action="store_true",
        help=(
            "Only allow account IDs that start with the given phrase. "
            "Will increase search time dramatically."
        )
    )
    parser.add_argument("phrase", type=str, help="Phrase to search for")

    args = parser.parse_args()

    threads = args.t
    phrase = args.phrase
    only_prefix = args.only_prefix

    if len(phrase) > 57:
        print("Phrase can be 57 characters long at most")
        sys.exit(1)

    phrase = phrase.lower()
    phrase = convert_phrase(phrase)

    pool = multiprocessing.Pool(args.t)

    # Create multiple processes for parallel searching
    runs = []

    for _ in range(0, threads):
        runs.append(pool.apply_async(search_for_id, (phrase, only_prefix)))

    if only_prefix:
        print(
            "Beginning search for account ID containing the prefix '{}'".format(
                phrase
            )
        )
    else:
        print("Beginning search for account ID containing "
              "phrase '{}'".format(phrase))
        print("If you want an account ID starting with phrase, "
              "use --only-prefix")

    print("Press Ctrl+C to stop")

    result_rates = []

    last_report_time = time.time()

    while True:
        for run in runs:
            if run.ready():
                result = run.get()

                if result["found"]:
                    print(
                        "FOUND A MATCH.\n"
                        "Account ID: {}\n"
                        "Private key: {}".format(
                            result["account_id"],
                            result["private_key"]
                        )
                    )
                    sys.exit(0)
                else:
                    result_rates.append(result["rate"])

                    if len(result_rates) > threads:
                        result_rates = result_rates[-threads:]

                    runs.append(
                        pool.apply_async(search_for_id, (phrase, only_prefix))
                    )

        # Only show rate every five seconds
        show_rate = (time.time() - last_report_time) > 5

        if len(result_rates) == threads and show_rate:
            last_report_time = time.time()
            print("Current search rate: {} IDs/s".format(int(sum(result_rates))))

        time.sleep(0.05)
