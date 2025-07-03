# Use an official Python runtime as a parent image
FROM python:3.11-slim

RUN groupadd -r web --gid=2001 && \
    useradd -r -g web --uid=2001 -d /code -k /emptydir -m web && \
    mkdir -p /code && \
    chown -R web:web /code

ENV PYTHONPATH="/code"

# Set working directory to root (not recommended for security, but as requested)
WORKDIR /code

# Copy the application code along with the requirements file into the container
# (Create this file if you don't have one yet)
COPY . /code

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the app runs on
EXPOSE 8000

ENTRYPOINT ["/code/docker/entrypoint.sh"]

USER web

# Command to run the application
CMD ["uvicorn"]
