[![Build Status](https://travis-ci.org/betsybeth/BrightEvents_API.svg?branch=develop)](https://travis-ci.org/betsybeth/BrightEvents_API)
[![Coverage Status](https://coveralls.io/repos/github/betsybeth/BrightEvents_API/badge.svg?branch=develop)](https://coveralls.io/github/betsybeth/BrightEvents_API?branch=develop)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/48a794b0171a4762a60132e3026d5879)](https://www.codacy.com/app/betsybeth/BrightEvents_API?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=betsybeth/BrightEvents_API&amp;utm_campaign=Badge_Grade)
[![Code Health](https://landscape.io/github/betsybeth/BrightEvents_API/develop/landscape.svg?style=flat)](https://landscape.io/github/betsybeth/BrightEvents_API/develop)

# BrightEvents_API
BrightEvents_API lets you create, update, delete events.

#### Introduction
 Bright Events API has database for persistance data.


#### Getting started
* To start using BrightEvent_API:
  * git clone:
    * `https://github.com/betsybeth/BrightEvents_API.git`
  * change directory to:
    * `cd BrightEvents_API`

#### Pre-requisites:
* flask
* Postgresql

#### Setting
* First install the virtual environment globally:
 * `sudo pip install virtualenv`
* create the virtual env and .env file to store your env variables:
 * `virtualenv --python=python3 myenv`
 * .env should be:
    * source ../env/bin/activate
    * export FLASK_APP="run.py"
    * export SECRET_KEY="it_is_awesome"
    * export APP_SETTINGS=".development"
    * export DATABASE_URL="postgresql://localhost/flask_api"
  * Run the manage.py using this commands:
    * `python manage.py db init`
    * `python manage.py db migrate`
    *  `python manage.py db upgrade`

 #### Flask API endpoints

| Endpoints                                       |       Functionality                  |
| ------------------------------------------------|:------------------------------------:|
| `POST /register`                                |  registers a user                    |
| `POST /login`                                   |  login a user                        |   
| `POST /create_event`                            |  create an event                     |
| `GET  /events/<eventId>/`                       |  get a single event                  |
| `GET /events`                                   |  Retrieves an event                  |
| `PUT /events/<eventId>/`                        |  updates an event                    |
| `DELETE /events/<eventId>/`                     |  deletes an event                    |
| `POST /events/<id>/create_rsvp/`                |  create an rsvp                      |
| `GET  /events/<int:id>/rsvps/rsvpId>/`          |  get a single rsvp                   |
| `GET /events/<id>/rsvps/`                       |  retrieves an rsvp                   |
|` PUT /events/<int:id>/rsvps/rsvpId>/`           |  updates an rsvp                     |
|` DELETE /events/<int:id>/rsvps/rsvpId/`         |  delete an rsvp                      |
|` POST logout`                                   |  logout a user                       |
| `POST reset-password`                           |  reset password for a registered user|
| `POST change-password`                          | change and existing  password        |


#### Run it
* run the server:
  * python manage.py runserver
  * test with postman

#### Credits
* [beth][1]

[1]: `https://github.com/betsybeth`
