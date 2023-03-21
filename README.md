# Hello HTTP

Build an HTTP server based on the standard library and respond to the request message.

## Usage

```text
usage: hello-http.py [-h HOST] [-p PORT] [-m ALLOWED_METHODS]
                     [-d DISALLOWED_METHODS] [--help]

optional arguments:
  -h HOST               Listen host.
                        If 0.0.0.0 will only listen all IPv4.
                        If [::] will only listen all IPv6.
                        If :: will listen all IPv4 and IPv6.
                        (default "127.0.0.1")
  -p PORT               Listen port.
                        If 0, random.
                        (default 8080)
  -m ALLOWED_METHODS    Allowed methods.
                        (format: <method>[,<methods>...])
  -d DISALLOWED_METHODS
                        Disallowed methods.
                        (format: <method>[,<methods>...])
  --help                Print help.
```

Run

```shell
python hello-http.py
```

Hello HTTP output

```text
Listening 127.0.0.1:8080
```

Test with cURL

```shell
curl http://127.0.0.1:8080
```

cURL output

```text
Hello HTTP

GET / HTTP/1.1
Host: 127.0.0.1:8080
User-Agent: curl/7.74.0
Accept: */*

```

Hello HTTP output

```text
GET / HTTP/1.1
```
