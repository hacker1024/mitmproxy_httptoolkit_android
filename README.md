# HTTP Toolkit Android integration for mitmproxy

A [mitmproxy] addon that allows use of the [HTTP Toolkit] Android app.

## Rationale

[HTTP Toolkit] is not as featureful as [mitmproxy], but has a very polished
Android connection experience. This addon allows all of HTTP Toolkit's Android
features (namely, guided certificate installation and per-app tunneling) to be
used with mitmproxy.

## Usage

### Installation

1. Download the [HTTP Toolkit Android app](https://play.google.com/store/apps/details?id=tech.httptoolkit.android.v1)
2. Clone this repository, or download the [addon script](./src/mitmproxy_httptoolkit_android.py)

### Execution

1. Launch `mitmproxy` (or `mitmdump`, `mitmweb`, etc.):  
   `mitmproxy -s src/mitmproxy_httptoolkit_android.py`
2. Follow the instructions in the log (type `E` in the TUI) to connect

#### Note: Multiple modes

If multiple mitmproxy modes are in use, the app will be able to connect to any
`listen_host`. It will only use the `listen_port` of the first mode for all of
them, however, due to limitations in its API.

### Installing the system certificate (rooted devices)

This feature is not yet implemented, but can be done manually in a number of
ways.

#### Method 1: Magisk

Install the CA certificate as instructed by the app. Then, install
[this Magisk module](https://www.androidacy.com/magisk-modules-repository/#movecerts)
and reboot.

#### Method 2: Generic

Manually perform the [actions the HTTP Toolkit server does](https://github.com/httptoolkit/httptoolkit-server/blob/b7379efcde361e0ab55383eac73ee4cbd4379bcd/src/interceptors/android/adb-commands.ts#L273).

[mitmproxy]: https://mitmproxy.org
[HTTP Toolkit]: https://httptoolkit.com/