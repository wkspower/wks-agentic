# L0002 — A wrong variant is kept as a small change applied when the check runs, never as a full copy

## Reason
A planted wrong build differs from the right one by a handful of lines.
Storing each as a whole program multiplies the repository without adding
proof, and hides the few lines that matter.

## Source
The wizardly-cerf run, 2026-11-18. Of 58,750 lines, 40,257 were planted
wrong builds. The web unit had 35 of them, each a full program that differed
from the others by 5 to 8 lines, and each carried four modules that were
byte-identical in all 35. The product itself was 845 lines.

## What would be a regression
Two files of 20 lines or more with the same bytes anywhere in the tree.
The case does not catch near-copies that differ by a line; those still need
a reader.
