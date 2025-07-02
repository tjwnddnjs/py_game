import pygame
import random
import sys

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('푸앙이런')

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

clock = pygame.time.Clock()
FPS = 60

obstacle_speed = -10

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
start_images = [
    pygame.transform.smoothscale(pygame.image.load("start1.png").convert_alpha(), START_IMG_SIZE),
    pygame.transform.smoothscale(pygame.image.load("start1.png").convert_alpha(), START_IMG_SIZE)
]
# --- [여기까지] ---

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.run_images = run_images
        self.jump_image = jump_image
        self.image = self.run_images[0]
        self.rect = self.image.get_rect()
        self.rect.x = 50
        self.rect.y = SCREEN_HEIGHT - PLAYER_SIZE[1]
        # --- [히트박스: 이미지 중앙 하단 기준, 크기 70x110] ---
        self.hitbox = pygame.Rect(0, 0, 70, 110)
        # ---------------------------------------------------
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

        # --- [히트박스 위치를 이미지 중앙 하단에 맞춤] ---
        self.hitbox.centerx = self.rect.centerx
        self.hitbox.bottom = self.rect.bottom
        # -------------------------------------------------

        if self.is_jumping:
            self.image = self.jump_image
        else:
            self.run_anim_timer += 1
            if self.run_anim_timer >= 10:
                self.run_frame = (self.run_frame + 1) % 2
                self.image = self.run_images[self.run_frame]
                self.run_anim_timer = 0

class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 50))
        self.image.fill((200, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = SCREEN_HEIGHT - 50
        self.speed_x = obstacle_speed

    def update(self):
        self.rect.x += self.speed_x
        if self.rect.right < 0:
            self.kill()

font_path = "C:/Windows/Fonts/malgun.ttf"  # 폰트 경로

# --- [시작화면 그리기: 이미지 2장 번갈아 표시] ---
def draw_start_screen(start_anim_frame):
    screen.fill(WHITE)
    # 캐릭터 이미지 애니메이션
    start_img = start_images[start_anim_frame % 2]
    screen.blit(start_img,   (SCREEN_WIDTH // 2 - START_IMG_SIZE[0] // 2, 40))

    # 타이틀
    font = pygame.font.Font(font_path, 30)
    title = font.render("", True, BLACK)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 20))

    # 버튼
    button_font = pygame.font.Font(font_path, 30)
    button_text = button_font.render("게임 시작", True, WHITE)
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
        if anim_timer >= 20:  # 20프레임마다 이미지 전환 (조절 가능)
            anim_frame = (anim_frame + 1) % 2
            anim_timer = 0
        clock.tick(FPS)

# --- 게임 시작 전 대기 화면 ---
wait_for_start()

# --- 본 게임 루프 ---
player = Player()
player_group = pygame.sprite.Group()
player_group.add(player)
obstacle_group = pygame.sprite.Group()

OBSTACLE_EVENT = pygame.USEREVENT + 1
SPEEDUP_EVENT = pygame.USEREVENT + 2

obstacle_interval = 1500
pygame.time.set_timer(OBSTACLE_EVENT, obstacle_interval)
pygame.time.set_timer(SPEEDUP_EVENT, 10000)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == OBSTACLE_EVENT:
            obstacle = Obstacle()
            obstacle_group.add(obstacle)
            obstacle_interval = random.randint(400, 2000)
            pygame.time.set_timer(OBSTACLE_EVENT, obstacle_interval)
        if event.type == SPEEDUP_EVENT:
            obstacle_speed -= 2
            print(f"장애물 속도 증가! 현재 속도: {abs(obstacle_speed)}")

    player_group.update()
    obstacle_group.update()

    # --- [히트박스 기준 충돌 체크] ---
    for obstacle in obstacle_group:
        if player.hitbox.colliderect(obstacle.rect):
            print('게임 오버!')
            running = False
            break
    # ---------------------------------

    # 화면 그리기
    screen.fill(WHITE)
    player_group.draw(screen)
    obstacle_group.draw(screen)
    # --- [히트박스 시각화 (빨간 테두리)] ---
    pygame.draw.rect(screen, (255, 0, 0), player.hitbox, 2)
    # --------------------------------------
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
      