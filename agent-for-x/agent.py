from dotenv import load_dotenv
import os
import openai
from openai import OpenAI
import json

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
    def __init__(self, name, description, var, output, function):
        self.name = name
        self.description = description
        self.input_parameters = var
        self.output_parameters = output
        self.function = function
        self.representation = "(" + ",".join([key for key, value in var])+ ")" + "-->" + "(" + ",".join([key for key, value in output]) + ")"

# Step 4: Task Handlers
class TaskHandler:
    def __init__(self, agent, tasks):
        self.agent = agent
        self.tasks = {task.name: task for task in tasks}

    def plan_tasks(self, prompt):
        messages = self.agent.format_messages("Create a plan to accomplish the objective utilizing only the available tools. Your response should be formatted as a JSON, with numbered fields for each of the steps. If you do not have enough tools, the 'FAILURE' field should be 'TRUE' and the 'REASON' field should have an explanation of why you don't have enough tools, otherwise 'FAILURE' should be 'FALSE' and 'REASON' should be blank. Every numbered step should have several fields: One for 'TOOL_NAME', and one for each of the input variables required (X,Y,Z). It should also have an 'OUTPUTS' field with each of the output names (A,B,C) and their description. If a tool needs the output of a previous tool as it's input, you can put the step number followed by the variable name. For example, to get the top search results from step one if you used the 'browser' tool, you would use '1B' as the input value.\n\n The final step should ALWAYS be to use the `to_user` function to print a response to the user. The last field should be a 'STEPS' field with the total number of steps.", self.task_list(), prompt)
        task_plan = self.agent.generate_response(messages)
        if task_plan.startswith("```json\n"):
            task_plan = task_plan[len("```json\n"):]
        if task_plan.endswith("```"):
            task_plan = task_plan[:-len("```")]
        return json.loads(task_plan)

    def lint_tasks(self, task_plan):
        return True

    def execute_tasks(self, task_plan):
        for i in range(task_plan["STEPS"]):
            print(task_plan[str(i+1)]["TOOL_NAME"])
        return True

    def handle_task(self, task_name, inputs):
        task = self.tasks.get(task_name)
        if not task:
            return "Unknown task type"
        return task["function"](inputs)

    def task_list(self):
        list = "AVAILABLE TASKS:\n"
        for name, task in self.tasks.items():
            list += "`" + task.name + "`" + " - " + task.description + "\n"
            list += "\t" + task.representation + "\n"
            list += "".join(["\t\t" + key + " - " + value + "\n" for key, value in task.input_parameters])
            list += "".join(["\t\t" + key + " - " + value + "\n" for key, value in task.output_parameters])
        return list

# Step 4: Main Program
def main():
    # Setup
    config = Config()
    if not config.api_key:
        print("API key not found. Please check your .env file.")
        return

    agent = Agent(config)
    tasks = [Task("browser", "This tool returns the titles and URLs of the top 10 results for a search term.", [("X", "search term")], [("A", "success/fail"), ("B", "top 10 search results")], undef), Task("to_user", "This tool prints to the user.", [("X", "print data")], [("A", "success/fail")], undef)]
    handler = TaskHandler(agent, tasks)

    # Main Loop
    print(handler.task_list())
    while(True):
        prompt = input("What can I help you with? (enter QUIT to leave)  ")
        if (prompt == "QUIT"):
            break
        task_plan = handler.plan_tasks(prompt)
        print(json.dumps(task_plan, indent=4, separators=(",", ": "), sort_keys=True))
        handler.execute_tasks(task_plan)

if __name__ == "__main__":
    main()

