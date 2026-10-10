"""SawBladeLean animation clips, batch 2 (70 clips).

Locomotion extras, traversal, attacks, defense, reactions, grabs, open-world
interactions and emotes. Reuses the solver, helpers and base poses from
sawbladelean_clips_1.py, which must sit in the same folder; it does not
rebuild the batch 1 clips.

Run from the repo root, with Blender 5.2 or newer:

    blender SawBladeLean.blend --python scripts/sawbladelean_clips_2.py

Nothing is saved or exported; save the file and export the FBX yourself
afterwards.
"""
import os
_here = os.path.dirname(os.path.abspath(__file__))
_lib = os.path.join(_here, "sawbladelean_clips_1.py")
_src = open(_lib).read().split("ONLY = globals().get")[0]
exec(compile(_src, _lib, "exec"))

FIRST = dict(CLIPS)
CLIPS.clear()


def U(v):
    return both("UpperArm", v)


def Lw(rx):
    return both("LowerArm", (rx, 0, 0))


def feet(dy, dz, pitch, dx=0.0):
    return {"footL": (dx, dy, dz, pitch, 0), "footR": (-dx, dy, dz, pitch, 0)}


def unflat(P):
    o = {}
    for kk, v in P.items():
        n, i = kk.rsplit("#", 1)
        if n.startswith(("spin.", "loc.", "flat.")):
            continue
        o.setdefault(n, {})[int(i)] = v
    return {n: tuple(d[i] for i in range(len(d))) for n, d in o.items()}


def mirror2(p):
    o = {}
    for kk, v in p.items():
        if kk == "hips":
            o[kk] = (-v[0], v[1], v[2])
        elif kk in ("footL", "footR"):
            o["footR" if kk == "footL" else "footL"] = (-v[0], v[1], v[2], v[3], -v[4])
        else:
            nk = "Right" + kk[4:] if kk.startswith("Left") else ("Left" + kk[5:] if kk.startswith("Right") else kk)
            o[nk] = (v[0], -v[1], -v[2])
    return o


def mk(keys):
    return [(f, mirror2(p), e) for f, p, e in keys]


def turned(a, aL=None, aR=None, liftL=0.0, liftR=0.0, z=-0.04):
    def rot(v, ang):
        return Matrix.Rotation(radians(ang), 3, 'Z') @ v
    hp = rot(H["Hips"], a) - H["Hips"]
    out = {"Hips": (0, 0, a), "hips": (hp.x, hp.y, z)}
    for key, bn, ang, lift in (("footL", "LeftFoot", a if aL is None else aL, liftL), ("footR", "RightFoot", a if aR is None else aR, liftR)):
        d = rot(H[bn], ang) - H[bn]
        out[key] = (d.x, d.y, lift, 0, ang)
    return out


def lerpflat(a, b, w):
    return {c: a.get(c, 0.0) * (1 - w) + b.get(c, 0.0) * w for c in set(a) | set(b)}


RUN0 = unflat(FIRST["Run"][0][0])
CROUCH = M({"hips": (0, 0, -0.28), "Spine": (22, 0, 0), "Chest": (8, 0, 0), "Head": (-24, 0, 0)}, U((-25, -10, 0)), Lw(-50))
GRAB = M({"hips": (0, -0.10, -0.08), "Spine": (14, 0, 0), "Chest": (8, 0, 0), "Head": (-14, 0, 0)}, U((-82, 0, -22)), Lw(-35))
PRONE = M({"Hips": (85, 0, 0), "hips": (0, -0.50, -0.40), "Spine": (-4, 0, 0), "Chest": (-4, 0, 0), "Head": (-15, 0, 30),
           "footL": (0, 0.0, -0.08, 168, 0), "footR": (0, 0.17, -0.08, 168, 0)}, U((-150, -35, 0)), Lw(-40))
SIT = M({"hips": (0, 0.28, -0.30), "Hips": (-5, 0, 0), "Spine": (8, 0, 0), "Chest": (4, 0, 0), "Head": (-6, 0, 0)}, U((-38, -6, 0)), Lw(-45))
REST = M({"hips": (0, 0.32, -0.40), "Hips": (-18, 0, 0), "Spine": (22, 0, 0), "Chest": (12, 0, 0), "Head": (-10, 0, 0)}, U((-60, -8, 0)), Lw(-25))
KNEEL = M({"hips": (0, 0.10, -0.36), "Hips": (12, 0, 0), "Spine": (40, 0, 0), "Chest": (25, 0, 0), "Head": (30, 0, 0),
           "footL": (0, 0.30, -0.08, 168, 0), "footR": (0, 0.38, -0.08, 168, 0)}, U((8, -10, 0)), Lw(-5))

# ------------------------------------------------------------ locomotion extras


def idle_look(t):
    p = idle((t * 1.5) % 1.0)
    yaw = 45 * sin(2 * pi * t) * (0.5 - 0.5 * cos(2 * pi * t))
    p["Head"] = (p["Head"][0], 0, yaw * 0.7)
    p["Neck"] = (0, 0, yaw * 0.3)
    p["Chest"] = (p["Chest"][0], 0, yaw * 0.25)
    return p


clip("IdleLook", loop_fn(90, idle_look), loop=True)
REV = M({"hips": (0, 0, -0.06), "Spine": (4, 0, -6), "Chest": (2, 0, -10), "Head": (4, 0, -25),
         "RightUpperArm": (-70, 10, 15), "RightLowerArm": (-80, 0, 0)})
rev = interp_keys([k(0, B), k(12, B, REV), k(18, B, M(REV, {"RightUpperArm": (-74, 10, 18)})), k(40, B, REV), k(60, B)], 60)
for f, P in enumerate(rev):
    e = max(0.0, min(1.0, (f - 10) / 6.0, (46 - f) / 8.0))
    P["RightUpperArm#0"] = P.get("RightUpperArm#0", 0) + 1.5 * e * sin(f * 2.4)
    P["RightLowerArm#0"] = P.get("RightLowerArm#0", 0) + 2.0 * e * sin(f * 2.9)
clip("IdleRev", rev, spin=(0, 1, 9))
clip("TurnLeft90", interp_keys([k(0, B), k(4, B, turned(25, aL=45, aR=0, liftL=0.08)), k(8, B, turned(55, aL=90, aR=0)),
                                k(12, B, turned(80, aL=90, aR=50, liftR=0.08)), k(16, B, turned(90))], 16))
clip("TurnRight90", interp_keys([k(0, B), k(4, B, turned(-25, aR=-45, aL=0, liftR=0.08)), k(8, B, turned(-55, aR=-90, aL=0)),
                                 k(12, B, turned(-80, aR=-90, aL=-50, liftL=0.08)), k(16, B, turned(-90))], 16))
clip("Turn180", interp_keys([k(0, B), k(4, B, turned(30, aL=70, aR=0, liftL=0.08)), k(8, B, turned(70, aL=110, aR=0)),
                             k(12, B, turned(110, aL=110, aR=100, liftR=0.10)), k(16, B, turned(150, aL=180, aR=100, liftL=0.08)),
                             k(20, B, turned(175, aL=180, aR=180, liftR=0.08)), k(24, B, turned(180))], 24))
