import chess
import os
import sys
import pygame
from start_chess import initialize_game
from chess_logic import *
from persuade import *
from black_moving import StockfishEngine

# GUI 관련 import 경로 수정 및 main_menu, custom_game_screen, settings_screen 추가
from gui_utils import WINDOW_WIDTH, WINDOW_HEIGHT
from main_menu import run_main_menu_screen
from custom_game_screen import run_custom_game_screen
from settings_screen import run_settings_screen
from chess_gui import run_game_gui, draw_current_state, run_game_over_screen


# --- 1. 환경 및 엔진 초기화 ---

STOCKFISH_PATH = r"main_game\stockfish\stockfish-windows-x86-64-avx2.exe"

# --- 1-2. 기본 설정값 (전역 변수) ---
current_elo = 400
current_king_name = "아서"
current_force_move_limit = 5

try:
    sf_engine = StockfishEngine(executable_path=STOCKFISH_PATH, elo_level=current_elo)
    if sf_engine.stockfish is None:
        print("Stockfish 엔진 로드 실패. 프로그램을 종료합니다.")
        sys.exit(1)
except Exception as e:
    print(f"Stockfish 초기화 중 오류 발생: {e}")
    sys.exit(1)


# --- 2. 게임 상태 전역 변수 선언 ---
game_board = None
game_white_ids = None
game_piece_data = None
morale = 1
force_move_remaining = current_force_move_limit


# --- 3. 핸들러 및 헬퍼 함수 정의 ---


def reset_game_for_new_start(fen: str = None):
    """
    [수정] 새 게임 시작을 위해 모든 전역 변수를 초기화합니다.
    (사기 점수 morale=1 초기화 추가)
    """
    global game_board, game_white_ids, game_piece_data, morale, force_move_remaining
    global current_king_name, current_force_move_limit

    if fen:
        print(f"--- 🚀 커스텀 게임(FEN)으로 상태 초기화 ---")
    else:
        print("--- 🚀 새 게임을 위한 상태 초기화 ---")

    # 1. 게임 로직 변수 초기화 (수정됨)
    game_board, game_white_ids, game_piece_data = initialize_game(
        fen=fen, king_name=current_king_name
    )
    morale = 1  # <--- 사기 점수 1로 리셋
    force_move_remaining = current_force_move_limit

    # 2. GUI 상태 (함수 속성) 초기화
    if hasattr(run_game_gui, "prev_last_response"):
        try:
            del run_game_gui.prev_last_response
            del run_game_gui.prev_last_piece_dialogue
            del run_game_gui.prev_selected_square_name
            del run_game_gui.prev_selected_piece_id
            del run_game_gui.prev_selected_piece_id_to_show
            print("이전 GUI 상태를 성공적으로 리셋했습니다.")
        except AttributeError:
            pass


def handle_player_move(
    uci_move: str, persuasion_dialogue: str, force_move: bool = False
) -> (str, str):
    """
    [수정] GUI에서 호출될 실제 백 기물 이동 처리 로직.
    move_piece로부터 (decision, dialogue, captured_value)를 받아
    morale 전역 변수를 업데이트합니다.
    """
    global game_board, game_white_ids, game_piece_data, morale

    try:
        if chess.Move.from_uci(uci_move) not in game_board.legal_moves:
            return "거부", "킹의 명령: 해당 이동은 현재 규칙상 유효하지 않습니다."
    except ValueError:
        return "오류", "킹의 명령: 잘못된 UCI 형식입니다."

    # 3. move_piece 호출 (이제 3개의 값을 반환)
    decision, dialogue, captured_value = move_piece(
        game_board,
        game_white_ids,
        game_piece_data,
        uci_move,
        persuade=(not force_move),
        persuasion_dialogue=persuasion_dialogue,
        morale=morale,
    )

    # 4. [추가] 사기 점수 적용
    if decision == "수락" or decision == True:
        if captured_value > 0:
            morale += captured_value
            print(f"🎉 기물 획득! 사기 {captured_value} 증가. (현재 사기: {morale})")

    return decision, dialogue


def handle_black_turn() -> (bool, int):
    """
    [수정] 흑(Stockfish) 턴의 이동을 처리합니다.
    move_piece_black으로부터 (success, lost_value)를 받아 그대로 반환합니다.
    """
    global game_board, game_white_ids, game_piece_data

    stockfish_move = sf_engine.get_best_move(game_board)

    if stockfish_move:
        success, lost_value = move_piece_black(
            game_board, game_white_ids, game_piece_data, stockfish_move
        )
        if success:
            return (True, lost_value)
        else:
            print(f"❌ 흑 기물 이동 오류: {stockfish_move}")
            return (False, 0)
    else:
        print("❌ Stockfish가 수를 찾지 못했습니다.")
        return (False, 0)


