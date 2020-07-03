# -*- coding: utf-8 -*-
"""
Created on Wed Jul 25 09:48:31 2018

@author: rportron

Tool to download "linked pics" from Internet page

Usage (as a command line):
python3 recup-image.py destination_folder [-url url] [picture_name_prefixe]

"""

from sys import exit
import argparse
import urllib.request, re
import os
from random import random

VERSION = '0.96'
EXTENSIONS_IMAGE = ['GIF', 'JPG', 'JPEG', 'PNG'] #valid extensions for this program

def program_exit(message=' ___ done -_~'):
    print(message)
    exit()

try:
    from bs4 import BeautifulSoup
except:
    program_exit('You need to install BeautifulSoup first : pip install beautifulsoup4')

PREFIXE_NOM_IMAGE = '' #by default don't add a prefix to the image name
HEADERS = ('User-Agent', 'Mozilla/5.0 (Linux; Android 5.1.1; KFFOWI Build/LVY48F) AppleWebKit/537.36 (KHTML, like Gecko) Silk/59.3.1 like Chrome/59.0.3071.117 Safari/537.36')
FANCY_BANNER = '    ___                      ___ _          \n' + \
    '   /   \_____      ___ __   / _ (_) ___ ___ \n' + \
    "  / /\ / _ \ \ /\ / / '_ \ / /_)/ |/ __/ __|\n" + \
    ' / /_// (_) \ V  V /| | | / ___/| | (__\__ \ \n' + \
    "/___,' \___/ \_/\_/ |_| |_\/    |_|\___|___/\n"

################
#url functions #
################
def last_slash_position(url):
    ''' Return the last slash (/) position '''
    position = -1
    for dummy_slash in re.finditer('/', url):
        position = dummy_slash.start()
    return position

def point_position(url):
    ''' Return the last point position (the one with the file extension) '''
    position = -1
    for dummy_point in re.finditer('\.', url):
        position = dummy_point.start()
    return position

def racine_du_site(url):
    ''' Return the root url (needed for relative path) '''
    debut = 8 # minimal position: https:// = 8 caracters
    position = last_slash_position(url)
    if position > debut:
        return url[:position + 1]
    else:
        return url

def lien_absolu(url):
    ''' Return True if the link is an absolute url (not relative) '''
    return url[0:4].lower() == 'http'

def lien_slash_slash(url):
    ''' Return True if the url begins with // '''
    return url[0:2].lower() == '//'

def instagram(url):
    ''' Return True if it's an Instagram url '''
    return url[0:25].lower() == 'https://www.instagram.com'

def url_is_chan(url):
    ''' Return True is it is a chan url
    because the pic is downloaded twice '''
    return (url[:23] == 'http://boards.4chan.org' or url[:15] == 'https://8ch.net')

def valide_extension(nom_image):
    ''' Return True if the extension is a pic's extension '''
    position_point = point_position(nom_image)
    extension = nom_image[position_point + 1:]
    if extension.upper() in EXTENSIONS_IMAGE:
        return True
    else:
        return False

def pic_correct_name(name):
    ''' Check if the file's name ends with a correct pic extension and return a correct name '''
    if valide_extension(name):
        return name
    else: #the file's name doesn't end with a correct extension
        position = -1
        for dummy_extension in EXTENSIONS_IMAGE:
            for dummy_point in re.finditer(dummy_extension, name.upper()):
                position = dummy_point.start()
            if position > 0:
                return name[:position + len(dummy_extension)]
        return name #no valid extensiton found

def nom_de_l_image(url):
    ''' Return the pic's name (needed to save the pic) '''
    image_position = last_slash_position(url)
    return pic_correct_name(url[image_position + 1::])

def decode(url, headers):
    ''' Return the parsed url with BeautifulSoup '''
    #Changement headers
    opener = urllib.request.build_opener()
    opener.addheaders = [headers]
    urllib.request.install_opener(opener)
    #Récupération du html
    try:
        response = urllib.request.urlopen(url)
    except ValueError:
        program_exit('\n *** ERROR *** Unknown url')
    except urllib.error.HTTPError:
        program_exit('\n *** ERROR 404: the webpage does not exist ***')
    except urllib.error.URLError:
        program_exit('\n *** ERROR *** the website refused the connection')
    data = response.read()      # a `bytes` object
    try:
        text = data.decode('utf-8') # a `str`; this step can't be used if data is binary
    except UnicodeDecodeError: #if data is binary
        #print('*** ERROR decode function while studying url {}\n*** data is binary'.format(url))
        text = data
    return BeautifulSoup(text, 'html.parser')