clip("RunStop", interp_keys([
    k(0, RUN0),
    k(4, B, M({"hips": (0, 0.10, -0.16), "Spine": (-12, 0, 0), "Chest": (-6, 0, 0), "footR": (0, -0.30, 0.02, -15, 0), "footL": (0, -0.05, 0, 0, 0)}, U((-40, -45, 0)), Lw(-30)), 'out'),
    k(9, B, M({"hips": (0, 0.02, -0.12), "Spine": (8, 0, 0), "footR": (0, -0.22, 0, 0, 0), "footL": (0, -0.05, 0, 0, 0)}, U((-20, -20, 0)), Lw(-30))),
    k(12, B, {"hips": (0, 0, -0.07), "footR": (0, -0.10, 0.05, 0, 0)}),
    k(14, B)], 14), wind=(0, -1.2, 0))
WG = gait(280, (0, -1), 0.20, 0.09, 0.6, -0.05, 0.015, 0.0, 0.03, 4, 22, 7, elbow=12, lowbase=-5)
RG = gait(180, (0, -1), 0.34, 0.20, 0.42, -0.10, 0.03, 0.2, 0.02, 14, 38, 10, guard=RUNARM, elbow=20)
w2r = []
ph = 0.0
phs = [0.0]
for f in range(22):
    u = (f + 0.5) / 22.0
    u = u * u * (3 - 2 * u)
    ph += (1 - u) / 28.0 + u / 18.0
    phs.append(ph)
for f in range(23):
    u = f / 22.0
    w = u * u * (3 - 2 * u)
    q = phs[f] / phs[-1]
    w2r.append(lerpflat(WG[int(round(q * 280)) % 280], RG[int(round(q * 180)) % 180], w))
clip("WalkToRun", w2r, wind=(0, -1.6, 0))


def crouch_idle(t):
    s = sin(2 * pi * t)
    return M(CROUCH, {"hips": (0, 0, -0.28 - 0.008 * s), "Spine": (22 + s, 0, 0), "Head": (-24, 0, 6 * sin(2 * pi * t + 1))})


clip("CrouchIdle", loop_fn(40, crouch_idle), loop=True)
CRG = M(U((-25, -10, 0)), Lw(-50))
clip("CrouchWalk", gait(28, (0, -1), 0.14, 0.07, 0.62, -0.26, 0.01, 0.0, 0.025, 34, 5, 4, pitchscale=0.5, guard=CRG, elbow=0), loop=True, wind=(0, -0.4, 0))

# ------------------------------------------------------------ traversal
clip("HardLand", interp_keys([
    k(0, AIR),
    k(2, AIR, M(feet(0, 0.03, 15), U((-70, -45, 0)))),
    k(5, B, M({"hips": (0, 0, -0.36), "Spine": (42, 0, 0), "Chest": (16, 0, 0), "Head": (-30, 0, 0)}, U((-35, -30, 0)), Lw(-20)), 'in'),
    k(12, B, M({"hips": (0, 0, -0.34), "Spine": (40, 0, 0), "Chest": (15, 0, 0), "Head": (-28, 0, 0)}, U((-30, -28, 0)), Lw(-25))),
    k(24, B)], 24), wind=(0, 0, 2.0))
clip("AirDash", interp_keys([
    k(0, AIR),
    k(4, AIR, M({"Hips": (50, 0, 0), "Spine": (10, 0, 0), "Chest": (5, 0, 0), "Head": (-45, 0, 0), "footL": (0, 0.30, 0.42, 70, 0), "footR": (0, 0.50, 0.50, 70, 0)}, U((55, -15, 0)), Lw(-10)), 'out'),
    k(9, AIR, M({"Hips": (46, 0, 0), "Spine": (10, 0, 0), "Chest": (5, 0, 0), "Head": (-42, 0, 0), "footL": (0, 0.32, 0.40, 70, 0), "footR": (0, 0.48, 0.50, 70, 0)}, U((50, -15, 0)), Lw(-10))),
    k(14, AIR)], 14), wind=(0, -3.0, 0))
clip("ClimbLedge", interp_keys([
    k(0, {}, M({"hips": (0, 0, 0.40), "Spine": (-5, 0, 0), "Head": (10, 0, 0)}, U((-170, -8, 0)), Lw(-10), feet(0.05, 0.40, 35))),
    k(10, {}, M({"hips": (0, -0.05, 1.00), "Spine": (5, 0, 0), "Head": (5, 0, 0)}, U((-110, -20, 0)), Lw(-100), feet(0.10, 1.00, 35))),
    k(20, {}, M({"hips": (0, -0.25, 1.75), "Spine": (45, 0, 0), "Chest": (10, 0, 0), "Head": (-30, 0, 0), "footR": (0, -0.35, 2.30, 0, 0), "footL": (0, 0.10, 1.60, 35, 0)}, U((-20, -25, 0)), Lw(-20))),
    k(30, {}, M({"hips": (0, -0.45, 2.00), "Spine": (30, 0, 0), "Chest": (10, 0, 0), "Head": (-20, 0, 0)}, U((-30, -10, 0)), Lw(-30), feet(-0.45, 2.30, 0))),
    k(40, B, M({"hips": (0, -0.45, 2.26)}, feet(-0.45, 2.30, 0)))], 40))
clip("Vault", interp_keys([
    k(0, B),
    k(4, B, M({"hips": (0, 0, -0.14), "Spine": (18, 0, 0)}, U((-40, -10, 0)), Lw(-30))),
    k(9, B, {"hips": (0.10, 0, 0.32), "Hips": (0, 12, 0), "Spine": (10, 14, 0), "LeftUpperArm": (-20, -25, 0), "LeftLowerArm": (5, 0, 0),
             "RightUpperArm": (-30, 60, 0), "RightLowerArm": (-30, 0, 0), "footL": (-0.30, -0.05, 0.70, 20, 0), "footR": (-0.25, -0.10, 0.80, 20, 0)}, 'out'),
    k(14, B, {"hips": (0.05, 0, 0.25), "Hips": (0, 8, 0), "Spine": (8, 8, 0), "LeftUpperArm": (10, -30, 0), "RightUpperArm": (-40, 40, 0),
              "footL": (-0.10, -0.15, 0.40, 10, 0), "footR": (-0.10, -0.20, 0.45, 10, 0)}),
    k(18, B, M({"hips": (0, 0, -0.18), "Spine": (22, 0, 0), "Chest": (8, 0, 0), "Head": (-16, 0, 0)}, U((-30, -20, 0)), Lw(-40)), 'in'),
    k(24, B)], 24))


def ladder(t):
    s = sin(2 * pi * t)
    return {"hips": (0, 0, 0.15 + 0.03 * sin(4 * pi * t)), "Spine": (5, 0, 0), "Chest": (2, 0, 0), "Head": (12, 0, 0),
            "LeftUpperArm": (-110 - 40 * s, -5, 0), "RightUpperArm": (-110 + 40 * s, 5, 0), "LeftLowerArm": (-60 + 30 * s, 0, 0), "RightLowerArm": (-60 - 30 * s, 0, 0),
            "footL": (0, -0.24, 0.30 - 0.20 * s, 0, 0), "footR": (0, -0.08, 0.30 + 0.20 * s, 0, 0)}


