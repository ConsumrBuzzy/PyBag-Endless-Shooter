import pygame
import random
import math
import asyncio
import sys

# Initialize Pygame
pygame.init()

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SIZE = 32
ENEMY_SIZE = 32
BULLET_SIZE = 8
PLAYER_SPEED = 5
ENEMY_SPEED = 2
BULLET_SPEED = 7
SPAWN_RATE = 1000
MIN_SPAWN_DISTANCE = 200
MAX_SPAWN_ATTEMPTS = 10
FIRE_RATE = 120
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
FPS = 60

# --- Helper Functions ---
def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# --- Game Object Classes ---
class DebugButton:
    def __init__(self):
        self.rect = pygame.Rect(SCREEN_WIDTH - 100, 10, 80, 30)
        self.text = "Debug: ON"
        self.active = True
        self.font = pygame.font.Font(None, 24)

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect, 2)
        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.FINGERDOWN:
            touch_x = event.x * SCREEN_WIDTH
            touch_y = event.y * SCREEN_HEIGHT
            if self.rect.collidepoint(touch_x, touch_y):
                self.toggle()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.toggle()

    def toggle(self):
        self.active = not self.active
        self.text = "Debug: ON" if self.active else "Debug: OFF"

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.base_image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
        pygame.draw.polygon(self.base_image, GREEN, [
            (0, PLAYER_SIZE),
            (0, 0),
            (PLAYER_SIZE, PLAYER_SIZE/2)
        ])
        self.image = self.base_image
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.angle = 0
        self.is_shooting = False
        self.touch_pos = None
        self.last_shot_time = 0
        self.base_color = GREEN
        self.current_color = GREEN

    def update(self):
        if self.touch_pos:
            target_x, target_y = self.touch_pos
        else:
            target_x, target_y = pygame.mouse.get_pos()
            
        self.angle = math.atan2(target_y - self.rect.centery, target_x - self.rect.centerx)
        
        current_time = pygame.time.get_ticks()
        time_since_shot = current_time - self.last_shot_time
        cooldown_progress = min(1.0, time_since_shot / FIRE_RATE)
        
        if cooldown_progress < 1.0:
            self.current_color = (
                int(GREEN[0] * cooldown_progress + YELLOW[0] * (1 - cooldown_progress)),
                int(GREEN[1] * cooldown_progress + YELLOW[1] * (1 - cooldown_progress)),
                int(GREEN[2] * cooldown_progress + YELLOW[2] * (1 - cooldown_progress))
            )
        else:
            self.current_color = GREEN
        
        self.base_image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
        pygame.draw.polygon(self.base_image, self.current_color, [
            (0, PLAYER_SIZE),
            (0, 0),
            (PLAYER_SIZE, PLAYER_SIZE/2)
        ])
        
        self.image = pygame.transform.rotate(self.base_image, -math.degrees(self.angle))
        self.rect = self.image.get_rect(center=self.rect.center)

    def handle_touch(self, event):
        if event.type == pygame.FINGERDOWN:
            touch_x = event.x * SCREEN_WIDTH
            touch_y = event.y * SCREEN_HEIGHT
            self.touch_pos = (touch_x, touch_y)
            self.is_shooting = True
        elif event.type == pygame.FINGERUP:
            self.touch_pos = None
            self.is_shooting = False
        elif event.type == pygame.FINGERMOTION:
            self.touch_pos = (event.x * SCREEN_WIDTH, event.y * SCREEN_HEIGHT)
            self.is_shooting = True

    def draw_debug(self, surface, debug_active):
        if not debug_active:
            return
            
        if self.touch_pos:
            target_x, target_y = self.touch_pos
        else:
            target_x, target_y = pygame.mouse.get_pos()
            
        pygame.draw.line(surface, RED, self.rect.center, (target_x, target_y), 2)
        tip_pos = self.get_tip_position()
        pygame.draw.circle(surface, BLUE, (int(tip_pos[0]), int(tip_pos[1])), 5)

    def get_tip_position(self):
        angle_rad = self.angle
        tip_x = self.rect.centerx + math.cos(angle_rad) * PLAYER_SIZE/2
        tip_y = self.rect.centery + math.sin(angle_rad) * PLAYER_SIZE/2
        return (tip_x, tip_y)

    def can_shoot(self):
        current_time = pygame.time.get_ticks()
        return current_time - self.last_shot_time >= FIRE_RATE

    def shoot(self):
        if self.can_shoot():
            self.last_shot_time = pygame.time.get_ticks()
            self.current_color = YELLOW
            tip_x, tip_y = self.get_tip_position()
            return Bullet(tip_x, tip_y, self.angle)
        return None

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        self.image = pygame.Surface((BULLET_SIZE, BULLET_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(self.image, YELLOW, (0, 0, BULLET_SIZE, BULLET_SIZE))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = BULLET_SPEED
        self.angle = angle
        self.dx = math.cos(angle) * self.speed
        self.dy = math.sin(angle) * self.speed

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        if self.rect.left > SCREEN_WIDTH or self.rect.right < 0 or self.rect.top > SCREEN_HEIGHT or self.rect.bottom < 0:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((ENEMY_SIZE, ENEMY_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(self.image, RED, (ENEMY_SIZE / 2, ENEMY_SIZE / 2), ENEMY_SIZE / 2)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = ENEMY_SPEED
        self.target = player

    def update(self):
        dx = self.target.rect.centerx - self.rect.centerx
        dy = self.target.rect.centery - self.rect.centery
        angle = math.atan2(dy, dx)
        self.rect.x += math.cos(angle) * self.speed
        self.rect.y += math.sin(angle) * self.speed

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.images = [
            pygame.Surface((32, 32), pygame.SRCALPHA),
            pygame.Surface((32, 32), pygame.SRCALPHA),
            pygame.Surface((32, 32), pygame.SRCALPHA),
            pygame.Surface((32, 32), pygame.SRCALPHA),
            pygame.Surface((32, 32), pygame.SRCALPHA),
            pygame.Surface((32, 32), pygame.SRCALPHA),
        ]
        for i, img in enumerate(self.images):
            pygame.draw.circle(img, YELLOW, (16, 16), 16 - i * 2)

        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.frame_rate = 5
        self.timer = 0

    def update(self):
        self.timer += 1
        if self.timer % self.frame_rate == 0:
            self.frame_index += 1
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]

# --- Game Setup ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Endless Top-Down Shooter")
clock = pygame.time.Clock()

# Sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
explosions = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

# --- Event Timer ---
pygame.time.set_timer(pygame.USEREVENT, SPAWN_RATE)

# --- Game Loop ---
async def main():
    running = True
    score = 0
    game_over = False
    font = pygame.font.Font(None, 36)
    debug_button = DebugButton()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.USEREVENT:
                if not game_over:
                    for _ in range(MAX_SPAWN_ATTEMPTS):
                        x = random.randint(ENEMY_SIZE, SCREEN_WIDTH - ENEMY_SIZE)
                        y = random.randint(ENEMY_SIZE, SCREEN_HEIGHT - ENEMY_SIZE)
                        
                        if distance(x, y, player.rect.centerx, player.rect.centery) >= MIN_SPAWN_DISTANCE:
                            enemy = Enemy(x, y)
                            enemies.add(enemy)
                            all_sprites.add(enemy)
                            break
            
            if event.type in (pygame.FINGERDOWN, pygame.FINGERUP, pygame.FINGERMOTION):
                player.handle_touch(event)
                debug_button.handle_event(event)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not game_over:
                    if event.button == 1:
                        player.is_shooting = True
                        debug_button.handle_event(event)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    player.is_shooting = False

        if not game_over:
            all_sprites.update()

            enemy_hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
            for enemy in enemy_hits:
                score += 10
                explosion = Explosion(enemy.rect.centerx, enemy.rect.centery)
                all_sprites.add(explosion)
                explosions.add(explosion)

            player_hits = pygame.sprite.spritecollide(player, enemies, True)
            if player_hits:
                game_over = True
                for enemy in player_hits:
                    explosion = Explosion(enemy.rect.centerx, enemy.rect.centery)
                    all_sprites.add(explosion)
                    explosions.add(explosion)
                game_over_text = font.render("Game Over", True, RED)
                game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50))
                final_score_text = font.render(f"Final Score: {score}", True, WHITE)
                final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
                screen.blit(game_over_text, game_over_rect)
                screen.blit(final_score_text, final_score_rect)
                pygame.display.flip()
                await asyncio.sleep(3)
                running = False

        screen.fill(BLACK)
        all_sprites.draw(screen)

        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        player.draw_debug(screen, debug_button.active)
        debug_button.draw(screen)
        
        if player.is_shooting:
            bullet = player.shoot()
            if bullet:
                bullets.add(bullet)
                all_sprites.add(bullet)

        pygame.display.flip()
        await asyncio.sleep(0)
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
