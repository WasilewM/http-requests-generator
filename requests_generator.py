import requests
import concurrent.futures
import json
import sys
from random import randrange
from scipy.stats import poisson


URL = "http://localhost:8080/factorization_results"
SECONDS_NUM = 10


def generate_requests_by_poisson_dist(events_num, timespan):
    lambda_ = events_num / timespan
    poisson_dist = poisson(lambda_)
    return poisson_dist.rvs(size=timespan)


def generate_requests_urls(requests_number):
    random_nums = [
        randrange(10, 10*2)
        for _ in range(requests_number)
    ]
    return [
        f'{URL}/{number}'
        for number in random_nums
    ]


def send_request(url):
    r = requests.get(url=url, params=dict())
    r_json = json.loads(r.content)
    print(r_json)


def run(requests_per_sec):
    for rps in requests_per_sec:
        urls_with_args = generate_requests_urls(rps)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(send_request, url)
                for url in urls_with_args
            ]
            concurrent.futures.wait(futures)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 svc_requests.py <number>")
    else:
        try:
            print(f"Type of sys.argv[1]: {type(sys.argv[1])}")
            print(f"Value of sys.argv[1]: {sys.argv[1]}")
            number = int(sys.argv[1], 10)
            requests_per_sec = generate_requests_by_poisson_dist(
                number, SECONDS_NUM
            )
            print(requests_per_sec)
            run(requests_per_sec)
        except ValueError:
            print("Invalid input. Please enter a valid number.")
