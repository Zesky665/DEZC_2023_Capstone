prefect cloud login --key $PREFECT_KEY --workspace $PREFECT_WORKSPACE
python opt/flows/deploy_blocks.py
python opt/flows/deploy_flows.py