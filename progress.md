# mrs-llm 프로젝트 진행 상황

## 프로젝트 개요
COHERENT (LLM 기반 이종 멀티 로봇 시스템) 를 현실 기반으로 재구현하는 프로젝트.
- 참고 레포: mrkeee/coherent
- 목표: 시뮬레이션 기반 COHERENT를 현실 로봇 팔(UR RTDE) 기반으로 재구현

## 현재 구조
```
mrs/
├── main.py           # 전체 루프 (while not done: oracle.step())
├── LLM/
│   ├── base.py       # RobotBase 부모 클래스
│   ├── LLM.py        # OpenAI API 호출 클래스
│   ├── agent.py      # Robot Arm Agent 클래스
│   └── oracle.py     # Oracle (중앙 컨트롤러) 클래스
├── config/
│   └── config.yaml   # LLM 설정
pyproject.toml
```

## 아키텍처 설계 결정사항

### 클래스 구조
- `RobotBase` — 부모 클래스 (공통 관측, LLM)
    - `Oracle(RobotBase)` — 태스크 관리, subtask 생성, Agent 지시
    - `Agent(RobotBase)` — 로봇 팔 제어, 행동 결정

### LLM API 방식
- OpenAI Responses API 사용
- CoT 3단계 추론: `previous_response_id`로 체이닝
- 장기 대화 히스토리: `conversation_id`로 관리 (Oracle이 소유)
- 흐름: CoT 1번 → 2번 → 3번(Judge) → 최종 결과만 conversation에 추가

### 실행 흐름
```
main.py (전체 루프)
    ↓
oracle.step() (한 사이클)
    ↓ subtask 생성
agent.step() (한 행동)
    ↓ CoT 3단계 추론
로봇 실행 (MCP 서버로 분리 예정)
    ↓ 피드백
conversation에 결과 추가
```

### 로봇 제어
- URController (UR RTDE 기반) → 별도 MCP 서버로 분리 예정
- mrs-llm 레포에는 로봇 제어 코드 없음
- Tool → MCP 순서로 단계적 구현 예정

## 구현 완료된 것들

### LLM.py
- OpenAI Responses API 호출
- `generate(prompt, conversation_id, previous_response_id)`
- `calculate_cost()` — 모델별 비용 계산
- `@backoff.on_exception` — API 실패 시 재시도

### agent.py
- `AFFORDANCE_MAP` — 물체별 properties/states 정의 (하드코딩, 추후 교체)
- `get_available_plans(detected_objects)` — rule 기반 action list 생성
- `step()` — CoT 3단계 추론 흐름 (골격 구현)
    - N 추론 (반복 횟수)
    - check_progress()
    - get_available_plans()
    - 1단계: CoT (YES I CAN / SORRY I CANNOT)
    - 2단계: 행동 선택
    - 3단계: Judge 검증
    - conversation에 최종 결과 추가

### oracle.py
- `_init_conversation()` — 태스크 시작 시 conversation 자동 생성
- `@backoff.on_exception` — 연결 실패 시 재시도
- `conversation_id` 관리

### base.py
- `RobotBase` — 공통 부모 클래스

## 미구현 / 해결 필요한 것들

### 별도 파악 필요한 3가지 항목
1. **Task 완료 판단** — 현실에서 어떻게 할지 미정
2. **Action List 동적 생성** — Affordance 공부 필요 (논문 서치 계획 중)
   - 키워드: Object Affordance Detection, Visual Affordance Learning, LASO, AffordanceNet
3. **obs 정보 → LLM 텍스트 변환** — GroundingDINO + SAM 기존 코드 있음, 변환 방식 파악 필요

### oracle.step() 구현
- get_observation() 구현 필요 (3번 항목)
- prompt 구성 (obs 텍스트 변환 필요)
- agent.step() 호출 및 피드백 수신
- → 위 3가지 항목 해결 후 구현 가능

### agent.py
- get_observation() 구현 필요 (GroundingDINO + SAM)
- 로봇 제어 실행 → MCP 서버로 대체 예정

### MCP 서버
- URController 기반 로봇 제어 MCP 서버 별도 구축 예정
- 기존 URController 코드 있음

## 다음에 파악해야 할 것들
- 현실 기반 구현에서 추가로 필요한 것들 파악 (아직 미발견 항목 있을 수 있음)
- GroundingDINO + SAM obs → LLM 텍스트 변환 방식
- Affordance 관련 논문 서치
- Task 완료 판단 방법 설계
- Oracle prompt 현실 기반으로 재설계
- Agent prompt obs 정보 형태 결정

## 참고사항
- COHERENT와의 주요 차이점
    - 그래프 기반 시뮬레이터 → 현실 로봇 (RTDE + 카메라)
    - properties 미리 라벨링 → AFFORDANCE_MAP (임시 하드코딩)
    - 완전 정보 → 카메라 기반 부분 관측
    - get_env_info.py (시뮬레이터) → MCP 서버 (로봇 제어)