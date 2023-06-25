import typing
import logging
import hashlib
import base64
import json
import socket

import psutil
from cryptography import x509
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from mitmproxy import ctx, http
from mitmproxy.proxy.mode_specs import ProxyMode
from mitmproxy.addons.onboardingapp import read_cert


class HTTPToolkitAndroidAddon:
    def running(self) -> None:
        port, setup_params = self._create_setup_params()
        intent_data = base64.urlsafe_b64encode(
            json.dumps(setup_params).encode()
        ).decode()

        logging.info("HTTP Toolkit Android app integration enabled.")
        logging.info(
            f"""Please launch the HTTP Toolkit Android app with ADB:
- If you'd like to tunnel over USB (can be unreliable), run this command first:
  adb reverse tcp:{port} tcp:{port}
- Then, run this command to launch the app.
  Alternatively, you can make a QR code containing the data URL, and scan it with the app.
  adb shell am start -a tech.httptoolkit.android.ACTIVATE -d 'https://android.httptoolkit.tech/connect/?data={intent_data}'"""
        )

    def request(self, flow: http.HTTPFlow) -> None:
        if (
            flow.request.pretty_host == "android.httptoolkit.tech"
            and flow.request.path == "/config"
        ):
            flow.response = http.Response.make(
                content=json.dumps({"certificate": self._read_pem().decode()})
            )

    def _create_setup_params(self) -> tuple[int, dict[str, object]]:
        # Based on https://github.com/httptoolkit/httptoolkit-server/blob/b7379efcde361e0ab55383eac73ee4cbd4379bcd/src/interceptors/android/android-adb-interceptor.ts#L101
        certificate = x509.load_pem_x509_certificate(self._read_pem())
        spki = certificate.public_key().public_bytes(
            Encoding.DER,
            PublicFormat.SubjectPublicKeyInfo,
        )
        certificate_digest = hashlib.sha256(spki).digest()
        certificate_fingerprint = base64.b64encode(certificate_digest).decode()

        modes = [ProxyMode.parse(spec) for spec in ctx.options.mode]
        listen_hosts = list(self._get_listen_hosts(modes, ctx.options.listen_host))
        listen_port = modes[0].listen_port(ctx.options.listen_port)

        return listen_port, {
            "addresses": listen_hosts,
            "port": listen_port,
            "localTunnelPort": listen_port,
            "certFingerprint": certificate_fingerprint,
        }

    @staticmethod
    def _read_pem() -> bytes:
        pem, pem_headers = read_cert("pem", "application/x-x509-ca-cert")
        return pem

    @staticmethod
    def _get_listen_hosts(
        modes: typing.Iterable[ProxyMode],
        default: str | None = None,
    ) -> typing.Iterator[str]:
        listen_all: bool = False
        for mode in modes:
            listen_host = mode.listen_host(default)
            if listen_host == "":
                listen_all = True
            else:
                yield listen_host

        if not listen_all:
            return

        # Add common Android emulator IPs
        yield "10.0.2.2"  # Standard emulator localhost IP
        yield "10.0.3.2"  # Genymotion localhost IP

        if_addrs = psutil.net_if_addrs()
        if_stats = psutil.net_if_stats()
        for interface, addresses in if_addrs.items():
            flags = typing.cast(str, if_stats[interface].flags).split(",")

            if (
                "loopback" in flags  # Loopback interfaces
                or interface == "docker0"  # Docker default bridge interface
                or interface.startswith("br-")  # More docker bridge interfaces
                or interface.startswith(
                    "veth"
                )  # Virtual interfaces for each docker container
            ):
                continue

            for address in addresses:
                # Android VPN app supports IPv4 only
                if address.family != socket.AF_INET:
                    continue
                yield address.address


addons: list[object] = [
    HTTPToolkitAndroidAddon(),
]
