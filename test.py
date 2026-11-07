"""Integration check for a dedicated, empty Linux Docker VM. Run as guest root."""
import base64
import hashlib
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.error
import urllib.request

APP = "victoriametrics"
URL = "http://127.0.0.1:18428"


def check(ok, label):
    if not ok:
        raise RuntimeError(label)
    print("PASS", label, flush=True)


def request(path, password=None, body=None):
    req = urllib.request.Request(URL + path, data=body)
    if password is not None:
        token = base64.b64encode(("metrics:" + password).encode()).decode()
        req.add_header("Authorization", "Basic " + token)
    try:
        with urllib.request.urlopen(req, timeout=4) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as exc:
        return exc.code, b""


def wait_for(test, label):
    for _ in range(90):
        try:
            if test():
                check(True, label)
                return
        except (urllib.error.URLError, ConnectionError):
            pass
        time.sleep(1)
    raise RuntimeError(label)


def run(package):
    check(os.getuid() == 0 and sys.platform == "linux" and
          not subprocess.check_output(["docker", "ps", "-aq"]).strip(), "dedicated empty Linux engine")
    print("Archive SHA256", hashlib.sha256(package.read_bytes()).hexdigest(), flush=True)
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        with tarfile.open(package) as tar:
            (root/"docker-compose.yml").write_bytes(tar.extractfile("docker-compose.yml").read())
        for folder in ["data", "config"]:
            (root/folder).mkdir(mode=0o700)
            os.chown(root/folder, 1000, 1000)

        def compose(*args):
            subprocess.run(["docker", "compose", "-p", "tosvmtest", *args], cwd=root, check=True)

        def start():
            compose("create")
            compose("start")

        password = secrets.token_urlsafe(32)
        query = "/api/v1/query?query=tos_pilot_metric"
        def sample():
            code, raw = request(query, password)
            return code == 200 and any(float(v["value"][1]) == 42
                for v in json.loads(raw)["data"]["result"])

        try:
            start()
            wait_for(lambda: request(query)[0] == 401, "unconfigured instance rejects anonymous query")
            check(request(query, "")[0] == 401, "missing password file rejects empty password")
            path = root/"config/http-password"
            path.write_text(password + "\n")
            path.chmod(0o600)
            os.chown(path, 1000, 1000)
            wait_for(lambda: request(query, password)[0] == 200, "per-install password accepted")
            state = json.loads(subprocess.check_output(["docker", "inspect", APP]))[0]
            image = json.loads(subprocess.check_output(["docker", "image", "inspect", state["Image"]]))[0]
            check(image["Architecture"] == "amd64" and image["Os"] == "linux", "running Linux amd64 image")
            status = Path('/proc/{}/status'.format(state['State']['Pid'])).read_text().splitlines()
            for name in ["Uid", "Gid"]:
                check(next(s.split()[1:] for s in status if s.startswith(name + ":")) == ["1000"]*4, name+" 1000")
            check("NoNewPrivs:\t1" in status and int(next(s.split()[1] for s in status if s.startswith("CapEff:")), 16) == 0
                  and state["HostConfig"]["ReadonlyRootfs"], "read-only root, zero capabilities and no privilege escalation")
            code, page = request("/vmui/", password)
            check(code == 200 and b"<script" in page and b"vmui" in page.lower(), "VMUI HTML and application entrypoint")
            ingest = "/api/v1/import/prometheus"
            check(request(ingest, "incorrect", b"tos_pilot_metric 99\n")[0] == 401, "unauthorized ingestion rejected")
            check(request(ingest, password, b"tos_pilot_metric 42\n")[0] == 204, "authorized sample written")
            wait_for(sample, "query returns sample value 42")
            compose("stop")
            compose("start")
            wait_for(sample, "sample survives stop and start")
            compose("down")
            start()
            wait_for(sample, "sample and login survive removal and reinstall with retained directories")
        finally:
            compose("down")
    check(not subprocess.check_output(["docker", "ps", "-aq"]).strip() and not root.exists(), "container, test credentials and data removed")


if __name__ == "__main__":
    run(Path(sys.argv[1]))
