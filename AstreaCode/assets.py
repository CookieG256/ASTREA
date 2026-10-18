# assets.py
import pygame
import os

pygame.init()
pygame.mixer.init()

class CarregadorAssets:
    def __init__(self):
        self.sprites = {}
        self.sons = {}

    def carregar_som(self, nome, caminho):
        if os.path.exists(caminho):
            self.sons[nome] = pygame.mixer.Sound(caminho)
        else:
            self.sons[nome] = None

    def tocar_som(self, nome, volume=1.0):
        if nome in self.sons and self.sons[nome]:
            self.sons[nome].set_volume(volume)
            self.sons[nome].play()

    def carregar_sprite(self, nome, caminho):
        if os.path.exists(caminho):
            self.sprites[nome] = pygame.image.load(caminho).convert_alpha()
        else:
            self.sprites[nome] = None
        return self.sprites.get(nome)