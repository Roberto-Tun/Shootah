#importing modules
import pygame
from pygame.locals import *
from pygame import mixer
import os
import time
import random

#initializing pygame font module and mixer module
pygame.font.init()
pygame.mixer.init(44100, -16, 2, 512)

WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shootah")

#loading sounds and setting their volumes
pygame.mixer.music.load("assets/music.mp3")
pygame.mixer.music.set_volume(0.09)
pygame.mixer.music.play(-1)
game_over_fx = pygame.mixer.Sound("assets/game_over.mp3")
game_over_fx.set_volume(0.8)
hit = pygame.mixer.Sound("assets/gugu.mp3")
hit.set_volume(0.4)
Level_inc = pygame.mixer.Sound("assets/Level_inc.mp3")
Level_inc.set_volume(0.6)


#Loading Enemy Ships
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "Coconut_lady.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "Guatemala.png"))

#Loading Healer Ship
FOOD_SPACE_SHIP = pygame.image.load(os.path.join("assets", "Garifuna.png"))

#Loading Player Ship
PLAYER_SPACE_SHIP = pygame.image.load(os.path.join("assets", "Choco.png"))

#Food Laser
FOOD_LASER = pygame.image.load(os.path.join("assets", "R_B.png"))

# Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "Coco.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "Machette.png"))


# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)

class Food:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                hit.play(0)
                self.lasers.remove(laser)


    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

class Healer_Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.foods = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for food in self.foods:
            food.draw(window)

    def move_foods(self, vel, obj):
        self.cooldown()
        for food in self.foods:
            food.move(vel)
            if food.off_screen(HEIGHT):
                self.foods.remove(food)
            elif food.collision(obj):
                obj.health += 10
                if obj.health > 100:
                    obj.health = 100
                self.foods.remove(food)


    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            food = Food(self.x, self.y, self.food_img)
            self.food.append(food)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = PLAYER_SPACE_SHIP
        self.ship_img = pygame.transform.scale(self.ship_img,(80, 65))
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))


class Enemy(Ship):
    COLOR_MAP = {
                "red": (RED_SPACE_SHIP, RED_LASER),
                "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
                }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.ship_img = pygame.transform.scale(self.ship_img, (80, 65))
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

class Healer(Healer_Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = FOOD_SPACE_SHIP
        self.ship_img = pygame.transform.scale(self.ship_img, (80, 65))
        self.food_img = FOOD_LASER
        self.food_img = pygame.transform.scale(self.food_img, (65, 65))
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.food_img)
            self.foods.append(laser)
            self.cool_down_counter = 1



def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
    run = True
    FPS = 60
    level = 0
    main_font = pygame.font.SysFont("Orbitron", 40)
    lost_font = pygame.font.SysFont("Orbitron", 40)

    enemies = []
    healers = []
    wave_length = 5
    healer_length = 1
    enemy_vel = 1
    healer_vel = 1

    player_vel = 5
    laser_vel = 5

    player = Player(300, 630)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        WIN.blit(BG, (0,0))
        # draw text
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))
        WIN.blit(level_label, (WIDTH - level_label.get_width() -290, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)
        for healer in healers:
            healer.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("You Lost!!", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if player.health <= 0:
            lost = True
            lost_count += 1
            game_over_fx.play(0)
        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            Level_inc.play(0)
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue"]))
                enemies.append(enemy)
        if len(healers) == 0:
            healer_length += 2
            for i in range(healer_length):
                healer = Healer(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100), FOOD_SPACE_SHIP)
                healers.append(healer)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0: # left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: # right
            player.x += player_vel

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                enemies.remove(enemy)
        for healer in healers[:]:
            healer.move(healer_vel)
            healer.move_foods(laser_vel, player)

            if random.randrange(0, 2*60) == 1:
                healer.shoot()

            if collide(healer, player):
                player.health += 10
                healers.remove(healer)
                if player.health > 100:
                    player.health = 100

            elif healer.y + healer.get_height() > HEIGHT:
                healers.remove(healer)

        player.move_lasers(-laser_vel, enemies,)
        player.move_lasers(-laser_vel, healers)

def main_menu():
    title_font = pygame.font.SysFont("Orbitron", 40)
    run = True
    while run:
        WIN.blit(BG, (0,0))
        title_label = title_font.render("Press The Mouse to Begin...", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()