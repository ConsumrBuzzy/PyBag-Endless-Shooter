import pybag
import random
import math

# Initialize PyBag
pybag.init()

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SIZE = 32
ENEMY_SIZE = 32
BULLET_SIZE = 8
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

class Game:
    def __init__(self):
        self.screen = pybag.Screen(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.clock = pybag.Clock()
        self.running = True
        self.score = 0
        self.game_over = False
        
        # Sprite groups
        self.all_sprites = pybag.Group()
        self.enemies = pybag.Group()
        self.bullets = pybag.Group()
        self.explosions = pybag.Group()
        
        # Create player
        self.player = Player(self)
        self.all_sprites.add(self.player)
        
        # Debug button
        self.debug_button = DebugButton()
        
        # Set up spawn timer
        self.spawn_timer = 0
        
        # Load font
        self.font = pybag.Font(None, 36)

    def handle_events(self):
        for event in pybag.get_events():
            if event.type == pybag.QUIT:
                self.running = False
            elif event.type == pybag.TOUCH_DOWN:
                # Check if touch is on debug button
                if self.debug_button.rect.collidepoint(event.pos):
                    self.debug_button.toggle()
                else:
                    self.player.handle_touch(event, True)
            elif event.type == pybag.TOUCH_UP:
                self.player.handle_touch(event, False)
            elif event.type == pybag.TOUCH_MOTION:
                self.player.handle_touch(event, True)
            elif event.type == pybag.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if self.debug_button.rect.collidepoint(event.pos):
                        self.debug_button.toggle()
                    else:
                        self.player.is_shooting = True
            elif event.type == pybag.MOUSEBUTTONUP:
                if event.button == 1:  # Left click
                    self.player.is_shooting = False

    def update(self):
        if not self.game_over:
            # Update spawn timer
            self.spawn_timer += self.clock.get_time()
            if self.spawn_timer >= SPAWN_RATE:
                self.spawn_timer = 0
                self.spawn_enemy()
            
            # Update all sprites
            self.all_sprites.update()
            
            # Check collisions
            self.check_collisions()

    def spawn_enemy(self):
        for _ in range(MAX_SPAWN_ATTEMPTS):
            x = random.randint(ENEMY_SIZE, SCREEN_WIDTH - ENEMY_SIZE)
            y = random.randint(ENEMY_SIZE, SCREEN_HEIGHT - ENEMY_SIZE)
            
            if self.distance(x, y, self.player.rect.centerx, self.player.rect.centery) >= MIN_SPAWN_DISTANCE:
                enemy = Enemy(self, x, y)
                self.enemies.add(enemy)
                self.all_sprites.add(enemy)
                break

    def check_collisions(self):
        # Check bullet-enemy collisions
        for enemy in self.enemies:
            for bullet in self.bullets:
                if self.distance(enemy.rect.centerx, enemy.rect.centery, 
                               bullet.rect.centerx, bullet.rect.centery) < (ENEMY_SIZE + BULLET_SIZE) / 2:
                    self.score += 10
                    explosion = Explosion(enemy.rect.centerx, enemy.rect.centery)
                    self.all_sprites.add(explosion)
                    self.explosions.add(explosion)
                    enemy.kill()
                    bullet.kill()
        
        # Check player-enemy collisions
        for enemy in self.enemies:
            if self.distance(enemy.rect.centerx, enemy.rect.centery,
                           self.player.rect.centerx, self.player.rect.centery) < (ENEMY_SIZE + PLAYER_SIZE) / 2:
                self.game_over = True
                explosion = Explosion(enemy.rect.centerx, enemy.rect.centery)
                self.all_sprites.add(explosion)
                self.explosions.add(explosion)
                enemy.kill()

    def draw(self):
        self.screen.fill(BLACK)
        self.all_sprites.draw(self.screen)
        
        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Draw debug visuals if active
        if self.debug_button.active:
            self.player.draw_debug(self.screen)
        
        # Draw debug button
        self.debug_button.draw(self.screen)
        
        pybag.display.flip()

    def distance(self, x1, y1, x2, y2):
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

class Player(pybag.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.image = pybag.Surface((PLAYER_SIZE, PLAYER_SIZE), pybag.SRCALPHA)
        pygame.draw.polygon(self.image, GREEN, [
            (0, PLAYER_SIZE),
            (0, 0),
            (PLAYER_SIZE, PLAYER_SIZE/2)
        ])
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.angle = 0
        self.is_shooting = False
        self.touch_pos = None
        self.last_shot_time = 0
        self.current_color = GREEN

    def update(self):
        # Update color based on cooldown
        current_time = pybag.time.get_ticks()
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
        
        # Redraw triangle with current color
        self.image = pybag.Surface((PLAYER_SIZE, PLAYER_SIZE), pybag.SRCALPHA)
        pygame.draw.polygon(self.image, self.current_color, [
            (0, PLAYER_SIZE),
            (0, 0),
            (PLAYER_SIZE, PLAYER_SIZE/2)
        ])
        
        # Rotate to face touch/mouse
        if self.touch_pos:
            target_x, target_y = self.touch_pos
        else:
            target_x, target_y = pybag.mouse.get_pos()
            
        self.angle = math.atan2(target_y - self.rect.centery, target_x - self.rect.centerx)
        self.image = pybag.transform.rotate(self.image, -math.degrees(self.angle))
        self.rect = self.image.get_rect(center=self.rect.center)
        
        # Handle shooting
        if self.is_shooting and self.can_shoot():
            self.shoot()

    def handle_touch(self, event, is_down):
        if is_down:
            self.touch_pos = event.pos
            self.is_shooting = True
        else:
            self.touch_pos = None
            self.is_shooting = False

    def can_shoot(self):
        current_time = pybag.time.get_ticks()
        return current_time - self.last_shot_time >= FIRE_RATE

    def shoot(self):
        self.last_shot_time = pybag.time.get_ticks()
        tip_x = self.rect.centerx + math.cos(self.angle) * PLAYER_SIZE/2
        tip_y = self.rect.centery + math.sin(self.angle) * PLAYER_SIZE/2
        bullet = Bullet(self.game, tip_x, tip_y, self.angle)
        self.game.bullets.add(bullet)
        self.game.all_sprites.add(bullet)

    def draw_debug(self, surface):
        if self.touch_pos:
            target_x, target_y = self.touch_pos
        else:
            target_x, target_y = pybag.mouse.get_pos()
            
        pygame.draw.line(surface, RED, self.rect.center, (target_x, target_y), 2)
        
        tip_x = self.rect.centerx + math.cos(self.angle) * PLAYER_SIZE/2
        tip_y = self.rect.centery + math.sin(self.angle) * PLAYER_SIZE/2
        pygame.draw.circle(surface, BLUE, (int(tip_x), int(tip_y)), 5)

class Bullet(pybag.Sprite):
    def __init__(self, game, x, y, angle):
        super().__init__()
        self.game = game
        self.image = pybag.Surface((BULLET_SIZE, BULLET_SIZE), pybag.SRCALPHA)
        pygame.draw.rect(self.image, YELLOW, (0, 0, BULLET_SIZE, BULLET_SIZE))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.angle = angle
        self.speed = BULLET_SPEED

    def update(self):
        self.rect.x += math.cos(self.angle) * self.speed
        self.rect.y += math.sin(self.angle) * self.speed
        
        # Remove if off screen
        if (self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or
            self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT):
            self.kill()

class Enemy(pybag.Sprite):
    def __init__(self, game, x, y):
        super().__init__()
        self.game = game
        self.image = pybag.Surface((ENEMY_SIZE, ENEMY_SIZE), pybag.SRCALPHA)
        pygame.draw.circle(self.image, RED, (ENEMY_SIZE/2, ENEMY_SIZE/2), ENEMY_SIZE/2)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = ENEMY_SPEED

    def update(self):
        # Move toward player
        dx = self.game.player.rect.centerx - self.rect.centerx
        dy = self.game.player.rect.centery - self.rect.centery
        angle = math.atan2(dy, dx)
        
        self.rect.x += math.cos(angle) * self.speed
        self.rect.y += math.sin(angle) * self.speed

class Explosion(pybag.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pybag.Surface((32, 32), pybag.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (16, 16), 16)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.lifetime = 10  # Frames to live

    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()

class DebugButton:
    def __init__(self):
        self.rect = pygame.Rect(SCREEN_WIDTH - 100, 10, 80, 30)
        self.text = "Debug: ON"
        self.active = True
        self.font = pybag.Font(None, 24)

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect, 2)
        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def toggle(self):
        self.active = not self.active
        self.text = "Debug: ON" if self.active else "Debug: OFF"

if __name__ == "__main__":
    game = Game()
    game.run() 