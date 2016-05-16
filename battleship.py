# -----------------------------------------------------------------------------
# MIT License
# Copyright (c) 2016 - Hugo Malgrange & Marine Vaillant 
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# -----------------------------------------------------------------------------

from Tkinter import *
import urllib # dialogue serveur
import urllib2
import winsound # Faire des bip
import tkMessageBox # fenetre popup
import time # Compter les secondes (scrutage serveur)
import thread # Appeler une fonction en asynchrone (scrutage serveur)

root = Tk()

iBateau = list()
grid = list()
fond = {
      "src":"grid1019.gif", # image de fond
      "grid1X":255, # position X NW de la grille
      "grid1Y":175,
      "grid1W":309, # largeur de la grille
      "grid1H":297,
      "gridXN":8, # nombre de cases horizontales de la grille
      "gridYN":8,
      "grid2X":637, # position X NW de la grille cible
      "grid2Y":175,
      "carreauMarge":5, # distance entre le coin NW du bateau et le coin NW du carreau - permet de  centrer  l image
      "parcX":110, # position X centrale du parking a bateau
      "parcY":160, # position Y du parking pour le premier bateau
      "parcDY":60 # ecart vertical entre chaque bateau
    }    
bateau=[
        ["carrier180.gif","Porte-avions",5],
        ["destroyer142.gif","Croiseur",4],
        ["submarine105.gif","Sous-marin",3],
        ["submarine105.gif","Sous-marin",3], # essai avec 2 sous-marins
        ["camo105.gif","Corvette",3],
        ["zodiac68.gif","Patrouilleur",2]
    ]
fe = 0

#
# *****************  fonctions techniques  ***************************
#

def battleMenu():
    winsound.Beep(500,250) # ......

def dialogueServeur(actions):
    #
    # Communication in/out avec le serveur
    # actions : {'action':"chat", "key":"batailleNavale", "valeur":"a", "player":"hugo"}
    #
    # ******************************* CHANGE THIS URL *****************************
    url = "http://www.mysite/battleship/battleship.php"
    # *****************************************************************************
    values = actions
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    return response.read()

def fenetreInit(wid,hei,tit="",bg="",t="init"):
    #
    # Creation de la fenetre d accueil
    #
    fe = Canvas(root, width=wid, height=hei)
    root.title(tit)
    # Menu
    m = Menu(root)
    m.add_command(label="Cr\xE9er une partie", command=lambda :creerPartiePseudo(m,0))
    m = partieEnAttente(m) # Creation menu parties en attente
    m.add_command(label="Aide", command=aide)
    m.add_command(label="Quitter", command=root.quit)
    root.config(menu=m)
    fe.pack()
    if bg!="":
        fe.create_image(0, 0, anchor=NW, image=bg, tag=t)
    return fe

def creerPartiePseudo(menuPrincipal,joueur=0):
    #
    # Joueur A & B - Popup pour entrer un Pseudo
    # joueur : pseudoA
    #
    popPseudo = Frame(root)
    Label(popPseudo, text="Pseudo").pack(side=LEFT)
    pseudo = Entry(popPseudo)
    pseudo.pack(padx=5,side=LEFT)
    b = Button(popPseudo, text="OK", command=lambda :creerPartieValid(pseudo,popPseudo,menuPrincipal,joueur))
    b.pack(pady=5,side=RIGHT)
    popPseudo.pack()
    popPseudo.place(x=10, y=10) # positionnement dans la fenetre (par dessus) et non en supplement en bas

