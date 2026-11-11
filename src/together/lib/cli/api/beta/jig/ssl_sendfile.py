
# /// script
# requires-python = ">=3.14"
# ///
"""kTLS + SSL_sendfile uploader — S3-compatible (Tigris, R2, AWS)

Requires Linux with kTLS kernel support and OpenSSL with SSL_sendfile.
Usage: python3 ssl_sendfile.py --s3 [profile] <source_dir> s3://bucket/prefix
"""

from __future__ import annotations

import os
import ssl as _stdlib_ssl
import time
import errno
import fcntl
import queue
import ctypes
import select
import socket
import struct
import asyncio
import threading
import ctypes.util
from time import monotonic
from ctypes import CDLL, c_int, c_long, c_ulong, c_char_p, c_size_t, c_void_p, c_ssize_t
from typing import Any, Callable
from pathlib import Path
from dataclasses import dataclass

# --- Config ---

CHUNK_MIN = 5 * 1024 * 1024  # S3 minimum part size
WORKERS = int(os.environ.get("WORKERS", min(len(os.sched_getaffinity(0)) * 2, 256)))
PARTS_MULT = int(os.environ.get("PARTS", "4"))  # parts = PARTS_MULT * WORKERS
SO_SNDBUFFORCE = 32

noop = lambda *args: None
debug = print if os.getenv("DEBUG") else noop
trace = print if os.getenv("TRACE") else noop

# --- OpenSSL ctypes ---

_libssl = CDLL(ctypes.util.find_library("ssl") or "libssl.so")
_libcrypto = CDLL(ctypes.util.find_library("crypto") or "libcrypto.so")
off_t = c_long if ctypes.sizeof(c_long) >= 8 else ctypes.c_longlong

WANT_READ, WANT_WRITE, ERR_SYSCALL, ERR_ZERO = 2, 3, 5, 6
KTLS_SEND_CTRL = 73  # BIO_CTRL_GET_KTLS_SEND


# def _fn[*Ts, R](lib: CDLL, name: str, argtypes: tuple[*Ts], restype: R = c_int) -> Callable[[*Ts], R]:
def _fn(
    lib: CDLL, name: str, argtypes: list[Any], restype: Any = c_int
) -> Callable[..., Any]:
    f = getattr(lib, name)
    f.argtypes, f.restype = argtypes, restype
    return f


_ERR_get = _fn(_libcrypto, "ERR_get_error", [], c_ulong)
_ERR_str = _fn(_libcrypto, "ERR_error_string_n", [c_ulong, c_char_p, c_size_t], None)
_BIO_ctrl = _fn(_libcrypto, "BIO_ctrl", [c_void_p, c_int, c_long, c_void_p], c_long)

