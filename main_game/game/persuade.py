import ollama

# --- 설정 (사용자가 지정한 모델명) ---
OLLAMA_MODEL_NAME = 'EEVE-Korean-10.8B' 
# ---

def generate_ollama_prompt(piece_id: str, piece_data: dict, uci_move: str, persuasion_attempt: str, calculated_risks: dict) -> tuple:
    """
    LLM에 전달할 시스템 및 사용자 메시지 리스트를 생성합니다.
    """
    
    # 1. 시스템 메시지 (성격, 거절 횟수 반영 및 행동 규칙 정의)
    
    # 현재까지의 누적 거절 횟수 계산 (history에서 [Decline] 메시지 개수)
    # piece_data['history']의 첫 번째 요소는 시스템 메시지이므로, 인덱스 1부터 assistant 메시지를 확인합니다.
    current_rejection_count = sum(
        1 for msg in piece_data[piece_id]['history'][1:] if msg.get('role') == 'assistant' and msg.get('content', '').startswith("[Decline]")
    )
    
    base_profile = piece_data[piece_id]['profile']

    # 거절 횟수에 따른 성격 변화 규칙을 시스템 메시지에 주입 (예시)
    if '자존심이 강한 기물이다' in base_profile and current_rejection_count > 0:
        rejection_effect = f"당신은 현재까지 {current_rejection_count}번 거절했습니다. 당신의 판단에 확신을 갖고 주인의 전략을 더욱 엄격하게 평가하십시오. 자존심을 지키세요."
    elif '경제적 어려움' in base_profile and current_rejection_count >= 2:
        rejection_effect = f"당신은 현재까지 {current_rejection_count}번 거절했습니다. 추가 거절은 가족의 생계를 위협하는 '해고(희생)'로 이어질 수 있습니다. 불안감을 반영하십시오."
    else:
        rejection_effect = f"당신의 누적 거절 횟수는 {current_rejection_count}회입니다. 이전 대화 기록을 참고하십시오."


    system_content = f"""
당신은 체스 기물인 '{piece_id}'입니다. 당신의 고유 성격은 다음과 같습니다:
{base_profile}

--- 상황 및 판단 기준 ---
{rejection_effect}
객관적 위험도는 다음과 같습니다: 위험도(흑 공격 수): {calculated_risks['risk_score']} / 안전도(백 방어 수): {calculated_risks['safety_score']}

당신의 임무는 주인의 요청에 대해 당신의 성격, 대화 맥락, 그리고 객관적인 위험도를 종합하여 **동의(Accept)**하거나 **거절(Decline)**하는 것입니다.

**응답 규칙:**
1. 당신의 응답은 반드시 **[Accept]** 또는 **[Decline]** 태그로 시작해야 합니다.
2. 태그 뒤에는 **당신의 성격과 상황**을 반영한 설득력 있는 이유를 한국어로 작성해야 합니다.
"""

    # 2. 사용자 메시지 (요청 및 객관적 정보)
    risk_info_block = f"""
--- 분석 정보 ---
- 요청된 이동: {uci_move}
- 위험 수준: **{calculated_risks['risk_level']}**
- 점수 변화: {calculated_risks['value_change']}점
---
"""
    
    user_request_content = f"""
{risk_info_block}

**주인의 설득 문구:**
"{persuasion_attempt}"

당신은 이 요청에 동의합니까?
"""
    
    # 3. 전체 메시지 리스트 구성: [System] + [Past User/Assistant] + [Current User]
    
    messages_to_send = [{'role': 'system', 'content': system_content}]
    
    # 과거 대화 기록 추가 (시스템 메시지를 제외한 과거의 user/assistant 메시지)
    messages_to_send.extend(piece_data[piece_id]['history'][1:]) 
    
    user_message = {'role': 'user', 'content': user_request_content}
    messages_to_send.append(user_message)
    
    return messages_to_send, user_message


def request_move_to_ollama(piece_id: str, piece_data: dict, uci_move: str, persuasion_attempt: str, calculated_risks: dict) -> tuple:
    """
    Ollama EEVE 모델을 호출하여 기물의 동의/거절 여부를 결정하고 메시지를 반환합니다.
    
    Args:
        piece_id (str): 설득하려는 기물의 고유 ID.
        piece_data (dict): 기물의 데이터.
        uci_move (str): 요청된 이동.
        persuasion_attempt (str): 플레이어의 설득 문구.
        calculated_risks (dict): 위험도 정보.

    Returns:
        tuple: (decision: str, response_text: str, user_message: dict, llm_response_message: dict)
    """
    
    messages_to_send, current_user_message = generate_ollama_prompt(
        piece_id, piece_data, uci_move, persuasion_attempt, calculated_risks
    )
    
    try:
        # Ollama API 호출
        response = ollama.chat(
            model=OLLAMA_MODEL_NAME,
            messages=messages_to_send
        )

        llm_response_text = response['message']['content'].strip()
        
        # 응답 파싱
        if llm_response_text.startswith("[Accept]"):
            decision = "동의"
        elif llm_response_text.startswith("[Decline]"):
            decision = "거절"
        else:
            decision = "불명확" 
        
        # 대화 기록 업데이트를 위한 LLM 응답 메시지 준비
        llm_response_message = {'role': 'assistant', 'content': llm_response_text}
        
        return decision, llm_response_text, current_user_message, llm_response_message

    except Exception as e:
        error_message = f"Ollama API 호출 중 오류 발생. 서버가 실행 중인지 확인하세요: {e}"
        # 오류 시 기본적으로 거절 처리합니다.
        return "오류", error_message, current_user_message, {'role': 'assistant', 'content': f"[Decline] 통신 오류로 인해 명령을 수행할 수 없습니다: {e}"}