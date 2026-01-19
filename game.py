from random import randint
from secrets import choice
from data.code import settings
from data.code import player
from data.code import sprites
from pytmx.util_pygame import load_pygame
from data.code import groups

class Game:
    def __init__(self):
        # general setup
        settings.pygame.init()
        self.screen = settings.pygame.display.set_mode((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
        settings.pygame.display.set_caption('BBB')
        self.clock = settings.pygame.time.Clock()
        self.running = True
        self.death_timer = 2000  # milliseconds

        self.all_sprites = groups.AllSprites()
        self.collision_sprites = settings.pygame.sprite.Group()
        self.bullet_sprites = settings.pygame.sprite.Group()
        self.enemy_sprites = settings.pygame.sprite.Group()

        self.can_shoot = True
        self.shoot_time = 0
        self.gun_cooldown = 100  # milliseconds

        self.score = 0
        self.font = settings.pygame.font.Font(None, 36)

        self.enemy_event = settings.pygame.event.custom_type()
        settings.pygame.time.set_timer(self.enemy_event, 300)
        self.spawn_positions = []

        self.load_imges()
        self.setup()

    def load_imges(self):
        self.bullet_surf = settings.pygame.image.load(settings.resource_path(settings.join('data', 'sprites', 'gun', 'bullet.png'))).convert_alpha()

        folders = list(settings.walk(settings.resource_path(settings.join('data', 'sprites', 'enemies'))))[0][1]
        self.enemy_frames = {}
        for folder in folders:
            for folder_path, _, file_names in settings.walk(settings.resource_path(settings.join('data', 'sprites', 'enemies', folder))):
                self.enemy_frames[folder] = []
                for file_name in sorted(file_names, key = lambda name: int(name.split('.')[0])):
                    full_path = settings.join(folder_path, file_name)
                    surf = settings.pygame.image.load(full_path).convert_alpha()
                    self.enemy_frames[folder].append(surf)
        print(self.enemy_frames)

    def input(self):
        if settings.pygame.mouse.get_pressed()[0] and self.can_shoot and self.player.alive():
            pos = self.gun.rect.center + self.gun.player_direction * 50
            sprites.Bullet(self.bullet_surf, pos, self.gun.player_direction, (self.all_sprites, self.bullet_sprites))
            self.can_shoot = False
            self.shoot_time = settings.pygame.time.get_ticks()

    def gun_timer(self):
        if not self.can_shoot:
            current_time = settings.pygame.time.get_ticks()
            if current_time - self.shoot_time >= self.gun_cooldown:
                self.can_shoot = True

    def setup(self):
        map = load_pygame(settings.resource_path(settings.join('data', 'maps', 'world.tmx')))
        
        for x,y,image in map.get_layer_by_name('Ground').tiles():
            sprites.Sprite((x * settings.TILE_SIZE, y * settings.TILE_SIZE), image, self.all_sprites)

        for obj in map.get_layer_by_name('Objects'):
            sprites.CollisionSprite((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites])

        for col in map.get_layer_by_name('Collisions'):
            sprites.CollisionSprite((col.x, col.y), settings.pygame.Surface((col.width, col.height)), [self.collision_sprites])

        for obj in map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = player.Player((obj.x, obj.y), self.all_sprites, self.collision_sprites)
                self.gun = sprites.Gun(self.player, self.all_sprites)
            else:
                self.spawn_positions.append((obj.x, obj.y))

    def reset(self):
        self.all_sprites.empty()
        self.collision_sprites.empty()
        self.bullet_sprites.empty()
        self.enemy_sprites.empty()
        self.can_shoot = True
        self.shoot_time = 0
        self.score = 0
        self.setup()

    def death_screen(self):
        death_screen_surf = settings.pygame.Surface((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT), settings.pygame.SRCALPHA)
        death_screen_surf.fill((0, 0, 0, 200))
        
        button_image = settings.pygame.image.load(settings.resource_path(settings.join('data', 'sprites', 'restart_button.png'))).convert_alpha()
        button_rect = button_image.get_frect(center=(settings.WINDOW_WIDTH // 2, settings.WINDOW_HEIGHT // 2 + 100))
        if button_rect.collidepoint(settings.pygame.mouse.get_pos()):
            button_image = settings.pygame.transform.rotozoom(button_image, 0, 1.1)
            button_rect = button_image.get_frect(center=button_rect.center)
            if settings.pygame.mouse.get_pressed()[0] and self.death_timer <= 0:
                self.reset()

        self.screen.blit(death_screen_surf, (0, 0))
        self.screen.blit(button_image, button_rect)

    def bullet_collision(self):
        if self.bullet_sprites:
            for bullet in self.bullet_sprites:
                collision_sprites = settings.pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, settings.pygame.sprite.collide_mask)
                if collision_sprites:
                    for sprite in collision_sprites:
                        self.score += 10
                        sprite.destroy()
                        bullet.kill()

    def player_collision(self):
        if settings.pygame.sprite.spritecollide(self.player, self.enemy_sprites, False, settings.pygame.sprite.collide_mask) and self.player.shield <= 0:
            self.player.health -= 1
            if self.player.health == 0:
                self.player.kill()
                self.gun.kill()
            else:
                self.player.shield = settings.SHEILD_DURATION
                print(self.player.health)

    def draw_hearts(self, surface):
            for i in range(self.player.health):
                heart_surf = settings.pygame.image.load(settings.resource_path(settings.join('data', 'sprites', 'heart.png'))).convert_alpha()
                heart_rect = heart_surf.get_frect(topleft=(10 + i * (heart_surf.get_width() + 10), 10))
                surface.blit(heart_surf, heart_rect)

    def show_score(self):
        if self.player.health == 0 or not self.player.alive():
            self.text = self.font.render(f'Final Score: {self.score}', True, 'white')
            self.screen.blit(self.text, (settings.WINDOW_WIDTH // 2 - self.text.get_width() // 2, settings.WINDOW_HEIGHT // 2 - 50))
        else:
            self.text = self.font.render(f'Score: {self.score}', True, 'white')
            self.screen.blit(self.text, (settings.WINDOW_WIDTH - 200, 10))
            
    def run(self):

        while self.running:
            # dt
            dt = self.clock.tick() / 1000

            # event loop
            for event in settings.pygame.event.get():
                if event.type == settings.pygame.QUIT:
                    self.running = False
                if event.type == self.enemy_event:
                    sprites.Enemy(choice(self.spawn_positions), choice(list(self.enemy_frames.values())), (self.all_sprites, self.enemy_sprites), self.player, self.collision_sprites)
                    

            # update
            self.gun_timer()
            self.input()
            self.all_sprites.update(dt)
            self.bullet_collision()
            self.player_collision()

            # draw
            self.screen.fill('black')
            self.all_sprites.draw(self.player.rect.center)
            if self.player.shield > 0:
                shield_surf = settings.pygame.Surface((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT), settings.pygame.SRCALPHA)
                settings.pygame.draw.circle(shield_surf, (255, 0, 0, 100), (settings.WINDOW_WIDTH // 2, settings.WINDOW_HEIGHT // 2), 70)
                self.screen.blit(shield_surf, (0, 0))
            self.draw_hearts(self.screen)
            if self.player.health <= 0:
                self.death_timer -= dt * 1000  # convert to milliseconds
                self.death_screen()
            self.show_score()

            settings.pygame.display.flip()
        settings.pygame.quit()

game = Game()
game.run()
                