_TLS_method = _fn(_libssl, "TLS_client_method", [], c_void_p)
_CTX_new = _fn(_libssl, "SSL_CTX_new", [c_void_p], c_void_p)
_CTX_verify = _fn(_libssl, "SSL_CTX_set_verify", [c_void_p, c_int, c_void_p], None)
_CTX_paths = _fn(_libssl, "SSL_CTX_set_default_verify_paths", [c_void_p])
_CTX_opts = _fn(_libssl, "SSL_CTX_set_options", [c_void_p, c_ulong], c_ulong)
_CTX_ctrl = _fn(_libssl, "SSL_CTX_ctrl", [c_void_p, c_int, c_long, c_void_p], c_long)
_CTX_ciphers = _fn(_libssl, "SSL_CTX_set_cipher_list", [c_void_p, c_char_p])
_SSL_new = _fn(_libssl, "SSL_new", [c_void_p], c_void_p)
_SSL_free = _fn(_libssl, "SSL_free", [c_void_p], None)
_SSL_set_fd = _fn(_libssl, "SSL_set_fd", [c_void_p, c_int])
_SSL_ctrl = _fn(_libssl, "SSL_ctrl", [c_void_p, c_int, c_long, c_void_p], c_long)
_SSL_set1_host = _fn(_libssl, "SSL_set1_host", [c_void_p, c_char_p])
_SSL_connect = _fn(_libssl, "SSL_connect", [c_void_p])
_SSL_get_error = _fn(_libssl, "SSL_get_error", [c_void_p, c_int])
_SSL_verify = _fn(_libssl, "SSL_get_verify_result", [c_void_p], c_long)
_SSL_write = _fn(_libssl, "SSL_write", [c_void_p, c_void_p, c_int])
_SSL_read = _fn(_libssl, "SSL_read", [c_void_p, c_void_p, c_int])
_SSL_wbio = _fn(_libssl, "SSL_get_wbio", [c_void_p], c_void_p)
_SSL_sendfile = _fn(
    _libssl, "SSL_sendfile", [c_void_p, c_int, off_t, c_size_t, c_int], c_ssize_t
)
_SSL_shutdown = _fn(_libssl, "SSL_shutdown", [c_void_p])
_SSL_get1_session = _fn(_libssl, "SSL_get1_session", [c_void_p], c_void_p)
_SSL_set_session = _fn(_libssl, "SSL_set_session", [c_void_p, c_void_p])
_SSL_get_version = _fn(_libssl, "SSL_get_version", [c_void_p], c_char_p)
_SSL_get_current_cipher = _fn(_libssl, "SSL_get_current_cipher", [c_void_p], c_void_p)
_SSL_CIPHER_get_name = _fn(_libssl, "SSL_CIPHER_get_name", [c_void_p], c_char_p)


def _ssl_errors() -> str:
    msgs = []
    while code := _ERR_get():
        buf = ctypes.create_string_buffer(256)
        _ERR_str(code, buf, 256)
        msgs.append(buf.value.decode())
    return "; ".join(msgs) or "(no error)"


def _wait(sock: socket.socket, err: int, deadline: float) -> None:
    timeout = max(0, deadline - monotonic())
    r: list[socket.socket] = [sock] if err == WANT_READ else []
    w: list[socket.socket] = [] if err == WANT_READ else [sock]
    if not any(select.select(r, w, [], timeout)):
        raise TimeoutError


_TCP_STATES = {1: "ESTABLISHED", 2: "SYN_SENT", 3: "SYN_RECV", 4: "FIN_WAIT1"}
_TCP_STATES |= {5: "FIN_WAIT2", 6: "TIME_WAIT", 7: "CLOSE", 8: "CLOSE_WAIT"}
_TCP_STATES |= {9: "LAST_ACK", 10: "LISTEN", 11: "CLOSING"}


def _sock_diag(sock: socket.socket) -> str:
    """Show TCP-level state to attach to an error.

    `tcp=` and `since_peer_data=` tell apart two broken-pipe cases:
    CLOSE_WAIT with recent peer data means the server answered and hung up;
    ESTABLISHED with stale peer data means the path died silently.
    """
    out: list[str] = []
    try:
        e = sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        if e:
            out.append(f"so_error={errno.errorcode.get(e, e)}")
    except OSError:
        pass
    try:
        # struct tcp_info: 8 u8 then 24 u32, through tcpi_total_retrans
        f = struct.unpack(
            "=8B24I", sock.getsockopt(socket.IPPROTO_TCP, socket.TCP_INFO, 104)[:104]
        )
        out += [
            f"tcp={_TCP_STATES.get(f[0], f[0])}", f"cwnd={f[26]}",
            f"unacked={f[12]}", f"lost={f[14]}", f"retrans={f[15]}/{f[31]}",
            f"rtt={f[23] / 1000:.1f}ms", f"rto={f[8] / 1000:.0f}ms",
            f"since_peer_data={f[19]}ms",
        ]
    except (OSError, struct.error):
        pass
    try:  # TIOCOUTQ: bytes still queued (unsent + unacked)
        out.append(f"outq={struct.unpack('i', fcntl.ioctl(sock, 0x5411, b'0000'))[0]}")
    except OSError:
        pass
    return " ".join(out) or "no diag available"


