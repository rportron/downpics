# downpics
Command line tool to download "linked pics" from Internet page

Dependance needed: BeautifulSoup

# Gestting started
## Get the code on your machine.
```
git clone git@github.com:rportron/downpics.git
cd downpics
```

## Install dependance
`pip install --upgrade BeautifulSoup4`

# How to use it
## Command line
`python3 recup-image.py folder [-url url] [name_prefixe]`

It will download pics from url into folder (with the name_prefixe before if given)
Don't write -url if you want to repeatly download pics from various url

For example:
`python3 recup-image.py -url http://portron.org/downpics.html toto_` will download "linked pics" with toto_ added before the pic name

## As a library
import ...
