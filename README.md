
<p align="center">
  <img src="images/inugami-mascot.png" alt="Inugami mascot" width="50%">
</p>

# Inugami

Inugami is an experimental web framework for Hachi focused on lightweight HTTP services, APIs, and native server-side apps.

## What is included

- `hMods/inugami.🐺` - the full Inugami framework module
- `main.hachi` - ready-to-run demo app
- `examples/` - smaller examples you can study or adapt
- `pages/sample_api_page.html` - sample static page for `file:` routes

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

## Quick start

A minimal Inugami app looks like this:

```hachi
>@"inugami"

setLogLevel: 1

get: "/", "Hello from Inugami"
json: "/health", "{\"ok\":true}"
html: "/docs", "<h1>Docs</h1>"
statusText: "/teapot", 418, "I am a teapot"

run: 8080
```

## API reference

### `setLogLevel: <level>`

Sets the framework log verbosity.

Accepted levels:

- `0` - debug
- `1` - info
- `2` - warning
- `3` - error
- `4` - critical

Example:

```hachi
setLogLevel: 1
```

---

### `get: <path>, <body>`

Registers a `GET` route that returns plain text.

Arguments:

- `path` - route path, such as `"/"` or `"/hello"`
- `body` - plain-text response body

Example:

```hachi
get: "/", "Hello from Inugami"
```

---

### `html: <path>, <body>`

Registers a `GET` route that returns HTML.

Arguments:

- `path` - route path
- `body` - HTML response body

Example:

```hachi
html: "/docs", "<h1>Inugami</h1><p>Docs page</p>"
```

---

### `json: <path>, <body>`

Registers a `GET` route that returns JSON.

Arguments:

- `path` - route path
- `body` - JSON response body as a string

Example:

```hachi
json: "/health", "{\"ok\":true}"
```

---

### `statusText: <path>, <status>, <body>`

Registers a `GET` route that returns plain text with an explicit HTTP status code.

Arguments:

- `path` - route path
- `status` - numeric HTTP status code
- `body` - plain-text response body

Example:

```hachi
statusText: "/teapot", 418, "I am a teapot"
```

---

### `statusHtml: <path>, <status>, <body>`

Registers a `GET` route that returns HTML with an explicit HTTP status code.

Arguments:

- `path` - route path
- `status` - numeric HTTP status code
- `body` - HTML response body

Example:

```hachi
statusHtml: "/missing", 404, "<h1>404</h1><p>Not found.</p>"
```

---

### `statusJson: <path>, <status>, <body>`

Registers a `GET` route that returns JSON with an explicit HTTP status code.

Arguments:

- `path` - route path
- `status` - numeric HTTP status code
- `body` - JSON response body as a string

Example:

```hachi
statusJson: "/api/error", 500, "{\"ok\":false}"
```

---

### `redirect: <path>, <target>`

Registers a `GET` route that redirects to another location.

Arguments:

- `path` - source route path
- `target` - redirect destination

Example:

```hachi
redirect: "/home", "/"
```

Using `curl -i` is helpful for seeing the redirect headers:

```bash
curl localhost:8080/home -i
```

---

### `file: <route>, <filePath>`

Registers a `GET` route that serves a file from disk.

Arguments:

- `route` - route path to expose
- `filePath` - local file path to read and return

Example:

```hachi
file: "/landing", "pages/sample_api_page.html"
file: "/images/inugami-mascot.png", "images/inugami-mascot.png"
```

This is useful for static HTML pages, images, JSON fixtures, and other simple assets.

Current behavior:

- returns raw file bytes
- returns `404` with `file not found` if the file cannot be opened
- does **not** infer MIME type yet

That means HTML, PNG, JSON, and other files can be served, but content type headers are not yet automatically set.

---

### `post: <path>, <body>`

Registers a `POST` route that returns plain text.

Arguments:

- `path` - route path
- `body` - plain-text response body


Example:

```hachi
post: "/submit", "posted ok"
```

Test it with:

```bash
curl -X POST localhost:8080/submit
```

---

### `postJson: <path>, <body>`

Registers a `POST` route that returns JSON.

Arguments:

- `path` - route path
- `body` - JSON response body as a string

Example:

```hachi
postJson: "/save", "{\"saved\":true}"
```

Test it with:

```bash
curl -X POST localhost:8080/save
```

---

### `run: <port>`

Starts the Inugami server on the given port using multithreaded server mode.

Arguments:

- `port` - port number to bind to

Example:

```hachi
run: 8080
```

This is the normal mode you will usually want.

---

### `runSingle: <port>`

Starts the Inugami server on the given port using single-threaded mode.

Arguments:

- `port` - port number to bind to

Example:

```hachi
runSingle: 8080
```

This is useful for simpler debugging and more predictable local behavior.

## Full example

```hachi
>@"inugami"

setLogLevel: 1

get: "/", "Inugami is alive"
json: "/health", "{\"ok\":true}"
json: "/version", "{\"framework\":\"Inugami\",\"lang\":\"Hachi\"}"
html: "/docs", "<h1>Inugami</h1><p>Experimental Hachi web framework.</p>"
statusText: "/teapot", 418, "I am a teapot"
statusHtml: "/missing", 404, "<h1>404</h1><p>Nothing here.</p>"
redirect: "/home", "/"
file: "/landing", "pages/sample_api_page.html"
file: "/images/inugami-mascot.png", "images/inugami-mascot.png"
post: "/submit", "posted ok"
postJson: "/save", "{\"saved\":true}"

run: 8080
```

## Notes

- `file:` currently serves raw file bytes and does not infer MIME type yet.
- `run:` uses multithreaded server mode.
- `runSingle:` is included for simpler debugging.
- `json:` and `postJson:` expect valid JSON as a string literal.
- To reference images from HTML pages served by Inugami, expose them with a matching `file:` route.
