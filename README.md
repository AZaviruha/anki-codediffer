# Anki CodeDiffer

Add-on for Anki SRC. It allows you to create cards with interactive input. Also it uses differ to visualize how your input is different from correct answer.

## When to use?

This addon should be helpful to learn some new APIs. With it you can learn API not by drilling, but by trying to solve some simple tasks.

## How to use?

For example, you can copy/paste some code samples from [MDN](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Generator):

![editor](./doc/img/editor.jpg)


Then you try to input the correct solution on the Question side:

![frontside](./doc/img/frontside.jpg)


... and then you can check how close your solution is to the right answer:

![backside](./doc/img/backside.jpg)

Tags `[diff][/diff]` and `[diff-answ][/diff-answ]` should be added manually. 
It can be improved in the feature by adding some additional GUI into Anki card editor.

- `[diff][/diff]` is used to to let add-on figure where to insert code editor;
- `[diff-answ][/diff-answ]` is used to to let add-on figure which part of the answer should be used as "correct answer" in code differ.

## Supported languages and themes

```python
SUPPORTED_LANGUAGES = [
    'javascript',
    'python',
    'sql',
    'typescript'
]

SUPPORTED_THEMES = [
    'chrome',
    'monokai',
    'solarized_dark',
    'solarized_light'
]
```

## TODO

1. Allow to override sample's language by car'ds field `Lang`.
2. Add GUI to mark code editor place on the question side.
2. Add GUI to mark differ-ed part of answer.
4. Research how to add any of [Ace](https://ace.c9.io/)'s languages/themes on the fly.


# Thanks

<div>Icons made by <a href="https://www.freepik.com/" title="Freepik">Freepik</a> from <a href="https://www.flaticon.com/" 			    title="Flaticon">www.flaticon.com</a> is licensed by <a href="http://creativecommons.org/licenses/by/3.0/" 			    title="Creative Commons BY 3.0" target="_blank">CC 3.0 BY</a></div>