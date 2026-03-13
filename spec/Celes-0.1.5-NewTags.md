# Celes 0.1.5 — New Tags Spec

## New tags in this version

- `<video>` — embedded HTML5 video player
- `<audio>` — embedded HTML5 audio player
- `<background>` — sets the page background color
- `<coloredtext>` — inline colored text

---

## `<video>`

**Type:** Block tag  
**Content:** Path or URL to a video file  

### Syntax
```
<video>{path/or/url}
<video -loop>{path/or/url}
<video -mute>{path/or/url}
<video -autoplay -loop -mute>{path/or/url}
```

### Attributes
| Attribute | Description |
|-----------|-------------|
| *(none)*  | Renders with controls visible (default) |
| `-loop`   | Video loops on end |
| `-autoplay` | Video plays automatically on load |
| `-mute`   | Video is muted (required for autoplay in most browsers) |

### Rules
- Controls are always shown — there is no `-nocontrols` attribute in 0.1.5
- `-autoplay` without `-mute` is allowed but will be silently suppressed by most browsers
- Supported formats: `.mp4`, `.webm`, `.ogg` (browser-dependent)
- Renders as `<video controls ...><source src="..."></video>`

### Examples
```
; Basic embed
<video>{https://example.com/demo.mp4}

; Looping muted autoplay (e.g. background hero video)
<video -autoplay -loop -mute>{assets/hero.mp4}
```

### HTML output
```html
<!-- <video>{https://example.com/demo.mp4} -->
<video controls class="celes-video">
  <source src="https://example.com/demo.mp4">
  Your browser does not support the video tag.
</video>

<!-- <video -autoplay -loop -mute>{assets/hero.mp4} -->
<video controls autoplay loop muted class="celes-video">
  <source src="assets/hero.mp4">
  Your browser does not support the video tag.
</video>
```

---

## `<audio>`

**Type:** Block tag  
**Content:** Path or URL to an audio file  

### Syntax
```
<audio>{path/or/url}
<audio -loop>{path/or/url}
<audio -autoplay>{path/or/url}
```

### Attributes
| Attribute | Description |
|-----------|-------------|
| *(none)*  | Renders with controls visible (default) |
| `-loop`   | Audio loops on end |
| `-autoplay` | Audio plays automatically on load |

### Rules
- Controls are always shown
- Supported formats: `.mp3`, `.ogg`, `.wav` (browser-dependent)
- Renders as `<audio controls ...><source src="..."></audio>`

### Examples
```
; Basic audio player
<audio>{podcast-episode-1.mp3}

; Looping background music
<audio -loop -autoplay>{ambient.mp3}
```

### HTML output
```html
<!-- <audio>{podcast-episode-1.mp3} -->
<audio controls class="celes-audio">
  <source src="podcast-episode-1.mp3">
  Your browser does not support the audio tag.
</audio>
```

---

## `<background>`

**Type:** Document-level tag (place near top with `<title>`, `<author>`, `<date>`)  
**Content:** A CSS color — named color or hex code  

### Syntax
```
<background>{colorname}
<background>{#hexcode}
```

### Rules
- Only one `<background>` tag is valid per document — if multiple are present, the first one wins
- Accepts any valid CSS color value: named colors (`red`, `coral`, `navy`), hex (`#D4622A`), shorthand hex (`#f0f`)
- Does **not** accept `rgb()`, `hsl()`, or other CSS functions in 0.1.5
- Not rendered visually as a block — applies `background-color` to the document body
- `<author>` and `<date>` are still not rendered visually; `<background>` follows the same pattern

### Examples
```
<!Celes-0.1.5>
<title>{My Page}
<background>{#1a1a2e}
<header -size=1>{Dark themed page}
<line>{This page has a dark background.}
```

```
<background>{cornsilk}
```

### HTML output
```html
<!-- Applied as inline style on <body> or injected <style> -->
<style>body { background-color: #1a1a2e; }</style>
```

---

## `<coloredtext>`

**Type:** Inline tag (used inside `<line>`, `<blockquote>`, list tags, etc.)  
**Content:** The text to color  

### Syntax
```
<coloredtext -color=value>{text}
```

### Attributes
| Attribute | Required | Description |
|-----------|----------|-------------|
| `-color=value` | ✅ Yes | Any CSS color — named or hex |

### Rules
- `-color` attribute is **required** — the parser will error if omitted
- Accepts named colors and hex codes (same rule as `<background>` — no `rgb()`/`hsl()` in 0.1.5)
- Hex codes with `#` are written without quotes: `-color=#ff6600`
- Can be nested inside other inline tags (`<bold>`, `<italic>`, etc.)
- Other inline tags can be nested inside `<coloredtext>`

### Examples
```
<line>{The word <coloredtext -color=red>{danger} is highlighted.}
<line>{<coloredtext -color=#D4622A>{Celes} is the language.}
<line>{<bold>{<coloredtext -color=royalblue>{Bold and blue.}}}
<line>{<coloredtext -color=#00b894>{<italic>{Green italic text.}}}
```

### HTML output
```html
<p>The word <span style="color:red">danger</span> is highlighted.</p>
<p><span style="color:#D4622A">Celes</span> is the language.</p>
<p><strong><span style="color:royalblue">Bold and blue.</span></strong></p>
```

---

## Summary table — all 0.1.5 new tags

| Tag | Type | Self-closing | Required attrs | Optional attrs |
|-----|------|:---:|---|---|
| `<video>{url}` | Block | No | — | `-loop` `-autoplay` `-mute` |
| `<audio>{url}` | Block | No | — | `-loop` `-autoplay` |
| `<background>{color}` | Document | No | — | — |
| `<coloredtext -color=x>{text}` | Inline | No | `-color` | — |

---

## Parser validation rules added in 0.1.5

- `<coloredtext>` missing `-color` → error: `<coloredtext> requires -color attribute`
- `<background>` used more than once → warning: `duplicate <background> tag — first value used`
- `<video>` or `<audio>` used inline (inside `<line>`) → error: `<video>/<audio> must be block-level, not inline`
- `-autoplay` on `<video>` without `-mute` → warning: `autoplay without -mute may be suppressed by browsers`

---

## Full 0.1.5 example

```
<!Celes-0.1.5>
<title>{Media Demo}
<author>{Sourasish Das}
<background>{#0f0f0f}

<header -size=1>{Celes 0.1.5 Media Demo}

<section>{Video}
<line>{Here is an embedded video:}
<video -loop -mute>{demo.mp4}

<section>{Audio}
<line>{And a podcast episode:}
<audio>{episode-1.mp3}

<section>{Colored Text}
<line>{<coloredtext -color=#D4622A>{Celes} uses a consistent tag-based syntax.}
<line>{<bold>{<coloredtext -color=royalblue>{Bold blue}}, <coloredtext -color=green>{plain green}.}}
```
