Smart Proxy 
---

Site can easily ban us if use the same proxy twice, etc.

Programmers, who parses a lot need a special class for good rotating for their proxies.

SmartProxy class, is very simple but useful solution.

It uses simple random ticket system, for better performance of proxy rotation.

Example:
---
```python
    # Init and load proxies
    s = SmartProxy()
    s.get_proxy_from_path("proxy.txt")
    
    # Use in your requests
    response = requests.get(url, proxies=s.get_request_proxy())
```