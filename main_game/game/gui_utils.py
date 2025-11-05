import pygame
from pathlib import Path

# --- 1. 경로 설정 ---
BASE_DIR = Path(__file__).resolve().parent
IMAGE_DIR = BASE_DIR / "images"

# --- 2. 상수 정의 (보드 및 패널 크기) ---
# 1. 보드 너비를 750으로 설정 (기준)
BOARD_WIDTH = 750

# 2. 패널 너비를 보드의 절반(2:1 비율)으로 설정 (750 / 2 = 375)
PANEL_WIDTH = 375

# 3. 전체 창 너비 (750 + 375 = 1125)
WINDOW_WIDTH = BOARD_WIDTH + PANEL_WIDTH

# 4. 전체 창 높이는 보드 높이(750)와 맞춤
WINDOW_HEIGHT = 750

# 5. 정사각형 크기는 자동으로 계산됨 (750 // 8 = 93)
SQUARE_SIZE = BOARD_WIDTH // 8

# --- 3. Pygame 폰트 초기화 (가장 먼저 호출) ---
pygame.font.init()
INFO_FONT_TITLE = pygame.font.SysFont("malgungothic", 24, bold=True)
INFO_FONT_HEADER = pygame.font.SysFont("malgungothic", 18, bold=True)
INFO_FONT_BODY = pygame.font.SysFont("malgungothic", 16, bold=True)
COORD_FONT = pygame.font.SysFont("Arial", 14, bold=True)

# --- 3-1. 메인 메뉴용 대형 폰트 ---
MENU_FONT_TITLE = pygame.font.SysFont("malgungothic", 60, bold=True)
MENU_FONT_BUTTON = pygame.font.SysFont("malgungothic", 30, bold=True)

# ⬇️⬇️⬇️ [이 부분 추가됨] ⬇️⬇️⬇️
# --- 3-2. 설정 화면용 폰트 ---
SETTINGS_FONT_TITLE = pygame.font.SysFont("malgungothic", 40, bold=True)
SETTINGS_FONT_LABEL = pygame.font.SysFont("malgungothic", 22, bold=True)
# ⬆️⬆️⬆️ [추가 완료] ⬆️⬆️⬆️


# --- 4. 기물 심볼-한글 이름 매핑 ---
PIECE_NAME_KR = {
    "P": "폰",
    "N": "나이트",
    "B": "비숍",
    "R": "룩",
    "Q": "퀸",
    "K": "킹",
}

# --- 5. 이미지 캐싱 ---
_PIECE_IMAGES = {}


# --- 6. 공통 함수: load_piece_images ---
def load_piece_images(size: int) -> dict:
    """
    기물 이미지 파일을 로드하고 캐시합니다.
    """
    global _PIECE_IMAGES

    if _PIECE_IMAGES:
        return _PIECE_IMAGES

    pieces = ["wP", "wN", "wB", "wR", "wQ", "wK", "bP", "bN", "bB", "bR", "bQ", "bK"]
    images = {}

    print(f"--- 이미지 로드 시도 (경로: {IMAGE_DIR}) ---")
    try:
        for piece in pieces:
            path = IMAGE_DIR / f"{piece}.png"
            images[piece] = pygame.transform.scale(
                pygame.image.load(path), (size, size)
            )
        print("✅ 이미지 로드 성공.")
    except FileNotFoundError as e:
        print(f"❌ 오류: '{e.filename}' 이미지를 찾을 수 없습니다.")
        print(f"'{IMAGE_DIR}' 폴더에 12개의 PNG 이미지가 필요합니다.")
        return None
    except pygame.error as e:
        print(f"❌ Pygame 오류 (이미지 로드): {e}")
        return None

    _PIECE_IMAGES = images
    return _PIECE_IMAGES


# --- 7. 공통 함수: draw_button ---
def draw_button(
    screen: pygame.Surface,
    rect: pygame.Rect,
    text: str,
    font: pygame.font.Font,
    color: pygame.Color,
    hover_color: pygame.Color,
) -> bool:
    """
    클릭 가능한 버튼을 그리고, 마우스 호버 상태를 감지합니다.
    """
    mouse_pos = pygame.mouse.get_pos()
    is_hovered = rect.collidepoint(mouse_pos)
    current_color = hover_color if is_hovered else color

    pygame.draw.rect(screen, current_color, rect, border_radius=5)

    text_surf = font.render(text, True, pygame.Color(255, 255, 255))
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

    return is_hovered


# --- 8. 공통 함수: draw_text_input ---
def draw_text_input(
    screen: pygame.Surface,
    input_text: str,
    rect: pygame.Rect,
    active: bool = False,
    cursor_on: bool = False,
    composition_text: str = "",
):
    """
    텍스트 입력창을 그립니다. (chess_gui.py에서 이동)
    """
    color = pygame.Color(50, 50, 50) if active else pygame.Color(40, 40, 40)
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, pygame.Color(200, 200, 200), rect, 2)

    max_line_width = rect.width - 10
    line_height = (
        INFO_FONT_BODY.get_linesize()
    )  # (INFO_FONT_BODY는 이 파일 상단에 정의됨)

    current_line = ""
    lines = []

    words = input_text.split(" ")
    for word in words:
        test_line = current_line + word + " "
        test_surf = INFO_FONT_BODY.render(test_line, True, pygame.Color(255, 255, 255))

        if test_surf.get_width() > max_line_width:
            lines.append(current_line)
            current_line = word + " "
        else:
            current_line = test_line

    lines.append(current_line)

    cursor_x, cursor_y = rect.x + 5, rect.y + 5

    for i, line in enumerate(lines):
        if i >= 3:
            break

        line_surf = INFO_FONT_BODY.render(
            line.rstrip(), True, pygame.Color(255, 255, 255)
        )
        screen.blit(line_surf, (rect.x + 5, rect.y + 5 + i * line_height))

        if i == len(lines) - 1:
            cursor_x = rect.x + 5 + line_surf.get_width()
            cursor_y = rect.y + 5 + i * line_height

    if composition_text:
        comp_surf = INFO_FONT_BODY.render(
            composition_text, True, pygame.Color(255, 100, 100)
        )
        comp_x = cursor_x
        comp_y = cursor_y

        screen.blit(comp_surf, (comp_x, comp_y))

        cursor_x = comp_x + comp_surf.get_width()

    if active and cursor_on:
        v_margin = line_height // 5

        pygame.draw.line(
            screen,
            pygame.Color(255, 255, 255),
            (cursor_x, cursor_y + v_margin),
            (cursor_x, cursor_y + line_height - v_margin),
            2,
        )
