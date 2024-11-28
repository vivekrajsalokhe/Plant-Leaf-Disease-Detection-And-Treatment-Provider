FROM python:3.10.12

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

ENV NAME PlantDiseaseAnalyzer

CMD ["python3", "app.py"]