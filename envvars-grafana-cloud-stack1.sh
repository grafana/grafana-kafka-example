# Grafana Cloud Configuration

# Loki Remote Write Endpoint
# See: https://grafana.com/docs/loki/latest/api/
export GRAFANA_LOGS_URL="https://logs-prod-us-central1.grafana.net/loki/api/v1/push"
export GRAFANA_LOGS_USERNAME="123456"
export GRAFANA_LOGS_API_KEY="eyJrIjoi...."

# Prometheus Remote Write Endpoint
# See: https://grafana.com/docs/grafana-cloud/metrics-prometheus/
export GRAFANA_METRICS_URL="https://prometheus-prod-10-prod-us-central-0.grafana.net/api/prom/push"
export GRAFANA_METRICS_USERNAME="123456"
export GRAFANA_METRICS_API_KEY="eyJrIjoi...."
