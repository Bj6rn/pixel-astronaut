#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import pygame
from pygame.locals import *
import sys
import os
import random

pygame.init()

window = pygame.display.set_mode((1280, 800))
pygame.display.set_caption("Pixel Astronaut")
clock = pygame.time.Clock()
FPS = 60

class background:
    def __init__(self,breite,hoehe,start_x):
        self.breite = breite
        self.hoehe = hoehe
        self.x = start_x
        self.image = [pygame.image.load(os.path.join("assets","moon_background_frame1.png")), pygame.image.load(os.path.join("assets","moon_background_frame2.png"))]
        self.scaled_image = [pygame.transform.scale(self.image[0], (self.breite, self.hoehe)), pygame.transform.scale(self.image[1], (self.breite, self.hoehe))]
        self.frame = 0

    def scroll(self,game_speed):
        #scrolls the background to the left
        self.x -= game_speed
        #if the background is completly gone to the left, it resets itself to the end of the screen
        if self.x < self.breite * -1:
            self.x = self.breite   

    def draw(self,window):
        self.frame += 1
        #changing between two background images, to simulate an animation of the stars
        if self.frame <= 30:
            window.blit(self.scaled_image[0], (self.x, 0))
        else:
            window.blit(self.scaled_image[1], (self.x, 0))

        if self.frame == 60:
            self.frame = 0

class player:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.breite = 60
        self.hoehe = 90
        self.hitbox = pygame.Rect(self.x+6,self.y,self.breite-12,self.hoehe)
        self.jumping = False
        self.jump_count = 0
        self.jump_speed = 1
        self.max_jump_height = 60
        self.walk = False
        self.walkcount = 0
        self.shooting = False
        self.shoot_count = 0
        self.image = pygame.image.load(os.path.join("assets","astronaut_still.png"))
        self.walk_image = [pygame.image.load(os.path.join("assets","astronaut_step1_right.png")),pygame.image.load(os.path.join("assets","astronaut_step2_right.png"))]
        self.jump_image = pygame.image.load(os.path.join("assets","astronaut_jump.png"))
        self.shoot_image = pygame.image.load(os.path.join("assets","astronaut_shooting.png"))

    def handle_movement(self):
        if self.jumping:
            self.walk = False
            if self.jump_count < self.max_jump_height: #aktuelle sprunghöhe kleiner maximale sprunghöhe
                self.jump_count += self.jump_speed
                self.y -= self.jump_speed
            elif self.jump_count >= self.max_jump_height: #aktuelle sprunghöhe größer gleich maximale sprunghöhe
                if self.jump_count >= self.max_jump_height*2: #sprungbewegung in beide richtungen durchgeführt, dann zurücksetzen
                    self.jump_count = 0
                    self.jumping = False
                else:
                    self.jump_count += self.jump_speed
                    self.y += self.jump_speed                
        else:
            self.walk = True

        if self.shooting:
            if self.shoot_count < 15:
                self.shoot_count += 1
            else:
                self.shoot_count = 0
                self.shooting = False

    def draw(self,window):
        #updating the hitbox to current position
        self.hitbox = pygame.Rect(self.x+6,self.y,self.breite-12,self.hoehe)
        #pygame.draw.rect(window,(255,0,0),self.hitbox,2)
        #limiting the animationspeed; wechsel zwischen den Schritten alle 10 Frames
        if self.walkcount <= 10:
            walk_animation_pos = 0
        else:
            walk_animation_pos = 1

        if self.walkcount > 20:
            self.walkcount = 0
        #drawing different images to the screen based on movement state
        if self.shooting:
            scaled_image = pygame.transform.scale(self.shoot_image, (self.breite, self.hoehe))
            window.blit(scaled_image, (self.x, self.y))
        elif self.walk:
            scaled_image = pygame.transform.scale(self.walk_image[walk_animation_pos], (self.breite, self.hoehe))
            window.blit(scaled_image, (self.x, self.y))
            self.walkcount += 1
        elif self.jumping:
            scaled_image = pygame.transform.scale(self.jump_image, (self.breite, self.hoehe))
            window.blit(scaled_image, (self.x, self.y))
        else:
            scaled_image = pygame.transform.scale(self.image, (self.breite, self.hoehe))
            window.blit(scaled_image, (self.x, self.y))

class collectable_oxygen:
    def __init__(self,x,y):
        self.name = "oxygen"
        self.x = x
        self.y = y
        self.breite = 32
        self.hoehe = 32
        self.hitbox = pygame.Rect(self.x,self.y,self.breite,self.hoehe)
        self.image = pygame.image.load(os.path.join("assets","O2_Bubble.png"))
        self.scaled_image = pygame.transform.scale(self.image, (self.breite, self.hoehe))

    def draw(self,window):
        #updating the hitbox to current position
        self.hitbox = pygame.Rect(self.x,self.y,self.breite,self.hoehe)
        #drawing the scaled image
        window.blit(self.scaled_image, (self.x, self.y))

