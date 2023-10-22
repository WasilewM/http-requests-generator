import requests
import concurrent.futures
import json
import sys
from random import randrange
from scipy.stats import poisson
import numpy as np
import argparse


class RequestsGenerator:
    def __init__(self, url: str, requests_number: int, timespan: int,
                 lower_limit: int = 0, upper_limit: int = 10**6) -> None:
        self._url = url
        self._requests_number = requests_number
        self._timespan = timespan
        self._lower_limit = lower_limit
        self._upper_limit = upper_limit

    def generate_requests_poisson_dist(self) -> np.ndarray:
        lambda_ = self._requests_number / self._timespan
        poisson_dist = poisson(lambda_)
        return poisson_dist.rvs(size=self._timespan)

    def generate_random_requests_urls(self, requests_number: int) -> list:
        random_nums = [
            randrange(self._lower_limit, self._upper_limit)
            for _ in range(requests_number)
        ]
        return [
            f'{self._url}/{number}'
            for number in random_nums
        ]

    def send_request(self, url: str) -> None:
        r = requests.get(url=url, params=dict())
        r_json = json.loads(r.content)
        print(r_json)

    def run(self):
        requests_per_sec = self.generate_requests_poisson_dist()
        for rps in requests_per_sec:
            urls_with_args = self.generate_random_requests_urls(rps)

            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(self.send_request, url)
                    for url in urls_with_args
                ]
                concurrent.futures.wait(futures)


def run(argv):
    parser = argparse.ArgumentParser(
        prog="http-requests-generator",
        description='''Generates http requests for given URL
         with random numbers appended at the end of the URL'''
    )
    parser.add_argument("url", type=str, help='''URL to your service.
                        Remember that random integers will be added at the end
                        of the URL request'''
                        )
    parser.add_argument("requests_num", type=int,
                        help='''Average number of requests you want to send
                        over the timespan''')
    parser.add_argument("timespan", type=int,
                        help='''Timespan during which the requests have
                        to be sent''')
    parser.add_argument("-l", "--lower_limit", type=int,
                        help='''Lower limit of integer values that will be
                        randomly added to the URL''')
    parser.add_argument("-u", "--upper_limit", type=int,
                        help='''Lower limit of integer values that will be
                        randomly added to the URL''')
    args = parser.parse_args()
    requests_generator = RequestsGenerator(
        args.url, args.requests_num, args.timespan
    )
    requests_generator.run()


if __name__ == '__main__':
    run(sys.argv)
