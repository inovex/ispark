#!/usr/bin/env bash

export EG_KERNEL_LAUNCH_TIMEOUT=120

## start enterprise-gateway server
exec jupyter enterprisegateway --ip=0.0.0.0 --port_retries=0 --port=$GATEWAY_PORT \
--config='/tmp/jupyter_enterprise_gateway_config.py' \
--EnterpriseGatewayApp.yarn_endpoint=http://$HOSTNAME:8088/ws/v1 \
--EnterpriseGatewayApp.alt_yarn_endpoint=http://$HOSTNAME:8088/ws/v1 
--log-level=DEBUG

