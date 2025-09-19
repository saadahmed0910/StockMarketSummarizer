# Use a Python base image. We're using a specific version (3.11)
# that is known to work with Playwright to avoid version issues.
FROM python:3.11-slim
# Install system-level dependencies for running a browser.
# These are the libraries that Playwright's browser engines need to function.



RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxcb1 \
    libxkbcommon0 \
    libatspi2.0-0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2

# Set the working directory inside the container. This is where your code will live.
WORKDIR /app

# Copy the requirements file and install the Python packages.
# We do this first so Docker can use a cached layer if requirements.txt doesn't change.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install the Playwright browsers. This is the crucial step that fixes your error.
RUN playwright install

# Copy all the rest of your project's files into the container.
COPY . .

# Set the command to run your application.
# Make sure to replace `your_app.py` with the name of your main Python file.
CMD ["python", "app.py"]