import requests
import argparse
import concurrent.futures
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
import ssl

def highly_aggressive_load_test(url, num_requests, concurrency, disable_ssl, increase_risk, no_retry):
    # Create a session with retry strategy
    session = requests.Session()
    retries = Retry(total=0 if no_retry else 10, backoff_factor=0.1)
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    if disable_ssl:
        session.verify = False
        # Ignore SSL warnings
        requests.packages.urllib3.disable_warnings()
        ssl._create_default_https_context = ssl._create_unverified_context

    def make_request():
        try:
            response = session.get(url)
            print(f"Request completed with status code {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")

    # Double the number of requests if increase_risk is enabled
    total_requests = num_requests * (5 if increase_risk else 1)

    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(make_request) for _ in range(total_requests)]
        concurrent.futures.wait(futures)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Highly Aggressive Load Test Tool")
    parser.add_argument("url", help="Target URL")
    parser.add_argument("--num-requests", type=int, default=1000, help="Number of requests to send")
    parser.add_argument("--concurrency", type=int, default=50000, help="Number of concurrent workers")  # Increased by 100x
    parser.add_argument("--disable-ssl", action="store_true", help="Disable SSL verification")
    parser.add_argument("--increase-risk", action="store_true", help="Increase the number of requests")
    parser.add_argument("--no-retry", action="store_true", help="Disable retry mechanism")
    args = parser.parse_args()

    start_time = time.time()
    highly_aggressive_load_test(args.url, args.num_requests, args.concurrency, args.disable_ssl, args.increase_risk, args.no_retry)
    end_time = time.time()
    print(f"Load test completed in {end_time - start_time} seconds")