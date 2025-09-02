FROM python:3.11-slim 
WORKDIR /app 
COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt 
COPY . . 
EXPOSE 5000 47808 5020 4840 
CMD ["python", "main.py"]
