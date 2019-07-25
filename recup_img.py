# -*- coding: utf-8 -*-
"""
Created on Wed Jul 25 09:48:31 2018

@author: rportron

Tool to download "linked pics" from Internet page

Usage (as a command line):
python3 recup-image.py destination_folder [-url url] [picture_name_prefixe]

"""

from sys import argv
import argparse
import urllib.request, re
import os
from random import random

VERSION = '0.94'

def program_exit(message=' ___ done -_~'):
    print(message)
    exit()

try:
    from bs4 import BeautifulSoup
except:
    program_exit('You need to install BeautifulSoup first : pip install beautifulsoup4')

PREFIXE_NOM_IMAGE = '' #pour renommer l'image avec un préfixe donné
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
    ''' Renvoie la position du dernier slash '''
    position = -1
    for dummy_slash in re.finditer('/', url):
        position = dummy_slash.start()
    return position

def point_position(url):
    '''
    Renvoie la position du dernier point de l'url => le point avant l'extension du nom de fichier
    '''
    position = -1
    for dummy_point in re.finditer('\.', url):
        position = dummy_point.start()
    return position

def racine_du_site(url):
    ''' Renvoie la racine de l'url => utile pour les chemins relatifs '''
    debut = 8 # position minimal : https:// = 8 caractères
    position = last_slash_position(url)
    if position > debut:
        return url[:position + 1]
    else:
        return url

def lien_absolu(url):
    ''' Renvoie vrai si le lien est un lien absolu '''
    return url[0:4].lower() == 'http'

def lien_slash_slash(url):
    ''' Détecte si l'url commence par // '''
    return url[0:2].lower() == '//'

def instagram(url):
    ''' Renvoie vrai si c'est un lien Instagram '''
    return url[0:25].lower() == 'https://www.instagram.com'

def url_is_chan(url):
    ''' Return True is it is a chan url
    because the pic is downloaded twice '''
    return (url[:23] == 'http://boards.4chan.org' or url[:15] == 'https://8ch.net')

def nom_de_l_image(url):
    '''
    Renvoie le nom de l'image (sert pour sauvegarder l'image avec son nom)
    '''
    image_position = last_slash_position(url)
    return url[image_position + 1::]

def decode(url, headers):
    ''' Renvoie l'url parsé avec BeautifulSoup '''
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
    data = response.read()      # a `bytes` object
    try:
        text = data.decode('utf-8') # a `str`; this step can't be used if data is binary
    except UnicodeDecodeError: #if data is binary
        #print('*** ERROR decode function while studying url {}\n*** data is binary'.format(url))
        text = data
    return BeautifulSoup(text, 'html.parser')

def download_pic(complete_link, pic_complete_destination, url, lien, nom_image):
    try:
        urllib.request.urlretrieve(complete_link, pic_complete_destination)
        print('Saving: ', racine_du_site(url) + lien)
    except urllib.request.HTTPError:
        print('Download ERROR: {} (404: the page {} does not exist)'.format(nom_image, racine_du_site(url) + lien))
    except OSError:
        print('Download ERROR: {} (problem with the file name concerning the link {})'.format(nom_image, racine_du_site(url) + lien))

###################
# image functions #
###################
def numerotation_image(nom_image):
    '''
    Vérifie si la numérotation est sur un seul chiffre, rajoute un zéro le cas échéant
    Renvoi le nom de l'image
    Exemple 1.png devient 01.png
    '''
    DIGITS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    #print(' *** DEBUG numerotation_image - nom image sur lequel on travaille : ', nom_image[::point_position(nom_image)])
    if nom_image[:point_position(nom_image)] in DIGITS:
        return '0' + nom_image
    return nom_image

def extension_valide(nom_image):
    ''' Renvoie True si l'extension de l'image correspond à une image '''
    EXTENSIONS_IMAGE = ['gif', 'jpg', 'jpeg', 'png']
    position_point = point_position(nom_image)
    extension = nom_image[position_point + 1:]
    #print(' *** DEBUG extension_valide - travail sur l image {} avec comme extension {}'.format(nom_image, extension))
    if extension.lower() in EXTENSIONS_IMAGE:
        return True
    else:
        return False

def pic_name_analyse(url, title):
    ''' Analyse l'url et le titre pour trouver un prefixe de l'image valide '''
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
    Télécharge dans le dossier "folder" les images ciblées par des liens de la page "url"
    Vérifie s'il n'y a pas déjà une image du même nom (avec le prefixe) dans le dossier folder
    Si c'est le cas et si pas de préfixe proposé alors ajoute un suffixe et le signale à l'utilisateur
    '''
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
                    print(url)
                    if url_is_chan(url): #because in xchan : pic is downloaded twice
                        name_ok = False
                    else:
                        name_ok = True
                        random_suffix = '_' + str(round(10000*random()))
                        #website_title = soup.title.string #soup.find_all('title')
                        #nom_image = prefixe_nom_image + pic_name_analyse(url, website_title).replace('/','_') + nom_image
                        nom_image = prefixe_nom_image + nom_image[:point_position(nom_image)] + random_suffix + nom_image[point_position(nom_image):]
                        print('\nA file with the same name is already here, it will be downloaded with the following name {}'.format(nom_image))
                if extension_valide(nom_image) and name_ok:
                    pic_complete_destination = folder + prefixe_nom_image + nom_image
                    if lien_absolu(lien):
                        download_pic(lien, pic_complete_destination, url, lien, nom_image)
                    elif lien_slash_slash(lien): #lien commençant par //
                        download_pic('https:' + lien, pic_complete_destination, url, lien, nom_image)
                    else:
                        download_pic(racine_du_site(url) + lien, pic_complete_destination, url, lien, nom_image)
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
        lien_image_instagram = str(recherche)[:index_depart][15:] #= le lien de l'image :)
        if lien_absolu(lien_image_instagram):
            nom_image = numerotation_image(nom_de_l_image(lien_image_instagram))
            if os.path.isfile(folder + prefixe_nom_image + nom_image):
                raise IOError('Le fichier {} existe dans le répertoire {}.'.format(nom_image, folder))
            print('Saving Instagram pic: ', lien_image_instagram)
            download_pic(lien_image_instagram, folder + prefixe_nom_image + nom_image, url, lien, nom_image)

#########################
# Alternative functions #
#########################

def image_downloader_linked_serial(liste_urls, folder, prefixe_nom_image = PREFIXE_NOM_IMAGE):
    ''' Télécharge par lots à partir d'une liste '''
    i = 10
    #i = 20
    for dummy_url in liste_urls:
        image_downloader_linked(dummy_url, folder, prefixe_nom_image = prefixe_nom_image + '_' + str(i) + '_')
        i += 1

def image_downloader_linked_file(file, folder, prefixe_nom_image = PREFIXE_NOM_IMAGE):
    ''' Télécharge par lots à partir d'un fichier d'url : 1 url par ligne'''
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
    if not folder[-1] == '/':
        folder += '/'
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