LAD = loop_fn(24, ladder)
clip("LadderUp", LAD, loop=True)
clip("LadderDown", list(reversed([dict(p) for p in LAD])), loop=True)


def swim(t):
    s = sin(2 * pi * t)
    c = cos(2 * pi * t)
    return {"Hips": (80, 0, 6 * s), "hips": (0, 0, 0.30), "Spine": (-8, 0, -8 * s), "Chest": (-8, 0, -10 * s), "Neck": (-25, 0, 0), "Head": (-35, 0, 0),
            "LeftUpperArm": (-75 - 95 * c, -15, 0), "RightUpperArm": (-75 + 95 * c, 15, 0), "LeftLowerArm": (-25 - 25 * s, 0, 0), "RightLowerArm": (-25 + 25 * s, 0, 0),
            "footL": (0, 0.47, 0.85 + 0.10 * sin(4 * pi * t), 160, 0), "footR": (0, 0.62, 0.85 - 0.10 * sin(4 * pi * t), 160, 0)}


clip("Swim", loop_fn(30, swim), loop=True, wind=(0, -0.8, 0))


def tread(t):
    s = sin(2 * pi * t)
    c = cos(2 * pi * t)
    return {"hips": (0, 0, 0.10 + 0.04 * sin(4 * pi * t)), "Spine": (4, 0, 0), "Chest": (2, 0, 0), "Head": (-8, 0, 0),
            "LeftUpperArm": (-30 + 15 * c, -60 + 10 * s, 0), "RightUpperArm": (-30 - 15 * c, 60 + 10 * s, 0), "LeftLowerArm": (-30, 0, 0), "RightLowerArm": (-30, 0, 0),
            "footL": (0.08 * c, -0.10 + 0.08 * s, 0.22 + 0.08 * s, 30, 0), "footR": (-0.08 * c, 0.08 - 0.08 * s, 0.22 - 0.08 * s, 30, 0)}


clip("TreadWater", loop_fn(40, tread), loop=True)
SLIDE = M({"Hips": (-55, 0, 0), "hips": (0, 0.12, -0.34), "Spine": (20, 0, 0), "Chest": (15, 0, 0), "Head": (20, 0, 0),
           "footR": (0, -0.52, -0.02, -45, 0), "footL": (0, -0.22, 0.0, -10, 0),
           "LeftUpperArm": (10, -45, 0), "LeftLowerArm": (-30, 0, 0), "RightUpperArm": (-40, 25, 0), "RightLowerArm": (-50, 0, 0)})
clip("Slide", interp_keys([k(0, RUN0), k(5, SLIDE, None, 'out'), k(14, SLIDE, {"hips": (0, 0.13, -0.35)}),
                           k(18, B, M({"hips": (0, 0.02, -0.24), "Spine": (25, 0, 0)}, U((-25, -15, 0)), Lw(-40))), k(22, B)], 22), wind=(0, -2.0, 0))

# ------------------------------------------------------------ attacks
clip("Heavy2", interp_keys([
    k(0, B),
    k(10, B, {"hips": (0, 0.03, -0.10), "Hips": (0, 0, -20), "Spine": (4, 0, -25), "Chest": (2, 0, -30), "Head": (-2, 0, 60),
              "RightUpperArm": (-40, 70, 0), "RightLowerArm": (-20, 0, 0), "LeftUpperArm": (-80, 0, -70), "LeftLowerArm": (-20, 0, 0)}),
    k(14, B, {"hips": (0, -0.08, -0.12), "Hips": (0, 0, 25), "Spine": (8, 0, 30), "Chest": (4, 0, 40), "Head": (-4, 0, -75),
              "RightUpperArm": (-80, 0, 60), "RightLowerArm": (0, 0, 0), "LeftUpperArm": (-40, -80, 0), "LeftLowerArm": (0, 0, 0)}, 'in'),
    k(18, B, {"hips": (0, -0.08, -0.12), "Hips": (0, 0, 30), "Spine": (8, 0, 34), "Chest": (4, 0, 48), "Head": (-4, 0, -85),
              "RightUpperArm": (-75, 0, 75), "RightLowerArm": (-10, 0, 0), "LeftUpperArm": (-20, -85, 0), "LeftLowerArm": (-10, 0, 0)}, 'out'),
    k(32, B)], 32), spin=(0, 5, 5))


def charge(t):
    s = sin(2 * pi * t)
    j = sin(2 * pi * 6 * t)
    return M({"hips": (0, 0.04, -0.12 - 0.01 * s), "Spine": (-6 + 0.6 * j, 0, 0), "Chest": (-6, 0, 0), "Head": (6, 0, 0)}, U((-150 + 1.5 * j, -15, 0)), Lw(-50 + 2 * j))


clip("HeavyCharge", loop_fn(30, charge), loop=True, spin=(0, 8, 8))
clip("Kick", interp_keys([
    k(0, B),
    k(6, B, M({"hips": (0, 0.02, -0.03), "Spine": (-8, 0, 0), "footR": (0, -0.10, 0.45, 20, 0)}, U((-40, -10, -10)), Lw(-70))),
    k(9, B, M({"hips": (0, -0.05, 0.0), "Spine": (-16, 0, 0), "Chest": (-6, 0, 0), "Head": (14, 0, 0), "footR": (0, -0.62, 0.62, -20, 0)}, U((-30, -25, 0)), Lw(-60)), 'in'),
    k(12, B, M({"hips": (0, -0.05, 0.0), "Spine": (-16, 0, 0), "Chest": (-6, 0, 0), "Head": (14, 0, 0), "footR": (0, -0.60, 0.60, -20, 0)}, U((-30, -25, 0)), Lw(-60))),
    k(17, B, M({"hips": (0, 0.02, -0.03), "Spine": (-6, 0, 0), "footR": (0, -0.10, 0.40, 20, 0)}, U((-40, -10, -10)), Lw(-70))),
    k(26, B)], 26))
clip("RunAttack", interp_keys([
    k(0, RUN0),
    k(5, B, {"hips": (0, 0, -0.10), "Spine": (10, 0, -15), "Chest": (4, 0, -20), "Head": (-6, 0, 30), "RightUpperArm": (-150, 25, 0), "RightLowerArm": (-50, 0, 0),
             "LeftUpperArm": (-40, 0, -10), "LeftLowerArm": (-60, 0, 0), "footR": (0, -0.10, 0.08, 0, 0)}),
    k(8, B, {"hips": (0, -0.15, -0.16), "Spine": (30, 0, 20), "Chest": (10, 0, 25), "Head": (-25, 0, -40), "RightUpperArm": (-50, 0, 30), "RightLowerArm": (0, 0, 0),
             "LeftUpperArm": (20, -20, 0), "LeftLowerArm": (-60, 0, 0), "footR": (0, -0.30, 0, 0, 0)}, 'in'),
    k(12, B, {"hips": (0, -0.16, -0.17), "Spine": (32, 0, 22), "Chest": (10, 0, 28), "Head": (-26, 0, -44), "RightUpperArm": (-40, 0, 35), "RightLowerArm": (0, 0, 0),
              "LeftUpperArm": (20, -20, 0), "LeftLowerArm": (-60, 0, 0), "footR": (0, -0.30, 0, 0, 0)}),
    k(17, B, {"hips": (0, -0.06, -0.08), "Spine": (10, 0, 0), "footR": (0, -0.14, 0.06, 0, 0)}),
    k(20, B)], 20), wind=(0, -1.2, 0), spin=(0, 1, 4))
