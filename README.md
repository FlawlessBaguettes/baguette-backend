# baguette-backend
Backend of the Baguette social media platform.

# Prerequisites

* `python 3`
* `pip version >= 19.0`

# Setting Up The Database

## Download Homebrew

` $ /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"`

## Download Postgres using Homebrew

`brew update
brew install postgresql`

## Creating the database

`createdb flawless_baguettes;`

# Setting Up Environment

## Install virtualenv

`python -m pip install --user virtualenv`

## Create a virtual environment

Go to the projects directory and run the following command

`python -m virtualenv env`

## Activate the virtual environment

`source env/bin/activate`

Note to deactivate run the following command
`deactivate`

## Downloading packages

To download all packages:

`pip install -r requirements.txt`


# Running the Application

## Run the migrations

`python manage.py db upgrade`

## Run the seeds

`python seeds.py`

## Launch the application

Launch the application by running `python app.py`.

The application can be accessed `http://localhost:5000`.