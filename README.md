# ListenLocal

Listen Local is a small web app creates a Spotify playlist for you consisting of all the artists playing near you. Discover shows you might have missed by listening to the top song of everyone playing a show.

## Prerequisites
* python3
* virtualenv

## Getting Started

### Install and run local

Download the repo and setup the environment:
```bash
git clone https://github.com/pgrauman/listen-local-app.git
cd listen-local-app

# Make and activate environment
make develop
source .venv/bin/activate
```

Copy `dummy_config.py` to `copy_config.py`. Then fill in your own information (API credentials, app secret key). Don't worry `config.py` is already in `.gitignore`

```bash
cp dummy_config.py copy_config.py
vim copy_config.py
```

Once it's all setup you can launch with the Makefile and visit on your localhost (address displayed on launch)

```bash
$ make launch-app
```

## Deployment

This app was originally launched to a `t2.micro` EC2 instance on AWS using Elastic Beanstalk. To deploy with this method:
1. Setup your Elastic Beanstalk app for python 3.6.  
2. Package app using `make aws-eb-prep`; then upload the resulting `listen-local-app.zip` file
3. For the static files to work you will need to go to Configuration > Software.modify. Under "Static Paths" add "Path: /static/" and "Directory: listen_local_app/static/"

## Design

Front-end web design thanks to [@heyitsjaki](https://www.designbyjaki.com)

## Built with
* [Flask](http://flask.pocoo.org) - Python microframework for Apps
* [Spotipy](https://github.com/plamere/spotipy) - Python wrapper for Spotify API

## Ackowledgments
* Thank you to [Seatgeek](www.seatgeek.com) and [Spotify](www.spotfy.com) for their powerful public APIs
