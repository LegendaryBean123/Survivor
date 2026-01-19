from data.code.settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites):
        super().__init__(groups)
        self.image = pygame.image.load(resource_path(join('data', 'sprites', 'player.png'))).convert_alpha()
        self.rect = self.image.get_frect(center=pos)
        self.hitbox = self.rect.inflate(0, -50)

        self.direction = pygame.Vector2(1,0)
        self.speed = 500
        self.collision_sprites = collision_sprites
        self.health = 3
        self.shield = SHEILD_DURATION # milliseconds

    def input(self):
        keys = pygame.key.get_pressed()

        self.direction.x = int((keys[pygame.K_RIGHT] or keys[pygame.K_d])) - int((keys[pygame.K_LEFT] or keys[pygame.K_a]))
        self.direction.y = int((keys[pygame.K_DOWN] or keys[pygame.K_s])) - int((keys[pygame.K_UP] or keys[pygame.K_w]))
        self.direction = self.direction.normalize() if self.direction else self.direction
        

    def move(self, dt):
        self.hitbox.x += self.direction.x * self.speed * dt
        self.collision('horizontal')
        self.hitbox.y += self.direction.y * self.speed * dt
        self.collision('vertical')
        self.rect.center = self.hitbox.center
        

    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox):
                if direction == 'horizontal':
                    if self.direction.x > 0:  # moving right
                        self.hitbox.right = sprite.rect.left
                    if self.direction.x < 0:  # moving left
                        self.hitbox.left = sprite.rect.right
                if direction == 'vertical':
                    if self.direction.y > 0:  # moving down
                        self.hitbox.bottom = sprite.rect.top
                    if self.direction.y < 0:  # moving up
                        self.hitbox.top = sprite.rect.bottom


    def update(self, dt):
        if self.shield > 0:
            self.shield -= dt * 1000  # convert to milliseconds
        self.input()
        self.move(dt) 