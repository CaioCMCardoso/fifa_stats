FROM python:3.12-slim

# Evita bytecode e melhora logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# deps primeiro (melhor cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copia o projeto
COPY . .

# cria pastas de runtime (CSV e logs)
RUN mkdir -p /app/data /app/logs

# expõe a porta da API
EXPOSE 8000

# defaults (podem ser sobrescritos no docker run ou no compose)
ENV ENV=DES
ENV DEBUG=false
ENV TESTING=false
ENV CSV_PATH=/app/data/player_stats.csv
ENV LOG_LEVEL=INFO
ENV LOGFILE_PATH=/app/logs/app.log

# start
CMD ["python", "-m", "fifa_stats"]