# --- TLS context ---


def _make_ssl_ctx() -> int:
    """Create one shared SSL_CTX — expensive to build, cheap to reuse per connection."""
    ctx = _CTX_new(_TLS_method())
    assert ctx, _ssl_errors()
    _CTX_verify(ctx, 0x01, None)  # SSL_VERIFY_PEER
    _CTX_paths(ctx)  # load system CA bundle once
    _CTX_opts(ctx, 1 << 3)  # SSL_OP_ENABLE_KTLS
    if not os.getenv("NO_TLS12"):
        # TLS 1.2 + AES-128-GCM: hardware TLS offload on ConnectX-5/6
        _CTX_ctrl(
            ctx, 124, 0x0303, None
        )  # SSL_CTRL_SET_MAX_PROTO_VERSION, TLS1_2_VERSION
        assert _CTX_ciphers(
            ctx, b"ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256"
        ), _ssl_errors()
    return ctx


_shared_ctx = _make_ssl_ctx()


# --- Connection ---


class Connection:
    """Persistent HTTPS/1.1 connection with kTLS for SSL_sendfile."""

    def __init__(
        self,
        host: str,
        token: str | None = None,
        port: int = 443,
        timeout: float = 30.0,
        session: int | None = None
    ) -> None:
        self.host = host
        self.timeout = timeout
        self.session: int | None = None
        self._closed = False
        self.token = token

        sock = socket.create_connection((host, port), timeout=timeout)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        # attempt to increase the send buffer
        want_sndbuf_kb = 64 * 1024  # 64MB
        try:
            # forcing a specific buffer size requires sudo or CAP_NET_ADMIN
            sock.setsockopt(socket.SOL_SOCKET, SO_SNDBUFFORCE, want_sndbuf_kb * 1024)
            print("Force set send buffer to", want_sndbuf_kb, "KB")
        except PermissionError:
            # unlike SNDBUFFORCE, SNDBUF is capped to wmem_max (208KB default)
            # setting SNDBUFFORCE also disables autotuning of the send buffer
            # only bother if wmem_max is actually higher than what we want
            try:
                with open("/proc/sys/net/core/wmem_max") as f:
                    wmem_max_kb = int(f.read()) / 1024
            except OSError:
                wmem_max_kb = 0
            msg = f"Set send buffer: Want {want_sndbuf_kb} KB, write memory max {wmem_max_kb} KB:"
            if wmem_max_kb >= want_sndbuf_kb:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, want_sndbuf_kb * 1024)
                print(msg, "OK")
            else:
                # otherwise leave it alone: autotuning reaches tcp_wmem[2] by itself
                print(msg, "can't raise send buffer")
        sock.setblocking(False)

        ssl = _SSL_new(_shared_ctx)
        assert ssl, _ssl_errors()
        try:
            sni = host.encode("idna")
            sni_p = c_char_p(sni)  # prevent GC before SSL_ctrl returns
            _SSL_ctrl(ssl, 55, 0, ctypes.cast(sni_p, c_void_p))  # SNI
            _SSL_set1_host(ssl, sni)
            _SSL_set_fd(ssl, sock.fileno())
            if session:
                # resumption — skips full handshake + cert verify
                _SSL_set_session(ssl, session)

            deadline = monotonic() + timeout
            while (ret := _SSL_connect(ssl)) != 1:
                err = _SSL_get_error(ssl, ret)
                if err in (WANT_READ, WANT_WRITE):
                    _wait(sock, err, deadline)
                    continue
                # Handshake failed — probe what the server supports for diagnostics
                diag = _ssl_errors()
                try:
                    with socket.create_connection((host, port), timeout=5) as probe:
                        default_ctx = _stdlib_ssl.create_default_context()
                        with default_ctx.wrap_socket(probe, server_hostname=host) as s:
                            c = s.cipher()
                            diag += f"\n  server supports: {s.version()} {c[0] if c else '?'}"
                except Exception:  # noqa: BLE001, S110
                    pass
                raise RuntimeError(f"SSL_connect to {host}: {diag}")

            if not session:
                assert _SSL_verify(ssl) == 0, "cert verification failed"

            wbio = _SSL_wbio(ssl)
            ktls = wbio and _BIO_ctrl(wbio, KTLS_SEND_CTRL, 0, None) > 0
            c = _SSL_get_current_cipher(ssl)
            cipher = _SSL_CIPHER_get_name(c).decode() if c else "unknown"
            version = (
                _SSL_get_version(ssl).decode() if _SSL_get_version(ssl) else "unknown"
            )
            if not ktls:
                raise RuntimeError(
                    f"kTLS not available for {host} (negotiated {version} {cipher}). "
                    f"Need kernel kTLS support + AES-GCM cipher."
                )

            self.session = _SSL_get1_session(ssl)  # pool caches for future connections
            self._sock, self._ssl = sock, ssl
        except BaseException:
            _SSL_free(ssl)
            sock.close()
            raise

    @property
    def alive(self) -> bool:
        return not self._closed

    def close(self) -> None:
        if not self._closed:
            self._closed = True
            _SSL_shutdown(self._ssl)
            _SSL_free(self._ssl)
            self._sock.close()

    def _write(self, data: bytes) -> None:
        sock, ssl, deadline = self._sock, self._ssl, monotonic() + self.timeout
        pos = 0
        while pos < len(data):
            n = min(len(data) - pos, 1 << 30)
            buf = (ctypes.c_char * n).from_buffer_copy(data[pos : pos + n])
            ret = _SSL_write(ssl, buf, n)
            if ret > 0:
                pos += ret
                continue
            err = _SSL_get_error(ssl, ret)
            if err in (WANT_READ, WANT_WRITE):
                _wait(sock, err, deadline)
                continue
            raise RuntimeError(f"SSL_write at {pos}/{len(data)}: {_ssl_errors()} | {_sock_diag(sock)}")

    def _read(self, n: int = 8192) -> bytes:
        sock, ssl, deadline = self._sock, self._ssl, monotonic() + self.timeout
        buf = ctypes.create_string_buffer(n)
        while True:
            ret = _SSL_read(ssl, buf, n)
            if ret > 0:
                trace(f"read: {buf.raw[:ret]}")
                return buf.raw[:ret]
            err = _SSL_get_error(ssl, ret)
            if err in (ERR_ZERO, ERR_SYSCALL):
                return b""
            if err in (WANT_READ, WANT_WRITE):
                _wait(sock, err, deadline)
                continue
            raise RuntimeError(f"SSL_read: {_ssl_errors()} | {_sock_diag(sock)}")

    def _sendfile(self, fd: int, offset: int, size: int) -> None:
        """Send body from fd via SSL_sendfile. Inactivity timeout, not total."""
        sock, ssl = self._sock, self._ssl
        sent = 0
        calls = 0
        while sent < size:
            ret = _SSL_sendfile(ssl, fd, off_t(offset + sent), size - sent, 0)
            calls += 1
            if ret > 0:
                sent += ret
                debug(f"sendfile ok: fd={fd}, ret={ret}, sent={sent}, size={size}, calls={calls}")
                continue
            err = _SSL_get_error(ssl, ret)
            if err == WANT_READ:
                debug(f"sendfile: WANT_READ: fd={fd}, ret={ret}, sent={sent}, size={size}, calls={calls}, wait={self.timeout}")
                _wait(sock, err, monotonic() + self.timeout)
                continue
            if err == WANT_WRITE:
                debug(f"sendfile: WANT_WRITE: fd={fd}, ret={ret}, sent={sent}, size={size}, calls={calls}, wait={self.timeout}")
                _wait(sock, err, monotonic() + self.timeout)
                continue
            diag = _sock_diag(sock)  # capture before _read: reading mutates state
            try:
                response = self._read(512).split(b"\r\n", 1)[0].decode("latin-1", "replace")
            except Exception:  # noqa: BLE001 - diagnostics must not mask the real error
                response = ""

            raise RuntimeError(
                f"libssl error: SSL_sendfile at {sent}/{size} after {calls} calls: "
                f"{_ssl_errors()} | {diag}: server response: {response}"
            )

    def _read_response(self) -> tuple[int, dict[str, str], bytes]:
        """Read HTTP/1.1 response. Returns (status, headers, body)."""
        raw = b""
        while b"\r\n\r\n" not in raw:
            chunk = self._read()
            if not chunk:
                raise RuntimeError("connection closed reading response")
            raw += chunk

        hdr_end = raw.index(b"\r\n\r\n") + 4
        lines = raw[:hdr_end].decode("latin-1").strip().lower().split("\r\n")
        status = int(lines[0].split()[1])

        pairs = [line.split(":", 1) for line in lines[1:] if ":" in line]
        headers = {k.strip(): v.strip() for k, v in pairs}

        # Drain body so connection is reusable
        body = raw[hdr_end:]
        if content_length := headers.get("content-length"):
            while remaining := (int(content_length) - len(body)):
                if not (chunk := self._read(min(8192, remaining))):
                    break
                body += chunk

        if headers.get("connection") == "close":
            debug("connection: close")
            self.close()

        return status, headers, body

    def put(self, target: str, fd: int, size: int, offset=0, req_headers=None) -> list[Any]:
        extra = "".join(f"{k}: {v}\r\n" for k, v in (req_headers or {}).items())
        
        if self.token:
            msg = f"PUT {target} HTTP/1.1\r\nhost: {self.host}\r\ncontent-length: {size}\r\nAuthorization: {self.token}\r\n{extra}\r\n"
        else:
            msg = f"PUT {target} HTTP/1.1\r\nhost: {self.host}\r\ncontent-length: {size}\r\n{extra}\r\n"
        
        trace(f"write request: {msg}")
        self._write(msg.encode())
        self._sendfile(fd, offset, size)
        status, headers, body = self._read_response()
        if not (200 <= status < 300):
            raise Exception(f"Unexpected HTTP status code {status} for https://{target}, size {size}: {headers} {body}")  # noqa: TRY002
        return [status, headers, body]


