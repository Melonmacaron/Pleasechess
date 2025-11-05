import ollama
import chess
import os
from dotenv import load_dotenv
import time

load_dotenv()

POD_ID = os.getenv("POD_ID")

RUNPOD_OLLAMA_URL = f"https://{POD_ID}-11434.proxy.runpod.net"


def reset_rejection(piece_data):
    for k in piece_data.keys():
        piece_data[k]["rejection_count_this_turn"] = 0


def query_ollama(prompt: list, model: str = "EEVE-Korean-10.8B:latest") -> str:
    """
    Ollama API를 호출합니다.
    (수정됨: 네트워크 오류 발생 시 5회 재시도)
    """
    client = ollama.Client(host=RUNPOD_OLLAMA_URL)

    max_retries = 5
    last_exception = None

    for attempt in range(max_retries):
        try:
            response = client.chat(model=model, messages=prompt)
            # 1. 성공 시 즉시 결과 반환
            return response["message"]["content"]
        except Exception as e:
            # 2. 실패 시 로그 출력 및 1초 대기
            print(f"Ollama LLM 호출 오류 (시도 {attempt + 1}/{max_retries}): {e}")
            last_exception = e
            time.sleep(1)  # 1초 대기 후 재시도

    # 3. 5회 모두 실패한 경우, 예외를 발생시킴
    print(f"Ollama 호출 {max_retries}회 재시도 모두 실패.")
    raise last_exception


# --- LLM 프롬프트에 사용할 기물 한글 이름 ---
PIECE_TYPE_MAP = {
    "P": "폰",
    "N": "나이트",
    "B": "비숍",
    "R": "룩",
    "Q": "퀸",
    "K": "킹",
}


def persuade_piece(
    board: chess.Board,
    piece_data: dict,
    white_ids: dict,
    move_uci: str,
    persuasion_dialogue: str,
    stability: int,
    risk: int,
    morale: int,
) -> (str, str):
    """
    LLM을 호출하여 특정 기물이 왕의 명령(이동)을 수락할지 거부할지 결정합니다.
    (수정됨: 형식 오류 및 네트워크 오류 시 "오류"를 반환하고 history에 저장하지 않음)
    """

    # 1. 이동하는 기물 ID 찾기
    location_to_id = {v: k for k, v in white_ids.items()}
    start_square = chess.Move.from_uci(move_uci).from_square
    start_square_name = chess.square_name(start_square)

    piece_id = location_to_id.get(start_square_name)

    if not piece_id:
        return (
            "거부",  # (이것은 LLM 오류가 아닌 시스템 오류이므로 '거부' 유지)
            f"(오류) '{start_square_name}' 위치의 아군 기물 ID를 찾을 수 없습니다.",
        )

    # 2. 설득할 기물의 정보 가져오기
    target_piece = piece_data.get(piece_id)
    if not target_piece:
        return ("거부", f"(오류) '{piece_id}'의 상세 데이터를 찾을 수 없습니다.")

    # 3. LLM에게 전달할 프롬프트 생성
    # ( ... 코드 동일 ... )
    piece_type_symbol = target_piece["type"]
    piece_type_kr = PIECE_TYPE_MAP.get(piece_type_symbol, piece_type_symbol)
    current_fen = board.fen()
    to_square_name = chess.square_name(chess.Move.from_uci(move_uci).to_square)

    situation_prompt = f"""
### 현재 상황 ###
너는 {piece_type_kr} '{piece_id}'이다.
현재 너의 위치는 '{start_square_name}'이다.
아군 전체의 사기는 {morale}이다.
현재 전체 전장 상황(FEN): {current_fen}

### 왕의 명령 ###
왕(플레이어)이 너에게 '{to_square_name}'(으)로 이동하라고 명령했다. (이동: {move_uci})
이 이동의 위험도(적의 공격)는 {risk}이고, 안정도(아군 방어)는 {stability}이다.

왕이 다음과 같이 설득한다:
"{persuasion_dialogue}"

### 너의 결정 ###
너의 성격(페르소나)과 위 상황을 종합적으로 고려하여 이 명령을 [수락]할지 [거부]할지 결정하라.
너의 계급({piece_type_kr})에 맞는 말투를 사용하라. (폰은 비굴하거나 충성스럽게, 퀸은 위엄 있게 등)
반드시 다음 형식으로만 대답해야 한다:
[결정][너의 대답]

### 출력예시:
[수락][알겠습니다, 폐하! 가문의 영광을 위해!]
[거부][제 목숨이 위험합니다. 이 명령은 따를 수 없습니다.]
"""

    # 4. LLM 호출 준비
    messages_history = list(target_piece["history"])
    messages_history.append({"role": "user", "content": situation_prompt})

    # 5. OLLAMA LLM 호출
    try:
        llm_output = query_ollama(messages_history).strip()

        # 6. LLM 응답 파싱 및 반환
        if llm_output.startswith("[수락]"):
            decision = "수락"
            dialogue = llm_output[len("[수락]") :].strip()
            target_piece["rejection_count_this_turn"] = 0

        elif llm_output.startswith("[거부]"):
            decision = "거부"
            dialogue = llm_output[len("[거부]") :].strip()
            target_piece["rejection_count_this_turn"] += 1

        else:
            # --- [수정됨] ---
            # LLM이 형식을 지키지 않았을 경우 "오류"로 처리
            decision = "오류"
            dialogue = f"(응답 형식 오류) {llm_output}"
            # 거절 카운트를 올리지 않음
            # --- [수정 완료] ---

        # 7. 대화 내역(History) 업데이트
        # --- [수정됨] ---
        # "오류"가 아닐 때(수락 또는 거부)만 history에 저장
        if decision == "수락" or decision == "거부":
            target_piece["history"].append(
                {"role": "user", "content": situation_prompt}
            )
            target_piece["history"].append({"role": "assistant", "content": llm_output})
        # --- [수정 완료] ---

        return (decision, dialogue)

    except Exception as e:
        # [수정 없음]
        # query_ollama가 5회 재시도 후에도 실패하면 "오류" 반환
        # history는 저장되지 않음
        return (
            "오류",
            f"({piece_id}가 혼란에 빠졌습니다. 명령을 이해하지 못했습니다. 오류: {e})",
        )
