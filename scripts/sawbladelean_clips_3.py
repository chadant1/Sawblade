"""SawBladeLean animation clips, batch 3 (18 character-specific clips).

Blade moves, tie and coat gags and personality beats. Reuses the solver and
helpers from sawbladelean_clips_1.py and sawbladelean_clips_2.py, which must
sit in the same folder; it does not rebuild their clips.

Run from the repo root, with Blender 5.2 or newer:

    blender SawBladeLean.blend --python scripts/sawbladelean_clips_3.py

Nothing is saved or exported; save the file and export the FBX yourself
afterwards.
"""
import os
_here = os.path.dirname(os.path.abspath(__file__))
_lib2 = os.path.join(_here, "sawbladelean_clips_2.py")
_g = {"__file__": _lib2, "__name__": "sawbladelean_lib"}
exec(compile(open(_lib2).read().split("\nmade = {}\nfor name, (poses, kw) in CLIPS.items():")[0], _lib2, "exec"), _g)
globals().update({_k: _v for _k, _v in _g.items() if not _k.startswith("__")})

CLIPS.clear()


def shake(poses, f0, f1, chans, ramp=3.0):
    """Add a shudder to flat pose channels between two frames."""
    for f, P in enumerate(poses):
        e = max(0.0, min(1.0, (f - f0) / ramp, (f1 - f) / ramp))
        if e <= 0:
            continue
        for i, (c, (amp, freq)) in enumerate(chans.items()):
            P[c] = P.get(c, 0.0) + amp * e * sin(f * freq + i)


def grow(poses, f0, f1, chans):
    """Like shake, but the amplitude builds from zero up to full at f1."""
    for f, P in enumerate(poses):
        if f0 <= f <= f1:
            e = (f - f0) / float(f1 - f0)
            for i, (c, (amp, freq)) in enumerate(chans.items()):
                P[c] = P.get(c, 0.0) + amp * e * sin(f * freq + i)


# ------------------------------------------------------------ blade moves
br = interp_keys([
    k(0, B),
    k(8, B, M({"hips": (0, 0, -0.12), "Spine": (14, 0, 0), "Chest": (8, 0, 0), "Head": (14, 0, 0)}, U((-35, -30, 0)), Lw(-55))),
    k(28, B, M({"hips": (0, 0, -0.16), "Spine": (18, 0, 0), "Chest": (10, 0, 0), "Head": (16, 0, 0)}, U((-38, -32, 0)), Lw(-58))),
    k(32, B, M({"hips": (0, 0, -0.02), "Spine": (-10, 0, 0), "Chest": (-12, 0, 0), "Head": (-16, 0, 0)}, U((-30, -70, 0)), Lw(-40)), 'out'),
    k(40, B)], 40)
grow(br, 8, 30, {"LeftUpperArm#0": (2.5, 2.7), "RightUpperArm#0": (2.5, 3.1), "Spine#0": (1.2, 2.3), "hips#2": (0.006, 2.9), "Head#2": (3.0, 2.5)})
clip("BladeRev", br, spin=(0, 14, 14), spinfn=lambda t: t * t)

# centre of the tucked body, which the roll turns about; its height is the ball's radius
TUCKC = Vector((0, -0.10, 0.56))


def tuck(theta):
    Rm = Matrix.Rotation(radians(theta), 3, 'X')
    P = M({"hips": tuple(TUCKC + Rm @ Vector((0, 0.43, 0)) - H["Hips"]), "Hips": (20 + theta, 0, 0), "Spine": (45, 0, 0), "Chest": (35, 0, 0), "Neck": (20, 0, 0), "Head": (20, 0, 0)},
          U((-25, -12, 0)), Lw(-140))
    for key, bn in (("footL", "LeftFoot"), ("footR", "RightFoot")):
        w = TUCKC + Rm @ Vector((H[bn].x, 0.35, -0.34))
        d = w - H[bn]
        P[key] = (d.x, d.y, d.z, 20 + theta, 0)
    return P


