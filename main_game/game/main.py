import chess
import os
import sys
import pygame 
from start_chess import initialize_game
from chess_logic import *
from persuade import *
from black_moving import StockfishEngine
# draw_current_state를 임포트하려면 chess_gui.py에 이 함수가 정의되어 있어야 합니다.
from chess_gui import run_game_gui, WINDOW_WIDTH, WINDOW_HEIGHT, draw_current_state 

# --- 1. 환경 및 엔진 초기화 ---

# [필수] 다운로드한 Stockfish .exe 파일의 '전체 경로'를 입력하세요.
# (이 경로는 이미 사용자님의 로컬 환경에 맞게 설정되어 있다고 가정합니다.)
STOCKFISH_PATH = r"D:\Library\바탕화면\Game_project\Pleasechess\main_game\stockfish\stockfish-windows-x86-64-avx2.exe"

try:
    # StockfishEngine 초기화
    sf_engine = StockfishEngine(executable_path=STOCKFISH_PATH, skill_level=10)
    if sf_engine.stockfish is None:
        print("Stockfish 엔진 로드 실패. 프로그램을 종료합니다.")
        sys.exit(1)
except Exception as e:
    print(f"Stockfish 초기화 중 오류 발생: {e}")
    sys.exit(1)


# --- 2. 게임 상태 및 데이터 초기화 (전역 변수 유지) ---
print("--- 🚀 자아 체스 게임 시작 ---")
# 전역 변수: game_board, game_white_ids, game_piece_data
game_board, game_white_ids, game_piece_data = initialize_game(fen=None) 
morale = 1  # 사기 점수 초기화


# --- 3. 핸들러 함수 정의 ---

def handle_player_move(uci_move: str, persuasion_dialogue: str) -> (str, str):
    """
    GUI에서 호출될 실제 백 기물 이동 처리 로직.
    """
    global game_board, game_white_ids, game_piece_data, morale
    
    # 1. 유효성 검사 (GUI에서 이미 처리하지만, 안전을 위해 다시 확인)
    try:
        if chess.Move.from_uci(uci_move) not in game_board.legal_moves:
            return "거부", "킹의 명령: 해당 이동은 현재 규칙상 유효하지 않습니다."
    except ValueError:
        return "오류", "킹의 명령: 잘못된 UCI 형식입니다."

    # 2. 안전도/위험도 계산 (필요하다면 주석 해제)
    # stability, risk = get_square_safety(game_board, uci_move)

    # 3. move_piece (설득 포함) 호출
    decision, dialogue = move_piece(
        game_board,
        game_white_ids,
        game_piece_data,
        uci_move,
        persuade=True,  # 설득 활성화
        persuasion_dialogue=persuasion_dialogue,
        morale=morale
    )

    return decision, dialogue


def handle_black_turn():
    """
    흑(Stockfish) 턴의 이동을 처리합니다.
    """
    global game_board, game_white_ids, game_piece_data
    
    # 1. Stockfish 최적의 수 계산
    stockfish_move = sf_engine.get_best_move(game_board)

    if stockfish_move:
        # 2. 이동 적용 (흑 기물은 설득 없이 바로 이동)
        if move_piece_black(game_board, game_white_ids, game_piece_data, stockfish_move):
            return True
        else:
            print(f"❌ 흑 기물 이동 오류: {stockfish_move}")
            return False
    else:
        print("❌ Stockfish가 수를 찾지 못했습니다.")
        return False


# --- 4. 게임 종료 후 딜레이 및 최종 화면 표시 함수 ---
def delay_game_over(screen, clock, final_message: str):
    """
    게임 종료 메시지를 표시하고 일정 시간 대기하는 루프.
    """
    # [수정] 전역 변수 선언 추가
    global game_board, game_white_ids, game_piece_data
    
    delay_ms = 5000 # 게임 종료 후 5초 대기
    start_time = pygame.time.get_ticks()
    
    # GUI 상태는 모두 초기화된 것으로 간주 (선택된 기물 없음)
    selected_piece_id_to_show = None
    last_piece_dialogue = "" # 최종 결과이므로 기물 응답은 비움
    
    # 최종 보드 상태를 한 번 그리고 시작
    draw_current_state(
        screen, 
        game_board, 
        game_white_ids, 
        game_piece_data, 
        final_message, # 최종 메시지를 last_response로 전달
        last_piece_dialogue,
        selected_piece_id_to_show
    )
    
    while pygame.time.get_ticks() < start_time + delay_ms:
        # Pygame 이벤트 큐를 비워서 창이 멈추지 않도록 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 
            # ESC나 아무 키/클릭을 누르면 바로 종료 가능하도록 처리
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return 
                
        # 딜레이 동안 화면 유지 및 갱신 (60 FPS)
        clock.tick(60)

# --- 5. 메인 게임 루프 ---

