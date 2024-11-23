FROM python:3-alpine
# An argument needed to be passed
ARG SECRET_KEY
ARG ALLOWED_HOSTS=127.0.0.1,localhost

WORKDIR /app/polls

# Set needed settings
ENV SECRET_KEY=${SECRET_KEY}
ENV DEBUG=True
ENV TIMEZONE=UTC
ENV ALLOWED_HOSTS=${ALLOWED_HOSTS:-127.0.0.1,localhost}

# Test for secret key
RUN if [ -z "$SECRET_KEY" ]; then echo "No secret key specified in build-arg"; exit 1; fi

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Running Django functions in here is not good!
# Apply migrations
#RUN python ./manage.py migrate

# Apply fixtures
#RUN python ./manage.py loaddata data/polls-v4.json
#RUN python ./manage.py loaddata data/users.json
#RUN python ./manage.py loaddata data/votes-v4.json

# Create superuser
#RUN python ./manage.py createsuperuser --username admin1 --email admin@example.com --noinput


RUN chmod +x ./entrypoint.sh

EXPOSE 8000
# Run application
CMD [ "./entrypoint.sh" ]

#  docker build -t ku-polls . --build-arg SECRET_KEY=***
#  docker run --rm -d -p 8000:8000 ku-polls
