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

⬆️ Show the character list for `httpstatus` *but* do not give the final answer directly (Success Rate: $10\%\rightarrow 20\%$)

### Week02

I use `DeepSeek Reasoner` and the [opencode](https://opencode.ai/) to do the exercise. The prompts I used can be found in [prompts.md](./week02/prompts.md)
