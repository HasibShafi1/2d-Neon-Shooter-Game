import numpy as np
import pygame

def generate_square_wave(frequency, duration, sample_rate=44100, volume=0.5):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = np.sign(np.sin(frequency * t * 2 * np.pi))
    # Fade out
    fade = np.linspace(1.0, 0.0, len(wave))
    wave = wave * fade * volume
    
    # Convert to 16-bit integer format
    audio = np.int16(wave * 32767)
    # Duplicate to stereo
    stereo = np.column_stack((audio, audio))
    return pygame.sndarray.make_sound(stereo)

def generate_noise(duration, sample_rate=44100, volume=0.5):
    t = int(sample_rate * duration)
    wave = np.random.uniform(-1.0, 1.0, t)
    # Fade out
    fade = np.linspace(1.0, 0.0, len(wave))
    wave = wave * fade * volume
    
    audio = np.int16(wave * 32767)
    stereo = np.column_stack((audio, audio))
    return pygame.sndarray.make_sound(stereo)

class SoundManager:
    def __init__(self):
        # Initialize mixer if not already initialized
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            
        self.shoot_sound = generate_square_wave(880.0, 0.1, volume=0.2) # High pitch pew
        self.explosion_sound = generate_noise(0.3, volume=0.4)          # White noise explosion
        self.enemy_hit_sound = generate_square_wave(220.0, 0.1, volume=0.3) # Low pitch hit

    def play_shoot(self):
        self.shoot_sound.play()

    def play_explosion(self):
        self.explosion_sound.play()
        
    def play_enemy_hit(self):
        self.enemy_hit_sound.play()