def download_pic(complete_link, pic_complete_destination, url, nom_image):
    ''' Download the pic from Internet (complete_link) to a local place (pic_complete_destination)
    url: the url where you want do download pictures (provided by the user)
    nom_image: the name which the pic will be saved with'''
    if len(complete_link) > 50: #shorten urls for the print information
        lien = complete_link[0:50] + ' (...)'
    else:
        lien = complete_link
    try:
        urllib.request.urlretrieve(complete_link, pic_complete_destination)
        print('Saving: ', lien)
    except urllib.request.HTTPError:
        print('Download ERROR: {} (404: the page {} does not exist)'.format(nom_image, lien))
    except OSError:
        print('Download ERROR: {} (problem with the file name concerning the link {})'.format(nom_image, lien))

###################
# image functions #
###################
def numerotation_image(nom_image):
    '''
    Check the pic's name, if it's a unique number: add a 0 and return the new name
    Example: 1.png becomes 01.png
    '''
    DIGITS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    #print(' *** DEBUG numerotation_image - nom image sur lequel on travaille : ', nom_image[::point_position(nom_image)])
    if nom_image[:point_position(nom_image)] in DIGITS:
        return '0' + nom_image
    return nom_image

def pic_name_analyse(url, title):
    ''' Basic url and title analysis: to find a good prefix for the pic's name '''
    if lien_absolu(url):
        lien = url[4:]
    if lien_slash_slash(url):
        lien = url[2:]
    else:
        lien = url
    titre = title
    return titre + '_'

##############################

def image_downloader_linked(url, folder, prefixe_nom_image = PREFIXE_NOM_IMAGE, headers = HEADERS):
    '''
    Download the linked pics from "url" to the directory "folder"
    Check if there is not already a file with the same name, if so add automatically a random suffix
    '''
    if not (folder[-1] == '/' or folder[-1] == '\\'):
        folder += os.sep
    soup = decode(url, headers)
    #search_pics = re.compile('[a-z0-9]+\.(gif|jpg|jpeg|png)+')
    search_pics = re.compile('(.)+\.[(gif|jpg|jpeg|png)]+$')
    for link in soup.find_all('a'):
        #print(' *** DEBUG image_downloader_linked - link étudié : ', link)
        try:
            lien = link.get('href').replace('\n', '')
            #print(' *** DEBUG image_downloader_linked - lien étudié : ', lien)
            try:
                match_pics = re.match(search_pics, lien.lower())
            except AttributeError: #AttributeError: 'NoneType' object has no attribute 'lower'
                match_pics = False
            #match_jpg=re.search('jpg', lien, flags=re.IGNORECASE) #on recherhe de l'image
            #match_png=re.search('png', lien, flags=re.IGNORECASE) #on recherhe de l'image
            #match_gif=re.search('gif', lien.lower()) #on recherhe de l'image
            if match_pics:# != None: #if (match_jpg or match_png or match_gif):
                name_ok = True
                nom_image = numerotation_image(nom_de_l_image(lien))
                if os.path.isfile(folder + prefixe_nom_image + nom_image):
                    #print(url)
                    if url_is_chan(url): #because in xchan : pic is downloaded twice
                        name_ok = False
                    else:
                        name_ok = True
                        random_suffix = '_' + str(round(10000*random()))
                        #website_title = soup.title.string #soup.find_all('title')
                        #nom_image = prefixe_nom_image + pic_name_analyse(url, website_title).replace('/','_') + nom_image
                        nom_image = prefixe_nom_image + nom_image[:point_position(nom_image)] + random_suffix + nom_image[point_position(nom_image):]
                        print('\nA file with the same name is already here, it will be downloaded with the following name {}'.format(nom_image))
                if valide_extension(nom_image) and name_ok:
                    pic_complete_destination = folder + prefixe_nom_image + nom_image
                    if lien_absolu(lien):
                        download_pic(lien, pic_complete_destination, url, nom_image)
                    elif lien_slash_slash(lien): #lien commençant par //
                        download_pic('https:' + lien, pic_complete_destination, url, nom_image)
                    else:
                        download_pic(racine_du_site(url) + lien, pic_complete_destination, url, nom_image)