def creerPartieValid(pseudo,popPseudo,menuPrincipal,joueur=0):
    #
    # Joueur A & B - Validation du pseudo par envoi au serveur - Creation de la partie
    #
    p = pseudo.get()
    if joueur==0:
        a = {"action":"creerPartie", "key":"batailleNavale", "pseudoA":p} # joueur A
    else:
        a = {"action":"choixPartie", "key":"batailleNavale", "pseudoA":joueur, "pseudoB":p} # joueur B
    r = dialogueServeur(a) # r : 1 = succes ; 0 = echec
    popPseudo.destroy()
    if r!="0":
        if joueur==0:
            tkMessageBox.showinfo(title="Nouvelle partie", message="Partie "+ p +" cr\xE9\xE9e. En attente d'un autre joueur...")
        else:
            tkMessageBox.showinfo(title="Invitation dans une partie", message="Partie avec "+ joueur +" demand\xE9. En attente accord...")
        thread.start_new_thread(attenteJoueur,(p,joueur,)) # attenteJoueur appelee en asynchrone
        menuPrincipal.delete(2)
        menuPrincipal.delete(1)
    else:
        if joueur==0:
            tkMessageBox.showinfo(title="Nouvelle partie", message="Impossible, cette partie existe d\xE9j\xE0 !")
        else:
            tkMessageBox.showinfo(title="Invitation dans une partie", message="Impossible, le joueur vient de partir.")

def attenteJoueur(pseudo,joueur):
    #
    # Joueur A & B - Scrute le serveur toutes les 4 sec pour chercher un adversaire.
    # Cette fonction doit etre appelee en Asynchrone : thread.start_new_thread(attenteJoueur,(pseudo,joueur,))
    #
    r = "0"
    if joueur==0:
        a = {"action":"attenteJoueur", "key":"batailleNavale", "pseudoA":pseudo}
    else:
        a = {"action":"attenteAccord", "key":"batailleNavale", "pseudoA":joueur, "pseudoB":pseudo}
    while r=="0":
        r = dialogueServeur(a) # r : 1 = succes ; 0 = echec
        print "je suis en attente"
        time.sleep(4)
    if joueur==0:
        print "le joueur " + str(r) + " veut jouer"
        joueurAccord(pseudo,str(r)) # pseudoA, pseudoB
    else:
        print "le joueur " + str(r) + " est d'accord"
        accord(str(r),pseudo) # pseudoA, pseudoB

def partieEnAttente(menuPrincipal,actualiser=0):
    #
    # Joueur B - Sous-menu avec la liste des joueurs en attente d un adversaire - interrogation du serveur en actualisant
    #
    menuSecondaire = Menu(menuPrincipal, tearoff=0)
    menuSecondaire.add_command(label="-Actualiser-", command=lambda :partieEnAttente(menuPrincipal,1))
    a = {"action":"partieEnAttente", "key":"batailleNavale"}
    r = dialogueServeur(a) # r : retour serveur : "bob,juliette,Hugo" ou 0
    if r!="0":
        r1 = r.split(',') # Convertion string vers tableau
        for i,b in enumerate(r1):
            if b!="":
                menuSecondaire.add_command(label=b, command=lambda b=b:creerPartiePseudo(menuPrincipal,b)) # Galere !!! la variable b change avec la boucle. Cette technique permet de passer la bonne
    else:
        menuSecondaire.add_command(label="-aucune partie-")
    if actualiser==0:
        menuPrincipal.add_cascade(label="Entrer dans une partie", menu=menuSecondaire)
        return menuPrincipal
    else:
        menuPrincipal.delete(2)
        menuPrincipal.insert_cascade(2,label="Entrer dans une partie", menu=menuSecondaire)

def joueurAccord(pseudoA,pseudoB):
    #
    # Joueur A - Reception de l invitation du joueur B
    #
    popAccord = Frame(root)
    Label(popAccord, text=pseudoB+" voudrait jouer contre vous").pack(side=LEFT)
    b = Button(popAccord, text="Jouer", command=lambda :prepareJeu(popAccord,pseudoA,pseudoB,"A")) # je suis A
    b.pack(pady=5,side=RIGHT)
    popAccord.pack()
    popAccord.place(x=10, y=10)

def accord(pseudoA,pseudoB):
    #
    # Joueur B - Reception de l accord du joueur A
    #
    popAccord = Frame(root)
    Label(popAccord, text=pseudoA+" est d'accord pour vous affronter").pack(side=LEFT)
    b = Button(popAccord, text="Jouer", command=lambda :prepareJeu(popAccord,pseudoA,pseudoB,"B")) # je suis B
    b.pack(pady=5,side=RIGHT)
    popAccord.pack()
    popAccord.place(x=10, y=10) # positionnement dans la fenetre (par dessus) et non en supplement en bas

