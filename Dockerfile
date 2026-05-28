FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LLM_PROVIDER=fake

WORKDIR /app

COPY pyproject.toml README.md ./
COPY app ./app
COPY tests ./tests
COPY scripts ./scripts
COPY docs ./docs
COPY jmeter ./jmeter

RUN python -m pip install --upgrade pip && \
    pip install -e .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
