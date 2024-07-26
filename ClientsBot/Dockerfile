FROM python:3.12.4-slim

RUN apt-get update && apt-get install -y curl

WORKDIR /app

COPY ./requirements.txt ./
RUN pip install -r requirements.txt
RUN rm ./requirements.txt

COPY src ./src
COPY locale ./locale

RUN pybabel update -i locale/messages.pot -d locale
RUN pybabel compile -f -d locale

ARG bot_token
ARG db_user
ARG db_password
ARG db_name
ARG db_host
ARG db_port
ARG db_name
ARG openai_api_key
ARG json_extractor_assistant_id
ARG sellers_bot_backend_url
ARG payment_provider_terminal
ARG payment_provider_api_name
ARG log_level

ENV bot_token $bot_token
ENV db_user $db_user
ENV db_password $db_password
ENV db_name $db_name
ENV db_host $db_host
ENV db_port $db_port
ENV db_name $db_name
ENV openai_api_key $openai_api_key
ENV json_extractor_assistant_id $json_extractor_assistant_id
ENV sellers_bot_backend_url $sellers_bot_backend_url
ENV payment_provider_terminal $payment_provider_terminal
ENV payment_provider_api_name $payment_provider_api_name
ENV log_level $log_level

CMD python -m src.app
