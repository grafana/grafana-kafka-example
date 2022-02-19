# grafana-kafka-example
Example integration of a Kafka Producer, Kafka Broker and Promtail producing test data to Grafana Cloud Logs, see [architecture](https://github.com/grafana/grafana-kafka-example/blob/main/architecture1.png)

Requires Docker and Docker Compose

## Configure the environment variables

Configure the environment variables below from your Grafana Cloud Account Logs Data Source settings:

1. Log into your [Grafana Cloud account](https://grafana.com/auth/sign-in) to access the Cloud Portal
2. Select the **Loki Send Logs** to set up and manage the Loki logging service from the [Cloud Portal](https://grafana.com/docs/grafana-cloud/fundamentals/cloud-portal/)
3. From the **Grafana Data Source setting for Logs**, use the hostname of the **URL**, the **User** and **Password** in the following environment variables:

Edit the file: ```envvars-grafana-cloud-stack1.sh```

```
export GRAFANA_LOGS_HOST="logs-prod-us-central1.grafana.net"
export GRAFANA_LOGS_USERNAME="123456"
export GRAFANA_LOGS_API_KEY="eyJrIjoi...."
```
## Configure Promtail
```
source envvars-grafana-cloud-stack1.sh
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

Import the example dashboard ```dashboard-example-1.json``` into Grafana and configure the Logs Data Source

## Stop the containers
```
./ctl.sh down
```
