import pygame
import random
import sys
from tkinter import Tk, filedialog
from PIL import Image

# 초기화
pygame.init()

# 게임 설정
GRID_WIDTH = 10
GRID_HEIGHT = 20
CELL_SIZE = 30
SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE + 200
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE + 100

# 색상 정의
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
COLORS = [
    (0, 255, 255),  # I - 청록색
    (0, 0, 255),    # J - 파란색
    (255, 165, 0),  # L - 주황색
    (255, 255, 0),  # O - 노란색
    (0, 255, 0),    # S - 초록색
    (128, 0, 128),  # T - 보라색
    (255, 0, 0)     # Z - 빨간색
]

# 테트리스 블록 모양 정의
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]],  # L
    [[1, 1], [1, 1]],  # O
    [[0, 1, 1], [1, 1, 0]],  # S
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 1, 0], [0, 1, 1]]   # Z
]

class Tetris:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("■■가 드러나는 테트리스")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.reset_game()
        self.background_image = None
        self.image_surface = None
        self.cover_grid = [[True for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
    def reset_game(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.score = 0
        self.lines_cleared = 0
        self.game_over = False
        self.fall_time = 0
        self.fall_speed = 500
        
    def load_image(self):
        root = Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            title="배경 이미지 선택",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp")]
        )
        root.destroy()
        
        if file_path:
            # PIL로 이미지 열고 크기 조정
            img = Image.open(file_path)
            img = img.resize((GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE), Image.Resampling.LANCZOS)
            
            # Pygame surface로 변환
            img_str = img.tobytes()
            self.background_image = pygame.image.fromstring(img_str, img.size, img.mode)
            self.image_surface = pygame.Surface((GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE))
            self.image_surface.blit(self.background_image, (0, 0))
            
            # 커버 그리드 초기화 (모두 가려진 상태)
            self.cover_grid = [[True for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
            
    def new_piece(self):
        shape = random.choice(SHAPES)
        color = random.choice(COLORS)
        return {
            'shape': shape,
            'color': color,
            'x': GRID_WIDTH // 2 - len(shape[0]) // 2,
            'y': 0,
            'rotation': 0
        }
        
    def rotate_piece(self, piece):
        return [[piece['shape'][y][x] for y in range(len(piece['shape']))] 
                for x in range(len(piece['shape'][0]) - 1, -1, -1)]
        
    def valid_move(self, piece, x, y):
        for row in range(len(piece['shape'])):
            for col in range(len(piece['shape'][row])):
                if piece['shape'][row][col]:
                    new_x = x + col
                    new_y = y + row
                    if (new_x < 0 or new_x >= GRID_WIDTH or 
                        new_y >= GRID_HEIGHT or
                        (new_y >= 0 and self.grid[new_y][new_x])):
                        return False
        return True
        
    def place_piece(self):
        for row in range(len(self.current_piece['shape'])):
            for col in range(len(self.current_piece['shape'][row])):
                if self.current_piece['shape'][row][col]:
                    y = self.current_piece['y'] + row
                    x = self.current_piece['x'] + col
                    if y >= 0:
                        self.grid[y][x] = self.current_piece['color']
                        
    def clear_lines(self):
        lines_to_clear = []
        for row in range(GRID_HEIGHT):
            if all(self.grid[row]):
                lines_to_clear.append(row)
                
        for row in lines_to_clear:
            del self.grid[row]
            self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])
            
            # 이미지 커버 제거 (아래에서 위로)
            if self.background_image:
                cover_row = GRID_HEIGHT - 1 - self.lines_cleared
                if 0 <= cover_row < GRID_HEIGHT:
                    for col in range(GRID_WIDTH):
                        self.cover_grid[cover_row][col] = False
                        
            self.lines_cleared += 1
            
        if lines_to_clear:
            self.score += len(lines_to_clear) * 100
            
    def draw_grid(self):
        # 배경 이미지 그리기 (있는 경우)
        if self.background_image:
            for row in range(GRID_HEIGHT):
                for col in range(GRID_WIDTH):
                    x = col * CELL_SIZE + 50
                    y = row * CELL_SIZE + 50
                    
                    # 커버되지 않은 부분만 이미지 표시
                    if not self.cover_grid[row][col]:
                        img_rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                        self.screen.blit(self.background_image, (x, y), img_rect)
                    else:
                        # 커버된 부분은 어두운 회색으로
                        pygame.draw.rect(self.screen, DARK_GRAY, (x, y, CELL_SIZE, CELL_SIZE))
                        
        # 그리드 선 그리기
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(self.screen, GRAY, 
                           (x * CELL_SIZE + 50, 50), 
                           (x * CELL_SIZE + 50, GRID_HEIGHT * CELL_SIZE + 50))
        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(self.screen, GRAY, 
                           (50, y * CELL_SIZE + 50), 
                           (GRID_WIDTH * CELL_SIZE + 50, y * CELL_SIZE + 50))
            
        # 고정된 블록 그리기
        for row in range(GRID_HEIGHT):
            for col in range(GRID_WIDTH):
                if self.grid[row][col]:
                    x = col * CELL_SIZE + 50
                    y = row * CELL_SIZE + 50
                    pygame.draw.rect(self.screen, self.grid[row][col], 
                                   (x + 1, y + 1, CELL_SIZE - 2, CELL_SIZE - 2))
                    
    def draw_piece(self, piece, offset_x=0, offset_y=0, ghost=False):
        for row in range(len(piece['shape'])):
            for col in range(len(piece['shape'][row])):
                if piece['shape'][row][col]:
                    x = (piece['x'] + col) * CELL_SIZE + 50 + offset_x
                    y = (piece['y'] + row) * CELL_SIZE + 50 + offset_y
                    color = (100, 100, 100) if ghost else piece['color']
                    pygame.draw.rect(self.screen, color, 
                                   (x + 1, y + 1, CELL_SIZE - 2, CELL_SIZE - 2))
                    
    def draw_ghost_piece(self):
        ghost_piece = self.current_piece.copy()
        while self.valid_move(ghost_piece, ghost_piece['x'], ghost_piece['y'] + 1):
            ghost_piece['y'] += 1
        self.draw_piece(ghost_piece, ghost=True)
        
    def draw_ui(self):
        # 점수 표시
        score_text = self.font.render(f"점수: {self.score}", True, WHITE)
        self.screen.blit(score_text, (GRID_WIDTH * CELL_SIZE + 70, 100))
        
        # 지운 줄 수 표시
        lines_text = self.small_font.render(f"지운 줄: {self.lines_cleared}", True, WHITE)
        self.screen.blit(lines_text, (GRID_WIDTH * CELL_SIZE + 70, 150))
        
        # 다음 블록 표시
        next_text = self.small_font.render("다음 블록:", True, WHITE)
        self.screen.blit(next_text, (GRID_WIDTH * CELL_SIZE + 70, 200))
        
        # 다음 블록 그리기
        next_piece_copy = self.next_piece.copy()
        next_piece_copy['x'] = GRID_WIDTH + 3
        next_piece_copy['y'] = 8
        self.draw_piece(next_piece_copy)
        
        # 조작법 표시
        controls = [
            "← → : 이동",
            "↓ : 빠르게 내리기",
            "↑ : 회전",
            "Space : 바로 떨어뜨리기",
            "P : 이미지 선택",
            "R : 재시작"
        ]
        y_offset = 350
        for control in controls:
            control_text = self.small_font.render(control, True, WHITE)
            self.screen.blit(control_text, (GRID_WIDTH * CELL_SIZE + 70, y_offset))
            y_offset += 25
            
    def run(self):
        running = True
        
        while running:
            dt = self.clock.tick(60)
            self.fall_time += dt
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.load_image()
                        
                    if event.key == pygame.K_r:
                        self.reset_game()
                        
                    if not self.game_over:
                        if event.key == pygame.K_LEFT:
                            if self.valid_move(self.current_piece, 
                                             self.current_piece['x'] - 1, 
                                             self.current_piece['y']):
                                self.current_piece['x'] -= 1
                                
                        elif event.key == pygame.K_RIGHT:
                            if self.valid_move(self.current_piece, 
                                             self.current_piece['x'] + 1, 
                                             self.current_piece['y']):
                                self.current_piece['x'] += 1
                                
                        elif event.key == pygame.K_DOWN:
                            if self.valid_move(self.current_piece, 
                                             self.current_piece['x'], 
                                             self.current_piece['y'] + 1):
                                self.current_piece['y'] += 1
                                self.score += 1
                                
                        elif event.key == pygame.K_UP:
                            rotated = self.rotate_piece(self.current_piece)
                            if self.valid_move({'shape': rotated, 'x': self.current_piece['x'], 
                                              'y': self.current_piece['y']}, 
                                             self.current_piece['x'], self.current_piece['y']):
                                self.current_piece['shape'] = rotated
                                
                        elif event.key == pygame.K_SPACE:
                            while self.valid_move(self.current_piece, 
                                                self.current_piece['x'], 
                                                self.current_piece['y'] + 1):
                                self.current_piece['y'] += 1
                                self.score += 2
                                
            # 자동 낙하
            if not self.game_over and self.fall_time >= self.fall_speed:
                if self.valid_move(self.current_piece, 
                                 self.current_piece['x'], 
                                 self.current_piece['y'] + 1):
                    self.current_piece['y'] += 1
                else:
                    self.place_piece()
                    self.clear_lines()
                    self.current_piece = self.next_piece
                    self.next_piece = self.new_piece()
                    
                    if not self.valid_move(self.current_piece, 
                                         self.current_piece['x'], 
                                         self.current_piece['y']):
                        self.game_over = True
                        
                self.fall_time = 0
                
            # 화면 그리기
            self.screen.fill(BLACK)
            self.draw_grid()
            self.draw_ghost_piece()
            self.draw_piece(self.current_piece)
            self.draw_ui()
            
            if self.game_over:
                game_over_text = self.font.render("게임 오버!", True, WHITE)
                text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                self.screen.blit(game_over_text, text_rect)
                
            pygame.display.flip()
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Tetris()
    game.run()