# L0007 — A request from another site, or to another host name, is refused

## Reason
An app on localhost with no login is still reachable by any page open in the
same browser: that page can post a form to it, or point its own host name at
127.0.0.1 and read the data. The shop accepts a request only when its Host is
this machine, and a post only when its Origin, if the browser sent one, is the
shop itself.

## Source
The wizardly-cerf run, 2026-11-18: cross-site posts were accepted, and no
measure, audit or blind build looked for it. The person, run 001, 2026-11-19
(answer 7: "cross-site posts are still refused").
Read as written and accepted by the person, 2026-11-19 (run 005).

## What would be a regression
A post with a foreign Origin, or `Sec-Fetch-Site` other than same-origin, or
any request with a foreign Host, answered with anything but 403.
