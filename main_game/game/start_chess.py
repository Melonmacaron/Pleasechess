from persona import persona_list, NAME_LIST  # NAME_LIST를 persona.py에서 함께 임포트
import random
import chess
import copy


def initialize_board(fen: str = None) -> chess.Board:
    """
    FEN 문자열이 주어지면 해당 FEN으로 보드를 초기화합니다.
    주어지지 않으면 기본 시작 보드로 초기화합니다.
    """
    if fen:
        try:
            board = chess.Board(fen)
            return board
        except ValueError:
            print(f"오류: 유효하지 않은 FEN 문자열입니다. '{fen}'")
            print("기본 보드로 초기화합니다.")
            return chess.Board()
    else:
        # FEN이 제공되지 않으면 기본값으로 시작
        return chess.Board()

def get_piece_id_at_square(white_ids: dict, square_name: str) -> str | None:
    """
    주어진 칸 이름(e.g., 'a2')에 위치한 백색 기물의 ID(e.g., 'P1')를 찾습니다.
    """
    # white_ids는 {ID: square_name} 형태입니다.
    for piece_id, location in white_ids.items():
        if location == square_name:
            return piece_id
    return None

def assign_white_piece_ids(board: chess.Board) -> dict:
    """
    보드 상태를 기반으로 '백색 기물'에만 고유 ID를 할당합니다.
    A1 -> H8 순서로 스캔하여 ID를 부여합니다.

    반환:
        white_piece_map: {'R1': 'a1', 'N1': 'b1', 'P1': 'a2', ...}
    """
    white_piece_map = {}

    # 백색 기물 종류별 카운터
    white_counters = {
        chess.PAWN: 1,
        chess.KNIGHT: 1,
        chess.BISHOP: 1,
        chess.ROOK: 1,
        chess.QUEEN: 1,
        chess.KING: 1,
    }

    # chess.SQUARES는 A1 (0) 부터 H8 (63) 까지 순서대로 된 리스트입니다.
    for square in chess.SQUARES:
        piece = board.piece_at(square)

        # 기물이 존재하고, 그 기물이 백색일 경우에만 처리
        if piece and piece.color == chess.WHITE:
            piece_type = piece.piece_type
            piece_symbol = chess.piece_symbol(piece_type).upper()
            square_name = chess.square_name(square)

            count = white_counters[piece_type]
            piece_id = f"{piece_symbol}{count}"

            # ID를 키로, 위치를 값으로 저장
            white_piece_map[piece_id] = square_name

            white_counters[piece_type] += 1

    return white_piece_map


def print_board_with_ids(board: chess.Board, white_id_map: dict):
    """
    보드판을 시각화합니다.
    백색 기물은 ID로 (e.g., P1, N1), 흑색 기물은 심볼로 (e.g., p, n) 표시합니다.

    Args:
        board (chess.Board): 현재 chess 보드 객체
        white_id_map (dict): {'R1': 'a1', ...} 형태의 백색 기물 ID 맵
    """

    # ID 맵을 뒤집어서 '위치'를 키로 하는 맵을 만듭니다. (검색 속도 향상)
    # e.g., {'a1': 'R1', 'b1': 'N1', 'a2': 'P1', ...}
    location_map = {v: k for k, v in white_id_map.items()}

    print("\n--- ⚪⚫ 보드 ID 시각화 ---")
    print("   a  b  c  d  e  f  g  h")  # (공백 수정됨)
    print(" +-------------------------+")

    # Rank 8 (인덱스 7) 부터 Rank 1 (인덱스 0) 까지 역순으로
    for rank_idx in range(7, -1, -1):
        line = f"{rank_idx + 1}|"  # Rank 숫자 (8, 7, ..., 1)

        # File A (인덱스 0) 부터 File H (인덱스 7) 까지
        for file_idx in range(8):
            # 64칸 인덱스 계산 (e.g., a8 = 56, h1 = 7)
            square_idx = chess.square(file_idx, rank_idx)
            square_name = chess.square_name(square_idx)

            cell_content = ""

            # 1. 백색 기물 ID가 있는지 확인
            if square_name in location_map:
                cell_content = location_map[square_name]
            else:
                # 2. 흑색 기물 또는 빈칸 확인
                piece = board.piece_at(square_idx)
                if piece:
                    cell_content = piece.symbol()  # 흑색 기물 (e.g., 'p', 'n')
                else:
                    cell_content = "."  # 빈 칸

            # 3. 셀 포맷팅 (모든 셀을 3칸 너비로 맞춤)
            line += f" {cell_content: <2}"  # :<2 는 2칸 너비, 왼쪽 정렬

        line += " |"
        print(line)

    print(" +-------------------------+")


