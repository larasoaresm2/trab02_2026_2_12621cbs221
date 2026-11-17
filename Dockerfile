FROM python:3.12-slim

# Do not write .pyc files and show print() output immediately
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Security patches from Debian for the packages in the base image (S5_15)
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Dependencies first: this layer is reused while requirements.txt does not change
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY asset_inventory/ asset_inventory/

# Least privilege: run as a regular user, not root
RUN useradd --create-home appuser && mkdir -p /app/data && chown appuser /app/data
USER appuser

# Healthy = the saved data can be loaded through the Inventory rules
HEALTHCHECK --interval=1m --timeout=10s \
    CMD python -c "from asset_inventory.inventory import Inventory; from asset_inventory.storage import JsonStorage; JsonStorage('data').load(Inventory())"

CMD ["python", "main.py"]