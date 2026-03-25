import backoff
from openai import OpenAIError

from mrs.LLM.base import RobotBase
from mrs.LLM.LLM import LLM


class Oracle(RobotBase):
    def __init__(self, llm: LLM, agent: list):
        self.llm = llm
        self.last_done = False
        self.conversation_id = self._init_conversation()

    @backoff.on_exception(backoff.expo, OpenAIError)
    def _init_conversation(self):
        conv = self.llm.client.conversations.create()
        return conv.id

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