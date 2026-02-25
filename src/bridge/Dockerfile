FROM python:3.11-slim

WORKDIR /app

COPY ../Ronaldinho.NeuralCore.Python/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bridge.py"]
