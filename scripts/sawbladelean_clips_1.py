"""SawBladeLean animation clips, batch 1 (22 clips).

Generates the actions procedurally on the rig in SawBladeLean.blend:
Idle, Walk, Run, Sprint, WalkBack, StrafeLeft/Right, the jump clips,
Light1-3, Heavy1, Headbutt, BladeThrow, BlockLoop, DodgeBack, HitLight,
Knockdown, GetUp and Death.

Run from the repo root, with Blender 5.2 or newer:

    blender SawBladeLean.blend --python scripts/sawbladelean_clips_1.py

It needs the objects "SawCharacter_Rig" and "SawCharacter_Game". Each clip is
rebuilt from scratch, replacing any action with the same name. Nothing is
saved or exported; save the file and export the FBX yourself afterwards.

Poses are written as rotations in world axes relative to the parent bone
(X = pitch, Y = roll, Z = yaw; the character faces -Y), hips offsets in
metres, and foot targets solved with two-bone IK. The tie, coat tails and
blade spin are added on top by the bake step.
"""
import bpy, math
from math import sin, cos, pi, radians
from mathutils import Vector, Matrix, Euler, Quaternion

ao = bpy.data.objects["SawCharacter_Rig"]
arm = ao.data
FPS = 30
R = {b.name: b.matrix_local.to_3x3() for b in arm.bones}
Rinv = {n: m.inverted() for n, m in R.items()}
H = {b.name: Vector(b.head_local) for b in arm.bones}
TL = {b.name: Vector(b.tail_local) for b in arm.bones}
PAR = {b.name: (b.parent.name if b.parent else None) for b in arm.bones}
ORDER = [b.name for b in arm.bones]
BLADES = ["HeadBlade", "LeftHandBlade", "RightHandBlade"]
LEGS = {"L": ("LeftUpperLeg", "LeftLowerLeg", "LeftFoot", "LeftToes", "footL"),
        "R": ("RightUpperLeg", "RightLowerLeg", "RightFoot", "RightToes", "footR")}
LEGBONES = {n for v in LEGS.values() for n in v[:4]}
TIE = ["Tie_%02d" % i for i in range(1, 11)]
FLOOR = 0.07
CHAINS = [(["CoatTail_Back_01", "CoatTail_Back_02"], 0.16, 0.08, 0.06, 0.6),
          (["CoatTail_Left"], 0.16, 0.08, 0.05, 0.6), (["CoatTail_Right"], 0.16, 0.08, 0.05, 0.6),
          (["CoatTail_FrontLeft"], 0.16, 0.08, 0.05, 0.6), (["CoatTail_FrontRight"], 0.16, 0.08, 0.05, 0.6)]
SIMBONES = {n for c in CHAINS for n in c[0]} | set(TIE)


def frame(d, b):
    d = d.normalized()
    x = (b - d * b.dot(d)).normalized()
    z = x.cross(d)
    return Matrix((x, d, z)).transposed()


def _tie_frames():
    import numpy as np
    mesh = bpy.data.objects["SawCharacter_Game"]
    out = {}
    prevb = None
    for n in TIE:
        gi = mesh.vertex_groups[n].index
        pts = [v.co.copy() for v in mesh.data.vertices if any(g_.group == gi and g_.weight > 0.4 for g_ in v.groups)]
        d = (TL[n] - H[n]).normalized()
        c = sum(pts, Vector()) / len(pts)
        A = np.array([list((p - c) - d * (p - c).dot(d)) for p in pts])
        u, sv, vt = np.linalg.svd(A, full_matrices=False)
        b = Vector(vt[0])
        b = (b - d * b.dot(d)).normalized()
        if prevb is None:
            if b.x < 0:
                b = -b
        elif b.dot(prevb) < 0:
            b = -b
        prevb = b
        out[n] = frame(d, b)
    return out


TF = _tie_frames()


def rotv(w):
    return Matrix.Rotation(w.length, 3, w.normalized()) if w.length > 1e-6 else Matrix.Identity(3)


def clampv(w, m):
    return w * (m / w.length) if w.length > m else w