bz = interp_keys([k(0, B), k(5, tuck(0), None, 'in')], 5, smooth=False)
for f in range(6, 23):
    u = (f - 5) / 18.0
    bz.append(flatten(tuck(720.0 * (0.25 * u * u * (3 - 2 * u) + 0.75 * u))))
bz += interp_keys([k(0, tuck(0)), k(7, B)], 7, smooth=False)
clip("BuzzsawDash", bz, wind=(0, -3.0, 0), headspin=8, spin=(0, 3, 3))

LOWG = M({"hips": (0, -0.05, -0.25), "Hips": (0, -6, 0), "Spine": (34, -14, -10), "Chest": (12, -10, -12), "Head": (-30, 0, 20),
          "RightUpperArm": (-36, 14, 0), "RightLowerArm": (5, 0, 0), "LeftUpperArm": (-40, -30, 0), "LeftLowerArm": (-60, 0, 0),
          "footR": (0, 0.10, 0, 0, 0), "footL": (0, -0.25, 0, 0, 0)})
clip("GroundGrind", interp_keys([
    k(0, RUN0),
    k(5, LOWG, None, 'out'),
    k(14, LOWG, {"hips": (0, -0.08, -0.25), "RightUpperArm": (-46, 14, 0)}, 'lin'),
    k(18, B, {"hips": (0, -0.10, -0.04), "Spine": (-8, 0, 25), "Chest": (-8, 0, 30), "Head": (-10, 0, -50), "RightUpperArm": (-150, 10, 10), "RightLowerArm": (-10, 0, 0),
              "LeftUpperArm": (20, -25, 0), "footL": (0, -0.25, 0, 0, 0)}, 'in'),
    k(22, B, {"hips": (0, -0.10, -0.03), "Spine": (-10, 0, 28), "Chest": (-10, 0, 34), "Head": (-10, 0, -56), "RightUpperArm": (-166, 10, 10), "RightLowerArm": (-15, 0, 0),
              "LeftUpperArm": (22, -25, 0), "footL": (0, -0.25, 0, 0, 0)}),
    k(27, B, {"hips": (0, -0.04, -0.05), "footL": (0, -0.12, 0.05, 0, 0)}),
    k(30, B)], 30), wind=(0, -1.5, 0), spin=(0, 1, 10))

clip("BladeClash", interp_keys([
    k(0, B),
    k(6, B, M({"hips": (0, 0, -0.08), "Chest": (-6, 0, 0)}, U((-55, -55, 0)), Lw(-50))),
    k(9, B, M({"hips": (0, -0.03, -0.08), "Spine": (6, 0, 0)}, U((-72, 0, -36)), Lw(-60)), 'in'),
    k(12, B, M({"hips": (0, -0.03, -0.08), "Spine": (6, 0, 0), "LeftUpperArm": (-98, 0, -30), "RightUpperArm": (-48, 0, 30)}, Lw(-60))),
    k(15, B, M({"hips": (0, 0, -0.06), "Chest": (-8, 0, 0)}, U((-60, -65, 0)), Lw(-30)), 'out'),
    k(22, B)], 22), spin=(0, 6, 6))

cy = []
for f in range(41):
    u = f / 40.0
    a = 1080.0 * (u * u * (3 - 2 * u))
    e = sin(pi * u) ** 0.5
    P = M(B, turned(a, liftL=0.03 * max(0.0, sin(radians(a))) * e, liftR=0.03 * max(0.0, -sin(radians(a))) * e, z=-0.04 - 0.06 * e),
          {"Spine": (2 + 4 * e, 0, 0), "Head": (-2 - 4 * e, 0, 0)}, U((-8 * e, -85 * e, 0)), Lw(-10 * e))
    cy.append(flatten(P))
clip("SpinCyclone", cy, spin=(0, 8, 8))


