import pygame
import random
import math
import os

pygame.init()

# ============================================================
# CONFIG
# ============================================================

WIDTH = 1200
HEIGHT = 750
FPS = 60

TITLE = "NEON SURVIVOR"

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)

clock = pygame.time.Clock()

# ============================================================
# COLORS
# ============================================================

BLACK = (5, 8, 18)
DARK = (10, 15, 30)

WHITE = (245, 250, 255)
CYAN = (0, 230, 255)
BLUE = (50, 120, 255)
PURPLE = (170, 70, 255)
PINK = (255, 60, 170)
RED = (255, 60, 70)
ORANGE = (255, 150, 40)
YELLOW = (255, 230, 70)
GREEN = (50, 255, 130)

# ============================================================
# FONTS
# ============================================================

FONT_SMALL = pygame.font.SysFont("consolas", 18)
FONT_MEDIUM = pygame.font.SysFont("consolas", 26, bold=True)
FONT_BIG = pygame.font.SysFont("consolas", 55, bold=True)
FONT_HUGE = pygame.font.SysFont("consolas", 80, bold=True)

# ============================================================
# UTILITY
# ============================================================

def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def draw_text(surface, text, font, color, x, y, center=False):
    image = font.render(text, True, color)

    if center:
        rect = image.get_rect(center=(x, y))
    else:
        rect = image.get_rect(topleft=(x, y))

    surface.blit(image, rect)

    return rect


# ============================================================
# PARTICLE
# ============================================================

class Particle:

    def __init__(self, x, y, color):

        self.x = x
        self.y = y

        angle = random.uniform(0, math.tau)
        speed = random.uniform(1, 6)

        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

        self.life = random.randint(20, 50)
        self.max_life = self.life

        self.size = random.randint(2, 5)

        self.color = color

    def update(self):

        self.x += self.vx
        self.y += self.vy

        self.vx *= 0.97
        self.vy *= 0.97

        self.life -= 1

    def draw(self, surface):

        if self.life <= 0:
            return

        alpha = self.life / self.max_life

        color = tuple(
            int(c * alpha)
            for c in self.color
        )

        pygame.draw.circle(
            surface,
            color,
            (int(self.x), int(self.y)),
            max(1, int(self.size * alpha))
        )


# ============================================================
# BULLET
# ============================================================

class Bullet:

    def __init__(self, x, y, target):

        self.x = x
        self.y = y

        dx = target[0] - x
        dy = target[1] - y

        length = math.hypot(dx, dy)

        if length == 0:
            length = 1

        speed = 13

        self.vx = dx / length * speed
        self.vy = dy / length * speed

        self.radius = 5

        self.damage = 20

        self.alive = True

    def update(self):

        self.x += self.vx
        self.y += self.vy

        if (
            self.x < -20
            or self.x > WIDTH + 20
            or self.y < -20
            or self.y > HEIGHT + 20
        ):
            self.alive = False

    def draw(self, surface):

        pygame.draw.circle(
            surface,
            CYAN,
            (int(self.x), int(self.y)),
            self.radius
        )

        pygame.draw.circle(
            surface,
            WHITE,
            (int(self.x), int(self.y)),
            2
        )


# ============================================================
# POWER UP
# ============================================================

class PowerUp:

    TYPES = [
        "health",
        "rapid",
        "shield"
    ]

    def __init__(self, x, y):

        self.x = x
        self.y = y

        self.type = random.choice(
            self.TYPES
        )

        self.radius = 16

        self.timer = 0

    def update(self):

        self.timer += 1

    def draw(self, surface):

        colors = {
            "health": GREEN,
            "rapid": YELLOW,
            "shield": BLUE
        }

        symbols = {
            "health": "+",
            "rapid": "R",
            "shield": "S"
        }

        color = colors[self.type]

        pygame.draw.circle(
            surface,
            color,
            (int(self.x), int(self.y)),
            self.radius
        )

        draw_text(
            surface,
            symbols[self.type],
            FONT_MEDIUM,
            BLACK,
            self.x,
            self.y,
            center=True
        )


