"""Install the pinned native Ramos compiler; no application runtime dependency."""
from pathlib import Path
import hashlib
import platform
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.24.0"
ASSETS = {
    "Linux": ("ramos-linux-x86_64", "ramos", "d6eb08021b352ba133f902d016937af7b7a094704eb1e2e9d92cde024b256e85"),
    "Windows": ("ramos.exe", "ramos.exe", "280f69d2841de1411aa7030bb25b66be0644058870fc29f19a20767eff8e7c13"),
}

def install():
    system = platform.system()
    if platform.machine().lower() not in ("x86_64", "amd64") or system not in ASSETS:
        raise SystemExit("Ramos 0.24.0 requires Linux x64 or Windows x64")
    asset, filename, sha = ASSETS[system]
    path = ROOT / filename
    if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() == sha:
        return path
    url = f"https://github.com/zackmsa777-a11y/ramos/releases/download/v{VERSION}/{asset}"
    data = urllib.request.urlopen(url, timeout=60).read()
    if hashlib.sha256(data).hexdigest() != sha:
        raise SystemExit("Compiler SHA-256 mismatch; installation aborted")
    temporary = path.with_suffix(".download")
    temporary.write_bytes(data)
    temporary.chmod(0o755)
    temporary.replace(path)
    return path

if __name__ == "__main__":
    print(install())
