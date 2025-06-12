# dind_runner/Dockerfile
FROM docker:dind

RUN apk add --no-cache go bash tini curl

RUN mkdir /app
WORKDIR /app
COPY main.go go.mod go.sum /app/

RUN go build -o runner main.go

RUN cat <<'EOF' > /app/start.sh && chmod +x /app/start.sh
#!/bin/bash
set -e

echo "[+] Starting dockerd..."
dockerd-entrypoint.sh &
trap 'kill $(jobs -p)' EXIT

echo "[+] Waiting for Docker daemon to be ready..."
until docker info >/dev/null 2>&1; do
  sleep 0.2
done

echo "[+] Docker is ready. Starting runner..."
exec /app/runner
EOF

HEALTHCHECK --interval=5s --timeout=3s --start-period=10s --retries=3 \
    CMD (docker info > /dev/null && curl -f http://127.0.0.1:8000/health) || exit 1
ENTRYPOINT ["/sbin/tini", "--", "/app/start.sh"]