#                else:
#                    print('*** DEBUG extension non valide ***')
#            else:
#                print('*** DEBUG le lien {} ne matche pas ***'.format(lien))
        except TypeError: # lien de type <a id="top"></a>
            #print('*** DEBUG TypeError : <a id="top"></a> ***')
            pass
        except AttributeError: # lien de type <a title="...
            pass
    if instagram(url):
        recherche = soup.find('meta', attrs = {'property':'og:image'})
        insta_og = re.compile('og:image')
        result = insta_og.search(str(recherche))
        index_depart = result.span()[0] - 12 #--> position du début de og:image
        #lien_image_instagram = str(recherche)[:index_depart][15:] #= le lien de l'image :)
        lien_image_instagram = str(recherche)[:index_depart][15:].replace('amp;','') #= le lien de l'image :)
        if lien_absolu(lien_image_instagram):
            nom_image = numerotation_image(nom_de_l_image(lien_image_instagram))
            if os.path.isfile(folder + prefixe_nom_image + nom_image):
                random_suffix = '_' + str(round(10000*random()))
                nom_image = nom_image[:point_position(nom_image)] + random_suffix + nom_image[point_position(nom_image):]
                #raise IOError('File {} already exists in the folder {}.'.format(nom_image, folder))
            download_pic(lien_image_instagram, folder + prefixe_nom_image + nom_image, url, nom_image)

#########################
# Alternative functions #
#########################

def image_downloader_linked_serial(liste_urls, folder, prefixe_nom_image = PREFIXE_NOM_IMAGE):
    ''' Batch download using url from a Python list '''
    i = 10
    #i = 20
    for dummy_url in liste_urls:
        image_downloader_linked(dummy_url, folder, prefixe_nom_image = prefixe_nom_image + '_' + str(i) + '_')
        i += 1

def image_downloader_linked_file(file, folder, prefixe_nom_image = PREFIXE_NOM_IMAGE):
    ''' Batch download using url from a file (one url a line)'''
    i = 20
    with open(file,'r') as my_file:
        for line in my_file:
            image_downloader_linked(line, folder, prefixe_nom_image = prefixe_nom_image + '_' + str(i) + '_')
            i += 1

#########
# TESTS # attention non exécuté si commande direct
#########
assert point_position("image2.jpeg") == 6
assert last_slash_position('toto') == -1
assert last_slash_position('http://') == 6

if __name__ == '__main__':
    print(FANCY_BANNER)
    parser = argparse.ArgumentParser(description='download "linked pics" from Internet page')
    parser.add_argument('folder', help='the folder where you want to download pics')
    parser.add_argument('-url', nargs='?', help='url where the linked pics are diplayed')
    parser.add_argument('-prefix', nargs='?', help='prefix for the pictures names')
    args = parser.parse_args()
    folder = args.folder
    if not os.path.isdir(folder):
        create_folder = input("The folder {} does not exist, should I create it?\n(y/n) ".format(folder))
        if create_folder == 'y':
            os.mkdir(folder)
        else:
            program_exit("m'kay")
    if args.prefix:
        prefixe_nom_image = args.prefix
    else:
        prefixe_nom_image = PREFIXE_NOM_IMAGE
    if args.url:
        url = args.url
        print("\nWill try to download pics from {} to {}\n".format(url, folder))
        image_downloader_linked(url, folder, prefixe_nom_image)
    else:
        download_again = True
        while download_again:
            url = input('\nPlease provide the link or type q to quit\n')
            if url == 'q':
                download_again = False
            elif url == '':
                print('')
            else:
                print("\nWill try to download pics from {} to {}\nWith pics prefix = {}\n".format(url, folder, prefixe_nom_image))
                image_downloader_linked(url, folder, prefixe_nom_image)
    #if not lien_absolu(url): # S'assure que c'est bien une url qui a été entré
    program_exit()

################
#Pour le futur #
################
# * tout télécharger depuis un site "grand père"
# * repérer les noms de modèles dans l'url pour renommer les images directement
# * argument pour ligne de commandes
