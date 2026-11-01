#!/usr/bin/env python3
import json
import sys
import os
import tempfile

METRICS_FILE = "/tmp/metrics.json"

# Pega o caminho absoluto da pasta onde o script está rodando
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_STATUS_FILE = os.path.join(SCRIPT_DIR, "status.json")

DISK_CRITICAL_THRESHOLD = 80
RAM_WARNING_THRESHOLD = 75

def load_metrics(filepath):
    if not os.path.exists(filepath):
        print(f"[ERRO] Arquivo '{filepath}' não encontrado.")
        sys.exit(1)
    with open(filepath, 'r') as f:
        return json.load(f)

def analyze_health(data):
    alerts = []
    status = "OK"

    disk = data.get("disk_usage_percent", 0)
    ram = data.get("ram_usage_percent", 0)
    service_name = data.get("service_monitored", "squid")
    service_status = data.get("service_status", "unknown")

    if disk >= DISK_CRITICAL_THRESHOLD:
        status = "CRITICAL"
        alerts.append(f"Disco crítico: {disk}% ocupado (Limite: {DISK_CRITICAL_THRESHOLD}%).")

    if ram >= RAM_WARNING_THRESHOLD:
        if status != "CRITICAL":
            status = "WARNING"
        alerts.append(f"Uso elevado de RAM: {ram}% (Limite: {RAM_WARNING_THRESHOLD}%).")

    if service_status != "active":
        status = "CRITICAL"
        alerts.append(f"Serviço '{service_name}' está inativo ou fora do ar!")

    return status, alerts

def export_web_data(data, status, alerts):
    web_payload = {
        "timestamp": data.get("timestamp"),
        "status": status,
        "disk_usage": data.get("disk_usage_percent"),
        "ram_usage": data.get("ram_usage_percent"),
        "service_name": data.get("service_monitored"),
        "service_status": data.get("service_status"),
        "alerts": alerts
    }

    # Criar um arquivo temporário na mesma pasta e depois renomear (Escrita Atômica)
    temp_file = OUTPUT_STATUS_FILE + ".tmp"
    with open(temp_file, 'w') as f:
        json.dump(web_payload, f, indent=2)

    # O SO faz a troca em milissegundos sem deixar o arquivo 'vazio' para o navegador
    os.replace(temp_file, OUTPUT_STATUS_FILE)

    print(f"[OK] Arquivo 'status.json' gerado com sucesso em: {OUTPUT_STATUS_FILE}")

# BLOCO QUE FALTAVA: Chama as funções na ordem correta ao executar o script
if __name__ == "__main__":
    metrics = load_metrics(METRICS_FILE)
    status, alerts = analyze_health(metrics)
    export_web_data(metrics, status, alerts)