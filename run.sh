#!/bin/bash
service redis-server start
if [ "$APP_SERVER" = "webagent" ]; then
  python manage.py webagent
elif [ "$APP_SERVER" = "grpc_server" ]; then
  python manage.py grpc_server
else
  if [ "$APP_ENV" = "test" ]; then
    python manage.py app_test
  elif [ "$APP_ENV" = "prod" ]; then
    # export PATH="/root/.local/bin:$PATH"
    # opentelemetry-instrument --traces_exporter otlp_proto_http --metrics_exporter none --service_name techadmin-server --exporter_otlp_traces_endpoint http://tracing-analysis-dc-sh.aliyuncs.com/adapt_c1w9rriv36@abcd270e26d717e_c1w9rriv36@53df7ad2afe8301/api/otlp/traces python manage.py server
    python manage.py server
  else
    python manage.py server
  fi
fi