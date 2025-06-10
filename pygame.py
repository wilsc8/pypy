import pygame
from random import randint

pygame.init()
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)


# Класс игрока
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        side_length = 50
        height = int(side_length * (3 ** 0.5) / 2)

        points = [
            (side_length // 2, 0),
            (0, height),
            (side_length, height)
        ]

        self.image = pygame.Surface([side_length, height], pygame.SRCALPHA)
        pygame.draw.polygon(self.image, BLUE, points)
        self.rect = self.image.get_rect(center=(screen_width // 2, screen_height - 70))
        self.speed_x = 0
        self.speed_y = 0
        self.bullet_timer = 0
        self.speed_bonus_time = 0

    def update(self):
        keys = pygame.key.get_pressed()
        self.speed_x = 0
        self.speed_y = 0

        speed_multiplier = 0.5
        if self.speed_bonus_time > pygame.time.get_ticks():
            speed_multiplier *= 2

        if keys[pygame.K_LEFT]:
            self.speed_x -= 12 * speed_multiplier
        elif keys[pygame.K_RIGHT]:
            self.speed_x += 12 * speed_multiplier
        if keys[pygame.K_UP]:
            self.speed_y -= 5 * speed_multiplier

        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > screen_width:
            self.rect.right = screen_width
        if self.rect.top < 0:
            self.rect.top = 0
        elif self.rect.bottom > screen_height:
            self.rect.bottom = screen_height

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.bullet_timer > 300:
            self.bullet_timer = now
            return True
        else:
            return False


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        square_size = 33
        self.image = pygame.Surface([square_size, square_size])
        self.image.fill(RED)
        self.rect = self.image.get_rect(midbottom=(randint(0, screen_width), 0))
        self.speed_y = randint(2, 4)

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top >= screen_height:
            self.kill()


class Bonus(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        bonus_size = 22
        self.image = pygame.Surface([bonus_size, bonus_size])
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(midbottom=(randint(0, screen_width), 0))
        self.speed_y = 2

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top >= screen_height:
            self.kill()



class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([10, 10])
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=(x, y)).inflate(-2, -2)
        self.speed_y = -40

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.bottom <= 0:
            self.kill()


def draw_text(surf, text, size, x, y, color=WHITE):
    font = pygame.font.SysFont("arial", size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    surf.blit(text_surface, text_rect)


def show_menu_screen():
    menu_running = True
    while menu_running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    menu_running = False

        screen.fill(BLACK)
        draw_text(screen, 'Стрелялка', 64, screen_width // 2, screen_height // 4)
        draw_text(screen, 'Нажмите Enter или Пробел, чтобы начать', 22, screen_width // 2, screen_height * 3 // 4)
        pygame.display.flip()


def spawn_enemy():
    new_enemy = Enemy()
    all_sprites.add(new_enemy)
    enemies.add(new_enemy)


def spawn_bonus():
    new_bonus = Bonus()
    all_sprites.add(new_bonus)
    bonuses.add(new_bonus)


all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bonuses = pygame.sprite.Group()
bullets = pygame.sprite.Group()
player = Player()
all_sprites.add(player)

show_menu_screen()
score_value = 0
running = True
paused = False
bonus_active_until = None

while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                paused = not paused
            elif event.key == pygame.K_SPACE and not paused:
                if player.shoot():
                    vertex_position = (
                        player.rect.centerx,
                        player.rect.top
                    )
                    bullet = Bullet(*vertex_position)
                    all_sprites.add(bullet)
                    bullets.add(bullet)

    if not paused:
        all_sprites.update()

        collisions = pygame.sprite.groupcollide(bonuses, bullets, True, True)
        for _ in collisions.keys():
            player.speed_bonus_time = pygame.time.get_ticks() + 5000
            bonus_active_until = pygame.time.get_ticks() + 2000

        hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
        for _ in hits:
            score_value += 5
            spawn_enemy()

        if len(bonuses) < 2:
            spawn_bonus()

        if len(enemies) < 3:
            spawn_enemy()

        screen.fill(BLACK)
        all_sprites.draw(screen)

        current_time = pygame.time.get_ticks()
        if bonus_active_until is not None and current_time < bonus_active_until:
            draw_text(screen, 'БОНУС!', 40, screen_width // 2, 20, PURPLE)
        else:
            bonus_active_until = None

        draw_text(screen, f'Очки: {score_value}', 30, 50, 15)
    else:
        draw_text(screen, 'Игра приостановлена', 64, screen_width // 2, screen_height // 2)
        draw_text(screen, 'Нажмите ESC, чтобы продолжить', 22, screen_width // 2, screen_height * 3 // 4)

    pygame.display.flip()

pygame.quit()
