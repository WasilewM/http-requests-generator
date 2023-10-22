import requests
import concurrent.futures
import json
import sys
from random import randrange
from scipy.stats import poisson
import numpy as np


class RequestsGenerator:
    def __init__(self, url: str, requests_number: int, timespan: int) -> None:
        self._url = url
        self._requests_number = requests_number
        self._timespan = timespan

    def generate_requests_poisson_dist(self) -> np.ndarray:
        lambda_ = self._requests_number / self._timespan
        poisson_dist = poisson(lambda_)
        return poisson_dist.rvs(size=self._timespan)

    def generate_random_requests_urls(self, requests_number: int) -> list:
        random_nums = [
            randrange(10, 10*2)
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


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 requests_generator.py <number>")
    else:
        try:
            print(f"Type of sys.argv[1]: {type(sys.argv[1])}")
            print(f"Value of sys.argv[1]: {sys.argv[1]}")
            request_url = sys.argv[1]
            print(f"Type of sys.argv[2]: {type(sys.argv[2])}")
            print(f"Value of sys.argv[2]: {sys.argv[2]}")
            requests_number = int(sys.argv[2], 10)
            print(f"Type of sys.argv[3]: {type(sys.argv[3])}")
            print(f"Value of sys.argv[3]: {sys.argv[3]}")
            timespan = int(sys.argv[3], 10)
            requests_generator = RequestsGenerator(
                request_url, requests_number, timespan
            )
            requests_generator.run()
        except ValueError:
            print("Invalid input. Please enter a valid number.")