def aide():
    #
    # Affiche une fenetre d aide
    #
    aide = "Bienvenue sur BattleShip Bataille navale"
    tkMessageBox.showinfo(title="Aide", message=aide)

def fenetreJeu(wid,hei,tit="",bg="",t="bg"):
    #
    #    # Creation de la fenetre de jeu
    #
    fe = Canvas(root, width=wid, height=hei)
    root.title(tit)
    # Menu
    m = Menu(root)
    ms = Menu(m, tearoff=0)
    ms.add_command(label="Bataille navale", command=battleMenu)
    ms.add_command(label="Quitter", command=root.quit)
    m.add_cascade(label="Partie", menu=ms)
    root.config(menu=m)
    fe.pack()
    if bg!="":
        fe.create_image(0, 0, anchor=NW, image=bg, tag=t)
    return fe

def clicGauche(event):
    #
    # Clic gauche sur un bateau : enregistrement de la position relative du clic sur l image bateau
    #
    global iBateau
    for i,b in enumerate(iBateau):
        if event.x>b["x"] and event.x<b["x"]+b["wid"] and event.y>b["y"] and event.y<b["y"]+b["hei"]:
            iBateau[i]["clic"] = 1 # Ce bateau est clique
            iBateau[i]['clicX'] = int(event.x - b["x"])
            iBateau[i]['clicY'] = int(event.y - b["y"])
            break

def clicDroit(event):
    #
    # Clic droit sur un bateau : rotation de 90 deg
    #
    global iBateau,fe
    for i,b in enumerate(iBateau):
        if event.x>b["x"] and event.x<b["x"]+b["wid"] and event.y>b["y"] and event.y<b["y"]+b["hei"]:
            f =  b["wid"]
            g =  b["hei"]
            iBateau[i]["wid"] = g # Inversion
            iBateau[i]["hei"] = f
            if b["verticale"]==0:
                fe.delete("H"+str(i))
                iBateau[i]["verticale"] = 1
                fe.create_image(b["x"],b["y"], anchor=NW, image=b["imgV"], tag="V"+str(i))
            else:
                fe.delete("V"+str(i))
                iBateau[i]["verticale"] = 0
                fe.create_image(b["x"],b["y"], anchor=NW, image=b["img"], tag="H"+str(i))
            p = aimantGrid(b["x"],b["y"]) # uniquement pour recuperer les numeros de carreau (au lieu des x,y)
            sauvGrid(i,p[2],p[3])
            break

def dragBateau(event):
    #
    # deplacement d un bateau a la souris
    #
    global iBateau, fe
    for i,b in enumerate(iBateau):
        if b["clic"]==1:
            deltaX = event.x - b["x"] - b['clicX']
            deltaY = event.y - b["y"] - b['clicY']
            if b["verticale"]==0:
                fe.move("H"+str(i),deltaX,deltaY)
            else:
                fe.move("V"+str(i),deltaX,deltaY)
            iBateau[i]["x"] = event.x - b['clicX']
            iBateau[i]["y"] = event.y - b['clicY']
            break
            
def finClicGauche(event):
    #
    # Fin du clic de la souris
    #
    global iBateau, fond
    for i,b in enumerate(iBateau):
        if b["clic"]==1:
            iBateau[i]["clic"] = 0
            if event.x-b["clicX"]<fond["grid1X"] or event.x-b["clicX"]+b["wid"]>fond["grid1X"]+fond["grid1W"] or event.y-b["clicY"]<fond["grid1Y"] or event.y-b["clicY"]+b["hei"]>fond["grid1Y"]+fond["grid1H"]:
                retourParc(i) # Pas dans la grille ? Retour case depart
            else:
                aimant = aimantGrid(b["x"],b["y"])
                if b["verticale"]==0:
                    fe.delete("H"+str(i))
                    fe.create_image(aimant[0],aimant[1], anchor=NW, image=b["img"], tag="H"+str(i))
                else:
                    fe.delete("V"+str(i))
                    fe.create_image(aimant[0],aimant[1], anchor=NW, image=b["imgV"], tag="V"+str(i))
                iBateau[i]["x"] = aimant[0]
                iBateau[i]["y"] = aimant[1]
                iBateau[i]["grid"] = 1 # en place
                sauvGrid(i,aimant[2],aimant[3])