clip("CrouchAttack", interp_keys([
    k(0, CROUCH),
    k(5, CROUCH, {"Hips": (0, 0, 10), "Spine": (22, 0, 15), "Chest": (8, 0, 20), "Head": (-24, 0, -40), "LeftUpperArm": (-10, -70, 0), "LeftLowerArm": (-20, 0, 0)}),
    k(8, CROUCH, {"Hips": (0, 0, -12), "Spine": (24, 0, -18), "Chest": (8, 0, -28), "Head": (-24, 0, 50), "LeftUpperArm": (-75, 0, -45), "LeftLowerArm": (0, 0, 0)}, 'in'),
    k(11, CROUCH, {"Hips": (0, 0, -14), "Spine": (24, 0, -20), "Chest": (8, 0, -32), "Head": (-24, 0, 55), "LeftUpperArm": (-70, 0, -60), "LeftLowerArm": (-10, 0, 0)}),
    k(18, CROUCH)], 18), spin=(0, 4, 1))
clip("JumpPunch", interp_keys([
    k(0, AIR),
    k(6, AIR, M({"Spine": (-15, 0, 0), "Chest": (-12, 0, 0), "Head": (10, 0, 0), "footL": (0, 0.15, 0.30, 50, 0), "footR": (0, 0.25, 0.28, 50, 0)}, U((-170, -10, 0)), Lw(-30))),
    k(9, AIR, M({"Spine": (35, 0, 0), "Chest": (18, 0, 0), "Head": (-25, 0, 0), "footL": (0, -0.20, 0.30, 0, 0), "footR": (0, -0.15, 0.25, 0, 0)}, U((-50, 0, -6)), Lw(-10)), 'in'),
    k(12, AIR, M({"Spine": (37, 0, 0), "Chest": (19, 0, 0), "Head": (-26, 0, 0), "footL": (0, -0.20, 0.30, 0, 0), "footR": (0, -0.15, 0.25, 0, 0)}, U((-45, 0, -6)), Lw(-10))),
    k(18, AIR)], 18), spin=(0, 4, 4))
clip("JumpKick", interp_keys([
    k(0, AIR),
    k(5, AIR, M({"Spine": (-10, 0, 0), "footR": (0, -0.15, 0.50, 20, 0), "footL": (0, 0.10, 0.25, 40, 0)})),
    k(8, AIR, M({"Hips": (-15, 0, 0), "Spine": (-12, 0, 0), "Head": (20, 0, 0), "footR": (0, -0.60, 0.50, -20, 0), "footL": (0, 0.15, 0.32, 50, 0)}, U((-30, -45, 0))), 'in'),
    k(11, AIR, M({"Hips": (-15, 0, 0), "Spine": (-12, 0, 0), "Head": (20, 0, 0), "footR": (0, -0.58, 0.50, -20, 0), "footL": (0, 0.15, 0.32, 50, 0)}, U((-30, -45, 0)))),
    k(18, AIR)], 18))
clip("GroundSlam", interp_keys([
    k(0, AIR),
    k(6, AIR, M({"Spine": (-12, 0, 0), "Chest": (-10, 0, 0), "footL": (0, 0.10, 0.35, 45, 0), "footR": (0, 0.20, 0.32, 45, 0)}, U((-165, -12, 0)), Lw(-40))),
    k(10, AIR, M({"Hips": (15, 0, 0), "Spine": (20, 0, 0), "Head": (-20, 0, 0), "footL": (0, 0, 0.10, 20, 0), "footR": (0, 0, 0.10, 20, 0)}, U((-100, -5, 0)), Lw(0))),
    k(12, B, M({"hips": (0, -0.05, -0.36), "Spine": (45, 0, 0), "Chest": (15, 0, 0), "Head": (-35, 0, 0)}, U((-62, 0, -8)), Lw(0)), 'in'),
    k(20, B, M({"hips": (0, -0.05, -0.35), "Spine": (44, 0, 0), "Chest": (15, 0, 0), "Head": (-34, 0, 0)}, U((-60, 0, -8)), Lw(0))),
    k(30, B)], 30), wind=(0, 0, 2.5), spin=(0, 6, 6))

# ------------------------------------------------------------ defence
clip("BlockStart", interp_keys([k(0, B), k(6, GUARD, None, 'out')], 6))
clip("BlockHit", interp_keys([
    k(0, GUARD),
    k(2, GUARD, M({"hips": (0, 0.07, -0.11), "Spine": (2, 0, 0), "Chest": (0, 0, 0), "Head": (-2, 0, 0)}, U((-64, 0, -26)), Lw(-92)), 'out'),
    k(10, GUARD)], 10))
clip("GuardBreak", interp_keys([
    k(0, GUARD),
    k(3, B, M({"hips": (0, 0.12, -0.02), "Spine": (-18, 0, 0), "Chest": (-14, 0, 0), "Head": (-16, 0, 0)}, U((-40, -80, 0)), Lw(-20)), 'out'),
    k(10, B, M({"hips": (-0.04, 0.16, -0.06), "Spine": (-8, -6, 0), "Chest": (-6, 0, 0), "Head": (-6, 0, 12), "footL": (0, 0.18, 0, 0, 0)}, U((-10, -50, 0)), Lw(-30))),
    k(18, B, M({"hips": (0.03, 0.10, -0.08), "Spine": (10, 5, 0), "Head": (6, 0, -8), "footL": (0, 0.18, 0, 0, 0)}, U((5, -20, 0)), Lw(-20))),
    k(23, B, {"hips": (0, 0.04, -0.05), "footL": (0, 0.09, 0.05, 0, 0)}),
    k(26, B)], 26))
clip("Parry", interp_keys([
    k(0, B),
    k(3, B, {"hips": (0, 0, -0.07), "Chest": (2, 0, 12), "RightUpperArm": (-80, 0, 35), "RightLowerArm": (-70, 0, 0)}, 'out'),
    k(5, B, {"hips": (0, 0, -0.07), "Chest": (2, 0, -15), "Head": (-2, 0, 12), "RightUpperArm": (-70, 40, 0), "RightLowerArm": (-50, 0, 0)}, 'in'),
    k(8, B, {"hips": (0, 0, -0.07), "Chest": (2, 0, -18), "Head": (-2, 0, 14), "RightUpperArm": (-66, 46, 0), "RightLowerArm": (-45, 0, 0)}),
    k(14, B)], 14), spin=(0, 1, 3))
