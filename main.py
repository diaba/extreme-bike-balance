import pygame
import sys
import os
import random
import pickle
from pygame.locals import *


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Example Usage in your Bike class:
# path = resource_path("assets/bike1.png")
# img = pygame.image.load(path).convert_alpha()





# --- 1. GLOBAL CONFIGURATION ---
WIDTH, HEIGHT = 800, 600
WHITE, GOLD, RED, BLUE = (255, 255, 255), (255, 215, 0), (255, 50, 50), (0, 180, 255)
NITRO_COLOR = (0, 200, 255)

# Background color options: (Label, RGB Tuple, Text Color for HUD)
BG_THEMES = {
    "K": ("BLACK", (15, 15, 25), WHITE),
    "L": ("WHITE", (240, 240, 240), (20, 20, 20)),
    "G": ("GREEN", (34, 139, 34), WHITE)
}

BIKE_CONFIGS = {
    "1": {"name": "Agile Scout", "grav": 0.0012, "lean": 0.12, "speed": 0.9, "color": (100, 255, 100), "img": "./assets/bike1.png"},
    "2": {"name": "Balanced Pro", "grav": 0.0022, "lean": 0.08, "speed": 1.1, "color": (100, 180, 255), "img": "./assets/bike2.png"},
    "3": {"name": "Heavy Beast",  "grav": 0.0038, "lean": 0.05, "speed": 1.5, "color": (255, 80, 80), "img": "./assets/bike3.jpg"}
}

# --- 2. WEATHER SYSTEM (Same as before) ---
class WeatherSystem:
    def __init__(self):
        self.wind_force = 0.0
        self.target_wind = 0.0
        self.timer = 0
        self.rain_drops = []

    def update(self):
        self.timer += 1
        if self.timer % 180 == 0:
            self.target_wind = random.uniform(-0.012, 0.012)
        self.wind_force += (self.target_wind - self.wind_force) * 0.02

        if len(self.rain_drops) < 60:
            self.rain_drops.append([random.randint(-200, WIDTH+200), random.randint(-100, 0), random.randint(7, 12)])
        
        for drop in self.rain_drops:
            drop[1] += drop[2]
            drop[0] += self.wind_force * 300
            if drop[1] > HEIGHT:
                drop[1] = random.randint(-50, -10)
                drop[0] = random.randint(-200, WIDTH+200)

    def draw(self, screen, font, rain_color):
        for drop in self.rain_drops:
            end_x = drop[0] + (self.wind_force * 500)
            pygame.draw.line(screen, rain_color, (drop[0], drop[1]), (end_x, drop[1] + 8), 1)

