import pygame
import random
import sys

pygame.init()

# 핸드폰 세로 비율 (예: 480x800)
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('PUANG RUN')

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BUTTON_COLOR = (100, 180, 255)  # 버튼 색상

clock = pygame.time.Clock()
FPS = 60

obstacle_speed_init = -6  # 모바일에서 적당한 장애물 속도(음수!)
PLAYER_SIZE = (160, 160)    # 캐릭터 크기

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
START_IMG_SIZE = (300, 300)

def make_ellipse_masked_surface(img, size):
    mask = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.ellipse(mask, (255, 255, 255, 255), mask.get_rect())
    img = pygame.transform.smoothscale(img, size)
    masked_img = pygame.Surface(size, pygame.SRCALPHA)
    masked_img.blit(img, (0, 0))
    masked_img.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return masked_img

def load_start_image(filename):
    img = pygame.image.load(filename).convert_alpha()
    return make_ellipse_masked_surface(img, START_IMG_SIZE)

start_images = [
    load_start_image("start1.png"),
    load_start_image("start2.png")
]

font_path = "DungGeunMo.ttf"  # 폰트 경로

# --- 구름 이미지 불러오기 및 구름 클래스 추가 ---
CLOUD_SIZE = (150, 150)  # 캐릭터보다 조금 작게

def load_cloud_image(filename):
    img = pygame.image.load(filename).convert_alpha()
    return make_ellipse_masked_surface(img, CLOUD_SIZE)

cloud_images = [
    load_cloud_image("object1.png"),
    load_cloud_image("object2.png")
]

class Cloud(pygame.sprite.Sprite):
    def __init__(self, images, existing_rects=None, force_x=None):
        super().__init__()
        idx = random.randint(0, len(images)-1)
        self.image = images[idx]
        self.rect = self.image.get_rect()
        self.rect.y = random.randint(10, int(SCREEN_HEIGHT * 0.25))
        self.rect.x = force_x if force_x is not None else SCREEN_WIDTH + random.randint(0, 120)
        # 구름 속도를 확실히 움직이도록 1.2~2.0으로 조정
        self.speed_x = random.uniform(1.2, 1.4)
        # print(f"Cloud speed_x: {self.speed_x:.2f}")  # 디버깅용, 필요 없으면 주석 처리
        if existing_rects is not None:
            tries = 0
            while any(self.rect.colliderect(r.inflate(10, 10)) for r in existing_rects):
                self.rect.y = random.randint(10, int(SCREEN_HEIGHT * 0.25))
                self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
                tries += 1
                if tries > 50:
                    break

    def update(self):
        self.rect.x -= self.speed_x
        if self.rect.right < 0:
            self.kill()

cloud_group = pygame.sprite.Group()

CLOUD_EVENT = pygame.USEREVENT + 10
pygame.time.set_timer(CLOUD_EVENT, 3500)  # 3.5초마다 구름 생성

def init_clouds():
    existing_rects = []
    for i in range(3):
        force_x = int(i * (SCREEN_WIDTH / 5) + random.randint(-20, 20))
        cloud = Cloud(cloud_images, existing_rects=existing_rects, force_x=force_x)
        existing_rects.append(cloud.rect.copy())
        cloud_group.add(cloud)
