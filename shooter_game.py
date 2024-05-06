# Імпорт необхідних модулів та класів
from pygame import *
from random import randint
from time import time as timer

# Ініціалізація Pygame та музики
mixer.init()
mixer.music.load('maintheme.ogg')
mixer.music.play()
fire_sound = mixer.Sound('fire.ogg')

# Ініціалізація шрифтів
font.init()
font1 = font.SysFont("Arial", 36)
font2 = font.SysFont("Arial", 80)
win = font2.render('YOU WIN!', True, (255, 255, 255))
lose = font2.render('YOU LOSE!', True, (180, 0, 0))

# Шляхи до зображень
img_back = "ss.png"
img_hero = "pz4g.png"  # Початкове зображення танка
img_enemy = "sherman.png"  # Зображення ворога шермана
img_ast = "kw2.png"  # Зображення кв2
img_bullet = "bullet.png"  # Зображення кулі
img_hero_damaged = "pz4g_damaged.png"  # Зображення танка при пошкодженні
img_hero_heavily_damaged = "pz4g_heavily_damaged.png"  # Зображення танка при сильному пошкодженні
img_hero_fatal_damage = "pz4g_fatal_damage.png"  # Зображення танка при фатальному пошкодженні

# Глобальні змінні для гри
score = 0
lost = 0
goal = 10
max_lost = 4
life = 3


# Функція для оновлення зображення танка
def update_tank_image():
    if life == 2:
        ship.image = transform.scale(image.load(img_hero_damaged), (ship.rect.width, ship.rect.height))
    elif life == 1:
        ship.image = transform.scale(image.load(img_hero_heavily_damaged), (ship.rect.width, ship.rect.height))


# Клас для спрайтів гри
class GameSprite(sprite.Sprite):
    def __init__(self, sprite_img, sprite_x, sprite_y, size_x, size_y, sprite_speed):
        super().__init__()
        self.image = transform.scale(image.load(sprite_img), (size_x, size_y))
        self.speed = sprite_speed
        self.rect = self.image.get_rect()
        self.rect.x = sprite_x
        self.rect.y = sprite_y

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))


# Клас для головного героя
class Player(GameSprite):
    def update(self):
        keys = key.get_pressed()
        if keys[K_a] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_d] and self.rect.x < win_width - 80:
            self.rect.x += self.speed
        if keys[K_w] and self.rect.y > win_height / 2:  # Рух вгору при натисканні клавіші W
            self.rect.y -= self.speed
        if keys[K_s] and self.rect.y < win_height - self.rect.height:
            self.rect.y += self.speed

    def fire(self):
        bullet = Bullet(img_bullet, self.rect.centerx, self.rect.top, 15, 20, -15)
        bullets.add(bullet)

    def decrease_hp(self):
        global life
        life -= 1
        if life <= 0:
            life = 0
        update_tank_image()  # Оновлюємо зображення танка


# Клас для ворогів
class Enemy(GameSprite):
    def update(self):
        self.rect.y += self.speed
        global lost
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 40)
            self.rect.y = 0
            lost += 1

    @staticmethod
    def respawn():
        if randint(1, 5) <= 2:  # Змінюємо ймовірність респавну на 20%
            num_enemies = 1
        else:
            num_enemies = 2

        for _ in range(num_enemies):
            enemy = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 120, randint(1, 3))
            monsters.add(enemy)


# Клас для астероїдів
class Asteroid(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 10)
            self.rect.y = 0


# Клас для куль
class Bullet(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y < 0:
            self.kill()


# Габарити вікна гри
win_width = 1000
win_height = 700
window = display.set_mode((win_width, win_height))
display.set_caption("Shooter")
background = transform.scale(image.load(img_back), (win_width, win_height))

# Створення головного героя
ship = Player(img_hero, 5, win_height - 170, 80, 170, 10)

# Групи спрайтів
bullets = sprite.Group()
monsters = sprite.Group()
asteroids = sprite.Group()

# Додавання ворогів
for i in range(1, 2):
    monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 150, randint(1, 3))
    monsters.add(monster)

# Додавання астероїдів
for i in range(1, 3):
    asteroid = Asteroid(img_ast, randint(30, win_width - 30), -40, 80, 150, randint(1, 2))
    asteroids.add(asteroid)

# Основний цикл гри
run = True
finish = False
clock = time.Clock()
FPS = 30
rel_time = False
num_fire = 0

# Основний геймплей
while run:
    for e in event.get():
        if e.type == QUIT:
            run = False
        elif e.type == KEYDOWN and not finish:
            if e.key == K_SPACE:
                if num_fire < 1 and not rel_time:
                    num_fire += 1
                    fire_sound.play()
                    ship.fire()

                if num_fire >= 1 and not rel_time:
                    last_time = timer()
                    rel_time = True

    if not finish:
        window.blit(background, (0, 0))
        ship.update()
        monsters.update()
        bullets.update()
        asteroids.update()

        ship.reset()
        monsters.draw(window)
        bullets.draw(window)
        asteroids.draw(window)

        if rel_time:
            now_time = timer()
            if now_time - last_time < 2:
                reload = font2.render('перезарядка...', 1, (150, 70, 0))
                window.blit(reload, (win_width / 2 - 200, win_height - 100))
            else:
                num_fire = 0
                rel_time = False

        collides = sprite.groupcollide(monsters, bullets, True, True)
        for collide in collides:
            score += 1
            Enemy.respawn()  # Респавн ворогів після знищення

        if sprite.spritecollide(ship, monsters, False) or sprite.spritecollide(ship, asteroids, False):
            sprite.spritecollide(ship, monsters, True)
            sprite.spritecollide(ship, asteroids, True)
            ship.decrease_hp()

        if life == 0 or lost >= max_lost:
            finish = True
            window.blit(lose, (200, 200))

        if score >= goal:
            finish = True
            window.blit(win, (200, 200))

        text = font1.render("Рахунок: " + str(score), 1, (255, 255, 255))
        window.blit(text, (10, 20))

        text_lose = font1.render("Пропуски: " + str(lost), 1, (230, 30, 70))
        window.blit(text_lose, (10, 50))

        text_life = font1.render("Життя: " + str(life), 1, (0, 150, 0))
        window.blit(text_life, (850, 10))

        # Додавання ворогів та астероїдів
        if len(monsters) == 0:
            Enemy.respawn()

        if len(asteroids) == 0:
            for _ in range(randint(2, 3)):
                asteroid = Asteroid(img_ast, randint(30, win_width - 30), -40, 80, 150, randint(1, 2))
                asteroids.add(asteroid)

        display.update()

    clock.tick(FPS)
