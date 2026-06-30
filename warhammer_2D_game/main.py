import pygame
import random

pygame.init()

# ── MUSIC ─────────────────────────────────────
pygame.mixer.init()
pygame.mixer.music.load("assets/music/battle_theme.mp3")
pygame.mixer.music.set_volume(0.3)   # 0.0 = silent, 1.0 = full volume
pygame.mixer.music.play(-1)          # -1 means loop forever
clock = pygame.time.Clock()

fps = 60

# ─────────────────────────────────────────────
# SCREEN SETUP
# ─────────────────────────────────────────────
bottom_panel = 150
screen_width  = 525
screen_height = 350 + bottom_panel

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Warhammer AOS 2D")

# ─────────────────────────────────────────────
# FONTS & COLORS
# ─────────────────────────────────────────────
font        = pygame.font.SysFont("cinzeldecorative", 25)
font_small  = pygame.font.SysFont("cinzeldecorative", 11)
font_medium  = pygame.font.SysFont("cinzeldecorative", 18)

RED         = (200,  40,  40)
GREEN       = ( 40, 180,  40)
BLACK       = (  0,   0,   0)
WHITE       = (255, 255, 255)
GOLD        = (212, 175,  55)
DARK_GREY   = ( 40,  40,  40)

# ─────────────────────────────────────────────
# LOAD SHARED ASSETS
# ─────────────────────────────────────────────
background_forest_img = pygame.image.load(
    "assets/background_images/test_forest_image.jpg"
).convert_alpha()

panel_wood_img = pygame.image.load(
    "assets/ui/menu_background/wooden_menu_1.jpg"
).convert()

button_img = pygame.image.load(
    "assets/ui/buttons/button_wood_1.jpg"
).convert()


# ─────────────────────────────────────────────
# HELPER – load every frame from a sprite sheet
# ─────────────────────────────────────────────
def load_frames(path, frame_w, frame_h, scale, flip=False):
    sheet  = pygame.image.load(path).convert_alpha()
    count  = sheet.get_width() // frame_w
    frames = []
    for i in range(count):
        f = sheet.subsurface(pygame.Rect(i * frame_w, 0, frame_w, frame_h))
        f = pygame.transform.scale(f, (frame_w * scale, frame_h * scale))
        if flip:
            f = pygame.transform.flip(f, True, False)
        frames.append(f)
    return frames


# ─────────────────────────────────────────────
# CHARACTER CLASS
# ─────────────────────────────────────────────
BASE = "assets/characters/tiny_rpg_chars_placeholders/Characters(100x100)"

