# Use an official Python runtime as the parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Add the project root to the Python path
ENV PYTHONPATH=/app

# Run the MRA MIP script when the container launches
CMD ["python", "src/mra_mip.py", "--input-dir", "/app/data", "--output-dir", "/app/output"]