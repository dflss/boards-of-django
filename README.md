# Boards of Django

## Table of contents
* [General info](#general-info)
* [Getting started](#getting-started)
* [Testing](#testing)
* [How to contribute](#how-to-contribute)
* [Status](#status)

## General info
The aim of the project is to provide an API for a discussion website that is supposed to mimic Reddit.

## Getting started

Boards of Django works with [Python 3](https://www.python.org/downloads/), on any platform. It is required to install [docker](https://docs.docker.com/get-docker/) and [docker-compose](https://docs.docker.com/compose/install/).

To get started with Boards of Django, first create .env file. Example file content can be found in .env.example. Then run the following:

```
docker-compose up --build
docker-compose exec django python manage.py migrate
```

Then, view the site at http://localhost/

## Testing

```
docker-compose exec django pytest
```

## How to contribute

Contributions are welcome. For major changes, please open an issue first to discuss what you would like to change.

See the guidelines below:

1. Fork and clone the repository.
2. Create a new branch using convention `{work type e.g. feature, refactor, bugfix}/{2-3 word summary}`.
3. Push to your fork. Please make sure to update tests as appropriate.
4. Submit a pull request using PR template.
5. Wait for your pull request to be reviewed and merged.
6. Once your pull request is accepted, remember to use squash commit when merging to dev branch. The squash commit should follow the [conventional commits specification](https://www.conventionalcommits.org/en/v1.0.0-beta.2/).


## Status
Project is in progress.
