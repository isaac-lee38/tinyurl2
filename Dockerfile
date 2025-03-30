# This tells docker how to build the container. 
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /usr/src/app

COPY requirements.txt .
# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt
# Copy the current directory contents into the container
COPY . .

ENV FLASK_APP=app.py

CMD ["python", "app.py"]
