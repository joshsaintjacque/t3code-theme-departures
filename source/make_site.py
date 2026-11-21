"""Generate index.html (palette rows come straight from departures.json)."""
import json, os
H = os.path.dirname(os.path.abspath(__file__))
c = json.load(open(os.path.join(H, "..", "departures.json")))["colors"]
SITE = "https://joshsaintjacque.github.io/t3code-theme-departures/"
REPO = "https://github.com/joshsaintjacque/t3code-theme-departures"
ROLES = [("canvas", "Concourse floor behind the chat"), ("sidebar", "Sidebar, a shade darker"), ("surface", "Composer and panels"),
         ("text", "Cream type on black"), ("textMuted", "Secondary text"), ("accent", "Amber: buttons, focus, lamps"),
         ("accentForeground", "Ink on amber"), ("messageSurface", "Your messages: boarding-pass stock"), ("messageForeground", "Ink on the pass"),
         ("border", "Hairlines"), ("codeBackground", "Code blocks"), ("sidebarRowSelected", "Selected thread"),
         ("warningForeground", "Pale amber for warnings"), ("update", "On-time green"), ("error", "Cancelled red"), ("terminalSelection", "Terminal selection")]
rows = "\n".join(
    f"<tr tabindex=0 role=button data-hex='{c[k]}' aria-label='Copy {k} {c[k]}'><td><i style='background:{c[k]}'></i></td><td class=k>{k}</td><td class=h>{c[k]}</td><td class=u>{u}</td></tr>"
    for k, u in ROLES)
html = open(os.path.join(H, "site.tpl.html")).read().replace("__ROWS__", rows).replace("__SITE__", SITE).replace("__REPO__", REPO)
open(os.path.join(H, "..", "index.html"), "w").write(html)
print("index.html", len(html))