def wallclimb(t):
    s = sin(2 * pi * t)
    return {"hips": (0, 0, 0.25 + 0.04 * sin(4 * pi * t)), "Spine": (-4, 0, 0), "Chest": (-2, 0, 0), "Head": (14, 0, 0),
            "LeftUpperArm": (-135 - 30 * s, -22, 0), "RightUpperArm": (-135 + 30 * s, 22, 0), "LeftLowerArm": (-35 + 20 * s, 0, 0), "RightLowerArm": (-35 - 20 * s, 0, 0),
            "footL": (0.05, -0.22, 0.35 - 0.18 * s, -25, 0), "footR": (-0.05, -0.10, 0.35 + 0.18 * s, -25, 0)}


clip("WallSawClimb", loop_fn(24, wallclimb), loop=True, spin=(0, 8, 8))


def zipline(t):
    s = sin(2 * pi * t)
    return {"hips": (0.02 * s, 0, 0.45), "Hips": (10 + 5 * s, 0, 4 * s), "Spine": (-6, 0, 0), "Chest": (-4, 0, 0), "Head": (-10, 0, 0),
            "RightUpperArm": (-172, 4, 0), "RightLowerArm": (-6, 0, 0), "LeftUpperArm": (-20 + 8 * s, -40, 0), "LeftLowerArm": (-40, 0, 0),
            "footL": (0, 0.20 + 0.05 * s, 0.42, 45, 0), "footR": (0, 0.32 - 0.05 * s, 0.48, 45, 0)}


clip("SawZipline", loop_fn(30, zipline), loop=True, wind=(0, -3.0, 0), spin=(0, 1, 14), tie="stream")

ct = interp_keys([
    k(0, B),
    k(8, B, M({"hips": (0, -0.06, -0.04), "Spine": (6, 0, 0)}, U((-112, 0, -12)), Lw(-10))),
    k(30, B, M({"hips": (0, -0.10, -0.22), "Spine": (20, 0, 0), "Chest": (8, 0, 0), "Head": (-16, 0, 0)}, U((-62, 0, -12)), Lw(-10)), 'lin'),
    k(34, B, M({"hips": (0, -0.06, -0.10), "Spine": (4, 0, 0), "Chest": (-8, 0, 0)}, U((-70, -60, 0)), Lw(-30)), 'out'),
    k(44, B)], 44)
shake(ct, 8, 31, {"LeftUpperArm#0": (1.8, 2.7), "RightUpperArm#0": (1.8, 3.1), "Spine#0": (0.8, 2.3), "hips#2": (0.005, 2.9)})
clip("CutThrough", ct, spin=(0, 16, 16))

# ------------------------------------------------------------ tie and coat
clip("TieWhip", interp_keys([
    k(0, B),
    k(6, B, M({"hips": (0, 0.06, -0.08), "Spine": (-12, 0, 0), "Chest": (-12, 0, 0), "Head": (-10, 0, 0), "tie": (0.2, 0.8, 0.6, 0.6, 1, 0.1)}, U((20, -30, 0)))),
    k(9, B, M({"hips": (0, -0.12, -0.10), "Spine": (26, 0, 0), "Chest": (16, 0, 0), "Neck": (10, 0, 0), "Head": (-20, 0, 0), "tie": (0, -1, 0.12, 1.0, 1, 0.30)}, U((35, -40, 0)), Lw(-20)), 'in'),
    k(12, B, M({"hips": (0, -0.12, -0.10), "Spine": (26, 0, 0), "Chest": (16, 0, 0), "Neck": (10, 0, 0), "Head": (-20, 0, 0), "tie": (0, -1, 0.0, 1.0, 1, 0.12)}, U((32, -40, 0)), Lw(-20))),
    k(18, B, {"hips": (0, -0.03, -0.06), "Spine": (8, 0, 0), "tie": (0, -0.3, -1, 0.4, 1, 0.05)}),
    k(26, B, {"tie": (0, -0.25, -1, 0.28, 0, 0)})], 26))
