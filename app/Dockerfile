FROM python:3.10-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt
COPY ./main.py /code/main.py
EXPOSE 80
CMD ["streamlit", "run", "main.py", "--server.port=80", "--server.address=0.0.0.0"]