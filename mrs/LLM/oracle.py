from mrs.LLM.base import RobotBase
from mrs.LLM.LLM import LLM


class Oracle(RobotBase):
    def __init__(self, llm: LLM):
        self.llm = llm
        self.last_done = False

    def get_observation(self):
        return super().get_observation()
    
    def get_action(self):
        return super().get_action()
    
    def step(self):

        # subtask 생성
        # 1. get_observation()

        # 2. prompt 구성

        # 3. 추론 실행
        plan = self.llm.generate(prompt=None, conversation_id=None)

        # Executor 작동

        # Feedback 받기

        # 


        return done, task_results, agent_action, agent_meassage, steps