import llms.deepgram
import pygame
import os

chosen_model = "deepgram"


def play_sound(data):
    if chosen_model == "deepgram":
        llms.deepgram.make_audio(data)
        pygame.mixer.init()
        sound = pygame.mixer.Sound(os.path.dirname(__file__) + "/audio.mp3")
        sound.play()
