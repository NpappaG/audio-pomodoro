import os
import asyncio
import pyttsx3
from dotenv import load_dotenv
import openai
from pydantic import BaseModel
from typing import List
import instructor

# Load environment variables
load_dotenv()

# Patch OpenAI client with instructor
client = instructor.patch(openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY')))

class TaskBreakdown(BaseModel):
    tasks: List[str]

class AudioFeedback:
    def __init__(self):
        print("Initializing audio engine...")
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 1.0)
        
    def speak(self, text):
        """Speak the given text with drill sergeant intensity"""
        print(f"Speaking: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

class PomodoroApp:
    def __init__(self):
        print("Initializing PomodoroApp...")
        self.audio = AudioFeedback()
        
    async def work_session(self, task):
        print(f"Starting work session for: {task}")
        self.audio.speak(f"ATTENTION! Starting 25-minute focus session for: {task}")
        print("Starting 25-minute timer...")
        await asyncio.sleep(25 * 60)  # 25 minutes
        self.audio.speak("TIME'S UP! Take a 5-minute break!")
        
    async def break_session(self):
        print("Starting 5-minute break...")
        await asyncio.sleep(5 * 60)  # 5 minutes
        self.audio.speak("BREAK'S OVER! Get back to work!")
        
    def generate_tasks(self, main_task):
        """Generate subtasks using OpenAI with instructor"""
        print("Generating subtasks...")
        breakdown = client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_model=TaskBreakdown,
            messages=[
                {"role": "system", "content": "You are a task breakdown expert. Break down tasks into specific, actionable subtasks."},
                {"role": "user", "content": f"Break down this task into 4-6 specific subtasks: {main_task}"}
            ]
        )
        return breakdown.tasks
        
    async def run(self):
        main_task = input("Enter your main task: ")
        tasks = self.generate_tasks(main_task)
        
        print("\nGenerated subtasks:")
        for i, task in enumerate(tasks, 1):
            print(f"{i}. {task}")
            
        print("\nStarting Pomodoro sessions...")
        for task in tasks:
            await self.work_session(task)
            await self.break_session()
            
        self.audio.speak("ALL TASKS COMPLETED! Great job, soldier!")

async def main():
    print("Starting Pomodoro app...")
    app = PomodoroApp()
    await app.run()

if __name__ == "__main__":
    asyncio.run(main()) 