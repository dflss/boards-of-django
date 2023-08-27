# Base image contains the dependencies and no application code
FROM python:3.10-alpine as base

ENV DIST_DIR /usr/src/app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR $DIST_DIR

RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev bash libffi-dev \
    jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev \
    tcl-dev

COPY ./docker/django/entrypoint.sh /usr/src/entrypoint.sh
COPY requirements.txt ${DIST_DIR}/requirements.txt
COPY dev-requirements.txt ${DIST_DIR}/dev-requirements.txt
RUN pip install -r ${DIST_DIR}/requirements.txt -r ${DIST_DIR}/dev-requirements.txt

ENTRYPOINT ["/usr/src/entrypoint.sh"]

# Production image inherits from base and adds application code
FROM base as production

# Copy code
COPY . ${DIST_DIR}

RUN python manage.py collectstatic --no-input

CMD ["gunicorn", "config.wsgi:application", "--workers", "2", "--bind", "0.0.0.0:8000"]
