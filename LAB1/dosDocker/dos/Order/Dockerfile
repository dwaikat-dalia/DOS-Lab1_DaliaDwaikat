FROM python:latest

WORKDIR /app/order

# Copy only necessary files
COPY . /app/order

RUN pip install -r order_requirements.txt

EXPOSE 5003

CMD python index.py
