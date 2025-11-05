import chess
from persuade import persuade_piece

# ⬇️⬇️⬇️ [이 부분 추가] ⬇️⬇️⬇️
# --- 기물 점수 상수 ---
PIECE_VALUES = {
    "P": 1,  # 폰
    "N": 3,  # 나이트
    "B": 3,  # 비숍
    "R": 5,  # 룩
    "Q": 9,  # 퀸
    "K": 0,  # 킹 (잡힐 일 없음)
}
# ⬆️⬆️⬆️ [추가 완료] ⬆️⬆️⬆️

# --- 게임 상태 상수 정의 (수정됨) ---
# 1. 게임 종료 상태
STATUS_CHECKMATE_WHITE_WINS = "CHECKMATE_WHITE_WINS"
STATUS_CHECKMATE_BLACK_WINS = "CHECKMATE_BLACK_WINS"
STATUS_STALEMATE = "STALEMATE"
STATUS_DRAW_INSUFFICIENT_MATERIAL = "DRAW_INSUFFICIENT_MATERIAL"
STATUS_DRAW_SEVENTYFIVE_MOVES = "DRAW_SEVENTYFIVE_MOVES"
STATUS_DRAW_FIVEFOLD_REPETITION = "DRAW_FIVEFOLD_REPETITION"
STATUS_DRAW_OTHER = "DRAW_OTHER"

# 2. 게임 진행 중 상태 (턴 정보 추가)
STATUS_ONGOING_WHITE_TURN = "ONGOING_WHITE_TURN"  # 백 턴 (진행 중)
STATUS_ONGOING_BLACK_TURN = "ONGOING_BLACK_TURN"  # 흑 턴 (진행 중)
STATUS_CHECK_WHITE_TURN = "CHECK_WHITE_TURN"  # 백 턴 (체크 상태)
STATUS_CHECK_BLACK_TURN = "CHECK_BLACK_TURN"  # 흑 턴 (체크 상태)


def get_game_status(board: chess.Board) -> str:
    """
    현재 체스 보드의 상태를 검사하여 문자열로 반환합니다.
    (수정됨: ONGOING 또는 CHECK 상태일 때 현재 턴 정보를 포함합니다.)
    """

    # 1. 게임 종료 여부 확인 (기존과 동일)
    outcome = board.outcome()
    if outcome:
        termination = outcome.termination
        winner = outcome.winner

        if termination == chess.Termination.CHECKMATE:
            return (
                STATUS_CHECKMATE_WHITE_WINS
                if winner == chess.WHITE
                else STATUS_CHECKMATE_BLACK_WINS
            )
        elif termination == chess.Termination.STALEMATE:
            return STATUS_STALEMATE
        elif termination == chess.Termination.INSUFFICIENT_MATERIAL:
            return STATUS_DRAW_INSUFFICIENT_MATERIAL
        elif termination == chess.Termination.SEVENTYFIVE_MOVES:
            return STATUS_DRAW_SEVENTYFIVE_MOVES
        elif termination == chess.Termination.FIVEFOLD_REPETITION:
            return STATUS_DRAW_FIVEFOLD_REPETITION
        else:
            return STATUS_DRAW_OTHER

    # 2. 게임이 종료되지 않았다면, 체크 상태인지 확인 (턴 정보 포함)
    if board.is_check():
        if board.turn == chess.WHITE:
            return STATUS_CHECK_WHITE_TURN  # 백이 체크 상태 (백 턴)
        else:
            return STATUS_CHECK_BLACK_TURN  # 흑이 체크 상태 (흑 턴)

    # 3. 체크도 아니고 종료도 아니면, 일반 진행 중 (턴 정보 포함)
    if board.turn == chess.WHITE:
        return STATUS_ONGOING_WHITE_TURN
    else:
        return STATUS_ONGOING_BLACK_TURN


def is_move_valid(board: chess.Board, uci_move: str) -> bool:
    """
    입력된 UCI 문자열이 현재 보드에서 유효한 '법적' 이동인지 검사합니다.
    """

    # 1. UCI 문자열 형식이 올바른지 시도
    try:
        move = chess.Move.from_uci(uci_move)
    except ValueError:
        return False

    # 2. 'board.legal_moves'에 해당 수가 포함되어 있는지 확인
    if move in board.legal_moves:
        return True
    else:
        return False