# ============================================================
# ENEMY
# ============================================================

class Enemy:

    def __init__(self, difficulty):

        side = random.randint(0, 3)

        if side == 0:
            self.x = random.randint(0, WIDTH)
            self.y = -40

        elif side == 1:
            self.x = WIDTH + 40
            self.y = random.randint(0, HEIGHT)

        elif side == 2:
            self.x = random.randint(0, WIDTH)
            self.y = HEIGHT + 40

        else:
            self.x = -40
            self.y = random.randint(0, HEIGHT)

        enemy_type = random.random()

        if enemy_type < 0.65:

            self.type = "normal"

            self.radius = 18
            self.speed = 1.5 + difficulty * 0.05
            self.health = 40 + difficulty * 4
            self.damage = 10

            self.color = RED

            self.points = 10

        elif enemy_type < 0.9:

            self.type = "fast"

            self.radius = 12
            self.speed = 3 + difficulty * 0.08
            self.health = 25 + difficulty * 2
            self.damage = 8

            self.color = ORANGE

            self.points = 20

        else:

            self.type = "tank"

            self.radius = 28
            self.speed = 0.8 + difficulty * 0.03
            self.health = 150 + difficulty * 12
            self.damage = 25

            self.color = PURPLE

            self.points = 50

    def update(self, player):

        dx = player.x - self.x
        dy = player.y - self.y

        length = math.hypot(dx, dy)

        if length:

            self.x += dx / length * self.speed
            self.y += dy / length * self.speed

    def draw(self, surface):

        pygame.draw.circle(
            surface,
            self.color,
            (int(self.x), int(self.y)),
            self.radius
        )

        pygame.draw.circle(
            surface,
            WHITE,
            (int(self.x), int(self.y)),
            max(2, self.radius // 4)
        )

        # Health bar

        max_health = {
            "normal": 40,
            "fast": 25,
            "tank": 150
        }[self.type]

        ratio = clamp(
            self.health / max_health,
            0,
            1
        )

        bar_width = self.radius * 2

        pygame.draw.rect(
            surface,
            (50, 50, 60),
            (
                self.x - self.radius,
                self.y - self.radius - 10,
                bar_width,
                4
            )
        )

        pygame.draw.rect(
            surface,
            GREEN,
            (
                self.x - self.radius,
                self.y - self.radius - 10,
                bar_width * ratio,
                4
            )
        )


# ============================================================
# PLAYER
# ============================================================

class Player:

    def __init__(self):

        self.x = WIDTH / 2
        self.y = HEIGHT / 2

        self.radius = 20

        self.speed = 5

        self.health = 100
        self.max_health = 100

        self.fire_delay = 10
        self.fire_timer = 0

        self.rapid_timer = 0
        self.shield_timer = 0

    def update(self):

        keys = pygame.key.get_pressed()

        dx = 0
        dy = 0

        if keys[
            pygame.K_w
        ] or keys[
            pygame.K_UP
        ]:
            dy -= 1

        if keys[
            pygame.K_s
        ] or keys[
            pygame.K_DOWN
        ]:
            dy += 1

        if keys[
            pygame.K_a
        ] or keys[
            pygame.K_LEFT
        ]:
            dx -= 1

        if keys[
            pygame.K_d
        ] or keys[
            pygame.K_RIGHT
        ]:
            dx += 1

        if dx != 0 or dy != 0:

            length = math.hypot(
                dx,
                dy
            )

            dx /= length
            dy /= length

            self.x += dx * self.speed
            self.y += dy * self.speed

        self.x = clamp(
            self.x,
            self.radius,
            WIDTH - self.radius
        )

        self.y = clamp(
            self.y,
            self.radius,
            HEIGHT - self.radius
        )

        if self.fire_timer > 0:
            self.fire_timer -= 1

        if self.rapid_timer > 0:
            self.rapid_timer -= 1

        if self.shield_timer > 0:
            self.shield_timer -= 1

    def shoot(self, target):

        if self.fire_timer > 0:
            return None

        if self.rapid_timer > 0:
            self.fire_timer = 4
        else:
            self.fire_timer = self.fire_delay

        return Bullet(
            self.x,
            self.y,
            target
        )

    def damage(self, amount):

        if self.shield_timer > 0:
            return

        self.health -= amount

    def draw(self, surface):

        mouse = pygame.mouse.get_pos()

        angle = math.atan2(
            mouse[1] - self.y,
            mouse[0] - self.x
        )

        # Shield

        if self.shield_timer > 0:

            pygame.draw.circle(
                surface,
                BLUE,
                (int(self.x), int(self.y)),
                self.radius + 10,
                3
            )

        # Ship triangle

        size = 25

        points = []

        for offset in [
            0,
            2 * math.pi / 3,
            4 * math.pi / 3
        ]:

            px = self.x + math.cos(
                angle + offset
            ) * size

            py = self.y + math.sin(
                angle + offset
            ) * size

            points.append(
                (px, py)
            )

        pygame.draw.polygon(
            surface,
            CYAN,
            points
        )

        pygame.draw.polygon(
            surface,
            WHITE,
            points,
            2
        )

        # Engine glow

        back_x = self.x - math.cos(angle) * 20
        back_y = self.y - math.sin(angle) * 20

        pygame.draw.circle(
            surface,
            ORANGE,
            (int(back_x), int(back_y)),
            6
        )


# ============================================================
# GAME
# ============================================================

class Game:

    def __init__(self):

        self.player = Player()

        self.bullets = []
        self.enemies = []
        self.particles = []
        self.powerups = []

        self.score = 0

        self.high_score = self.load_high_score()

        self.wave = 1

        self.enemy_timer = 0

        self.wave_timer = 0

        self.game_time = 0

        self.paused = False

        self.game_over = False

        self.stars = []

        for _ in range(150):

            self.stars.append(
                (
                    random.randint(
                        0,
                        WIDTH
                    ),
                    random.randint(
                        0,
                        HEIGHT
                    ),
                    random.randint(
                        1,
                        3
                    )
                )
            )

    # ========================================================
    # HIGH SCORE
    # ========================================================

    def load_high_score(self):

        try:

            with open(
                "highscore.txt",
                "r"
            ) as file:

                return int(
                    file.read()
                )

        except:

            return 0

    def save_high_score(self):

        try:

            with open(
                "highscore.txt",
                "w"
            ) as file:

                file.write(
                    str(self.high_score)
                )

        except:

            pass

    # ========================================================
    # RESET
    # ========================================================

    def reset(self):

        self.__init__()

    # ========================================================
    # UPDATE
    # ========================================================

    def update(self):

        if self.paused or self.game_over:
            return

        self.game_time += 1

        # Difficulty

        difficulty = max(
            1,
            self.wave
        )

        # Player

        self.player.update()

        # Enemy spawning

        self.enemy_timer -= 1

        spawn_delay = max(
            12,
            55 - difficulty * 2
        )

        if self.enemy_timer <= 0:

            self.enemy_timer = spawn_delay

            self.enemies.append(
                Enemy(difficulty)
            )

        # Wave progression

        self.wave_timer += 1

        if self.wave_timer >= FPS * 20:

            self.wave_timer = 0

            self.wave += 1

        # Bullets

        for bullet in self.bullets:

            bullet.update()

        self.bullets = [
            bullet
            for bullet in self.bullets
            if bullet.alive
        ]

        # Enemies

        for enemy in self.enemies:

            enemy.update(
                self.player
            )

        # Particles

        for particle in self.particles:

            particle.update()

        self.particles = [
            particle
            for particle in self.particles
            if particle.life > 0
        ]

        # Powerups

        for powerup in self.powerups:

            powerup.update()

        self.handle_collisions()

        # Death

        if self.player.health <= 0:

            self.game_over = True

            if self.score > self.high_score:

                self.high_score = self.score

                self.save_high_score()

    # ========================================================
    # COLLISIONS
    # ========================================================

    def handle_collisions(self):

        # Bullets vs enemies

        for bullet in self.bullets:

            for enemy in self.enemies:

                if distance(
                    (bullet.x, bullet.y),
                    (enemy.x, enemy.y)
                ) < enemy.radius + bullet.radius:

                    enemy.health -= bullet.damage

                    bullet.alive = False

                    for _ in range(4):

                        self.particles.append(
                            Particle(
                                bullet.x,
                                bullet.y,
                                enemy.color
                            )
                        )

                    if enemy.health <= 0:

                        self.score += enemy.points

                        for _ in range(20):

                            self.particles.append(
                                Particle(
                                    enemy.x,
                                    enemy.y,
                                    enemy.color
                                )
                            )

                        if random.random() < 0.08:

                            self.powerups.append(
                                PowerUp(
                                    enemy.x,
                                    enemy.y
                                )
                            )

                        enemy.x = -10000

                    break

        self.enemies = [
            enemy
            for enemy in self.enemies
            if enemy.x > -5000
        ]

        # Enemies vs player

        for enemy in self.enemies:

            if distance(
                (self.player.x, self.player.y),
                (enemy.x, enemy.y)
            ) < (
                enemy.radius
                +
                self.player.radius
            ):

                self.player.damage(
                    enemy.damage
                )

                enemy.x = -10000

                for _ in range(12):

                    self.particles.append(
                        Particle(
                            self.player.x,
                            self.player.y,
                            RED
                        )
                    )

        self.enemies = [
            enemy
            for enemy in self.enemies
            if enemy.x > -5000
        ]

        # Powerups vs player

        remaining_powerups = []

        for powerup in self.powerups:

            if distance(
                (self.player.x, self.player.y),
                (powerup.x, powerup.y)
            ) < (
                self.player.radius
                +
                powerup.radius
            ):

                if powerup.type == "health":

                    self.player.health = min(
                        self.player.max_health,
                        self.player.health + 30
                    )

                elif powerup.type == "rapid":

                    self.player.rapid_timer = FPS * 8

                elif powerup.type == "shield":

                    self.player.shield_timer = FPS * 6

            else:

                remaining_powerups.append(
                    powerup
                )

        self.powerups = remaining_powerups

    # ========================================================
    # SHOOT
    # ========================================================

    def shoot(self):

        if self.game_over:
            return

        target = pygame.mouse.get_pos()

        bullet = self.player.shoot(
            target
        )

        if bullet:

            self.bullets.append(
                bullet
            )

    # ========================================================
    # DRAW BACKGROUND
    # ========================================================

    def draw_background(self):

        screen.fill(
            BLACK
        )

        # Stars

        for x, y, size in self.stars:

            pygame.draw.circle(
                screen,
                (40, 55, 80),
                (x, y),
                size
            )

        # Grid

        grid_size = 60

        for x in range(
            0,
            WIDTH,
            grid_size
        ):

            pygame.draw.line(
                screen,
                (12, 24, 45),
                (x, 0),
                (x, HEIGHT)
            )

        for y in range(
            0,
            HEIGHT,
            grid_size
        ):

            pygame.draw.line(
                screen,
                (12, 24, 45),
                (0, y),
                (WIDTH, y)
            )

    # ========================================================
    # DRAW
    # ========================================================

    def draw(self):

        self.draw_background()

        # Particles

        for particle in self.particles:

            particle.draw(
                screen
            )

        # Powerups

        for powerup in self.powerups:

            powerup.draw(
                screen
            )

        # Bullets

        for bullet in self.bullets:

            bullet.draw(
                screen
            )

        # Enemies

        for enemy in self.enemies:

            enemy.draw(
                screen
            )

        # Player

        self.player.draw(
            screen
        )

        self.draw_hud()

        if self.paused:

            self.draw_pause()

        if self.game_over:

            self.draw_game_over()

        pygame.display.flip()

    # ========================================================
    # HUD
    # ========================================================

    def draw_hud(self):

        # Score

        draw_text(
            screen,
            f"SCORE  {self.score}",
            FONT_MEDIUM,
            WHITE,
            20,
            18
        )

        draw_text(
            screen,
            f"WAVE  {self.wave}",
            FONT_MEDIUM,
            CYAN,
            20,
            50
        )

        draw_text(
            screen,
            f"BEST  {self.high_score}",
            FONT_SMALL,
            (160, 180, 210),
            20,
            85
        )

        # Health bar

        bar_x = WIDTH - 270
        bar_y = 25
        bar_w = 230
        bar_h = 20

        pygame.draw.rect(
            screen,
            (40, 45, 60),
            (
                bar_x,
                bar_y,
                bar_w,
                bar_h
            )
        )

        health_ratio = clamp(
            self.player.health /
            self.player.max_health,
            0,
            1
        )

        health_color = GREEN

        if health_ratio < 0.35:
            health_color = RED

        pygame.draw.rect(
            screen,
            health_color,
            (
                bar_x,
                bar_y,
                bar_w * health_ratio,
                bar_h
            )
        )

        draw_text(
            screen,
            f"HP {max(0, int(self.player.health))}",
            FONT_SMALL,
            WHITE,
            bar_x,
            52
        )

        # Powerups

        if self.player.rapid_timer > 0:

            draw_text(
                screen,
                "⚡ RAPID FIRE",
                FONT_SMALL,
                YELLOW,
                WIDTH - 200,
                85
            )

        if self.player.shield_timer > 0:

            draw_text(
                screen,
                "◉ SHIELD",
                FONT_SMALL,
                BLUE,
                WIDTH - 200,
                110
            )

    # ========================================================
    # PAUSE
    # ========================================================

    def draw_pause(self):

        overlay = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        overlay.fill(
            (0, 0, 0, 170)
        )

        screen.blit(
            overlay,
            (0, 0)
        )

        draw_text(
            screen,
            "PAUSED",
            FONT_HUGE,
            WHITE,
            WIDTH // 2,
            HEIGHT // 2 - 40,
            center=True
        )

        draw_text(
            screen,
            "Press P to continue",
            FONT_MEDIUM,
            CYAN,
            WIDTH // 2,
            HEIGHT // 2 + 50,
            center=True
        )

    # ========================================================
    # GAME OVER
    # ========================================================

    def draw_game_over(self):

        overlay = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        overlay.fill(
            (0, 0, 0, 190)
        )

        screen.blit(
            overlay,
            (0, 0)
        )

        draw_text(
            screen,
            "GAME OVER",
            FONT_HUGE,
            RED,
            WIDTH // 2,
            HEIGHT // 2 - 100,
            center=True
        )

        draw_text(
            screen,
            f"Score: {self.score}",
            FONT_BIG,
            WHITE,
            WIDTH // 2,
            HEIGHT // 2,
            center=True
        )

        draw_text(
            screen,
            f"Best: {self.high_score}",
            FONT_MEDIUM,
            YELLOW,
            WIDTH // 2,
            HEIGHT // 2 + 65,
            center=True
        )

        draw_text(
            screen,
            "Press R to restart",
            FONT_MEDIUM,
            CYAN,
            WIDTH // 2,
            HEIGHT // 2 + 125,
            center=True
        )

    # ========================================================
    # MAIN LOOP
    # ========================================================

    def run(self):

        running = True

        while running:

            clock.tick(
                FPS
            )

            for event in pygame.event.get():

                if event.type == pygame.QUIT:

                    running = False

                elif event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_ESCAPE:

                        running = False

                    elif event.key == pygame.K_p:

                        if not self.game_over:

                            self.paused = not self.paused

                    elif event.key == pygame.K_r:

                        if self.game_over:

                            self.reset()

                elif event.type == pygame.MOUSEBUTTONDOWN:

                    if event.button == 1:

                        if not self.paused:

                            self.shoot()

            self.update()

            self.draw()

        pygame.quit()


# ============================================================
# START GAME
# ============================================================

if __name__ == "__main__":

    game = Game()

    game.run()
