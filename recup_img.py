# -*- coding: utf-8 -*-
"""
Created on Wed Jul 25 09:48:31 2018

@author: rportron

Télécharge les images contenues dans les urls d'un site web

Usage :
python3 recup-image.py dossier [-url url] [prefixe_nom_image]

"""

from sys import argv
import urllib.request, re
import os

VERSION = '0.91'

try:
    from bs4 import BeautifulSoup
except:
    print('You need to install BeautifulSoup first : pip install beautifulsoup4\nrecup-image version ', VERSION)

PREFIXE_NOM_IMAGE = '' #pour renommer l'image avec un préfixe donné
HEADERS = ('User-Agent', 'Mozilla/5.0 (Linux; Android 5.1.1; KFFOWI Build/LVY48F) AppleWebKit/537.36 (KHTML, like Gecko) Silk/59.3.1 like Chrome/59.0.3071.117 Safari/537.36')
#HEADERS = {'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; KFFOWI Build/LVY48F) AppleWebKit/537.36 (KHTML, like Gecko) Silk/59.3.1 like Chrome/59.0.3071.117 Safari/537.36'}
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
#    print('\n *** DEBUG last_slash_position ***, travail sur url : ', url)
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
    if url[0:4].lower() == 'http':
        return True
    else:
        return False

def lien_slash_slash(url):
    ''' Détecte si l'url commence par // '''
    return url[0:2].lower() == '//'

def instagram(url):
    ''' Renvoie vrai si c'est un lien Instagram '''
    return url[0:25].lower() == 'https://www.instagram.com'

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
        print('\n *** ERROR *** Unknown url')
        exit()
    data = response.read()      # a `bytes` object
    try:
        text = data.decode('utf-8') # a `str`; this step can't be used if data is binary
    except UnicodeDecodeError: #if data is binary
        #print('*** ERROR decode function while studying url {}\n*** data is binary'.format(url))
        text = data
    return BeautifulSoup(text, 'html.parser')

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
    ''' Analyse l'url pour trouver un prefixe de l'image valide '''
    #Devrait aussi analyser le titre du site
    if lien_absolu(url):
        lien = url[4:]
    if lien_slash_slash(url):
        lien = url[2:]
    else:
        lien = url
    titre = title
    #print(' *** DEBUG lien = ', lien)
    #print(' *** DEBUG titre = ', titre)
    return titre + '_'

##############################

def image_downloader_linked(url, folder, prefixe_nom_image = PREFIXE_NOM_IMAGE, headers = HEADERS):
    '''
    Télécharge dans le dossier "folder" les images ciblées par des liens de la page "url"
    Vérifie s'il n'y a pas déjà une image du même nom (avec le prefixe) dans le dossier folder
    # A DEVELOPPER # Si c'est le cas et si pas de préfixe proposé alors ajouter un préfixe trouvé dans le nom de l'url et le signaler à l'utilisateur
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
                nom_image = numerotation_image(nom_de_l_image(lien))
                if os.path.isfile(folder + prefixe_nom_image + nom_image):
                    website_title = soup.title.string #soup.find_all('title')
                    nom_image = prefixe_nom_image + pic_name_analyse(url, website_title).replace('/','_') + nom_image
                    #print('*** DEBUG image_downloader_linked : Nom de l\'image : ', nom_image)
                    if os.path.isfile(folder + prefixe_nom_image + nom_image):
                        raise IOError('Le fichier {} existe dans le répertoire {}.'.format(nom_image, folder))
                    else:
                        print('Le fichier est renommé en {}'.format(nom_image)) #DEMANDER L'ACCORD DE LA PERSONNE
                #print('*** DEBUG image_downloader_linked : Image repérée : ', nom_image)
                #print(' *** DEBUG image_downloader_linked : racine du site : {} + lien de téléchargement : {}'.format(racine_du_site(url), racine_du_site(url) + lien))
                if extension_valide(nom_image):
                    if lien_absolu(lien):
                        try:
                            urllib.request.urlretrieve(lien, folder + prefixe_nom_image + nom_image)
                            print('Saving: ', racine_du_site(url) + lien)
                        except urllib.request.HTTPError:
                            print('ÉCHEC du téléchargement de {} (erreur 404 sur le lien {})'.format(nom_image, racine_du_site(url) + lien))
                        except OSError:
                            print('ÉCHEC du téléchargement de {} (erreur de nom de fichier sur le lien {})'.format(nom_image, racine_du_site(url) + lien))
                    elif lien_slash_slash(lien): #lien commençant par //
                        try:
                            urllib.request.urlretrieve('https:' + lien, folder + prefixe_nom_image + nom_image)
                            print('Saving: ', racine_du_site(url) + lien)
                        except urllib.request.HTTPError:
                            print('ÉCHEC du téléchargement de {} (erreur 404 sur le lien {})'.format(nom_image, racine_du_site(url) + lien))
                        except OSError:
                            print('ÉCHEC du téléchargement de {} (erreur de nom de fichier sur le lien {})'.format(nom_image, racine_du_site(url) + lien))
                    else:
                        try:
                            urllib.request.urlretrieve(racine_du_site(url) + lien, folder + prefixe_nom_image + nom_image)
                            print('Saving: ', racine_du_site(url) + lien)
                        except urllib.request.HTTPError:
                             print('ÉCHEC du téléchargement de {} (erreur 404 sur le lien {})'.format(nom_image, racine_du_site(url) + lien))
                        except OSError:
                            print('ÉCHEC du téléchargement de {} (erreur de nom de fichier sur le lien {})'.format(nom_image, racine_du_site(url) + lien))
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
            #print('*** DEBUG Lien Instagram retrouvé : ', lien_image_instagram)
            if os.path.isfile(folder + prefixe_nom_image + nom_image):
                raise IOError('Le fichier {} existe dans le répertoire {}.'.format(nom_image, folder))
            urllib.request.urlretrieve(lien_image_instagram, folder + prefixe_nom_image + nom_image)
            print('Saving Instagram pic: ', lien_image_instagram)

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
#    arg_numbers = len(argv)
    try:
        folder = argv[1]
    except IndexError:
        print("Usage : python3 recup-image.py dossier [prefixe_nom_image]\n")
        exit()
    try:
        prefixe_nom_image = argv[2]
    except IndexError:
        prefixe_nom_image = PREFIXE_NOM_IMAGE
    if prefixe_nom_image[0:4] == '-url':
        url = argv[3]
        try:
            prefixe_nom_image = argv[4]
        except IndexError:
            prefixe_nom_image = PREFIXE_NOM_IMAGE
        print("\nWill try to download pics from {} to {}\n".format(url, folder))
        image_downloader_linked(url, folder, prefixe_nom_image)
    else:
        download_again = True
        while download_again:
            url = input('\nPlease provide the link or type q to quit\n')
            if url == 'q':
                download_again = False
            else:
                print("\nWill try to download pics from {} to {}\nWith pics prefix = {}\n".format(url, folder, prefixe_nom_image))
                image_downloader_linked(url, folder, prefixe_nom_image)
    #if not lien_absolu(url): # S'assure que c'est bien une url qui a été entré
    print(' ___ done -_~')

################
#Pour le futur #
################
# * tout télécharger depuis un site "grand père"
# * repérer les noms de modèles dans l'url pour renommer les images directement
# * argument pour ligne de commandes