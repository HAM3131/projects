from dotenv import load_dotenv
import os
import openai
from openai import OpenAI

# Load .env file
load_dotenv()

def undef(*args, **kwargs): print("function undefined")

# Step 1: Configuration
class Config:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API')
        openai.api_key = self.api_key

# Step 2: Agent Class
class Agent:
    def __init__(self, config, model='gpt-4o'):
        self.config = config
        self.client = OpenAI()
        self.client.api_key = self.config.api_key
        self.model = "gpt-4o"

    def format_messages(self, system, tasks, prompt):
        messages = [
                {
                    "role": "system",
                    "content": [{
                        "type": "text",
                        "text": system + tasks
                }]},
                {
                    "role": "user",
                    "content": [{
                        "type": "text",
                        "text": prompt
                }]}
        ]
        return messages

    def generate_response(self, messages):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )
        return response.choices[0].message.content

# Step 3: Tasks
class Task:
    def __init__(self, name, description, parameters, function):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.function = function

# Step 4: Task Handlers
class TaskHandler:
    def __init__(self, agent, tasks):
        self.agent = agent
        self.tasks = {task.name: task for task in tasks}

    def plan_tasks(self, prompt):
        messages = self.agent.format_messages("Create a plan to accomplish the objective with a numbered list of steps utilizing the available tools. ONLY RESPOND WITH A NUMBERED LIST. If you do not have sufficient tools, only state: 'INSUFFICIENT TOOLBOX: ____` and describe what tools you need. ", self.task_list(), prompt)
        return self.agent.generate_response(messages)

    def handle_task(self, task_name, inputs):
        task = self.tasks.get(task_name)
        if not task:
            return "Unknown task type"
        return task["function"](inputs)

    def task_list(self):
        list = "AVAILABLE TASKS:\n"
        for key, value in self.tasks.items():
            list += value.name + " - " + value.description + "\n"
        return list

# Step 4: Main Program
def main():
    # Setup
    config = Config()
    if not config.api_key:
        print("API key not found. Please check your .env file.")
        return

    agent = Agent(config)
    tasks = [Task("browser", "This tool returns the titles and URLs of the top 10 results for a search term.", ["search term"], undef), Task("to_memory", "This tool stores some information to a file for future reference", ["data"], undef), Task("from_memory", "This tool retrieves some memory from a file", ["file name"], undef)]
    handler = TaskHandler(agent, tasks)

    # Main Loop
    while(True):
        prompt = input("What can I help you with? (enter QUIT to leave)  ")
        if (prompt == "QUIT"):
            break
        print(handler.plan_tasks(prompt))

if __name__ == "__main__":
    main()