init_clouds()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.run_images = run_images
        self.jump_image = jump_image
        self.image = self.run_images[0]
        self.rect = self.image.get_rect()
        self.rect.x = int(SCREEN_WIDTH * 0.13)  # 왼쪽에서 13% 위치
        self.rect.y = SCREEN_HEIGHT - PLAYER_SIZE[1] - 30  # 바닥에서 30px 위
        self.hitbox = pygame.Rect(0, 0, 45, 70)
        self.jump_speed = -18  # 점프 높이
        self.gravity = 1.1     # 중력
        self.speed_y = 0
        self.is_jumping = False
        self.run_frame = 0
        self.run_anim_timer = 0

    def update(self):
        # 모바일: 화면 터치로 점프
        keys = pygame.key.get_pressed()
        mouse_pressed = pygame.mouse.get_pressed()
        if not self.is_jumping:
            if keys[pygame.K_SPACE] or mouse_pressed[0]:
                self.speed_y = self.jump_speed
                self.is_jumping = True

        self.speed_y += self.gravity
        self.rect.y += self.speed_y

        if self.rect.y >= SCREEN_HEIGHT - PLAYER_SIZE[1] - 30:
            self.rect.y = SCREEN_HEIGHT - PLAYER_SIZE[1] - 30
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
        self.image = pygame.Surface((30, 60))
        self.image.fill((200, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = SCREEN_HEIGHT - 60 - 30  # 바닥에서 30px 위
        self.speed_x = speed
        self.passed = False

    def update(self):
        self.rect.x += self.speed_x
        if self.rect.right < 0:
            self.kill()

def draw_start_screen(start_anim_frame):
    screen.fill(WHITE)
    cloud_group.update()
    cloud_group.draw(screen)
    
    # "Game Start" 글씨 위치 계산
    button_font = pygame.font.Font(font_path, 60)
    button_text = button_font.render("Game Start", True, BUTTON_COLOR)
    button_rect = button_text.get_rect(center=(SCREEN_WIDTH // 2, int(SCREEN_HEIGHT * 0.7)))
    
    # 푸앙이 이미지를 GAME START 글씨 위에 blit
    start_img = start_images[start_anim_frame % 2]
    puang_rect = start_img.get_rect(midbottom=(button_rect.centerx, button_rect.top - 10))
    screen.blit(start_img, puang_rect)
    
    # GAME START 글씨
    screen.blit(button_text, button_rect)
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
            if event.type == CLOUD_EVENT:
                existing_rects = [c.rect for c in cloud_group]
                cloud = Cloud(cloud_images, existing_rects=existing_rects)
                cloud_group.add(cloud)
        anim_timer += 1
        if anim_timer >= 20:
            anim_frame = (anim_frame + 1) % 2
            anim_timer = 0
        clock.tick(FPS)

def show_game_over_screen(score):
    while True:
        screen.fill(WHITE)
        cloud_group.update()
        cloud_group.draw(screen)
        font = pygame.font.Font(font_path, 70)
        over_text = font.render("Game Over", True, (200, 0, 0))
        screen.blit(over_text, (SCREEN_WIDTH // 2 - over_text.get_width() // 2, 120))

        score_font = pygame.font.Font(font_path, 50)
        score_text = score_font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 250))

        button_font = pygame.font.Font(font_path, 60)
        button_text = button_font.render("Get Ready", True, BUTTON_COLOR)
        button_rect = button_text.get_rect(center=(SCREEN_WIDTH // 2, int(SCREEN_HEIGHT * 0.7)))
        screen.blit(button_text, button_rect)

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    return
            if event.type == CLOUD_EVENT:
                existing_rects = [c.rect for c in cloud_group]
                cloud = Cloud(cloud_images, existing_rects=existing_rects)
                cloud_group.add(cloud)

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

    obstacle_interval = 1300
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
                obstacle_interval = random.randint(900, 1800)
                pygame.time.set_timer(OBSTACLE_EVENT, obstacle_interval)
            if event.type == SPEEDUP_EVENT:
                obstacle_speed -= 1
                base_score_per_jump += 10
            if event.type == CLOUD_EVENT:
                existing_rects = [c.rect for c in cloud_group]
                cloud = Cloud(cloud_images, existing_rects=existing_rects)
                cloud_group.add(cloud)

        player_group.update()
        obstacle_group.update()
        cloud_group.update()

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
        cloud_group.draw(screen)
        player_group.draw(screen)
        obstacle_group.draw(screen)

        # 점수 표시
        score_font = pygame.font.Font(font_path, 40)
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
