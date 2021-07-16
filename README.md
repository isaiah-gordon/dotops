# dotops

An API that allows multiple [floor-board](https://github.com/isaiah-gordon/floor-board) clients to transfer sales data between McDonald's locations. 

> **dotops uses [Flask](https://flask.palletsprojects.com/en/2.0.x/) to manage requests and store data in a MySQL database.**

dotops can also send automated email reports of product sales performance.

- [dotops](#dotops)
  - [Setup](#setup)
    - [Configure](#configure)
    - [Database](#database)


## Setup
dotops has been tested and designed to run on [Google App Engine](https://cloud.google.com/appengine).

### Configure
dotops requires an `app.yaml` file in order to run.

**Example of app.yaml:**
```
runtime: python38

entrypoint: gunicorn -b :$PORT main:app

instance_class: F1

env_variables:
  # Secret for creating JSON web tokens:
  secret_key: 'SECRET_GOES_HERE'

  # MySQL server credentials:
  database_user: root
  database_password: PASSWORD_GOES_HERE
  database_host: IP_GOES_HERE

  # SMTP account for automated email reports:
  email_address: EMAIL_GOES_HERE
  email_password: PASSWORD_GOES_HERE
```

### Database
dotops will try to connect to a MySQL database with the name `database1` using the credentials provided in `app.yaml`.

#### Database Tables

`store_profiles`

| store_number  | email | total_games_won | store_name | store_short_name | store_image |
| ------------- |:-----:|:---------------:|:----------:|:----------------:|:-----------:|

`scheduled_games`

| id  | status | day_of_week | start_time | end_time | product | stores | total_sold0 | transactions0 | total_sold1 | transactions1 | total_sold2 | transactions2 |
| --- |:------:|:-----------:|:----------:|:--------:|:-------:|:------:|:-----------:|:-------------:|:-----------:|:-------------:|:-----------:|:-------------:|

`game_records`

| id  | date | start_time | end_time | product | stores | total_sold0 | transactions0 | total_sold1 | transactions1 | total_sold2 | transactions2 |
| --- |:----:|:----------:|:--------:|:-------:|:------:|:-----------:|:-------------:|:-----------:|:-------------:|:-----------:|:-------------:|

`email_front_page`

| id  | type | status | subject | source |
| --- |:----:|:------:|:-------:|:------:|

`email_advice`

| title  | status | image | text |
| ------ |:------:|:-----:|:----:|

`product_catalogue`

| product  | name |
| -------- |:----:|

