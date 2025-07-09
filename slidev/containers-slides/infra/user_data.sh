#!/bin/bash
set -e

ls -alh /home/ubuntu/.ssh >/var/log/check_ssh.log 2>&1 || true
cat /home/ubuntu/.ssh/authorized_keys >>/var/log/check_ssh.log 2>&1 || true
# aws ec2 get-console-output --instance-id $(terraform output -raw instance_id) --output text | grep -A20 check_ssh

# Install dependencies
apt-get update
apt-get install -y git nginx certbot python3 python3-certbot-nginx
# docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

sudo systemctl enable docker
sudo systemctl start docker
# Add ubuntu user to docker group
usermod -aG docker ubuntu

# compose
sudo mkdir -p /usr/lib/docker/cli-plugins
sudo curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 -o /usr/lib/docker/cli-plugins/docker-compose
sudo chmod +x /usr/lib/docker/cli-plugins/docker-compose

# Clone repo
workdir="/home/ubuntu/talks/slidev/containers-slides"
sudo -u ubuntu git clone "${repo_url}" /home/ubuntu/talks

# only chown this subdir
chown -R ubuntu:ubuntu /home/ubuntu/talks

# NGINX
cat >/etc/nginx/sites-available/workshop <<'EOF'
server {
    listen 80;
    server_name ${domain} api.${domain};

    # Disable all caching headers
    add_header Cache-Control "no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0";
    add_header Pragma "no-cache";
    add_header Expires "0";

    # WebSocket endpoints
    location /ws {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;

        # Extra no-cache for WebSockets
        proxy_cache off;
        proxy_no_cache 1;
        proxy_cache_bypass 1;
    }

    # Session API endpoints
    location /session {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Disable caching for API
        proxy_cache off;
        proxy_no_cache 1;
        proxy_cache_bypass 1;
    }

    # execution
    location /run {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # add_header Access-Control-Allow-Origin "$http_origin" always;
        # add_header Access-Control-Allow-Credentials "true" always;

        # No cache
        proxy_cache off;
        proxy_no_cache 1;
        proxy_cache_bypass 1;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
    }

    # Slides - if it is ever is hosted on the instance itself, uncomment
    # location / {
    #     proxy_pass http://localhost:3000;
    #     proxy_set_header Host $host;
    #     proxy_set_header X-Real-IP $remote_addr;
    #     proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    #     proxy_set_header X-Forwarded-Proto $scheme;
    #     # No cache for slides fallback
    #     proxy_cache off;
    # }

    # Fallthrough for all other endpoints, in case any are added or
    #   I missed any theres a chance this is sufficient.
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Disable caching for API
        proxy_cache off;
        proxy_no_cache 1;
        proxy_cache_bypass 1;
    }
}
EOF

# Enable NGINX site
ln -sf /etc/nginx/sites-available/workshop /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
systemctl restart nginx

# Build dind-runner image
cd $workdir
pushd dind_runner
docker build -t dind-runner .
popd

# Only start the dind manager service
sudo -u ubuntu docker compose up -d proxy

# Wait for services and get SSL cert
sleep 30
certbot --nginx -d api.${domain} --non-interactive --agree-tos --email mchristiani2017@gmail.com
# If we ever host the slides, also get a cert for root domain
# certbot --nginx -d ${domain} -d api.${domain} --non-interactive --agree-tos --email mchristiani2017@gmail.com

echo "Workshop platform ready at https://${domain}" >/var/log/workshop-ready.log
