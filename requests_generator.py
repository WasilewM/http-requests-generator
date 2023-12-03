import requests
import asyncio
import json
import sys
import numpy as np
import argparse
import json
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
        self.requests = None
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

    def generate_random_requests_urls(self) -> list:
        requests_per_sec = self.generate_requests_poisson_dist()
        random_requests_urls = []
        for rps in requests_per_sec:
            random_nums = [randrange(self._lower_limit, self._upper_limit) for _ in range(rps)]
            urls = [f"{self._url}/{number}" for number in random_nums]
            yield urls
            random_requests_urls.append(urls)
        return random_requests_urls

    def prepare_requests(self) -> None:
        self.requests = self.generate_random_requests_urls()

    @staticmethod
    async def send_request(url: str) -> None:
        r = requests.get(url=url, params=dict())
        r_json = json.loads(r.content)
        print(r_json)

    async def run(self) -> None:
        for urls in self.requests:
            before = perf_counter()
            await asyncio.gather(*(self.send_request(u) for u in urls))
            after = perf_counter()
            print("time taken: ", after - before)
            print("-" * 20)


def set_limits(args, requests_generator) -> None:
    if args.lower_limit is not None:
        requests_generator.set_lower_limit(args.lower_limit)
    if args.upper_limit is not None:
        requests_generator.set_upper_limit(args.upper_limit)


def handle_generate_flag(requests_generator) -> None:
    urls = requests_generator.generate_random_requests_urls()
    for u in urls:
        print(u)


def handle_generate_and_save_flag(args, requests_generator) -> None:
    if args.output is None:
        print("Filepath is required in order to save the requests")
        exit(1)
    urls = [u for u in requests_generator.generate_random_requests_urls()]
    urls_json = json.dumps(urls, indent=4)
    with open(args.output, "w") as f:
        f.write(urls_json)


def handle_generate_and_run_flag(args, requests_generator) -> None:
    requests_generator.prepare_requests()
    asyncio.run(requests_generator.run())


def handle_load_and_run_flag(args, requests_generator) -> None:
    if args.input is None:
        print("Filepath is required in order to load the requests")
        exit(1)
    with open(args.input, "r") as f:
        data = f.read()
        json_data = json.loads(data)
        requests_generator.requests = json_data
        asyncio.run(requests_generator.run())


def select_mode(args) -> None:
    requests_generator = RequestsGenerator(args.url, args.requests_num, args.timespan)
    set_limits(args, requests_generator)
    if args.mode in GENERATE_FLAGS:
        handle_generate_flag(requests_generator)
    elif args.mode in GENERATE_AND_SAVE_FLAGS:
        handle_generate_and_save_flag(args, requests_generator)
    elif args.mode in GENERATE_AND_RUN_FLAGS:
        handle_generate_and_run_flag(args, requests_generator)
    elif args.mode in LOAD_AND_RUN_FLAGS:
        handle_load_and_run_flag(args, requests_generator)
    else:
        print("Mode is not implemented")
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
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="""Path to file where requests will be saved""",
    )
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        help="""Path to file where requests are stored""",
    )
    args = parser.parse_args()
    select_mode(args)


if __name__ == "__main__":
    run(sys.argv)
