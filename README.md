# Inugami Starter

Inugami is an experimental Crow-backed web framework for Hachi focused on lightweight HTTP services, APIs, and native server-side apps.

## What is included

- `hMods/inugami.🐺` - framework-friendly facade
- `hMods/inugami/api.🐺` - Crow-backed route/runtime layer
- `main.hachi` - ready-to-run demo app
- `examples/` - a few smaller examples
- `pages/sample_api_page.html` - sample static page for `file:` routes
- `vendor/Crow-master/include/` - vendored Crow headers
- `vendor/Crow-master/LICENSE` - upstream Crow license

## Prerequisite

Install standalone Asio headers on your system.

On Debian/Ubuntu-like systems:

```bash
sudo apt install libasio-dev
```

## Run the included demo

```bash
hachi main.hachi -go -cf "-I./vendor/Crow-master/include -pthread"
```

Then test:

```bash
curl localhost:8080
curl localhost:8080/health
curl localhost:8080/version
curl localhost:8080/home -i
curl -X POST localhost:8080/submit
curl -X POST localhost:8080/save
```

## Developer feel

The intended user-facing style is:

```hachi
>@"inugami"

setLogLevel: 1

get: "/", "Hello from Inugami"
json: "/health", "{"ok":true}"
html: "/docs", "<h1>Docs</h1>"
statusText: "/teapot", 418, "I am a teapot"

run: 8080
```

## Notes

- `file:` currently serves raw file bytes and does not infer MIME type yet.
- `run:` uses Crow's multithreaded server mode.
- `runSingle:` is included for simpler debugging.
