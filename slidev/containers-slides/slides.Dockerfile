FROM oven/bun:latest

RUN apt-get update && apt-get install -y \
    python3 \
    make \
    g++ \
 && ln -s /usr/bin/python3 /usr/bin/python \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /slides
EXPOSE 3000

# COPY package.json bun.lock ./
# RUN bun install
# Im impatient
# RUN --mount=type=bind,src=node_modules,target=node_modules bun install



# # Prod
# COPY . .
# RUN bunx slidev build
CMD ["sh", "-c", "bun install && bunx slidev build && bunx serve -s dist -l 3000"]

# Dev
# CMD ["sh", "-c", "bun run slidev --port 3000 --remote"]
