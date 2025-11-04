import chess
from persuade import persuade_piece

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

    Args:
        board (chess.Board): 검사할 chess.Board 객체

    Returns:
        str: 게임 상태 (e.g., "CHECKMATE_WHITE_WINS", "ONGOING_WHITE_TURN", "CHECK_BLACK_TURN")
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

    Args:
        board (chess.Board): 현재 체스 보드
        uci_move (str): 검사할 이동 (예: "e2e4", "e7e8q")

    Returns:
        bool: 이동이 유효하면 True, 그렇지 않으면 False
    """

    # 1. UCI 문자열 형식이 올바른지 시도
    try:
        move = chess.Move.from_uci(uci_move)
    except ValueError:
        # "e2e9"처럼 형식이 아예 잘못된 경우
        return False

    # 2. 'board.legal_moves'에 해당 수가 포함되어 있는지 확인
    #    (행마법, 핀, 체크 방어 등이 모두 고려됨)
    if move in board.legal_moves:
        return True
    else:
        # 행마법 위반, 핀, 체크 미방어 등
        return False

# (다른 import 및 get_game_status, is_move_valid 함수가 여기에 있다고 가정)


def move_piece(
    board: chess.Board,
    white_ids: dict,
    piece_data: dict,
    uci_move: str,
    persuade: bool = False,
    persuasion_dialogue: str = "",
    morale: int = 1,
) -> (bool, str):
    """
    UCI 이동을 시도하고, 성공하면 모든 관련 데이터를 업데이트합니다.
    'persuade=True'인 경우, 킹 외 기물은 설득 과정을 거칩니다.

    Args:
        board (chess.Board): 현재 chess.Board 객체
        white_ids (dict): 기물 ID와 위치 맵 (e.g., {'P1': 'a2'})
        piece_data (dict): 기물 상세 데이터 맵 (e.g., {'P1': {...}})
        uci_move (str): "e2e4"와 같은 UCI 이동 문자열
        persuade (bool, optional): True이면 설득 로직을 실행. 기본값은 False.
        persuasion_dialogue (str, optional): 설득 대사.
        morale (int, optional): 현재 사기.

    Returns:
        (bool, str): (성공 여부, 부가 메시지/대사)
                     (True, "이동 성공") / (True, "킹은 설득이 필요 없습니다.") / (True, "[수락] 대사")
                     (False, "유효하지 않은 수입니다.") / (False, "[거부] 대사")
    """

    # 1. 이동 유효성 검사 (형식 및 합법성)
    try:
        move = chess.Move.from_uci(uci_move)
    except ValueError:
        return False, f"'{uci_move}'는 올바른 이동 형식이 아닙니다."

    if move not in board.legal_moves:
        # 유효하지 않은 이유 추정
        if board.is_check():
            return (
                False,
                "현재 체크 상태입니다! 킹을 방어하는 수(피하거나, 막거나, 잡는 수)만 둘 수 있습니다.",
            )
        start_square_name = chess.square_name(move.from_square)
        piece = board.piece_at(move.from_square)
        if piece is None:
            return False, f"'{start_square_name}' 칸에는 움직일 기물이 없습니다."
        return (
            False,
            f"'{uci_move}'는 유효한 행마법이 아니거나, 해당 기물이 핀(pinned)에 걸려 킹이 위험해질 수 있습니다.",
        )

    # 2. 이동할 기물의 ID 찾기
    location_to_id = {v: k for k, v in white_ids.items()}
    start_sq_name = chess.square_name(move.from_square)
    piece_id = location_to_id.get(start_sq_name)

    if not piece_id:
        # legal_moves 검사를 통과했다면 발생해서는 안 됨
        return False, f"'{start_sq_name}'의 아군 ID를 찾을 수 없습니다."

    # 3. [persuade=False] 또는 [킹]인 경우: 설득 없이 즉시 이동
    # (piece_data에서 기물 타입을 확인하여 킹인지 검사)
    is_king = piece_data[piece_id]["type"] == "K"

    if not persuade or is_king:
        message = (
            "킹은 설득이 필요 없습니다. 이동합니다."
            if is_king
            else "설득 없이 이동합니다."
        )

        # --- (기존 이동 로직) ---
        end_sq = chess.square_name(move.to_square)
        if board.is_castling(move):
            rook_start_sq, rook_end_sq = (None, None)
            if move.to_square == chess.G1:  # e1g1 (킹사이드)
                rook_start_sq, rook_end_sq = "h1", "f1"
            elif move.to_square == chess.C1:  # e1c1 (퀸사이드)
                rook_start_sq, rook_end_sq = "a1", "d1"

            if rook_start_sq:
                rook_id = location_to_id.get(rook_start_sq)
                if rook_id:
                    # 룩(Rook)의 위치 정보 업데이트
                    white_ids[rook_id] = rook_end_sq
                    piece_data[rook_id]["current_square"] = rook_end_sq

        # 킹(또는 일반 기물) 위치 업데이트
        white_ids[piece_id] = end_sq
        piece_data[piece_id]["current_square"] = end_sq

        # 폰 승급 처리
        if move.promotion:
            new_type_symbol = chess.piece_symbol(move.promotion).upper()
            piece_data[piece_id]["type"] = new_type_symbol

        board.push(move)
        # --- (기존 로직 끝) ---

        return True, message

    # 4. [persuade=True] 및 [킹 외 기물]인 경우: 설득 시도

    # 4-1. 안정도/위험도 계산
    # (get_square_safety 함수가 이 파일에 이미 존재한다고 가정)
    stability, risk = get_square_safety(board, uci_move)

    # 4-2. 설득 함수 호출
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

        return True, dialogue  # 성공 (대사와 함께)

    else:  # (decision == "거부")
        return False, dialogue  # 실패 (대사와 함께)


def move_piece_black(
    board: chess.Board, white_ids: dict, piece_data: dict, uci_move: str
) -> bool:
    """
    흑(Stockfish)의 이동을 처리합니다.
    (수정됨) 백 기물을 잡았을 때, 해당 기물의 위치를 'captured'로 변경합니다.
    """

    # 1. 흑 턴이 맞는지 확인
    if board.turn == chess.WHITE:
        return False

    # 2. 이동 유효성 검사
    try:
        move = chess.Move.from_uci(uci_move)
    except ValueError:
        return False

    if move not in board.legal_moves:
        return False

    # 3. 캡처(잡기)가 발생했는지 확인
    if board.is_capture(move):
        captured_sq_name = None

        if board.is_en_passant(move):
            # 앙파상
            captured_file = chess.square_file(move.to_square)
            captured_rank = chess.square_rank(move.from_square)
            captured_sq_index = chess.square(captured_file, captured_rank)
            captured_sq_name = chess.square_name(captured_sq_index)
        else:
            # 일반 캡처
            captured_sq_name = chess.square_name(move.to_square)  # e.g., 'd5'

        # 4. 잡힌 칸(captured_sq_name)에 백 기물이 있었는지 확인
        captured_id = None
        for piece_id, location in white_ids.items():
            if location == captured_sq_name:
                captured_id = piece_id  # e.g., 'P5'
                break

        # 5. [핵심 수정] 백색 기물이 잡혔다면, 상태를 'captured'로 변경
        if captured_id:
            # white_ids 맵에서 해당 기물 위치를 'captured'로 변경
            white_ids[captured_id] = None

            # piece_data 맵에서 해당 기물 위치를 'captured'로 변경
            if captured_id in piece_data:
                piece_data[captured_id]["current_square"] = None

    # 6. 보드에 이동 적용
    board.push(move)

    return True


def get_square_safety(board: chess.Board, uci_move: str) -> (int, int):
    """
    특정 이동의 '도착지' 칸에 대한 안정도와 위험도를 계산합니다.

    Args:
        board (chess.Board): 현재 체스 보드
        uci_move (str): "e2e4"와 같은 UCI 이동 문자열

    Returns:
        (int, int): (안정도, 위험도) 튜플
                    안정도: 도착 칸을 공격하는 아군 기물 수 (움직이는 기물 제외)
                    위험도: 도착 칸을 공격하는 적군 기물 수
    """

    try:
        move = chess.Move.from_uci(uci_move)
    except ValueError:
        # 유효하지 않은 UCI 형식이면 (0, 0) 반환
        return (0, 0)

    # 1. 이동할 칸(to_square)과 출발한 칸(from_square)
    to_square = move.to_square
    from_square = move.from_square

    # 2. 아군(현재 턴)과 적군 색상
    ally_color = chess.WHITE
    opponent_color = chess.BLACK

    # 3. 위험도 계산 (적군이 to_square를 공격하는 수)
    opponent_attackers = board.attackers(opponent_color, to_square)
    risk = len(opponent_attackers)

    # 4. 안정도 계산 (아군이 to_square를 공격하는 수)
    allied_attackers = board.attackers(ally_color, to_square)

    # 5. [핵심] 아군 공격자 목록에서 '움직이는 기물 자신(from_square)'을 제외
    #    (e.g., R-a1이 a5로 갈 때, a1은 a5의 공격자로 포함되므로 제외해야 함)
    #    .discard()는 해당 요소가 없어도 오류를 일으키지 않습니다.
    allied_attackers.discard(from_square)

    stability = len(allied_attackers)

    return (stability, risk)
