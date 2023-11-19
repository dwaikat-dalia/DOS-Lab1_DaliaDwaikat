FROM python:latest

WORKDIR /app/catalog

# Copy only necessary files
COPY . /app/catalog

RUN pip install -r catalog_requirements.txt

EXPOSE 5002

CMD python ./index.py