def main_game_loop():
    global game_board, game_white_ids, game_piece_data
    
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT)) 
    clock = pygame.time.Clock()
    
    while True:
        # 1. 매 루프 시작 시 보드 상태 확인
        board_state = get_game_status(game_board)
        
        # 2. [핵심] 게임 종료 확인 및 처리 (턴 로직보다 상위)
        is_game_over = board_state in [
            STATUS_CHECKMATE_WHITE_WINS, 
            STATUS_CHECKMATE_BLACK_WINS, 
            STATUS_STALEMATE, 
            STATUS_DRAW_INSUFFICIENT_MATERIAL, 
            STATUS_DRAW_SEVENTYFIVE_MOVES, 
            STATUS_DRAW_FIVEFOLD_REPETITION, 
            STATUS_DRAW_OTHER
        ]

        if is_game_over:
            print(f"--- 🏁 게임 종료 --- (최종 결과: {board_state})")
            
            # 최종 메시지 설정
            if board_state == STATUS_CHECKMATE_WHITE_WINS:
                final_message = "[게임 종료] 체크메이트! 백색 기물 승리!"
            elif board_state == STATUS_CHECKMATE_BLACK_WINS:
                final_message = "[게임 종료] 체크메이트! 흑색 기물 승리."
            elif board_state == STATUS_STALEMATE or \
                 board_state == STATUS_DRAW_INSUFFICIENT_MATERIAL or \
                 board_state == STATUS_DRAW_SEVENTYFIVE_MOVES or \
                 board_state == STATUS_DRAW_FIVEFOLD_REPETITION or \
                 board_state == STATUS_DRAW_OTHER:
                final_message = "[게임 종료] 무승부!"
            else:
                final_message = "[게임 종료] 게임이 종료되었습니다."
            
            # 최종 화면 표시 및 5초 대기 후 루프 종료
            delay_game_over(screen, clock, final_message)
            break
        
        # 3. 턴 처리 로직 시작 (종료되지 않았을 때만 실행)

        # 5-1. ⚪ 백 (플레이어) 턴: GUI 대기
        if game_board.turn == chess.WHITE:
            print(f"--- ⚪ 백 턴: {board_state} ---")
            
            # 흑 턴의 잔상을 제거하기 위해 화면을 한 번 지웁니다.
            screen.fill(pygame.Color(0, 0, 0)) 
            pygame.display.flip()
            
            # [수정된 run_game_gui 호출]
            gui_result = run_game_gui(
                game_board, 
                game_white_ids, 
                game_piece_data, 
                sf_engine, 
                handle_player_move,
                screen, 
                clock # U+00A0 오류 제거됨
            )

            if gui_result == "WHITE_MOVED":
                print("✅ 백의 수락 및 이동 완료. 흑 턴으로 전환.")
                
                # 백 턴 성공 직후 화면 안정화 (딜레이 직전에 하이라이트 제거된 화면 표시)
                last_response = getattr(run_game_gui, 'prev_last_response', "[INFO] 백의 이동 완료.")
                last_piece_dialogue = getattr(run_game_gui, 'prev_last_piece_dialogue', "")
                selected_piece_id_to_show = getattr(run_game_gui, 'prev_selected_piece_id_to_show', None)
                
                draw_current_state(
                    screen, 
                    game_board, 
                    game_white_ids, 
                    game_piece_data, 
                    last_response, 
                    last_piece_dialogue,
                    selected_piece_id_to_show
                )
                pygame.display.flip()
                
                # 딜레이를 100ms로 변경
                pygame.time.delay(100) 

            elif gui_result == "QUIT":
                print("사용자가 게임을 종료했습니다.")
                break
                
        # 5-2. ⚫ 흑 (Stockfish) 턴: 자동 진행
        elif game_board.turn == chess.BLACK:
            print("--- ⚫ 흑 턴: Stockfish 실행 중 ---")
            
            # 흑의 이동을 처리하고 보드를 업데이트
            if not handle_black_turn():
                print("흑 턴 처리 실패. 게임을 종료합니다.")
                break
            
            print("✅ 흑의 이동 완료. 백 턴으로 전환.")
            
            # 흑 턴 완료 후 결과를 사용자에게 보여주기 위한 딜레이 (100ms로 단축)
            last_response = getattr(run_game_gui, 'prev_last_response', "[INFO] 흑의 이동 완료.")
            last_piece_dialogue = getattr(run_game_gui, 'prev_last_piece_dialogue', "")
            selected_piece_id_to_show = getattr(run_game_gui, 'prev_selected_piece_id_to_show', None)
            
            delay_ms = 100 
            start_time = pygame.time.get_ticks()
            
            while pygame.time.get_ticks() < start_time + delay_ms:
                # 이벤트 큐를 비워 창이 멈추지 않도록 합니다.
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit(0)
                        
                # 흑 턴 완료 보드와 이전 메시지를 화면에 다시 그림
                draw_current_state(
                    screen, 
                    game_board, 
                    game_white_ids, 
                    game_piece_data, 
                    last_response, 
                    last_piece_dialogue,
                    selected_piece_id_to_show
                )
                clock.tick(60) 

            # 다음 백 턴 GUI 호출을 위해 이벤트 큐를 비움
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