ADJ = {"Spine": (-4, 0, 0), "Chest": (-8, 0, 0), "Neck": (-8, 0, 0), "Head": (-16, 0, -6), "RightUpperArm": (-62, 0, 38), "RightLowerArm": (-118, 0, 0), "tie": (0, -0.25, -1, 0.28, 1, 0)}
clip("TieStraighten", interp_keys([
    k(0, B),
    k(12, B, ADJ),
    k(16, B, M(ADJ, {"RightLowerArm": (-112, 0, 0), "Head": (-16, 0, 8), "tie": (0.06, -0.25, -1, 0.30, 1, 0.12)})),
    k(20, B, ADJ),
    k(24, B, M(ADJ, {"RightLowerArm": (-112, 0, 0), "Head": (-16, 0, -10), "tie": (-0.06, -0.25, -1, 0.30, 1, 0.12)})),
    k(28, B, ADJ),
    k(38, B, {"Head": (18, 0, 0), "RightUpperArm": (-45, 0, 30), "RightLowerArm": (-95, 0, 0), "tie": (0, -0.25, -1, 0.28, 1, 0)}),
    k(50, B, {"tie": (0, -0.25, -1, 0.28, 0, 0)})], 50))
YANK = {"hips": (-0.05, -0.08, -0.14), "Spine": (34, -10, -14), "Chest": (16, -6, -10), "Neck": (14, 0, 0), "Head": (22, 0, -12),
        "RightUpperArm": (-30, 10, 20), "RightLowerArm": (-70, 0, 0), "LeftUpperArm": (-20, -50, 0), "tie": (-0.6, -0.3, -0.75, 0.34, 1, 0)}
tcg = interp_keys([
    k(0, B),
    k(8, B, {"Head": (18, 0, -10), "RightUpperArm": (-50, 0, 30), "RightLowerArm": (-100, 0, 0)}),
    k(12, B, {"Head": (18, 0, -10), "RightUpperArm": (-50, 0, 30), "RightLowerArm": (-100, 0, 0), "tie": (-0.55, -0.45, -0.7, 0.36, 1, 0)}),
    k(16, B, YANK, 'in'),
    k(30, B, M(YANK, {"hips": (-0.05, -0.09, -0.16)})),
    k(33, B, {"hips": (0.03, 0.10, -0.04), "Spine": (-14, 4, 6), "Chest": (-10, 0, 0), "Head": (-14, 0, 0), "RightUpperArm": (-20, 45, 0), "LeftUpperArm": (-30, -50, 0),
              "tie": (0.2, -0.5, 0.8, 0.7, 1, 0.2)}, 'out'),
    k(38, B, {"hips": (0, 0.04, -0.06), "tie": (0, -0.3, -1, 0.4, 0.6, 0.1)}),
    k(44, B, {"tie": (0, -0.25, -1, 0.28, 0, 0)})], 44)
shake(tcg, 16, 31, {"Spine#0": (2.5, 2.4), "Head#2": (6.0, 2.9), "LeftUpperArm#1": (8.0, 2.2), "hips#1": (0.012, 2.6)})
clip("TieCaught", tcg, spin=(0, 1, 8))
clip("CoatFlourish", interp_keys([
    k(0, B),
    k(4, B, M({"hips": (0, 0, -0.10), "Hips": (0, 0, -30), "Spine": (4, 0, -10), "Chest": (2, 0, -10), "Head": (-2, 0, 45)}, U((10, -25, 0)))),
    k(8, B, M({"hips": (0, 0, 0.0), "Hips": (0, 0, 35), "Spine": (-4, 0, 12), "Chest": (-4, 0, 14), "Head": (-2, 0, -55)}, U((20, -45, 0)), Lw(-20)), 'in'),
    k(12, B, M({"hips": (0, 0, -0.03), "Hips": (0, 0, 28), "Spine": (-2, 0, 10), "Chest": (-2, 0, 10), "Head": (-2, 0, -44)}, U((16, -40, 0)), Lw(-20))),
    k(20, B)], 20))

