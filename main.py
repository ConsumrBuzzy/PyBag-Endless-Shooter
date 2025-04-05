import pygame
import random
import math
import asyncio

# Initialize Pygame
pygame.init()
# pygame.mixer.init() # Removed mixer init

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
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
FPS = 60

# --- Helper Functions ---
# def load_sound(file_name): # Removed load_sound
#     """Load a sound file.  Handles errors."""
#     try:
#         sound = pygame.mixer.Sound(file_name)
#         return sound
#     except pygame.error:
#         print(f"Error loading sound: {file_name}")
#         # Return a dummy sound object.  This way, the game doesn't crash.
#         class DummySound:
#             def play(self): pass
#             def stop(self): pass
#         return DummySound()

def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# --- Game Object Classes ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Create a simple triangle pointing right (0 degrees)
        self.base_image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
        # Points: left-center, right-center, center-bottom
        pygame.draw.polygon(self.base_image, GREEN, [
            (0, PLAYER_SIZE/2),  # left-center
            (PLAYER_SIZE, PLAYER_SIZE/2),  # right-center (tip)
            (PLAYER_SIZE/2, PLAYER_SIZE)  # center-bottom
        ])
        self.image = self.base_image
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.speed = PLAYER_SPEED
        self.angle = 0
        self.touch_start_pos = None
        self.is_shooting = False

    def update(self):
        """Update player position and rotation."""
        # Movement
        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0

        if keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_s]:
            dy += 1
        if keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_d]:
            dx += 1

        # Touch movement
        if self.touch_start_pos:
            touch_x, touch_y = self.touch_start_pos
            current_touch_pos = pygame.mouse.get_pos()
            move_x = current_touch_pos[0] - touch_x
            move_y = current_touch_pos[1] - touch_y
            if abs(move_x) > 10 or abs(move_y) > 10:
                dx = move_x / 10
                dy = move_y / 10

        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707

        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed

        # Keep player on screen
        self.rect.clamp_ip(screen.get_rect())

        # Calculate angle to mouse
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.angle = math.atan2(mouse_y - self.rect.centery, mouse_x - self.rect.centerx)
        
        # Rotate the triangle to point at mouse
        self.image = pygame.transform.rotate(self.base_image, -math.degrees(self.angle))
        self.rect = self.image.get_rect(center=self.rect.center)

    def draw_debug(self, surface):
        """Draw debug line to mouse position"""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        pygame.draw.line(surface, RED, self.rect.center, (mouse_x, mouse_y), 2)
        
        # Draw the tip position
        tip_pos = self.get_tip_position()
        pygame.draw.circle(surface, BLUE, (int(tip_pos[0]), int(tip_pos[1])), 5)

    def get_tip_position(self):
        """Calculate the position of the triangle's tip"""
        # The tip is at (PLAYER_SIZE, PLAYER_SIZE/2) in the base image
        # Convert to world coordinates
        angle_rad = self.angle
        # Calculate the offset from center to tip
        tip_x = self.rect.centerx + math.cos(angle_rad) * PLAYER_SIZE/2
        tip_y = self.rect.centery + math.sin(angle_rad) * PLAYER_SIZE/2
        return (tip_x, tip_y)

    def shoot(self):
        """Create a bullet at the tip of the triangle"""
        tip_x, tip_y = self.get_tip_position()
        return Bullet(tip_x, tip_y, self.angle)

    def hit(self):
        # self.hit_sound.play() # Removed sound
        pass

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        # Use a simple rectangle for the bullet
        self.image = pygame.Surface((BULLET_SIZE, BULLET_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(self.image, YELLOW, (0, 0, BULLET_SIZE, BULLET_SIZE))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = BULLET_SPEED
        self.angle = angle
        self.dx = math.cos(angle) * self.speed
        self.dy = math.sin(angle) * self.speed

    def update(self):
        """Update bullet position."""
        self.rect.x += self.dx
        self.rect.y += self.dy
        if self.rect.left > SCREEN_WIDTH or self.rect.right < 0 or self.rect.top > SCREEN_HEIGHT or self.rect.bottom < 0:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Use a simple circle for the enemy
        self.image = pygame.Surface((ENEMY_SIZE, ENEMY_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(self.image, RED, (ENEMY_SIZE / 2, ENEMY_SIZE / 2), ENEMY_SIZE / 2)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = ENEMY_SPEED
        self.target = player
        # self.hit_sound = load_sound("enemy_hit.wav") # Removed sound

    def update(self):
        """Update enemy position."""
        dx = self.target.rect.centerx - self.rect.centerx
        dy = self.target.rect.centery - self.rect.centery
        angle = math.atan2(dy, dx)
        self.rect.x += math.cos(angle) * self.speed
        self.rect.y += math.sin(angle) * self.speed

    def hit(self):
        # self.hit_sound.play() # Removed sound
        pass

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
        pygame.draw.circle(self.images[0], YELLOW, (16, 16), 16)
        pygame.draw.circle(self.images[1], YELLOW, (16, 16), 14)
        pygame.draw.circle(self.images[2], YELLOW, (16, 16), 12)
        pygame.draw.circle(self.images[3], YELLOW, (16, 16), 10)
        pygame.draw.circle(self.images[4], YELLOW, (16, 16), 8)
        pygame.draw.circle(self.images[5], YELLOW, (16, 16), 6)

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

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.USEREVENT:
                if not game_over:
                    x = random.randint(0, SCREEN_WIDTH)
                    y = random.randint(0, SCREEN_HEIGHT)
                    enemy = Enemy(x, y)
                    enemies.add(enemy)
                    all_sprites.add(enemy)
            # Touch events
            if event.type == pygame.FINGERDOWN:
                player.touch_start_pos = event.pos
                player.is_shooting = True
            if event.type == pygame.FINGERUP:
                player.touch_start_pos = None
                player.is_shooting = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not game_over:
                    if event.button == 1:
                        bullet = player.shoot()
                        bullets.add(bullet)
                        all_sprites.add(bullet)

        if not game_over:
            all_sprites.update()

            # Check for collisions
            enemy_hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
            for enemy in enemy_hits:
                score += 10
                explosion = Explosion(enemy.rect.centerx, enemy.rect.centery)
                all_sprites.add(explosion)
                explosions.add(explosion)

            player_hits = pygame.sprite.spritecollide(player, enemies, True)
            if player_hits:
                game_over = True
                player.hit()
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

        # Display score
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        # Draw debug line
        player.draw_debug(screen)
        
        if player.is_shooting:
            bullet = player.shoot()
            bullets.add(bullet)
            all_sprites.add(bullet)

        pygame.display.flip()
        await asyncio.sleep(0)
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
