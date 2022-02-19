# Grafana Cloud Configuration

# Loki Remote Endpoint
# See: https://grafana.com/docs/loki/latest/api/
export GRAFANA_LOGS_HOST="logs-prod-us-central1.grafana.net"
export GRAFANA_LOGS_USERNAME="123456"
export GRAFANA_LOGS_API_KEY="eyJrIjoi...."
#
export GRAFANA_LOGS_QUERY_URL="https://$GRAFANA_LOGS_HOST/loki/api/v1"
export GRAFANA_LOGS_WRITE_URL="https://$GRAFANA_LOGS_HOST/loki/api/v1/push"

# Prometheus Remote Endpoint
# See: https://grafana.com/docs/grafana-cloud/metrics-prometheus/
export GRAFANA_METRICS_HOST="prometheus-prod-10-prod-us-central-0.grafana.net"
export GRAFANA_METRICS_USERNAME="123456"
export GRAFANA_METRICS_API_KEY="eyJrIjoi...."
#
export GRAFANA_METRICS_QUERY_URL="https://$GRAFANA_METRICS_HOST/api/prom/api/v1"
export GRAFANA_METRICS_WRITE_URL="https://$GRAFANA_METRICS_HOST/api/prom/push"
