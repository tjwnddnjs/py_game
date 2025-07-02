import pygame
import random
import sys

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('PUANG RUN')

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

clock = pygame.time.Clock()
FPS = 60

obstacle_speed_init = -10  # 초기 장애물 속도
PLAYER_SIZE = (150, 150)

def load_flipped(filename):
    img = pygame.transform.smoothscale(pygame.image.load(filename).convert_alpha(), PLAYER_SIZE)
    img_flipped = pygame.transform.flip(img, True, False)
    return img_flipped

run_images = [
    load_flipped("run1.png"),
    load_flipped("run2.png")
]
jump_image = load_flipped("jump.png")

# --- [시작화면용 이미지 불러오기] ---
START_IMG_SIZE = (200, 200)

# [추가] 타원형 마스킹 함수
def make_ellipse_masked_surface(img, size):
    mask = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.ellipse(mask, (255, 255, 255, 255), mask.get_rect())
    img = pygame.transform.smoothscale(img, size)
    masked_img = pygame.Surface(size, pygame.SRCALPHA)
    masked_img.blit(img, (0, 0))
    masked_img.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return masked_img

# [수정] 시작 이미지 불러오기 함수
def load_start_image(filename):
    img = pygame.image.load(filename).convert_alpha()
    return make_ellipse_masked_surface(img, START_IMG_SIZE)

start_images = [
    load_start_image("start1.png"),
    load_start_image("start2.png")
]
# --- [여기까지] ---

font_path = "C:/Windows/Fonts/malgun.ttf"  # 폰트 경로

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.run_images = run_images
        self.jump_image = jump_image
        self.image = self.run_images[0]
        self.rect = self.image.get_rect()
        self.rect.x = 50
        self.rect.y = SCREEN_HEIGHT - PLAYER_SIZE[1]
        self.hitbox = pygame.Rect(0, 0, 70, 110)
        self.jump_speed = -15
        self.gravity = 1
        self.speed_y = 0
        self.is_jumping = False
        self.run_frame = 0
        self.run_anim_timer = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if not self.is_jumping:
            if keys[pygame.K_SPACE]:
                self.speed_y = self.jump_speed
                self.is_jumping = True

        self.speed_y += self.gravity
        self.rect.y += self.speed_y

        if self.rect.y >= SCREEN_HEIGHT - PLAYER_SIZE[1]:
            self.rect.y = SCREEN_HEIGHT - PLAYER_SIZE[1]
            self.is_jumping = False

        self.hitbox.centerx = self.rect.centerx
        self.hitbox.bottom = self.rect.bottom

        if self.is_jumping:
            self.image = self.jump_image
        else:
            self.run_anim_timer += 1
            if self.run_anim_timer >= 10:
                self.run_frame = (self.run_frame + 1) % 2
                self.image = self.run_images[self.run_frame]
                self.run_anim_timer = 0

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.image = pygame.Surface((30, 50))
        self.image.fill((200, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = SCREEN_HEIGHT - 50
        self.speed_x = speed
        self.passed = False

    def update(self):
        self.rect.x += self.speed_x
        if self.rect.right < 0:
            self.kill()

def draw_start_screen(start_anim_frame):
    screen.fill(WHITE)
    start_img = start_images[start_anim_frame % 2]
    screen.blit(start_img, (SCREEN_WIDTH // 2 - START_IMG_SIZE[0] // 2, 40))
    font = pygame.font.Font(font_path, 30)
    title = font.render("", True, BLACK)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 20))
    button_font = pygame.font.Font(font_path, 25)
    button_text = button_font.render("Game Start", True, WHITE)
    button_rect = pygame.Rect(0, 0, 150, 50)
    button_rect.center = (SCREEN_WIDTH // 2, 300)
    pygame.draw.rect(screen, (100, 180, 255), button_rect, border_radius=20)
    screen.blit(button_text, (button_rect.centerx - button_text.get_width() // 2,
                              button_rect.centery - button_text.get_height() // 2))
    pygame.display.flip()
    return button_rect

def wait_for_start():
    anim_timer = 0
    anim_frame = 0
    while True:
        button_rect = draw_start_screen(anim_frame)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    return
        anim_timer += 1
        if anim_timer >= 20:
            anim_frame = (anim_frame + 1) % 2
            anim_timer = 0
        clock.tick(FPS)

def show_game_over_screen(score):
    while True:
        screen.fill(WHITE)
        font = pygame.font.Font(font_path, 60)
        over_text = font.render("Game Over", True, (200, 0, 0))
        screen.blit(over_text, (SCREEN_WIDTH // 2 - over_text.get_width() // 2, 80))

        score_font = pygame.font.Font(font_path, 40)
        score_text = score_font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 170))

        button_font = pygame.font.Font(font_path, 35)
        button_text = button_font.render("Get Ready", True, WHITE)
        button_rect = pygame.Rect(0, 0, 200, 60)
        button_rect.center = (SCREEN_WIDTH // 2, 260)
        pygame.draw.rect(screen, (100, 180, 255), button_rect, border_radius=20)
        screen.blit(button_text, (button_rect.centerx - button_text.get_width() // 2,
                                  button_rect.centery - button_text.get_height() // 2))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    return  # 다시 시작

        clock.tick(FPS)

def main_game():
    global obstacle_speed_init
    obstacle_speed = obstacle_speed_init
    player = Player()
    player_group = pygame.sprite.Group()
    player_group.add(player)
    obstacle_group = pygame.sprite.Group()

    OBSTACLE_EVENT = pygame.USEREVENT + 1
    SPEEDUP_EVENT = pygame.USEREVENT + 2

    obstacle_interval = 1500
    pygame.time.set_timer(OBSTACLE_EVENT, obstacle_interval)
    pygame.time.set_timer(SPEEDUP_EVENT, 10000)

    score = 0
    base_score_per_jump = 100

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == OBSTACLE_EVENT:
                obstacle = Obstacle(obstacle_speed)
                obstacle_group.add(obstacle)
                obstacle_interval = random.randint(400, 2000)
                pygame.time.set_timer(OBSTACLE_EVENT, obstacle_interval)
            if event.type == SPEEDUP_EVENT:
                obstacle_speed -= 2
                base_score_per_jump += 10
                print(f"Current Velocity : {abs(obstacle_speed)}, Score : {base_score_per_jump}")

        player_group.update()
        obstacle_group.update()

        # 충돌 체크
        for obstacle in obstacle_group:
            if player.hitbox.colliderect(obstacle.rect):
                running = False
                break

        # 장애물 뛰어넘음 판정 및 점수 증가
        for obstacle in obstacle_group:
            if not obstacle.passed and obstacle.rect.right < player.hitbox.left:
                score += base_score_per_jump
                obstacle.passed = True

        # 화면 그리기
        screen.fill(WHITE)
        player_group.draw(screen)
        obstacle_group.draw(screen)
        # pygame.draw.rect(screen, (255, 0, 0), player.hitbox, 2) # 디버깅용 히트박스 표시

        # 점수 표시
        score_font = pygame.font.Font(font_path, 30)
        score_text = score_font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (20, 20))

        pygame.display.flip()
        clock.tick(FPS)

    return score

# --- 메인 루프 ---
while True:
    wait_for_start()
    final_score = main_game()
    show_game_over_screen(final_score)
