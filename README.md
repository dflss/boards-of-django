# Boards of Django

## Table of contents
* [General info](#general-info)
* [Getting started](#getting-started)
* [Testing](#testing)
* [Docs](#docs)
* [Styleguide](#styleguide)
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

Then, view the site at [http://localhost/](http://localhost/)

You can load fixtures to have to initial data to work with:

```
docker-compose exec django python manage.py migrate loaddata fixtures.json
```

Each user in the sample fixtures has a password "password".

## Testing

```
docker-compose exec django pytest
```

## Docs

After building and running the project locally, the documentation can be found at: [http://localhost/swagger/](http://localhost/swagger/). 


## Styleguide

The followed styleguide is the [HackSoft's Django-Styleguide](https://github.com/HackSoftware/Django-Styleguide). However, there is one exception regarding URLs.

In Django-Styleguide, each HTTP method is wrapped in a separate APIView and a separate URL is used for each of these APIViews. Therefore, URLs are built by appending the action's name like this:

```
urlpatterns = [
    path('', CourseListApi.as_view(), name='list'),
    path('<int:course_id>/', CourseDetailApi.as_view(), name='detail'),
    path('create/', CourseCreateApi.as_view(), name='create'),
    path('<int:course_id>/update/', CourseUpdateApi.as_view(), name='update'),
    path(
        '<int:course_id>/specific-action/',
        CourseSpecificActionApi.as_view(),
        name='specific-action'
    ),
]
```

In this project, a different approach is used. For each resource, we can have two types of actions: "list" actions and "detail" actions. "Detail" actions are those that require object id as a url parameter -- for example `update` or `delete`. "List" actions are for example `create` or `list`. Then, a single URL is built for "list" actions and "detail" actions". The action itself is recognized based on the HTTP method instead of explicit URL pattern.

```
urlpatterns = [
    path("", BoardsApi.as_view(), name="boards"),
    path("<int:board_id>/", DetailBoardsApi.as_view(), name="board_detail"),
    path("<int:board_id>/add_admin/", AddAdminsBoardsApi.as_view(), name="board_detail_add_admin"),
]
```

Special actions (such as `add_admin` in the example above) have a separate URL pattern and are defined as a separate APIView.

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
