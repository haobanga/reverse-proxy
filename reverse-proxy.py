import asyncio
import ssl
import sys
from argparse import ArgumentParser
from functools import partial
from urllib.parse import urlparse

LIMIT = 2 ** 16


def is_ssl(scheme):
    return scheme in {'wss', 'https'}


async def stream_transfer(reader, writer):
    try:
        while not reader.at_eof():
            data = await reader.read(LIMIT)
            if not data:
                break
            writer.write(data)
            await writer.drain()
    except Exception as e:
        print(e)
    finally:
        writer.close()


async def connected_handle(hostname, port, ssl_context, reader, writer):
    remote_reader, remote_writer = await asyncio.open_connection(hostname, port, ssl=ssl_context)
    asyncio.ensure_future(stream_transfer(remote_reader, writer))
    asyncio.ensure_future(stream_transfer(reader, remote_writer))


def main(argv):
    arg_parser = ArgumentParser(
        description="reverse proxy", prog="reverse"
    )

    arg_parser.add_argument(
        "-a",
        "--hostname",
        help="TCP/IP hostname to serve on (default: %(default)r)",
        default="127.0.0.1",
    )
    arg_parser.add_argument(
        "-p",
        "--port",
        help="TCP/IP port to serve on (default: %(default)r)",
        type=int,
        default="8080",
    )

    arg_parser.add_argument(
        "-r",
        "--remote",
        help="Reverse proxy address",
        required=True,
    )
    args, extra_argv = arg_parser.parse_known_args(argv)

    loop = asyncio.get_event_loop()

    remote_url = urlparse(args.remote)
    remote_port = remote_url.port or (443 if is_ssl(remote_url.scheme) else 80)
    ssl_context = ssl.create_default_context() if is_ssl(remote_url.scheme) else None

    server = loop.run_until_complete(asyncio.start_server(
        partial(connected_handle, remote_url.hostname, remote_port, ssl_context), args.hostname, args.port))

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr} ->', args.remote)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()


if __name__ == '__main__':
    main(sys.argv[1:])
