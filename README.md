
<p align="center">
  <img src="images/inugami-mascot.png" alt="Inugami mascot" width="50%">
</p>

# Inugami

Inugami is an experimental web framework for Hachi focused on lightweight HTTP services, APIs, and native server-side apps.

## What is included

- `hMods/inugami.🐺` - framework-friendly facade and runtime layer
- `main.hachi` - ready-to-run demo app
- `examples/` - a few smaller examples
- `pages/sample_api_page.html` - sample static page for `file:` routes
- `images/inugami-icon.png` - simple icon/logo
- `images/inugami-mascot.png` - main mascot art
- `images/inugami-mascot-round.png` - round mascot variant
- `vendor/Crow-master/include/` - vendored Crow headers
- `vendor/Crow-master/LICENSE` - upstream Crow license

## Prerequisite

Install standalone Asio headers on your system.

On Debian/Ubuntu-like systems:

```bash
sudo apt install libasio-dev
````

## Run the included demo

```bash
hachi main.hachi -go
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
json: "/health", "{\"ok\":true}"
html: "/docs", "<h1>Docs</h1>"
statusText: "/teapot", 418, "I am a teapot"

run: 8080
```

## Notes

- `file:` currently serves raw file bytes and does not infer MIME type yet.
- `run:` uses Crow's multithreaded server mode.
- `runSingle:` is included for simpler debugging.

