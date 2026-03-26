from mrs.LLM.base import RobotBase
from mrs.LLM.LLM import LLM

AFFORDANCE_MAP = {
    "object_name": {
        "properties": ["GRABABLE", "SURFACES", "CONTAINERS"],
        "states": ["CLOSED"]  # 초기 상태
    },
}

class Agent(RobotBase):
    def __init__(self, llm: LLM, agent_id: int):
        self.llm = llm
        self.id = agent_id
        self.remaining_count = None
        self.grabbed_object = None

    def get_observation(self):
        # GroundingDINO + SAM으로 물체 인식
        # RTDE로 로봇 상태 읽기
        pass

    def check_progress(self):
        return self.remaining_count == 0
    
    def get_available_plans(self, detected_objects):
        available_plans = []

        for obj in detected_objects:
            props = AFFORDANCE_MAP.get(obj['name'], {}).get('properties', [])
            states = AFFORDANCE_MAP.get(obj['name'], {}).get('states', [])

            if self.grabbed_object is None:
                if 'GRABABLE' in props:
                    available_plans.append(f"[grab] <{obj['name']}>")
                if 'CONTAINERS' in props and 'CLOSED' in states:
                    available_plans.append(f"[open] <{obj['name']}>")
                if 'CONTAINERS' in props and 'OPEN' in states:
                    available_plans.append(f"[close] <{obj['name']}>")

            if self.grabbed_object is not None:
                if 'SURFACES' in props:
                    available_plans.append(f"[puton] <{self.grabbed_object}> on <{obj['name']}>")
                if 'CONTAINERS' in props and 'OPEN' in states:
                    available_plans.append(f"[putinto] <{self.grabbed_object}> into <{obj['name']}>")

        plans = ""
        for i, plan in enumerate(available_plans):
            plans += f"{chr(ord('A') + i)}. {plan}\n"

        return plans, available_plans

    def step(self, instruction, conversation_id):
        # 0. N 추론
        n_prompt = f"How many times does the following task need to be repeated? Answer with only a number.\nTask: {instruction}"
        n_output, _ = self.llm.generate(n_prompt)
        self.remaining_count = int(n_output[0].strip())

        while not self.check_progress():
            # 1. 완료 체크
            # check_progress()가 False면 계속 진행

            # 2. 실행 가능한 action list 정의
            detected_objects = self.get_observation()
            plans, available_plans = self.get_available_plans(detected_objects)

            # 3. 1단계 추론 - CoT
            with open('prompt/robot_arm_prompt.txt', 'r') as f:
                agent_prompt = f.read()
            agent_prompt = agent_prompt.replace('#INSTRUCTION#', instruction)
            agent_prompt = agent_prompt.replace('#ACTIONLIST#', plans)

            output1, id1 = self.llm.generate(agent_prompt)

            if output1[0].upper().startswith("YES I CAN"):
                # 4. 2단계 추론 - 행동 선택
                output2, id2 = self.llm.generate(
                    "Answer with only one best next action in the list of available actions. So the answer is",
                    previous_response_id=id1
                )

                # 5. 3단계 추론 - Judge 검증
                with open('prompt/judge_prompt.txt', 'r') as f:
                    judge_prompt = f.read()
                judge_prompt = judge_prompt.replace('#INSTRUCTION#', instruction)
                judge_prompt = judge_prompt.replace('#PLAN#', output2[0])

                output3, id3 = self.llm.generate(
                    judge_prompt,
                    previous_response_id=id2
                )

                # 최종 결과 conversation에 추가
                self.llm.generate(
                    output3[0],
                    conversation_id=conversation_id
                )

            elif output1[0].upper().startswith("SORRY I CANNOT"):
                # Oracle에게 피드백
                self.llm.generate(
                    output1[0],
                    conversation_id=conversation_id
                )

            self.remaining_count -= 1

if __name__ == "__main__":
    import yaml

    with open("config/config.yaml") as f:
        config = yaml.safe_load(f)

    LLM_CFG = config["llm"]

    llm = LLM(**LLM_CFG)
    agent = Agent(llm)
    plan, obj = agent.get_available_plans([{'name': 'object_name'}])
    print(obj)
    print(plan)