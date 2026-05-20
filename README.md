## Repo Setup

```sh
$ uv sync
```

## Thoughts
### Week01
The most challenging assignment was [k_shot_prompting.py](./week01/k_shot_prompting.py). I tried several approaches, but none produced satisfactory results. In the end, my solution was somewhat of a workaround.
```
Example:
word: http
letters: h t t p
last-to-first: p t t h
answer: ptth

Example:
word: status
letters: s t a t u s
last-to-first: s u t a t s
answer: sutats

Example:
word: httpstatus
letters: h t t p s t a t u s
last-to-first: s u t a t s p t t h
```

⬆️ Show the character list for `httpstatus` *but* do not give the final answer directly (Success Rate: $10\%$ -> $20\%$)

### Week02

I use the [opencode](https://opencode.ai/) with `DeepSeek Chat/Reasoner` and `Minimax M2.5 Free` to do the exercise. The prompts are mainly taken from the [assignment](./week02/assignment.md).

### Week04

I use the [opencode](https://opencode.ai/) with `Minimax M2.5 Free` to generate a [AGENTS.md](./week04/AGENTS.md) and write a customized slash command [`tests`](./week04/.opencode/commands/tests.md).

### Week05

I use the [opencode](https://opencode.ai/) with `Minimax M2.5 Free` to finish the task 02 without using Warp automations.

### Week06

I encountered network issues when using `semgrep`, so I just skipped this assignment.

### Week07

I use the [opencode](https://opencode.ai/) with `DeepSeek V4 Pro` to finish the task 1 in [`TASK.md`](./week07/docs/TASKS.md).

I use a one-line prompt — I simply ask the agent to complete a task without providing any additional requirements. To my surprise, it does *more* than just finish the implementation. It also adds appropriate tests to verify that the implementation works correctly.

I manually reviewed the changes and was quite satisfied with the results. I then started a new session and asked `DeepSeek V4 Pro` to review the code changes. It did identify a few issues related to code style and maintainability, but it found no logical bugs :)
