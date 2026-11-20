# syntax=docker/dockerfile:1

# Alpine keeps the image small; Node 22 is the current LTS line.
FROM node:22-alpine

ENV NODE_ENV=production

WORKDIR /app

# Dependencies are copied and installed on their own so Docker can cache this
# layer: it is only rebuilt when package.json changes, not on every code edit.
COPY --chown=node:node package*.json ./
RUN npm install --omit=dev && npm cache clean --force

COPY --chown=node:node express.js ./

# The app listens on 4567 (see express.js). EXPOSE documents that; the port is
# actually published by compose.yaml.
EXPOSE 4567

# Drop root: the official image ships an unprivileged "node" user.
USER node

# Lets compose and orchestrators see whether the app is actually serving.
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -q -O /dev/null http://127.0.0.1:4567/ || exit 1

# Exec form, so node runs as PID 1 and receives SIGTERM on "docker compose down".
CMD ["node", "express.js"]
