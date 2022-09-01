import re
import random
import threading

import requests

class SmartProxy:
    # Default variables
    SCHEME = 'https'
    TEST_LINK = 'https://httpbin.org/status/200'
    TIMEOUT = 3
    TEST_STATUS_CODE = 200

    # Accepted schemes: http/https
    # Testing link: any, default is https://httpbin.org/status/20
    # Default timeout is 3, you can change it for your needs
    # Default testing status code is 200, you can change it for your needs
    def __init__(self, scheme: str = False, testing_link: str = False, timeout: int = False,
                 testing_status_code: int = False):
        self.proxy_dict = {}
        if scheme:
            self.SCHEME = scheme
        if testing_link:
            self.TEST_LINK = testing_link
        if timeout:
            self.TIMEOUT = timeout
        if testing_status_code:
            self.TEST_STATUS_CODE = testing_status_code
        self.last_requested_proxy = None

    # Getting proxy from path. Calls proxy checking method
    # Format: ip:port:user:pass
    # TODO: Will be updated with more formats of proxy
    def get_proxy_from_path(self, path: str) -> None:
        try:
            file = open(path, 'r')
            lines = file.readlines()
            if len(lines) == 0:
                raise Exception("Empty File")
            counter = 0
            for line in lines:
                try:
                    proxy = re.search(r'^(\d+\.\d+\.\d+\.\d+)\:(\d+)\:([^\:]*)\:([^\$]*)$', line.strip())
                    self.proxy_dict[counter] = {}
                    self.proxy_dict[counter][self.SCHEME] = f"{self.SCHEME}://{proxy.group(3)}:{proxy.group(4)}@{proxy.group(1)}:{proxy.group(2)}"
                except:
                    print(f'Line {line.strip()} was not recognized and skipped'
                          f'Please use ip:port:user:pass format.')
                counter += 1
            file.close()
            self.__check_proxy()
        except FileNotFoundError:
            print(F"Proxy file with path {path} was not found.")
            raise FileNotFoundError

    # Main method, that use should use for getting proxy for requests [works with requests]
    def get_request_proxy(self):
        if len(self.proxy_dict) == 0:
            raise Exception("Empty proxy list, please use .get_proxy_from_path method")
        proxies_count = len(self.proxy_dict)
        tickets = [i for i in range(proxies_count) for j in range(i + 1)]
        proxy_number = random.choice(tickets)
        self.proxy_dict[proxy_number], self.proxy_dict[0] = self.proxy_dict[0], self.proxy_dict[proxy_number]
        if len(self.proxy_dict) != 1 and self.last_requested_proxy == self.proxy_dict[0]:
            return self.get_request_proxy()
        self.last_requested_proxy = self.proxy_dict[0]
        return self.proxy_dict[0]

    # AutoMethod to check proxies
    # Testing link, timeout can be set in class constructor
    def __check_proxy(self):# my_thread = []
        # for proxi in list(proxy):
        #     my_thread.append(threading.Thread(target=check_proxy, args=(proxi,)))
        # for thread in my_thread:
        #     thread.start()
        # for thread in my_thread:
        #     thread.join()
        # print("Finished, Proxies Left:", len(proxy))
        # proxy_use = True
        # if len(proxy) == 0:
        #     proxy_use = False

        shadow_copy = self.proxy_dict.copy()
        threads = []
        for key in shadow_copy.keys():
            try:
                threads.append(threading.Thread(target=self.__check_one_proxy, args=(key,)))
                for thread in threads:
                    thread.start()
                for thread in threads:
                    thread.join()
            except:
                del self.proxy_dict[key]

    def __check_one_proxy(self, key):
        try:
            status_code = requests.get(self.TEST_LINK, proxies=self.proxy_dict[key],
                                       timeout=self.TIMEOUT).status_code
            if status_code != self.TEST_STATUS_CODE:
                del self.proxy_dict[key]
        except:
            del self.proxy_dict[key]


        print(self.proxy_dict)

    # TODO: Manual updating proxy priority

# Personal Testing
if __name__ == "__main__":
    s = SmartProxy()
    s.get_proxy_from_path("proxy.txt")
    for i in range(10):
        s.get_request_proxy()