clip("DodgeForward", interp_keys([
    k(0, B),
    k(3, B, M({"hips": (0, 0, -0.16), "Spine": (20, 0, 0)}, U((-10, -10, 0)), Lw(-40))),
    k(7, B, M({"hips": (0, -0.15, -0.30), "Spine": (45, 0, 0), "Chest": (10, 0, 0), "Head": (-40, 0, 0), "footR": (0, -0.25, 0, 0, 0), "footL": (0, 0.25, 0.05, 40, 0)}, U((40, -15, 0)), Lw(-20)), 'out'),
    k(12, B, M({"hips": (0, -0.16, -0.28), "Spine": (42, 0, 0), "Chest": (10, 0, 0), "Head": (-38, 0, 0), "footR": (0, -0.25, 0, 0, 0), "footL": (0, 0.22, 0.03, 35, 0)}, U((36, -15, 0)), Lw(-20))),
    k(16, B, {"hips": (0, -0.06, -0.12), "Spine": (14, 0, 0), "footR": (0, -0.12, 0.05, 0, 0), "footL": (0, 0.10, 0.05, 10, 0)}),
    k(20, B)], 20), wind=(0, -1.5, 0))
DL = [
    k(0, B),
    k(3, B, M({"hips": (-0.03, 0, -0.14), "Spine": (10, 6, 0)}, U((-20, -5, 0)), Lw(-40))),
    k(6, B, M({"hips": (0.10, 0, 0.02), "Spine": (0, -12, 0), "Chest": (0, -6, 0), "footL": (-0.06, 0, 0.14, 10, 0), "footR": (-0.12, 0, 0.18, 10, 0)}, U((-45, -35, 0)), Lw(-30)), 'out'),
    k(9, B, M({"hips": (0.10, 0, 0.03), "Spine": (0, -6, 0), "footL": (-0.02, 0, 0.10, 5, 0), "footR": (-0.06, 0, 0.12, 5, 0)}, U((-40, -35, 0)), Lw(-30))),
    k(12, B, M({"hips": (0.03, 0, -0.16), "Spine": (14, 4, 0), "Chest": (6, 0, 0), "Head": (-12, 0, 0)}, U((-30, -15, 0)), Lw(-40)), 'in'),
    k(18, B)]
clip("DodgeLeft", interp_keys(DL, 18), wind=(1.5, 0, 0))
clip("DodgeRight", interp_keys(mk(DL), 18), wind=(-1.5, 0, 0))

# ------------------------------------------------------------ reactions
HB_ = {"hips": (0, -0.07, -0.03), "Spine": (18, 0, -6), "Chest": (14, 0, -8), "Neck": (8, 0, 0), "Head": (-22, 0, 10),
       "LeftUpperArm": (25, -20, 0), "RightUpperArm": (25, 20, 0), "LeftLowerArm": (-15, 0, 0), "RightLowerArm": (-15, 0, 0)}
clip("HitBack", interp_keys([k(0, B), k(3, B, HB_, 'out'), k(7, B, M({kk: tuple(x * 0.4 for x in v) for kk, v in HB_.items()}, {"Head": (10, 0, 4)})), k(14, B)], 14))
clip("HitHeavy", interp_keys([
    k(0, B),
    k(3, B, M({"hips": (0, 0.14, -0.06), "Hips": (0, 0, 12), "Spine": (-22, 0, 14), "Chest": (-20, 0, 16), "Neck": (-12, 0, 0), "Head": (-22, 0, -20),
               "LeftUpperArm": (-30, -45, 0), "RightUpperArm": (-50, 35, 0)}, Lw(-25)), 'out'),
    k(8, B, M({"hips": (0, 0.20, -0.10), "Hips": (0, 0, 8), "Spine": (-6, 0, 8), "Chest": (-4, 0, 8), "Head": (6, 0, -10), "footL": (0, 0.22, 0, 0, 0)}, U((-10, -25, 0)), Lw(-30))),
    k(14, B, {"hips": (0, 0.12, -0.10), "Spine": (12, 0, 0), "Head": (4, 0, 0), "footL": (0, 0.22, 0, 0, 0)}),
    k(19, B, {"hips": (0, 0.04, -0.05), "footL": (0, 0.10, 0.06, 0, 0)}),
    k(22, B)], 22))
clip("Stagger", interp_keys([
    k(0, B),
    k(5, B, M({"hips": (0.08, 0.06, -0.08), "Hips": (0, 0, 8), "Spine": (-8, 10, 0), "Chest": (-4, 6, 0), "Head": (-8, -10, 10), "footL": (0.10, 0.06, 0, 0, 0)}, U((0, -30, 0)), Lw(-20))),
    k(12, B, M({"hips": (-0.08, 0.10, -0.10), "Hips": (0, 0, -8), "Spine": (6, -12, 0), "Chest": (4, -6, 0), "Head": (10, 10, -12), "footL": (0.10, 0.06, 0, 0, 0), "footR": (-0.10, 0.12, 0, 0, 0)}, U((10, -35, 0)), Lw(-25))),
    k(20, B, M({"hips": (0.05, 0.03, -0.10), "Spine": (14, 6, 0), "Head": (14, 0, 8), "footL": (0.04, 0.02, 0, 0, 0), "footR": (-0.10, 0.12, 0, 0, 0)}, U((5, -20, 0)), Lw(-20))),
    k(28, B, {"hips": (-0.02, 0, -0.07), "Spine": (6, -3, 0), "Head": (2, 0, -4), "footR": (-0.04, 0.05, 0.04, 0, 0)}),
    k(36, B)], 36))
clip("KnockdownFront", interp_keys([
    k(0, B),
    k(3, B, HB_, 'out'),
    k(8, B, M({"Hips": (40, 0, 0), "hips": (0, -0.28, -0.22), "Spine": (10, 0, 0), "Head": (-30, 0, 0), "footL": (0, 0, 0.02, 40, 0), "footR": (0, 0.08, 0.02, 40, 0)}, U((-110, -30, 0)), Lw(-30))),
    k(13, PRONE, {"footL": (0, 0, 0.12, 140, 0), "footR": (0, 0.17, 0.16, 140, 0)}, 'in'),
    k(17, PRONE, {"hips": (0, -0.50, -0.37)}),
    k(21, PRONE),
    k(30, PRONE)], 30))
clip("GetUpFront", interp_keys([
    k(0, PRONE),
    k(8, B, M({"Hips": (60, 0, 0), "hips": (0, -0.38, -0.28), "Spine": (-15, 0, 0), "Chest": (-10, 0, 0), "Head": (-30, 0, 0), "footL": (0, 0, 0.05, 80, 0), "footR": (0, 0.17, 0.05, 80, 0)}, U((-95, -35, 0)), Lw(-10))),
    k(16, B, M({"Hips": (30, 0, 0), "hips": (0, -0.12, -0.36), "Spine": (20, 0, 0), "Chest": (8, 0, 0), "Head": (-30, 0, 0), "footL": (0, 0, 0, 0, 0), "footR": (0, 0.10, 0.0, 40, 0)}, U((-50, -15, 0)), Lw(-30))),
    k(26, B, M({"Hips": (8, 0, 0), "hips": (0, -0.02, -0.16), "Spine": (16, 0, 0), "Chest": (6, 0, 0), "Head": (-10, 0, 0)}, U((-20, -5, 0)), Lw(-25))),
    k(36, B)], 36))