# ------------------------------------------------------------ personality
HOLD = {"hips": (0, 0, -0.06), "Spine": (8, 0, 0), "Chest": (6, 0, 0), "Head": (16, 0, 0), "LeftUpperArm": (-62, 0, -28), "LeftLowerArm": (-72, 0, 0),
        "RightUpperArm": (-78, 0, 30), "RightLowerArm": (-70, 0, 0)}
STROKE = M(HOLD, {"RightUpperArm": (-48, 0, 14), "RightLowerArm": (-50, 0, 0)})
clip("BladeSharpen", interp_keys([
    k(0, B), k(10, B, HOLD), k(16, B, STROKE, 'in'), k(22, B, HOLD), k(28, B, STROKE, 'in'), k(34, B, HOLD), k(40, B, STROKE, 'in'),
    k(48, B, M(HOLD, {"Head": (8, 0, -15), "RightUpperArm": (-85, 0, 20)})), k(60, B)], 60), spin=(0, 0, 0))
OFFER = {"Spine": (8, 0, 0), "Chest": (4, 0, 0), "Head": (-6, 0, 0), "RightUpperArm": (-72, 0, 6), "RightLowerArm": (8, 0, 0)}
clip("FailedHandshake", interp_keys([
    k(0, B),
    k(10, B, OFFER),
    k(20, B, M(OFFER, {"RightUpperArm": (-74, 0, 6)})),
    k(28, B, M(OFFER, {"Head": (20, 0, -14)})),
    k(36, B, {"Spine": (-2, 0, 0), "Head": (8, 0, -10), "RightUpperArm": (-30, 10, 10), "RightLowerArm": (-70, 0, 0)}),
    k(44, B, M({"Head": (-2, 8, 0)}, both("Shoulder", (0, -14, 0)), U((-8, -18, 0)), Lw(-45))),
    k(48, B, M({"Head": (-2, 8, 0)}, both("Shoulder", (0, -12, 0)), U((-8, -18, 0)), Lw(-45))),
    k(56, B)], 56))
DOWN = M({"hips": (0, -0.04, -0.34), "Spine": (40, 0, 0), "Chest": (14, 0, 0), "Head": (-8, 0, 0)}, U((-52, 0, -10)), Lw(0))
PINCH = M(DOWN, U((-52, 0, -22)))
OPEN = M(DOWN, U((-46, 0, -8)))
clip("TryToPickUp", interp_keys([
    k(0, B), k(12, B, DOWN), k(18, B, PINCH, 'in'), k(22, B, OPEN), k(28, B, PINCH, 'in'), k(32, B, OPEN), k(38, B, PINCH, 'in'),
    k(42, B, M(DOWN, {"Head": (-8, 12, 0)})),
    k(52, B, M({"Spine": (4, 0, 0)}, U((-10, -15, 0)), Lw(-30))),
    k(56, B, M({"Spine": (4, 0, 0), "Head": (-2, 0, 20)}, U((-10, -15, 0)), Lw(-30))),
    k(60, B, M({"Spine": (4, 0, 0), "Head": (-2, 0, -20)}, U((-8, -10, 0)), Lw(-20))),
    k(64, B)], 64))
