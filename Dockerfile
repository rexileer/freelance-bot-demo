FROM python:3.12-slim
WORKDIR /freelance_bot
COPY requirements.txt .
RUN pip install --default-timeout=100 -r requirements.txt
COPY . .
EXPOSE 8000