def launched(t):
    s = sin(2 * pi * t)
    c = cos(2 * pi * t)
    return {"Hips": (-70 + 6 * s, 0, 0), "hips": (0, 0, 0.30), "Spine": (-10, 0, 0), "Chest": (-8, 0, 0), "Head": (25, 0, 0),
            "LeftUpperArm": (-60 + 15 * s, -50, 0), "RightUpperArm": (-60 - 15 * s, 50, 0), "LeftLowerArm": (-30 + 15 * c, 0, 0), "RightLowerArm": (-30 - 15 * c, 0, 0),
            "footL": (0, -0.45, 0.75 + 0.10 * s, -40, 0), "footR": (0, -0.40, 0.65 - 0.10 * s, -40, 0)}


clip("Launched", loop_fn(20, launched), loop=True, wind=(0, 0, 1.5))
SPLAT = M({"hips": (0, 0.16, 0.05), "Spine": (-6, 0, 0), "Chest": (-8, 0, 0), "Neck": (-10, 0, 0), "Head": (-18, 0, 0), "footL": (0.06, 0, 0.05, 20, 0), "footR": (-0.06, 0.05, 0.05, 20, 0)},
          U((0, -85, 0)), Lw(-15))
clip("WallSplat", interp_keys([
    k(0, B),
    k(3, B, SPLAT, 'out'),
    k(12, B, M(SPLAT, {"hips": (0, 0.16, 0.03), "Head": (-10, 0, 8)})),
    k(20, B, M({"hips": (0, 0.14, -0.28), "Spine": (10, 0, 0), "Chest": (6, 0, 0), "Head": (25, 0, 6)}, U((0, -40, 0)), Lw(-15)), 'in'),
    k(26, B, M({"hips": (0, 0.06, -0.20), "Spine": (16, 0, 0), "Head": (10, 0, 0)}, U((-10, -15, 0)), Lw(-25))),
    k(34, B)], 34))


def stunned(t):
    s = sin(2 * pi * t)
    c = cos(2 * pi * t)
    return M({"hips": (0.04 * s, 0.03 * c, -0.08), "Spine": (6 + 4 * c, 5 * s, 0), "Chest": (4, 3 * s, 0), "Neck": (6 * c, 6 * s, 0), "Head": (14 + 8 * c, 10 * s, 8 * s),
              "LeftUpperArm": (6 + 3 * c, -6, 0), "RightUpperArm": (6 - 3 * c, 6, 0)}, Lw(-8))


clip("Stunned", loop_fn(40, stunned), loop=True)
clip("DeathForward", interp_keys([
    k(0, B),
    k(4, B, M({kk: tuple(x * 1.3 for x in v) for kk, v in HB_.items()}), 'out'),
    k(14, KNEEL, {"Spine": (20, 0, 0), "Chest": (10, 0, 0), "Head": (20, 0, 8)}),
    k(22, KNEEL, {"Spine": (26, 4, 0), "Head": (26, 0, -6)}),
    k(30, PRONE, {"Head": (-15, 0, -35)}, 'in'),
    k(34, PRONE, {"hips": (0, -0.50, -0.37), "Head": (-15, 0, -35)}),
    k(38, PRONE, {"Head": (-15, 0, -35)}),
    k(46, PRONE, {"Head": (-15, 0, -35)})], 46), spin=(0, 3, 3), spinfn=lambda t: min(1.0, 1 - (1 - min(1.0, t / 0.9)) ** 2))
clip("DeathKneel", interp_keys([
    k(0, B),
    k(4, B, M({kk: tuple(x * 1.2 for x in v) for kk, v in HIT.items()}), 'out'),
    k(12, B, M({"hips": (0, 0.06, -0.16), "Spine": (10, 0, 0), "Head": (12, 0, 0)}, U((4, -8, 0)))),
    k(22, KNEEL, {"Spine": (15, 0, 0), "Chest": (8, 0, 0), "Head": (10, 0, 0)}, 'in'),
    k(30, KNEEL, {"Spine": (28, 0, 0), "Chest": (18, 0, 0), "Head": (24, 0, 0)}),
    k(38, KNEEL),
    k(44, KNEEL)], 44), spin=(0, 3, 3), spinfn=lambda t: min(1.0, 1 - (1 - min(1.0, t / 0.9)) ** 2))

# ------------------------------------------------------------ grabs
clip("GrabStart", interp_keys([
    k(0, B),
    k(5, B, M({"hips": (0, 0.03, -0.08), "Spine": (4, 0, 0)}, U((-50, -60, 0)), Lw(-30))),
    k(9, GRAB, M({"hips": (0, -0.13, -0.09)}, U((-86, 0, -26))), 'in'),
    k(16, GRAB)], 16))


def grabhold(t):
    j = sin(2 * pi * 4 * t)
    s = sin(2 * pi * t)
    return M(GRAB, {"hips": (0, -0.10, -0.08 - 0.006 * s), "Spine": (14 + 0.6 * j, 0, 2 * s), "LeftUpperArm": (-82 + j, 0, -22), "RightUpperArm": (-82 - j, 0, 22)})


clip("GrabHold", loop_fn(30, grabhold), loop=True)
clip("Throw", interp_keys([
    k(0, GRAB),
    k(6, GRAB, {"hips": (0, -0.04, -0.16), "Hips": (0, 0, -18), "Spine": (18, 0, -22), "Chest": (8, 0, -26), "Head": (-14, 0, 50)}),
    k(10, GRAB, M({"hips": (0, -0.06, -0.04), "Hips": (0, 0, 28), "Spine": (0, 0, 34), "Chest": (-4, 0, 44), "Head": (-6, 0, -80)}, U((-120, 0, -10)), Lw(-10)), 'in'),
    k(14, B, {"hips": (0, -0.04, -0.05), "Hips": (0, 0, 32), "Spine": (4, 0, 38), "Chest": (0, 0, 50), "Head": (-4, 0, -90),
              "LeftUpperArm": (-60, -70, 0), "RightUpperArm": (-100, 0, 60)}, 'out'),
    k(26, B)], 26))


def grabbed(t):
    s = sin(2 * pi * 2 * t)
    c = cos(2 * pi * 2 * t)
    return M({"hips": (0, 0.04, 0.10), "Spine": (-10, 0, 4 * s), "Chest": (-8, 0, 0), "Neck": (-6, 0, 0), "Head": (-12, 0, 18 * s),
              "footL": (0, -0.05 + 0.10 * s, 0.14 + 0.05 * c, 30, 0), "footR": (0, 0.02 - 0.10 * s, 0.14 - 0.05 * c, 30, 0)}, U((10 + 3 * c, 2, 0)), Lw(-20 + 6 * s))


