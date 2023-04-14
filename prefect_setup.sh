#!/bin/bash
prefect cloud login --key $PREFECT_KEY --workspace $PREFECT_WORKSPACE
az login --service-principal --username $AZURE_CLIENT_ID --password $AZURE_CLIENT_SECRET --tenant $AZURE_TENANT_ID
cd opt/flows
python deploy_blocks.py
python deploy_flows.py
prefect agent start -q default