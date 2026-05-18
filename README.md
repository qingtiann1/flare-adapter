# flare-adapter

Lightweight Cloudflare bypass proxy using [cloudscraper](https://github.com/venomous/cloudscraper). No browser needed.

Used by [hanime-server](https://github.com/heisenyu/hanime-server) to scrape Cloudflare-protected pages.

## Usage

```bash
docker build -t flare-adapter .
docker run -d -p 7789:7789 flare-adapter
```

### With proxy

```bash
docker run -d -p 7789:7789 -e PROXY_URL=http://proxy:7890 flare-adapter
```

## How it works

Takes HTTP requests with an `x-hostname` header and forwards them through cloudscraper's TLS fingerprint bypass:

```
GET /path HTTP/1.1
x-hostname: target.example.com
→ cloudscraper GET https://target.example.com/path → response
```

## Compare with FlareSolverr

| | flare-adapter | FlareSolverr |
|---|---|---|
| Runtime | Python + cloudscraper | Python + headless Chrome |
| Memory | ~50MB | ~2GB |
| Startup | <1s | ~30s |
| Challenge types | Simple JS, TLS fingerprint | Full browser JS execution |
| When to use | Most CF-protected sites | Sites with advanced CF challenges |

They complement each other. Use flare-adapter for most requests, FlareSolverr as fallback for tougher challenges.
