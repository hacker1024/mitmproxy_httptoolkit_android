{ lib, python3 }:

let
  python = python3;
in
python.pkgs.buildPythonPackage {
  pname = "mitmproxy-httptoolkit-android";
  version = "0.1.0";
  format = "pyproject";

  src = lib.cleanSource ./.;

  propagatedBuildInputs = with python.pkgs; [
    mitmproxy
    cryptography
    psutil
  ];
}