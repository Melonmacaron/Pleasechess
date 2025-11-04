import pygame
import chess
from start_chess import initialize_game 
from pathlib import Path

# --- 1. 상수 정의 (보드 및 패널 크기) ---
BOARD_WIDTH = 800
PANEL_WIDTH = 400
WINDOW_WIDTH = BOARD_WIDTH + PANEL_WIDTH
WINDOW_HEIGHT = 800
SQUARE_SIZE = BOARD_WIDTH // 8

# --- 경로 설정 ---
BASE_DIR = Path(__file__).resolve().parent
IMAGE_DIR = BASE_DIR / "images"

# --- 2. Pygame 폰트 초기화 (패널용 폰트 추가) ---
pygame.font.init()
INFO_FONT_TITLE = pygame.font.SysFont('malgungothic', 24, bold=True)
INFO_FONT_HEADER = pygame.font.SysFont('malgungothic', 18, bold=True)
INFO_FONT_BODY = pygame.font.SysFont('malgungothic', 16, bold=True)
COORD_FONT = pygame.font.SysFont('Arial', 14, bold=True)

# --- 3. 기물 심볼-한글 이름 매핑 ---
PIECE_NAME_KR = {
    "P": "폰", "N": "나이트", "B": "비숍", "R": "룩", "Q": "퀸", "K": "킹",
}

# --- [추가] 이미지 캐싱 ---
_PIECE_IMAGES = {}
# ------------------------

# --- 4. 헬퍼 함수 정의 ---

def load_piece_images(size: int) -> dict:
    """
    기물 이미지 파일을 로드하고 캐시합니다. (수정됨: 캐시 구현)
    """
    global _PIECE_IMAGES

    # [핵심] 이미 로드된 이미지가 있으면 로그 없이 바로 반환
    if _PIECE_IMAGES:
        return _PIECE_IMAGES

    # 2. 로드된 이미지가 없으면 새로 로드하고 상태 출력
    pieces = ['wP', 'wN', 'wB', 'wR', 'wQ', 'wK', 'bP', 'bN', 'bB', 'bR', 'bQ', 'bK']
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
    
    # 3. 로드 완료 후 전역 변수(_PIECE_IMAGES)에 저장 (캐시)
    _PIECE_IMAGES = images
    
    return _PIECE_IMAGES

def draw_board(screen: pygame.Surface, selected_square: str | None = None, legal_moves_uci: list = [], target_square: str | None = None):
    # (코드 로직 동일)
    colors = [pygame.Color("white"), pygame.Color(200, 200, 200)]
    HIGHLIGHT_COLOR = pygame.Color(255, 255, 102, 180) # 기물 선택 (노란색)
    LEGAL_MOVE_COLOR = pygame.Color(100, 255, 100, 180) # 합법적 이동 (초록색)
    TARGET_COLOR = pygame.Color(255, 100, 100, 180) # <--- [추가] 목표 칸 (빨간색)
    TEXT_COLOR = pygame.Color(0, 0, 0)
    files = "abcdefgh"

    for r in range(8):
        for c in range(8):
            color = colors[((r + c) % 2)]
            rect = pygame.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(screen, color, rect)

            chess_rank = 8 - r
            chess_file = files[c]
            square_name = f"{chess_file}{chess_rank}"
            
            # 1. 선택된 기물 칸 하이라이트 (노란색)
            if square_name == selected_square:
                s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                s.fill(HIGHLIGHT_COLOR)
                screen.blit(s, rect)

            # 2. 이동 가능한 칸 하이라이트 (초록색)
            if legal_moves_uci:
                # 합법적 이동 목록에서 목표 칸이 포함되는지 확인
                if any(square_name == move[2:4] for move in legal_moves_uci if len(move) >= 4):
                    s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                    s.fill(LEGAL_MOVE_COLOR)
                    screen.blit(s, rect)
            
            # 3. <--- [추가] 목표 칸 하이라이트 (빨간색)
            # 빨간색 하이라이트는 초록색/노란색 위에 덧칠되어야 하므로 이 위치에 둡니다.
            if square_name == target_square:
                s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                s.fill(TARGET_COLOR)
                screen.blit(s, rect)


    for r in range(8):
        for c in range(8):
            rect = pygame.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            
            if c == 0:
                rank_text = str(8 - r)
                text_surf = COORD_FONT.render(rank_text, True, TEXT_COLOR)
                text_rect = text_surf.get_rect(topleft=(rect.left + 2, rect.top + 2))
                screen.blit(text_surf, text_rect)

            if r == 7:
                file_text = files[c]
                text_surf = COORD_FONT.render(file_text, True, TEXT_COLOR)
                text_rect = text_surf.get_rect(bottomright=(rect.right - 2, rect.bottom - 2))
                screen.blit(text_surf, text_rect)

    for r in range(8):
        for c in range(8):
            rect = pygame.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            
            if c == 0:
                rank_text = str(8 - r)
                text_surf = COORD_FONT.render(rank_text, True, TEXT_COLOR)
                text_rect = text_surf.get_rect(topleft=(rect.left + 2, rect.top + 2))
                screen.blit(text_surf, text_rect)

            if r == 7:
                file_text = files[c]
                text_surf = COORD_FONT.render(file_text, True, TEXT_COLOR)
                text_rect = text_surf.get_rect(bottomright=(rect.right - 2, rect.bottom - 2))
                screen.blit(text_surf, text_rect)

