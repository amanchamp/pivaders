"""pivaders is a space invaders clone written in Python and Py game for the Raspberry Pi.
This project was by Russell Barnes for Linux User $ Developer magazine issue (v.01)."""

#!/usr/bin/env python2

import pygame, random
# variables are being set with color or resolution/pixel size
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
ALIEN_SIZE = (30, 40)
ALIEN_SPACER = 20
BARRIER_ROW = 10
BARRIER_COLUMN = 4
BULLET_SIZE = (5, 10)
MISSILE_SIZE = (5, 5)
BLOCK_SIZE = (10, 10)
RES = (800, 600)


class Player(pygame.sprite.Sprite):
    # class designed to separate code from the board and player 
    # aids in modularization of the program 
    # takes pygame.sprite.Sprite which is a graphic that can be moved (ie picture of spaceship) 
    def __init__(self):
        # initializing the game and adding various attributes to the visual board 
        # self is a class instance and refers to the object using this function
        pygame.sprite.Sprite.__init__(self)
        self.size = (64, 61)
        self.rect = self.image.get_rect()
        self.rect.x = (RES[0] / 2) - (self.size[0] / 2) # allows size to be dynamic and not hard coded 
        self.rect.y = 520
        self.travel = 7
        self.speed = 350
        self.time = pygame.time.get_ticks() # more efficent then using epoch time

    def update(self):
        # this function updates the position of the player sprite 
        # only allows the player to move in the horizontal axis 
        # uses self as parameter for player object 
        self.rect.x += GameState.vector * self.travel
        if self.rect.x < 0: # forces boundary on player sprite 
            self.rect.x = 0
        elif self.rect.x > RES[0] - self.size[0]:   # moves player to desired place
            self.rect.x = RES[0] - self.size[0]


class Alien(pygame.sprite.Sprite):
    # class designed to seprate code between player and alien 
    # used to modularize code 
    # takes pygame.sprite.Sprite which allows a graphic item to move on screen
    def __init__(self):
        # create assoicated variables to the Alien Sprite
        # takes self as parameter for alien objects
        pygame.sprite.Sprite.__init__(self)
        self.size = (ALIEN_SIZE)
        self.rect = self.image.get_rect()
        self.has_moved = [0, 0]
        self.vector = [1, 1]  # uses array for position 
        self.travel = [(ALIEN_SIZE[0] - 7), ALIEN_SPACER] #find amount traveled on screen
        self.speed = 700
        self.time = pygame.time.get_ticks()

    def update(self):
        # updates alien sprite position based upon alien object speed 
        # self parameter for alien object 
        if GameState.alien_time - self.time > self.speed:
            if self.has_moved[0] < 12:
                self.rect.x += self.vector[0] * self.travel[0]
                self.has_moved[0] += 1
            else:                               # moves alien object at a certain speed
                if not self.has_moved[1]:
                    self.rect.y += self.vector[1] * self.travel[1]
                self.vector[0] *= -1
                self.has_moved = [0, 0]
                self.speed -= 20
                if self.speed <= 100:
                    self.speed = 100
            self.time = GameState.alien_time


class Ammo(pygame.sprite.Sprite):
    # class for ammo which can be used by both alien or player object 
    # this is because the parameter taken by the class is any graphic of pygame.sprite.Sprite object 
    def __init__(self, color, (width, height)):
        # set ammo object bullet properties 
        # the properties are the parameters allowed (ie color,width, height)
        pygame.sprite.Sprite.__init__(self)   # create graphic
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.speed = 0          
        self.vector = 0

    def update(self):
        # update position of ammo object interms of y position 
        self.rect.y += self.vector * self.speed
        if self.rect.y < 0 or self.rect.y > RES[1]: # if an object is hit then count as a hit 
            self.kill()


class Block(pygame.sprite.Sprite):
    # class for blocks that spawn over player 
    def __init__(self, color, (width, height)):
        # when creating a box the color, width, and height can be choosen
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()


class GameState:
    # class created but no methods to implement  
    pass # acts as placeholder


