FROM python:3.10-alpine

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev bash libffi-dev \
    jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev \
    tcl-dev

COPY ./entrypoint.sh /usr/src/
COPY ./wait-for-it.sh /usr/src/
RUN chmod +x /usr/src/wait-for-it.sh

ENTRYPOINT ["/usr/src/entrypoint.sh"]
