FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY ticket_agent ./ticket_agent
COPY api ./api
COPY ui ./ui
COPY .streamlit ./.streamlit
RUN python -m pip install --no-cache-dir ".[ui]"
COPY data ./data
RUN ticket train && useradd --create-home --uid 10001 ticket && mkdir -p /app/var && chown -R ticket:ticket /app/var
ENV HOME=/home/ticket STREAMLIT_BROWSER_GATHER_USAGE_STATS=false STREAMLIT_SERVER_HEADLESS=true
USER ticket
EXPOSE 8000 8501
CMD ["ticket", "serve", "--host", "0.0.0.0"]
