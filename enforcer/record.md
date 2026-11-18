# Record of the enforcer

**State.** Built and standing by the judge; verdict passes (90 cases, number 10738). In use.

**How it stood.** The first build stood with no judge, as the first effect
of principle 4 (how the tree grows): measure and planted wrong enforcers
first, then the build. Its `undo` then failed on first use while the verdict
passed. By principle 6 the measure gained the case first (20 cases, 8
planted wrong undos, by an agent that does not build the enforcer), the
standing build failed it, and the judge let the corrected build stand
(`judge/stands.tsv`, change `16d40e2`; undo of that change proven).

**Limits.**
- The coordinating session built it, and the same session gave it its
  declarations. The measure was written by a separate agent that never saw
  the build; the build was written before its maker saw the measure.
- Error: unknown (declaration 5).
- A full run reruns every planted build of every unit and takes minutes.

**Round before first effect.** Nothing asked of the root.

**Tried and rejected.** The first build (9968): `undo` died on every call.

**Due next.** A source for its error numbers; nothing in progress.
