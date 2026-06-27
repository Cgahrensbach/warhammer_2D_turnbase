import pygame

pygame.init()

clock = pygame.time.Clock()
fps = 60

#game window
bottom_panel = 150
screen_width = 525
screen_height = 350 + bottom_panel


screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Warhammer AOS 2D")

#load images
#background image
background_forest_img = pygame.image.load("assets/background_images/test_forest_image.jpg").convert_alpha()
#panel image
panel_wood_img = pygame.image.load("assets/ui/menu_background/wooden_menu_1.jpg")
#function for drawing background
def draw_bg():
    screen.blit(background_forest_img, (0,0))

#function for drawing panel
def draw_panel():
    screen.blit(panel_wood_img, (0, screen_height - bottom_panel))

#stabba class
class Stabba():
    def __init__(self, x, y, name, max_hp, strength, potions):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.strength = strength
        self.start_potion = potions
        self.potions = potions
        self.image = pygame.image.load("")
run = True
while run:
    
    clock.tick(fps)
    
    #draw background
    draw_bg()
    
    #draw panel
    draw_panel()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            
    pygame.display.update()

pygame.quit()