"""
🛡️ Noosphere Content Safety — NudeNet AI Moderation
AI 内容安全审核：对多媒体意识体（图片/视频）进行 NSFW 检测

Usage:
    python scripts/content_moderation.py <media_url> [--type image|video]

Exit codes:
    0 = SAFE (通过审核)
    1 = UNSAFE (检测到违规内容)
    2 = ERROR (审核过程出错，fail-open 策略)

Output:
    JSON to stdout with moderation results
"""
import sys
import json
import os
import tempfile
import urllib.request
import urllib.error


# ── NSFW 危险标签（检测到即拒绝） ──
UNSAFE_LABELS = {
    "FEMALE_BREAST_EXPOSED",
    "FEMALE_GENITALIA_EXPOSED",
    "MALE_GENITALIA_EXPOSED",
    "ANUS_EXPOSED",
    "BUTTOCKS_EXPOSED",
}

# ── 次危险标签（高置信度时拒绝） ──
WARN_LABELS = {
    "FEMALE_GENITALIA_COVERED",
    "BUTTOCKS_COVERED",
    "ANUS_COVERED",
}

# 置信度阈值
UNSAFE_THRESHOLD = 0.6   # 危险标签超过此分数 → 拒绝
WARN_THRESHOLD = 0.85    # 次危险标签超过此分数 → 拒绝


def download_media(url: str, suffix: str = ".jpg") -> str:
    """下载媒体文件到临时目录"""
    tmp = tempfile.mktemp(suffix=suffix)
    headers = {"User-Agent": "Noosphere-ContentMod/1.0"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        with open(tmp, "wb") as f:
            f.write(resp.read())
    return tmp


def extract_video_frames(video_path: str, max_frames: int = 5) -> list[str]:
    """从视频中抽取关键帧用于检测"""
    try:
        import cv2
    except ImportError:
        print("⚠️ opencv-python not available, skipping video frame extraction", file=sys.stderr)
        return []

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return []

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames <= 0:
        return []

    # 均匀抽取帧
    step = max(1, total_frames // max_frames)
    frame_paths = []

    for i in range(0, total_frames, step):
        if len(frame_paths) >= max_frames:
            break
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = cap.read()
        if ret:
            tmp = tempfile.mktemp(suffix=f"_frame{i}.jpg")
            cv2.imwrite(tmp, frame)
            frame_paths.append(tmp)

    cap.release()
    return frame_paths


def moderate_image(detector, image_path: str) -> dict:
    """对单张图片进行 NudeNet 审核"""
    detections = detector.detect(image_path)

    unsafe_hits = []
    warn_hits = []

    for d in detections:
        label = d["class"]
        score = d["score"]

        if label in UNSAFE_LABELS and score >= UNSAFE_THRESHOLD:
            unsafe_hits.append({"label": label, "score": round(score, 3)})
        elif label in WARN_LABELS and score >= WARN_THRESHOLD:
            warn_hits.append({"label": label, "score": round(score, 3)})

    is_safe = len(unsafe_hits) == 0 and len(warn_hits) == 0

    return {
        "is_safe": is_safe,
        "unsafe_detections": unsafe_hits,
        "warn_detections": warn_hits,
        "total_detections": len(detections),
    }


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: content_moderation.py <media_url> [--type image|video]"}))
        sys.exit(2)

    media_url = sys.argv[1]
    media_type = "image"  # default

    if "--type" in sys.argv:
        idx = sys.argv.index("--type")
        if idx + 1 < len(sys.argv):
            media_type = sys.argv[idx + 1]

    # Skip audio — NudeNet only handles visual content
    if media_type == "voice":
        result = {
            "status": "SKIPPED",
            "reason": "Audio content does not require visual moderation",
            "media_type": media_type,
        }
        print(json.dumps(result))
        sys.exit(0)

    print(f"🛡️ Content moderation: {media_type} from {media_url[:80]}...", file=sys.stderr)

    # ── Download media ──
    try:
        suffix = ".mp4" if media_type == "video" else ".jpg"
        local_path = download_media(media_url, suffix=suffix)
        file_size = os.path.getsize(local_path)
        print(f"   Downloaded: {file_size / 1024:.1f} KB", file=sys.stderr)
    except Exception as e:
        result = {
            "status": "ERROR",
            "reason": f"Failed to download media: {str(e)}",
            "media_type": media_type,
        }
        print(json.dumps(result))
        sys.exit(2)  # fail-open

    # ── Initialize NudeNet ──
    try:
        from nudenet import NudeDetector
        detector = NudeDetector()
    except ImportError:
        result = {
            "status": "ERROR",
            "reason": "NudeNet not installed (pip install nudenet)",
            "media_type": media_type,
        }
        print(json.dumps(result))
        sys.exit(2)  # fail-open

    # ── Run detection ──
    try:
        if media_type == "video":
            # Extract frames and check each
            frames = extract_video_frames(local_path, max_frames=5)
            if not frames:
                # Can't extract frames, try treating as image
                frames = [local_path]

            all_results = []
            is_safe = True
            for frame_path in frames:
                frame_result = moderate_image(detector, frame_path)
                all_results.append(frame_result)
                if not frame_result["is_safe"]:
                    is_safe = False

            # Aggregate unsafe detections
            all_unsafe = []
            all_warn = []
            for r in all_results:
                all_unsafe.extend(r["unsafe_detections"])
                all_warn.extend(r["warn_detections"])

            result = {
                "status": "SAFE" if is_safe else "UNSAFE",
                "media_type": media_type,
                "frames_checked": len(frames),
                "unsafe_detections": all_unsafe,
                "warn_detections": all_warn,
            }

            # Cleanup temp frames
            for f in frames:
                try:
                    os.unlink(f)
                except OSError:
                    pass
        else:
            # Image moderation
            img_result = moderate_image(detector, local_path)
            result = {
                "status": "SAFE" if img_result["is_safe"] else "UNSAFE",
                "media_type": media_type,
                "unsafe_detections": img_result["unsafe_detections"],
                "warn_detections": img_result["warn_detections"],
                "total_detections": img_result["total_detections"],
            }

        # Cleanup
        try:
            os.unlink(local_path)
        except OSError:
            pass

    except Exception as e:
        result = {
            "status": "ERROR",
            "reason": f"Detection error: {str(e)}",
            "media_type": media_type,
        }
        print(json.dumps(result))
        sys.exit(2)  # fail-open

    # ── Output result ──
    print(json.dumps(result))

    if result["status"] == "UNSAFE":
        unsafe_labels = [d["label"] for d in result.get("unsafe_detections", [])]
        print(f"🚫 UNSAFE content detected: {', '.join(unsafe_labels)}", file=sys.stderr)
        sys.exit(1)
    elif result["status"] == "SAFE":
        print("✅ Content safety check PASSED", file=sys.stderr)
        sys.exit(0)
    else:
        print(f"⚠️ Moderation inconclusive: {result.get('reason', 'unknown')}", file=sys.stderr)
        sys.exit(2)  # fail-open


if __name__ == "__main__":
    main()