def solve_tie(frames, loop, wind, mode):
    n = len(frames)
    W = Vector(wind)
    vf = Vector()
    vf2 = Vector()
    fly = 0.0
    prev = None
    scales = [1.0] * n
    for ps in range(3 if loop else 1):
        for fi in range(n):
            G, pos = frames[fi]
            Gc = G["Chest"]
            root = pos["Chest"] + Gc @ (H["Tie_01"] - H["Chest"])
            env = 1.0 if loop else min(1.0, (n - 1 - fi) / 5.0)
            wenv = 1.0 if loop else sin(pi * fi / (n - 1))
            v = (((root - prev) * FPS if prev is not None else Vector()) + W * wenv) * env
            prev = root.copy()
            vf += (v - vf) * min(1.0, (1.0 / FPS) / 0.10)
            vf2 += (v - vf2) * min(1.0, (1.0 / FPS) / 0.28)
            if mode in ("stream", "rise"):
                ph = 4 * pi * fi / (n - 1)
                for i, bn in enumerate(TIE):
                    if mode == "rise":
                        if i == 0:
                            td = Vector((0.8, -0.35, 0.5))
                        elif i == 1:
                            td = Vector((0.45, 0.2, 0.9))
                        else:
                            td = Vector((0.12 * sin(ph - 0.9 * i), 0.22 + 0.1 * sin(ph - 0.9 * i + 1), 1.0))
                    elif i == 0:
                        td = Vector((0.75, -0.2, 0.5))
                    elif i == 1:
                        td = Vector((0.6, 0.55, 0.4))
                    else:
                        td = Vector((0.12 * sin(ph - 0.9 * i), 1.0, 0.12 + 0.22 * sin(ph - 0.9 * i + 1)))
                    G[bn] = frame(td, Vector((0, 0, 1)) if mode == "stream" else Vector((1, 0, 0))) @ TF[bn].transposed()
                scales[fi] = 1.0
                continue
            target = min(1.0, max(0.0, (vf.length - 0.7) / 2.2))
            fly += (target - fly) * min(1.0, (1.0 / FPS) / 0.12)
            fly = min(fly, env)
            bf = Gc @ Vector((0, -1, 0))
            bd = Gc @ Vector((0, 0, -1))
            wd = Vector((0, 0, -1))
            c = wd.dot(bf)
            if c < 0:
                wd = wd - bf * c
            dl = (wd + 0.3 * bd + 0.3 * bf).normalized()
            bt = Gc @ Vector((1, 0, 0))
            o1 = -vf
            o2 = -vf2
            for o in (o1, o2):
                c = o.dot(bf)
                if c < 0:
                    o -= bf * c
            w1 = clampv(dl.cross(o1) * 0.22, 0.9)
            w2 = clampv(dl.cross(o2) * 0.25, 1.0)
            base = frame(dl, bt)
            for i, bn in enumerate(TIE):
                Dm = rotv(w1 * (1 + 0.3 * i * fly))
                if i > 0 and fly > 0.01:
                    Dm = rotv(w2 * (0.2 * i * fly)) @ Dm
                G[bn] = Dm @ base @ TF[bn].transposed()
            scales[fi] = 0.28 + 0.72 * fly
            # keep the tie above the floor: bones that would dip below it bend to lie along the ground
            sy = scales[fi]
            sz = 0.35 + 0.65 * fly
            fwd = Vector((bf.x, bf.y, 0.0))
            fwd = fwd.normalized() if fwd.length > 1e-3 else Vector((0, -1, 0))
            p = root.copy()
            Minv = None
            Ms = None
            for i, bn in enumerate(TIE):
                vec = TL[bn] - H[bn]
                ln = vec.length
                vh = vec.normalized()
                cur = G[bn] @ vh
                if i == 0:
                    u = cur

                    def length_of(u_):
                        return ln * sy
                else:
                    u = (Ms @ cur).normalized()

                    def length_of(u_):
                        return ln / (Minv @ u_).length
                if p.z < FLOOR:
                    uh = Vector((u.x, u.y, 0.0))
                    uh = uh.normalized() if uh.length > 0.2 else fwd
                    fwd = uh
                    tdir = uh if i == 0 else (Minv @ uh).normalized()
                    G[bn] = cur.rotation_difference(tdir).to_matrix() @ G[bn]
                    u = uh
                elif p.z + length_of(u) * u.z < FLOOR:
                    uh = Vector((u.x, u.y, 0.0))
                    uh = uh.normalized() if uh.length > 0.2 else fwd
                    lo, hi = math.asin(max(-1.0, min(1.0, u.z))), 0.6
                    for _ in range(14):
                        mid = 0.5 * (lo + hi)
                        um = uh * cos(mid) + Vector((0, 0, 1)) * sin(mid)
                        if p.z + length_of(um) * um.z < FLOOR:
                            lo = mid
                        else:
                            hi = mid
                    u = (uh * cos(hi) + Vector((0, 0, 1)) * sin(hi)).normalized()
                    fwd = uh
                    tdir = u if i == 0 else (Minv @ u).normalized()
                    G[bn] = cur.rotation_difference(tdir).to_matrix() @ G[bn]
                if i == 0:
                    A = G[bn] @ R[bn]
                    Ms = A @ Matrix.Diagonal((1.0, sy, sz)) @ A.inverted()
                    Minv = Ms.inverted()
                p = p + u * length_of(u)
    return scales


def E(rx, ry, rz):
    return Euler((radians(rx), radians(ry), radians(rz)), 'XYZ').to_matrix()


def flatten(p):
    o = {}
    for k, v in p.items():
        if isinstance(v, (tuple, list)):
            for i, x in enumerate(v):
                o["%s#%d" % (k, i)] = float(x)
        else:
            o[k + "#0"] = float(v)
    return o


def g(P, name, n=3):
    return tuple(P.get("%s#%d" % (name, i), 0.0) for i in range(n))


def M(*ds):
    o = {}
    for d in ds:
        o.update(d)
    return o


def both(suffix, v):
    return {"Left" + suffix: v, "Right" + suffix: (v[0], -v[1], -v[2])}


def ease(u, e):
    if e == 'in':
        return u ** 2.2
    if e == 'out':
        return 1 - (1 - u) ** 2.2
    if e == 'lin':
        return u
    return u * u * (3 - 2 * u)


def interp_keys(keys, N, smooth=True):
    flat = [(f, flatten(p), e) for f, p, e in keys]
    chans = set()
    for _, p, _ in flat:
        chans |= set(p)
    out = []
    for fr in range(N + 1):
        i = 0
        for j in range(len(flat) - 1):
            if flat[j][0] <= fr:
                i = j
        f0, p0, _ = flat[i]
        f1, p1, e = flat[i + 1]
        u = min(1.0, max(0.0, (fr - f0) / (f1 - f0)))
        w = ease(u, e)
        out.append({c: p0.get(c, 0.0) * (1 - w) + p1.get(c, 0.0) * w for c in chans})
    if smooth:
        sm = [dict(o) for o in out]
        for fr in range(1, N):
            for c in chans:
                sm[fr][c] = 0.2 * out[fr - 1][c] + 0.6 * out[fr][c] + 0.2 * out[fr + 1][c]
        out = sm
    return out


