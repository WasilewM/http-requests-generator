import requests
import concurrent.futures
import json
import sys
from random import randrange
from scipy.stats import poisson


def generate_requests_poisson_dist(events_num, timespan):
    lambda_ = events_num / timespan
    poisson_dist = poisson(lambda_)
    return poisson_dist.rvs(size=timespan)


def generate_random_requests_urls(request_url, requests_number):
    random_nums = [
        randrange(10, 10*2)
        for _ in range(requests_number)
    ]
    return [
        f'{request_url}/{number}'
        for number in random_nums
    ]


def send_request(url):
    r = requests.get(url=url, params=dict())
    r_json = json.loads(r.content)
    print(r_json)


def run(request_url, requests_per_sec):
    for rps in requests_per_sec:
        urls_with_args = generate_random_requests_urls(request_url, rps)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(send_request, url)
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
            number = int(sys.argv[2], 10)
            print(f"Type of sys.argv[3]: {type(sys.argv[3])}")
            print(f"Value of sys.argv[3]: {sys.argv[3]}")
            timespan = int(sys.argv[3], 10)
            requests_per_sec = generate_requests_poisson_dist(
                number, timespan
            )
            run(request_url, requests_per_sec)
        except ValueError:
            print("Invalid input. Please enter a valid number.")