def retourParc(i):
    #
    # Repositionnement d un bateau dans la partie Parking de l image de fond
    #
    global iBateau, fond, pare, popPare
    y = int(fond["parcY"]+i*fond["parcDY"])
    if iBateau[i]["verticale"]==0:
        x = int(fond["parcX"]-iBateau[i]["wid"]/2)
        fe.delete("H"+str(i))
        fe.create_image(x,y, anchor=NW, image=iBateau[i]["img"], tag="H"+str(i))
    else:
        x = int(fond["parcX"]-iBateau[i]["hei"]/2)
        iBateau[i]["verticale"] = 0
        f = iBateau[i]["wid"]
        g = iBateau[i]["hei"]
        iBateau[i]["wid"] = g # Inversion
        iBateau[i]["hei"] = f
        iBateau[i]["verticale"] = 0
        fe.delete("V"+str(i))
        fe.create_image(x,y, anchor=NW, image=iBateau[i]["img"], tag="H"+str(i))
    iBateau[i]["x"] = x
    iBateau[i]["y"] = y
    iBateau[i]["grid"] = 0
    if pare: # le joueur n est pas pare => suppression du bouton "pare"
        popPare.destroy()
        pare = 0;

def aimantGrid(x,y):
    #
    # Retourne la position du coin NW du carreau le plus proche de x,y
    #
    global fond
    # winsound.Beep(500,250)
    caseX = float((x-fond["grid1X"])/float(fond["grid1W"])*fond["gridXN"]) # Python2.7 : division necessite float sinon faux
    caseX = int(caseX + .5)
    caseY = float((y-fond["grid1Y"])/float(fond["grid1H"])*fond["gridYN"])
    caseY = int(caseY + .5)
    return [int(fond["grid1X"]+caseX*fond["grid1W"]/float(fond["gridXN"]))+fond["carreauMarge"],int(fond["grid1Y"]+caseY*fond["grid1H"]/float(fond["gridYN"]))+fond["carreauMarge"],caseX,caseY]

def sauvGrid(id,x,y):
    #
    # Sauvegarde le tableau de jeu dans la liste grid
    # numerotation : lecture horizontale, ligne apres ligne.  !!! ID + 1 !!! a cause du 0
    # retourne la chaine en string avec separation par des virgules : 0,0,0,3,3,3,0,0...
    #
    global iBateau, fond, grid, gridStr
    if not grid: # Initialisation de la sauvegarde : tout a 0
        for i in xrange(0,int(fond["gridXN"]*fond["gridYN"])):
            grid.append(0)
    else: # effacement des precedentes donnees de ce bateau (id)
        for i in xrange(0,int(fond["gridXN"]*fond["gridYN"])):
            if grid[i]==id+1:
                grid[i] = 0
    # Superposition ?
    s = 0;
    if iBateau[id]["verticale"]==0:
        for i in xrange(0,iBateau[id]["carreau"]):
            if int(x+i)>=fond["gridXN"]:
                s = 1 # ce bateau deborde a droite
            elif grid[int(i+x+y*fond["gridXN"])]!=0:
                s = 1 # ce bateau est au dessus d un autre
    else:
        for i in xrange(0,iBateau[id]["carreau"]):
            if int(y+i)>=fond["gridYN"]:
                s = 1 # ce bateau deborde en dessous
            elif grid[int((i*fond["gridXN"])+x+y*fond["gridXN"])]!=0:
                s = 1 # au dessus d un autre
    if s==1:
        retourParc(id)
    else:
        # Mise en memoire
        if iBateau[id]["verticale"]==0:
            for i in xrange(0,iBateau[id]["carreau"]):
                grid[int(i+x+y*fond["gridXN"])] = id+1 # Indice du bateau (+1) dans les cases correspondantes
        else:
            for i in xrange(0,iBateau[id]["carreau"]):
                grid[int((i*fond["gridXN"])+x+y*fond["gridXN"])] = id+1 # Indice du bateau (+1) dans les cases correspondantes
        # retour en string egalement pour envoi serveur
        gridStr = ""
        for i in xrange(0,int(fond["gridXN"]*fond["gridYN"])):
            gridStr += str(grid[i]) + ","
        # Reste des bateau au parking ?
        reste = 0
        for i,b in enumerate(iBateau):
            if b["grid"]==0: # Ce bateau est au parking
                reste = 1
        if reste==0:
            bateauPare()
        print gridStr

