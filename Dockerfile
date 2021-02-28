FROM python:latest

# Create app directory
WORKDIR /app

# Install app dependencies
COPY src/requirements.txt ./

RUN pip install -r requirements.txt
RUN python -m textblob.download_corpora

# Bundle app source
COPY src /app

EXPOSE 8080
CMD [ "python", "server.py" ]