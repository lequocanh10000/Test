import pygame
import cv2
import time
from pygame import mixer

pygame.init()
mixer.init()

# Kích thước màn hình
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Rhythm Game")

# Clock để giới hạn FPS
clock = pygame.time.Clock()

# Font để hiển thị điểm
font = pygame.font.Font(None, 36)

# Lớp Key
class Key():
    def __init__(self, x, y, color1, color2, key):
        self.x = x
        self.y = y
        self.color1 = color1
        self.color2 = color2
        self.key = key
        self.rect = pygame.Rect(self.x, self.y, 100, 40)
        self.handled = False

# Tạo các phím nhấn
keys = [
    Key(100, 500, (255, 0, 0), (220, 0, 0), pygame.K_a),
    Key(200, 500, (0, 255, 0), (0, 220, 0), pygame.K_s),
    Key(300, 500, (0, 0, 255), (0, 0, 220), pygame.K_d),
    Key(400, 500, (255, 255, 0), (220, 220, 0), pygame.K_f),
]

# Hàm load video nền
def play_background_video(video_path):
    video = cv2.VideoCapture(video_path)
    ret, frame = video.read()
    if not ret:
        print("Không thể load video nền.")
        return None
    return video

# Hàm load file nốt
def load_notes(map_file):
    rects = []
    mixer.music.load(map_file + ".mp3")
    mixer.music.play()
    with open(map_file + ".txt", 'r') as f:
        data = f.readlines()
    for y, line in enumerate(data):
        for x, char in enumerate(line.strip()):
            if char == '0':
                rects.append(pygame.Rect(keys[x].rect.centerx - 25, y * -100, 50, 25))
    return rects

# Khởi tạo video và nốt
video = play_background_video("ReEndOfADream.mp4")
map_rects = load_notes("ReEndOfADream")

fps = video.get(cv2.CAP_PROP_FPS)
print(fps)
frame_duration = 1 / fps  # Thời gian mỗi khung hình

start_time = time.time() 

# Điểm số và trạng thái game
score = 0
running = True

while running:
    # Xử lý sự kiện
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Phát frame từ video nền
    if video:
        ret, frame = video.read()
        if not ret:
            video.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Lặp lại video
            ret, frame = video.read()
        
        elapsed_time = time.time() - start_time
        expected_frame = int(elapsed_time * fps)  # Khung hình mong muốn
        current_frame = int(video.get(cv2.CAP_PROP_POS_FRAMES))
        
        if current_frame < expected_frame:
            continue
        
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        frame = cv2.flip(frame, 0)
        
        frame_surface = pygame.surfarray.make_surface(frame)
        frame_surface = pygame.transform.scale(frame_surface, (screen_width, screen_height))
        screen.blit(frame_surface, (0, 0))
    else:
        screen.fill((0, 0, 0))

    # Vẽ và xử lý các phím nhấn
    keys_pressed = pygame.key.get_pressed()
    for key in keys:
        color = key.color1 if keys_pressed[key.key] else key.color2
        pygame.draw.rect(screen, color, key.rect)
        key.handled = not keys_pressed[key.key]

    # Vẽ và xử lý các nốt
    for rect in map_rects[:]:
        pygame.draw.rect(screen, (200, 0, 0), rect)
        rect.y += 5  # Di chuyển nốt xuống

        # Xử lý va chạm với phím
        for key in keys:
            if key.rect.colliderect(rect) and not key.handled:
                map_rects.remove(rect)
                score += 100  # Tăng điểm nếu nhấn đúng
                break
        else:
            if rect.y > screen_height:  # Nốt rơi khỏi màn hình
                map_rects.remove(rect)
                score -= 50  # Trừ điểm khi bỏ lỡ

    # Hiển thị điểm số
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    # Kết thúc game khi bài hát dừng
    if not map_rects and not mixer.music.get_busy():
        running = False
        print(f"Game Over! Final Score: {score}")

    pygame.display.update()
    clock.tick(60)  # Giới hạn FPS

# Giải phóng tài nguyên
if video:
    video.release()
pygame.quit()
pygame.quit()

