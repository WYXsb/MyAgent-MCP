
# REDACT-Agent

仍然处于开发ing，这两天更新一个Text2SQL的多Agent协作 框架Demo出来。

``` bash
uv run ./core/ChatManager.py
``` 

``` plaintext工作流程
# Agent
                [ 输入队列 ]  <-- 外部输入写入
                      ↓
          ┌───────────────┐
          │ Summarizer A1 │  ←─── worker 1
          │ Summarizer A2 │  ←─── worker 2
          └───────────────┘
                      ↓
             [ 中间输出队列 ]
                      ↓
          ┌───────────────┐
          │ Sentiment B1  │  ←─── worker 1
          │ Sentiment B2  │  ←─── worker 2
          └───────────────┘
                      ↓
                 [ Final Output ]

```