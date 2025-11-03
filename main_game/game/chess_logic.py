import chess
import random
import ollama # LLM 상호작용을 위해 필요

# --- 1. 초기 상수 및 데이터 정의 ---

# A. 기물 타입별 성격/상황 설정 목록 (킹 제외)
SITUATION = {
    "QUEEN": [
        "나는 가장 강력하고 자존심이 강한 기물이다. 반복적인 설득에도 자존심을 굽히지 않는다.",
        "나는 대담하고 전진적인 성향이다. 공격적인 수를 좋아하며, 뒤로 물러나는 것을 모욕으로 여긴다."
    ],
    "ROOK": [
        "나는 매우 보수적이며 직선적인 이동만을 신뢰한다. 가족(다른 룩)의 안전을 중시한다.",
        "나는 과거 전쟁 영웅이었으며 명예를 중시한다. 승리를 위해 기꺼이 희생할 수 있지만, 명분 없는 퇴각은 수치로 여긴다."
    ],
    "BISHOP": [
        "나는 전략가이자 지식인이다. 데이터와 확률에 기반하여 판단하며, 감성적인 설득은 통하지 않는다.",
        "나는 교단의 지도자로서, 신성한 움직임(대각선) 외의 다른 움직임을 경계한다. '정의로운 희생'에는 동의할 수 있다."
    ],
    "KNIGHT": [
        "나는 기회주의자이자 도박꾼이다. 높은 위험이라도 보상이 크다면 기꺼이 감수한다. 반복적인 거절은 지루하다.",
        "나는 충직하고 단순하다. 주인의 명령에 쉽게 복종하지만, 예상치 못한 위험에는 겁을 먹는다."
    ],
    "PAWN": [
        "나는 매우 보수적이고 위험을 극도로 회피한다. 가정 경제가 어려워 무사히 퇴근하는 것이 가장 큰 목표다.",
        "나는 어리숙하고 주인의 명령에 쉽게 동조하는 폰이다. 설득이 잘 통한다.",
        "나는 미혼이고 세상 물정 모르는 젊은 폰이다. 출세(퀸 승격)에 대한 열망이 강하다. 위험하더라도 큰 기회가 따른다면 수락할 의향이 있다."
    ]
}

# B. 백색 기물 ID 정의 (K1 제외)
# B. 백색 기물 ID 및 초기 위치 정의
WHITE_PIECE_IDS_WITH_SQUARE = [
    ("KING", "K1", "e1"), ("QUEEN", "Q1", "d1"), 
    ("ROOK", "R1", "a1"), ("ROOK", "R2", "h1"), 
    ("BISHOP", "B1", "c1"), ("BISHOP", "B2", "f1"),
    ("KNIGHT", "N1", "b1"), ("KNIGHT", "N2", "g1"),
    ("PAWN", "P1", "a2"), ("PAWN", "P2", "b2"), ("PAWN", "P3", "c2"), ("PAWN", "P4", "d2"),
    ("PAWN", "P5", "e2"), ("PAWN", "P6", "f2"), ("PAWN", "P7", "g2"), ("PAWN", "P8", "h2"),
]

# --- 2. 초기화 함수 ---
def create_initial_game_data(fen: str = None):
    """
    FEN으로 보드를 초기화하고, 킹을 제외한 기물에 랜덤 성격을 할당하며,
    모든 기물의 현재 위치를 추적할 초기 데이터를 생성합니다.
    """
    # 보드 초기화
    board = chess.Board(fen) if fen else chess.Board()
        
    piece_data = {}
    assigned_situations = {ptype: list(SITUATION.get(ptype, [])) for ptype in SITUATION}
    
    for piece_type, piece_id, initial_square in WHITE_PIECE_IDS_WITH_SQUARE:
        selected_profile = ""
        
        if piece_id != "K1":
            # 킹을 제외한 기물에 랜덤 성격 할당
            if piece_type in assigned_situations and assigned_situations[piece_type]:
                selected_profile = random.choice(assigned_situations[piece_type])
                assigned_situations[piece_type].remove(selected_profile)
            else:
                selected_profile = SITUATION[piece_type][-1] if piece_type in SITUATION else ""

            system_message = {'role': 'system', 'content': selected_profile}
            
            piece_data[piece_id] = {
                "type": piece_type,
                "profile": selected_profile,    
                "history": [system_message],
                "rejection_count_this_turn": 0,
                "current_square": initial_square
            }
        else:
            # K1 별도 처리
            piece_data["K1"] = {
                "type": "KING",
                "profile": "플레이어 자신(설득 불필요)",
                "history": [],
                "rejection_count_this_turn": 0,
                "current_square": initial_square
            }
    
    return {
        "board": board,
        "piece_data": piece_data,
    }

