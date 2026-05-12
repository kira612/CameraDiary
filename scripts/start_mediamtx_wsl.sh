#!/usr/bin/env bash
set -euo pipefail

mediamtx_bin="${1:-/home/kirataiki/apps/vendor/mediamtx/mediamtx}"
mediamtx_config="${2:-/home/kirataiki/apps/config/mediamtx.yml}"

exec "$mediamtx_bin" "$mediamtx_config"