def draw_pieces(screen: pygame.Surface, board: chess.Board, piece_images: dict, white_id_map: dict):
    # (코드 로직 동일)
    if piece_images is None:
        return 

    for r in range(8):
        for c in range(8):
            chess_rank = 7 - r
            chess_file = c
            square_index = chess.square(chess_file, chess_rank)
            
            piece = board.piece_at(square_index)
            
            if piece:
                key = ('w' if piece.color == chess.WHITE else 'b') + piece.symbol().upper()
                rect = pygame.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                screen.blit(piece_images[key], rect)


def get_clicked_square(pos: (int, int)) -> str | None:
    # (코드 로직 동일)
    x, y = pos
    if x >= BOARD_WIDTH:
        return None
    c = x // SQUARE_SIZE
    r = y // SQUARE_SIZE
    
    chess_rank = 7 - r
    chess_file = c
    
    square_name = chess.square_name(chess.square(chess_file, chess_rank))
    return square_name

def draw_text_input(screen: pygame.Surface, input_text: str, rect: pygame.Rect, active: bool = False, cursor_on: bool = False, composition_text: str = ""):
    # (코드 로직 동일)
    color = pygame.Color(50, 50, 50) if active else pygame.Color(40, 40, 40)
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, pygame.Color(200, 200, 200), rect, 2)

    max_line_width = rect.width - 10
    line_height = INFO_FONT_BODY.get_linesize()
    
    current_line = ""
    lines = []
    
    words = input_text.split(' ')
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
        if i >= 3: # 0, 1, 2줄만 표시 (총 3줄)
            break 
            
        line_surf = INFO_FONT_BODY.render(line.rstrip(), True, pygame.Color(255, 255, 255))
        screen.blit(line_surf, (rect.x + 5, rect.y + 5 + i * line_height))
        
        if i == len(lines) - 1:
            cursor_x = rect.x + 5 + line_surf.get_width()
            cursor_y = rect.y + 5 + i * line_height
    
    if composition_text:
        comp_surf = INFO_FONT_BODY.render(composition_text, True, pygame.Color(255, 100, 100))
        comp_x = cursor_x
        comp_y = cursor_y
        
        screen.blit(comp_surf, (comp_x, comp_y))
        
        cursor_x = comp_x + comp_surf.get_width()

    if active and cursor_on:
        v_margin = line_height // 5 
        
        pygame.draw.line(screen, pygame.Color(255, 255, 255), 
                         (cursor_x, cursor_y + v_margin), 
                         (cursor_x, cursor_y + line_height - v_margin), 2)
        
def draw_button(screen: pygame.Surface, rect: pygame.Rect, text: str, font: pygame.font.Font, color: pygame.Color, hover_color: pygame.Color) -> bool:
    # (코드 로직 동일)
    mouse_pos = pygame.mouse.get_pos()
    is_hovered = rect.collidepoint(mouse_pos)
    current_color = hover_color if is_hovered else color
    
    pygame.draw.rect(screen, current_color, rect, border_radius=5)
    
    text_surf = font.render(text, True, pygame.Color(255, 255, 255))
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)
    
    return is_hovered


