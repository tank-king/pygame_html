# pygame_html

A pygbag-compatible utility library for rendering HTML documents in python

## Why use this library?

This library is unique because it can be utilized in web-based environments, unlike other available modules like pygame_gui. 
If you aim to create a pygame game that runs directly in a web browser using web assembly or emscripten, 
this library is an ideal choice. <br> 
If you don't know about porting pygame games to web, you can check out [pygbag](https://github.com/pygame-web/pygbag) - one of the possible options.

## Supported HTML features

The module mimics HTML rendering using a container-based GUI system,
approximating the visual appearance of HTML documents within its limitations.
Note that achieving true HTML rendering would require significant development similar
to building a web browser from scratch.

All the supported HTML tags are:

| tag      | self-closing | usage                             |      attributes      |
|----------|:------------:|-----------------------------------|:--------------------:|
| `no-tag` |      -       | `...`                             | [read more](#no-tag) |
| `text`   |      no      | `<text> ... </text>`              |          -           |
| `br`     |   **yes**    | `<br/>`                           |          -           |
| `img`    |   **yes**    | `<img src='path/to/image/file'>`  |        `src`         |
| `b`      |      no      | `<b> ... </b>`                    |          -           |
| `i`      |      no      | `<i> ... </i>`                    |          -           |
| `strike` |      no      | `<strike> ... </strike>`          |          -           |
| `center` |      no      | `<center> ... </center>`          |          -           |
| `p`      |      no      | `<p> ... </p>`                    |          -           |
| `a`      |      no      | `<a href='add/link/url> ... </a>` |        `href`        |

Supported Additional tags are:

| tag      | self-closing | usage                             |  attributes   |
|----------|:------------:|-----------------------------------|:-------------:|

Everything else that is not supported here can be simulated by arranging the containers accordingly,<br>
for example `list` containers.

By default, all containers support the following font settings. Each font setting can be override within
a container. If not overriden, the child container will inherit the parent container's corresponding font setting.

- `align`
- `font`
- `size`
- `bold`
- `italic`
- `strikethrough`
- `color`
- `wraplength`
- `antialias`

Example Usage: `<container align="center" size=25> ... </container>`

## How to Use:

pygame_html has been designed to be compatible with pygbag. Therefore you need to copy the folder pygame_html
into the root directory of your project. <br>
Now, we are asuming you have the following layout of your game:

```python
...

screen = pygame.display.set_mode(...)

# game loop
while True:
    events = pygame.event.get()
    for event in events:
        handle_event(event)
    
    screen.fill(0)
    
    # draw stuff on screen
    ...

```

Add the following lines:

```python
from pygame_html import GUIManager
```

Once you have initialized the display module, only after that you should initialize the
`GUIManager` class. This is to make sure the contents are bound to the display surface's width.
Otherwise, the rendering will stretch infinitely horizontally

```python
...
screen = pygame.display.set_mode(...)

gui_manager = GUIManager()
```

Now, in the main game loop, add the following:

```python

# game loop
while True:
    events = pygame.event.get()
    for event in events:
        handle_event(event)
    
    screen.fill(0)
    
    # draw stuff on screen
    ...
    
    # ---------------------------------
    gui_manager.update(events)
    gui_manager.draw(screen)
    # ---------------------------------
    
```

That's it!
To instantly load a new file, you need to just write
```python
gui_manager.load_popup('path/to/file/name.html')
```

To minimize or restore the HTML rendering, you can use the
`minimize()` and `restore()` methods respectively

## Details about selected Tags:
### no-tag
This tag denotes content you write within containers
For example
`<p> some text here </p>`

The words "some text here" are not parsed as tags. However, they are converted to Text Containers
by default. They have all the features of writing text content into the screen. Extra spaces are removed.
The sentences are parsed word by word to support word wrapping. Note that only words can wrap to another line
but not their individual letters. Words longer than entire display window needs scrolling horizontally
to work.

### 
