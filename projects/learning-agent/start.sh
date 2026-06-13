#!/bin/sh
set -eu

mkdir -p /app/.streamlit

if [ "${LEARNING_AGENT_AUTH_MODE:-local}" = "oidc" ]; then
  : "${OIDC_REDIRECT_URI:?OIDC_REDIRECT_URI is required in oidc mode}"
  : "${OIDC_COOKIE_SECRET:?OIDC_COOKIE_SECRET is required in oidc mode}"
  : "${OIDC_CLIENT_ID:?OIDC_CLIENT_ID is required in oidc mode}"
  : "${OIDC_CLIENT_SECRET:?OIDC_CLIENT_SECRET is required in oidc mode}"
  : "${OIDC_SERVER_METADATA_URL:?OIDC_SERVER_METADATA_URL is required in oidc mode}"

  cat > /app/.streamlit/secrets.toml <<EOF
[auth]
redirect_uri = "${OIDC_REDIRECT_URI}"
cookie_secret = "${OIDC_COOKIE_SECRET}"
client_id = "${OIDC_CLIENT_ID}"
client_secret = "${OIDC_CLIENT_SECRET}"
server_metadata_url = "${OIDC_SERVER_METADATA_URL}"
EOF
fi

exec streamlit run projects/learning-agent/src/app.py \
  --server.address=0.0.0.0 \
  --server.port="${PORT:-8501}" \
  --server.headless=true