def solve_body(P):
    G = {}
    pos = {}
    G["Hips"] = E(*g(P, "Hips"))
    pos["Hips"] = H["Hips"] + Vector(g(P, "hips"))
    for n in ORDER:
        if n == "Hips" or n in LEGBONES or n in SIMBONES or n in BLADES:
            continue
        p = PAR[n]
        G[n] = G[p] @ E(*g(P, n))
        pos[n] = pos[p] + G[p] @ (H[n] - H[p])
    Gh = G["Hips"]
    for up, low, foot, toes, key in LEGS.values():
        f = g(P, key, 5)
        hip = pos["Hips"] + Gh @ (H[up] - H["Hips"])
        L1 = (H[low] - H[up]).length
        L2 = (H[foot] - H[low]).length
        d1 = (H[low] - H[up]).normalized()
        d2 = (H[foot] - H[low]).normalized()
        T = H[foot] + Vector(f[:3])
        # keep toe tip and heel above the floor whatever the foot pitch
        Gf0 = E(f[3], 0, f[4])
        lowz = min((Gf0 @ (TL[toes] - H[foot])).z, (Gf0 @ Vector((0, 0.06, -H[foot].z))).z)
        if T.z + lowz < 0.0:
            T.z = -lowz
        v = T - hip
        dist = max(abs(L1 - L2) + 0.02, min(v.length, (L1 + L2) * 0.998))
        dn = v.normalized()
        a = (L1 * L1 - L2 * L2 + dist * dist) / (2 * dist)
        hgt = math.sqrt(max(0.0, L1 * L1 - a * a))
        pole = Gh @ Vector((0, -1, 0))
        pp = pole - dn * pole.dot(dn)
        if pp.length < 1e-4:
            pp = Vector((0, -1, 0))
        pp.normalize()
        K = hip + dn * a + pp * hgt
        Tc = hip + dn * dist
        Gu = (Gh @ d1).rotation_difference(K - hip).to_matrix() @ Gh
        Gl = (Gu @ d2).rotation_difference(Tc - K).to_matrix() @ Gu
        Gf = E(f[3], 0, f[4])
        G[up], G[low], G[foot] = Gu, Gl, Gf
        G[toes] = Gf @ E(-0.6 * max(0.0, f[3]), 0, 0)
        pos[up], pos[low], pos[foot] = hip, K, Tc
    FLAT = E(90, 0, 0).to_quaternion()
    for n in BLADES:
        p = PAR[n]
        Gb = G[p] @ E(*g(P, n))
        fl = g(P, "flat." + n, 1)[0]
        if fl > 0:
            Gb = Gb.to_quaternion().slerp(FLAT, min(1.0, fl)).to_matrix()
        G[n] = Gb
    return G, pos


def simulate(frames, loop, wind):
    """frames: list of (G,pos). Adds G for chain bones in place."""
    n = len(frames)
    seq = list(range(n))
    passes = 3 if loop else 1
    wind = Vector(wind)
    for names, gain, tau0, dtau, maxang in CHAINS:
        par = PAR[names[0]]
        vf = [Vector((0, 0, 0)) for _ in names]
        prev = None
        for ps in range(passes):
            for fi in seq:
                Gd, pos = frames[fi]
                root = pos[par] + Gd[par] @ (H[names[0]] - H[par])
                if prev is None:
                    if loop:
                        Gp_, pp_ = frames[n - 2]
                        prev = pp_[par] + Gp_[par] @ (H[names[0]] - H[par])
                    else:
                        prev = root.copy()
                v = (root - prev) * FPS + wind
                prev = root.copy()
                Gc = Gd[par]
                for i, bn in enumerate(names):
                    a = min(1.0, (1.0 / FPS) / (tau0 + dtau * i))
                    vf[i] += (v - vf[i]) * a
                    d = Gc @ (TL[bn] - H[bn]).normalized()
                    w = d.cross(-vf[i]) * gain
                    if w.length > maxang:
                        w = w * (maxang / w.length)
                    if w.length > 1e-6:
                        Gc = Matrix.Rotation(w.length, 3, w.normalized()) @ Gc
                    Gd[bn] = Gc.copy()
            if loop:
                prev_last = prev


def to_basis(P, G):
    rot = {}
    loc = {}
    for n in ORDER:
        p = PAR[n]
        Gp = G[p] if p else Matrix.Identity(3)
        q = (Rinv[n] @ Gp.inverted() @ G[n] @ R[n]).to_quaternion()
        if n in BLADES:
            q = q @ Quaternion((0, 1, 0), radians(g(P, "spin." + n, 1)[0]))
            loc[n] = Rinv[n] @ Gp.inverted() @ Vector(g(P, "loc." + n))
        rot[n] = q
    loc["Hips"] = Rinv["Hips"] @ Vector(g(P, "hips"))
    return rot, loc


