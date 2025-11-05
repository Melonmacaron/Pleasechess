import pygame
import sys
from gui_utils import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    # (INFO_FONT_TITLE은 이제 사용 안 함)
    INFO_FONT_HEADER,
    INFO_FONT_BODY,
    # ⬇️⬇️⬇️ [수정됨] ⬇️⬇️⬇️
    SETTINGS_FONT_TITLE,  # <--- 새로 추가된 폰트
    SETTINGS_FONT_LABEL,  # <--- 새로 추가된 폰트
    # ⬆️⬆️⬆️ [수정 완료] ⬆️⬆️⬆️
    draw_button,
    draw_text_input,
)


# 헬퍼 함수: 문자열이 숫자인지 확인 (정수만)
def is_numeric(value_str):
    return value_str.isdigit()


def run_settings_screen(
    screen: pygame.Surface, clock: pygame.Surface, current_settings: dict
) -> dict | None:
    """
    설정 화면을 표시하고 사용자 입력을 대기합니다.
    '저장' 시 새 설정 딕셔셔니를, '뒤로 가기' 시 None을 반환합니다.
    """

    # --- 1. 상태 변수 ---
    try:
        input_elo = str(current_settings.get("elo", 400))
        input_king_name = str(current_settings.get("king_name", "아서"))
        input_force_moves = str(current_settings.get("force_moves", 100))
    except Exception as e:
        print(f"설정 불러오기 오류: {e}")
        input_elo = "400"
        input_king_name = "아서"
        input_force_moves = "100"

    input_texts = {
        "elo": input_elo,
        "king_name": input_king_name,
        "force_moves": input_force_moves,
    }

    active_input = None
    running = True

    cursor_timer = 0
    cursor_on = True
    CURSOR_BLINK_RATE = 500

    # --- 2. 레이아웃 정의 ---
    center_x = WINDOW_WIDTH // 2
    INPUT_WIDTH = WINDOW_WIDTH * 0.6
    INPUT_HEIGHT = 50

    elo_input_rect = pygame.Rect(
        center_x - (INPUT_WIDTH // 2), 150, INPUT_WIDTH, INPUT_HEIGHT
    )

    king_name_input_rect = pygame.Rect(
        center_x - (INPUT_WIDTH // 2), 260, INPUT_WIDTH, INPUT_HEIGHT
    )

    force_moves_input_rect = pygame.Rect(
        center_x - (INPUT_WIDTH // 2), 370, INPUT_WIDTH, INPUT_HEIGHT
    )

    input_rects = {
        "elo": elo_input_rect,
        "king_name": king_name_input_rect,
        "force_moves": force_moves_input_rect,
    }

    save_button_rect = pygame.Rect(center_x - 100, 480, 200, 50)
    back_button_rect = pygame.Rect(center_x - 100, 550, 200, 50)

    # --- 3. 이벤트 루프 시작 (설정 전용) ---
    pygame.key.start_text_input()

    while running:
        cursor_timer += clock.get_time()
        if cursor_timer > CURSOR_BLINK_RATE:
            cursor_on = not cursor_on
            cursor_timer = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.key.stop_text_input()
                return None

            if event.type == pygame.TEXTINPUT and active_input:
                input_texts[active_input] += event.text

            if event.type == pygame.KEYDOWN:
                if active_input:
                    if event.key == pygame.K_BACKSPACE:
                        input_texts[active_input] = input_texts[active_input][:-1]

                    if event.key == pygame.K_RETURN:
                        if active_input == "elo":
                            active_input = "king_name"
                        elif active_input == "king_name":
                            active_input = "force_moves"
                        elif active_input == "force_moves":
                            active_input = None

                if event.key == pygame.K_ESCAPE:
                    print("선택: 뒤로 가기 (ESC)")
                    pygame.key.stop_text_input()
                    return None

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:

                    if save_button_rect.collidepoint(event.pos):
                        try:
                            elo_val = int(input_texts["elo"])
                            force_val = int(input_texts["force_moves"])
                            name_val = input_texts["king_name"].strip()

                            if not name_val:
                                name_val = "아서"

                            new_settings = {
                                "elo": elo_val,
                                "king_name": name_val,
                                "force_moves": force_val,
                            }
                            print(f"설정 저장: {new_settings}")
                            pygame.key.stop_text_input()
                            return new_settings

                        except ValueError:
                            print("오류: ELO와 강제 이동 횟수는 숫자여야 합니다.")
                            pass

                    elif back_button_rect.collidepoint(event.pos):
                        print("선택: 뒤로 가기")
                        pygame.key.stop_text_input()
                        return None

                    else:
                        clicked_on_input = False
                        for input_name, rect in input_rects.items():
                            if rect.collidepoint(event.pos):
                                active_input = input_name
                                clicked_on_input = True
                                break
                        if not clicked_on_input:
                            active_input = None

        # 4. 그리기
        screen.fill(pygame.Color(30, 30, 30))

        # 4-1. 제목
        # ⬇️⬇️⬇️ [수정됨] ⬇️⬇️⬇️
        title_surf = SETTINGS_FONT_TITLE.render(  # <--- 폰트 변경
            "설정", True, pygame.Color(255, 255, 255)
        )
        # ⬆️⬆️⬆️ [수정 완료] ⬆️⬆️⬆️
        title_rect = title_surf.get_rect(center=(center_x, 70))
        screen.blit(title_surf, title_rect)

        # 4-2. 입력창 1: ELO
        # ⬇️⬇️⬇️ [수정됨] ⬇️⬇️⬇️
        label_elo = SETTINGS_FONT_LABEL.render(
            "Stockfish ELO (숫자):", True, pygame.Color(200, 200, 200)
        )  # <--- 폰트 변경
        # ⬆️⬆️⬆️ [수정 완료] ⬆️⬆️⬆️
        screen.blit(
            label_elo, (elo_input_rect.x, elo_input_rect.y - 35)
        )  # (y 간격 조정)
        draw_text_input(
            screen,
            input_texts["elo"],
            elo_input_rect,
            active=(active_input == "elo"),
            cursor_on=cursor_on,
        )

        # 4-3. 입력창 2: 킹 이름
        # ⬇️⬇️⬇️ [수정됨] ⬇️⬇️⬇️
        label_king = SETTINGS_FONT_LABEL.render(
            "킹 이름:", True, pygame.Color(200, 200, 200)
        )  # <--- 폰트 변경
        # ⬆️⬆️⬆️ [수정 완료] ⬆️⬆️⬆️
        screen.blit(
            label_king, (king_name_input_rect.x, king_name_input_rect.y - 35)
        )  # (y 간격 조정)
        draw_text_input(
            screen,
            input_texts["king_name"],
            king_name_input_rect,
            active=(active_input == "king_name"),
            cursor_on=cursor_on,
        )

        # 4-4. 입력창 3: 강제 이동 횟수
        # ⬇️⬇️⬇️ [수정됨] ⬇️⬇️⬇️
        label_force = SETTINGS_FONT_LABEL.render(
            "강제 이동 횟수 (숫자):", True, pygame.Color(200, 200, 200)
        )  # <--- 폰트 변경
        # ⬆️⬆️⬆️ [수정 완료] ⬆️⬆️⬆️
        screen.blit(
            label_force, (force_moves_input_rect.x, force_moves_input_rect.y - 35)
        )  # (y 간격 조정)
        draw_text_input(
            screen,
            input_texts["force_moves"],
            force_moves_input_rect,
            active=(active_input == "force_moves"),
            cursor_on=cursor_on,
        )

        # 4-5. 버튼 그리기 (버튼 폰트는 INFO_FONT_HEADER 그대로 사용)
        draw_button(
            screen,
            save_button_rect,
            "저장",
            INFO_FONT_HEADER,
            pygame.Color(50, 150, 50),
            pygame.Color(80, 180, 80),
        )
        draw_button(
            screen,
            back_button_rect,
            "뒤로 가기 (ESC)",
            INFO_FONT_HEADER,
            pygame.Color(100, 100, 100),
            pygame.Color(130, 130, 130),
        )

        pygame.display.flip()
        clock.tick(60)

    pygame.key.stop_text_input()
    return None  # (Failsafe)
