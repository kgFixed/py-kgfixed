FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install -y git

RUN pip install --no-cache-dir .

# Ajoute src au PYTHONPATH
ENV PYTHONPATH="/app/src:${PYTHONPATH}"

RUN mkdir -p /workspace
VOLUME /workspace

ENTRYPOINT ["python", "src/py_kgfix_ror/create_ldes_fragment.py"]
# ENTRYPOINT ["python", "src/py_kgfix_ror/__main__.py"]