# 보드의 상태 확인하는 코드
def check_game_state(current_board: chess.Board) -> str:
    """현재 보드 상태(체크메이트, 스테일메이트 등)를 확인합니다."""
    if current_board.is_checkmate():
        return "Checkmate"
    elif current_board.is_stalemate():
        return "Stalemate"
    elif current_board.is_insufficient_material():
        return "Draw (Insufficient Material)"
    elif current_board.can_claim_threefold_repetition():
        return "Draw (Threefold Repetition)"
    elif current_board.is_check():
        return "Check"
    else:
        return "Ongoing"

# 움직임이 합법적인가를 탐지
def is_move_legal(board_state: chess.Board, uci_move: str) -> bool:
    """UCI 형식의 움직임이 체스 규칙상 합법적인지 확인합니다."""
    try:
        move = chess.Move.from_uci(uci_move)
        return move in board_state.legal_moves
    except:
        return False

# --- 3. 체스 로직 및 데이터 추적 함수 ---

def get_piece_id_from_square(square_name: str, board_state: chess.Board, piece_data: dict) -> str or None:
    """
    주어진 칸에 있는 백색 기물의 고유 ID (P1, R1 등)를 찾습니다.
    (piece_data의 'current_square' 정보를 사용합니다.)
    """
    square = chess.parse_square(square_name)
    piece = board_state.piece_at(square)
    
    if not piece or piece.color != chess.WHITE:
        return None 
    
    piece_symbol = piece.symbol().upper() 
    
    for piece_id, data in piece_data.items():
        if data.get("current_square") == square_name:
            # 보드의 기물 심볼과 데이터의 기물 타입이 일치하는지 확인 (예: 'P' == 'PAWN'[0])
            if data['type'].upper()[0] == piece_symbol:
                return piece_id
            
    return None


def update_piece_location(piece_id: str, new_square: str, piece_data: dict):
    """
    기물의 움직임이 확정된 후, piece_data에 저장된 기물의 위치를 업데이트합니다.
    (잡힌 기물은 메인 루프에서 처리되므로, 여기서는 새 위치만 기록합니다.)
    """
    if piece_id in piece_data:
        piece_data[piece_id]["current_square"] = new_square
        
def calculate_risk_and_safety(board_state: chess.Board, uci_move: str) -> dict:
    """
    움직임의 위험도와 안전도를 계산합니다.
    - 위험도: 도착 칸을 공격하는 흑 기물의 수
    - 안전도: 도착 칸을 보호하는 백 기물의 수
    """
    if not is_move_legal(board_state, uci_move):
        # 불법적인 수라면 계산 불가
        return {"risk_level": "불가능", "value_change": 0, "safety_score": 0, "risk_score": 99, "fen": board_state.fen()}

    move = chess.Move.from_uci(uci_move)
    target_square = move.to_square # 도착 칸

    # 1. 안전도 (Safety Score) 계산: 도착 칸을 지키는 아군 기물의 수
    # 공격하는 기물의 수를 세기 위해 board.attacks(square)를 사용합니다.
    
    # 아군 기물 (백색)
    safety_count = len(board_state.attackers(chess.WHITE, target_square))
    safety_score = safety_count # 안전도는 보호 기물 수 그대로 사용

    # 2. 위험도 (Risk Score) 계산: 도착 칸을 공격하는 상대 기물의 수
    # 상대 기물 (흑색)
    risk_count = len(board_state.attackers(chess.BLACK, target_square))
    risk_score = risk_count # 위험도는 공격 기물 수 그대로 사용
    
    # 3. 가치 변화 (Value Change) 계산
    value_change = 0 
    if board_state.is_capture(move):
        captured_piece = board_state.piece_at(target_square).piece_type
        # 기물 가치(폰=1, 나이트/비숍=3, 룩=5, 퀸=9)를 반영하여 점수 변화 계산
        value_change = {1: 1, 2: 3, 3: 3, 4: 5, 5: 9}.get(captured_piece, 1)

    # 4. 위험 수준 문자열 변환 (LLM이 직관적으로 이해하도록)
    # 위험도(공격 수) > 안전도(방어 수)라면 위험하다고 판단
    if risk_score > safety_score:
        risk_level = "매우 위험함 (공격 우세)"
    elif risk_score == safety_score and risk_score > 0:
        risk_level = "균형 위험 (동수 교환 가능)"
    else:
        risk_level = "낮음 (방어 우세 또는 공격 없음)"

    # 예외: 킹이 공격받는 위치로 이동하면 최우선적으로 치명적
    board_state.push(move)
    if board_state.is_check():
        risk_level = "치명적 (자살 행위)"
        risk_score = 99 # 극도의 위험을 표시
    board_state.pop() # 보드 상태 복원

    return {
        "risk_level": risk_level, 
        "value_change": value_change,
        "safety_score": safety_score, # 보호 기물 수
        "risk_score": risk_score,     # 공격 기물 수
        "fen": board_state.fen()
    }