import yaml
from mrs.LLM.oracle import Oracle
from mrs.LLM.agent import Agent
from mrs.LLM.LLM import LLM

with open("config/config.yaml") as f:
    config = yaml.safe_load(f)

LLM_CFG = config["llm"]

def main():
    try:
        llm = LLM(**LLM_CFG)

        # agents = [
        #     Agent(llm, camera1, agent_id=1),  # 로봇 팔 1
        #     Agent(llm, camera2, agent_id=2),  # 로봇 팔 2
        # ]

        agents = [
            Agent(llm, agent_id=1),
            Agent(llm, agent_id=2),
        ]

        oracle = Oracle(llm, agents)
    except RuntimeError as e:
        print(e)

    task_goal = None
    saved_info = []

    success = False
    steps = 0

    while True:
        success, result = oracle.step()

        if success:
            break
        else:
            steps += 1

if __name__ == "__main__":
    main()