def bake(name, poses, loop=False, wind=(0, 0, 0), spin=(1, 1, 1), spinfn=None, headspin=0, tie="drape"):
    N = len(poses) - 1
    for f, P in enumerate(poses):
        t = f / N
        s = spinfn(t) if spinfn else t
        for b, rv in zip(BLADES, spin):
            if b == "HeadBlade":
                # head blade stays upright: small rock only, unless the clip uses it to attack
                if headspin:
                    a = 360.0 * headspin * (t * t * (3 - 2 * t))
                elif loop:
                    a = 7.0 * sin(2 * pi * t)
                else:
                    a = 6.0 * sin(pi * t) * sin(3 * pi * t)
                P["spin.%s#0" % b] = a
                continue
            P["spin.%s#0" % b] = P.get("spin.%s#0" % b, 0.0) + 360.0 * rv * s
    frames = [solve_body(P) for P in poses]
    simulate(frames, loop, wind)
    scales = solve_tie(frames, loop, wind, tie)
    if loop:
        scales[0] = scales[N]
        frames[N] = (dict(frames[N][0]), frames[N][1])
        for bn in SIMBONES:
            frames[0][0][bn] = frames[N][0][bn]
    data = [to_basis(P, G) for P, (G, pos) in zip(poses, frames)]
    old = bpy.data.actions.get(name)
    if old:
        bpy.data.actions.remove(old)
    act = bpy.data.actions.new(name)
    act.use_fake_user = True
    if not ao.animation_data:
        ao.animation_data_create()
    ao.animation_data.action = act
    pb0 = ao.pose.bones["Hips"]
    pb0.keyframe_insert("location", frame=0)
    slot = ao.animation_data.action_slot
    from bpy_extras import anim_utils
    cb = anim_utils.action_ensure_channelbag_for_slot(act, slot)

    def curve(path, idx, grp):
        fc = cb.fcurves.find(path, index=idx)
        if fc is None:
            fc = cb.fcurves.new(path, index=idx, group_name=grp)
        return fc

    def write(fc, vals):
        while len(fc.keyframe_points):
            fc.keyframe_points.remove(fc.keyframe_points[0], fast=True)
        fc.keyframe_points.add(len(vals))
        co = []
        for i, v in enumerate(vals):
            co += [float(i), float(v)]
        fc.keyframe_points.foreach_set("co", co)
        for kp in fc.keyframe_points:
            kp.interpolation = 'LINEAR'
        fc.update()

    for n in ORDER:
        qs = []
        prev = None
        for rot, loc in data:
            q = rot[n].copy()
            if prev is not None and q.dot(prev) < 0:
                q.negate()
            prev = q
            qs.append(q)
        if loop and n not in BLADES:
            qs[-1] = qs[0].copy() if qs[-1].dot(qs[0]) > 0 else -qs[0]
        path = 'pose.bones["%s"].rotation_quaternion' % n
        for i in range(4):
            write(curve(path, i, n), [q[i] for q in qs])
        if n == "Hips" or n in BLADES:
            path = 'pose.bones["%s"].location' % n
            for i in range(3):
                write(curve(path, i, n), [loc[n][i] for rot, loc in data])
    for i in range(3):
        write(curve('pose.bones["Tie_01"].scale', i, "Tie_01"), [sc_ if i == 1 else (0.35 + 0.65 * (sc_ - 0.28) / 0.72 if i == 2 else 1.0) for sc_ in scales])
    act.use_frame_range = True
    act.frame_start = 0
    act.frame_end = N
    try:
        act.use_cyclic = loop
    except Exception:
        pass
    return act


# ---------------------------------------------------------------- poses
B = M({"hips": (0, 0, -0.04), "Spine": (2, 0, 0), "Chest": (2, 0, 0), "Head": (-2, 0, 0)})
GUARD = M({"hips": (0, 0, -0.09), "Spine": (8, 0, 0), "Chest": (6, 0, 0), "Head": (-8, 0, 0)},
          both("UpperArm", (-75, 0, -20)), both("LowerArm", (-75, 0, 0)))
AIR = M({"hips": (0, 0, 0), "Spine": (8, 0, 0), "Chest": (4, 0, 0), "Head": (-6, 0, 0),
         "footL": (0, -0.12, 0.28, 25, 0), "footR": (0, 0.10, 0.16, 35, 0)},
        both("UpperArm", (-50, -35, 0)), both("LowerArm", (-30, 0, 0)))
LYING = M({"Hips": (-88, 0, 0), "hips": (0, 0.58, -0.43), "Spine": (4, 0, 0), "Chest": (4, 0, 0), "Head": (10, 0, 0),
           "footL": (0, 0, -0.04, -75, 0), "footR": (0, 0, -0.04, -75, 0)},
          both("UpperArm", (18, -35, 0)), both("LowerArm", (-10, 0, 0)))


def k(f, base, over=None, e='io'):
    return (f, M(base, over or {}), e)


def gait(N, d, A, lift, duty, base_z, bob, bobshift, sway, lean, armsw, pelv, pitchscale=1.0, guard=None, elbow=20, lowbase=0):
    out = []
    dx, dy = d
    fwd = -dy
    cL = Vector((0, -0.085)) if abs(dy) > 0 else Vector((0, 0))
    cR = Vector((0, 0.08)) if abs(dy) > 0 else Vector((0, 0))
    for f in range(N + 1):
        t = (f % N) / N
        ph = 2 * pi * t
        P = {}
        P["hips"] = (sway * sin(ph), 0, base_z - bob * cos(4 * pi * (t - bobshift)))
        for key, off, c in (("footL", 0.0, cL), ("footR", 0.5, cR)):
            u = (t + off) % 1.0
            if u < duty:
                s = u / duty
                along = A * (1 - 2 * s)
                z = 0.0
                pitch = -12 * max(0.0, 1 - s / 0.15) + 22 * max(0.0, (s - 0.7) / 0.3) ** 2
            else:
                s = (u - duty) / (1 - duty)
                sm = s * s * (3 - 2 * s)
                along = -A + 2 * A * sm
                z = lift * sin(pi * s)
                pitch = 22 * (1 - sm) + 20 * sin(pi * s) * (1 - s) - 12 * s ** 3
            pitch *= pitchscale
            z += 0.12 * sin(radians(max(pitch, 0))) + 0.03 * sin(radians(max(-pitch, 0)))
            P[key] = (dx * along + c.x, dy * along + c.y, z, pitch, 0)
        cph = cos(ph)
        P["Hips"] = (0, -3 * sin(ph), -pelv * cph * fwd)
        P["Spine"] = (-lean * dy * 0.6 + 2, lean * dx * 0.6, 0.5 * pelv * cph * fwd)
        P["Chest"] = (-lean * dy * 0.4 + 2, lean * dx * 0.4, 1.3 * pelv * cph * fwd)
        P["Head"] = (lean * dy * 0.7 - 2, 0, -0.6 * pelv * cph * fwd)
        sw = armsw * cph * (fwd if fwd else 0.3)
        gu = guard or {}
        lu = gu.get("LeftUpperArm", (0, 0, 0))
        ru = gu.get("RightUpperArm", (0, 0, 0))
        ll = gu.get("LeftLowerArm", (lowbase, 0, 0))
        rl = gu.get("RightLowerArm", (lowbase, 0, 0))
        P["LeftUpperArm"] = (lu[0] + sw, lu[1], lu[2])
        P["RightUpperArm"] = (ru[0] - sw, ru[1], ru[2])
        P["LeftLowerArm"] = (ll[0] - elbow * max(0.0, -cph * fwd), 0, 0)
        P["RightLowerArm"] = (rl[0] - elbow * max(0.0, cph * fwd), 0, 0)
        out.append(flatten(P))
    return out