# --- Connection Pool ---


class Pool:
    """LIFO pool of warm kTLS connections to one origin."""

    def __init__(self, host: str, token: str | None = None, port: int = 443) -> None:
        self.host, self.port = host, port
        self._q: queue.LifoQueue[Connection] = queue.LifoQueue()
        self._session: int | None = None
        self._session_lock = threading.Lock()
        self.token = token

    def _new_conn(self) -> Connection:
        with self._session_lock:
            session = self._session
        return Connection(host=self.host, token=self.token, port=self.port, session=session)

    def _cache_session(self, c: Connection) -> None:
        if c.session and self._session is None:
            with self._session_lock:
                if self._session is None:
                    self._session = c.session

    def _acquire(self) -> Connection:
        try:
            c = self._q.get_nowait()
            if not c.alive:
                c.close()
                return self._new_conn()
            return c
        except queue.Empty:
            return self._new_conn()

    def _release(self, c: Connection) -> None:
        self._cache_session(c)
        if c.alive:
            self._q.put(c)

    def put(self, target: str, fd: int, size: int, offset = 0, tries = 1, req_headers=None) -> str:
        """PUT via kTLS + SSL_sendfile with retries. Returns status code."""
        for attempt in range(1, tries + 1):
            c = self._acquire()
            try:
                resp = c.put(target, fd, size=size, offset=offset, req_headers=req_headers)
                self._release(c)
                return resp
            except Exception as e:
                c.close()
                if attempt == tries:
                    raise
                print(f"retrying PUT {target} after err {repr(e)}")  # noqa: RUF010
                time.sleep(0.1 * attempt)
        raise RuntimeError("unreachable")