clip("Grabbed", loop_fn(30, grabbed), loop=True)
GRIND = M(GRAB, {"hips": (0, -0.14, -0.12), "Spine": (30, 0, 0), "Chest": (16, 0, 0), "Neck": (12, 0, 0), "Head": (8, 0, 0)}, U((-70, 0, -30)), Lw(-60))
fin = interp_keys([
    k(0, GRAB),
    k(8, GRAB, M({"hips": (0, 0.0, -0.06), "Spine": (-8, 0, 0), "Chest": (-8, 0, 0), "Neck": (-8, 0, 0), "Head": (-12, 0, 0)}, U((-78, 0, -26)), Lw(-55))),
    k(14, GRIND, None, 'in'),
    k(40, GRIND, {"hips": (0, -0.15, -0.14)}),
    k(46, GRAB, M({"hips": (0, -0.14, -0.06), "Spine": (10, 0, 0)}, U((-90, 0, -8)), Lw(5)), 'in'),
    k(50, GRAB, M({"hips": (0, -0.14, -0.06), "Spine": (10, 0, 0)}, U((-88, 0, -8)), Lw(5))),
    k(60, B)], 60)
for f, P in enumerate(fin):
    e = max(0.0, min(1.0, (f - 13) / 3.0, (41 - f) / 3.0))
    P["Head#0"] = P.get("Head#0", 0) + 3 * e * sin(f * 2.6)
    P["Spine#0"] = P.get("Spine#0", 0) + 1.5 * e * sin(f * 2.1)
    P["hips#2"] = P.get("hips#2", 0) + 0.006 * e * sin(f * 2.3)
clip("FinisherHeadGrind", fin, headspin=12, spin=(0, 2, 2))

# ------------------------------------------------------------ open world
clip("PickUp", interp_keys([
    k(0, B),
    k(10, B, {"hips": (0, -0.04, -0.34), "Spine": (38, 0, -6), "Chest": (14, 0, -8), "Head": (-10, 0, 0), "RightUpperArm": (-55, 0, 12), "RightLowerArm": (5, 0, 0), "LeftUpperArm": (10, -15, 0)}),
    k(15, B, {"hips": (0, -0.04, -0.35), "Spine": (40, 0, -6), "Chest": (14, 0, -8), "Head": (-10, 0, 0), "RightUpperArm": (-50, 0, 14), "RightLowerArm": (-10, 0, 0), "LeftUpperArm": (10, -15, 0)}),
    k(30, B)], 30))
clip("Interact", interp_keys([
    k(0, B),
    k(8, B, {"Spine": (6, 0, 6), "Chest": (4, 0, 10), "Head": (-4, 0, -12), "RightUpperArm": (-78, 0, 10), "RightLowerArm": (5, 0, 0)}),
    k(11, B, {"hips": (0, -0.03, -0.04), "Spine": (8, 0, 8), "Chest": (4, 0, 12), "Head": (-4, 0, -14), "RightUpperArm": (-84, 0, 10), "RightLowerArm": (12, 0, 0)}, 'in'),
    k(14, B, {"Spine": (6, 0, 6), "Chest": (4, 0, 10), "Head": (-4, 0, -12), "RightUpperArm": (-76, 0, 10), "RightLowerArm": (0, 0, 0)}),
    k(24, B)], 24))
clip("OpenDoor", interp_keys([
    k(0, B),
    k(8, B, {"Spine": (4, 0, 8), "Chest": (2, 0, 12), "Head": (-2, 0, -14), "RightUpperArm": (-70, 0, 8), "RightLowerArm": (-40, 0, 0)}),
    k(18, B, {"hips": (0, -0.12, -0.07), "Spine": (14, 0, 12), "Chest": (6, 0, 18), "Head": (-10, 0, -22), "RightUpperArm": (-86, 0, 6), "RightLowerArm": (10, 0, 0), "footR": (0, -0.18, 0, 0, 0)}),
    k(22, B, {"hips": (0, -0.12, -0.07), "Spine": (14, 0, 12), "Chest": (6, 0, 18), "Head": (-10, 0, -22), "RightUpperArm": (-84, 0, 6), "RightLowerArm": (8, 0, 0), "footR": (0, -0.18, 0, 0, 0)}),
    k(27, B, {"hips": (0, -0.05, -0.05), "footR": (0, -0.09, 0.05, 0, 0)}),
    k(30, B)], 30))
PG = M(U((-80, 0, -5)), Lw(-10))
clip("PushObject", gait(32, (0, -1), 0.13, 0.05, 0.66, -0.14, 0.008, 0.0, 0.02, 40, 0, 3, pitchscale=0.6, guard=PG, elbow=0), loop=True)


def talk(t):
    p = idle(t)
    g1 = max(0.0, sin(2 * pi * t)) ** 2
    g2 = max(0.0, sin(2 * pi * t + pi)) ** 2
    b = sin(2 * pi * 3 * t)
    p["RightUpperArm"] = (-50 * g1 + 4 * b * g1, 10 * g1, 10 * g1)
    p["RightLowerArm"] = (-60 * g1, 0, 0)
    p["LeftUpperArm"] = (-35 * g2, -20 * g2, 0)
    p["LeftLowerArm"] = (-45 * g2, 0, 0)
    p["Head"] = (-2 + 3 * b, 0, 8 * sin(2 * pi * t))
    p["Chest"] = (p["Chest"][0], 0, 5 * sin(2 * pi * t))
    return p


clip("Talk", loop_fn(60, talk), loop=True)


def listen(t):
    p = idle(t)
    p["Head"] = (-2 + 2 * sin(2 * pi * 2 * t), 8, 6)
    p["Neck"] = (0, 4, 0)
    return p


clip("Listen", loop_fn(60, listen), loop=True)
clip("Nod", interp_keys([k(0, B), k(4, B, {"Head": (16, 0, 0), "Neck": (6, 0, 0)}), k(8, B, {"Head": (-6, 0, 0)}), k(12, B, {"Head": (12, 0, 0), "Neck": (4, 0, 0)}), k(20, B)], 20))
clip("ShakeHead", interp_keys([k(0, B), k(4, B, {"Head": (-2, 0, 28), "Neck": (0, 0, 8)}), k(9, B, {"Head": (-2, 0, -28), "Neck": (0, 0, -8)}),
                               k(14, B, {"Head": (-2, 0, 20), "Neck": (0, 0, 6)}), k(19, B, {"Head": (-2, 0, -12)}), k(24, B)], 24))
SD = interp_keys([k(0, B), k(10, B, M({"hips": (0, 0.14, -0.20), "Spine": (28, 0, 0), "Chest": (8, 0, 0), "Head": (-20, 0, 0)}, U((-30, -8, 0)), Lw(-30))), k(20, SIT, None, 'in'), k(24, SIT)], 24)
clip("SitDown", SD)


