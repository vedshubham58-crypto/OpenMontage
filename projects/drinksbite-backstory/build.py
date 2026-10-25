# Builds the three "backstory" reels (pack pops → flips → zoom into the flavour story → front → end card).
import os, json

SKUS = {
  "beer": dict(
    n="beer", front="Cheddar &amp; Herbs", title="Smoky Cheddar &amp; Herb", insp="Beer-inspired", drink="beer",
    c="#f7b733", cl="#f7b733", glow="rgba(247,183,51,0.22)", ink="#171717",
    s=["Crisp jowar puffs hit you with a <m>bright, tangy crunch</m> that rolls right into <m>savory garlic, herbs</m>, and a low-key <m>malty depth</m>.",
       "Vibe-check them with a crisp, <m>hop-forward</m> drink profile full of refreshing <m>bitter-sweet</m> notes.",
       "The sharp tang cuts straight through the fizz while the herby, malty notes match the drink's energy for an absolute <m>match made in heaven</m>."],
    stick=["Vibe check: passed.", "10/10 would pair again"]),
  "rum": dict(
    n="rum", front="Coconut &amp; Spices", title="Coconut Smoke &amp; Spice", insp="Rum-inspired", drink="rum",
    c="#669933", cl="#8cc152", glow="rgba(102,153,51,0.30)", ink="#10180a",
    s=["Airy jowar puffs serve up <m>soft sweetness, warm spice</m>, and <m>subtle smoke</m>, all capped off with a <m>zesty citrus pop</m>.",
       "Made to flex right alongside rich <m>caramel, vanilla, and citrus</m> drink profiles.",
       "The light crunch gives all those deep, sweet flavors room to breathe, serving a totally balanced contrast that makes <m>every sip hit different</m>."],
    stick=["Main character energy", "Every. Single. Sip."]),
  "whiskey": dict(
    n="whiskey", front="Toasted Sesame Umami", title="Toasted Sesame Umami", insp="Whiskey-inspired", drink="whiskey",
    c="#8a5baa", cl="#b48fd0", glow="rgba(138,91,170,0.32)", ink="#f5f0ea",
    s=["Super crisp jowar puffs loaded with <m>deep roasted flavor</m>, heavy garlic, onion, and <m>pure umami</m>, ending on a smooth <m>toasted-oak warmth</m>.",
       "Styled to match <m>roasted, caramelized, smoky, and oak-inspired</m> drink profiles.",
       "The clean crunch keeps the bold seasoning in check so it completely backs up the drink's depth <m>without doing too much</m>."],
    stick=["Oak-ed to perfection", "Just enough. Never too much."]),
}

CARD = dict(x=260, y=450, w=560, h=1022)
TX, TY, TW = 40, 80, 340          # story block inside the card
SY = [152, 236, 320]              # sentence block tops (card coords)
S = 2.55                          # zoom

def focus(px, py, sx=540, sy=880):
    gx, gy = CARD["x"] + px, CARD["y"] + py
    return round(sx - S * gx, 1), round(sy - S * gy, 1)

TPL = open(os.path.join(os.path.dirname(__file__), "template.html")).read()
for key, d in SKUS.items():
    sent = "".join(
        f'<div class="sent" id="s{i}" style="top:{SY[i]}px">' + t.replace("<m>", '<span class="hl">').replace("</m>", "</span>") + "</div>"
        for i, t in enumerate(d["s"]))
    cams = {"title": focus(TX + TW / 2, TY + 40), "s0": focus(TX + TW / 2, SY[0] + 34), "s1": focus(TX + TW / 2, SY[1] + 30), "s2": focus(TX + TW / 2, SY[2] + 36)}
    html = (TPL.replace("%%KEY%%", key).replace("%%FRONT%%", d["front"]).replace("%%TITLE%%", d["title"]).replace("%%INSP%%", d["insp"])
            .replace("%%DRINK%%", d["drink"]).replace("%%C%%", d["c"]).replace("%%CL%%", d["cl"]).replace("%%GLOW%%", d["glow"]).replace("%%INK%%", d["ink"])
            .replace("%%SENT%%", sent).replace("%%ST0%%", d["stick"][0]).replace("%%ST1%%", d["stick"][1])
            .replace("%%S%%", str(S)).replace("%%CAMS%%", json.dumps(cams)))
    out = os.path.join(os.path.dirname(__file__), key); os.makedirs(out, exist_ok=True)
    open(os.path.join(out, "index.html"), "w").write(html)
    link = os.path.join(out, "assets")
    if not os.path.exists(link): os.symlink("../assets", link)
    print("built", key)
