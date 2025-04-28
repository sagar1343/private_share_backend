FROM python:3.13-alpine

RUN adduser -D developer

WORKDIR /app

RUN pip install --upgrade pip 

RUN pip install pipenv

COPY Pipfile Pipfile.lock /app/

RUN pipenv install --system

COPY . .

RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "private_share.wsgi:application" ]