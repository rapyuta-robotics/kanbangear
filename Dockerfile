# Use official Python image as base
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY auth_helpers.py auth.py config.py database.py initdb.py logging_utils.py \
     main.py models.py schemas.py upload_data.py users.py ./
COPY routes/ ./routes/
COPY server/ ./server/
COPY static/ ./static/
COPY templates/ ./templates/
COPY Site_create_html/ ./Site_create_html/

# Create logs directory if it doesn't exist
RUN mkdir -p logs

# Expose the port your application runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

