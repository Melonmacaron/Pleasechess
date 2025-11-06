# Please Chess
 
 AI 기반으로 체스말에 자아를 부여하고 이에 따라 왕의 명령을 선택적으로 수락하거나 거부하면서 진행되는 체스게임입니다. 사용자는 왕이되어 기본적인 체스의 룰에 기반하여 게임을 하되 자아를 가진 말을 설득하여 그들을 통솔하고 승리하여야 합니다.

 ## 프로젝트 개요

 이 프로젝트는 체스 말이 자아를 가지고 있다면 어떨까라는 상상에서 시작되었습니다. 체스에는 희생을 통한 전술이 존재합니다. 하지만 실제 전쟁에서 희생을 통한 전술에는 제약이 많습니다. 만약 체스말이 자아를 가지면 이런 전술들이 제약되고 이를 그냥 희생을 할 수 없는 체스에서 그치는 것이 아니라 대화를 통해 설득하는 과정에서 재미를 느낄 수 있지 않을까 하여 해당 게임을 제작하게 되었습니다.

 ## 프로젝트 구조

 ```📁 main_game/
├── 📄 README.MD
├── 📁 game/
│   ├── 📁 images/
│   │   ├── 📄 이미지 파일들...
│   ├── 📄 black_moving.py
│   ├── 📄 chess_gui.py
│   ├── 📄 chess_logic.py
│   ├── 📄 custom_game_screen.py
│   ├── 📄 gui_utils.py
│   ├── 📄 main_menu.py
│   ├── 📄 main.py
│   ├── 📄 persona.py
│   ├── 📄 persuade.py
│   ├── 📄 settings_screen.py
│   └── 📄 start_chess.py
└── 📁 stockfish/
    └── 📄 stockfish-windows-x86-64-avx2.exe
```

## 기술 스택
### 개발 환경

 <img src="https://img.shields.io/badge/VSCode-007ACC?style=for-the-badge&logo=visual-studio-code&logoColor=white">
 <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=Python&logoColor=white">

 ### 체스 로직
   <img src="https://img.shields.io/badge/Python chess-E6E6FA?style=for-the-badge&logo=&logoColor=white">

   <img src="https://img.shields.io/badge/Python Stockfish-3700AB?style=for-the-badge&logo=&logoColor=white">
   <img src="https://img.shields.io/badge/Stockfish-4B0082?style=for-the-badge&logo=&logoColor=white">

### AI 및 LLM
<img src="https://img.shields.io/badge/Runpod-3700AB?style=for-the-badge&logo=Runpod&logoColor=white">
  <img src="https://img.shields.io/badge/Ollama-000000?style=for-the-badge&logo=Ollama&logoColor=white">
  <img src="https://img.shields.io/badge/EEVE Korean 10.8B-36454F?style=for-the-badge&logo=EEVE&logoColor=white">

### GUI
  <img src="https://img.shields.io/badge/Pygame-FF8C00?style=for-the-badge&logo=Pygame&logoColor=white">

## 실행 준비 
### requirements.txt의 패키지 설치
  ``` pip install -r requirements.txt ```

### Runpod 서버 구성
- 기본적으로 Runpod서버는 EEVE 모델의 호스트로만 사용할 것이기 때문에 다음과 같이 구성한다.
1. Runpod에 네트워크 볼륨 생성 (20GB정도면 충분)
2. 해당 네트워크 볼륨을 이용해서 GPU를 포함한 Pod 생성(GPU로는 A4000정도면 충분)
3. 네트워크를 실행후 \workspace 에 start.sh를 복사
4. Runpod에서 Edit Pod을 선택 후 start command에 <br> ``` /bin/bash /workspace/start.sh ``` 입력
5. Port를 11434 에 22로 설정후 환경변수에 OLLAMA_HOST / 0.0.0.0으로 설정
6. log에 ```sleep infinity```가 보이면 준비 완료

### 환경변수 설정후 실행
1. .env파일을 /main_game/game 안에 생성후 <br>POD_ID={runpod인스턴스 아이디} 로 설정 
2. python /main_game/game/main.py로 실행

## 이미지 데이터 출처
[Lichess-github](https://github.com/lichess-org/lila)