def bateauPare():
    #
    # Affichage du bouton Pare - debut du jeu()
    #
    global pare, popPare
    if pare==0:
        popPare = Frame(root)
        Label(popPare, text="Par\xE9 au combat ?").pack(side=LEFT)
        b = Button(popPare, text="Par\xE9", command=pareJeu)
        b.pack(pady=5,side=RIGHT)
        popPare.pack()
        popPare.place(x=10, y=10)
        pare = 1

def deuxPare(p):
    #
    # Joueur A & B - Scrute le serveur toutes les 4 sec pour chercher un adversaire.
    # Cette fonction doit etre appelee en Asynchrone : thread.start_new_thread(attenteJoueur,(pseudo,joueur,))
    #
    r = "0"
    a = {"action":"deuxPare", "key":"batailleNavale", "pseudoA":p[0], "pseudoB":p[1]}
    while r=="0":
        r = dialogueServeur(a) # r : 1 = succes ; 0 = echec
        print "je suis en attente"
        time.sleep(2)
    attaqueJeu()

def clicFeu(event):
    #
    # Clic gauche sur la grille d attaque
    # Envoi les coordonnees du carreau
    #
    global fond, fe, pseu
    if event.x>fond["grid2X"] and event.x<fond["grid2X"]+fond["grid1W"] and event.y>fond["grid2Y"] and event.y<fond["grid2Y"]+fond["grid1H"]:
        fe.unbind('<Button-1>')
        caseX = float((event.x-fond["grid2X"])/float(fond["grid1W"])*fond["gridXN"]) # Python2.7 : division necessite float sinon faux
        caseX = int(caseX)
        caseY = float((event.y-fond["grid2Y"])/float(fond["grid1H"])*fond["gridYN"])
        caseY = int(caseY)
        case = caseX + caseY*fond["gridXN"]
        a = {"action":"feu", "key":"batailleNavale", "pseudoA":pseu[0], "pseudoB":pseu[1], "moi":pseu[2], "feu":case}
        r = dialogueServeur(a) # r : 0(rate)/1(touche)/2(coule)/A(fin A gagne)/B(gagne),A/B(joueur suivant)
        resultatFeu(r)

def autreFeu(pseu):
    #
    # Attente que l autre joueur attaque
    # Cette fonction doit etre appelee en mode Asynchrone
    #
    r = "0"
    a = {"action":"autreAttaque", "key":"batailleNavale", "pseudoA":pseu[0], "pseudoB":pseu[1], "moi":pseu[2]}
    while r=="0":
        r = dialogueServeur(a) # r : 0(rate)/1(touche)/2(coule)/A(fin A gagne)/B(gagne),A/B(joueur suivant) ou "0"
        print "attente Attaque"
        time.sleep(2)
    resultatFeu(r)

