# -*- coding: utf-8 -*-
import numpy as N
import cv2
from cv2 import *
import sys
# import tweepy  # http://raspi.tv/2014/tweeting-with-python-tweepy-on-the-raspberry-pi-part-2-pi-twitter-app-series
#import py_compile #py_compile.compile('nico.py') #import nico
import datetime
# import winsound

#Parametros
confirmacion=False
tweet=False
alarm=False
show=True
save=True
horario=False
deteccion=False

#Producir sonido
def beep(sound=sys.argv[0]):
    print 'ALARM'
    # winsound.PlaySound('%s.wav' % sound, winsound.SND_FILENAME)
#Configuracion
def pedir_confirmacion(prompt, reintentos=2, queja='Si o no, por favor!'):
    while True:
        ok = raw_input(prompt)
        if ok in ('s', 'S', 'si', 'Si', 'SI'):
            return True
        if ok in ('n', 'no', 'No', 'NO'):
            return False
        reintentos = reintentos - 1
        if reintentos < 0:
            raise IOError('usuario duro')
            sys.exit()
        print queja
        
# definition de la fonction qui permet de detecter le visage dans l'image
def detectFaceInImage(inputImg,cascade,flags,n):
    minFeatureSize = (5, 5);
    search_scale_factor = 1.1;
    storage = cv.CreateMemStorage(0);
    if (inputImg.nChannels > 1): #nChannels? &
        size = (inputImg.width, inputImg.height);
        greyImg = cv.CreateImage(size, IPL_DEPTH_8U, 1 ); #IPL_DEPTH_8U means an 8-bit unsigned image &
        cv.CvtColor( inputImg, greyImg, cv.CV_BGR2GRAY ); #?? conversion a Img gris &
        detectImg = greyImg; 
    rects = cv.HaarDetectObjects( detectImg, cascade, storage,#page 512 livre OpenCv
            search_scale_factor, 3, flags, minFeatureSize); #Viola-Jones -> Ondelettes de Haar
                                                            #Image (gris)
                                                            #cascade -> addresse de l image
                                                            #Storage (informatique, pas physique)
                                                            #Factor de Scale=Experimental ->livre OpenCv
                                                            #3 -> min_neighbors
                                                            #flags? -> 0
                                                            #taille de fenetre qui va augmenter &
    nFaces = len(rects);
    if (nFaces > n):
        rc = rects[n] #envoyer tous les rectangles &
    else:
        rc = None #aucun rectangle a envoyer, pas de visages
    return rc


print "--" *10
print "Nico - Alarma PC"
print "--" *10

if confirmacion:
    modificacion=pedir_confirmacion("Desea modificar los parametros prestablecidos?")
    if modificacion:
        tweet=pedir_confirmacion("tweet: ")
        alarm=pedir_confirmacion("alarm: ")
        show=pedir_confirmacion("show: ")
        save=pedir_confirmacion("save: ")
        horario=pedir_confirmacion("horario: ")
        deteccion=pedir_confirmacion("deteccion: ")

url= "http://tinyurl.com/nyklgva"
carpeta="./detected/"
cuenta_destino="@nicotomatis"
mensaje = 'Alarma_PC:'
cant_max_fotos=1000
mensaje_max = 'Se han enviado '+ str(cant_max_fotos) + ' fotos'
cant_adv_fotos=100
mensaje_adv = 'Se han enviado '+ str(cant_adv_fotos) + ' fotos'
hora_inicio=   "00"
hora_fin=      "24"

# Configuracion de twitter
# consumer_key = ""
# consumer_secret = ""
# access_token = ""
# access_token_secret = ""
# auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
# auth.secure = True
# auth.set_access_token(access_token, access_token_secret)
# api = tweepy.API(auth)

#Inicio del programa
print "El programa inicia a las: " , datetime.datetime.now()
# print "La cuenta de twitter es: " + api.me().name
print "Se escribira en la cuenta: " + cuenta_destino

capture = cv.CaptureFromCAM(0)#Captura de la webcam
if not capture:
    print "No hubo captura"
    sys.exit()
for i in range (10):# espera hasta que arranque la Webcam
    if cv.QueryFrame(capture) is None: pass
    