def draw_info_panel(screen: pygame.Surface, piece_data: dict, selected_piece_id: str | None, current_dialogue: str, dialogue_active: bool, last_response: str, last_piece_dialogue: str, cursor_on: bool):
    # (코드 로직 동일)
    panel_rect = pygame.Rect(BOARD_WIDTH, 0, PANEL_WIDTH, WINDOW_HEIGHT)
    pygame.draw.rect(screen, pygame.Color(30, 30, 30), panel_rect)

    padding = 20
    
    BUTTON_HEIGHT = 40
    INPUT_HEIGHT = 105
    BOTTOM_MARGIN = 20
    ELEMENT_GAP = 15
    
    button_rect = pygame.Rect(
        BOARD_WIDTH + padding, 
        WINDOW_HEIGHT - BOTTOM_MARGIN - BUTTON_HEIGHT, 
        PANEL_WIDTH - 2 * padding, 
        BUTTON_HEIGHT
    )
    
    input_rect = pygame.Rect(
        BOARD_WIDTH + padding, 
        button_rect.top - ELEMENT_GAP - INPUT_HEIGHT,
        PANEL_WIDTH - 2 * padding, 
        INPUT_HEIGHT
    )

    is_king = False
    piece_data_entry = None
    if selected_piece_id:
        piece_data_entry = piece_data.get(selected_piece_id)
        if piece_data_entry and piece_data_entry.get('type') == 'K':
            is_king = True

    if selected_piece_id and not is_king:
        # 입력 레이블
        input_label = INFO_FONT_HEADER.render("설득 대사:", True, pygame.Color(255, 255, 255))
        screen.blit(input_label, (BOARD_WIDTH + padding, input_rect.top - 25))
        
        # 텍스트 입력 칸
        draw_text_input(screen, current_dialogue, input_rect, dialogue_active, cursor_on)
        
        # 버튼
        draw_button(
            screen,
            button_rect,
            "설득하기 (ENTER)",
            INFO_FONT_HEADER,
            pygame.Color(50, 150, 255),
            pygame.Color(80, 180, 255)
        )
    else:
        # 기물이 선택되지 않은 경우, button_rect를 무효화하여 클릭 이벤트를 막습니다.
        button_rect = pygame.Rect(0, 0, 0, 0)
    # ⬆️⬆️⬆️ [수정 완료] ⬆️⬆️⬆️

    y_offset = 30
    
    response_color = pygame.Color(255, 255, 255)
    if "[수락]" in last_response or "[거부]" in last_response or "[오류]" in last_response:
        if "[수락]" in last_response:
            response_color = pygame.Color(100, 255, 100)
        elif "[거부]" in last_response:
            response_color = pygame.Color(255, 100, 100)
        else:
            response_color = pygame.Color(255, 150, 50)
    
    response_display = last_response.split(']')[0] + ']' if ']' in last_response else last_response
    response_surf = INFO_FONT_HEADER.render(response_display, True, response_color)
    screen.blit(response_surf, (BOARD_WIDTH + padding, y_offset))
    y_offset += 40

    if selected_piece_id and (data := piece_data.get(selected_piece_id)):
        
        piece_name = data.get('name', selected_piece_id) 
        piece_type_kr = PIECE_NAME_KR.get(data['type'], data['type']) 
        title_surf = INFO_FONT_TITLE.render(f"{piece_name} ({piece_type_kr})", True, pygame.Color(255, 255, 255))
        screen.blit(title_surf, (BOARD_WIDTH + padding, y_offset))
        y_offset += 50

        rejection_count = data.get('rejection_count_this_turn', 0)
        count_color = pygame.Color(255, 100, 100) if rejection_count > 0 else pygame.Color(150, 255, 150)
        count_surf = INFO_FONT_HEADER.render(f"거절 횟수: {rejection_count}", True, count_color)
        screen.blit(count_surf, (BOARD_WIDTH + padding, y_offset))
        y_offset += 40

        profile_title = INFO_FONT_HEADER.render("페르소나:", True, pygame.Color(200, 200, 200))
        screen.blit(profile_title, (BOARD_WIDTH + padding, y_offset))
        y_offset += 30

        profile_text = data['profile']
        max_text_width = PANEL_WIDTH - (padding * 2) - 10 
        sentences = profile_text.split('. ')
        
        for sentence in sentences:
            if not sentence: continue
            full_sentence = sentence.strip() + "."
            words = full_sentence.split(' ')
            current_line = ""
            for word in words:
                test_line = current_line + word + " "
                test_surf = INFO_FONT_BODY.render(test_line, True, pygame.Color(180, 180, 180))
                if test_surf.get_width() > max_text_width:
                    line_surf = INFO_FONT_BODY.render(current_line, True, pygame.Color(180, 180, 180))
                    screen.blit(line_surf, (BOARD_WIDTH + padding, y_offset))
                    y_offset += 25
                    current_line = word + " "
                else:
                    current_line = test_line
            if current_line.strip():
                line_surf = INFO_FONT_BODY.render(current_line.strip(), True, pygame.Color(180, 180, 180))
                screen.blit(line_surf, (BOARD_WIDTH + padding, y_offset))
                y_offset += 25
        
        y_offset += 20
        dialogue_surf = INFO_FONT_HEADER.render(f"기물 응답:", True, pygame.Color(200, 200, 255))
        screen.blit(dialogue_surf, (BOARD_WIDTH + padding, y_offset))
        y_offset += 30
        assistant_dialogue = next(
            (item['content'] for item in reversed(data['history']) if item['role'] == 'assistant'),
            "아직 기물의 응답이 없습니다."
        )

        # 대사에서 [수락] 또는 [거부] 태그를 제거하고 본문만 추출
        dialogue_text_body = assistant_dialogue.split(']', 1)[1].strip() if '[' in assistant_dialogue and ']' in assistant_dialogue else assistant_dialogue
        
        dialogue_words = dialogue_text_body.split(' ')
        current_dialogue_line = ""
        
        # 프로필 텍스트와 동일한 최대 너비 재사용
        max_dialogue_width = PANEL_WIDTH - (padding * 2) - 10 
        line_height = INFO_FONT_BODY.get_linesize()
        
        for word in dialogue_words:
            # 다음 단어를 추가한 테스트 라인 생성
            test_line = current_dialogue_line + word + " "
            test_surf = INFO_FONT_BODY.render(test_line, True, pygame.Color(255, 255, 255))
            
            # 너비가 초과되면 현재 라인을 출력하고 다음 단어부터 새 라인 시작
            if test_surf.get_width() > max_dialogue_width:
                if current_dialogue_line.strip():
                    line_surf = INFO_FONT_BODY.render(current_dialogue_line.strip(), True, pygame.Color(255, 255, 255))
                    screen.blit(line_surf, (BOARD_WIDTH + padding + 10, y_offset))
                    y_offset += line_height 
                current_dialogue_line = word + " "
            else:
                # 너비 초과 안 되면 계속 추가
                current_dialogue_line = test_line
        
        # 마지막 남은 라인 출력
        if current_dialogue_line.strip():
            line_surf = INFO_FONT_BODY.render(current_dialogue_line.strip(), True, pygame.Color(255, 255, 255))
            screen.blit(line_surf, (BOARD_WIDTH + padding + 10, y_offset))
            # ⬆️⬆️⬆️ [수정 완료] ⬆️⬆️⬆️

    else:
        text = INFO_FONT_HEADER.render("백색 기물을 클릭하세요.", True, pygame.Color(150, 150, 150))
        text_rect = text.get_rect(center=(BOARD_WIDTH + PANEL_WIDTH // 2, y_offset))
        screen.blit(text, text_rect)
        
    return button_rect


# chess_gui.py (draw_current_state 함수 정의)

def draw_current_state(screen, game_board, game_white_ids, game_piece_data, last_response, last_piece_dialogue, selected_piece_id_to_show: str | None):
    """
    현재 보드와 정보 패널을 그리는 단일 함수 (흑 턴 시 사용).
    (수정됨: 이전에 선택된 기물 ID를 인자로 받아 정보 패널에 표시합니다.)
    """
    # 흑 턴 시에는 키 입력 및 커서 비활성화
    dialogue_text = ""
    dialogue_active = False
    cursor_on = False

    king_square_name = None
    if game_board.is_checkmate():
        # 체크메이트 당한 킹의 색상 확인 (현재 턴이 진 쪽)
        king_color = game_board.turn
        king_sq_index = game_board.king(king_color)
        if king_sq_index is not None:
            king_square_name = chess.square_name(king_sq_index)

    # 1. 그리기
    screen.fill(pygame.Color(0, 0, 0))
    draw_board(screen) # 하이라이트 없이 보드만 그립니다.
    draw_pieces(screen, game_board, load_piece_images(SQUARE_SIZE), game_white_ids)
    
    # 2. 정보 패널 그리기 (메시지 및 기물 ID 유지)
    draw_info_panel(
        screen, 
        game_piece_data, 
        selected_piece_id_to_show, # <--- 인자로 받은 ID를 전달
        dialogue_text, 
        dialogue_active, 
        last_response, 
        last_piece_dialogue, 
        cursor_on
    )
    
    pygame.display.flip()

# run_game_gui 함수 (수정된 전체 코드)
def run_game_gui(game_board, game_white_ids, game_piece_data, sf_engine, turn_callback, screen, clock):
    """
    메인 게임 루프를 실행하고 사용자 입력을 처리하며, 상태를 함수 속성에 저장/복원하여 유지합니다.
    (수정됨: King 이동 시 설득 단계를 건너뛰고 즉시 이동을 시도합니다.)
    """
    # [제거] pygame.init()
    screen = screen # main.py에서 전달받음
    clock = clock   # main.py에서 전달받음
    
    pygame.display.set_caption("자아를 가진 체스")
    pygame.key.start_text_input()
    
    piece_images = load_piece_images(SQUARE_SIZE)
    if piece_images is None:
        return "QUIT" 

    # --- 상태 변수 초기화 및 로드 (함수 속성 사용으로 상태 유지) ---
    # 첫 호출이 아니라면 이전 상태를 유지합니다.
    if not hasattr(run_game_gui, 'prev_last_response'):
        run_game_gui.prev_last_response = "[INFO] 게임 시작. 백 턴."
        run_game_gui.prev_last_piece_dialogue = "아직 응답이 없습니다."
        run_game_gui.prev_selected_square_name = None
        run_game_gui.prev_selected_piece_id = None # <-- 실제 선택된 기물 ID
        run_game_gui.prev_selected_piece_id_to_show = None # <-- [추가] 화면 표시용 기물 ID

    running = True
    game_state = 0
    
    # 이전 상태 로드 (기물 ID와 응답 대사 복원)
    selected_square_name = run_game_gui.prev_selected_square_name 
    selected_piece_id = run_game_gui.prev_selected_piece_id 
    selected_piece_id_to_show = run_game_gui.prev_selected_piece_id_to_show # <-- [핵심] 화면 표시 ID 복원
    
    target_square_name = None
    uci_move_to_try = None
    legal_moves_uci = [] 
    
    location_to_id = {v: k for k, v in game_white_ids.items() if v is not None}
    
    dialogue_text = ""
    dialogue_active = False
    last_response = run_game_gui.prev_last_response
    last_piece_dialogue = run_game_gui.prev_last_piece_dialogue 

    # --- 커서 깜빡임 관련 변수 ---
    cursor_timer = 0
    cursor_on = True
    CURSOR_BLINK_RATE = 500

    # --- 헬퍼 함수: 상태 초기화 (수정됨) ---
    def reset_move_state(full_reset=False):
        nonlocal game_state, selected_square_name, selected_piece_id, target_square_name, uci_move_to_try, legal_moves_uci, dialogue_active, last_response, last_piece_dialogue, selected_piece_id_to_show
        
        game_state = 0 
        target_square_name = None
        uci_move_to_try = None
        legal_moves_uci = []
        dialogue_active = False
        
        if full_reset:
            # Full Reset 시 모든 선택 해제 및 저장
            selected_square_name = None
            selected_piece_id = None
            selected_piece_id_to_show = None # <-- 화면 표시 ID 초기화
            
            run_game_gui.prev_selected_square_name = None
            run_game_gui.prev_selected_piece_id = None
            run_game_gui.prev_selected_piece_id_to_show = None # <-- 저장
            run_game_gui.prev_last_response = "[INFO] 백 턴. 기물을 선택하세요."
            run_game_gui.prev_last_piece_dialogue = "아직 응답이 없습니다."
            
            return run_game_gui.prev_last_response
        
        # 거부/성공 후 상태 저장 (기물 선택만 None으로 리셋, 화면 표시 ID 유지)
        selected_piece_id = None # <-- [핵심] 실제 선택 ID만 None으로 리셋
        selected_square_name = None
        
        run_game_gui.prev_last_response = last_response
        run_game_gui.prev_last_piece_dialogue = last_piece_dialogue
        run_game_gui.prev_selected_square_name = selected_square_name
        run_game_gui.prev_selected_piece_id = selected_piece_id # None 저장
        run_game_gui.prev_selected_piece_id_to_show = selected_piece_id_to_show # <-- [핵심] 화면 표시 ID 유지 저장

        return last_response
        
    
    # --- 설득 시도 헬퍼 함수 (수정됨) ---
    def attempt_persuasion(is_king_move=False):
        nonlocal last_response, last_piece_dialogue, dialogue_text, dialogue_active, selected_piece_id_to_show
        
        # 킹 이동이 아니면서 대기 상태가 아니거나 대사가 없으면 오류
        if not is_king_move and (game_state != 2 or not dialogue_text.strip()):
            last_response = "[ERROR] 이동 목표 선택 및 대사 입력이 필요합니다."
            return None
        
        # 킹 이동인 경우 대사는 비워둡니다.
        persuasion_input = "" if is_king_move else dialogue_text
            
        last_response = "[WAIT] 기물 설득 중..." if not is_king_move else "[WAIT] 킹의 명령 처리 중..."
        pygame.display.flip() 

        # turn_callback(uci_move_to_try, dialogue_text) 호출
        decision, dialogue = turn_callback(uci_move_to_try, persuasion_input)
        
        last_piece_dialogue = dialogue
        dialogue_text = ""
        dialogue_active = True
        
        # 킹 이동 시 응답 메시지 정의
        if is_king_move and decision == True:
            last_response = "[수락] 킹의 명령이 즉시 수행되었습니다."
        elif is_king_move and decision == False:
            last_response = "[오류] 킹의 이동이 유효하지 않습니다."
        elif is_king_move and decision == "오류":
            last_response = f"[오류] 킹의 명령 처리 중 오류: {dialogue}"
        else:
            last_response = f"[{decision}] {dialogue}" if decision in ["수락", "거부", "오류"] else last_response
        
        
        if decision == "수락" or decision == True:
            # 성공 시: selected_piece_id는 None, selected_piece_id_to_show는 유지.
            reset_move_state(full_reset=False) 

            return "WHITE_MOVED" 
        
        elif decision == "거부" or decision == "오류" or decision == False: # False는 킹 이동의 경우 오류로 간주
            # 거부/오류 시 상태 저장 (재설득을 위해 기물 선택 유지)
            run_game_gui.prev_last_response = last_response
            run_game_gui.prev_last_piece_dialogue = last_piece_dialogue
            run_game_gui.prev_selected_square_name = selected_square_name
            run_game_gui.prev_selected_piece_id = selected_piece_id
            run_game_gui.prev_selected_piece_id_to_show = selected_piece_id_to_show
                
            return None
    
    
    # --- [수정] 흑 턴 완료 후 재진입 시 상태 복원 로직 ---
    if selected_square_name:
        start_sq_idx = chess.parse_square(selected_square_name)
        piece_at_sq = game_board.piece_at(start_sq_idx)
        
        if piece_at_sq and piece_at_sq.color == chess.WHITE:
            legal_moves_uci = [move.uci() for move in game_board.legal_moves if move.from_square == start_sq_idx]
            game_state = 1 # 기물 선택 상태 복원
        else:
            # 기물이 사라진 경우 (흑에게 잡혔거나 이동됨) 선택 해제 (Full Reset)
            last_response = reset_move_state(full_reset=True)

    # 흑 턴 완료 후 재진입 시 selected_piece_id가 None이면 
    # selected_piece_id_to_show는 이전 값을 계속 사용합니다.
    # --- [수정 완료] ---


    while running:
        # --- (생략: 커서 업데이트 로직) ---
        cursor_timer += clock.get_time()
        if cursor_timer > CURSOR_BLINK_RATE:
            cursor_on = not cursor_on
            cursor_timer = 0
        
        location_to_id = {v: k for k, v in game_white_ids.items() if v is not None}
        
        # 흑 턴이면 GUI를 빠져나가 main.py에게 처리를 요청합니다.
        if game_board.turn == chess.BLACK:
            # GUI 종료 전 현재 상태를 저장
            run_game_gui.prev_selected_square_name = selected_square_name
            run_game_gui.prev_selected_piece_id = selected_piece_id
            run_game_gui.prev_selected_piece_id_to_show = selected_piece_id_to_show # <-- 화면 표시 ID 저장
            run_game_gui.prev_last_response = last_response
            run_game_gui.prev_last_piece_dialogue = last_piece_dialogue
            return "BLACK_TURN" 
        
        
        # --- 1. 이벤트 처리 ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return "QUIT"
            
            if event.type == pygame.TEXTINPUT and dialogue_active:
                dialogue_text += event.text
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE and dialogue_active:
                    dialogue_text = dialogue_text[:-1]
                
                # Enter 키로 설득 시도 (game_state == 2 일 때만)
                if event.key == pygame.K_RETURN and game_state == 2:
                    result = attempt_persuasion()
                    if result:
                        return result
                    
                if event.key == pygame.K_ESCAPE:
                    last_response = reset_move_state(full_reset=True)
                    dialogue_text = ""
                    last_response = "[INFO] 선택이 취소되었습니다. 새로운 기물을 선택하세요."
            
            # B. [보드 클릭] 로직 내부의 상태 갱신 시에도 ID를 저장하도록 수정
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                clicked_square = get_clicked_square(pos)
                
                # 버튼 영역 체크 (생략)
                button_rect = pygame.Rect(BOARD_WIDTH + 20, WINDOW_HEIGHT - 60, PANEL_WIDTH - 40, 40)
                if button_rect.collidepoint(pos) and game_state == 2:
                    result = attempt_persuasion()
                    if result:
                        return result

                elif clicked_square:
                    clicked_piece_id = location_to_id.get(clicked_square)
                    clicked_piece = game_board.piece_at(chess.parse_square(clicked_square))
                    is_ally_piece = clicked_piece_id and clicked_piece and clicked_piece.color == chess.WHITE
                    
                    
                    # 1. 상태 0 (기물 선택 전): 1차 클릭
                    if game_state == 0 and is_ally_piece:
                        selected_square_name = clicked_square
                        selected_piece_id = clicked_piece_id 
                        selected_piece_id_to_show = clicked_piece_id # <-- [핵심] 화면 표시 ID 갱신
                        
                        start_sq_idx = chess.parse_square(selected_square_name)
                        legal_moves_uci = [move.uci() for move in game_board.legal_moves if move.from_square == start_sq_idx]
                        
                        game_state = 1
                        dialogue_active = False
                        # 기물 이름이 있으면 사용, 없으면 ID 사용
                        piece_name = game_piece_data.get(clicked_piece_id, {}).get('name', clicked_piece_id)
                        last_response = f"[INFO] {piece_name} 선택됨. 목표 칸을 클릭하세요."

                    # 2. 상태 1 (기물 선택됨): 2차 클릭 (이동 또는 선택 변경)
                    elif game_state == 1:
                        if clicked_square == selected_square_name or is_ally_piece:
                            # 2-1. 같은 칸 재클릭 또는 다른 아군 기물 선택 -> 선택 리셋 후 새 기물 선택
                            if is_ally_piece and clicked_square != selected_square_name:
                                last_response = reset_move_state(full_reset=False) # 기존 선택 해제 (selected_piece_id = None)
                                
                                selected_square_name = clicked_square
                                selected_piece_id = clicked_piece_id 
                                selected_piece_id_to_show = clicked_piece_id # <-- [핵심] 새 기물 선택 시 화면 표시 ID 갱신
                                start_sq_idx = chess.parse_square(selected_square_name)
                                legal_moves_uci = [move.uci() for move in game_board.legal_moves if move.from_square == start_sq_idx]
                                game_state = 1
                                piece_name = game_piece_data.get(clicked_piece_id, {}).get('name', clicked_piece_id)
                                last_response = f"[INFO] {piece_name} 선택됨. 목표 칸을 클릭하세요."
                            else:
                                # 같은 칸 재클릭 -> 선택 해제 (Full Reset)
                                last_response = reset_move_state(full_reset=True) # <-- [핵심] 화면 표시 ID도 None
                                dialogue_text = ""
                                
                        else:
                            # 2-2. 다른 칸 클릭 -> 이동 유효성 검사 및 설득 대기 상태로 진입 (또는 킹 이동)
                            target_square_name = clicked_square
                            
                            move_str = selected_square_name + target_square_name
                            
                            # 승진 처리 (임시)
                            piece_to_move = game_board.piece_at(chess.parse_square(selected_square_name))
                            uci_move_to_try = move_str
                            if piece_to_move and piece_to_move.piece_type == chess.PAWN and chess.parse_square(target_square_name) in [chess.A8, chess.H8, chess.B8, chess.C8, chess.D8, chess.E8, chess.F8, chess.G8]:
                                uci_move_to_try = move_str + 'q'
                            
                            # [핵심] 유효성 최종 확인
                            if uci_move_to_try in legal_moves_uci or (uci_move_to_try[:4] + 'q') in legal_moves_uci:
                                
                                # ⬇️⬇️⬇️ [새로운 로직] 킹(K) 이동 체크 ⬇️⬇️⬇️
                                is_king = piece_to_move.symbol().upper() == 'K'
                                
                                if is_king:
                                    # 킹의 이동은 설득 없이 즉시 시도합니다.
                                    result = attempt_persuasion(is_king_move=True)
                                    if result:
                                        return result
                                    # 결과가 None (거부/오류)인 경우 상태 유지 (selected_piece_id 유지)
                                    
                                else:
                                    # 킹이 아닌 경우, 설득 대기 상태로 진입합니다.
                                    game_state = 2 # 설득 대기 상태 진입
                                    dialogue_active = True # 키 입력 활성화
                                    last_response = f"[WAIT] '{uci_move_to_try}' 이동 확인. 대사를 입력 후 설득하세요."
                                    legal_moves_uci = [] # 초록색 하이라이트 제거
                                
                            else:
                                # 유효하지 않은 이동
                                last_response = f"[ERROR] '{uci_move_to_try[:4]}'는 합법적인 이동이 아닙니다."
                                game_state = 1 # 선택 상태 유지
                                target_square_name = None 
                                uci_move_to_try = None 

                    # 3. 상태 2 (설득 대기): 선택 변경은 금지
                    elif game_state == 2:
                        last_response = f"[WAIT] 현재 '{uci_move_to_try[:4]}' 설득 중입니다. [설득하기] 버튼을 누르거나 Enter를 치세요."

        
        # --- 2. 그리기 ---
        screen.fill(pygame.Color(0, 0, 0))
        # [수정] target_square_name 인자를 draw_board에 전달
        draw_board(screen, selected_square_name, legal_moves_uci, target_square_name) 
        draw_pieces(screen, game_board, piece_images, game_white_ids)
        
        # draw_info_panel 호출 (화면 표시 ID 전달)
        draw_info_panel(
            screen, 
            game_piece_data, 
            selected_piece_id_to_show, # <-- [핵심] 이 변수를 사용하여 정보를 표시합니다.
            dialogue_text, 
            dialogue_active, 
            last_response, 
            last_piece_dialogue,
            cursor_on
        )
        
        # 3. 화면 업데이트
        pygame.display.flip()
        clock.tick(60) 
        
    return "QUIT"