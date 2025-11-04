import chess
from start_chess import *
from chess_logic import *
from persuade import *
from black_moving import StockfishEngine

# --- 1. Stockfish 엔진 초기화 ---
# [필수] 다운로드한 Stockfish .exe 파일의 '전체 경로'를 입력하세요.
# 예: "C:/Users/chris/Desktop/stockfish/stockfish.exe"
# 예: "./stockfish-ubuntu" (같은 폴더에 있을 경우)
STOCKFISH_PATH = r"C:\Users\chris\Desktop\game_project\Pleasechess\main_game\stockfish\stockfish-windows-x86-64-avx2.exe"  # <-- [필수] 이 경로를 수정하세요.

sf_engine = StockfishEngine(executable_path=STOCKFISH_PATH, skill_level=10)

if sf_engine.stockfish is None:
    print("Stockfish 엔진 로드에 실패하여 프로그램을 종료합니다.")
    exit()

# --- 2. 게임 변수 초기화 ---
print("--- 🚀 게임을 시작합니다 ---")
fen = None  # None이면 기본 보드
game_board, game_white_ids, game_piece_data = initialize_game(fen)
morale = 1  # (향후 기물 교환 시 이 값을 변경하는 로직 추가 가능)


# --- 3. 메인 게임 루프 ---
while True:
    # 3-1. 현재 보드 상태 출력
    print_board_with_ids(game_board, game_white_ids)

    # 3-2. 게임 상태 확인
    board_state = get_game_status(game_board)
    print(f"\n현재 상태: {board_state}")

    # 3-3. 게임 종료 조건 확인
    if "ONGOING" not in board_state and "CHECK" not in board_state:
        print(f"--- 🏁 게임 종료 ---")
        print(f"결과: {board_state}")
        break

    # 3-4. ⚪ 백 (플레이어) 턴
    if (
        board_state == STATUS_ONGOING_WHITE_TURN
        or board_state == STATUS_CHECK_WHITE_TURN
    ):
        print("--- ⚪ 백 (플레이어) 턴 ---")

        # [수락/이동]이 성공할 때까지 입력을 반복
        while True:
            # 1. 이동 입력
            uci_move = input("이동할 수를 입력하세요 (예: e2e4): ").strip()

            if uci_move.lower() == "exit":
                print("게임을 종료합니다.")
                exit()

            # 2. (선택적) 유효성 사전 검사 (persuade_piece에서도 검사하지만, 미리 하면 LLM 호출을 아낄 수 있음)
            if not is_move_valid(game_board, uci_move):
                print(
                    f"'{uci_move}'는 유효한 이동이 아닙니다. (규칙 위반, 핀, 체크 미방어 등)"
                )
                continue  # 다시 입력받기

            # 3. 설득 대사 입력 (킹을 움직이는 경우 이 대사는 무시됨)
            persuasion_dialogue = input("설득 대사를 입력하세요: ").strip()

            # 4. move_piece (설득 포함) 호출
            decision, dialogue = move_piece(
                game_board,
                game_white_ids,
                game_piece_data,
                uci_move,
                persuade=True,  # <-- 설득 활성화
                persuasion_dialogue=persuasion_dialogue,
                morale=morale,
            )

            # 5. 결과 출력
            print(f"응답: {dialogue}")

            # 6. 턴 종료 조건
            if decision == "수락" or decision == True:  # (True는 킹이 이동했을 때)
                print("이동이 수락되었습니다.")
                break  # 백 턴 종료 (while True 탈출)

            elif decision == "오류":
                print("LLM 오류가 발생했습니다. 다른 수를 시도하세요.")
                # 턴이 종료되지 않음

            else:  # (decision == "거부" or decision == False)
                print("이동이 거부되었습니다. 다른 수를 시도하거나 재설득하세요.")
                # 턴이 종료되지 않음

    # 3-5. ⚫ 흑 (Stockfish) 턴
    elif (
        board_state == STATUS_ONGOING_BLACK_TURN
        or board_state == STATUS_CHECK_BLACK_TURN
    ):
        print("--- ⚫ 흑 (Stockfish) 턴 ---")

        stockfish_move = sf_engine.get_best_move(game_board)

        if stockfish_move:
            print(f"Stockfish 선택: {stockfish_move}")
            # 흑의 이동은 설득 없이 즉시 실행
            move_piece_black(
                game_board, game_white_ids, game_piece_data, stockfish_move
            )
        else:
            print("Stockfish가 수를 결정하지 못했습니다. (게임 오류)")
            break  # 메인 루프 탈출
