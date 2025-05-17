import os
from dotenv import load_dotenv
import asyncio
import time
from openai import OpenAI
from openai import AsyncOpenAI

MODEL_NAME = 'gpt-4o-mini'

load_dotenv()

def completion(instruction,model_name=MODEL_NAME):
    max_retries = 100
    retries = 0
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("未找到 OPENAI_API_KEY 环境变量")
    client = OpenAI(
        api_key=api_key,
    )
    while retries < max_retries:
        try:
            # try api
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": instruction,
                    }
                ],
                model=model_name,
            )

            # success then break
            break

        except Exception as e:
            # print error
            print(f"An error occurred: {e}")
            retries += 1
            # wait and retry
            time.sleep(5)  # wait 5s
            print(f"Retrying... (attempt {retries + 1}/{max_retries})")
    return chat_completion.choices[0].message.content

async def completion_async(prompt,model="gpt-4o-mini"):
    max_retries = 100
    retries = 0
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("未找到 OPENAI_API_KEY 环境变量")
    client = AsyncOpenAI(
        api_key=api_key
    )
    while retries < max_retries:
        try:
            chat_completion = await client.chat.completions.create(
                messages=[
                    {
                        'role': 'user',
                        'content': prompt,
                    }
                ],
                model=model,
            )
            break
        except Exception as e:
            retries += 1
            print(f"An error occurred: {e}")
            retries += 1
            # wait and retry
            time.sleep(5)  # wait 5s
            print(f"Retrying... (attempt {retries + 1}/{max_retries})")
    
    return chat_completion.choices[0].message.content


async def main():
    task1 = completion_async("nihao")
    results = await asyncio.gather(task1)
    print(results)
if __name__ == '__main__':
    # test 异步函数,并打印输出
    
    asyncio.run(main())