# Sawblade

A rigged, game-ready character: a muscular red-skinned brute with a sawblade head and sawblade hands.

## Files

| File | What it is |
| --- | --- |
| `Sawblade.fbx` | Rigged export for Unity (Y up, 2.2 m tall, textures embedded, 14 animation clips) |
| `Sawblade.blend` | Blender 5.2 source with the rig and the original high-poly mesh (hidden) |
| `sawblade 3d model.glb` | Original unrigged model |
| `sawblade*.png` | Reference images |

## Two versions

| Version | Files | Head blade |
| --- | --- | --- |
| Original | `Sawblade.fbx`, `Sawblade.blend` | Eye in the centre of the blade |
| Scar | `ScarSawblade.fbx`, `ScarSawblade.blend` | No eye; bare blade face with a deep vertical scar cut into it (30,989 triangles) |

Both versions share the same skeleton and the same 14 animation clips.

## SawBladeLean

A separate build of the character on its own skeleton: `SawBladeLean.fbx` and `SawBladeLean.blend`. It does not share the skeleton or the animation clips above; it has its own 22 clips, listed below.

- 45,835 triangles, one material, 1.8 m tall, textures embedded in the FBX
- 40 bones using Unity Humanoid names (`Hips`, `Spine`, `Chest`, `Neck`, `Head`, ...); no finger bones
- Extra bones: `HeadBlade`, `LeftHandBlade`, `RightHandBlade` (spin around the bone's length axis), `Tie_01`-`Tie_10`, `CoatTail_Back_01`, `CoatTail_Back_02`, `CoatTail_Left`, `CoatTail_Right`, `CoatTail_FrontLeft`, `CoatTail_FrontRight`
- Hand blades are complete discs, so they can spin or leave the hand
- Max 4 bone influences per vertex; rest pose is arms-down, not a T-pose
- `SawBladeLean.blend` is the Blender 5.2 source with the rig and the original high-poly mesh (hidden)

### SawBladeLean animations

All clips are in place (no root motion), 30 fps, with every frame keyed. In Unity the takes are named `SawCharacter_Rig|<Clip>`. One-shots start and end on the `Idle` pose unless noted.

| Clip | Frames | Type | Notes |
| --- | --- | --- | --- |
| `Idle` | 60 | Loop | |
| `Walk` | 28 | Loop | |
| `Run` | 18 | Loop | Tie streams back over the left shoulder. |
| `Sprint` | 14 | Loop | Tie streams back over the left shoulder. |
| `WalkBack` | 28 | Loop | Arms in a half guard. |
| `StrafeLeft`, `StrafeRight` | 24 | Loop | Arms in a half guard. |
| `JumpStart` | 12 | One-shot | `Idle` to the air pose. |
| `JumpLoop` | 20 | Loop | Air pose. Tie floats upward. |
| `JumpLand` | 16 | One-shot | Air pose to `Idle`. |
| `Light1` | 16 | One-shot | Right blade jab. |
| `Light2` | 16 | One-shot | Left blade rising slash. |
| `Light3` | 22 | One-shot | Right spinning backhand. |
| `Heavy1` | 30 | One-shot | Overhead double-blade slam. |
| `Headbutt` | 26 | One-shot | Steps in and drives the head blade forward. The only clip where the head blade spins. |
| `BladeThrow` | 45 | One-shot | Both hand blades fly 4 m forward and return. |
| `BlockLoop` | 30 | Loop | Blades crossed in front. |
| `DodgeBack` | 18 | One-shot | Hop back. |
| `HitLight` | 14 | One-shot | |
| `Knockdown` | 30 | One-shot | Ends lying on his back. |
| `GetUp` | 36 | One-shot | Starts from the `Knockdown` end pose. |
| `Death` | 50 | One-shot | Collapses backward; hand blades spin down to a stop. |

- Head blade stays upright and only rocks a few degrees, except in `Headbutt`. Hand blades spin in every clip.
- Tie hangs down the front when standing, shortened by a scale key on `Tie_01` (Y about 0.28), and returns to full length when it flies. It is kept above a flat floor at his feet.

## Rig

- 31,118 triangles, one material, 4K base colour / normal / roughness-metallic maps
- 35 bones using Unity Humanoid names (`Hips`, `Spine`, `Chest`, `UpperChest`, `Neck`, `Head`, ...); no finger bones
- Extra bones: `RightBlade`, `LeftBlade`, `HeadBlade` (spin around the bone's length axis), `Tie_01`-`Tie_06`, `CoatTail_Back_01`, `CoatTail_Back_02`, `CoatTail_L`, `CoatTail_R`
- Max 4 bone influences per vertex
- Rest pose is arms-down, not a T-pose

## Animations

All clips are in place (no root motion), 30 fps, with every frame keyed. The three blade bones spin in every clip.

| Clip | Frames | Length | Notes |
| --- | --- | --- | --- |
| `Idle` | 60 | 2.0 s | Loop. |
| `Walk` | 28 | 0.93 s | Loop. Matches a ground speed of about 1.0 m/s. Tie hangs down the front. |
| `Run` | 18 | 0.6 s | Loop. Matches about 2.8 m/s. Tie streams back over the left shoulder. |
| `WalkToRun` | 22 | 0.73 s | One-shot. Starts on the first frame of `Walk`, ends on the first frame of `Run`. |
| `Punch` | 20 | 0.67 s | Right blade jab. Starts and ends on `Idle`. |
| `BladeThrow` | 45 | 1.5 s | Both hand blades fly 4 m forward and return. Starts and ends on `Idle`. |
| `Kick` | 26 | 0.87 s | Right front kick. Starts and ends on `Idle`. |
| `JumpStart` | 12 | 0.4 s | `Idle` to the air pose. |
| `JumpLoop` | 20 | 0.67 s | Loop. Air pose. |
| `JumpLand` | 16 | 0.53 s | Air pose to `Idle`. |
| `JumpPunch` | 18 | 0.6 s | Overhead double-blade slam. Starts and ends on the air pose. |
| `JumpKick` | 18 | 0.6 s | Air kick. Starts and ends on the air pose. |
| `HitReact` | 14 | 0.47 s | Starts and ends on `Idle`. |
| `Death` | 50 | 1.67 s | Falls backward and stays down. |

## Unity import

1. Drop `Sawblade.fbx` into `Assets`.
2. Materials tab: Extract Textures, then Extract Materials.
3. Rig tab: Animation Type = Humanoid, Apply.
4. If bones show red in Configure, use Pose > Enforce T-Pose.
