
class RobotBase:
    def __init__(self, llm, camera):
        self.llm = llm
        self.camera = camera
    
    def get_observation(self):
        # GroundingDINO + SAM
        # 공통 관측 로직
        raise NotImplementedError
    
    def step(self):
        raise NotImplementedError