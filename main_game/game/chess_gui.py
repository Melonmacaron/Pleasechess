import pygame
import chess

# ⬇️⬇️⬇️ [수정됨] ⬇️⬇️⬇️
# 모든 공통 상수/함수를 gui_utils에서 import 하도록 변경
# (draw_text_input이 목록에 추가됨)
from gui_utils import (
    BOARD_WIDTH,
    PANEL_WIDTH,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    SQUARE_SIZE,
    INFO_FONT_TITLE,
    INFO_FONT_HEADER,
    INFO_FONT_BODY,
    COORD_FONT,
    PIECE_NAME_KR,
    load_piece_images,
    draw_button,
    draw_text_input,  # <--- [추가됨]
)

# ⬆️⬆️⬆️ [수정 완료] ⬆️⬆️⬆️

from start_chess import initialize_game  # (main.py에서 사용, 여기선 직접 사용 안함)

# --- 4. 헬퍼 함수 정의 ---
# [삭제됨] load_piece_images (gui_utils로 이동)
# [삭제됨] draw_text_input (gui_utils로 이동)
# [삭제됨] draw_button (gui_utils로 이동)


def draw_board(
    screen: pygame.Surface,
    selected_square: str | None = None,
    legal_moves_uci: list = [],
    target_square: str | None = None,
):
    # (코드 로직 동일)
    colors = [pygame.Color("white"), pygame.Color(200, 200, 200)]
    HIGHLIGHT_COLOR = pygame.Color(255, 255, 102, 180)  # 기물 선택 (노란색)
    LEGAL_MOVE_COLOR = pygame.Color(100, 255, 100, 180)  # 합법적 이동 (초록색)
    TARGET_COLOR = pygame.Color(255, 100, 100, 180)  # <--- [추가] 목표 칸 (빨간색)
    TEXT_COLOR = pygame.Color(0, 0, 0)
    files = "abcdefgh"

    for r in range(8):
        for c in range(8):
            color = colors[((r + c) % 2)]
            rect = pygame.Rect(
                c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE
            )
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
                if any(
                    square_name == move[2:4]
                    for move in legal_moves_uci
                    if len(move) >= 4
                ):
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
            rect = pygame.Rect(
                c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE
            )

            if c == 0:
                rank_text = str(8 - r)
                text_surf = COORD_FONT.render(rank_text, True, TEXT_COLOR)
                text_rect = text_surf.get_rect(topleft=(rect.left + 2, rect.top + 2))
                screen.blit(text_surf, text_rect)

            if r == 7:
                file_text = files[c]
                text_surf = COORD_FONT.render(file_text, True, TEXT_COLOR)
                text_rect = text_surf.get_rect(
                    bottomright=(rect.right - 2, rect.bottom - 2)
                )
                screen.blit(text_surf, text_rect)

    for r in range(8):
        for c in range(8):
            rect = pygame.Rect(
                c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE
            )

            if c == 0:
                rank_text = str(8 - r)
                text_surf = COORD_FONT.render(rank_text, True, TEXT_COLOR)
                text_rect = text_surf.get_rect(topleft=(rect.left + 2, rect.top + 2))
                screen.blit(text_surf, text_rect)

            if r == 7:
                file_text = files[c]
                text_surf = COORD_FONT.render(file_text, True, TEXT_COLOR)
                text_rect = text_surf.get_rect(
                    bottomright=(rect.right - 2, rect.bottom - 2)
                )
                screen.blit(text_surf, text_rect)


def draw_pieces(
    screen: pygame.Surface, board: chess.Board, piece_images: dict, white_id_map: dict
):
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
                key = (
                    "w" if piece.color == chess.WHITE else "b"
                ) + piece.symbol().upper()
                rect = pygame.Rect(
                    c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE
                )
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


# [삭제됨] draw_text_input 함수 (gui_utils로 이동)


# [draw_info_panel 함수의 전체 코드]


