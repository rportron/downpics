# downpics
Command line tool to download "linked pics" from Internet page

Dependance needed: BeautifulSoup

# Gestting started
## Get the code on your machine.
```
git clone git://github.com/rportron/downpics.git
cd downpics
```

## Install dependance
`pip install --upgrade BeautifulSoup4`

# How to use it
## Command line
`python3 recup-img.py folder [-url url] [-prefix name_prefixe]`

It will download pics from url into the folder (with the name_prefixe before if given)
Don't write -url if you want to repeatly download pics from various url

For example:
`python3 recup-image.py . -url http://portron.org/downpics.html -prefix toto_` will download all "linked pics" from the given url with toto_ added before the pic name to the current directory

## As a library
import ...

## GUI
Use recup_img_xwin