class Character:
    def __init__(self, x, y, name, max_hp, strength, potions,
                 idle_path, attack_path, hurt_path, death_path,
                 flip=False, scale=3, sprite_top_offset=0):

        self.name      = name
        self.max_hp    = max_hp
        self.hp        = max_hp
        self.strength  = strength
        self.potions   = potions
        self.start_potions = potions   # remember original for restart
        self.flip      = flip
        self.alive     = True
        self.x, self.y = x, y
        self.sprite_top_offset = sprite_top_offset

        # store paths and config for restart
        self._idle_path   = idle_path
        self._attack_path = attack_path
        self._hurt_path   = hurt_path
        self._death_path  = death_path
        self._scale       = scale

        self.anims = {
            "idle"  : load_frames(idle_path,   100, 100, scale, flip),
            "attack": load_frames(attack_path, 100, 100, scale, flip),
            "hurt"  : load_frames(hurt_path,   100, 100, scale, flip),
            "death" : load_frames(death_path,  100, 100, scale, flip),
        }

        self.current_anim = "idle"
        self.frame_index  = 0
        self.anim_counter = 0
        self.anim_speed   = 8
        self.anim_done    = False

        self.image = self.anims["idle"][0]
        self.rect  = self.image.get_rect(center=(x, y))

    def reset(self):
        """Restore character to full health for a new mission."""
        self.hp        = self.max_hp
        self.potions   = self.start_potions
        self.alive     = True
        self.set_anim("idle")
        self.frame_index  = 0
        self.anim_counter = 0
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def set_anim(self, name):
        if self.current_anim != name:
            self.current_anim = name
            self.frame_index  = 0
            self.anim_counter = 0
            self.anim_done    = False

    def update_animation(self):
        frames = self.anims[self.current_anim]
        self.anim_counter += 1
        if self.anim_counter >= self.anim_speed:
            self.anim_counter = 0
            self.frame_index += 1
            if self.frame_index >= len(frames):
                if self.current_anim in ("attack", "hurt"):
                    self.anim_done = True
                    self.set_anim("idle")
                elif self.current_anim == "death":
                    self.frame_index = len(frames) - 1
                    self.anim_done   = True
                else:
                    self.frame_index = 0
            self.image = frames[min(self.frame_index, len(frames) - 1)]

    def take_damage(self, amount):
        if not self.alive:
            return
        self.hp -= amount
        if self.hp <= 0:
            self.hp    = 0
            self.alive = False
            self.set_anim("death")
        else:
            self.set_anim("hurt")

    def use_potion(self):
        if self.potions > 0 and self.hp < self.max_hp:
            heal = random.randint(15, 35)
            self.hp = min(self.max_hp, self.hp + heal)
            self.potions -= 1
            return heal
        return 0

    @property
    def visual_top(self):
        return self.rect.top + self.sprite_top_offset

    def draw(self):
        self.update_animation()
        screen.blit(self.image, self.rect)
        if self.alive:
            self._draw_health_bar()
            self._draw_name()

    def _draw_health_bar(self):
        bar_w, bar_h = 80, 10
        bx = self.rect.centerx - bar_w // 2
        by = self.visual_top - bar_h - 2

        pygame.draw.rect(screen, DARK_GREY,
                         (bx - 1, by - 1, bar_w + 2, bar_h + 2), border_radius=4)
        pygame.draw.rect(screen, RED,
                         (bx, by, bar_w, bar_h), border_radius=3)
        fill = int(bar_w * (self.hp / self.max_hp))
        if fill > 0:
            pygame.draw.rect(screen, GREEN,
                             (bx, by, fill, bar_h), border_radius=3)
        pygame.draw.rect(screen, GOLD,
                         (bx - 1, by - 1, bar_w + 2, bar_h + 2), 1, border_radius=4)
        hp_txt = font_small.render(f"{self.hp}/{self.max_hp}", True, WHITE)
        screen.blit(hp_txt, (bx + bar_w // 2 - hp_txt.get_width() // 2, by))

    def _draw_name(self):
        name_txt = font_small.render(self.name, True, GOLD)
        bar_h    = 10
        by       = self.visual_top - bar_h - 2
        screen.blit(name_txt,
                    (self.rect.centerx - name_txt.get_width() // 2,
                     by - name_txt.get_height() - 2))


# ─────────────────────────────────────────────
# BUTTON CLASS
# ─────────────────────────────────────────────
class Button:
    def __init__(self, x, y, w, h, label):
        self.rect    = pygame.Rect(x, y, w, h)
        self.label   = label
        self.hovered = False
        self.img     = pygame.transform.scale(button_img, (w, h))

    def draw(self):
        screen.blit(self.img, self.rect)
        if self.hovered:
            surf = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
            surf.fill((255, 255, 200, 50))
            screen.blit(surf, self.rect)
        pygame.draw.rect(screen, GOLD, self.rect, 2, border_radius=4)
        txt = font.render(self.label, True, WHITE)
        screen.blit(txt, (self.rect.centerx - txt.get_width()  // 2,
                           self.rect.centery - txt.get_height() // 2))

    def is_clicked(self, pos, click):
        self.hovered = self.rect.collidepoint(pos)
        return self.hovered and click


# ─────────────────────────────────────────────
# DRAW HELPERS
# ─────────────────────────────────────────────
def draw_bg():
    screen.blit(background_forest_img, (0, 0))

def draw_panel():
    screen.blit(panel_wood_img, (0, screen_height - bottom_panel))
    pygame.draw.line(screen, GOLD,
                     (0, screen_height - bottom_panel),
                     (screen_width, screen_height - bottom_panel), 2)

def draw_message(msg, color=WHITE):
    txt = font.render(msg, True, color)
    screen.blit(txt, (screen_width // 2 - txt.get_width() // 2, 10))

def draw_potions(character):
    pot_txt = font_medium.render(f"Potions: {character.potions}", True, GOLD)
    screen.blit(pot_txt, (20, screen_height - bottom_panel + 115))


# ─────────────────────────────────────────────
# BUILD CHARACTERS
# ─────────────────────────────────────────────
S = f"{BASE}/Soldier/Soldier"
O = f"{BASE}/Orc/Orc"

soldier = Character(
    x=150, y=260,
    name="Soldier",
    max_hp=100, strength=15, potions=3,
    idle_path   = f"{S}/Soldier-Idle.png",
    attack_path = f"{S}/Soldier-Attack01.png",
    hurt_path   = f"{S}/Soldier-Hurt.png",
    death_path  = f"{S}/Soldier-Death.png",
    flip=False,
    sprite_top_offset=117,
)

orc_path_args = dict(
    idle_path   = f"{O}/Orc-Idle.png",
    attack_path = f"{O}/Orc-Attack01.png",
    hurt_path   = f"{O}/Orc-Hurt.png",
    death_path  = f"{O}/Orc-Death.png",
    flip=True,
    sprite_top_offset=126,
)

enemy_list = [
    Character(360, 210, "Orc Grunt",  50, 10, 0, **orc_path_args),
    Character(410, 260, "Orc Brute",  65, 14, 0, **orc_path_args),
    Character(360, 310, "Orc Shaman", 40,  8, 0, **orc_path_args),
]

all_characters = [soldier] + enemy_list


# ─────────────────────────────────────────────
# BUTTONS
# ─────────────────────────────────────────────
panel_y      = screen_height - bottom_panel
btn_w, btn_h = 100, 36

attack_btn  = Button(20, panel_y + 20, btn_w, btn_h, "ATTACK")
potion_btn  = Button(20, panel_y + 66, btn_w, btn_h, "POTION")
restart_btn = Button(screen_width // 2 - 75, screen_height // 2 + 20, 150, 44, "RESTART")

enemy_btns = []
for i, enemy in enumerate(enemy_list):
    eb = Button(145 + i * 115, panel_y + 20, 105, 36, enemy.name)
    enemy_btns.append(eb)


# ─────────────────────────────────────────────
# GAME STATE
# ─────────────────────────────────────────────
PLAYER_TURN = 0
ENEMY_TURN  = 1
VICTORY     = 2
DEFEAT      = 3

def reset_game():
    """Reset all characters and return fresh game state variables."""
    for c in all_characters:
        c.reset()
    return PLAYER_TURN, None, None, "Choose an action!", WHITE, 0

game_state, selected_enemy, action_chosen, message, message_color, enemy_turn_timer = reset_game()
ENEMY_DELAY = 60


# ─────────────────────────────────────────────
# GAME LOOP
# ─────────────────────────────────────────────
run = True
while run:
    clock.tick(fps)

    mouse_pos = pygame.mouse.get_pos()
    click     = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            click = True

    # DRAW WORLD
    draw_bg()
    draw_panel()
    draw_potions(soldier)

    soldier.draw()
    for enemy in enemy_list:
        enemy.draw()

    if selected_enemy is not None and selected_enemy.alive:
        r = selected_enemy.rect
        pygame.draw.rect(screen, GOLD, (r.left, r.bottom + 2, r.width, 3))

    # PLAYER TURN
    if game_state == PLAYER_TURN:
        attack_btn.draw()
        potion_btn.draw()

        if action_chosen is not None:
            for i, eb in enumerate(enemy_btns):
                if enemy_list[i].alive:
                    eb.draw()

        if attack_btn.is_clicked(mouse_pos, click):
            action_chosen = "attack"
            message       = "Select a target!"
            message_color = GOLD

        if potion_btn.is_clicked(mouse_pos, click):
            if soldier.potions > 0 and soldier.hp < soldier.max_hp:
                healed        = soldier.use_potion()
                message       = f"Used a potion! +{healed} HP"
                message_color = GREEN
                action_chosen = None
                game_state    = ENEMY_TURN
                enemy_turn_timer = ENEMY_DELAY
            elif soldier.potions == 0:
                message       = "No potions left!"
                message_color = RED
            else:
                message       = "Already at full HP!"
                message_color = RED

        if action_chosen == "attack":
            for i, eb in enumerate(enemy_btns):
                if enemy_list[i].alive and eb.is_clicked(mouse_pos, click):
                    selected_enemy = enemy_list[i]
                    dmg = random.randint(soldier.strength - 5,
                                         soldier.strength + 5)
                    soldier.set_anim("attack")
                    selected_enemy.take_damage(dmg)
                    message        = f"You hit {selected_enemy.name} for {dmg}!"
                    message_color  = WHITE
                    action_chosen  = None
                    selected_enemy = None

                    if all(not e.alive for e in enemy_list):
                        game_state = VICTORY
                    else:
                        game_state       = ENEMY_TURN
                        enemy_turn_timer = ENEMY_DELAY

    # ENEMY TURN 
    elif game_state == ENEMY_TURN:
        message       = "Enemy is thinking..."
        message_color = RED

        enemy_turn_timer -= 1
        if enemy_turn_timer <= 0:
            living = [e for e in enemy_list if e.alive]
            if living and soldier.alive:
                attacker = random.choice(living)
                dmg      = random.randint(attacker.strength - 3,
                                           attacker.strength + 3)
                attacker.set_anim("attack")
                soldier.take_damage(dmg)
                message       = f"{attacker.name} hit you for {dmg}!"
                message_color = RED

                game_state = DEFEAT if not soldier.alive else PLAYER_TURN

    #VICTORY
    elif game_state == VICTORY:
        # dim overlay
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))

        title = font.render("VICTORY!", True, GOLD)
        sub   = font_small.render("All enemies have been slain.", True, WHITE)
        screen.blit(title, (screen_width // 2 - title.get_width() // 2,
                             screen_height // 2 - 50))
        screen.blit(sub,   (screen_width // 2 - sub.get_width() // 2,
                             screen_height // 2 - 20))
        restart_btn.draw()

        if restart_btn.is_clicked(mouse_pos, click):
            (game_state, selected_enemy, action_chosen,
             message, message_color, enemy_turn_timer) = reset_game()

    # DEFEAT 
    elif game_state == DEFEAT:
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((80, 0, 0, 140))
        screen.blit(overlay, (0, 0))

        title = font.render("DEFEAT!", True, RED)
        sub   = font_small.render("You have fallen in battle.", True, WHITE)
        screen.blit(title, (screen_width // 2 - title.get_width() // 2,
                             screen_height // 2 - 50))
        screen.blit(sub,   (screen_width // 2 - sub.get_width() // 2,
                             screen_height // 2 - 20))
        restart_btn.draw()

        if restart_btn.is_clicked(mouse_pos, click):
            (game_state, selected_enemy, action_chosen,
             message, message_color, enemy_turn_timer) = reset_game()

    # draw message only during active play
    if game_state in (PLAYER_TURN, ENEMY_TURN):
        draw_message(message, message_color)

    pygame.display.update()

pygame.quit()