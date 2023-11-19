FROM python:latest

WORKDIR /app/front

# Copy only necessary files
COPY . /app/front

RUN pip install -r front_requirements.txt

EXPOSE 5000

CMD python index.py