old = cv.QueryFrame(capture)
cv.Flip(old, None, 1)#Mirror image
size = (old.width, old.height);
gray_old = cv.CreateImage(size, IPL_DEPTH_8U, 1)
cv.CvtColor(old, gray_old, cv.CV_BGR2GRAY)
dif = cv.CloneImage(gray_old)
gray_new = cv.CloneImage(gray_old)
umb = cv.CloneImage(gray_old)

tiempo=""
lista_tiempo=[]
lista_twitter=[]
contador_fotos=0

#Deteccion de rostros
if deteccion:
    faceCascadeFilename = "./haarcascade_profileface.xml"
    faceCascade = cv.Load(faceCascadeFilename)
while True:
    if horario: 
        if not (int(hora_inicio) <= int(datetime.datetime.now().strftime("%H")) < int(hora_fin)): break
    new = cv.QueryFrame(capture)
    cv.Flip(new, None, 1)#Mirror image
    gray_new = cv.CreateImage(size, IPL_DEPTH_8U, 1)
    cv.CvtColor(new, gray_new, cv.CV_BGR2GRAY)
    cv.AbsDiff(gray_new, gray_old, dif)
    gray_old = gray_new
    cv.Threshold(dif, umb, 50, 255, cv.CV_THRESH_BINARY)
    if show: cv.ShowImage("original", new)
    # cv.ShowImage("gray", gray_new)
    # cv.ShowImage("dif", dif)
    cv2.destroyWindow(tiempo)
    matriz = N.ascontiguousarray(cv.GetMat(umb))
    if len(matriz.nonzero()[0]) > 1000:
        tiempo=datetime.datetime.now().strftime("%H-%M-%S")
        if contador_fotos == cant_max_fotos:
            if len(cuenta_destino+" "+tiempo+" "+mensaje_max)<=140:
                print cuenta_destino+" "+tiempo+" "+mensaje_max
                # if tweet: api.update_status(cuenta_destino+" "+tiempo+" "+mensaje_max)
                break
        if contador_fotos == cant_adv_fotos:
            if len(cuenta_destino+" "+tiempo+" "+mensaje_adv)<=140:
                print cuenta_destino+" "+tiempo+" "+mensaje_adv
                # if tweet: api.update_status(cuenta_destino+" "+tiempo+" "+mensaje_adv)
                contador_fotos = contador_fotos + 1
        if tiempo not in lista_tiempo:
            lista_tiempo.append(tiempo)
            contador_fotos=contador_fotos+1
            nombre_imagen=carpeta+tiempo+".jpg"
            #Deteccion de rostro
            if deteccion:
                faceRect = detectFaceInImage(new, faceCascade, cv.CV_HAAR_FIND_BIGGEST_OBJECT | cv.CV_HAAR_DO_ROUGH_SEARCH,0);
                if faceRect: 
                    rostro = cv.CloneImage( new )
                    cv.Rectangle(rostro,(int(faceRect[0][0]),int(faceRect[0][1])),(int(faceRect[0][0])+int(faceRect[0][2]),int(faceRect[0][1])+int(faceRect[0][3])),cv.RGB(100,200,150),2)
                    if save:
                        cv.SaveImage(carpeta+tiempo+"rostro"+".jpg", rostro)
                elif save:
                    cv.SaveImage(nombre_imagen, new)
            elif save:
                print 'Guardando imagen'
                cv.SaveImage(nombre_imagen, new)
            if alarm:
                beep("alarm")
        if tiempo[0:2] not in lista_twitter:
            lista_twitter.append(tiempo[0:2])
            if len(cuenta_destino +" "+mensaje+str(contador_fotos)+" "+tiempo+" "+url)<=140:
                print cuenta_destino+" "+mensaje+str(contador_fotos)+" "+tiempo+" "+url
                # if tweet: api.update_status(cuenta_destino+" "+mensaje+str(contador_fotos)+" "+tiempo+" "+url)
            else:
                print cuenta_destino+" "+tiempo+" "+url
                # if tweet: api.update_status(cuenta_destino+" "+tiempo+" "+url)
        if show: cv.ShowImage(tiempo, umb)
    if cv.WaitKey(1)& 0xFF == ord('q'): break #cuando se presiona q sale
print "El programa finaliza a las: " , datetime.datetime.now()