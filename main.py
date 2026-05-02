import pygame
import os
from db import (
    create_player,
    update_stats,
    get_player,
    consume_recovery,
    level_up_player,
    set_level,
    get_leaderboard
)

#----------- INIT ----------
pygame.init()
pygame.font.init()
pygame.mixer.init()

WIN_WIDTH, WIN_HEIGHT = 900, 500
WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Firstgame")

# --------- COLORS -----------
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)

# ------ CONSTANTS ------
BOARDER = pygame.Rect(WIN_WIDTH // 2 - 5, 0, 10, WIN_HEIGHT)
FPS = 60

LEVELS = {
    1: {"bullet_vel": 6, "max_bullets": 3, "player_vel": 4},
    2: {"bullet_vel": 8, "max_bullets": 5, "player_vel": 5},
    3: {"bullet_vel": 10, "max_bullets": 7, "player_vel": 6},
    4: {"bullet_vel": 13, "max_bullets": 10, "player_vel": 7},
}

SHOW_LEVEL = True

YELLOW_HIT = pygame.USEREVENT + 1
RED_HIT = pygame.USEREVENT + 2

# ---------- FONTS ----------
HEALTH_FONT = pygame.font.SysFont("comicsans", 40)
NAME_FONT = pygame.font.SysFont("comicsans", 30)
NAME_TOP_PADDING = 80
LEVEL_FONT = pygame.font.SysFont("comicsans", 25)
WINNER_FONT = pygame.font.SysFont("comicsans", 60)

# ---------------- ASSETS ----------------
BULLET_FIRE_SOUND = pygame.mixer.Sound(os.path.join("assets", "Gun+Silencer.mp3"))
BULLET_HIT_SOUND = pygame.mixer.Sound(os.path.join("assets", "Grenade+1.mp3"))

PLAYER1 = pygame.transform.rotate(
    pygame.transform.scale(
        pygame.image.load(os.path.join("assets", "spaceship_yellow.png")), (55, 40)
    ),
    90,
)
PLAYER2 = pygame.transform.rotate(
    pygame.transform.scale(
        pygame.image.load(os.path.join("assets", "spaceship_red.png")), (55, 40)
    ),
    270,
)

SPACE = pygame.transform.scale(
    pygame.image.load(os.path.join("assets", "space.png")),
    (WIN_WIDTH, WIN_HEIGHT),
)

# ------- UI HELPERS -----------
def render_fit_text(text, color, max_width):
    size = 30
    while True:
        font = pygame.font.SysFont("comicsans", size)
        if font.size(text)[0] <= max_width or size <= 15:
            return font.render(text, True, color)
        size -= 1


def text_input_screen(title, prompt):
    clock = pygame.time.Clock()
    text = ""

    while True:
        clock.tick(30)
        WIN.fill((15, 15, 30))

        WIN.blit(
            WINNER_FONT.render(title, True, YELLOW),
            (WIN_WIDTH // 2 - 150, 100),
        )
        WIN.blit(NAME_FONT.render(prompt, True, WHITE), (280, 200))

        pygame.draw.rect(WIN, WHITE, (250, 260, 400, 50), 2)
        WIN.blit(HEALTH_FONT.render(text, True, YELLOW), (260, 270))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and text:
                    return text
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                elif len(text) < 15:
                    text += event.unicode


def leaderboard_screen():
    clock = pygame.time.Clock()
    data = get_leaderboard()

    while True:
        clock.tick(30)
        WIN.fill((10, 10, 20))

        WIN.blit(
            WINNER_FONT.render("LEADERBOARD", True, YELLOW),
            (WIN_WIDTH // 2 - 200, 50),
        )

        for i, p in enumerate(data):
            line = f"{i+1}. {p['username']}  -  Wins: {p['wins']}"
            WIN.blit(NAME_FONT.render(line, True, WHITE), (250, 150 + i * 40))

        WIN.blit(LEVEL_FONT.render("ESC - Back", True, WHITE), (10, 470))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return


def post_game_menu(winner):
    while True:
        WIN.fill(BLACK)

        WIN.blit(
            WINNER_FONT.render(f"{winner} WINS!", True, YELLOW),
            (WIN_WIDTH // 2 - 200, 150),
        )

        options = ["R - Retry Level", "N - Next Level", "L - Leaderboard", "Q - Quit"]

        for i, opt in enumerate(options):
            WIN.blit(NAME_FONT.render(opt, True, WHITE), (350, 260 + i * 40))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "retry"
                if event.key == pygame.K_n:
                    return "next"
                if event.key == pygame.K_l:
                    leaderboard_screen()
                if event.key == pygame.K_q:
                    return "quit"
                


# ---GAME LOGIC --
def yellow_handle_movement(keys, yellow, vel):
    if keys[pygame.K_a] and yellow.x > 0:
        yellow.x -= vel
    if keys[pygame.K_d] and yellow.x + yellow.width < BOARDER.x:
        yellow.x += vel
    if keys[pygame.K_w] and yellow.y > 0:
        yellow.y -= vel
    if keys[pygame.K_s] and yellow.y < WIN_HEIGHT - 40:
        yellow.y += vel


def red_handle_movement(keys, red, vel):
    if keys[pygame.K_LEFT] and red.x > BOARDER.x:
        red.x -= vel
    if keys[pygame.K_RIGHT] and red.x + red.width < WIN_WIDTH:
        red.x += vel
    if keys[pygame.K_UP] and red.y > 0:
        red.y -= vel
    if keys[pygame.K_DOWN] and red.y < WIN_HEIGHT - 40:
        red.y += vel


def handle_bullets(yb, rb, y, r, vel):
    for b in yb[:]:
        b.x += vel
        if r.colliderect(b):
            pygame.event.post(pygame.event.Event(RED_HIT))
            yb.remove(b)
        elif b.x > WIN_WIDTH:
            yb.remove(b)

    for b in rb[:]:
        b.x -= vel
        if y.colliderect(b):
            pygame.event.post(pygame.event.Event(YELLOW_HIT))
            rb.remove(b)
        elif b.x < 0:
            rb.remove(b)


def draw_window(red, yellow, rb, yb, rh, yh, ln, rn, lvl):
    WIN.blit(SPACE, (0, 0))
    pygame.draw.rect(WIN, BLACK, BOARDER)

    WIN.blit(HEALTH_FONT.render(f"Health: {yh}", True, WHITE), (10, 10))
    WIN.blit(HEALTH_FONT.render(f"Health: {rh}", True, WHITE), (700, 10))


    right_name = render_fit_text(rn, RED, 200)
    WIN.blit(render_fit_text(ln, YELLOW, 200), (10, NAME_TOP_PADDING))

    right_name = render_fit_text(rn, RED, 200)
    WIN.blit(right_name, (WIN_WIDTH - 10 - right_name.get_width(), NAME_TOP_PADDING))


    if SHOW_LEVEL:
        WIN.blit(LEVEL_FONT.render(f"Level {lvl}", True, WHITE), (420, 10))

    WIN.blit(PLAYER1, (yellow.x, yellow.y))
    WIN.blit(PLAYER2, (red.x, red.y))

    for b in yb:
        pygame.draw.rect(WIN, YELLOW, b)
    for b in rb:
        pygame.draw.rect(WIN, RED, b)

    pygame.display.update()


# ----- MAIN ------
def main():
    left = text_input_screen("FOOLWING", "Enter LEFT Player Name")
    right = text_input_screen("FOOLWING", "Enter RIGHT Player Name")

    create_player(left)
    create_player(right)

    current_level = min(get_player(left)["level"], 4)

    while True:
        cfg = LEVELS[current_level]
        bullet_vel = cfg["bullet_vel"]
        max_bullets = cfg["max_bullets"]
        player_vel = cfg["player_vel"]

        yh = rh = 10
        yellow = pygame.Rect(100, 300, 55, 40)
        red = pygame.Rect(700, 300, 55, 40)

        yb, rb = [], []
        clock = pygame.time.Clock()
        run = True

        while run:
            clock.tick(FPS)
            keys = pygame.key.get_pressed()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LCTRL and len(yb) < max_bullets:
                        yb.append(pygame.Rect(yellow.x + yellow.width, yellow.y + 18, 10, 5))
                    if event.key == pygame.K_RCTRL and len(rb) < max_bullets:
                        rb.append(pygame.Rect(red.x, red.y + 18, 10, 5))

                if event.type == RED_HIT:
                    rh -= 1
                if event.type == YELLOW_HIT:
                    yh -= 1

            if rh <= 0 or yh <= 0:
                winner = left if rh <= 0 else right
                update_stats(winner, True)
                choice = post_game_menu(winner)

                if choice == "next":
                    current_level = min(current_level + 1, 4)
                    level_up_player(winner)
                    set_level(winner, current_level)
                if choice == "quit":
                    pygame.quit()
                    return
                break

            yellow_handle_movement(keys, yellow, player_vel)
            red_handle_movement(keys, red, player_vel)
            handle_bullets(yb, rb, yellow, red, bullet_vel)

            draw_window(red, yellow, rb, yb, rh, yh, left, right, current_level)


if __name__ == "__main__":
    main()








