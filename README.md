# pygame5 - Python Tetris 프로젝트

## 1) 프로젝트 개요
이 프로젝트는 **Python + Pygame**으로 구현한 테트리스 게임입니다. 
현재 코드는 단일 파일(`tet.py`) 구조로, 기본적인 테트리스 규칙(블록 이동/회전/낙하/줄 삭제/점수/레벨/게임오버)을 포함하고 있습니다.

- 보드 크기: 10 x 20
- 테트로미노: I, O, T, L, J, S, Z
- 입력: 방향키(이동/회전/소프트드랍), 스페이스(하드드랍), ESC(종료), ENTER(게임오버 후 재시작)

---

## 2) 구현 기술(Tech Stack)

### 언어/런타임
- **Python 3.9+** 권장

### 그래픽/입력
- **Pygame 2.x**
  - 게임 창 생성 (`pygame.display.set_mode`)
  - 키보드 입력 처리 (`pygame.event.get`, `KEYDOWN`)
  - 도형/텍스트 렌더링 (`pygame.draw.rect`, `pygame.font.SysFont`)
  - 프레임 제어 (`pygame.time.Clock`)

### 표준 라이브러리
- `random`: 다음 블록 랜덤 생성
- `sys`: 프로그램 종료 처리
- `typing`: 타입 힌트 (`List`, `Tuple`, `Dict`, `Optional`)

---

## 3) 현재 코드 구조

단일 실행 파일(`tet.py`) 안에 핵심 구성 요소가 포함되어 있습니다.

- `rotate_matrix(mat)`
  - 4x4 매트릭스 형태의 블록을 시계 방향 회전

- `Piece`
  - 블록의 위치/형태/색상 관리
  - 회전, 좌표 계산, 복사 기능 제공

- `Board`
  - 잠긴 블록(`locked`)과 현재 격자(`grid`) 관리
  - 충돌 판정, 줄 삭제, 게임오버 판정 담당

- `TetrisGame`
  - 게임 루프, 이벤트 처리, 점수/레벨, 렌더링 UI 전체 담당

---

## 4) 필요한 라이브러리 및 설치 방법

### 필수 라이브러리
- `pygame`

### 설치
```bash
python -m pip install --upgrade pip
python -m pip install pygame
```

### 선택(권장) 개발 도구
코드 품질 향상을 위해 아래 도구를 함께 사용하는 것을 권장합니다.

```bash
python -m pip install black ruff mypy
```

- `black`: 코드 포맷터
- `ruff`: 린터/정적 분석
- `mypy`: 타입 체크

---

## 5) 실행 방법

프로젝트 루트에서 아래 명령어를 실행합니다.

```bash
python tet.py
```

---

## 6) 조작 방법

- `←` / `→` : 좌우 이동
- `↓` : 한 칸 하강
- `↑` : 회전
- `Space` : 하드 드랍
- `ESC` : 게임 종료
- `ENTER` : 게임오버 화면에서 재시작

---

## 7) 점수/레벨 규칙

- 줄 삭제 시 점수 증가: `score += (삭제 줄 수^2) * 100`
- 레벨 계산: `level = 1 + score // 500`
- 낙하 속도 증가: 레벨이 오를수록 자동 낙하 간격 감소(최소 150ms)

---

## 8) 향후 확장 제안

- 홀드(Hold) 기능
- 고스트 피스(Ghost Piece)
- 콤보/백투백 점수 시스템
- 사운드 효과(BGM/SE)
- 랭킹 저장(로컬 JSON)
- 2인 멀티플레이(로컬 분할 화면 또는 네트워크)

자세한 멀티플레이 구현 계획은 `todo.md`를 참고하세요.