STUCK = M({"hips": (0, -0.22, -0.14), "Spine": (40, 0, 0), "Chest": (22, 0, 0), "Neck": (15, 0, 0), "Head": (10, 0, 0), "footR": (0, -0.25, 0, 0, 0)}, U((-95, -10, 0)), Lw(-20))
PULL = M(STUCK, {"hips": (0, -0.15, -0.15), "Spine": (45, 0, 0)}, U((-100, -10, 0)), Lw(-5))
clip("HeadStuck", interp_keys([
    k(0, B),
    k(6, B, WIND),
    k(8, B, M(WIND, {"footR": (0, -0.12, 0.07, -8, 0)})),
    k(10, B, M(STUCK, U((50, -30, 0)), Lw(-15)), 'in'),
    k(16, B, STUCK),
    k(22, B, PULL), k(26, B, STUCK), k(32, B, PULL), k(36, B, STUCK),
    k(42, B, M(PULL, {"hips": (0, -0.12, -0.12), "Spine": (48, 0, 0)})),
    k(46, B, M({"hips": (0, 0.16, -0.04), "Spine": (-16, 0, 0), "Chest": (-12, 0, 0), "Head": (-14, 0, 0), "footR": (0, -0.10, 0.04, 0, 0), "footL": (0, 0.20, 0, 0, 0)}, U((-60, -60, 0))), 'out'),
    k(54, B, {"hips": (0, 0.10, -0.08), "Spine": (8, 0, 0), "footL": (0, 0.20, 0, 0, 0)}),
    k(60, B, {"hips": (0, 0.04, -0.05), "footL": (0, 0.10, 0.05, 0, 0)}),
    k(64, B)], 64))
LOOK = {"Spine": (4, 0, -6), "Chest": (2, 0, -10), "Head": (12, 0, -28), "RightUpperArm": (-66, 12, 14), "RightLowerArm": (-84, 0, 0)}
SHK = M(LOOK, {"RightLowerArm": (-68, 0, 0)})
UP = M(LOOK, {"hips": (0.03, 0, -0.03), "Spine": (6, 0, 0), "RightUpperArm": (-120, 15, 0), "RightLowerArm": (-60, 0, 0), "footR": (0, -0.05, 0.30, 10, 0)})
BANG = M(LOOK, {"hips": (0.03, 0, -0.04), "Spine": (14, 0, 0), "Head": (14, 0, -20), "RightUpperArm": (-35, 5, 10), "RightLowerArm": (-40, 0, 0), "footR": (0, -0.08, 0.38, 10, 0)})
bj = interp_keys([
    k(0, B), k(10, B, LOOK), k(14, B, SHK), k(17, B, LOOK), k(20, B, SHK), k(23, B, LOOK),
    k(30, B, UP), k(33, B, BANG, 'in'), k(36, B, UP), k(39, B, BANG, 'in'),
    k(44, B, M(LOOK, {"Head": (4, 0, -28)})), k(56, B)], 56)
for f, P in enumerate(bj):
    P["spin.RightHandBlade#0"] = 360.0 * 4 * (max(0, f - 39) / 17.0) ** 2
clip("BladeJam", bj, spin=(0, 1, 0))
KN = M({"hips": (0, -0.06, -0.36), "Spine": (40, 0, 0), "Chest": (14, 0, 0), "Head": (-10, 0, 0), "RightUpperArm": (-48, 0, 10), "RightLowerArm": (8, 0, 0),
        "LeftUpperArm": (-20, -30, 0), "LeftLowerArm": (-50, 0, 0)})
FW = M(KN, {"RightUpperArm": (-64, 0, 10)})
clip("SparkLighter", interp_keys([
    k(0, B), k(12, B, KN), k(16, B, FW, 'in'), k(20, B, KN), k(24, B, FW, 'in'), k(28, B, KN), k(32, B, FW, 'in'),
    k(38, B, M(KN, {"hips": (0, 0.02, -0.30), "Spine": (22, 0, 0), "Head": (4, 0, 0), "RightUpperArm": (-30, 20, 0)})),
    k(46, B, M(KN, {"hips": (0, 0.02, -0.30), "Spine": (20, 0, 0), "Head": (6, 0, 0), "RightUpperArm": (-30, 20, 0)})),
    k(56, B)], 56), spin=(0, 1, 10))

made = {}
for name, (poses, kw) in CLIPS.items():
    a = bake(name, [dict(p) for p in poses], **kw)
    made[name] = len(poses) - 1
ao.animation_data.action = bpy.data.actions["Idle"]
ao.animation_data.action_slot = bpy.data.actions["Idle"].slots[0]
bpy.context.scene.frame_set(0)
RESULT = made
