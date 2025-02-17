# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV BOT_TOKEN=8184177184:AAH0nl6KHpNixXRuIZwm0ubrQYEDoW-6R94

# Run bot.py when the container launches
CMD ["python", "bot.py"]