def loop_fn(N, fn):
    return [flatten(fn((f % N) / N)) for f in range(N + 1)]


CLIPS = {}


def clip(name, poses, **kw):
    CLIPS[name] = (poses, kw)


# Idle
def idle(t):
    s = sin(2 * pi * t)
    s2 = sin(2 * pi * t - 0.8)
    return M(B, {"hips": (0.006 * sin(2 * pi * t + 1), 0, -0.04 - 0.012 * s), "Spine": (2 + 1.0 * s, 0, 0), "Chest": (2 + 1.5 * s2, 0, 0),
                 "Head": (-2 - 1.5 * s2, 0, 2 * sin(2 * pi * t + 2)), "LeftUpperArm": (1.5 * s2, -2 * s, 0), "RightUpperArm": (1.5 * s2, 2 * s, 0),
                 "LeftLowerArm": (-3 * s2 - 3, 0, 0), "RightLowerArm": (-3 * s2 - 3, 0, 0)})


clip("Idle", loop_fn(60, idle), loop=True, spin=(1, 1, 1))
clip("Walk", gait(28, (0, -1), 0.20, 0.09, 0.6, -0.05, 0.015, 0.0, 0.03, 4, 22, 7, elbow=12, lowbase=-5),
     loop=True, wind=(0, -0.5, 0), spin=(1, 1, 1))
RUNARM = M(both("UpperArm", (-5, -8, 0)), both("LowerArm", (-55, 0, 0)))
clip("Run", gait(18, (0, -1), 0.34, 0.20, 0.42, -0.10, 0.03, 0.2, 0.02, 14, 38, 10, guard=RUNARM, elbow=20),
     loop=True, wind=(0, -1.6, 0), spin=(2, 2, 2), tie="stream")
SPRARM = M(both("UpperArm", (-5, -10, 0)), both("LowerArm", (-75, 0, 0)))
clip("Sprint", gait(14, (0, -1), 0.38, 0.26, 0.36, -0.12, 0.035, 0.18, 0.015, 24, 55, 13, guard=SPRARM, elbow=15),
     loop=True, wind=(0, -2.6, 0), spin=(2, 2, 2), tie="stream")
CG = M(both("UpperArm", (-45, 0, -12)), both("LowerArm", (-65, 0, 0)))
clip("WalkBack", gait(28, (0, 1), 0.15, 0.07, 0.62, -0.08, 0.012, 0.0, 0.025, -3, 6, 4, pitchscale=0.3, guard=CG, elbow=0),
     loop=True, wind=(0, 0.4, 0), spin=(1, 1, 1))
clip("StrafeLeft", gait(24, (1, 0), 0.11, 0.07, 0.6, -0.09, 0.012, 0.0, 0.0, 4, 6, 0, pitchscale=0.3, guard=CG, elbow=0),
     loop=True, wind=(0.5, 0, 0), spin=(1, 1, 1))
clip("StrafeRight", gait(24, (-1, 0), 0.11, 0.07, 0.6, -0.09, 0.012, 0.0, 0.0, 4, 6, 0, pitchscale=0.3, guard=CG, elbow=0),
     loop=True, wind=(-0.5, 0, 0), spin=(1, 1, 1))

# Jumps
clip("JumpStart", interp_keys([
    k(0, B),
    k(5, B, M({"hips": (0, 0, -0.22), "Spine": (28, 0, 0), "Chest": (10, 0, 0), "Head": (-20, 0, 0)}, both("UpperArm", (45, -10, 0)), both("LowerArm", (-30, 0, 0)))),
    k(8, B, M({"hips": (0, 0, 0.02), "Spine": (0, 0, 0), "Chest": (-5, 0, 0), "footL": (0, 0, 0.06, 30, 0), "footR": (0, 0, 0.06, 30, 0)}, both("UpperArm", (-95, -10, 0)), both("LowerArm", (-20, 0, 0))), 'in'),
    k(12, AIR, None, 'out')], 12), spin=(1, 1, 1))


def airloop(t):
    s = sin(2 * pi * t)
    c = cos(2 * pi * t)
    return M(AIR, {"Spine": (8 + 2 * s, 0, 0), "footL": (0, -0.12 + 0.015 * c, 0.28 + 0.02 * s, 25, 0), "footR": (0, 0.10 - 0.015 * c, 0.16 - 0.02 * s, 35, 0),
                   "LeftUpperArm": (-50 + 4 * s, -35 - 3 * c, 0), "RightUpperArm": (-50 - 4 * s, 35 + 3 * c, 0)})


clip("JumpLoop", loop_fn(20, airloop), loop=True, wind=(0, 0, -2.0), spin=(1, 1, 1), tie="rise")
clip("JumpLand", interp_keys([
    k(0, AIR),
    k(2, AIR, M({"footL": (0, 0, 0.03, 15, 0), "footR": (0, 0, 0.03, 15, 0)}, both("UpperArm", (-70, -40, 0)))),
    k(5, B, M({"hips": (0, 0, -0.26), "Spine": (30, 0, 0), "Chest": (12, 0, 0), "Head": (-22, 0, 0)}, both("UpperArm", (-30, -25, 0)), both("LowerArm", (-40, 0, 0))), 'in'),
    k(8, B, M({"hips": (0, 0, -0.22), "Spine": (26, 0, 0), "Chest": (10, 0, 0), "Head": (-18, 0, 0)}, both("UpperArm", (-20, -18, 0)), both("LowerArm", (-35, 0, 0)))),
    k(16, B)], 16), wind=(0, 0, 1.0), spin=(1, 1, 1))