# --- 5. 메인 게임 루프 (상태 관리자) ---


def main_game_loop():
    global game_board, game_white_ids, game_piece_data, force_move_remaining, morale
    global current_elo, current_king_name, current_force_move_limit, sf_engine

    pygame.init()

    # ⬇️⬇️⬇️ [수정] ⬇️⬇️⬇️
    # screen과 clock을 먼저 정의해야 합니다.
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    # 클립보드(붙여넣기) 모듈 초기화 (창 생성 *이후*에 호출)
    try:
        pygame.scrap.init()
        print("✅ Pygame 클립보드(scrap) 모듈 초기화 성공.")
    except pygame.error as e:
        print(f"❌ Pygame 클립보드(scrap) 초기화 실패: {e}")
        print("붙여넣기(Ctrl+V) 기능이 작동하지 않을 수 있습니다.")
    # ⬆️⬆️⬆️ [수정 완료] ⬆️⬆️⬆️

    current_state = "MENU"

    while True:

        # --- 5-1. 메인 메뉴 상태 ---
        if current_state == "MENU":
            pygame.display.set_caption("PLEASE Chess - 메인 메뉴")
            menu_choice = run_main_menu_screen(screen, clock)

            if menu_choice == "NEW_GAME":
                reset_game_for_new_start(fen=None)
                current_state = "PLAYING"

            elif menu_choice == "CUSTOM_GAME":
                current_state = "CUSTOM_GAME_SETUP"

            elif menu_choice == "SETTINGS":
                current_state = "SETTINGS"

            elif menu_choice == "QUIT":
                break

        # --- 5-2. 커스텀 게임 FEN 입력 상태 ---
        elif current_state == "CUSTOM_GAME_SETUP":
            pygame.display.set_caption("PLEASE Chess - 커스텀 게임 설정")
            fen_result = run_custom_game_screen(screen, clock)

            if fen_result == "BACK":
                current_state = "MENU"

            elif fen_result == "QUIT":
                break

            else:
                reset_game_for_new_start(fen=fen_result)
                current_state = "PLAYING"

        # --- 5-3. 설정 화면 상태 ---
        elif current_state == "SETTINGS":
            pygame.display.set_caption("PLEASE Chess - 설정")

            current_settings_data = {
                "elo": current_elo,
                "king_name": current_king_name,
                "force_moves": current_force_move_limit,
            }

            new_settings = run_settings_screen(screen, clock, current_settings_data)

            if new_settings:
                print(f"새 설정 적용: {new_settings}")

                try:
                    new_elo = int(new_settings["elo"])
                    if current_elo != new_elo:
                        current_elo = new_elo
                        sf_engine.set_elo(current_elo)

                    current_king_name = new_settings["king_name"]
                    current_force_move_limit = int(new_settings["force_moves"])

                except ValueError:
                    print(
                        "오류: settings_screen이 숫자가 아닌 값을 반환했습니다. (ELO/Force)"
                    )
                except Exception as e:
                    print(f"설정 적용 중 오류: {e}")

            current_state = "MENU"

        # --- 5-4. 게임 플레이 상태 ---
        elif current_state == "PLAYING":
            pygame.display.set_caption("자아를 가진 체스 (플레이 중)")

            # 1. 보드 상태 확인
            board_state = get_game_status(game_board)

            # 2. 게임 종료 확인
            is_game_over = board_state in [
                STATUS_CHECKMATE_WHITE_WINS,
                STATUS_CHECKMATE_BLACK_WINS,
                STATUS_STALEMATE,
                STATUS_DRAW_INSUFFICIENT_MATERIAL,
                STATUS_DRAW_SEVENTYFIVE_MOVES,
                STATUS_DRAW_FIVEFOLD_REPETITION,
                STATUS_DRAW_OTHER,
            ]

            if is_game_over:
                # ( ... 게임 오버 로직 ... )
                if board_state == STATUS_CHECKMATE_WHITE_WINS:
                    final_message = "체크메이트! 백색 승리!"
                elif board_state == STATUS_CHECKMATE_BLACK_WINS:
                    final_message = "체크메이트! 흑색 승리."
                else:
                    final_message = "무승부!"

                selected_piece_id_to_show = getattr(
                    run_game_gui, "prev_selected_piece_id_to_show", None
                )
                last_piece_dialogue = getattr(
                    run_game_gui, "prev_last_piece_dialogue", ""
                )
                draw_current_state(
                    screen,
                    game_board,
                    game_white_ids,
                    game_piece_data,
                    f"[게임 종료] {final_message}",
                    last_piece_dialogue,
                    selected_piece_id_to_show,
                    force_move_count=force_move_remaining,
                )
                pygame.display.flip()

                game_over_choice = run_game_over_screen(screen, clock, final_message)

                if game_over_choice == "NEW_GAME":
                    reset_game_for_new_start(fen=None)
                    continue

                elif game_over_choice == "QUIT":
                    current_state = "MENU"

            # 3. 턴 처리 로직 (게임이 종료되지 않았을 때)
            else:
                # 3-1. ⚪ 백 (플레이어) 턴
                if game_board.turn == chess.WHITE:
                    gui_result = run_game_gui(
                        game_board,
                        game_white_ids,
                        game_piece_data,
                        sf_engine,
                        handle_player_move,
                        screen,
                        clock,
                        force_move_count=force_move_remaining,
                    )

                    if gui_result == "WHITE_MOVED":
                        print("✅ 백의 수락 및 이동 완료. 흑 턴으로 전환.")
                        reset_rejection(game_piece_data)
                        # ( ... 딜레이 로직 ... )
                        last_response = getattr(
                            run_game_gui, "prev_last_response", "[INFO] 백의 이동 완료."
                        )
                        last_piece_dialogue = getattr(
                            run_game_gui, "prev_last_piece_dialogue", ""
                        )
                        selected_piece_id_to_show = getattr(
                            run_game_gui, "prev_selected_piece_id_to_show", None
                        )
                        draw_current_state(
                            screen,
                            game_board,
                            game_white_ids,
                            game_piece_data,
                            last_response,
                            last_piece_dialogue,
                            selected_piece_id_to_show,
                            force_move_count=force_move_remaining,
                        )
                        pygame.display.flip()
                        pygame.time.delay(100)

                    elif gui_result == "WHITE_MOVED_FORCED":
                        force_move_remaining -= 1
                        print(
                            f"✅ 백의 강제 이동 완료. (남은 횟수: {force_move_remaining})"
                        )
                        reset_rejection(game_piece_data)
                        # ( ... 딜레이 로직 ... )
                        last_response = getattr(
                            run_game_gui, "prev_last_response", "[INFO] 백의 이동 완료."
                        )
                        last_piece_dialogue = getattr(
                            run_game_gui, "prev_last_piece_dialogue", ""
                        )
                        selected_piece_id_to_show = getattr(
                            run_game_gui, "prev_selected_piece_id_to_show", None
                        )
                        draw_current_state(
                            screen,
                            game_board,
                            game_white_ids,
                            game_piece_data,
                            last_response,
                            last_piece_dialogue,
                            selected_piece_id_to_show,
                            force_move_count=force_move_remaining,
                        )
                        pygame.display.flip()
                        pygame.time.delay(100)

                    elif gui_result == "QUIT":
                        print("사용자가 게임을 중단했습니다. 메뉴로 복귀합니다.")
                        current_state = "MENU"

                # 3-2. ⚫ 흑 (Stockfish) 턴
                elif game_board.turn == chess.BLACK:
                    print("--- ⚫ 흑 턴: Stockfish 실행 중 ---")

                    success, lost_value = handle_black_turn()

                    if not success:
                        print("흑 턴 처리 실패. 게임을 종료합니다.")
                        break

                    if lost_value > 0:
                        morale -= lost_value
                        print(
                            f"🔥 기물 잃음! 사기 {lost_value} 감소. (현재 사기: {morale})"
                        )

                    print("✅ 흑의 이동 완료. 백 턴으로 전환.")

                    # ( ... 흑 턴 딜레이 로직 ... )
                    last_response = getattr(
                        run_game_gui, "prev_last_response", "[INFO] 흑의 이동 완료."
                    )
                    last_piece_dialogue = getattr(
                        run_game_gui, "prev_last_piece_dialogue", ""
                    )
                    selected_piece_id_to_show = getattr(
                        run_game_gui, "prev_selected_piece_id_to_show", None
                    )

                    delay_ms = 100
                    start_time = pygame.time.get_ticks()

                    while pygame.time.get_ticks() < start_time + delay_ms:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit(0)

                        draw_current_state(
                            screen,
                            game_board,
                            game_white_ids,
                            game_piece_data,
                            last_response,
                            last_piece_dialogue,
                            selected_piece_id_to_show,
                            force_move_count=force_move_remaining,
                        )
                        clock.tick(60)

                    pygame.event.clear()

    # 메인 루프 종료 시 Pygame 환경 최종 종료
    pygame.quit()


if __name__ == "__main__":
    try:
        main_game_loop()
    except Exception as e:
        print(f"치명적인 오류 발생: {e}")
        pygame.quit()
        sys.exit(1)