# ⬇️⬇️⬇️ [수정됨] ⬇️⬇️⬇️
def move_piece(
    board: chess.Board,
    white_ids: dict,
    piece_data: dict,
    uci_move: str,
    persuade: bool = False,
    persuasion_dialogue: str = "",
    morale: int = 1,
) -> (bool, str, int):  # <--- [반환값 수정] (bool, str, captured_value)
    """
    [수정] UCI 이동을 시도하고, (성공여부, 메시지, 잡은기물점수)를 반환합니다.
    """
    # ⬆️⬆️⬆️ [수정 완료] ⬆️⬆️⬆️

    # 1. 이동 유효성 검사 (형식 및 합법성)
    try:
        move = chess.Move.from_uci(uci_move)
    except ValueError:
        return (
            False,
            f"'{uci_move}'는 올바른 이동 형식이 아닙니다.",
            0,
        )  # <--- [수정] 0점 반환

    if move not in board.legal_moves:
        message = f"'{uci_move}'는 유효한 행마법이 아닙니다."
        if board.is_check():
            message = "현재 체크 상태입니다! 킹을 방어하는 수만 둘 수 있습니다."

        return False, message, 0  # <--- [수정] 0점 반환

    # 2. 이동할 기물의 ID 찾기
    location_to_id = {v: k for k, v in white_ids.items()}
    start_sq_name = chess.square_name(move.from_square)
    piece_id = location_to_id.get(start_sq_name)

    if not piece_id:
        return (
            False,
            f"'{start_sq_name}'의 아군 ID를 찾을 수 없습니다.",
            0,
        )  # <--- [수정] 0점 반환

    # ⬇️⬇️⬇️ [추가] ⬇️⬇️⬇️
    captured_value = 0  # 잡은 기물 점수 초기화
    # ⬆️⬆️⬆️ [추가 완료] ⬆️⬆️⬆️

    # 3. [persuade=False] 또는 [킹]인 경우: 설득 없이 즉시 이동
    is_king = piece_data[piece_id]["type"] == "K"

    if not persuade or is_king:

        message = ""
        if is_king:
            message = "킹은 설득이 필요 없습니다. 이동합니다."
        elif not persuade:
            message = "킹의 권한으로 강제 이동합니다."
        else:
            message = "설득 없이 이동합니다."

        # ⬇️⬇️⬇️ [추가] ⬇️⬇️⬇️
        # 이동 직전에 캡처 여부 확인
        if board.is_capture(move):
            captured_piece = board.piece_at(move.to_square)  # 흑 기물
            if captured_piece:
                symbol = captured_piece.symbol().upper()
                captured_value = PIECE_VALUES.get(symbol, 0)
        # ⬆️⬆️⬆️ [추가 완료] ⬆️⬆️⬆️

        # --- (기존 이동 로직) ---
        end_sq = chess.square_name(move.to_square)
        if board.is_castling(move):
            rook_start_sq, rook_end_sq = (None, None)
            if move.to_square == chess.G1:
                rook_start_sq, rook_end_sq = "h1", "f1"
            elif move.to_square == chess.C1:
                rook_start_sq, rook_end_sq = "a1", "d1"
            if rook_start_sq:
                rook_id = location_to_id.get(rook_start_sq)
                if rook_id:
                    white_ids[rook_id] = rook_end_sq
                    piece_data[rook_id]["current_square"] = rook_end_sq

        white_ids[piece_id] = end_sq
        piece_data[piece_id]["current_square"] = end_sq

        if move.promotion:
            new_type_symbol = chess.piece_symbol(move.promotion).upper()
            piece_data[piece_id]["type"] = new_type_symbol

        board.push(move)
        # --- (기존 로직 끝) ---

        return True, message, captured_value  # <--- [수정] 점수 반환

    # 4. [persuade=True] 및 [킹 외 기물]인 경우: 설득 시도
    stability, risk = get_square_safety(board, uci_move)

    decision, dialogue = persuade_piece(
        board,
        piece_data,
        white_ids,
        uci_move,
        persuasion_dialogue,
        stability,
        risk,
        morale,
    )

    # 4-3. 설득 결과 처리
    if decision == "수락":

        # ⬇️⬇️⬇️ [추가] ⬇️⬇️⬇️
        # 이동 직전에 캡처 여부 확인
        if board.is_capture(move):
            captured_piece = board.piece_at(move.to_square)  # 흑 기물
            if captured_piece:
                symbol = captured_piece.symbol().upper()
                captured_value = PIECE_VALUES.get(symbol, 0)
        # ⬆️⬆️⬆️ [추가 완료] ⬆️⬆️⬆️

        # --- (기존 이동 로직과 동일) ---
        end_sq = chess.square_name(move.to_square)
        if board.is_castling(move):
            rook_start_sq, rook_end_sq = (None, None)
            if move.to_square == chess.G1:
                rook_start_sq, rook_end_sq = "h1", "f1"
            elif move.to_square == chess.C1:
                rook_start_sq, rook_end_sq = "a1", "d1"
            if rook_start_sq:
                rook_id = location_to_id.get(rook_start_sq)
                if rook_id:
                    white_ids[rook_id] = rook_end_sq
                    piece_data[rook_id]["current_square"] = rook_end_sq

        white_ids[piece_id] = end_sq
        piece_data[piece_id]["current_square"] = end_sq

        if move.promotion:
            new_type_symbol = chess.piece_symbol(move.promotion).upper()
            piece_data[piece_id]["type"] = new_type_symbol

        board.push(move)
        # --- (기존 로직 끝) ---

        return True, dialogue, captured_value  # <--- [수정] 점수 반환

    else:  # (decision == "거부" or "오류")
        return False, dialogue, 0  # <--- [수정] 0점 반환


