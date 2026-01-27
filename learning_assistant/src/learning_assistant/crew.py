from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.memory import LongTermMemory, ShortTermMemory, EntityMemory
from crewai.memory.storage.rag_storage import RAGStorage
from crewai.memory.storage.ltm_sqlite_storage import LTMSQLiteStorage
from crewai_tools import SerperDevTool

from learning_assistant.tools.memory_search_tool import MemorySearchTool


@CrewBase
class LearningAssistantCrew:

    @agent
    def curriculum_planner(self) -> Agent:
        return Agent(
            config=self.agents_config['curriculum_planner'],
            verbose=True,
            tools=[MemorySearchTool()]
        )

    @agent
    def content_creator(self) -> Agent:
        return Agent(
            config=self.agents_config['content_creator'],
            verbose=True,
            tools=[SerperDevTool()]
        )

    @agent
    def exercise_generator(self) -> Agent:
        return Agent(
            config=self.agents_config['exercise_generator'],
            verbose=True
        )

    @task
    def plan_learning_path(self) -> Task:
        return Task(
            config=self.tasks_config['plan_learning_path']
        )

    @task
    def create_lesson_content(self) -> Task:
        return Task(
            config=self.tasks_config['create_lesson_content']
        )

    @task
    def generate_exercises(self) -> Task:
        return Task(
            config=self.tasks_config['generate_exercises']
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=True,
            long_term_memory=LongTermMemory(
                storage=LTMSQLiteStorage(
                    db_path="./memory/long_term_memory_storage.db"
                )
            ),
            short_term_memory=ShortTermMemory(
                storage=RAGStorage(
                    embedder_config={
                        "provider": "openai",
                        "config": {
                            "model_name": "text-embedding-3-small"
                        }
                    },
                    type="short_term",
                    path="./memory/"
                )
            ),
            entity_memory=EntityMemory(
                storage=RAGStorage(
                    embedder_config={
                        "provider": "openai",
                        "config": {
                            "model_name": "text-embedding-3-small"
                        }
                    },
                    type="entities",
                    path="./memory/"
                )
            )
        )