def draw_info_panel(
    screen: pygame.Surface,
    piece_data: dict,
    selected_piece_id: str | None,
    current_dialogue: str,
    dialogue_active: bool,
    last_response: str,
    last_piece_dialogue: str,
    cursor_on: bool,
    force_move_count: int,
) -> (pygame.Rect, pygame.Rect):
    """
    정보 패널을 그립니다.
    (수정됨: 킹(King)을 선택한 경우, 페르소나와 기물 응답 섹션을 숨깁니다.)
    (수정됨: 상단 응답 메시지(last_response)가 길어지면 자동 줄 바꿈 처리합니다.)
    """
    panel_rect = pygame.Rect(BOARD_WIDTH, 0, PANEL_WIDTH, WINDOW_HEIGHT)
    pygame.draw.rect(screen, pygame.Color(30, 30, 30), panel_rect)

    padding = 20

    # --- 버튼 레이아웃 정의 ---
    BUTTON_HEIGHT = 40
    INPUT_HEIGHT = 105
    BOTTOM_MARGIN = 20
    ELEMENT_GAP = 15

    button_rect = pygame.Rect(
        BOARD_WIDTH + padding,
        WINDOW_HEIGHT - BOTTOM_MARGIN - BUTTON_HEIGHT,
        PANEL_WIDTH - 2 * padding,
        BUTTON_HEIGHT,
    )
    force_move_button_rect = pygame.Rect(
        button_rect.x,
        button_rect.y - ELEMENT_GAP - BUTTON_HEIGHT,
        button_rect.width,
        BUTTON_HEIGHT,
    )
    input_rect = pygame.Rect(
        button_rect.x,
        force_move_button_rect.y - ELEMENT_GAP - INPUT_HEIGHT,
        button_rect.width,
        INPUT_HEIGHT,
    )
    # --- 레이아웃 정의 끝 ---

    is_king = False
    piece_data_entry = None
    if selected_piece_id:
        piece_data_entry = piece_data.get(selected_piece_id)
        if piece_data_entry and piece_data_entry.get("type") == "K":
            is_king = True

    # --- '설득하기' 및 '강제 이동' 버튼 그리기 ---
    if selected_piece_id and not is_king:
        input_label = INFO_FONT_HEADER.render(
            "설득 대사", True, pygame.Color(255, 255, 255)
        )
        screen.blit(input_label, (BOARD_WIDTH + padding, input_rect.top - 25))

        draw_text_input(
            screen, current_dialogue, input_rect, dialogue_active, cursor_on
        )

        draw_button(
            screen,
            button_rect,
            "설득하기 (ENTER)",
            INFO_FONT_HEADER,
            pygame.Color(50, 150, 255),
            pygame.Color(80, 180, 255),
        )

        if force_move_count > 0:
            draw_button(
                screen,
                force_move_button_rect,
                f"강제 이동 ({force_move_count}회 남음)",
                INFO_FONT_HEADER,
                pygame.Color(220, 50, 50),
                pygame.Color(250, 80, 80),
            )
        else:
            draw_button(
                screen,
                force_move_button_rect,
                "강제 이동 (0회)",
                INFO_FONT_HEADER,
                pygame.Color(100, 100, 100),
                pygame.Color(100, 100, 100),
            )
    else:
        button_rect = pygame.Rect(0, 0, 0, 0)
        force_move_button_rect = pygame.Rect(0, 0, 0, 0)
    # --- 버튼 그리기 끝 ---

    y_offset = 30

    # ⬇️⬇️⬇️ [수정됨] ⬇️⬇️⬇️
    # --- 응답 상태 표시 (줄 바꿈 적용) ---
    response_color = pygame.Color(255, 255, 255)
    if (
        "[수락]" in last_response
        or "[거부]" in last_response
        or "[오류]" in last_response
    ):
        if "[수락]" in last_response:
            response_color = pygame.Color(100, 255, 100)
        elif "[거부]" in last_response:
            response_color = pygame.Color(255, 100, 100)
        else:
            response_color = pygame.Color(255, 150, 50)

    # 1. 폰트를 INFO_FONT_BODY로 변경 (글자 크기 줄이기)
    font_to_use = INFO_FONT_BODY
    line_height = font_to_use.get_linesize()

    # 2. 텍스트 래핑(Wrapping) 로직 추가 (자동 줄 바꿈)
    words = last_response.split(" ")
    current_line = ""
    max_line_width = PANEL_WIDTH - (padding * 2)

    for word in words:
        test_line = current_line + word + " "
        test_surf = font_to_use.render(test_line, True, response_color)

        if test_surf.get_width() > max_line_width:
            line_surf = font_to_use.render(current_line.strip(), True, response_color)
            screen.blit(line_surf, (BOARD_WIDTH + padding, y_offset))
            y_offset += line_height
            current_line = word + " "
        else:
            current_line = test_line

    # 마지막 남은 라인 그리기
    if current_line.strip():
        line_surf = font_to_use.render(current_line.strip(), True, response_color)
        screen.blit(line_surf, (BOARD_WIDTH + padding, y_offset))
        y_offset += line_height

    y_offset += 20  # 간격 조절
    # --- 응답 상태 끝 ---
    # ⬆️⬆️⬆️ [수정 완료] ⬆️⬆️⬆️

    if selected_piece_id and (data := piece_data.get(selected_piece_id)):
        # --- 1. 공통 정보 (이름, 횟수 등) ---
        piece_name = data.get("name", selected_piece_id)
        piece_type_kr = PIECE_NAME_KR.get(data["type"], data["type"])
        title_surf = INFO_FONT_TITLE.render(
            f"{piece_name} ({piece_type_kr})", True, pygame.Color(255, 255, 255)
        )
        screen.blit(title_surf, (BOARD_WIDTH + padding, y_offset))
        y_offset += 50

        force_color = (
            pygame.Color(150, 255, 150)
            if force_move_count > 0
            else pygame.Color(255, 100, 100)
        )

        rejection_count = data.get("rejection_count_this_turn", 0)
        count_color = (
            pygame.Color(255, 100, 100)
            if rejection_count > 0
            else pygame.Color(150, 255, 150)
        )
        count_surf = INFO_FONT_HEADER.render(
            f"거절 횟수 : {rejection_count}", True, count_color
        )
        screen.blit(count_surf, (WINDOW_WIDTH - padding * 7, y_offset))
        # --- 공통 정보 끝 ---

        # --- 2. 페르소나 및 기물 응답 (킹이 아닐 때만 표시) ---
        if not is_king:  # (이전 단계에서 수정한 부분)
            # --- 페르소나 섹션 ---
            profile_title = INFO_FONT_HEADER.render(
                "페르소나", True, pygame.Color(200, 200, 200)
            )
            screen.blit(profile_title, (BOARD_WIDTH + padding, y_offset))
            y_offset += 30

            profile_text = data["profile"]
            max_text_width = PANEL_WIDTH - (padding * 2) - 10
            sentences = profile_text.split(". ")

            for sentence in sentences:
                if not sentence:
                    continue
                full_sentence = sentence.strip() + "."
                words = full_sentence.split(" ")
                current_line = ""
                for word in words:
                    test_line = current_line + word + " "
                    test_surf = INFO_FONT_BODY.render(
                        test_line, True, pygame.Color(180, 180, 180)
                    )
                    if test_surf.get_width() > max_text_width:
                        line_surf = INFO_FONT_BODY.render(
                            current_line, True, pygame.Color(180, 180, 180)
                        )
                        screen.blit(line_surf, (BOARD_WIDTH + padding, y_offset))
                        y_offset += 25
                        current_line = word + " "
                    else:
                        current_line = test_line
                if current_line.strip():
                    line_surf = INFO_FONT_BODY.render(
                        current_line.strip(), True, pygame.Color(180, 180, 180)
                    )
                    screen.blit(line_surf, (BOARD_WIDTH + padding, y_offset))
                    y_offset += 25

            # --- 기물 응답 섹션 ---
            y_offset += 20
            dialogue_surf = INFO_FONT_HEADER.render(
                f"기물 응답", True, pygame.Color(200, 200, 255)
            )
            screen.blit(dialogue_surf, (BOARD_WIDTH + padding, y_offset))
            y_offset += 30
            assistant_dialogue = next(
                (
                    item["content"]
                    for item in reversed(data["history"])
                    if item["role"] == "assistant"
                ),
                "아직 기물의 응답이 없습니다.",
            )

            dialogue_text_body = (
                assistant_dialogue.split("]", 1)[1].strip()
                if "[" in assistant_dialogue and "]" in assistant_dialogue
                else assistant_dialogue
            )

            dialogue_words = dialogue_text_body.split(" ")
            current_dialogue_line = ""
            max_dialogue_width = PANEL_WIDTH - (padding * 2) - 10
            line_height = INFO_FONT_BODY.get_linesize()

            # ⬇️⬇️⬇️ [ 여기가 수정된 부분입니다 ] ⬇️⬇️⬇️
            # (lines 633-646) -> (아래 코드로 전체 교체)
            for word in dialogue_words:
                # 1. 'current_line'이 아닌 'current_dialogue_line'을 사용
                test_line = current_dialogue_line + word + " "
                test_surf = INFO_FONT_BODY.render(
                    test_line, True, pygame.Color(255, 255, 255)
                )

                # 2. 페르소나 래핑 로직과 동일하게 수정
                if test_surf.get_width() > max_dialogue_width:
                    # (1) 단어를 추가하기 전의 'current_dialogue_line'을 먼저 그림
                    line_surf = INFO_FONT_BODY.render(
                        current_dialogue_line.strip(),  # .strip() 추가 (안전)
                        True,
                        pygame.Color(255, 255, 255),
                    )
                    screen.blit(line_surf, (BOARD_WIDTH + padding + 10, y_offset))
                    y_offset += line_height
                    # (2) 새 줄을 현재 단어로 시작
                    current_dialogue_line = word + " "
                else:
                    # (3) 단어를 현재 줄에 추가
                    current_dialogue_line = test_line
            # ⬆️⬆️⬆️ [ 수정 완료 ] ⬆️⬆️⬆️

            if current_dialogue_line.strip():
                line_surf = INFO_FONT_BODY.render(
                    current_dialogue_line.strip(),
                    True,
                    pygame.Color(255, 255, 255),
                )
                screen.blit(line_surf, (BOARD_WIDTH + padding + 10, y_offset))
        # --- [if not is_king:] 블록 끝 ---

    else:
        # 기물이 선택되지 않았을 때 표시
        text = INFO_FONT_HEADER.render(
            "백색 기물을 클릭하세요.", True, pygame.Color(150, 150, 150)
        )
        text_rect = text.get_rect(center=(BOARD_WIDTH + PANEL_WIDTH // 2, y_offset))
        screen.blit(text, text_rect)

    return button_rect, force_move_button_rect


# 'force_move_count' 인자 추가 (기본값 0)
def draw_current_state(
    screen,
    game_board,
    game_white_ids,
    game_piece_data,
    last_response,
    last_piece_dialogue,
    selected_piece_id_to_show: str | None,
    force_move_count: int = 0,  # <--- [추가] 흑 턴/게임 종료 시 호출 대비 기본값
):
    # (코드 로직 동일)
    dialogue_text = ""
    dialogue_active = False
    cursor_on = False

    king_square_name = None
    if game_board.is_checkmate():
        king_color = game_board.turn
        king_sq_index = game_board.king(king_color)
        if king_sq_index is not None:
            king_square_name = chess.square_name(king_sq_index)

    screen.fill(pygame.Color(0, 0, 0))
    draw_board(screen)
    draw_pieces(screen, game_board, load_piece_images(SQUARE_SIZE), game_white_ids)

    draw_info_panel(
        screen,
        game_piece_data,
        selected_piece_id_to_show,
        dialogue_text,
        dialogue_active,
        last_response,
        last_piece_dialogue,
        cursor_on,
        force_move_count=force_move_count,
    )
    pygame.display.flip()


# 'force_move_count' 인자 추가 및 헬퍼 함수 추가
def run_game_gui(
    game_board,
    game_white_ids,
    game_piece_data,
    sf_engine,
    turn_callback,
    screen,
    clock,
    force_move_count: int,
):
    # (코드 로직 동일 - run_confirmation_popup 호출 부분 포함)
    screen = screen
    clock = clock

    pygame.display.set_caption("자아를 가진 체스")
    pygame.key.start_text_input()

    piece_images = load_piece_images(SQUARE_SIZE)
    if piece_images is None:
        return "QUIT"

    if not hasattr(run_game_gui, "prev_last_response"):
        run_game_gui.prev_last_response = "[INFO] 게임 시작. 백 턴."
        run_game_gui.prev_last_piece_dialogue = "아직 응답이 없습니다."
        run_game_gui.prev_selected_square_name = None
        run_game_gui.prev_selected_piece_id = None
        run_game_gui.prev_selected_piece_id_to_show = None

    running = True
    game_state = 0

    selected_square_name = run_game_gui.prev_selected_square_name
    selected_piece_id = run_game_gui.prev_selected_piece_id
    selected_piece_id_to_show = run_game_gui.prev_selected_piece_id_to_show

    target_square_name = None
    uci_move_to_try = None
    legal_moves_uci = []

    location_to_id = {v: k for k, v in game_white_ids.items() if v is not None}

    dialogue_text = ""
    dialogue_active = False
    last_response = run_game_gui.prev_last_response
    last_piece_dialogue = run_game_gui.prev_last_piece_dialogue

    cursor_timer = 0
    cursor_on = True
    CURSOR_BLINK_RATE = 500

    button_rect = pygame.Rect(0, 0, 0, 0)
    force_move_button_rect = pygame.Rect(0, 0, 0, 0)

    def reset_move_state(full_reset=False):
        nonlocal game_state, selected_square_name, selected_piece_id, target_square_name, uci_move_to_try, legal_moves_uci, dialogue_active, last_response, last_piece_dialogue, selected_piece_id_to_show

        game_state = 0
        target_square_name = None
        uci_move_to_try = None
        legal_moves_uci = []
        dialogue_active = False

        if full_reset:
            selected_square_name = None
            selected_piece_id = None
            selected_piece_id_to_show = None

            run_game_gui.prev_selected_square_name = None
            run_game_gui.prev_selected_piece_id = None
            run_game_gui.prev_selected_piece_id_to_show = None
            run_game_gui.prev_last_response = "[INFO] 백 턴. 기물을 선택하세요."
            run_game_gui.prev_last_piece_dialogue = "아직 응답이 없습니다."

            return run_game_gui.prev_last_response

        selected_piece_id = None
        selected_square_name = None

        run_game_gui.prev_last_response = last_response
        run_game_gui.prev_last_piece_dialogue = last_piece_dialogue
        run_game_gui.prev_selected_square_name = selected_square_name
        run_game_gui.prev_selected_piece_id = selected_piece_id
        run_game_gui.prev_selected_piece_id_to_show = selected_piece_id_to_show

        return last_response

    def attempt_persuasion(is_king_move=False):
        nonlocal last_response, last_piece_dialogue, dialogue_text, dialogue_active, selected_piece_id_to_show

        if not is_king_move and (game_state != 2 or not dialogue_text.strip()):
            last_response = "[ERROR] 이동 목표 선택 및 대사 입력이 필요합니다."
            return None

        persuasion_input = "" if is_king_move else dialogue_text

        last_response = (
            "[WAIT] 기물 설득 중..."
            if not is_king_move
            else "[WAIT] 킹의 명령 처리 중..."
        )
        pygame.display.flip()

        decision, dialogue = turn_callback(
            uci_move_to_try, persuasion_input, force_move=False
        )

        last_piece_dialogue = dialogue
        dialogue_text = ""
        dialogue_active = True

        if is_king_move and decision == True:
            last_response = "[수락] 킹의 명령이 즉시 수행되었습니다."
        elif is_king_move and decision == False:
            last_response = "[오류] 킹의 이동이 유효하지 않습니다."
        elif is_king_move and decision == "오류":
            last_response = f"[오류] 킹의 명령 처리 중 오류: {dialogue}"
        else:
            last_response = (
                f"[{decision}] {dialogue}"
                if decision in ["수락", "거부", "오류"]
                else last_response
            )

        if decision == "수락" or decision == True:
            reset_move_state(full_reset=False)
            return "WHITE_MOVED"

        elif decision == "거부" or decision == "오류" or decision == False:
            run_game_gui.prev_last_response = last_response
            run_game_gui.prev_last_piece_dialogue = last_piece_dialogue
            run_game_gui.prev_selected_square_name = selected_square_name
            run_game_gui.prev_selected_piece_id = selected_piece_id
            run_game_gui.prev_selected_piece_id_to_show = selected_piece_id_to_show
            return None

    def attempt_force_move():
        nonlocal last_response, last_piece_dialogue, dialogue_active

        if game_state != 2:
            last_response = "[ERROR] 강제 이동은 목표 칸이 선택된 상태여야 합니다."
            return None
        if force_move_count <= 0:
            last_response = "[ERROR] 강제 이동 횟수를 모두 사용했습니다."
            return None

        last_response = "[WAIT] 킹의 권한으로 강제 이동 중..."
        pygame.display.flip()

        decision, dialogue = turn_callback(
            uci_move_to_try, persuasion_dialogue="[강제 이동]", force_move=True
        )

        last_piece_dialogue = dialogue
        dialogue_text = ""
        dialogue_active = True

        if decision == "수락" or decision == True:
            last_response = f"[수락] {dialogue}"
            reset_move_state(full_reset=False)
            return "WHITE_MOVED_FORCED"

        else:
            last_response = f"[{decision}] {dialoglge}"
            run_game_gui.prev_last_response = last_response
            run_game_gui.prev_last_piece_dialogue = last_piece_dialogue
            run_game_gui.prev_selected_square_name = selected_square_name
            run_game_gui.prev_selected_piece_id = selected_piece_id
            run_game_gui.prev_selected_piece_id_to_show = selected_piece_id_to_show
            return None

    if selected_square_name:
        start_sq_idx = chess.parse_square(selected_square_name)
        piece_at_sq = game_board.piece_at(start_sq_idx)

        if piece_at_sq and piece_at_sq.color == chess.WHITE:
            legal_moves_uci = [
                move.uci()
                for move in game_board.legal_moves
                if move.from_square == start_sq_idx
            ]
            game_state = 1
        else:
            last_response = reset_move_state(full_reset=True)

    while running:
        cursor_timer += clock.get_time()
        if cursor_timer > CURSOR_BLINK_RATE:
            cursor_on = not cursor_on
            cursor_timer = 0

        location_to_id = {v: k for k, v in game_white_ids.items() if v is not None}

        if game_board.turn == chess.BLACK:
            run_game_gui.prev_selected_square_name = selected_square_name
            run_game_gui.prev_selected_piece_id = selected_piece_id
            run_game_gui.prev_selected_piece_id_to_show = selected_piece_id_to_show
            run_game_gui.prev_last_response = last_response
            run_game_gui.prev_last_piece_dialogue = last_piece_dialogue
            return "BLACK_TURN"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return "QUIT"

            if event.type == pygame.TEXTINPUT and dialogue_active:
                dialogue_text += event.text

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE and dialogue_active:
                    dialogue_text = dialogue_text[:-1]

                if event.key == pygame.K_RETURN and game_state == 2:
                    result = attempt_persuasion()
                    if result:
                        return result

                if event.key == pygame.K_ESCAPE:
                    last_response = reset_move_state(full_reset=True)
                    dialogue_text = ""
                    last_response = (
                        "[INFO] 선택이 취소되었습니다. 새로운 기물을 선택하세요."
                    )

                elif event.key == pygame.K_BACKQUOTE:
                    print("백틱(`) 눌림. 메인 메뉴 복귀 확인 팝업...")
                    confirmation_result = run_confirmation_popup(
                        screen, clock, "메인 메뉴로 돌아가시겠습니까?"
                    )
                    if confirmation_result == "CONFIRMED":
                        print("메인 메뉴로 복귀합니다.")
                        return "QUIT"
                    else:
                        print("게임을 계속합니다.")
                        pass

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                clicked_square = get_clicked_square(pos)

                if button_rect.collidepoint(pos) and game_state == 2:
                    result = attempt_persuasion()
                    if result:
                        return result

                elif force_move_button_rect.collidepoint(pos) and game_state == 2:
                    result = attempt_force_move()
                    if result:
                        return result

                elif clicked_square:
                    clicked_piece_id = location_to_id.get(clicked_square)
                    clicked_piece = game_board.piece_at(
                        chess.parse_square(clicked_square)
                    )
                    is_ally_piece = (
                        clicked_piece_id
                        and clicked_piece
                        and clicked_piece.color == chess.WHITE
                    )

                    if game_state == 0 and is_ally_piece:
                        selected_square_name = clicked_square
                        selected_piece_id = clicked_piece_id
                        selected_piece_id_to_show = clicked_piece_id

                        start_sq_idx = chess.parse_square(selected_square_name)
                        legal_moves_uci = [
                            move.uci()
                            for move in game_board.legal_moves
                            if move.from_square == start_sq_idx
                        ]

                        game_state = 1
                        dialogue_active = False
                        piece_name = game_piece_data.get(clicked_piece_id, {}).get(
                            "name", clicked_piece_id
                        )
                        last_response = (
                            f"[INFO] {piece_name} 선택됨. 목표 칸을 클릭하세요."
                        )

                    elif game_state == 1:
                        if clicked_square == selected_square_name or is_ally_piece:
                            if is_ally_piece and clicked_square != selected_square_name:
                                last_response = reset_move_state(full_reset=False)

                                selected_square_name = clicked_square
                                selected_piece_id = clicked_piece_id
                                selected_piece_id_to_show = clicked_piece_id
                                start_sq_idx = chess.parse_square(selected_square_name)
                                legal_moves_uci = [
                                    move.uci()
                                    for move in game_board.legal_moves
                                    if move.from_square == start_sq_idx
                                ]
                                game_state = 1
                                piece_name = game_piece_data.get(
                                    clicked_piece_id, {}
                                ).get("name", clicked_piece_id)
                                last_response = (
                                    f"[INFO] {piece_name} 선택됨. 목표 칸을 클릭하세요."
                                )
                            else:
                                last_response = reset_move_state(full_reset=True)
                                dialogue_text = ""

                        else:
                            target_square_name = clicked_square
                            move_str = selected_square_name + target_square_name
                            piece_to_move = game_board.piece_at(
                                chess.parse_square(selected_square_name)
                            )
                            uci_move_to_try = move_str
                            if (
                                piece_to_move
                                and piece_to_move.piece_type == chess.PAWN
                                and chess.parse_square(target_square_name)
                                in [
                                    chess.A8,
                                    chess.H8,
                                    chess.B8,
                                    chess.C8,
                                    chess.D8,
                                    chess.E8,
                                    chess.F8,
                                    chess.G8,
                                ]
                            ):
                                uci_move_to_try = move_str + "q"

                            if (
                                uci_move_to_try in legal_moves_uci
                                or (uci_move_to_try[:4] + "q") in legal_moves_uci
                            ):
                                is_king = piece_to_move.symbol().upper() == "K"
                                if is_king:
                                    result = attempt_persuasion(is_king_move=True)
                                    if result:
                                        return result
                                else:
                                    game_state = 2
                                    dialogue_active = True
                                    last_response = f"[WAIT] '{uci_move_to_try}' 이동 확인. 대사를 입력 후 설득하세요."
                                    legal_moves_uci = []
                            else:
                                last_response = f"[ERROR] '{uci_move_to_try[:4]}'는 합법적인 이동이 아닙니다."
                                game_state = 1
                                target_square_name = None
                                uci_move_to_try = None
                    elif game_state == 2:
                        last_response = f"[WAIT] 현재 '{uci_move_to_try[:4]}' 설득 중입니다. [설득하기] 버튼을 누르거나 Enter를 치세요."

        screen.fill(pygame.Color(0, 0, 0))
        draw_board(screen, selected_square_name, legal_moves_uci, target_square_name)
        draw_pieces(screen, game_board, piece_images, game_white_ids)

        button_rect, force_move_button_rect = draw_info_panel(
            screen,
            game_piece_data,
            selected_piece_id_to_show,
            dialogue_text,
            dialogue_active,
            last_response,
            last_piece_dialogue,
            cursor_on,
            force_move_count=force_move_count,
        )

        pygame.display.flip()
        clock.tick(60)

    return "QUIT"


# (run_game_over_screen 함수는 이 아래에 위치함 - 변경 없음)
def run_game_over_screen(
    screen: pygame.Surface, clock: pygame.Surface, final_message: str
) -> str:
    # (코드 로직 동일)
    POPUP_WIDTH = 400
    POPUP_HEIGHT = 250
    BUTTON_WIDTH = 150
    BUTTON_HEIGHT = 50

    popup_rect = pygame.Rect(
        (WINDOW_WIDTH - POPUP_WIDTH) // 2,
        (WINDOW_HEIGHT - POPUP_HEIGHT) // 2,
        POPUP_WIDTH,
        POPUP_HEIGHT,
    )

    new_game_rect = pygame.Rect(
        popup_rect.x + (POPUP_WIDTH // 4) - (BUTTON_WIDTH // 2),
        popup_rect.y + POPUP_HEIGHT - BUTTON_HEIGHT - 30,
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
    )

    menu_rect = pygame.Rect(
        popup_rect.x + (POPUP_WIDTH * 3 // 4) - (BUTTON_WIDTH // 2),
        popup_rect.y + POPUP_HEIGHT - BUTTON_HEIGHT - 30,
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
    )

    title_font = INFO_FONT_TITLE
    button_font = INFO_FONT_HEADER

    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if new_game_rect.collidepoint(mouse_pos):
                        print("선택: 새 게임")
                        return "NEW_GAME"
                    if menu_rect.collidepoint(mouse_pos):
                        print("선택: 메뉴로 돌아가기 (더미)")
                        return "QUIT"

        pygame.draw.rect(screen, pygame.Color(50, 50, 50), popup_rect, border_radius=10)
        pygame.draw.rect(
            screen, pygame.Color(200, 200, 200), popup_rect, width=2, border_radius=10
        )

        clean_message = (
            final_message.split("]")[-1].strip()
            if "]" in final_message
            else final_message
        )
        message_surf = title_font.render(
            clean_message, True, pygame.Color(255, 255, 255)
        )
        message_rect = message_surf.get_rect(
            center=(popup_rect.centerx, popup_rect.y + 60)
        )
        screen.blit(message_surf, message_rect)

        draw_button(
            screen,
            new_game_rect,
            "새 게임",
            button_font,
            pygame.Color(50, 150, 50),
            pygame.Color(80, 180, 80),
        )

        draw_button(
            screen,
            menu_rect,
            "메뉴로",
            button_font,
            pygame.Color(100, 100, 100),
            pygame.Color(130, 130, 130),
        )

        pygame.display.flip()
        clock.tick(60)

    return "QUIT"


# ⬇️⬇️⬇️ [새 함수 추가] ⬇️⬇️⬇️
# (이 함수는 run_game_gui의 K_BACKQUOTE 로직에서 호출됩니다)
def run_confirmation_popup(
    screen: pygame.Surface, clock: pygame.Surface, message: str
) -> str:
    """
    범용 확인 팝업창을 띄우고 "확인" 또는 "취소"를 반환합니다.
    """

    # --- 1. 팝업창 및 버튼 크기/위치 정의 ---
    POPUP_WIDTH = 450
    POPUP_HEIGHT = 200
    BUTTON_WIDTH = 120
    BUTTON_HEIGHT = 50

    # 화면 중앙에 팝업창 위치 계산
    popup_rect = pygame.Rect(
        (WINDOW_WIDTH - POPUP_WIDTH) // 2,
        (WINDOW_HEIGHT - POPUP_HEIGHT) // 2,
        POPUP_WIDTH,
        POPUP_HEIGHT,
    )

    # 버튼 위치 (팝업창 기준)
    confirm_rect = pygame.Rect(
        popup_rect.x + (POPUP_WIDTH // 4) - (BUTTON_WIDTH // 2),
        popup_rect.y + POPUP_HEIGHT - BUTTON_HEIGHT - 30,
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
    )

    cancel_rect = pygame.Rect(
        popup_rect.x + (POPUP_WIDTH * 3 // 4) - (BUTTON_WIDTH // 2),
        popup_rect.y + POPUP_HEIGHT - BUTTON_HEIGHT - 30,
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
    )

    # --- 2. 폰트 정의 (gui_utils에서 가져옴) ---
    title_font = INFO_FONT_HEADER  # 게임 오버보다 작은 폰트 사용
    button_font = INFO_FONT_HEADER

    # --- 3. 배경 어둡게 처리 (Semi-Transparent Overlay) ---
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # 180/255 투명도의 검은색
    screen.blit(overlay, (0, 0))

    # --- 4. 이벤트 루프 시작 (팝업 전용) ---
    running = True
    while running:
        # 5. 이벤트 처리
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "CANCELLED"  # 창 닫기는 '취소'로 간주

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # ESC 키로도 취소 가능
                    return "CANCELLED"

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 좌클릭
                    if confirm_rect.collidepoint(mouse_pos):
                        return "CONFIRMED"
                    if cancel_rect.collidepoint(mouse_pos):
                        return "CANCELLED"

        # 6. 그리기
        pygame.draw.rect(screen, pygame.Color(60, 60, 60), popup_rect, border_radius=10)
        pygame.draw.rect(
            screen, pygame.Color(200, 200, 200), popup_rect, width=2, border_radius=10
        )

        message_surf = title_font.render(message, True, pygame.Color(255, 255, 255))
        message_rect = message_surf.get_rect(
            center=(popup_rect.centerx, popup_rect.y + 60)
        )
        screen.blit(message_surf, message_rect)

        # 확인 버튼 (빨간색 - 위험한 동작)
        draw_button(
            screen,
            confirm_rect,
            "확인",
            button_font,
            pygame.Color(220, 50, 50),
            pygame.Color(250, 80, 80),
        )
        # 취소 버튼 (회색 - 안전한 동작)
        draw_button(
            screen,
            cancel_rect,
            "취소",
            button_font,
            pygame.Color(100, 100, 100),
            pygame.Color(130, 130, 130),
        )

        # 7. 화면 업데이트
        pygame.display.flip()
        clock.tick(60)

    return "CANCELLED"  # (Failsafe)
