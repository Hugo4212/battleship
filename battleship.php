<?php
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

#
# 1. EXIT si conditions non remplies
$key = 'batailleNavale';
if(!isset($_POST['action']) || !isset($_POST['key']) || $_POST['key']!=$key ) die();
#
# 2. Mise en memoire des variables POST dans leurs nom ($_POST['action'] devient $action)
foreach($_POST as $key=>$value)
	{
	$$key = $value;
	}
#
# 3. Verification structure dossier
$base = dirname(__FILE__).'/';
if(!is_dir($base.'chat/')) mkdir($base.'chat/');
if(!is_dir($base.'partie/')) mkdir($base.'partie/');
#
# 4. Actions
switch($action)
	{
	# ********************************************************************************************
	case 'creerPartie':
	# Creation d une nouvelle partie par joueur A
	# Creation du dossier $partie (nom du joueur) dans /partie/
	# Validation du pseudo 0 ou 1
	if(isset($pseudoA) && !file_exists($base.'partie/'.$pseudoA.'.txt'))
		{
		file_put_contents($base.'partie/'.$pseudoA.'.txt', '');
		echo 1;
		}
	else echo 0;
	break;
	# ********************************************************************************************
	case 'partieEnAttente':
	# Liste des parties (joueurs A) en attente
	if($dh=opendir($base.'partie/')) # lecture du dossier
		{
		$r = "";
		while(($file=readdir($dh))!==false)
			{
			# Suppression des fichiers plus vieux que 30 minutes (1800 sec)
			if($file!='..' && $file!='.' && file_exists($base.'partie/'.$file) && !is_dir($base.'partie/'.$file) && filemtime($base.'partie/'.$file)<time()-1800)
				{
				unlink($base.'partie/'.$file);
				}
			else if($file!='..' && $file!='.' && is_dir($base.'partie/'.$file.'/') && filemtime($base.'partie/'.$file.'/')<time()-1800)
				{
				rmdirR($base.'partie/'.$file);
				echo $file.',';
				}
			# on retire les 4 derniers caracteres (.txt) et on ajoute a la chaine de sortie
			else if($file && file_exists($base.'partie/'.$file) && $file!='.' && $file!='..') $r .= substr($file,0,-4).',';
		//	$r .= $file;
			}
		closedir($dh);
		if($r!="") echo $r;
		}
	break;
	# ********************************************************************************************
	case 'attenteJoueur':
	# Joueur A attend une invitation d un joueur B
	# Retour : Joueur B si OK, 0 sinon
	if(isset($pseudoA) && file_exists($base.'partie/'.$pseudoA.'.txt'))
		{
		$pseudoB = file_get_contents($base.'partie/'.$pseudoA.'.txt'); # fichier A vide ?
		if($pseudoB!="") echo $pseudoB;
		else echo 0;
		}
	else echo 0;
	break;
	# ********************************************************************************************
	case 'choixPartie':
	# Joueur B a selectionne pseudo joueur A pour une partie
	if(isset($pseudoA) && isset($pseudoB) && file_exists($base.'partie/'.$pseudoA.'.txt'))
		{
		file_put_contents($base.'partie/'.$pseudoA.'.txt', $pseudoB); # B place son nom dans fichier A
		echo 1;
		}
	else echo 0;
	break;
	# ********************************************************************************************
	case 'attenteAccord':
	# Joueur B scrute pour connaitre accord de joueur A 
	# Retour : Joueur A si OK, 0 sinon
	if(isset($pseudoA) && is_dir($base.'partie/'.$pseudoA)) echo $pseudoA;
	else echo 0;
	break;
	# ********************************************************************************************
	case 'accord':
	# Joueur A donne accord a joueur B : creation du dossier joueurA = accord
	if(isset($pseudoA))
		{
		mkdir($base.'partie/'.$pseudoA);
		echo 1;
		}
	else echo 0;
	break;
	# ********************************************************************************************
	case 'bateauPare':
	if(isset($pseudoA) && isset($pseudoB) && isset($moi) && isset($grille) && is_dir($base.'partie/'.$pseudoA))
		{
		if($moi=="A") file_put_contents($base.'partie/'.$pseudoA.'/'.$pseudoA.'.txt', $grille);
		else file_put_contents($base.'partie/'.$pseudoA.'/'.$pseudoB.'.txt', $grille);
		echo 1;
		}
	else echo 0;
	break;
	# ********************************************************************************************
	case 'deuxPare':
	# Si le dossier pseudoA contient les deux fichier des grilles (pseudoA et pseudoB) => OK
	if(isset($pseudoA) && isset($pseudoB) && is_dir($base.'partie/'.$pseudoA) && file_exists($base.'partie/'.$pseudoA.'/'.$pseudoA.'.txt') && file_exists($base.'partie/'.$pseudoA.'/'.$pseudoB.'.txt')) echo 1;
	else echo 0;
	break;
	# ********************************************************************************************
	case 'feu':
	# Un joueur A/B fait feu sur un carreau (indice du carreau)
	if(isset($pseudoA) && isset($pseudoB) && isset($moi) && isset($feu))
		{
		# lecture de la grille de l adversaire
		if($moi=="A")
			{
			$a = file_get_contents($base.'partie/'.$pseudoA.'/'.$pseudoB.'.txt');
			$suivant = "B";
			}
		else
			{
			$a = file_get_contents($base.'partie/'.$pseudoA.'/'.$pseudoA.'.txt');
			$suivant = "A";
			}
		$grille = explode(",", $a);
		# Rep : 0(rate) / 1(touche) / 2(coule) / A(fin A gagne) / B(fin B gagne)
		if($grille[$feu]=="0") $rep = "0";
		else
			{
			# Touche - analyse ce qui flotte encore
			$c1 = 0; $c2 = 0; # compteurs
			foreach($grille as $k=>$v)
				{
				if($v!="0" && $v!="") $c2++; # il y a encore des bateaux qui flottent
				if($v==$grille[$feu]) $c1++; # il y a plusieurs cases pour ce bateau : touche !
				}
			if($c2<=1) $rep = $moi; # coule et fin de partie - moi a gagne !
			else if($c1>1) $rep = "1"; # Touche ! ( >1 car la case actuelle n est pas supprimee)
			else $rep = "2"; # Coule !
			# Mise a 0 de la case et mise a jour du fichier
			$grille[$feu] = "0";
			$a = implode(",", $grille);
			if($moi=="A") file_put_contents($base.'partie/'.$pseudoA.'/'.$pseudoB.'.txt', $a);
			else file_put_contents($base.'partie/'.$pseudoA.'/'.$pseudoA.'.txt', $a);
			}
		file_put_contents($base.'partie/'.$pseudoA.'/_feu.txt', $rep . "," . $suivant . "," . $feu); # boite-aux-lettres
		echo $rep . "," . $suivant . "," . $feu;
		}
	break;
	# ********************************************************************************************
	case 'autreAttaque':
	# Attente que l autre joueur attaque - appel asynchrone !
	# retourne 0 tant que pas d attaque
	if(isset($pseudoA) && isset($pseudoB) && isset($moi) && file_exists($base.'partie/'.$pseudoA.'/_feu.txt'))
		{
		$a = file_get_contents($base.'partie/'.$pseudoA.'/_feu.txt'); # lecture boite-aux-lettres
	//	unlink($base.'partie/'.$pseudoA.'/_feu.txt'); # vide boite-aux-lettres
		$b = explode(",", $a);
		if($b[1]==$moi) echo $a; # c est bien pour moi !
		else echo 0;
		}
	else echo 0;
	break;
	# ********************************************************************************************
	}
clearstatcache(); # mise a jour des informations sur les fichiers dans PHP
#
# Fonctions annexes
#
function rmdirR($dir)
	{
	# Suppression du contenu d un dossier
	$files = array_diff(scandir($dir), array('.','..'));
	foreach ($files as $file)
		{
		(is_dir("$dir/$file")) ? rmdirR("$dir/$file") : unlink("$dir/$file");
		}
	return rmdir($dir);
	}
//
exit;
?>
