# Sawblade

A rigged, game-ready character: a muscular red-skinned brute with a sawblade head and sawblade hands.

## Files

| File | What it is |
| --- | --- |
| `Sawblade.fbx` | Rigged export for Unity (Y up, 2.2 m tall, textures embedded, no animation) |
| `Sawblade.blend` | Blender 5.2 source with the rig and the original high-poly mesh (hidden) |
| `sawblade 3d model.glb` | Original unrigged model |
| `sawblade*.png` | Reference images |

## Rig

- 31,118 triangles, one material, 4K base colour / normal / roughness-metallic maps
- 35 bones using Unity Humanoid names (`Hips`, `Spine`, `Chest`, `UpperChest`, `Neck`, `Head`, ...); no finger bones
- Extra bones: `RightBlade`, `LeftBlade`, `HeadBlade` (spin around the bone's length axis), `Tie_01`-`Tie_06`, `CoatTail_Back_01`, `CoatTail_Back_02`, `CoatTail_L`, `CoatTail_R`
- Max 4 bone influences per vertex
- Rest pose is arms-down, not a T-pose

## Unity import

1. Drop `Sawblade.fbx` into `Assets`.
2. Materials tab: Extract Textures, then Extract Materials.
3. Rig tab: Animation Type = Humanoid, Apply.
4. If bones show red in Configure, use Pose > Enforce T-Pose.
