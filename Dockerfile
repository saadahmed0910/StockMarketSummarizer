# Use the official Playwright image for Python.
# It comes with all browsers and their dependencies pre-installed.
# The version tag 'v1.44.0' should be kept up to date.
FROM mcr.microsoft.com/playwright/python:v1.44.0

# Set the working directory inside the container
WORKDIR /app

# Copy your requirements.txt and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Define the command to run your app
# Make sure to replace `scrapeResults.py` with your main script's name
CMD ["python", "app.py"]