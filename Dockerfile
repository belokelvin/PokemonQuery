# Dockerfile para Buscador de Pokémon
FROM python:3.11-slim

# Defino variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Crio usuário não-root para segurança
RUN groupadd -r pokemon && useradd -r -g pokemon pokemon

# Defino diretório de trabalho
WORKDIR /app

# Copio arquivo de dependências primeiro (para aproveitar cache do Docker)
COPY requirements.txt .

# Instalo dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copio código da aplicação
COPY Pokemon/ Pokemon/
COPY main.py .

# Altero proprietário dos arquivos
RUN chown -R pokemon:pokemon /app

# Mudo para usuário não-root
USER pokemon

# Exponho porta (caso futuramente seja necessário criar endpoints)
EXPOSE 8000

# Comando padrão para executar os testes
CMD ["python", "main.py"]