# Attacks
L1 = [
    k(0, B),
    k(4, B, {"hips": (0, 0.03, -0.07), "Hips": (0, 0, -10), "Spine": (2, 0, -12), "Chest": (2, 0, -15), "Head": (-2, 0, 30),
             "RightUpperArm": (30, 25, 0), "RightLowerArm": (-60, 0, 0), "LeftUpperArm": (-40, 0, -10), "LeftLowerArm": (-60, 0, 0)}),
    k(7, B, {"hips": (0, -0.08, -0.09), "Hips": (0, 0, 12), "Spine": (10, 0, 15), "Chest": (4, 0, 22), "Head": (-6, 0, -40),
             "RightUpperArm": (-85, 0, 25), "RightLowerArm": (0, 0, 0), "LeftUpperArm": (10, -10, 0), "LeftLowerArm": (-70, 0, 0)}, 'in'),
    k(9, B, {"hips": (0, -0.09, -0.09), "Hips": (0, 0, 13), "Spine": (10, 0, 16), "Chest": (4, 0, 26), "Head": (-6, 0, -44),
             "RightUpperArm": (-80, 0, 32), "RightLowerArm": (-5, 0, 0), "LeftUpperArm": (12, -10, 0), "LeftLowerArm": (-70, 0, 0)}),
    k(16, B)]
clip("Light1", interp_keys(L1, 16), spin=(1, 1, 3))


def mirror(p):
    o = {}
    for kk, v in p.items():
        if kk.startswith("Left"):
            nk = "Right" + kk[4:]
        elif kk.startswith("Right"):
            nk = "Left" + kk[5:]
        else:
            nk = kk
        if kk in ("hips",):
            o[nk] = (-v[0], v[1], v[2])
        elif kk.startswith("foot"):
            o[kk] = v
        else:
            o[nk] = (v[0], -v[1], -v[2])
    return o


L2 = [
    k(0, B),
    k(4, B, mirror({"hips": (0, 0.03, -0.09), "Hips": (0, 0, -10), "Spine": (6, 0, -12), "Chest": (4, 0, -15), "Head": (-2, 0, 30),
                    "RightUpperArm": (35, 20, 0), "RightLowerArm": (-40, 0, 0), "LeftUpperArm": (-40, 0, -10), "LeftLowerArm": (-60, 0, 0)})),
    k(7, B, mirror({"hips": (0, -0.07, -0.05), "Hips": (0, 0, 12), "Spine": (0, 0, 15), "Chest": (-4, 0, 22), "Head": (-2, 0, -40),
                    "RightUpperArm": (-125, 0, 20), "RightLowerArm": (-5, 0, 0), "LeftUpperArm": (15, -10, 0), "LeftLowerArm": (-70, 0, 0)}), 'in'),
    k(9, B, mirror({"hips": (0, -0.08, -0.04), "Hips": (0, 0, 13), "Spine": (-2, 0, 16), "Chest": (-5, 0, 26), "Head": (-2, 0, -44),
                    "RightUpperArm": (-135, 0, 26), "RightLowerArm": (-10, 0, 0), "LeftUpperArm": (15, -10, 0), "LeftLowerArm": (-70, 0, 0)})),
    k(16, B)]
clip("Light2", interp_keys(L2, 16), spin=(1, 3, 1))
L3 = [
    k(0, B),
    k(5, B, {"hips": (0, 0, -0.09), "Hips": (0, 0, 15), "Spine": (6, 0, 20), "Chest": (4, 0, 30), "Head": (-2, 0, -55),
             "RightUpperArm": (-70, 0, 60), "RightLowerArm": (-40, 0, 0), "LeftUpperArm": (10, -20, 0), "LeftLowerArm": (-50, 0, 0)}),
    k(9, B, {"hips": (0, -0.05, -0.08), "Hips": (0, 0, -15), "Spine": (6, 0, -20), "Chest": (2, 0, -32), "Head": (-2, 0, 55),
             "RightUpperArm": (-20, 80, 0), "RightLowerArm": (10, 0, 0), "LeftUpperArm": (-30, -10, -10), "LeftLowerArm": (-70, 0, 0)}, 'in'),
    k(12, B, {"hips": (0, -0.05, -0.08), "Hips": (0, 0, -18), "Spine": (6, 0, -24), "Chest": (2, 0, -42), "Head": (-2, 0, 65),
              "RightUpperArm": (15, 75, 0), "RightLowerArm": (0, 0, 0), "LeftUpperArm": (-35, -10, -10), "LeftLowerArm": (-70, 0, 0)}, 'out'),
    k(22, B)]
clip("Light3", interp_keys(L3, 22), spin=(1, 1, 4))
HV = [
    k(0, B),
    k(8, B, M({"hips": (0, 0.04, 0.0), "Spine": (-12, 0, 0), "Chest": (-12, 0, 0), "Head": (12, 0, 0)}, both("UpperArm", (-165, -10, 0)), both("LowerArm", (-30, 0, 0)))),
    k(11, B, M({"hips": (0, 0.05, 0.0), "Spine": (-15, 0, 0), "Chest": (-14, 0, 0), "Head": (14, 0, 0)}, both("UpperArm", (-172, -10, 0)), both("LowerArm", (-35, 0, 0)))),
    k(14, B, M({"hips": (0, -0.10, -0.22), "Spine": (35, 0, 0), "Chest": (20, 0, 0), "Head": (-25, 0, 0)}, both("UpperArm", (-45, 0, -6)), both("LowerArm", (-10, 0, 0))), 'in'),
    k(19, B, M({"hips": (0, -0.10, -0.24), "Spine": (38, 0, 0), "Chest": (21, 0, 0), "Head": (-26, 0, 0)}, both("UpperArm", (-40, 0, -6)), both("LowerArm", (-10, 0, 0)))),
    k(30, B)]
