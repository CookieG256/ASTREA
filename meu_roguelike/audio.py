# audio.py
import pygame
import numpy as np

class GerenciadorAudio:
    def __init__(self):
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2)
            self.ativo = True
        except:
            self.ativo = False

    def tocar_som(self, tipo):
        if not self.ativo: return
        try:
            sample_rate = 22050; duracao = 0.1
            t = np.linspace(0, duracao, int(sample_rate * duracao), endpoint=False)
            freq = np.linspace(800, 200, len(t)) if tipo == "tiro" else np.linspace(150, 60, len(t))
            onda = np.int16(32767 * np.sin(2 * np.pi * freq * t))
            pygame.sndarray.make_sound(np.column_stack((onda, onda))).play()
        except:
            pass