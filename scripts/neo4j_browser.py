"""One private Codespaces origin for Neo4j Browser and Bolt-over-WebSocket.

Only Python's standard library is required. Run by the app container, before
post-create installs the shared workshop requirements. TLS and access control
are provided by GitHub's PRIVATE port forwarding, not by this local proxy.
"""

import argparse
import asyncio
import contextlib
import os
from urllib.parse import urlsplit


START_PAGE = """<!doctype html>
<html lang="de"><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Neo4j im Storage-Workshop</title>
<style>
body{font:18px/1.6 system-ui,sans-serif;max-width:680px;margin:8vh auto;padding:24px;color:#17324d}
a{display:inline-block;background:#075d85;color:white;padding:12px 20px;border-radius:8px;text-decoration:none}
code{overflow-wrap:anywhere;font-size:15px}dt{font-weight:bold}dd{margin:0 0 12px}
</style>
<h1>Neo4j im Storage-Workshop</h1>
<p>Öffne den Neo4j Browser und melde Dich mit dem Passwort Deiner Kursdatenbank an.</p>
<p><a id="open">Neo4j Browser öffnen</a></p>
<dl><dt>Benutzer</dt><dd>neo4j</dd><dt>Datenbank</dt><dd>neo4j</dd>
<dt>Verbindungsadresse (automatisch vorbereitet)</dt><dd><code id="address"></code></dd></dl>
<p>Nach der Anmeldung zum Prüfen ausführen: <code>RETURN 1 AS verbindung_ok;</code></p>
<noscript>Bitte JavaScript im Webbrowser erlauben.</noscript>
<script>
const secure = location.protocol === 'https:';
const address = `${secure ? 'bolt+s' : 'bolt'}://${location.hostname}:${location.port || (secure ? '443' : '80')}`;
document.getElementById('address').textContent = address;
const params = new URLSearchParams({connectURL: address.replace('://', '://neo4j@'), db: 'neo4j'});
document.getElementById('open').href = '/browser/?' + params;
</script></html>
""".encode("utf-8")


async def reply(writer, status, body, content_type="text/plain; charset=utf-8"):
    writer.write((f"HTTP/1.1 {status}\r\nContent-Type: {content_type}\r\n"
                  f"Content-Length: {len(body)}\r\nConnection: close\r\n"
                  "Cache-Control: no-store\r\n\r\n").encode() + body)
    await writer.drain()


async def pipe(reader, writer):
    while data := await reader.read(65536):
        writer.write(data)
        await writer.drain()


async def handle(reader, writer, host, http_port, bolt_port):
    upstream = None
    tasks = []
    forwarding = False
    try:
        raw = await asyncio.wait_for(reader.readuntil(b"\r\n\r\n"), 15)
        lines = raw[:-4].split(b"\r\n")
        method, target, version = lines[0].decode("ascii").split()
        if not target.startswith("/") or version not in {"HTTP/1.0", "HTTP/1.1"}:
            raise ValueError("Invalid request")
        headers = []
        for line in lines[1:]:
            key, value = line.split(b":", 1)
            headers.append((key, value.strip()))
        lookup = {k.lower(): v for k, v in headers}
        websocket = lookup.get(b"upgrade", b"").lower() == b"websocket"
        path = urlsplit(target).path
        if not websocket and method == "GET" and (
            path == "/workshop/" or (path == "/" and b"text/html" in lookup.get(b"accept", b""))
        ):
            await reply(writer, "200 OK", START_PAGE, "text/html; charset=utf-8")
            return
        # Never forward GitHub session cookies or access tokens to Neo4j.
        # Force ordinary HTTP connections to close after one request, so each
        # request is parsed and filtered. WebSockets remain bidirectional.
        skip = {b"cookie", b"x-github-token", b"proxy-authorization"}
        if not websocket:
            skip |= {b"connection", b"keep-alive"}
        outgoing = [lines[0]] + [k + b": " + v for k, v in headers if k.lower() not in skip]
        if not websocket:
            outgoing.append(b"Connection: close")
        upstream_reader, upstream = await asyncio.wait_for(
            asyncio.open_connection(host, bolt_port if websocket else http_port), 10
        )
        upstream.write(b"\r\n".join(outgoing) + b"\r\n\r\n")
        await upstream.drain()
        forwarding = True
        tasks = [asyncio.create_task(pipe(reader, upstream)),
                 asyncio.create_task(pipe(upstream_reader, writer))]
        await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    except (ValueError, UnicodeError, asyncio.LimitOverrunError):
        if not forwarding:
            await reply(writer, "400 Bad Request", b"Invalid HTTP request.\n")
    except (OSError, asyncio.TimeoutError):
        if not forwarding:
            await reply(writer, "502 Bad Gateway",
                        b"Neo4j ist noch nicht erreichbar. Bitte den Setup-Check pruefen und erneut laden.\n")
    except asyncio.IncompleteReadError:
        pass
    finally:
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        for stream in (upstream, writer):
            if stream:
                stream.close()
                with contextlib.suppress(OSError):
                    await stream.wait_closed()


async def serve(args):
    server = await asyncio.start_server(
        lambda r, w: handle(r, w, args.neo4j_host, args.http_port, args.bolt_port),
        args.bind, args.port, limit=65536,
    )
    print(f"Neo4j Browser bereit: Port {args.port} im Register Ports oeffnen (Private / HTTP).", flush=True)
    async with server:
        await server.serve_forever()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bind", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--neo4j-host", default=os.environ.get("NEO4J_HOST", "neo4j"))
    parser.add_argument("--http-port", type=int, default=7474)
    parser.add_argument("--bolt-port", type=int, default=int(os.environ.get("NEO4J_PORT", "7687")))
    args = parser.parse_args()
    try:
        asyncio.run(serve(args))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