# --- Upload ---


@dataclass
class File:
    """A local file to upload."""

    fd: int
    size: int
    key: str
    n_parts: int = 0

    def split(self) -> list[Part]:
        chunk = -(-self.size // self.n_parts)
        return [
            Part(i * chunk, min(chunk, self.size - i * chunk), i + 1)
            for i in range(self.n_parts)
        ]


@dataclass
class Part:
    """One upload request: URL + file region."""

    offset: int
    size: int
    part_num: int = 1


def find_files(source: Path, s3_path: str) -> list[File]:
    def make_file(p: Path) -> File:
        fd = os.open(p, os.O_RDONLY)
        size = os.fstat(fd).st_size
        return File(fd, size, f"/{s3_path}/{p.relative_to(source).as_posix()}")

    files = [make_file(p) for p in source.rglob("*") if p.is_file()]
    files.sort(key=lambda f: -f.size)
    # set f.n_parts on each file, distributing target parts proportionally by size.
    target = PARTS_MULT * WORKERS
    total = sum(f.size for f in files)
    for f in files:
        f.n_parts = max(1, round(target * f.size / total))
    delta = target - sum(f.n_parts for f in files)
    for f in files[: abs(delta)]:
        f.n_parts += 1 if delta > 0 else -1
    for f in files:
        f.n_parts = max(1, min(f.n_parts, -(-f.size // CHUNK_MIN)))
    return files

# --- CLI ---


async def main() -> None:
    return
    # if len(sys.argv) < 4 or sys.argv[1] != "--s3":
    #     sys.exit(f"Usage: {sys.argv[0]} --s3 [profile] <source_dir> s3://bucket/prefix")

    # profile = sys.argv[2] if len(sys.argv) == 5 else "tigris"
    # source = Path(sys.argv[-2])
    # s3_path = sys.argv[-1].removeprefix("s3://")
    # await S3Upload(SigV4(profile), source, s3_path).run()


if __name__ == "__main__":
    asyncio.run(main())


    # def presign_put(self, key: str, upload_id: str, part_num: int) -> str:
    #     params = {
    #         "partNumber": str(part_num),
    #         "uploadId": upload_id,
    #         "X-Amz-Algorithm": "AWS4-HMAC-SHA256",
    #         "X-Amz-Credential": self._cred,
    #         "X-Amz-Date": self._amz,
    #         "X-Amz-Expires": "3600",
    #         "X-Amz-SignedHeaders": "host",
    #     }
    #     if self._tok:
    #         params["X-Amz-Security-Token"] = self._tok
    #     canonical_query = "&".join(
    #         f"{quote(k, safe='')}={quote(v, safe='')}"
    #         for k, v in sorted(params.items())
    #     )
    #     canonical_request = f"PUT\n{quote(key, safe='/')}\n"
    #     canonical_request += f"{canonical_query}\n"
    #     canonical_request += f"host:{self.host}\n\nhost\nUNSIGNED-PAYLOAD"
    #     signed_query = f"{canonical_query}&X-Amz-Signature={self._sign(canonical_request, self._amz)}"
    #     return f"{key}?{signed_query}"

    # def _sign(self, canonical_request: str, amz: str) -> str:
    #     cr = sha256(canonical_request.encode()).hexdigest()
    #     string_to_sign = f"AWS4-HMAC-SHA256\n{amz}\n{self._scope}\n{cr}"
    #     return hmac.new(self._key, string_to_sign.encode(), sha256).hexdigest()