def resultatFeu(r):
    #
    # Affiche le resultat du feu en haut a gauche - Relance attaqueJeu() pour attaque suivante
    #
    global fond, popAttaque,pseu
    print r
    r1 = r.split(',')
    print r1[2]
    caseY = int(float(r1[2])/float(fond["gridXN"])+.00001)
    caseX = int((float(r1[2])/float(fond["gridXN"])+.00001 - caseY) * fond["gridXN"] + .00001)
    if r1[0]!="A" and r1[0]!="B":
        popAttaque.destroy()
        if r1[0]=="0":
            re = "Dans l'eau."
            co = "green"
        elif r1[0]=="1":
            re = "Touch\xE9 !"
            co = "yellow"
        elif r1[0]=="2":
            re = "Coul\xE9 !!!"
            co = "red"
        marqueAttaque(r1[1],r1[0],caseX,caseY) # coloration de la case adverse / a moi
        popAttaque = Frame(root)
        Label(popAttaque, text=re, bg=co).pack(side=LEFT)
        popAttaque.pack()
        popAttaque.place(x=10, y=10)
        attaqueJeu(r1[1],r1[0]) # relance attaqueJeu
    else:
        finJeu(r1[0])

def marqueAttaque(m,t,x,y):
    #
    # Coloration de la grille adverse selon le resultat
    #
    global fond, fe, pseu
    marge = 8
    if m==pseu[2]: # A/B 
        x1 = fond["grid1X"] + (x*fond["grid1W"]/fond["gridXN"]) + marge
        y1 = fond["grid1Y"] + (y*fond["grid1H"]/fond["gridYN"]) + marge
    else:
        x1 = fond["grid2X"] + (x*fond["grid1W"]/fond["gridXN"]) + marge
        y1 = fond["grid2Y"] + (y*fond["grid1H"]/fond["gridYN"]) + marge
    x2 = x1 + fond["grid1W"]/fond["gridXN"] - 2*marge
    y2 = y1 + fond["grid1H"]/fond["gridYN"] - 2*marge
    if t=="0":
        co = "cyan"
    elif t=="1":
        co = "yellow"
    elif t=="2":
        co = "red"
    fe.create_rectangle(x1,y1,x2,y2,fill=co)

#
# *****************  fonctions principales de deroulement du jeu  ***************************
#

def initJeu():
    #
    # Initialisation du jeu : fenetre d accueil
    #
    global fe
    a = PhotoImage(file="BattleShipTittle.gif")
    wid = int(a.width())
    hei = int(a.height())
    fe = fenetreInit(wid, hei, 'BattleShip Bataille navale', a)
    # Affichage   
    root.mainloop()

def prepareJeu(popAccord,pseudoA,pseudoB,moi):
    #
    # Trame du jeu
    # moi : A ou B
    #
    global iBateau, bateau, fond, fe, pseu, pare
    pseu = [pseudoA, pseudoB, moi] # les pseudos deviennent globaux
    pare = 0 # bouton pare non affiche
    if moi=="A":
        a = {"action":"accord", "key":"batailleNavale", "pseudoA":pseudoA, "pseudoB":pseudoB}
        r = dialogueServeur(a)
    # 1. Destruction de la fenetre precedente.
    fe.destroy()
    popAccord.destroy()
    # 2. Creation et affichage de la fenetre
    a = PhotoImage(file=fond["src"]) # image : 1019x546 - grid : 309x297 (38,125 par case)
    wid = int(a.width())
    hei = int(a.height())
    # creation de la fenetre
    fe = fenetreJeu(wid,hei,'Battleship - '+pseudoA+' contre '+pseudoB,a)
    # ajout des bateaux en liste verticale
    iBateau=list()
    for i,b in enumerate(bateau):
        img = PhotoImage(file=b[0])
        imgV = PhotoImage(file="V"+b[0])
        w = int(img.width())
        h = int(img.height())
        x = int(fond["parcX"]-w/2)
        y = int(fond["parcY"]+i*fond["parcDY"])
        iBateau.append({
            "img":img, # objet image
            "imgV":imgV, # objet image verticale
            "wid":w, # largeur image
            "hei":h,
            "x":x, # position X coin NW image
            "y":y,
            "src":b[0], # nom du fichier image
            "nom":b[1], # appelation de l image (croiseur, sous-marin...)
            "carreau":b[2], # taille en carreau
            "clic":0, # 1 si clic en cours
            "clicX":0, # position relative X du clic par rapport au coin NW de l image
            "clicY":0,
            "grid":0, # 1 si image sur la grille
            "verticale":0 # 1 si l image est verticale
            })
        fe.create_image(x,y, anchor=NW, image=img, tag="H"+str(i)) # tag du bateau : H ou V suivi de son Indice dans iBateau
    # Clic sur un bateau - envoi de l ensemble des elements des bateaux : iBateau
    fe.bind('<Button-1>', clicGauche)
    fe.bind('<Button-3>', clicDroit)
    fe.bind('<B1-Motion>', dragBateau)
    fe.bind('<ButtonRelease-1>', finClicGauche)
    # Affichage   
    root.mainloop()

