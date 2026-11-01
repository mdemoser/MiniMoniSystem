#!/bin/bash

# 1. Coleta Uso de Disco
DISK_USAGE=$(df -P / | tail -n 1 | awk '{print $5}' | tr -d '%')

# 2. Coleta Uso de RAM
RAM_USAGE=$(free -m | awk '/Mem/ {print int($3/$2 * 100)}')

# 3. Verificação do Serviço
SERVICE_NAME="squid"
SERVICE_STATUS=$(systemctl is-active "$SERVICE_NAME" 2>/dev/null)

if [ -z "$SERVICE_STATUS" ]; then
    SERVICE_STATUS="inactive"
fi

# 4. Timestamp ISO 8601
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# 5. Gera arquivo JSON
cat <<EOF > /tmp/metrics.json
{
  "timestamp": "$TIMESTAMP",
  "disk_usage_percent": ${DISK_USAGE:-0},
  "ram_usage_percent": ${RAM_USAGE:-0},
  "service_monitored": "$SERVICE_NAME",
  "service_status": "$SERVICE_STATUS"
}
EOF

echo "[OK] Métricas coletadas em $(date)"
