import pygame
import sys
from gui_utils import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    INFO_FONT_TITLE,
    INFO_FONT_HEADER,
    INFO_FONT_BODY,
    draw_button,
    draw_text_input,  # <--- 1단계에서 옮긴 함수
)


def run_custom_game_screen(screen: pygame.Surface, clock: pygame.Surface) -> str:
    """
    커스텀 게임 FEN 입력 화면을 표시하고 사용자 입력을 대기합니다.
    입력된 FEN 문자열, "BACK", 또는 "QUIT"을 반환합니다.
    (수정됨: Ctrl+V 붙여넣기 기능 수정)
    """

    # --- 1. 상태 변수 ---
    fen_input_text = ""
    input_active = True  # 시작부터 입력창 활성화
    running = True

    # 커서 깜빡임용
    cursor_timer = 0
    cursor_on = True
    CURSOR_BLINK_RATE = 500

    # --- 2. 레이아웃 정의 ---
    center_x = WINDOW_WIDTH // 2

    # FEN 입력창
    input_rect = pygame.Rect(
        center_x - (WINDOW_WIDTH * 0.7) // 2,  # 너비 70%
        200,
        WINDOW_WIDTH * 0.7,
        100,  # 높이 100
    )

    # "게임 시작" 버튼
    start_button_rect = pygame.Rect(
        center_x - 100,  # 너비 200
        350,
        200,
        50,  # 높이 50
    )

    # "뒤로 가기" 버튼
    back_button_rect = pygame.Rect(
        center_x - 100,
        420,
        200,
        50,
    )

    # --- 3. 이벤트 루프 시작 (FEN 입력 전용) ---
    pygame.key.start_text_input()  # 텍스트 입력 활성화

    while running:
        # 3-1. 커서 타이머 업데이트
        cursor_timer += clock.get_time()
        if cursor_timer > CURSOR_BLINK_RATE:
            cursor_on = not cursor_on
            cursor_timer = 0

        # 3-2. 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.key.stop_text_input()  # 종료 전 입력기 비활성화
                return "QUIT"

            # --- 키보드 입력 처리 ---
            if event.type == pygame.TEXTINPUT and input_active:
                fen_input_text += event.text

            if event.type == pygame.KEYDOWN:
                if input_active:

                    # ⬇️⬇️⬇️ [수정됨] ⬇️⬇️⬇️
                    # Ctrl+V (붙여넣기) 감지
                    if event.key == pygame.K_v and (event.mod & pygame.KMOD_CTRL):
                        try:
                            # pygame.scrap.get()은 bytes를 반환
                            paste_bytes = pygame.scrap.get(pygame.SCRAP_TEXT)
                            if paste_bytes:
                                # bytes를 디코딩하고, null 문자(\x00) 제거
                                paste_text = paste_bytes.decode("utf-8").rstrip("\x00")
                                fen_input_text += paste_text
                                print(f"클립보드 붙여넣기: {paste_text}")
                        except (pygame.error, UnicodeDecodeError) as e:
                            # (클립보드가 비어있거나, 텍스트가 아니거나, 초기화 안됨)
                            print(f"클립보드 오류: {e}")

                    # [수정] 'elif'로 변경하여 동시 실행 방지
                    elif event.key == pygame.K_BACKSPACE:
                        # ⬆️⬆️⬆️ [수정 완료] ⬆️⬆️⬆️
                        fen_input_text = fen_input_text[:-1]

                    if event.key == pygame.K_RETURN:
                        # Enter 키로 게임 시작
                        print(f"FEN 입력 완료: {fen_input_text}")
                        pygame.key.stop_text_input()
                        return fen_input_text.strip()

                if event.key == pygame.K_ESCAPE:
                    # ESC 키로 뒤로 가기
                    print("선택: 뒤로 가기 (ESC)")
                    pygame.key.stop_text_input()
                    return "BACK"

            # --- 마우스 클릭 처리 ---
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 좌클릭

                    # "게임 시작" 버튼
                    if start_button_rect.collidepoint(event.pos):
                        print(f"FEN 입력 완료: {fen_input_text}")
                        pygame.key.stop_text_input()
                        return fen_input_text.strip()

                    # "뒤로 가기" 버튼
                    if back_button_rect.collidepoint(event.pos):
                        print("선택: 뒤로 가기")
                        pygame.key.stop_text_input()
                        return "BACK"

                    # 입력창 클릭 시 활성화/비활성화
                    if input_rect.collidepoint(event.pos):
                        input_active = True
                    else:
                        input_active = False

        # 4. 그리기

        # 4-1. 배경
        screen.fill(pygame.Color(30, 30, 30))

        # 4-2. 제목
        title_surf = INFO_FONT_TITLE.render(
            "커스텀 게임 (FEN 입력)", True, pygame.Color(255, 255, 255)
        )
        title_rect = title_surf.get_rect(center=(center_x, 100))
        screen.blit(title_surf, title_rect)

        # 4-3. FEN 입력창 레이블
        input_label = INFO_FONT_HEADER.render(
            "FEN 문자열을 입력하세요:", True, pygame.Color(200, 200, 200)
        )
        screen.blit(input_label, (input_rect.x, input_rect.y - 30))

        # 4-4. FEN 입력창 그리기 (gui_utils.py 함수 사용)
        draw_text_input(
            screen,
            fen_input_text,
            input_rect,
            active=input_active,
            cursor_on=cursor_on,
        )

        # 4-5. 버튼 그리기
        draw_button(
            screen,
            start_button_rect,
            "게임 시작 (Enter)",
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

        # 5. 화면 업데이트
        pygame.display.flip()
        clock.tick(60)

    pygame.key.stop_text_input()
    return "BACK"  # (Failsafe)
