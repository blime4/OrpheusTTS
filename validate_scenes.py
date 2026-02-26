#!/usr/bin/env python3
"""
Manim Scene Validator — 检测动画中的重叠、出界、位置异常问题。

工作原理：
  1. Monkey-patch Scene.play() 来拦截每一步动画
  2. 对每个动画参数，将其 mobject 添加到场景并设置到最终状态
  3. 每步后扫描所有在场 mobject 的边界框
  4. 检测出界 (OOB) 和重叠 (OVERLAP)

用法：
  source .venv/bin/activate
  python validate_scenes.py [--scene SceneName] [--overlap-threshold 0.3] [--verbose]
"""

import sys
import argparse
import importlib
import traceback
import numpy as np
from collections import defaultdict

from manim import *

# Disable rendering
config.preview = False
config.write_to_movie = False
config.disable_caching = True
config.quality = "low_quality"


# ================================================================
# Geometry helpers
# ================================================================

FRAME_W = config.frame_width    # ~14.22
FRAME_H = config.frame_height   # 8.0
HALF_W = FRAME_W / 2
HALF_H = FRAME_H / 2
EDGE_TOL = 0.05  # small tolerance


def get_bbox(mob):
    """Return (left, right, bottom, top) or None."""
    try:
        if not mob.has_points() and not mob.submobjects:
            return None
        ul = mob.get_corner(UL)
        dr = mob.get_corner(DR)
        l, r = float(ul[0]), float(dr[0])
        b, t = float(dr[1]), float(ul[1])
        if r - l < 1e-5 or t - b < 1e-5:
            return None
        return (l, r, b, t)
    except Exception:
        return None


def bbox_area(bbox):
    l, r, b, t = bbox
    return max(0, r - l) * max(0, t - b)


def bbox_intersection(b1, b2):
    l = max(b1[0], b2[0])
    r = min(b1[1], b2[1])
    b = max(b1[2], b2[2])
    t = min(b1[3], b2[3])
    if l < r and b < t:
        return (l, r, b, t)
    return None


def overlap_ratio(b1, b2):
    inter = bbox_intersection(b1, b2)
    if inter is None:
        return 0.0
    inter_area = bbox_area(inter)
    min_area = min(bbox_area(b1), bbox_area(b2))
    if min_area < 1e-6:
        return 0.0
    return inter_area / min_area


def is_oob(bbox):
    l, r, b, t = bbox
    violations = []
    if l < -HALF_W - EDGE_TOL:
        violations.append(f"LEFT (x={l:.2f} < {-HALF_W:.2f})")
    if r > HALF_W + EDGE_TOL:
        violations.append(f"RIGHT (x={r:.2f} > {HALF_W:.2f})")
    if b < -HALF_H - EDGE_TOL:
        violations.append(f"BOTTOM (y={b:.2f} < {-HALF_H:.2f})")
    if t > HALF_H + EDGE_TOL:
        violations.append(f"TOP (y={t:.2f} > {HALF_H:.2f})")
    return violations


def mob_label(mob):
    """Human-readable label for a mobject."""
    cls = type(mob).__name__
    if isinstance(mob, (Text, MarkupText)):
        txt = getattr(mob, 'text', getattr(mob, 'original_text', ''))
        return f'{cls}("{txt[:25]}")'
    if isinstance(mob, VGroup):
        # Try to find a text child for better labeling
        for sub in mob.submobjects[:3]:
            if isinstance(sub, (Text, MarkupText)):
                txt = getattr(sub, 'text', '')
                return f'{cls}["{txt[:20]}",...]'
        return f'{cls}({len(mob.submobjects)} sub)'
    return cls


def mob_label_deep(mob, depth=0):
    """Detailed label with position info."""
    bbox = get_bbox(mob)
    pos = f"({bbox[0]:.1f},{bbox[2]:.1f})-({bbox[1]:.1f},{bbox[3]:.1f})" if bbox else "no-bbox"
    return f"{'  '*depth}{mob_label(mob)} @ {pos}"