def sitidle(t):
    s = sin(2 * pi * t)
    return M(SIT, {"Spine": (8 + s, 0, 0), "Chest": (4 + 1.2 * s, 0, 0), "Head": (-6 - s, 0, 4 * sin(2 * pi * t + 1))})


clip("SitIdle", loop_fn(60, sitidle), loop=True)
clip("SitUp", list(reversed([dict(p) for p in SD])))
RS = interp_keys([k(0, B), k(10, B, M({"hips": (0, 0.10, -0.32), "Spine": (36, 0, 0), "Chest": (10, 0, 0), "Head": (-24, 0, 0)}, U((-20, -10, 0)), Lw(-30))),
                  k(22, REST, None, 'in'), k(28, REST)], 28)
clip("RestStart", RS)


def restloop(t):
    s = sin(2 * pi * t)
    return M(REST, {"Spine": (22 + s, 0, 0), "Chest": (12 + 1.2 * s, 0, 0), "Head": (-10 - s, 0, 5 * sin(2 * pi * t + 1))})


clip("RestLoop", loop_fn(60, restloop), loop=True)
clip("RestEnd", list(reversed([dict(p) for p in RS])))


def sleep(t):
    s = sin(2 * pi * t)
    return M(LYING, {"Chest": (4 - 2.0 * s, 0, 0), "Spine": (4 - 1.0 * s, 0, 0), "Head": (10, 0, 20)}, U((18, -30 - 1.5 * s, 0)))


clip("Sleep", loop_fn(80, sleep), loop=True, spin=(0, 0, 0))
ITEM = {"Spine": (-4, 0, 0), "Chest": (-4, 0, 0), "Head": (-14, 0, 0), "RightUpperArm": (-72, 0, 14), "RightLowerArm": (-112, 0, 0)}
clip("UseItem", interp_keys([k(0, B), k(10, B, ITEM), k(26, B, M(ITEM, {"Head": (-20, 0, 0), "RightLowerArm": (-118, 0, 0)})), k(40, B)], 40))
clip("Equip", interp_keys([
    k(0, B),
    k(8, B, {"Spine": (-4, 0, -8), "Chest": (-4, 0, -12), "Head": (-2, 0, 20), "RightUpperArm": (-150, 25, 0), "RightLowerArm": (-115, 0, 0)}),
    k(12, B, {"Spine": (-4, 0, -8), "Chest": (-4, 0, -12), "Head": (-2, 0, 20), "RightUpperArm": (-155, 25, 0), "RightLowerArm": (-120, 0, 0)}),
    k(18, B, {"Spine": (6, 0, 8), "Chest": (4, 0, 10), "Head": (-4, 0, -14), "RightUpperArm": (-70, 0, 10), "RightLowerArm": (-30, 0, 0)}, 'in'),
    k(24, B)], 24))

# ------------------------------------------------------------ emotes
TA = M({"hips": (0, 0, -0.10), "Spine": (-6, 0, 0), "Chest": (-10, 0, 0), "Head": (14, 0, 0)}, U((-20, -75, 0)), Lw(-45))
ta = interp_keys([k(0, B), k(10, B, TA), k(36, B, M(TA, {"hips": (0, -0.03, -0.12), "Spine": (2, 0, 0), "Head": (10, 0, 0)})), k(50, B)], 50)
for f, P in enumerate(ta):
    e = max(0.0, min(1.0, (f - 9) / 4.0, (38 - f) / 5.0))
    P["Head#2"] = P.get("Head#2", 0) + 8 * e * sin(f * 1.3)
    P["Chest#0"] = P.get("Chest#0", 0) + 2 * e * sin(f * 2.2)
clip("Taunt", ta, spin=(0, 10, 10))
VU = M({"hips": (0, 0, 0.0), "Spine": (-8, 0, 0), "Chest": (-8, 0, 0), "Head": (-10, 0, 0)}, U((-165, -22, 0)), Lw(-20))
VD = M({"hips": (0, 0, -0.10), "Spine": (0, 0, 0), "Chest": (-4, 0, 0), "Head": (-6, 0, 0)}, U((-140, -28, 0)), Lw(-70))
clip("Victory", interp_keys([k(0, B), k(10, B, VU, 'out'), k(18, B, VD), k(26, B, VU), k(34, B, VD), k(42, B, VU), k(60, B)], 60), spin=(0, 6, 6))
clip("Defeat", interp_keys([
    k(0, B),
    k(14, B, M({"hips": (0, 0.02, -0.10), "Spine": (16, 0, 0), "Chest": (12, 0, 0), "Neck": (10, 0, 0), "Head": (22, 0, 0)}, U((6, -4, 0)), Lw(-4))),
    k(30, KNEEL, {"Spine": (24, 0, 0), "Chest": (14, 0, 0), "Head": (26, 0, 0)}, 'in'),
    k(40, KNEEL),
    k(50, KNEEL)], 50), spin=(0, 1, 1), spinfn=lambda t: min(1.0, 1 - (1 - min(1.0, t / 0.9)) ** 2))
CL = M({"hips": (0, 0, -0.08), "Spine": (6, 0, 0), "Chest": (4, 0, 0), "Head": (-6, 0, 0)}, U((-70, 0, -32)), Lw(-60))
clip("Spawn", interp_keys([
    k(0, B, M({"hips": (0, 0, -0.36), "Spine": (42, 0, 0), "Chest": (16, 0, 0), "Head": (10, 0, 0)}, U((-35, -30, 0)), Lw(-20))),
    k(10, B, M({"hips": (0, 0, -0.34), "Spine": (40, 0, 0), "Chest": (15, 0, 0), "Head": (-28, 0, 0)}, U((-30, -28, 0)), Lw(-25))),
    k(22, B, M({"hips": (0, 0, -0.06), "Spine": (-4, 0, 0), "Chest": (-6, 0, 0)}, U((-40, -70, 0)), Lw(-40))),
    k(26, B, CL, 'in'),
    k(29, B, M(CL, U((-60, -30, 0)))),
    k(32, B, CL, 'in'),
    k(36, B, M(CL, U((-64, -20, 0)))),
    k(50, B)], 50), spin=(0, 5, 5))


def lowhealth(t):
    s = sin(2 * pi * 2 * t)
    return M({"hips": (0.02, 0, -0.10 - 0.015 * s), "Spine": (18 + 2.5 * s, -4, 0), "Chest": (10 + 3 * s, -3, 0), "Neck": (6, 0, 0), "Head": (10 - 2 * s, 0, 6),
              "LeftUpperArm": (6, -4, 0), "LeftLowerArm": (-6, 0, 0), "RightUpperArm": (-25, 0, 40), "RightLowerArm": (-95, 0, 0)})


clip("LowHealthIdle", loop_fn(60, lowhealth), loop=True)

made = {}
for name, (poses, kw) in CLIPS.items():
    a = bake(name, [dict(p) for p in poses], **kw)
    made[name] = len(poses) - 1
ao.animation_data.action = bpy.data.actions["Idle"]
ao.animation_data.action_slot = bpy.data.actions["Idle"].slots[0]
bpy.context.scene.frame_set(0)
RESULT = made
