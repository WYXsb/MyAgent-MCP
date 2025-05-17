import asyncio
import abc
import logging
# 这个abc里面的 ABC abstractmethod是干啥的？
from abc import ABC, abstractmethod
from llm import completion_async

class BaseAgent(ABC):
    def __init__(self, name: str, worker_count: int, input_queue: asyncio.Queue, output_queue: asyncio.Queue):
        self.name = name
        self.worker_count = worker_count
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.workers = []

    @abstractmethod
    async def process(self, message: dict) -> dict:
        pass

    async def worker(self,wid: int):
        while True:
            try:
                message = await self.input_queue.get()
                result = await self.process(message)
                if result is not None:
                    await self.output_queue.put(result)
                    
                self.input_queue.task_done()
            except asyncio.CancelledError:
                logging.info(f"[{self.name}-{wid}] 协程被取消")
                break
            except Exception as e:
                logging.error(f"[{self.name}-{wid}] 工作出错: {e}")

    async def start(self):
        for i in range(self.worker_count):
            task = asyncio.create_task(self.worker(i))
            self.workers.append(task)

    def stop(self):
        for task in self.workers:
            task.cancel()

class SummarizerAgent(BaseAgent):
    async def process(self, message: dict) -> dict:
        text = message["text"]
        try:
            summary = await completion_async(f"请总结以下内容的核心观点：{text}")
            result = {
                "agent": "Summarizer",
                "action": "summarize",
                "input": text,
                "result": summary,
                "id": message["id"]  # 确保包含 id 字段
            }
            logging.info(f"[Summarizer] 处理完成，准备放入 middle_queue: {result}")
            return result
        except Exception as e:
            logging.error(f"[Summarizer] 处理出错: {e}")
            return None


class SentimentAgent(BaseAgent):
    async def process(self, message: dict) -> dict:
        try:
            text = message["result"]
            sentiment = await completion_async(f"请你复述一遍下面的话：{text}")
            return {
                "agent": "Sentiment",
                "action": "analyze",
                "input": text,
                "result": sentiment,
                "id": message["id"]  # 确保包含 id 字段
            }
        except KeyError:
            print(f"[Sentiment] 消息缺少 'result' 字段: {message}")
            return None
        except Exception as e:
            print(f"[Sentiment] 处理出错: {e}")
            return None
