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
background_forest_img = pygame.image.load("assets/background_images/test_forest_image.jpg").convert_alpha()
panel_wood_img = pygame.image.load("assets/ui/menu_background/wooden_menu_1.jpg")

def draw_bg():
    screen.blit(background_forest_img, (0,0))

def draw_panel():
    screen.blit(panel_wood_img, (0, screen_height - bottom_panel))


class Character():
    def __init__(self, x, y, name, max_hp, strength, potions, image_path, flip=False):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.strength = strength
        self.start_potion = potions
        self.potions = potions
        self.flip = flip
        self.x = x
        self.y = y

        # animation variables
        self.frame_index = 0
        self.animation_counter = 0
        self.animation_speed = 8  # lower = faster animation

        # load and store the full sprite sheet
        self.sprite_sheet = pygame.image.load(image_path)

        # count how many frames are in the sheet
        self.frame_count = self.sprite_sheet.get_width() // 100

        # load all frames into a list
        self.frames = []
        for i in range(self.frame_count):
            # cut each frame out
            frame = self.sprite_sheet.subsurface(pygame.Rect(i * 100, 0, 100, 100))
            # scale it up
            frame = pygame.transform.scale(frame, (frame.get_width() * 3, frame.get_height() * 3))
            # flip if enemy
            if flip:
                frame = pygame.transform.flip(frame, True, False)
            self.frames.append(frame)

        # set starting image
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update_animation(self):
        # tick the counter
        self.animation_counter += 1

        # when counter reaches animation speed move to next frame
        if self.animation_counter >= self.animation_speed:
            self.animation_counter = 0
            # advance frame and loop back to 0 when reaching the end
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]

    def draw(self):
        # update animation every draw call
        self.update_animation()
        screen.blit(self.image, self.rect)


# soldier on the left
soldier = Character(
    x=170, y=260,
    name="Soldier",
    max_hp=30, strength=10, potions=3,
    image_path="assets/characters/tiny_rpg_chars_placeholders/Characters(100x100)/Soldier/Soldier/Soldier-Idle.png",
    flip=False
)

# orcs on the right
orc_path = "assets/characters/tiny_rpg_chars_placeholders/Characters(100x100)/Orc/Orc/Orc-Idle.png"

enemy_list = [
    Character(370, 230, "Orc1", 40, 12, 0, orc_path, flip=True),
    Character(420, 260, "Orc2", 40, 12, 0, orc_path, flip=True),
    Character(370, 300, "Orc3", 40, 12, 0, orc_path, flip=True),
]

run = True
while run:
    clock.tick(fps)

    draw_bg()
    draw_panel()

    # draw soldier
    soldier.draw()

    # draw all enemies
    for enemy in enemy_list:
        enemy.draw()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()