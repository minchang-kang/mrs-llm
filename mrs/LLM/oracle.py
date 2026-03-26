import backoff
from openai import OpenAIError

from mrs.LLM.base import RobotBase
from mrs.LLM.agent import Agent
from mrs.LLM.LLM import LLM

class Oracle(RobotBase):
    def __init__(self, llm: LLM, agents: list[Agent]):
        self.llm = llm
        self.agents = agents
        self.oracle_prompt_path = None

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
        oracle_prompt = self.oracle_prompt_path
        with open(oracle_prompt, 'r') as f:
            oracle_prompt = f.read()
        oracle_prompt = oracle_prompt.replace(self.conversation_id)

        # 3. 추론 실행
        subtask, _ = self.llm.generate(oracle_prompt, self.conversation_id)

        # Executor 작동
        # subtask로 부터 Agent 추출
        # 해당 Agent에게 인가
        id = 0
        for agent in self.agents:
            if agent.id == id:
                done, task_results = agent.step(subtask, conversation_id=None)

        # Feedback 받기

        if done:
            return done, task_results
        
        else:
            return done, task_results