class Game(object):
    # The Game class sets the board and controls animations, score, and collision calculations 
    def __init__(self):
        # initial variables being set 
        # sets the level, amount of lives, and other various variables concerning gameplay 
        pygame.init()
        pygame.font.init()
        self.clock = pygame.time.Clock()
        self.game_font = pygame.font.Font(
            'data/Orbitracer.ttf', 28)
        self.intro_font = pygame.font.Font(
            'data/Orbitracer.ttf', 72)
        self.screen = pygame.display.set_mode([RES[0], RES[1]])
        self.time = pygame.time.get_ticks()
        self.refresh_rate = 20
        self.rounds_won = 0
        self.level_up = 50
        self.score = 0
        self.lives = 2
        self.player_group = pygame.sprite.Group()
        self.alien_group = pygame.sprite.Group()
        self.bullet_group = pygame.sprite.Group()
        self.missile_group = pygame.sprite.Group()
        self.barrier_group = pygame.sprite.Group()
        self.all_sprite_list = pygame.sprite.Group()
        self.intro_screen = pygame.image.load(
            'data/graphics/start_screen.jpg').convert()
        self.background = pygame.image.load(
            'data/graphics/Space-Background.jpg').convert()
        pygame.display.set_caption('Pivaders - ESC to exit')
        pygame.mouse.set_visible(False)
        Alien.image = pygame.image.load(
            'data/graphics/Spaceship16.png').convert()
        Alien.image.set_colorkey(WHITE)
        self.ani_pos = 5  # 11 images of ship leaning from left to right. 5th image is 'central'
        self.ship_sheet = pygame.image.load(
            'data/graphics/ship_sheet_final.png').convert_alpha()
        Player.image = self.ship_sheet.subsurface(self.ani_pos * 64, 0, 64, 61)
        self.animate_right = False
        self.animate_left = False
        self.explosion_sheet = pygame.image.load(
            'data/graphics/explosion_new1.png').convert_alpha()
        self.explosion_image = self.explosion_sheet.subsurface(0, 0, 79, 96)
        self.alien_explosion_sheet = pygame.image.load(
            'data/graphics/alien_explosion.png')
        self.alien_explode_graphics = self.alien_explosion_sheet.subsurface(0, 0, 94, 96)
        self.explode = False
        self.explode_pos = 0
        self.alien_explode = False
        self.alien_explode_pos = 0
        pygame.mixer.music.load('data/sound/10_Arpanauts.ogg')
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.7)
        self.bullet_fx = pygame.mixer.Sound(
            'data/sound/medetix__pc-bitcrushed-lazer-beam.ogg')
        self.explosion_fx = pygame.mixer.Sound(
            'data/sound/timgormly__8-bit-explosion.ogg')
        self.explosion_fx.set_volume(0.5)
        self.explodey_alien = []
        GameState.end_game = False
        GameState.start_screen = True
        GameState.vector = 0
        GameState.shoot_bullet = False

    def control(self):
        # keyboard listner for detecting user input 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                GameState.start_screen = False
                GameState.end_game = True
            if event.type == pygame.KEYDOWN \
                    and event.key == pygame.K_ESCAPE:
                if GameState.start_screen:
                    GameState.start_screen = False
                    GameState.end_game = True
                    self.kill_all()
                else:
                    GameState.start_screen = True
        self.keys = pygame.key.get_pressed()
        if self.keys[pygame.K_LEFT]:
            GameState.vector = -1
            self.animate_left = True
            self.animate_right = False
        elif self.keys[pygame.K_RIGHT]:
            GameState.vector = 1
            self.animate_right = True
            self.animate_left = False

        else:
            GameState.vector = 0
            self.animate_right = False
            self.animate_left = False

        if self.keys[pygame.K_SPACE]:
            if GameState.start_screen:
                GameState.start_screen = False
                self.lives = 2
                self.score = 0
                self.make_player()
                self.make_defenses()
                self.alien_wave(0)
            else:
                GameState.shoot_bullet = True
                self.bullet_fx.play()

    def animate_player(self):
        # animate player object ( spaceship banks left or right depending on input)
        if self.animate_right:
            if self.ani_pos < 10:
                Player.image = self.ship_sheet.subsurface(self.ani_pos * 64, 0, 64, 61)
                self.ani_pos += 1
        else:
            if self.ani_pos > 5:
                self.ani_pos -= 1
                Player.image = self.ship_sheet.subsurface(self.ani_pos * 64, 0, 64, 61)

        if self.animate_left:
            if self.ani_pos > 0:
                self.ani_pos -= 1
                Player.image = self.ship_sheet.subsurface(self.ani_pos * 64, 0, 64, 61)
        else:
            if self.ani_pos < 5:
                Player.image = self.ship_sheet.subsurface(self.ani_pos * 64, 0, 64, 61)
                self.ani_pos += 1

    def player_explosion(self):
        # animate an explosion if the player object was hit with a missle from an alien object 
        if self.explode:
            if self.explode_pos < 8:
                self.explosion_image = self.explosion_sheet.subsurface(0, self.explode_pos * 96, 79, 96)
                self.explode_pos += 1
                self.screen.blit(self.explosion_image, [self.player.rect.x - 10, self.player.rect.y - 30])
            else:
                self.explode = False
                self.explode_pos = 0

    def alien_explosion(self):
        # animate alien explosion if the object has detected a collision
        if self.alien_explode:
            if self.alien_explode_pos < 9:
                self.alien_explode_graphics = self.alien_explosion_sheet.subsurface(
                    0, self.alien_explode_pos * 96, 94, 96)
                self.alien_explode_pos += 1
                self.screen.blit(self.alien_explode_graphics, [
                    int(self.explodey_alien[0]) - 50, int(self.explodey_alien[1]) - 60])
            else:
                self.alien_explode = False
                self.alien_explode_pos = 0
                self.explodey_alien = []

    def splash_screen(self):
        # create splashscreen with option to play game 
        while GameState.start_screen:
            self.kill_all()
            self.screen.blit(self.intro_screen, [0, 0])
            self.screen.blit(self.intro_font.render(
                "PIVADERS", 1, WHITE), (265, 120))
            self.screen.blit(self.game_font.render(
                "PRESS SPACE TO PLAY", 1, WHITE), (274, 191))
            pygame.display.flip()
            self.control()
            self.clock.tick(self.refresh_rate / 2)

    def make_player(self):
        # make the player ship on the game screen 
        self.player = Player()
        self.player_group.add(self.player)
        self.all_sprite_list.add(self.player)

    def refresh_screen(self):
        # place all objects needed for the game on the screen 
        self.all_sprite_list.draw(self.screen)
        self.animate_player()
        self.player_explosion()
        self.alien_explosion()
        self.refresh_scores()
        pygame.display.flip()
        self.screen.blit(self.background, [0, 0])
        self.clock.tick(self.refresh_rate)

    def refresh_scores(self):
        # update score 
        self.screen.blit(self.game_font.render(
            "SCORE " + str(self.score), 1, WHITE), (10, 8))
        self.screen.blit(self.game_font.render(
            "LIVES " + str(self.lives + 1), 1, RED), (355, 575))

    def alien_wave(self, speed):
        # produce alien objects and adjust speed of travel 
        for column in range(BARRIER_COLUMN):
            for row in range(BARRIER_ROW):
                alien = Alien()
                alien.rect.y = 65 + (column * (
                    ALIEN_SIZE[1] + ALIEN_SPACER))
                alien.rect.x = ALIEN_SPACER + (
                    row * (ALIEN_SIZE[0] + ALIEN_SPACER))
                self.alien_group.add(alien)
                self.all_sprite_list.add(alien)
                alien.speed -= speed

    def make_bullet(self):
        # user initiated bullet triggered 
        if GameState.game_time - self.player.time > self.player.speed:
            bullet = Ammo(BLUE, BULLET_SIZE)
            bullet.vector = -1
            bullet.speed = 26
            bullet.rect.x = self.player.rect.x + 28
            bullet.rect.y = self.player.rect.y
            self.bullet_group.add(bullet)
            self.all_sprite_list.add(bullet)
            self.player.time = GameState.game_time
        GameState.shoot_bullet = False

    def make_missile(self):
        # shoots a missle randomly from alien object 
        if len(self.alien_group):
            shoot = random.random()
            if shoot <= 0.05:
                shooter = random.choice([
                    alien for alien in self.alien_group])
                missile = Ammo(RED, MISSILE_SIZE)
                missile.vector = 1
                missile.rect.x = shooter.rect.x + 15
                missile.rect.y = shooter.rect.y + 40
                missile.speed = 10
                self.missile_group.add(missile)
                self.all_sprite_list.add(missile)

    def make_barrier(self, columns, rows, spacer):
        # make barrier depending on the number of columns and rows along with spacing 
        for column in range(columns):
            for row in range(rows):
                barrier = Block(WHITE, (BLOCK_SIZE))
                barrier.rect.x = 55 + (200 * spacer) + (row * 10)
                barrier.rect.y = 450 + (column * 10)
                self.barrier_group.add(barrier)
                self.all_sprite_list.add(barrier)

    def make_defenses(self):
        # creates 3 barriers 
        for spacing, spacing in enumerate(xrange(4)):
            self.make_barrier(3, 9, spacing)

    def kill_all(self):
        # kill allows board to reset / clear board of aliens or other objects 
        for items in [self.bullet_group, self.player_group,
                      self.alien_group, self.missile_group, self.barrier_group]:
            for i in items:
                i.kill()

    def is_dead(self):
        # player has been killed from too many hits and game restarts 
        if self.lives < 0:
            self.screen.blit(self.game_font.render(
                "The war is lost! You scored: " + str(
                    self.score), 1, RED), (250, 15))
            self.rounds_won = 0
            self.refresh_screen()
            self.level_up = 50
            self.explode = False
            self.alien_explode = False
            pygame.time.delay(3000)
            return True

    def defenses_breached(self):
        # aliens have reached the barriers and game reloads/restarts
        for alien in self.alien_group:
            if alien.rect.y > 410:      # 410 is the y location of barriers 
                self.screen.blit(self.game_font.render(
                    "The aliens have breached Earth defenses!",
                    1, RED), (180, 15))
                self.refresh_screen()
                self.level_up = 50
                self.explode = False
                self.alien_explode = False
                pygame.time.delay(3000)
                return True

    def win_round(self):
        # player has won the round 
        # no aliens exist so the next round is loaded in
        if len(self.alien_group) < 1:
            self.rounds_won += 1
            self.screen.blit(self.game_font.render(
                "You won round " + str(self.rounds_won) +
                "  but the battle rages on", 1, RED), (200, 15))
            self.refresh_screen()
            pygame.time.delay(3000)
            return True

    def next_round(self):
        # move the game logic to next round using self (game) object 
        # resets board by killing aliens and adding 50 points to score board 
        # also restores aliens exploded ships and any other variables 
        self.explode = False
        self.alien_explode = False
        for actor in [self.missile_group,
                      self.barrier_group, self.bullet_group]:
            for i in actor:
                i.kill()
        self.alien_wave(self.level_up)
        self.make_defenses()
        self.level_up += 50

    def calc_collisions(self):
        # calculate if a collision has occured between ammo and player/alien 
        pygame.sprite.groupcollide(
            self.missile_group, self.barrier_group, True, True)
        pygame.sprite.groupcollide(
            self.bullet_group, self.barrier_group, True, True)

        for z in pygame.sprite.groupcollide(
                self.bullet_group, self.alien_group, True, True):
            self.alien_explode = True
            self.explodey_alien.append(z.rect.x)
            self.explodey_alien.append(z.rect.y)
            self.score += 10
            self.explosion_fx.play()
            
        if pygame.sprite.groupcollide(     # if an alien object hits the player object lives must be subtracted by one and explosion animation triggered
                self.player_group, self.missile_group, False, True):
            self.lives -= 1
            self.explode = True
            self.explosion_fx.play()

    def main_loop(self):
        # Starts the game and runs until the game ends using while loop and creates objects
        while not GameState.end_game:
            while not GameState.start_screen:
                GameState.game_time = pygame.time.get_ticks()
                GameState.alien_time = pygame.time.get_ticks()
                self.control()
                self.make_missile()
                self.calc_collisions()
                self.refresh_screen()
                if self.is_dead() or self.defenses_breached():
                    GameState.start_screen = True
                for actor in [self.player_group, self.bullet_group,
                              self.alien_group, self.missile_group]:
                    for i in actor:
                        i.update()
                if GameState.shoot_bullet:
                    self.make_bullet()
                if self.win_round():
                    self.next_round()
            self.splash_screen()
        pygame.quit()


if __name__ == '__main__':
    pv = Game()
    pv.main_loop()