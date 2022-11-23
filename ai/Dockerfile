FROM python:3.10-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt
COPY ./main.py /app/main.py
COPY ./artifacts /app/artifacts
EXPOSE 80
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]