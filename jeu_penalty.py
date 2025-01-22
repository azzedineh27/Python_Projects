#Imports
import pygame
import random

#Initialisation de Pygame
pygame.init()

#Caractéristiques de la fenetre (window)
LARGEUR, HAUTEUR = 800, 600
fenetre = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Jeu de Pénalty - 2 Joueurs")

#Image du terrain et taille
image_fond = pygame.image.load("terrain.jpg")
image_fond = pygame.transform.scale(image_fond, (LARGEUR, HAUTEUR))
#Image du gardien et taille
image_gardien = pygame.image.load("gardien.png")
image_gardien = pygame.transform.scale(image_gardien, (150, 100))
#Image du ballon et taille
image_ballon = pygame.image.load("ballon.png")
image_ballon = pygame.transform.scale(image_ballon, (70, 70))
#Image de cage de foot et dimensions
image_filet = pygame.image.load("cagefoot.png")
image_filet = pygame.transform.scale(image_filet, (LARGEUR, 200))

#Couleurs CSS pour animations
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
ROUGE = (255, 0, 0)
BLEU = (50, 50, 255)


#Classes des éléments du jeu
class Gardien:
    def __init__(self):
        self.image = image_gardien
        self.rect = self.image.get_rect(center=(LARGEUR // 2, HAUTEUR // 2))
        self.position = "centre"  # Peut être 'gauche', 'centre' ou 'droite'

    def deplacer_aleatoirement(self):
        """Déplace le gardien soit à droite ou gauche ou au milieu."""
        direction = random.choice(["gauche", "centre", "droite"])
        self.deplacer(direction)

    def deplacer(self, direction):
        if direction == "gauche":
            self.position = "gauche"
            self.rect.centerx = LARGEUR // 3
        elif direction == "droite":
            self.position = "droite"
            self.rect.centerx = 2 * LARGEUR // 3
        else:
            self.position = "centre"
            self.rect.centerx = LARGEUR // 2

    def dessiner(self, fenetre):
        fenetre.blit(self.image, self.rect)


class Ballon:
    def __init__(self):
        self.image = image_ballon
        self.rect = self.image.get_rect(center=(LARGEUR // 2, HAUTEUR - 50))
        self.direction = None

    def tirer(self, direction):
        self.direction = direction

    def deplacer(self):
        if self.direction == "gauche":
            self.rect.x -= 5
            self.rect.y -= 10
        elif self.direction == "droite":
            self.rect.x += 5
            self.rect.y -= 10
        elif self.direction == "centre":
            self.rect.y -= 10

    def dessiner(self, fenetre):
        fenetre.blit(self.image, self.rect)


class Filets:
    def __init__(self):
        self.image = image_filet
        self.rect = self.image.get_rect(topleft=(0, HAUTEUR // 2 - 100))

    def dessiner(self, fenetre):
        fenetre.blit(self.image, self.rect)


class Jeu:
    def __init__(self):
        self.gardien = Gardien()
        self.ballon = Ballon()
        self.filets = Filets()
        self.scores = [0, 0]  #Scores des joueurs
        self.joueur_actif = 0  #0 pour Joueur 1, 1 pour Joueur 2
        self.nb_tirs = 0  #Nombre de tirs du joueur actuel
        self.nb_max_tirs = 5  #Nombrede tirs par manche
        self.police_info = pygame.font.Font(None, 36)
        self.police_score = pygame.font.Font(None, 72)
        self.partie_terminee = False

    def verifier_but(self): #vérifie le but et la collision pour le score
        """Vérifie si le ballon a marqué avec la collision."""
        if self.ballon.direction is None:
            return False

        if self.ballon.rect.top < self.filets.rect.bottom:
            limite_gauche = self.filets.rect.left
            limite_droite = self.filets.rect.right

            if limite_gauche <= self.ballon.rect.centerx <= limite_droite:
                if self.gardien.rect.colliderect(self.ballon.rect):
                    return False  # Arrêt du gardien
                if ((self.ballon.direction == "gauche" and self.gardien.position != "gauche") or
                    (self.ballon.direction == "droite" and self.gardien.position != "droite") or
                    (self.ballon.direction == "centre" and self.gardien.position != "centre")):
                    self.scores[self.joueur_actif] += 1
                    return True
        return False

    def reinitialiser_tir(self): #réset le ballon pour le mettre au point de départ
        """Réinitialise le ballon jusqu'au point de départ et le gardien pour le prochain tir."""
        self.ballon = Ballon()
        self.gardien.deplacer("centre")
        self.nb_tirs += 1
        if self.nb_tirs >= self.nb_max_tirs:
            self.joueur_actif = 1 - self.joueur_actif
            self.nb_tirs = 0
            if self.joueur_actif == 0:
                self.partie_terminee = True

    def dessiner(self, fenetre):
        self.filets.dessiner(fenetre)
        self.gardien.dessiner(fenetre)
        self.ballon.dessiner(fenetre)

        info_texte = self.police_info.render(
            f"Joueur {self.joueur_actif + 1} - Tir {self.nb_tirs + 1}/{self.nb_max_tirs}",
            True, BLEU
        )
        fenetre.blit(info_texte, (LARGEUR // 2 - info_texte.get_width() // 2, 10))

        texte_score = self.police_score.render(f"Score: {self.scores[self.joueur_actif]}", True, BLEU)
        fenetre.blit(texte_score, (LARGEUR // 2 - texte_score.get_width() // 2, HAUTEUR - 550))


def afficher_vainqueur(fenetre, jeu): #Affiche le vainqueur après le jeu 
    horloge = pygame.time.Clock()
    if jeu.scores[0] > jeu.scores[1]:
        message = "Joueur 1 gagne !"
    elif jeu.scores[1] > jeu.scores[0]:
        message = "Joueur 2 gagne !"
    else:
        message = "Egalité !"

    police = pygame.font.Font(None, 72)
    temps = 0
    clignote = True
    while temps < 3000:
        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                pygame.quit()
                return

        fenetre.fill(BLANC)
        texte = police.render(message, True, ROUGE if clignote else NOIR)
        texte_rect = texte.get_rect(center=(LARGEUR // 2, HAUTEUR // 2))
        fenetre.blit(texte, texte_rect)
        pygame.display.flip()
        pygame.time.delay(300)
        clignote = not clignote
        temps += 300
        horloge.tick(60)


def main():
    horloge = pygame.time.Clock()
    #Variable controle du jeu
    en_cours = True
 
    jeu = Jeu() #Initialisation d'un nouvel objet Jeu pour le lancer après
    jeu.gardien.deplacer("centre")#Position du gardiende base

    #Boucle principale du jeu
    while en_cours:
        fenetre.blit(image_fond, (0, 0))
        #Vérifie si la partie est terminée
        if jeu.partie_terminee:
            afficher_vainqueur(fenetre, jeu)
            en_cours = False
            continue
        #Parcours de tous les événements
        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                en_cours = False
            elif evenement.type == pygame.KEYDOWN:
                #Vérifie si le ballon est immobile
                if jeu.ballon.direction is None:
                    # Si la touche "A" tire le ballon vers la gauche
                    if evenement.key == pygame.K_a:
                        jeu.ballon.tirer("gauche")
                        # Le gardien se déplace aléatoirement
                        jeu.gardien.deplacer_aleatoirement()
                    #Si la touche "D" tire ballon vers la droite
                    elif evenement.key == pygame.K_d:
                        jeu.ballon.tirer("droite")
                        # Le gardien se déplace aléatoirement
                        jeu.gardien.deplacer_aleatoirement()
                    #Si la touche "W" tire le ballon centre
                    elif evenement.key == pygame.K_w:
                        jeu.ballon.tirer("centre")
                        #déplacement aléatoire
                        jeu.gardien.deplacer_aleatoirement()

        if jeu.ballon.direction:
            jeu.ballon.deplacer()
            #Vérifie si lacollision avec le gardien
            if jeu.ballon.rect.colliderect(jeu.gardien.rect):
                jeu.reinitialiser_tir()
            #Vérifie si un but est marqué
            elif jeu.verifier_but():
                #Réinitialise le tir après un but
                jeu.reinitialiser_tir()
            elif jeu.ballon.rect.bottom < 0:
                jeu.reinitialiser_tir()

        #Dessineles éléments du jeu
        jeu.dessiner(fenetre)
        pygame.display.flip()
        #Limite la vitesse de la boucle à 60 images/s
        horloge.tick(60)
    pygame.quit()


if __name__ == "__main__":
    main()#lancer le jeu
