# Specifies the base image
FROM python:3.10-slim-buster
# Sets the working directory
WORKDIR /app
# Copy files from the host
COPY . /app/
# Run the linux command; installs packages using requirements.txt file
RUN pip install -r requirements.txt
# Expose ports
EXPOSE 5000
# command for executing the container
CMD ["python", "app.py"]