
class RobotBase:
    def __init__(self, llm, agents, camera):
        self.llm = llm
        self.agents = agents
        self.camera = camera
    
    def get_observation(self):
        # GroundingDINO + SAM
        # 공통 관측 로직
        raise NotImplementedError
    
    def step(self):
        raise NotImplementedError