# ================================================================
# Issue tracker
# ================================================================

class IssueTracker:
    def __init__(self):
        self.issues = []

    def add(self, severity, scene_name, step, msg):
        self.issues.append((severity, scene_name, step, msg))

    def report(self):
        if not self.issues:
            print("\n✅ 所有场景验证通过，未发现问题！")
            return True

        print(f"\n{'='*70}")
        print(f"  验证报告 — 共发现 {len(self.issues)} 个问题")
        print(f"{'='*70}")

        # Group by scene
        by_scene = defaultdict(list)
        for sev, scene, step, msg in self.issues:
            by_scene[scene].append((sev, step, msg))

        for scene_name, items in by_scene.items():
            print(f"\n  📌 {scene_name}:")
            errors = [(s, st, m) for s, st, m in items if s == "ERROR"]
            warns = [(s, st, m) for s, st, m in items if s == "WARN"]
            for sev, step, msg in errors:
                print(f"    🔴 step {step}: {msg}")
            for sev, step, msg in warns:
                print(f"    🟡 step {step}: {msg}")

        total_err = sum(1 for s, _, _, _ in self.issues if s == "ERROR")
        total_warn = sum(1 for s, _, _, _ in self.issues if s == "WARN")
        print(f"\n  总计: {total_err} 错误, {total_warn} 警告")
        print(f"{'='*70}")
        return False


# ================================================================
# Scene validator
# ================================================================

class SceneValidator:
    def __init__(self, scene_class, tracker, overlap_threshold=0.3, verbose=False):
        self.scene_class = scene_class
        self.scene_name = scene_class.__name__
        self.tracker = tracker
        self.overlap_threshold = overlap_threshold
        self.verbose = verbose
        self.step = 0
        self._reported_overlaps = set()
        self._reported_oob = set()

    def validate(self):
        print(f"\n🔍 验证 {self.scene_name} ...")
        self.step = 0
        self._reported_overlaps = set()
        self._reported_oob = set()

        scene = self.scene_class()
        validator = self

        def patched_play(*args, **kwargs):
            for anim_arg in args:
                if isinstance(anim_arg, Animation):
                    mob = anim_arg.mobject
                    if mob is not None:
                        # Add to scene if not already there
                        if mob not in scene.mobjects:
                            scene.add(mob)
                        # Apply animation to final state
                        try:
                            anim_arg._setup_scene(scene)
                            anim_arg.begin()
                            # Interpolate to t=1 (final state)
                            anim_arg.interpolate(1.0)
                            anim_arg.finish()
                        except Exception as e:
                            if validator.verbose:
                                print(f"    ⚠ Animation error: {e}")
                        # Re-add mob in case clean_up removed it
                        if mob not in scene.mobjects:
                            scene.add(mob)

            validator.step += 1
            validator._check_frame(scene)

        def patched_wait(*args, **kwargs):
            pass

        scene.play = patched_play
        scene.wait = patched_wait

        try:
            scene.construct()
        except Exception as e:
            self.tracker.add("ERROR", self.scene_name, self.step,
                             f"construct() 异常: {type(e).__name__}: {e}")
            if self.verbose:
                traceback.print_exc()

        # Final frame check
        self._check_frame(scene, final=True)
        print(f"  ✓ {self.scene_name} 完成，共 {self.step} 步动画，"
              f"最终 {len(scene.mobjects)} 个 mobject")

    def _check_frame(self, scene, final=False):
        """Check all mobjects on screen for issues."""
        mobs_with_bbox = []
        for mob in scene.mobjects:
            bbox = get_bbox(mob)
            if bbox is not None:
                mobs_with_bbox.append((mob, bbox))

        if self.verbose and final:
            print(f"    最终帧 mobjects ({len(mobs_with_bbox)}):")
            for mob, bbox in mobs_with_bbox:
                print(f"      {mob_label_deep(mob)}")

        # 1) Out-of-bounds check
        for mob, bbox in mobs_with_bbox:
            violations = is_oob(bbox)
            if violations:
                label = mob_label(mob)
                # Use bbox as part of key to catch different positions
                key = (label, tuple(violations))
                if key not in self._reported_oob:
                    self._reported_oob.add(key)
                    l, r, b, t = bbox
                    self.tracker.add(
                        "ERROR", self.scene_name, self.step,
                        f"出界 [OOB] {label} bbox=({l:.1f},{b:.1f})-({r:.1f},{t:.1f}) → {', '.join(violations)}"
                    )

        # 2) Overlap check — pairwise among top-level mobs
        #    Skip parent-child pairs (VGroup contains its children's bbox)
        #    Only compare mobs that are NOT ancestors of each other
        for i in range(len(mobs_with_bbox)):
            for j in range(i + 1, len(mobs_with_bbox)):
                mob_i, bbox_i = mobs_with_bbox[i]
                mob_j, bbox_j = mobs_with_bbox[j]

                # Skip if one is ancestor of the other
                if self._is_ancestor(mob_i, mob_j) or self._is_ancestor(mob_j, mob_i):
                    continue

                ratio = overlap_ratio(bbox_i, bbox_j)
                if ratio > self.overlap_threshold:
                    l1 = mob_label(mob_i)
                    l2 = mob_label(mob_j)
                    key = tuple(sorted([l1, l2]))
                    if key not in self._reported_overlaps:
                        self._reported_overlaps.add(key)
                        severity = "ERROR" if ratio > 0.6 else "WARN"
                        self.tracker.add(
                            severity, self.scene_name, self.step,
                            f"重叠 [OVERLAP {ratio:.0%}] {l1} ↔ {l2}"
                        )

    @staticmethod
    def _is_ancestor(potential_ancestor, mob):
        """Check if potential_ancestor contains mob (directly or nested)."""
        if not hasattr(potential_ancestor, 'submobjects'):
            return False
        for sub in potential_ancestor.submobjects:
            if sub is mob:
                return True
            if SceneValidator._is_ancestor(sub, mob):
                return True
        return False


