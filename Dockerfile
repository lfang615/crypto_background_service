FROM python:3.11.1

WORKDIR /app

# Install FastAPI dependencies
COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY ./app /app/app

# Expose the port on which the application will run
EXPOSE 5000

# Start the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]
