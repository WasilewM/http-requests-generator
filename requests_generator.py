import requests
import asyncio
import json
import sys
import numpy as np
import argparse
from random import randrange
from scipy.stats import poisson
from time import perf_counter

GENERATE_FLAGS = ["generate", "g"]
GENERATE_AND_SAVE_FLAGS = ["generate-and-save", "gs"]
GENERATE_AND_RUN_FLAGS = ["generate-and-run", "gr"]
LOAD_AND_RUN_FLAGS = ["load-and-run", "lr"]


class RequestsGenerator:
    def __init__(
        self,
        url: str,
        requests_number: int,
        timespan: int,
        lower_limit: int = 0,
        upper_limit: int = 10**6,
    ) -> None:
        self._url = url
        self._requests_number = requests_number
        self._timespan = timespan
        self._lower_limit = lower_limit
        self._upper_limit = upper_limit

    def set_lower_limit(self, new_limit: int) -> None:
        self._lower_limit = new_limit

    def set_upper_limit(self, new_limit: int) -> None:
        self._upper_limit = new_limit

    def generate_requests_poisson_dist(self) -> np.ndarray:
        lambda_ = self._requests_number / self._timespan
        poisson_dist = poisson(lambda_)
        return poisson_dist.rvs(size=self._timespan)

    def generate_random_requests_urls(self, requests_number: int) -> list:
        random_nums = [randrange(self._lower_limit, self._upper_limit) for _ in range(requests_number)]
        return [f"{self._url}/{number}" for number in random_nums]

    @staticmethod
    async def send_request(url: str) -> None:
        r = requests.get(url=url, params=dict())
        r_json = json.loads(r.content)
        print(r_json)

    async def run(self):
        requests_per_sec = self.generate_requests_poisson_dist()
        for rps in requests_per_sec:
            urls_with_args = self.generate_random_requests_urls(rps)
            before = perf_counter()
            await asyncio.gather(*(self.send_request(url) for url in urls_with_args))
            after = perf_counter()
            print("time taken: ", after - before)
            print("-" * 20)


def select_mode(args):
    if args.mode in GENERATE_AND_RUN_FLAGS:
        requests_generator = RequestsGenerator(args.url, args.requests_num, args.timespan)

        if args.lower_limit is not None:
            requests_generator.set_lower_limit(args.lower_limit)
        if args.upper_limit is not None:
            requests_generator.set_upper_limit(args.upper_limit)

        asyncio.run(requests_generator.run())
    else:
        print("Implement me!")
        exit(1)


def run(argv):
    parser = argparse.ArgumentParser(
        prog="http-requests-generator",
        description="""Generates http requests for given URL
         with random numbers appended at the end of the URL""",
    )
    parser.add_argument(
        "url",
        type=str,
        help="""URL to your service.
                        Remember that random integers will be added at the end
                        of the URL request""",
    )
    parser.add_argument(
        "requests_num",
        type=int,
        help="""Average number of requests you want to send
                        over the timespan""",
    )
    parser.add_argument(
        "timespan",
        type=int,
        help="""Timespan during which the requests have
                        to be sent""",
    )
    parser.add_argument(
        "-l",
        "--lower_limit",
        type=int,
        help="""Lower limit of integer values that will be
                        randomly added to the URL""",
    )
    parser.add_argument(
        "-u",
        "--upper_limit",
        type=int,
        help="""Lower limit of integer values that will be
                        randomly added to the URL""",
    )
    parser.add_argument(
        "-m",
        "--mode",
        type=str,
        help="""Mode which should be executed""",
        choices=[*GENERATE_FLAGS, *GENERATE_AND_SAVE_FLAGS, *GENERATE_AND_RUN_FLAGS, *LOAD_AND_RUN_FLAGS],
        default="generate-and-run",
    )
    args = parser.parse_args()
    select_mode(args)


if __name__ == "__main__":
    run(sys.argv)
