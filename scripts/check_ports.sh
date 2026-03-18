#!/usr/bin/env bash
# ============================================================
# check_ports.sh — Find available ports before starting
# Usage: bash scripts/check_ports.sh
# ============================================================

PORTS=(8000 5555 6379 5432 9090 3001)
NAMES=(API Flower Redis Postgres Prometheus Grafana)

echo ""
echo "=== TradingBot-IN Port Check ==="
echo ""

declare -A SUGGESTIONS

for i in "${!PORTS[@]}"; do
    PORT="${PORTS[$i]}"
    NAME="${NAMES[$i]}"
    if lsof -iTCP:"$PORT" -sTCP:LISTEN -t &>/dev/null 2>&1; then
        # Find next available port
        NEXT=$((PORT + 1))
        while lsof -iTCP:"$NEXT" -sTCP:LISTEN -t &>/dev/null 2>&1; do
            NEXT=$((NEXT + 1))
        done
        echo "❌  $NAME  — port $PORT is IN USE  →  suggest $NEXT"
        SUGGESTIONS[$NAME]=$NEXT
    else
        echo "✅  $NAME  — port $PORT is free"
        SUGGESTIONS[$NAME]=$PORT
    fi
done

echo ""
echo "=== Suggested .env overrides (copy what you need) ==="
echo ""
echo "API_PORT=${SUGGESTIONS[API]}"
echo "FLOWER_PORT=${SUGGESTIONS[Flower]}"
echo "REDIS_PORT=${SUGGESTIONS[Redis]}"
echo "POSTGRES_PORT=${SUGGESTIONS[Postgres]}"
echo "PROMETHEUS_PORT=${SUGGESTIONS[Prometheus]}"
echo "GRAFANA_PORT=${SUGGESTIONS[Grafana]}"
echo ""
echo "Add any conflicting lines to your .env, then run: docker compose up -d"
echo ""
