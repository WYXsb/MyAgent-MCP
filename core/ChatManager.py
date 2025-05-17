import asyncio
import logging
from agents import SummarizerAgent,SentimentAgent

class MultiAgentPipeline:
    def __init__(self, max_queue_size=20, worker_per_agent=2):
        self.input_queue = asyncio.Queue(maxsize=max_queue_size)
        self.middle_queue = asyncio.Queue(maxsize=max_queue_size)
        self.output_queue = asyncio.Queue(maxsize=max_queue_size)

        self.summarizer = SummarizerAgent(name="Summarizer", worker_count = worker_per_agent, input_queue = self.input_queue, output_queue = self.middle_queue)
        self.sentiment = SentimentAgent(name="Sentiment",worker_count =  worker_per_agent, input_queue =self.middle_queue, output_queue = self.output_queue)

    async def feed_inputs(self, items: list[dict]):
        for item in items:
            await self.input_queue.put(item)
            logging.info(f"[输入] 添加任务 {item['id']}，middle_queue 大小: {self.middle_queue.qsize()}")
            await asyncio.sleep(0.05)  # 可调节速率

    async def collect_outputs(self, total: int):
        results = []
        for _ in range(total):
            result = await self.output_queue.get()
            print(f"[输出] 完成任务 {result['id']}：{result}")
            results.append(result)
            self.output_queue.task_done()
        return results

    async def run(self, inputs: list[dict]):
        await self.summarizer.start()
        await self.sentiment.start()

        producer = asyncio.create_task(self.feed_inputs(inputs))
        consumer = asyncio.create_task(self.collect_outputs(len(inputs)))

        await producer
        await self.input_queue.join()
        await self.middle_queue.join()
        await self.output_queue.join()
        await consumer

        self.summarizer.stop()
        self.sentiment.stop()

        await asyncio.gather(*self.summarizer.workers, *self.sentiment.workers, return_exceptions=True)
# test
async def test():
    inputs = [{"id": i, "text": f"这是第 {i} 条测试文本"} for i in range(10)]
    # inputs.append({"flag": None, "text": "这是结束了"})
    pipeline = MultiAgentPipeline(max_queue_size=10, worker_per_agent=2)
    await pipeline.run(inputs)

if __name__ == "__main__":
    asyncio.run(test())