# ================================================================
# Main
# ================================================================

def main():
    parser = argparse.ArgumentParser(description="Manim 场景验证器")
    parser.add_argument("--scene", type=str, default=None,
                        help="只验证指定场景 (类名)")
    parser.add_argument("--overlap-threshold", type=float, default=0.3,
                        help="重叠比例阈值 (默认 0.3)")
    parser.add_argument("--scenes-file", type=str, default="scenes",
                        help="场景模块名 (默认 scenes)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="详细输出")
    args = parser.parse_args()

    try:
        scenes_mod = importlib.import_module(args.scenes_file)
    except ImportError as e:
        print(f"❌ 无法导入 {args.scenes_file}: {e}")
        sys.exit(1)

    # Only pick up our Scene1-7 classes (filter out Manim built-in subclasses)
    scene_classes = []
    for name in sorted(dir(scenes_mod)):
        obj = getattr(scenes_mod, name)
        if (isinstance(obj, type)
            and issubclass(obj, Scene)
            and obj.__module__ == scenes_mod.__name__  # defined in our file
            and name.startswith("Scene")):
            if args.scene is None or name == args.scene:
                scene_classes.append(obj)

    if not scene_classes:
        print(f"❌ 未找到场景类" + (f" (filter: {args.scene})" if args.scene else ""))
        sys.exit(1)

    print(f"📋 将验证 {len(scene_classes)} 个场景")
    print(f"   Frame: {FRAME_W:.2f} × {FRAME_H:.2f} (half: ±{HALF_W:.2f} × ±{HALF_H:.2f})")
    print(f"   重叠阈值: {args.overlap_threshold:.0%}")

    tracker = IssueTracker()

    for sc in scene_classes:
        validator = SceneValidator(sc, tracker, args.overlap_threshold, args.verbose)
        validator.validate()

    ok = tracker.report()
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
