import pygame
import sys
from gui_utils import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    # (폰트 import는 이제 필요 없으므로 제거)
    IMAGE_DIR,
)


# 헬퍼 함수: 비율에 맞게 이미지 리사이즈
def scale_image_proportional(image, target_width):
    """
    이미지의 비율을 유지하면서 목표 너비(target_width)에 맞게 리사이즈합니다.
    """
    # 1. 원본 크기 및 비율 계산
    original_width = image.get_width()
    original_height = image.get_height()
    aspect_ratio = original_height / original_width

    # 2. 목표 높이 계산
    target_height = int(target_width * aspect_ratio)

    # 3. 리사이즈 (smoothscale이 scale보다 품질이 좋음)
    scaled_image = pygame.transform.smoothscale(image, (target_width, target_height))
    return scaled_image


def run_main_menu_screen(screen: pygame.Surface, clock: pygame.Surface) -> str:
    """
    메인 메뉴 화면을 표시하고 사용자 입력을 대기합니다.
    (수정됨: 모든 UI 이미지의 비율을 유지하며 리사이즈)
    """

    # --- 1. 배경 이미지 로드 ---
    try:
        bg_image_original = pygame.image.load(IMAGE_DIR / "background.png")
        bg_image = pygame.transform.scale(
            bg_image_original, (WINDOW_WIDTH, WINDOW_HEIGHT)
        )
    except pygame.error as e:
        print(f"❌ 배경 이미지 'background.png' 로드/스케일 오류: {e}")
        bg_image = None

    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))

    # ⬇️⬇️⬇️ [수정됨] ⬇️⬇️⬇️
    # --- 2. UI 목표 너비 정의 ---
    # (이 너비를 기준으로 비율에 맞게 높이가 자동 계산됩니다)

    # (제목 이미지 비율은 알려주지 않으셔서 일단 400으로 가정합니다)
    TARGET_TITLE_WIDTH = 400

    # (새게임, 커스텀, 설정 버튼: 710x348 비율)
    # (기존 파일의 200px을 목표 너비로 사용)
    TARGET_BUTTON_WIDTH = 175

    # (종료 버튼: 505x505 비율)
    # (기존 파일의 150px을 목표 너비로 사용)
    TARGET_QUIT_WIDTH = 50

    # --- 3. UI 이미지 로드 및 비율 유지 리사이즈 ---
    try:
        # 1. 제목 이미지 (비율 유지 리사이즈)
        title_img_orig = pygame.image.load(
            IMAGE_DIR / "title_image.png"
        ).convert_alpha()
        title_img = scale_image_proportional(title_img_orig, TARGET_TITLE_WIDTH)

        # 2. 새 게임 버튼 (710x348 비율 -> TARGET_BUTTON_WIDTH x N)
        new_game_img_orig = pygame.image.load(
            IMAGE_DIR / "button_new_game_normal.png"
        ).convert_alpha()
        new_game_img = scale_image_proportional(new_game_img_orig, TARGET_BUTTON_WIDTH)
        new_game_img_hover_orig = pygame.image.load(
            IMAGE_DIR / "button_new_game_hover.png"
        ).convert_alpha()
        new_game_img_hover = scale_image_proportional(
            new_game_img_hover_orig, TARGET_BUTTON_WIDTH
        )

        # 3. 커스텀 게임 버튼
        custom_game_img_orig = pygame.image.load(
            IMAGE_DIR / "button_custom_normal.png"
        ).convert_alpha()
        custom_game_img = scale_image_proportional(
            custom_game_img_orig, TARGET_BUTTON_WIDTH
        )
        custom_game_img_hover_orig = pygame.image.load(
            IMAGE_DIR / "button_custom_hover.png"
        ).convert_alpha()
        custom_game_img_hover = scale_image_proportional(
            custom_game_img_hover_orig, TARGET_BUTTON_WIDTH
        )

        # 4. 설정 버튼
        settings_img_orig = pygame.image.load(
            IMAGE_DIR / "button_settings_normal.png"
        ).convert_alpha()
        settings_img = scale_image_proportional(settings_img_orig, TARGET_BUTTON_WIDTH)
        settings_img_hover_orig = pygame.image.load(
            IMAGE_DIR / "button_settings_hover.png"
        ).convert_alpha()
        settings_img_hover = scale_image_proportional(
            settings_img_hover_orig, TARGET_BUTTON_WIDTH
        )

        # 5. 게임 종료 버튼 (505x505 비율 -> TARGET_QUIT_WIDTH x N)
        quit_img_orig = pygame.image.load(
            IMAGE_DIR / "button_quit_normal.png"
        ).convert_alpha()
        quit_img = scale_image_proportional(quit_img_orig, TARGET_QUIT_WIDTH)
        quit_img_hover_orig = pygame.image.load(
            IMAGE_DIR / "button_quit_hover.png"
        ).convert_alpha()
        quit_img_hover = scale_image_proportional(
            quit_img_hover_orig, TARGET_QUIT_WIDTH
        )

    except pygame.error as e:
        print(f"❌ 메뉴 UI 이미지 로드 또는 리사이즈 실패: {e}")
        return "QUIT"
    # ⬆️⬆️⬆️ [수정 완료] ⬆️⬆️⬆️

    # --- 4. UI 위치 및 Rect 정의 ---
    # (레이아웃은 마지막에 업로드해주신 '오른쪽 정렬'을 기준으로 합니다)

    elements_center_x = (WINDOW_WIDTH // 6) * 5
    BUTTON_Y_START = 350
    BUTTON_GAP = 20

    # 1. 제목 Rect
    title_rect = title_img.get_rect(center=(elements_center_x - 100, 135))

    # 2. '새 게임' 버튼 Rect
    new_game_rect = new_game_img.get_rect(center=(elements_center_x, BUTTON_Y_START))

    # 3. '커스텀 게임' 버튼 Rect
    # (이전 버튼의 bottom + 갭 + 새 버튼 높이의 절반)으로 중앙 정렬
    # (이제 높이가 다르므로 이 로직이 매우 중요합니다)
    custom_game_rect = custom_game_img.get_rect(
        center=(
            elements_center_x,
            new_game_rect.bottom + BUTTON_GAP + (custom_game_img.get_height() // 2),
        )
    )

    # 4. '설정' 버튼 Rect
    settings_rect = settings_img.get_rect(
        center=(
            elements_center_x,
            custom_game_rect.bottom + BUTTON_GAP + (settings_img.get_height() // 2),
        )
    )

    # 5. '게임 종료' 버튼 Rect
    quit_game_rect = quit_img.get_rect(
        bottomright=(WINDOW_WIDTH - 20, WINDOW_HEIGHT - 20)
    )

    # --- 5. 이벤트 루프 시작 (메뉴 전용) ---
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
                    if custom_game_rect.collidepoint(mouse_pos):
                        print("선택: 커스텀 게임")
                        return "CUSTOM_GAME"
                    if settings_rect.collidepoint(mouse_pos):
                        print("선택: 설정")
                        return "SETTINGS"
                    if quit_game_rect.collidepoint(mouse_pos):
                        print("선택: 게임 종료")
                        return "QUIT"

        # --- 6. 그리기 ---

        # 6-1. 배경 그리기
        if bg_image:
            screen.blit(bg_image, (0, 0))
            screen.blit(overlay, (0, 0))
        else:
            screen.fill(pygame.Color(20, 20, 20))

        # 6-2. 제목 이미지 그리기 (리사이즈된 이미지)
        screen.blit(title_img, title_rect)

        # 6-3. 버튼 이미지 그리기 (리사이즈된 이미지)

        # 새 게임
        if new_game_rect.collidepoint(mouse_pos):
            screen.blit(new_game_img_hover, new_game_rect)
        else:
            screen.blit(new_game_img, new_game_rect)

        # 커스텀 게임
        if custom_game_rect.collidepoint(mouse_pos):
            screen.blit(custom_game_img_hover, custom_game_rect)
        else:
            screen.blit(custom_game_img, custom_game_rect)

        # 설정
        if settings_rect.collidepoint(mouse_pos):
            screen.blit(settings_img_hover, settings_rect)
        else:
            screen.blit(settings_img, settings_rect)

        # 게임 종료
        if quit_game_rect.collidepoint(mouse_pos):
            screen.blit(quit_img_hover, quit_game_rect)
        else:
            screen.blit(quit_img, quit_game_rect)

        # 7. 화면 업데이트
        pygame.display.flip()
        clock.tick(60)

    return "QUIT"
