# Usa Python slim come base per mantenere l'immagine leggera
FROM python:3.12-slim

# Crea una directory di lavoro nel container
WORKDIR /barattApp

# Copia i file dal progetto al container
COPY . .

# Installa le dipendenze necessarie
RUN pip install --no-cache-dir -r requirements.txt

# Espone la porta usata da Flask
EXPOSE 5000

# Variabili d'ambiente per il funzionamento di Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Comando di default per avviare l'app
CMD ["flask", "run"]