def pareJeu():
    #
    # Attente autre joueur pare
    #
    global pseu, popPare, fe, gridStr
    popPare.destroy()
    fe.unbind('<Button-1>')
    fe.unbind('<Button-3>')
    fe.unbind('<B1-Motion>')
    fe.unbind('<ButtonRelease-1>')
    a = {"action":"bateauPare", "key":"batailleNavale", "pseudoA":pseu[0], "pseudoB":pseu[1], "moi":pseu[2], "grille":gridStr}
    r = dialogueServeur(a)
    if r=="1":
        thread.start_new_thread(deuxPare,(pseu,)) # deuxPare appelee en asynchrone
        
def attaqueJeu(j="A",rep="0"):
    #
    # Phase attaque
    # Fonction appelee en boucle a chaque coup jusqu a la fin de la partie
    # Reponse : 0(rate) / 1(touche) / 2(coule) / A(fin A gagne) / B(fin B gagne)
    #
    global pseu, fe, popAttaque
    print "feu non de dieu"
    if rep=="A" or rep=="B":
        # FIN PARTIE
        popAttaque = Frame(root)
        if rep==pseu[2]:
            t = "J'ai gagn\xE9 ! Fin de la partie"
            co = "green"
        else:
            t = "J'ai perdu ! Fin de la partie"
            co = "blue"
        Label(popAttaque, text=t, bg=co).pack(side=LEFT)
        popAttaque.pack()
        popAttaque.place(x=10, y=10) # positionnement dans la fenetre (par dessus) et non en supplement en bas
    elif j==pseu[2]:
        # a moi de jouer
        popAttaque = Frame(root)
        Label(popAttaque, text="A vous de jouer", bg="blue").pack(side=LEFT)
        popAttaque.pack()
        popAttaque.place(x=10, y=10) # positionnement dans la fenetre (par dessus) et non en supplement en bas
        fe.bind('<Button-1>', clicFeu)
    else:
        # A l autre de jouer
        popAttaque = Frame(root)
        popAttaque.pack()
        thread.start_new_thread(autreFeu,(pseu,)) # autreAttaque appelee en asynchrone
        
def finJeu(gagne):
    #
    # Phase attaque
    # Fonction appelee en boucle a chaque coup jusqu a la fin de la partie
    # Reponse : 0(rate) / 1(touche) / 2(coule) / A(fin A gagne) / B(fin B gagne)
    #
    global pseu, fe
    fe.destroy()
    if gagne==pseu[2]:
        re = "P A R T I E   G A G N E E ! ! !"
    else :
        re = "V O U S   A V E Z   P E R D U !"
    a = PhotoImage(file="BattleShipTittle.gif")
    wid = int(a.width())
    hei = int(a.height())
    fe = Canvas(root, width=wid, height=hei)
    fe.create_image(0, 0, anchor=NW, image=a, tag=re)
    fe.pack()
    popAttaque = Frame(root)
    Label(popAttaque, text=re, bg="cyan", font="times 24 bold").pack(side=LEFT)
    popAttaque.pack()
    popAttaque.place(relx=0.5, rely=0.5, anchor=CENTER) # positionnement dans la fenetre centre



initJeu()
