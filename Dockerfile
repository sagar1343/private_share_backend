FROM python:3.13-alpine

RUN adduser -D developer

WORKDIR /app

RUN pip install --upgrade pip 

RUN pip install pipenv

COPY Pipfile Pipfile.lock /app/

RUN pipenv install --system

COPY . .

CMD ["uvicorn", "private_share.asgi:application" ,"--host", "0.0.0.0", "--port","8000"]