#!/bin/bash
prefect cloud login --key $PREFECT_KEY --workspace $PREFECT_WORKSPACE
cd opt/flows
python deploy_blocks.py
python deploy_flows.py
prefect agent start -q default