#!/usr/bin/env python3
"""Diagnostic: show compact source contexts for the kazak's arm animations."""
import re
from pathlib import Path

html = Path("index.html").read_text(encoding="utf-8")
patterns = [
    r"mustache", r"moustache", r"\u0443\u0441\u044b", r"\u0443\u0441\u043e\u0432",
    r"\u043f\u0440\u0430\u0432\u0430\u044f\s+\u0440\u0443\u043a\u0430",
    r"arm", r"hand", r"hero", r"kazak", r"cossack",
    r"idle", r"sprite", r"@keyframes",
    r"\u0430\u043d\u0438\u043c\u0430\u0446\u0438\u044f", r"\u0430\u043d\u0438\u043c\u0430\u0446",
    r"\u043a\u0430\u0437\u0430\u043a",
]
print(f"SOURCE characters={len(html)} lines={html.count(chr(10))+1}")
for pattern in patterns:
    found = list(re.finditer(pattern, html, flags=re.I))
    print(f"PATTERN {pattern} COUNT {len(found)}")
    for match in found[:10]:
        start, end = match.span()
        excerpt = html[max(0,start-220):min(len(html),end+320)].replace("\n"," ")
        print("  CONTEXT:",excerpt[:540])
