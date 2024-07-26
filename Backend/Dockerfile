FROM python:3.12.4-slim

RUN apt-get update && apt-get install -y curl

WORKDIR /app

COPY ./requirements.txt ./
RUN pip install -r requirements.txt
RUN rm ./requirements.txt

COPY src ./src

ARG db_user
ARG db_password
ARG db_name
ARG db_host
ARG db_port
ARG backend_host
ARG backend_port
ARG sellers_bot_host
ARG sellers_bot_port
ARG clients_bot_host
ARG clients_bot_port
ARG environment
ARG backend_access_token
ARG log_level

ENV db_user $db_user
ENV db_password $db_password
ENV db_name $db_name
ENV db_host $db_host
ENV db_port $db_port
ENV backend_host $backend_host
ENV backend_port $backend_port
ENV sellers_bot_host $sellers_bot_host
ENV sellers_bot_port $sellers_bot_port
ENV clients_bot_host $clients_bot_host
ENV clients_bot_port $clients_bot_port
ENV environment $environment
ENV backend_access_token $backend_access_token
ENV log_level $log_level

CMD python -m src.main
