FROM python:3.10.4-slim-bullseye

COPY docker_setup.sh .

RUN chmod +x docker_setup.sh

RUN ./docker_setup.sh

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY start_agent.sh .

RUN chmod +x start_agent.sh

COPY prefect_setup.sh .

RUN chmod +x prefect_setup.sh

RUN mkdir root/.dbt

RUN mkdir root/.aws

RUN touch root/.aws/config

RUN touch root/.aws/credentials

COPY flows opt/flows

RUN touch opt/flows/__init__.py

RUN touch opt/__init__.py

RUN touch __init__.py

ENTRYPOINT ["./prefect_setup.sh"]




