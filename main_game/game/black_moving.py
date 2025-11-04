import chess
from stockfish import Stockfish


class StockfishEngine:
    def __init__(self, executable_path: str, skill_level: int = 10):
        """
        Stockfish 엔진을 초기화합니다.

        Args:
            executable_path (str): 'stockfish.exe' 또는 'stockfish' 파일의
                                     전체 경로입니다.
            skill_level (int, optional): 스톡피쉬의 레벨 (0~20). 기본값은 10.
        """
        try:
            self.stockfish = Stockfish(path=executable_path)
            self.stockfish.set_skill_level(skill_level)
            print(f"✅ Stockfish 엔진 로드 성공. (레벨: {skill_level})")

            if not self.stockfish.is_move_correct("e2e4"):
                raise Exception("엔진 응답 없음")

        except FileNotFoundError:
            print(f"❌ 오류: Stockfish 실행 파일을 찾을 수 없습니다.")
            print(f"입력된 경로: {executable_path}")
            print("Stockfish (https://stockfishchess.org/download/)를 다운로드하고")
            print("정확한 .exe 파일의 전체 경로를 입력해야 합니다.")
            self.stockfish = None
        except Exception as e:
            print(f"❌ Stockfish 로드 중 알 수 없는 오류 발생: {e}")
            self.stockfish = None

    def get_best_move(self, board: chess.Board) -> str | None:
        """
        현재 보드 상태에서 Stockfish의 최적의 수를 받아옵니다.
        """
        if not self.stockfish:
            print("Stockfish 엔진이 초기화되지 않았습니다.")
            return None

        if board.turn == chess.WHITE:
            print("경고: 흑 턴이 아닌데 Stockfish가 호출되었습니다.")
            return None

        self.stockfish.set_fen_position(board.fen())
        best_move_uci = self.stockfish.get_best_move_time(1000)  # 1초

        if not best_move_uci:
            print("Stockfish가 수를 반환하지 못했습니다.")
            return None

        return best_move_uci
