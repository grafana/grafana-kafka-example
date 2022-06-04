#!/bin/bash
#
#
GRAFANA_PROMTAIL_CONFIG_FILE="promtail-config.yml"

_escapeRegex() {
  echo $(printf '%s\n' "$1" | sed 's/[\[\.*^$/]/\\&/g' )
}

_modifyYml() {
  MOD_FILE=$1
  MOD_STR=$(_escapeRegex $2)
  NEW_VAL=$(_escapeRegex $3)
  sed -i '.backup' "s/$MOD_STR/$NEW_VAL/g" $MOD_FILE
}

case "$1" in
  build)
    docker build -t kafka_producer -f kafka_producer.Dockerfile .
  ;;
  configure)
    # Logs
    cp promtail-config-blank.yml $GRAFANA_PROMTAIL_CONFIG_FILE
    _modifyYml $GRAFANA_PROMTAIL_CONFIG_FILE "\${GRAFANA_LOGS_WRITE_URL}"   "$GRAFANA_LOGS_WRITE_URL"
    _modifyYml $GRAFANA_PROMTAIL_CONFIG_FILE "\${GRAFANA_LOGS_USERNAME}"    "$GRAFANA_LOGS_USERNAME"
    _modifyYml $GRAFANA_PROMTAIL_CONFIG_FILE "\${GRAFANA_LOGS_API_KEY}"     "$GRAFANA_LOGS_API_KEY"
    echo "Created: $GRAFANA_PROMTAIL_CONFIG_FILE"
    ;;
  run)
    # For testing kafka_producer
    docker run -i -t kafka_producer
  ;;
  up)
    docker-compose -f docker-compose.yaml up --detach
  ;;
  down)
    docker-compose -f docker-compose.yaml down
  ;;
  start)
    echo "start"
    ;;
  *)
    echo "Command not recognized [$@]"
    echo "Help:"
    echo "  build"
    echo "  configure"
    echo "  up | down"
    ;;
esac
