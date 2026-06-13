FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8501 \
    AI_BUILDER_OS_RUNTIME_ROOT=/data \
    AI_BUILDER_OS_LEARNING_RELEASE_PROFILE=external_v2

WORKDIR /app

COPY projects/learning-agent/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY . /app
RUN mkdir -p /data /app/.streamlit \
    && cp projects/learning-agent/.streamlit/config.toml /app/.streamlit/config.toml \
    && chmod +x projects/learning-agent/start.sh

EXPOSE 8501

CMD ["projects/learning-agent/start.sh"]