def initialize_piece_data(
    board: chess.Board, white_id_map: dict, persona_list_dict: dict
) -> dict:
    """
    백색 기물 ID 맵을 기반으로 각 기물의 상세 데이터와 '이름'을 초기화합니다.
    (수정됨: NAME_LIST에서 이름을 가져오고, 이름을 중복 없이 할당합니다.)
    """
    piece_data = {}

    available_personas = copy.deepcopy(persona_list_dict)
    # NAME_LIST를 복사하여 사용 후 제거할 수 있게 합니다.
    available_names_by_type = copy.deepcopy(NAME_LIST) 

    for piece_id, square_name in white_id_map.items():

        # 1. 'type' (심볼) 가져오기
        square_index = chess.SQUARE_NAMES.index(square_name)
        piece = board.piece_at(square_index)

        # 'P1' -> 'P', 'N2' -> 'N'
        piece_symbol = chess.piece_symbol(piece.piece_type).upper()

        # 2. 'profile' (랜덤 페르소나 텍스트) 할당
        selected_profile = None

        if piece_symbol in available_personas and available_personas[piece_symbol]:
            profile_list = available_personas[piece_symbol]
            selected_profile = profile_list.pop(random.randrange(len(profile_list)))
        else:
            print(
                f"경고: {piece_symbol} 타입의 페르소나가 부족하거나 없습니다. (ID: {piece_id})"
            )
            selected_profile = f"기본 페르소나 ({piece_id})"

        # 3. [추가] 클래스별 랜덤 이름 할당
        selected_name = f"{piece_id} NoName" # 기본값
        if piece_symbol in available_names_by_type and available_names_by_type[piece_symbol]:
            name_list = available_names_by_type[piece_symbol]
            # 목록에서 이름을 뽑은 후 제거하여 중복을 방지
            name_index = random.randrange(len(name_list))
            selected_name = name_list.pop(name_index) 
        
        # 4. 'history' 초기화
        initial_history = [{"role": "system", "content": selected_profile}]

        # 5. piece_data 딕셔너리에 추가
        piece_data[piece_id] = {
            "type": piece_symbol, 
            "profile": selected_profile, 
            "history": initial_history,
            "rejection_count_this_turn": 0,
            "current_square": square_name,
            "name": selected_name, # <-- 이름 추가
        }

    return piece_data


def initialize_game(fen: str = None) -> (chess.Board, dict, dict):
    """
    게임을 초기화하고 보드, 백색 기물 ID 맵, 기물 상세 데이터를 반환합니다.

    Args:
        fen (str, optional): FEN 문자열.

    Returns:
        tuple: (board, white_ids, piece_data)
               - board: chess.Board 객체
               - white_ids: {'P1': 'a2', ...} 형태의 백색 기물 ID 맵
               - piece_data: {'P1': {...}, ...} 형태의 기물 상세 데이터
    """

    # 1. 보드 초기화
    board = initialize_board(fen)

    # 2. 백색 기물 ID 할당
    white_ids = assign_white_piece_ids(board)

    # 3. 기물 상세 데이터(piece_data) 초기화
    piece_data = initialize_piece_data(board, white_ids, persona_list)

    return board, white_ids, piece_data