clip("Heavy1", interp_keys(HV, 30), spin=(2, 5, 5))
WIND = M({"hips": (0, 0.10, -0.06), "Spine": (-18, 0, 0), "Chest": (-12, 0, 0), "Neck": (-10, 0, 0), "Head": (-15, 0, 0)}, both("UpperArm", (35, -15, 0)), both("LowerArm", (-40, 0, 0)))
HB = [
    k(0, B),
    k(6, B, WIND),
    k(8, B, M(WIND, {"footR": (0, -0.12, 0.07, -8, 0)})),
    k(10, B, M({"hips": (0, -0.22, -0.14), "Spine": (40, 0, 0), "Chest": (22, 0, 0), "Neck": (15, 0, 0), "Head": (10, 0, 0), "footR": (0, -0.25, 0, 0, 0)},
               both("UpperArm", (50, -30, 0)), both("LowerArm", (-15, 0, 0))), 'in'),
    k(14, B, M({"hips": (0, -0.24, -0.15), "Spine": (42, 0, 0), "Chest": (23, 0, 0), "Neck": (15, 0, 0), "Head": (10, 0, 0), "footR": (0, -0.25, 0, 0, 0)},
               both("UpperArm", (46, -30, 0)), both("LowerArm", (-15, 0, 0)))),
    k(20, B, {"hips": (0, -0.08, -0.07), "Spine": (12, 0, 0), "Chest": (6, 0, 0), "footR": (0, -0.12, 0.06, 0, 0)}),
    k(26, B)]
clip("Headbutt", interp_keys(HB, 26), spin=(0, 1, 1), headspin=6)
BT = [
    k(0, B),
    k(8, B, M({"hips": (0, 0.05, -0.08), "Spine": (-8, 0, 0), "Chest": (-10, 0, 0)}, both("UpperArm", (40, -40, 0)), both("LowerArm", (-50, 0, 0)))),
    k(12, B, M({"hips": (0, -0.10, -0.10), "Spine": (25, 0, 0), "Chest": (15, 0, 0), "Head": (-22, 0, 0)}, both("UpperArm", (-85, 0, -5)), both("LowerArm", (15, 0, 0))), 'in'),
    k(16, B, M({"hips": (0, -0.11, -0.10), "Spine": (28, 0, 0), "Chest": (16, 0, 0), "Head": (-24, 0, 0)}, both("UpperArm", (-70, 0, -8)), both("LowerArm", (10, 0, 0)))),
    k(30, B, M({"hips": (0, -0.03, -0.06), "Spine": (10, 0, 0), "Chest": (6, 0, 0), "Head": (-10, 0, 0)}, both("UpperArm", (-60, -15, 0)), both("LowerArm", (-20, 0, 0)))),
    k(36, B, M({"hips": (0, -0.03, -0.06), "Spine": (10, 0, 0), "Chest": (6, 0, 0), "Head": (-10, 0, 0)}, both("UpperArm", (-62, -15, 0)), both("LowerArm", (-20, 0, 0)))),
    k(38, B, M({"hips": (0, 0.04, -0.08), "Spine": (-5, 0, 0), "Chest": (-8, 0, 0)}, both("UpperArm", (-30, -15, 0)), both("LowerArm", (-60, 0, 0))), 'out'),
    k(45, B)]
bt = interp_keys(BT, 45)
for f, P in enumerate(bt):
    if 12 <= f <= 36:
        s = (f - 12) / 24.0
        for b, side in (("LeftHandBlade", 1), ("RightHandBlade", -1)):
            P["loc.%s#0" % b] = side * 0.8 * sin(2 * pi * s)
            P["loc.%s#1" % b] = -4.0 * sin(pi * s)
            P["loc.%s#2" % b] = 0.35 * sin(pi * s)
            P["flat.%s#0" % b] = min(1.0, s / 0.12, (1 - s) / 0.12)
            P["spin.%s#0" % b] = 360 * 6 * s
clip("BladeThrow", bt, spin=(2, 3, 3))


def block(t):
    s = sin(2 * pi * t)
    return M(GUARD, {"hips": (0, 0, -0.09 - 0.008 * s), "Spine": (8 + s, 0, 0), "LeftUpperArm": (-75 + 1.5 * s, 0, -20), "RightUpperArm": (-75 + 1.5 * s, 0, 20)})


clip("BlockLoop", loop_fn(30, block), loop=True, spin=(1, 1, 1))
DG = [
    k(0, B),
    k(3, B, M({"hips": (0, -0.02, -0.14), "Spine": (14, 0, 0)}, both("UpperArm", (-20, 0, 0)), both("LowerArm", (-40, 0, 0)))),
    k(6, B, M({"hips": (0, 0.10, 0.02), "Spine": (-12, 0, 0), "Chest": (-6, 0, 0), "footL": (0, -0.10, 0.14, 20, 0), "footR": (0, -0.14, 0.18, 25, 0)},
              both("UpperArm", (-55, -25, 0)), both("LowerArm", (-30, 0, 0))), 'out'),
    k(9, B, M({"hips": (0, 0.12, 0.03), "Spine": (-4, 0, 0), "footL": (0, -0.05, 0.10, 10, 0), "footR": (0, -0.06, 0.12, 10, 0)},
              both("UpperArm", (-50, -30, 0)), both("LowerArm", (-30, 0, 0)))),
    k(12, B, M({"hips": (0, 0.04, -0.16), "Spine": (16, 0, 0), "Chest": (6, 0, 0), "Head": (-12, 0, 0)}, both("UpperArm", (-30, -15, 0)), both("LowerArm", (-40, 0, 0))), 'in'),
    k(18, B)]