# --- 3. BIKE OBJECT (Same as before) ---
class Bike:
    def __init__(self, specs):
        self.specs = specs
        self.image = self.load_scaled(specs['img'], specs['color'], int(HEIGHT * 0.18))
        self.menu_thumb = self.load_scaled(specs['img'], specs['color'], 80)
        self.reset()

    def load_scaled(self, path, color, target_h):
        try:
            img = pygame.image.load(path).convert_alpha()
        except:
            img = pygame.Surface((target_h * 2, target_h), pygame.SRCALPHA)
            pygame.draw.ellipse(img, color, [0, target_h//2, target_h*2, target_h//2])
        ratio = img.get_width() / img.get_height()
        return pygame.transform.smoothscale(img, (int(target_h * ratio), target_h))

    def reset(self):
        self.angle = 0
        self.angular_velocity = 0
        self.boost_fuel = 100
        self.rect_center = (WIDTH // 2, HEIGHT // 2 + 100)

    def update(self, keys, score, wind_force):
        is_boosting = keys[K_SPACE] and self.boost_fuel > 0
        gravity = self.specs['grav'] + (score / 50000)
        lean_power = self.specs['lean'] * (1.5 if is_boosting else 1.0)
        self.angular_velocity += (self.angle * (gravity * 0.6 if is_boosting else gravity)) + wind_force
        if keys[K_w]: self.angular_velocity -= lean_power
        if keys[K_s]: self.angular_velocity += lean_power
        self.angle += self.angular_velocity
        if is_boosting: self.boost_fuel -= 0.7
        elif self.boost_fuel < 100: self.boost_fuel += 0.15
        return is_boosting

    def draw(self, screen):
        rotated = pygame.transform.rotate(self.image, -self.angle)
        rect = rotated.get_rect(center=self.rect_center)
        screen.blit(rotated, rect.topleft)

# --- 4. MAIN GAME ENGINE ---
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 22, bold=True)
        self.state = "MENU"
        self.score = 0
        self.high_score = self.load_record()
        self.weather = WeatherSystem()
        
        # Default Theme
        self.bg_key = "K" 
        self.menu_bikes = {k: Bike(v) for k, v in BIKE_CONFIGS.items()}

    def load_record(self):
        if os.path.exists("record.pkl"):
            with open("record.pkl", "rb") as f: return pickle.load(f)
        return 0

    def draw_menu(self):
        theme_info = BG_THEMES[self.bg_key]
        self.screen.fill(theme_info[1])
        txt_col = theme_info[2]

        title = self.font.render("GARAGE: SELECT RIDE & THEME", True, txt_col if self.bg_key != "L" else (50,50,50))
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 20))

        # Theme selection UI
        theme_txt = self.font.render(f"Theme: {theme_info[0]} (Press [K] Black, [L] White, [G] Green)", True, txt_col)
        self.screen.blit(theme_txt, (WIDTH//2 - theme_txt.get_width()//2, 60))

        for i, (key, bike_obj) in enumerate(self.menu_bikes.items()):
            x = 60 + (i * 240); rect = pygame.Rect(x, 110, 220, 420)
            pygame.draw.rect(self.screen, (40, 40, 50) if self.bg_key != "L" else (200, 200, 200), rect, border_radius=15)
            pygame.draw.rect(self.screen, bike_obj.specs['color'], rect, 2, border_radius=15)
            
            thumb = bike_obj.menu_thumb
            self.screen.blit(thumb, (x + 110 - thumb.get_width()//2, 200))
            
            prompt = self.font.render(f"START [{key}]", True, bike_obj.specs['color'])
            self.screen.blit(prompt, (x + 110 - prompt.get_width()//2, 460))

    def run(self):
        while True:
            keys = pygame.key.get_pressed()
            theme_info = BG_THEMES[self.bg_key]
            
            for event in pygame.event.get():
                if event.type == QUIT: pygame.quit(); sys.exit()
                
                if self.state == "MENU" and event.type == KEYDOWN:
                    # Bike selection
                    if event.unicode in BIKE_CONFIGS:
                        self.bike = Bike(BIKE_CONFIGS[event.unicode])
                        self.score = 0
                        self.state = "PLAYING"
                    # Background selection
                    if event.unicode.upper() in BG_THEMES:
                        self.bg_key = event.unicode.upper()
                
                if self.state == "GAMEOVER" and event.type == KEYDOWN:
                    if event.key == K_r: self.state = "MENU"

            if self.state == "MENU":
                self.draw_menu()
            elif self.state == "PLAYING":
                self.update_playing(keys, theme_info)
            elif self.state == "GAMEOVER":
                self.draw_gameover(theme_info)

            pygame.display.flip()
            self.clock.tick(60)

    def update_playing(self, keys, theme):
        self.weather.update()
        is_boosting = self.bike.update(keys, self.score, self.weather.wind_force)
        self.score += 2 if is_boosting else 1
        
        self.screen.fill(theme[1])
        # Rain color changes based on background for visibility
        rain_col = (200, 200, 255) if self.bg_key != "L" else (100, 100, 150)
        self.weather.draw(self.screen, self.font, rain_col)
        self.bike.draw(self.screen)
        self.draw_hud(theme[2])

        if abs(self.bike.angle) > 90:
            self.state = "GAMEOVER"
            if self.score > self.high_score:
                self.high_score = self.score
                with open("record.pkl", "wb") as f: pickle.dump(self.high_score, f)

    def draw_hud(self, txt_col):
        score_txt = self.font.render(f"DIST: {self.score//10}m", True, txt_col)
        self.screen.blit(score_txt, (20, 20))
        # Nitro Bar
        pygame.draw.rect(self.screen, (100, 100, 100), (20, 55, 150, 10))
        pygame.draw.rect(self.screen, NITRO_COLOR, (20, 55, self.bike.boost_fuel * 1.5, 10))

    def draw_gameover(self, theme):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0,0))
        msg = self.font.render("WIPEOUT! Press R for Garage", True, RED)
        self.screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2))

if __name__ == "__main__":
    Game().run()