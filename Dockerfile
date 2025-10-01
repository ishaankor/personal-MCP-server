FROM python:3.12-slim

WORKDIR /app

RUN pip install uv 

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
 
ENV MCP_HTTP_PORT=8000
ENV MCP_HTTP_HOST=0.0.0.0

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 CMD curl --fail http://localhost:8000/health || exit 1

CMD ["uv", "run", "main.py"]