clip("DodgeBack", interp_keys(DG, 18), wind=(0, 1.5, 0), spin=(1, 1, 1))
HIT = {"hips": (0, 0.07, -0.03), "Hips": (0, 0, 8), "Spine": (-14, 0, 10), "Chest": (-14, 0, 12), "Neck": (-10, 0, 0), "Head": (-18, 0, -15),
       "LeftUpperArm": (15, -25, 0), "RightUpperArm": (-10, 20, 0), "LeftLowerArm": (-25, 0, 0), "RightLowerArm": (-25, 0, 0)}
HIT2 = {kk: tuple(x * 0.4 for x in v) for kk, v in HIT.items()}
clip("HitLight", interp_keys([k(0, B), k(3, B, HIT, 'out'), k(7, B, M(HIT2, {"hips": (0, 0.03, -0.05)})), k(14, B)], 14), spin=(1, 1, 1))
KD = [
    k(0, B),
    k(3, B, M({"hips": (0, 0.10, -0.05), "Spine": (-20, 0, 0), "Chest": (-18, 0, 0), "Head": (-20, 0, 0)}, both("UpperArm", (-70, -30, 0)), both("LowerArm", (-20, 0, 0))), 'out'),
    k(8, B, M({"Hips": (-40, 0, 0), "hips": (0, 0.35, -0.25), "Spine": (-10, 0, 0), "Chest": (5, 0, 0), "Head": (20, 0, 0),
               "footL": (0, 0, 0, -30, 0), "footR": (0, 0, 0, -30, 0)}, both("UpperArm", (-80, -40, 0)), both("LowerArm", (-20, 0, 0)))),
    k(13, LYING, M({"footL": (0, -0.05, 0.20, -60, 0), "footR": (0, -0.05, 0.25, -60, 0), "Head": (25, 0, 0)}, both("UpperArm", (-10, -50, 0))), 'in'),
    k(17, LYING, {"hips": (0, 0.58, -0.39), "footL": (0, 0, 0.04, -70, 0), "footR": (0, 0, 0.05, -70, 0)}),
    k(21, LYING),
    k(30, LYING)]
clip("Knockdown", interp_keys(KD, 30), spin=(1, 1, 1))
GU = [
    k(0, LYING),
    k(8, B, M({"Hips": (-50, 0, 0), "hips": (0, 0.50, -0.36), "Spine": (25, 0, 0), "Chest": (20, 0, 0), "Head": (10, 0, 0),
               "footL": (0, 0, -0.03, -40, 0), "footR": (0, 0, -0.03, -40, 0)}, both("UpperArm", (20, -20, 0)), both("LowerArm", (-30, 0, 0)))),
    k(16, B, M({"Hips": (15, 0, 0), "hips": (0, 0.15, -0.33), "Spine": (25, 0, 0), "Chest": (10, 0, 0), "Head": (-20, 0, 0)}, both("UpperArm", (-40, -10, 0)), both("LowerArm", (-40, 0, 0)))),
    k(24, B, M({"Hips": (8, 0, 0), "hips": (0, 0.02, -0.15), "Spine": (15, 0, 0), "Chest": (6, 0, 0), "Head": (-10, 0, 0)}, both("UpperArm", (-20, -5, 0)), both("LowerArm", (-25, 0, 0)))),
    k(36, B)]
clip("GetUp", interp_keys(GU, 36), spin=(1, 1, 1))
DEAD = M(LYING, {"Head": (10, 0, 25)}, both("UpperArm", (18, -55, 0)))
DE = [
    k(0, B),
    k(4, B, M({kk: tuple(x * 1.4 for x in v) for kk, v in HIT.items()}), 'out'),
    k(12, B, {"hips": (0.05, 0.12, -0.08), "Hips": (0, 0, 10), "Spine": (-10, 5, 8), "Chest": (-4, 0, 6), "Head": (-10, 0, -12),
              "LeftUpperArm": (10, -8, 0), "RightUpperArm": (10, 8, 0), "footL": (0, 0.15, 0, 0, 0)}),
    k(20, B, M({"hips": (0, 0.15, -0.30), "Hips": (-10, 0, 0), "Spine": (20, 0, 0), "Chest": (15, 0, 0), "Head": (25, 0, 0), "footL": (0, 0.15, 0, 0, 0)},
               both("UpperArm", (0, -5, 0)), both("LowerArm", (10, 0, 0)))),
    k(28, B, M({"Hips": (-45, 0, 0), "hips": (0, 0.42, -0.36), "Spine": (0, 0, 0), "Head": (10, 0, 0),
                "footL": (0, 0.10, 0, -30, 0), "footR": (0, 0, 0, -30, 0)}, both("UpperArm", (-40, -30, 0)))),
    k(34, DEAD, {"footL": (0, 0.05, 0.02, -65, 0), "footR": (0, 0, 0.06, -65, 0)}, 'in'),
    k(38, DEAD, {"hips": (0, 0.58, -0.41)}),
    k(42, DEAD),
    k(50, DEAD)]
clip("Death", interp_keys(DE, 50), spin=(3, 3, 3), spinfn=lambda t: min(1.0, 1 - (1 - min(1.0, t / 0.9)) ** 2))

ONLY = globals().get("ONLY")
made = {}
for name, (poses, kw) in CLIPS.items():
    if ONLY and name not in ONLY:
        continue
    a = bake(name, [dict(p) for p in poses], **kw)
    made[name] = len(poses) - 1
ao.animation_data.action = bpy.data.actions["Idle"]
try:
    ao.animation_data.action_slot = bpy.data.actions["Idle"].slots[0]
except Exception:
    pass
bpy.context.scene.frame_set(0)
RESULT = made
