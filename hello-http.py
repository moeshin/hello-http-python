#!/usr/bin/env python3

import argparse
import http.server
import io
import socket
import socketserver
import typing
import logging

logger = logging.getLogger("hello-http")

a_allowed_methods = None
a_disallowed_methods = None


class Server(socketserver.TCPServer):
    def __init__(self, host, port, handler):
        is_all = host == '::'
        if ':' in host:
            self.address_family = socket.AF_INET6
        else:
            self.address_family = socket.AF_INET
        super().__init__((host, port), handler, False)
        if is_all:
            self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, False)

        try:
            self.server_bind()
            self.server_activate()
            logger.info('Listening %s', get_address_string(self.server_address))
        except Exception:
            self.server_close()
            raise


class Handler(http.server.BaseHTTPRequestHandler):

    def log_request(self, code: typing.Union[int, str] = ..., size: typing.Union[int, str] = ...) -> None:
        ...

    def __getattribute__(self, item: str):
        if item.startswith('do_'):
            item = 'do_ALL'
        return super().__getattribute__(item)

    def do_ALL(self):
        logger.info("%s", self.requestline)
        logger.debug("addr: %s", self.client_address)

        if (a_disallowed_methods is not None and self.command in a_disallowed_methods) \
                or (a_allowed_methods is not None and self.command not in a_allowed_methods):
            self.send_response(http.HTTPStatus.METHOD_NOT_ALLOWED)
            self.end_headers()
            return

        self.send_response(http.HTTPStatus.OK)
        self.send_header('Content-Type', 'text/plain')

        if self.command == 'HEAD':
            self.end_headers()
            return
        out = io.BytesIO()
        out.write(b'Hello HTTP\n\n')
        out.write(self.requestline.encode())
        out.write(b'\n')
        out.write(bytes(self.headers))
        length = int(self.headers.get('Content-Length', 0))
        if length > 0:
            out.write(self.rfile.read(length))

        out = out.getvalue()

        self.send_header('Content-Length', str(len(out)))
        self.end_headers()
        self.wfile.write(out)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('%s', out.decode())


def get_address_string(address: typing.Tuple[str, int]):
    host, port, *_ = address
    if not host.startswith('[') and ':' in host:
        host = f'[{host}]'
    return f'{host}:{port}'


def parse_methods(string: typing.Optional[str]):
    if string is None:
        return None
    methods = set()
    for method in string.split(','):
        method = method.strip()
        if method == "":
            continue
        methods.add(method.upper())
    if len(methods) == 0:
        return None
    return methods


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s:%(levelname)s:%(name)s:%(message)s"
    )
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        '-h', dest='host', type=str, default='127.0.0.1',
        help='Listen host. '
             'If 0.0.0.0 will only listen all IPv4. '
             'If [::] will only listen all IPv6. '
             'If :: will listen all IPv4 and IPv6. '
             '(default "127.0.0.1")')
    parser.add_argument(
        '-p', dest='port', type=int, default=8080,
        help='Listen port. '
             'If 0, random. '
             '(default 8080)')
    parser.add_argument(
        '-m', dest='allowed_methods',
        help='Allowed methods. '
             '(format: <method>[,<method>...])')
    parser.add_argument(
        '-d', dest='disallowed_methods',
        help='Disallowed methods. '
             '(format: <method>[,<method>...])')
    parser.add_argument('-v', action='store_true', help='Enable verbose output.')
    parser.add_argument('--help', action='help', help='Print help.')
    args = parser.parse_args()

    if args.v:
        logging.getLogger().setLevel(logging.DEBUG)

    global a_allowed_methods, a_disallowed_methods
    a_allowed_methods = parse_methods(args.allowed_methods)
    a_disallowed_methods = parse_methods(args.disallowed_methods)

    with Server(args.host, args.port, Handler) as server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            ...


if __name__ == '__main__':
    main()
