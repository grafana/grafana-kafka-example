# grafana-kafka-example
Example integration of a Kafka Producer, Kafka Broker and Promtail producing test data to Grafana Cloud Logs

## Configure the environment variables 

Configure the environment variables below from your Grafana Cloud Account Logs Data Source settings, see [Create a Grafana Cloud API Key](https://grafana.com/docs/grafana-cloud/reference/create-api-key/)

File: envvars-grafana-cloud-stack1.sh

```
export GRAFANA_LOGS_URL="https://logs-prod-us-central1.grafana.net/loki/api/v1/push"
export GRAFANA_LOGS_USERNAME="123456"
export GRAFANA_LOGS_API_KEY="eyJrIjoi...."
```
## Configure Promtail
```
./ctl.sh configure
```
Check the file ```promtail-config.yml``` now has the correct _LOGS_ credentials
## Build the Docker container for the Kafka Producer
```
./ctl.sh build
```
## Start the containers using Docker Compose
```
./ctl.sh up
```
This will start the containers: zookeeper, kafka, producer and promtail
## Validate logs are being sent to Grafana Cloud Logs

Using the Logs Data Source and [LogQL](https://grafana.com/docs/loki/latest/logql/) Check for log messages under the labels: ```{job="kafka"}``` and ```{job="varlogs"}```
## Stop the containers
```
./ctl.sh down
```