class tank_level:
    def __init__(self):
        self.x = 10
        self.y = 10
        self.breite = 104 
        self.hoehe = 48
        self.current_level = 50
        self.max_level = 100
        self.image = pygame.image.load(os.path.join("assets","O2_Bottle_Tileset3.png"))
        self.scaled_image = pygame.transform.scale(self.image, (self.breite*11, self.hoehe))

    def oxygen_collected(self):
        if self.current_level + 20 < self.max_level:
            self.current_level += 20
        else:
            self.current_level = self.max_level

    def consume_oxygen(self,health):
        if self.current_level -10 >= 0:
            self.current_level -= 10
        else:
            self.current_level = 0
            health.live_lost()

    def draw(self,window):
        x = (self.current_level//10)*self.breite
        window.blit(self.scaled_image, (self.x, self.y), (x,0,self.breite,self.hoehe)) 

class health_level:
    def __init__(self):
        self.current_level = 3
        self.max_level = 3
        self.breite = 56
        self.hoehe = 48
        self.image = pygame.image.load(os.path.join("assets","herz.png"))
        self.scaled_image = pygame.transform.scale(self.image, (self.breite, self.hoehe))

    def live_lost(self):
        self.current_level -= 1

    def draw(self,window):
        x = window.get_width() - (self.breite +10)
        for i in range(self.current_level):
            window.blit(self.scaled_image,(x,10))
            x -= (self.breite + 10)     

class score:
    def __init__(self):
        self.score = 1
        self.counter = 1
        self.font = pygame.font.SysFont("monospace",40)

    def increment_difficulty(self,game_speed):
        if self.counter % 1000 == 0 and game_speed <= 10:
            game_speed += 1
        return game_speed

    def draw(self,window):
        self.counter += 1
        self.score = self.counter//10
        text = self.font.render(str(self.score),True,(255,255,255))
        x = (window.get_width()//2) - (text.get_width()//2)
        window.blit(text, (x,10))

class enemy:
    def __init__(self,name,x,y,breite,hoehe,hitbox_correction): 
        self.name = name
        self.x = x
        self.y = y
        self.breite = breite
        self.hoehe = hoehe
        self.hb_cor = hitbox_correction
        self.hitbox = pygame.Rect(self.x+self.hb_cor[0],self.y+self.hb_cor[1],self.breite-self.hb_cor[2],self.hoehe-self.hb_cor[3])
        self.image = pygame.image.load(os.path.join("assets", self.name + ".png"))
        self.scaled_image = pygame.transform.scale(self.image, (self.breite, self.hoehe))

    def draw(self,window):
        #updating the hitbox to current position
        self.hitbox = pygame.Rect(self.x+self.hb_cor[0],self.y+self.hb_cor[1],self.breite-self.hb_cor[2],self.hoehe-self.hb_cor[3])
        #pygame.draw.rect(window,(255,0,0),self.hitbox,2)
        #drawing the scaled image
        window.blit(self.scaled_image, (self.x, self.y))

class bullets:
    def __init__(self):
        self.bullet_list = []

    def draw(self,window):
        for bullet in self.bullet_list:
            bullet.x += 4
            if bullet.x > window.get_width():
                self.bullet_list.remove(bullet) 
            pygame.draw.rect(window, (0,255,0), bullet)

def handle_collisions(spawned_objects,game_speed,spieler_hitbox,oxygen,health,spieler_bullets):
    for item in spawned_objects:
        item.x -= game_speed
        if item.x < item.breite * -1:
            spawned_objects.remove(item)
        elif spieler_hitbox.colliderect(item.hitbox) and item.name == "oxygen":              
            spawned_objects.remove(item)
            oxygen.oxygen_collected()
        elif spieler_hitbox.colliderect(item.hitbox):
            spawned_objects.remove(item)
            health.live_lost() 

        for bullet in spieler_bullets.bullet_list:
            if bullet.colliderect(item.hitbox):
                spawned_objects.remove(item)
                spieler_bullets.bullet_list.remove(bullet)

def draw_window(hintergrund_1,hintergrund_2,spieler_1,spawned_objects,oxygen,health,score,spieler_bullets):
    #alle draw methoden werden aufgerufen und dann das bild aktualisiert
    hintergrund_1.draw(window)
    hintergrund_2.draw(window)
    spieler_1.draw(window)
    for item in spawned_objects:
        item.draw(window)
    oxygen.draw(window)
    spieler_bullets.draw(window)
    health.draw(window)
    score.draw(window)
    pygame.display.update()

def main_gameloop():
    #initialize player and backgrounds
    game_speed = 4
    hintergrund_1 = background(window.get_width(),window.get_height(),0)
    hintergrund_2 = background(window.get_width(),window.get_height(),window.get_width())
    spieler_1 = player(250,518)
    spieler_bullets = bullets()
    spawned_objects = []
    oxygen = tank_level()
    health = health_level()
    myscore = score()
    #my events
    spawn_oxygen = pygame.USEREVENT +1
    pygame.time.set_timer(spawn_oxygen, 8000)
    consume_oxygen = pygame.USEREVENT +2
    pygame.time.set_timer(consume_oxygen, 4000)
    spawn_enemy = pygame.USEREVENT +3
    pygame.time.set_timer(spawn_enemy, 5000)
    run = True
    while run:
        clock.tick(FPS)
        #checking for events
        for event in pygame.event.get():
            if event.type==QUIT:
                pygame.quit()
                sys.exit()
                break
            elif event.type == pygame.KEYDOWN and event.key == K_ESCAPE:
                main_menu()
                break
            elif event.type == pygame.KEYDOWN and event.key == K_w:
                spieler_1.jumping = True
            elif event.type == pygame.KEYDOWN and event.key == K_e:
                if len(spieler_bullets.bullet_list) < 3:
                    bullet = pygame.Rect(spieler_1.x + spieler_1.breite, spieler_1.y + spieler_1.hoehe//2 -3, 10, 6)
                    spieler_bullets.bullet_list.append(bullet)
                    spieler_1.shooting = True
            elif event.type == spawn_oxygen:
                x = random.randint(1280,2560)
                y = random.randint(450,560)
                spawned_objects.append(collectable_oxygen(x,y))
            elif event.type == consume_oxygen:
                oxygen.consume_oxygen(health)
            elif event.type == spawn_enemy:
                auswahl = random.randint(0,3)
                if auswahl == 0:
                    spawned_objects.append(enemy("enemy_pflanze1",1280,578,35,30,[10,0,20,0]))
                elif auswahl == 1:
                    spawned_objects.append(enemy("alien_zyklop",1280,553,55,55,[15,0,15,0]))
                elif auswahl == 2:
                    spawned_objects.append(enemy("alien_oktopussi",1280,538,55,70,[10,0,20,0]))
                elif auswahl == 3:
                    spawned_objects.append(enemy("ufo",1280,480,64,64,[12,0,24,0]))
   
        #scrolling both backgrounds
        hintergrund_1.scroll(game_speed)
        hintergrund_2.scroll(game_speed)
        #handle player movement
        spieler_1.handle_movement()
        #handle collectable/enemy movement and collision
        handle_collisions(spawned_objects,game_speed,spieler_1.hitbox,oxygen,health,spieler_bullets)
        #check if the player is still alive  
        if health.current_level <= 0:
            print("GameOver - Keine Leben mehr.")
            gameover(myscore.score)
            break
        #erhöhen des schwierigkeitsgrads indem das Spiel schneller gemacht wird
        game_speed = myscore.increment_difficulty(game_speed)
        #calls the draw function
        draw_window(hintergrund_1,hintergrund_2,spieler_1,spawned_objects,oxygen,health,myscore,spieler_bullets)

def main_menu():
    while True:
        for event in pygame.event.get():
            if event.type==QUIT:
                pygame.quit()
                sys.exit()
                break
            elif event.type == pygame.KEYDOWN and event.key == K_SPACE:
                main_gameloop()
                break
        
        background = pygame.image.load(os.path.join("assets","main_menu_background.png"))
        #background = pygame.transform.scale(background, (window.get_width(), window.get_height()))
        window.blit(background,(0,0))
        pygame.display.update()

def gameover(score):
    while True:
        for event in pygame.event.get():
            if event.type==QUIT:
                pygame.quit()
                sys.exit()
                break
            elif event.type == pygame.KEYDOWN and event.key == K_ESCAPE:
                main_menu()
                break
            elif event.type == pygame.KEYDOWN and event.key == K_SPACE:
                main_gameloop()
                break
    
        window.fill((0,0,0))
        font69 = pygame.font.SysFont("monospace",69)
        font42 = pygame.font.SysFont("monospace",42)
        text1 = font69.render("GAME OVER",True,(255,255,255))
        window.blit(text1,((window.get_width()//2) - (text1.get_width()//2),(window.get_height()//2) - (text1.get_height()*2)))
        scoreText = font69.render("Score: " + str(score),True,(255,255,255))
        window.blit(scoreText,((window.get_width()//2) - (scoreText.get_width()//2),(window.get_height()//2) - (scoreText.get_height()//2)))
        text2 = font42.render("- Press SPACE to play again. -",True,(255,255,255))
        window.blit(text2,((window.get_width()//2) - (text2.get_width()//2),(window.get_height()//2) + text1.get_height()))

        pygame.display.update()

if __name__ == "__main__":
    main_menu()