#!/usr/bin/env python3
"""Judging scribe: phone mic -> this computer -> local whisper -> projects/<name>/transcript.md
No internet needed (phone and computer on the same network, e.g. computer on phone hotspot).
Run from your workspace: python3 /path/to/scribe/server.py   then open https://<ip>:8844 on the phone.
Needs: ffmpeg, whisper-cli (whisper.cpp) and a ggml model (WHISPER_MODEL).
"""
import http.server, ssl, json, os, re, subprocess, threading, queue, time, socket, urllib.parse, datetime, sys

ROOT = os.path.abspath(os.environ.get("WORKSPACE", os.getcwd()))
PROJ = os.path.join(ROOT, "projects")
HERE = os.path.dirname(os.path.abspath(__file__))
PORT = int(os.environ.get("SCRIBE_PORT", 8844))
MODEL = os.path.expanduser(os.environ.get("WHISPER_MODEL", "~/whisper-models/ggml-small.en.bin"))

jobs = queue.Queue()
lock = threading.Lock()

def slug(s):
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s[:60] or "unnamed"

def pdir(name):
    d = os.path.join(PROJ, slug(name))
    os.makedirs(os.path.join(d, "audio"), exist_ok=True)
    return d

def append(path, text):
    with lock, open(path, "a") as f:
        f.write(text)

def hhmm(ts):
    return datetime.datetime.fromtimestamp(ts / 1000).strftime("%H:%M:%S")

def env(key):
    try:
        for l in open(os.path.join(ROOT, ".env")):
            if l.startswith(key + "="): return l.split("=", 1)[1].strip().strip('"\'')
    except FileNotFoundError: pass
    return os.environ.get(key, "")

# Optional: auto-create a folder for each project on the judging page.
# Needs an HTTP browser bridge that accepts POST /cmd {"cmd":"tabs"|"eval",...}. Read only.
BRIDGE = env("BROWSER_BRIDGE")
JUDGE_URL = env("JUDGE_URL")  # e.g. ethglobal.com/events/<event>/judging
EXTRACT_JS = r"""(() => {
  const seen = new Set(), out = [];
  for (const a of document.querySelectorAll('main a[href], a[href*="/showcase/"], a[href*="/judging/"]')) {
    const h = a.href.split('#')[0].split('?')[0];
    if (!/ethglobal\.com\/(showcase|events\/[^/]+\/(judging|project))\/[^/]+/.test(h)) continue;
    if (/judging\/?$/.test(h) || seen.has(h)) continue;
    seen.add(h);
    const name = (a.innerText || a.getAttribute('aria-label') || '').trim().split('\n')[0];
    let c = a, src = '', demo = '';
    for (let i = 0; i < 8 && c; i++, c = c.parentElement) {
      const links = [...c.querySelectorAll('a')];
      const s = links.find(x => /source code/i.test(x.innerText)), d = links.find(x => /^demo$/i.test(x.innerText.trim()));
      if (s || d) { src = s ? s.href : ''; demo = d ? d.href : ''; break; }
    }
    out.push({url: h, name: name || h.split('/').filter(Boolean).pop(), repo: src, demo});
  }
  return {projects: out, header: (document.body.innerText.match(/Projects \(\d+\/\d+\)/) || [''])[0]};
})()"""

def bridge(cmd, args=None):
    import urllib.request
    req = urllib.request.Request(BRIDGE + "/cmd", data=json.dumps({"cmd": cmd, "args": args or {}}).encode())
    r = json.loads(urllib.request.urlopen(req, timeout=20).read())
    if not r.get("ok"): raise RuntimeError(r.get("error"))
    return r["result"]

def watcher():
    """Poll the judging tab (read only). New project -> create projects/<slug>/meta.json."""
    if not (BRIDGE and JUDGE_URL):
        print("no BROWSER_BRIDGE/JUDGE_URL; project auto-detect off (type the project name on the phone)"); return
    tab = None
    while True:
        try:
            if tab is None:
                tab = next(t["tab_id"] for t in bridge("tabs")["tabs"] if JUDGE_URL in t.get("url", ""))
            res = bridge("eval", {"tab_id": tab, "code": EXTRACT_JS})["value"]
            for p in res["projects"]:
                key = p["url"].rstrip("/").split("/")[-1]
                d = os.path.join(PROJ, slug(key))
                m = os.path.join(d, "meta.json")
                if not os.path.exists(m):
                    os.makedirs(os.path.join(d, "audio"), exist_ok=True)
                    json.dump({"name": p["name"], "url": p["url"], "repo": p.get("repo", ""), "demo": p.get("demo", ""), "first_seen": int(time.time() * 1000)}, open(m, "w"), indent=1)
                    print("new project:", p["name"], p["url"], flush=True)
        except StopIteration:
            tab = None  # tab not listed right now (extension blip) — retry
        except Exception as e:
            tab = None
            print("watcher:", e, file=sys.stderr, flush=True)
        time.sleep(15)

