# reverse-proxy
a simple reverse proxy on asyncio
# Use:
```
optional arguments:
  -h, --help            show this help message and exit
  -a HOSTNAME, --hostname HOSTNAME
                        TCP/IP hostname to serve on (default: '127.0.0.1')
  -p PORT, --port PORT  TCP/IP port to serve on (default: '8080')
  -r REMOTE, --remote REMOTE
                        Reverse proxy address

$ python reverse_proxy.py -r https://httpbin.org

Serving on ('127.0.0.1', 8080) -> http://httpbin.org
```
