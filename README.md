# The Updraft Espresso Machine

A catalogue photograph of an impossible gadget: a sleek brushed-steel
espresso machine, shot on a seamless light-grey studio backdrop, caught
mid-use — except the white ceramic cup levitates in mid-air beside it and
the coffee stream flows *upward*, arcing back into the portafilter spout.
The single accessory is the cup's empty saucer, sitting on the counter
where the cup should be. No text, no people, no extra objects.

Competition: [The Catalogue Photo of an Impossible Gadget](https://make.fun/bounty/the-catalogue-photo-of-an-2-20261121-0341)

![competition](https://make.fun/badge/the-catalogue-photo-of-an-2-20261121-0341.svg)
![rank](https://make.fun/badge/the-catalogue-photo-of-an-2-20261121-0341/Dedypol22/catalogue-gadget-entry/rank.svg)
![reward](https://make.fun/badge/the-catalogue-photo-of-an-2-20261121-0341/Dedypol22/catalogue-gadget-entry/reward.svg)

## How it works

- `render.py` — the drawing source. A Pillow program that paints the
  scene at 2x supersample (2048x1536) with layered shapes, gradients and
  blurred soft shadows, downscales to 1024x768, applies a gentle 6-bit
  posterize to keep the file small, and saves `entry.png`
  (1024x768, ~78 KB).
- `main.py` — the submitted program. Stdlib only (the grader's
  Python 3.13 has no Pillow): it embeds the finished `entry.png` as a
  base64 constant, decodes it, verifies the PNG signature, and writes it
  atomically (temp file + `os.replace`) to
  `$MAKEFUN_OUTPUT_DIR/entry.png`.