def worker():
    while True:
        name, src, ts = jobs.get()
        try:
            wav = src.rsplit(".", 1)[0] + ".wav"
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-ar", "16000", "-ac", "1", wav], check=True)
            out = subprocess.run(["whisper-cli", "-m", MODEL, "-l", "en", "-nt", "-np", "-f", wav],
                                 capture_output=True, text=True, timeout=300).stdout
            text = " ".join(l.strip() for l in out.splitlines() if l.strip())
            # whisper hallucinates on silence
            if text and not re.fullmatch(r"[\s\.\[\]()a-zA-Z_]*(BLANK_AUDIO|silence|Thank you\.?|you)[\s\.\]\)]*", text, re.I):
                append(os.path.join(pdir(name), "transcript.md"), f"[{hhmm(ts)}] {text}\n")
            os.remove(wav)
            append(os.path.join(os.path.dirname(src), ".done"), os.path.basename(src) + "\n")
        except Exception as e:
            print("transcribe failed", src, e, file=sys.stderr)
        jobs.task_done()

class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def send(self, code, body, ctype="application/json"):
        b = body if isinstance(body, bytes) else body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        if u.path == "/":
            return self.send(200, open(os.path.join(HERE, "index.html"), "rb").read(), "text/html")
        if u.path == "/projects":
            os.makedirs(PROJ, exist_ok=True)
            names = sorted((d for d in os.listdir(PROJ) if os.path.isdir(os.path.join(PROJ, d))),
                           key=lambda d: -os.path.getmtime(os.path.join(PROJ, d)))
            meta = {}
            for n in names:
                try: meta[n] = json.load(open(os.path.join(PROJ, n, "meta.json")))
                except Exception: meta[n] = {"name": n, "first_seen": int(os.path.getmtime(os.path.join(PROJ, n)) * 1000)}
            names.sort(key=lambda n: -meta[n].get("first_seen", 0))
            return self.send(200, json.dumps({"projects": names, "meta": meta, "queue": jobs.qsize()}))
        if u.path == "/tail":
            q = urllib.parse.parse_qs(u.query)
            f = os.path.join(PROJ, slug(q.get("project", [""])[0]), "transcript.md")
            t = open(f).read()[-3000:] if os.path.exists(f) else ""
            return self.send(200, json.dumps({"text": t, "queue": jobs.qsize()}))
        self.send(404, "{}")

    def do_POST(self):
        u = urllib.parse.urlparse(self.path)
        q = {k: v[0] for k, v in urllib.parse.parse_qs(u.query).items()}
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        name = q.get("project", "")
        if not name:
            return self.send(400, '{"error":"no project"}')
        d = pdir(name)
        ts = int(q.get("ts", time.time() * 1000))
        if u.path == "/chunk":
            ext = re.sub(r"[^a-z0-9]", "", q.get("ext", "webm"))[:5] or "webm"
            src = os.path.join(d, "audio", f"{ts}.{ext}")
            if not os.path.exists(src):  # retries are idempotent
                open(src, "wb").write(body)
                jobs.put((name, src, ts))
            return self.send(200, '{"ok":true}')
        if u.path == "/note":
            text = body.decode("utf-8", "replace").strip()
            if text:
                append(os.path.join(d, "notes.md"), f"- [{hhmm(ts)}] {text}\n")
            return self.send(200, '{"ok":true}')
        self.send(404, "{}")

def cert():
    c, k = os.path.join(ROOT, ".scribe-cert.pem"), os.path.join(ROOT, ".scribe-key.pem")
    if not os.path.exists(c):
        subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "30",
                        "-keyout", k, "-out", c, "-subj", "/CN=judge-scribe"], check=True, capture_output=True)
    return c, k

def ips():
    o = subprocess.run(["ifconfig"], capture_output=True, text=True).stdout
    return [ip for ip in re.findall(r"inet (\d+\.\d+\.\d+\.\d+)", o) if not ip.startswith("127.")]

if __name__ == "__main__":
    threading.Thread(target=worker, daemon=True).start()
    threading.Thread(target=watcher, daemon=True).start()
    # re-queue audio that was saved but never transcribed (crash / restart)
    for p in (os.listdir(PROJ) if os.path.isdir(PROJ) else []):
        a = os.path.join(PROJ, p, "audio")
        if os.path.isdir(a):
            done = set(open(os.path.join(a, ".done")).read().split()) if os.path.exists(os.path.join(a, ".done")) else set()
            for f in sorted(os.listdir(a)):
                if f.startswith(".") or f.endswith(".wav") or f in done: continue
                jobs.put((p, os.path.join(a, f), int(f.split(".")[0])))
    s = http.server.ThreadingHTTPServer(("0.0.0.0", PORT), H)
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(*cert())
    s.socket = ctx.wrap_socket(s.socket, server_side=True)
    print("model:", os.path.basename(MODEL))
    for ip in ips():
        print(f"open on phone: https://{ip}:{PORT}")
    s.serve_forever()