# ⬇️⬇️⬇️ [수정됨] ⬇️⬇️⬇️
def move_piece_black(
    board: chess.Board, white_ids: dict, piece_data: dict, uci_move: str
) -> (bool, int):  # <--- [반환값 수정] (bool, lost_value)
    """
    [수정] 흑(Stockfish)의 이동을 처리하고 (성공여부, 잃은기물점수)를 반환합니다.
    """
    # ⬆️⬆️⬆️ [수정 완료] ⬆️⬆️⬆️

    # 1. 흑 턴이 맞는지 확인
    if board.turn == chess.WHITE:
        return (False, 0)  # <--- [수정]

    # 2. 이동 유효성 검사
    try:
        move = chess.Move.from_uci(uci_move)
    except ValueError:
        return (False, 0)  # <--- [수정]

    if move not in board.legal_moves:
        return (False, 0)  # <--- [수정]

    # ⬇️⬇️⬇️ [추가] ⬇️⬇️⬇️
    lost_value = 0  # 잃은 기물 점수 초기화
    # ⬆️⬆️⬆️ [추가 완료] ⬆️⬆️⬆️

    # 3. 캡처(잡기)가 발생했는지 확인
    if board.is_capture(move):
        captured_sq_name = None

        if board.is_en_passant(move):
            captured_file = chess.square_file(move.to_square)
            captured_rank = chess.square_rank(move.from_square)
            captured_sq_index = chess.square(captured_file, captured_rank)
            captured_sq_name = chess.square_name(captured_sq_index)
        else:
            captured_sq_name = chess.square_name(move.to_square)

        # 4. 잡힌 칸(captured_sq_name)에 백 기물이 있었는지 확인
        captured_id = None
        for piece_id, location in white_ids.items():
            if location == captured_sq_name:
                captured_id = piece_id
                break

        # 5. [핵심 수정] 백색 기물이 잡혔다면, 상태 변경 및 점수 계산
        if captured_id:
            white_ids[captured_id] = None

            if captured_id in piece_data:
                piece_data[captured_id]["current_square"] = None

                # ⬇️⬇️⬇️ [추가] ⬇️⬇️⬇️
                # 잃은 기물의 점수 계산
                lost_piece_type = piece_data[captured_id]["type"]
                lost_value = PIECE_VALUES.get(lost_piece_type, 0)
                print(
                    f"흑에게 {captured_id}({lost_piece_type}) 기물을 잃음. (점수: {lost_value})"
                )
                # ⬆️⬆️⬆️ [추가 완료] ⬆️⬆️⬆️

    # 6. 보드에 이동 적용
    board.push(move)

    return (True, lost_value)  # <--- [수정] 성공여부와 점수 반환


def get_square_safety(board: chess.Board, uci_move: str) -> (int, int):
    """
    특정 이동의 '도착지' 칸에 대한 안정도와 위험도를 계산합니다.
    """
    # (코드 로직 동일)
    try:
        move = chess.Move.from_uci(uci_move)
    except ValueError:
        return (0, 0)

    to_square = move.to_square
    from_square = move.from_square

    ally_color = chess.WHITE
    opponent_color = chess.BLACK

    opponent_attackers = board.attackers(opponent_color, to_square)
    risk = len(opponent_attackers)

    allied_attackers = board.attackers(ally_color, to_square)
    allied_attackers.discard(from_square)
    stability = len(allied_attackers)

    return (stability, risk)
