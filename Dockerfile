FROM python:3.12

#Update the package lists
RUN apt-get update

COPY . /tasks-api-py-fastapi-postgresql

#Set the working directory in the container
WORKDIR /tasks-api-py-fastapi-postgresql

RUN python -m venv env

ENV VIRTUAL_ENV /env

ENV PATH /env/bin:$PATH

#Install the python dependencies
RUN pip install --no-cache-dir -r requirements.txt

#Run the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "15400"]