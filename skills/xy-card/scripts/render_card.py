#!/usr/bin/env python3
"""把一段文字渲染成3:4图文卡片，输出PNG。调用系统已装的Chrome/Chromium headless截图，不依赖任何npm/pip第三方包。"""
import argparse
import html
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import urllib.request


def find_chrome():
    candidates = []
    system = platform.system()
    if system == "Darwin":
        candidates.append("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
        candidates.append("/Applications/Chromium.app/Contents/MacOS/Chromium")
    elif system == "Windows":
        candidates.append(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
        candidates.append(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe")
    else:
        for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
            path = shutil.which(name)
            if path:
                candidates.append(path)
    for path in candidates:
        if os.path.exists(path) or shutil.which(path):
            return path
    return None


def escape(s):
    return html.escape(s or "", quote=True)


def font_size_and_top(text_len):
    if text_len <= 120:
        return 36, 14
    if text_len <= 220:
        return 30, 8
    if text_len <= 320:
        return 26, 5
    return 22, 3


def bg_to_data_uri(bg_url):
    """把背景图下载下来转成data URI内嵌进HTML，绕开file://页面加载远程图片的限制。"""
    try:
        req = urllib.request.Request(bg_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            data = r.read()
            content_type = r.headers.get_content_type() or "image/jpeg"
        import base64
        b64 = base64.b64encode(data).decode("ascii")
        return f"data:{content_type};base64,{b64}"
    except Exception as e:
        print(f"警告：背景图下载失败({e})，改用纯色背景", file=sys.stderr)
        return None


def render_html(name, handle, date, avatar, text, bg_data_uri):
    text = text[:2000]
    font_size, top = font_size_and_top(len(text))
    safe_avatar = avatar or (
        "https://api.dicebear.com/7.x/initials/svg?seed=" + escape(name or "Me")
    )
    bg_style = (
        f'background-image:url({bg_data_uri});background-size:cover;background-position:center;'
        if bg_data_uri
        else "background:#222;"
    )
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  html,body {{ width:1080px; height:1440px; overflow:hidden; }}
  body {{ font-family: -apple-system, "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif; }}
  .card-wrap {{ width:1080px; height:1440px; position:relative; overflow:hidden; {bg_style} }}
  .overlay {{ position:absolute; inset:0; background:rgba(0,0,0,.25); }}
  .tweet-card {{ position:absolute; left:48px; right:48px; top:{top}%; background:rgba(255,255,255,0.97); border-radius:36px; padding:48px 44px; box-shadow:0 16px 60px rgba(0,0,0,.35); }}
  .head {{ display:flex; align-items:center; gap:24px; margin-bottom:32px; }}
  .avatar {{ width:96px; height:96px; border-radius:50%; object-fit:cover; background:#ddd; }}
  .name-row {{ display:flex; align-items:center; gap:10px; }}
  .name {{ font-weight:700; font-size:32px; color:#0f1419; }}
  .check {{ width:32px; height:32px; border-radius:50%; background:#1d9bf0; display:flex; align-items:center; justify-content:center; flex-shrink:0; }}
  .check svg {{ width:19px; height:19px; }}
  .handle-date {{ font-size:26px; color:#667; margin-top:4px; }}
  .body-text {{ font-size:{font_size}px; line-height:1.65; color:#0f1419; white-space:pre-wrap; word-break:break-word; }}
</style></head>
<body>
  <div class="card-wrap">
    <div class="overlay"></div>
    <div class="tweet-card">
      <div class="head">
        <img class="avatar" src="{escape(safe_avatar)}" />
        <div>
          <div class="name-row">
            <span class="name">{escape(name or '你的名字')}</span>
            <span class="check"><svg viewBox="0 0 24 24" fill="none"><path d="M4 12l5 5L20 6" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg></span>
          </div>
          <div class="handle-date">{escape(handle or '@yourhandle')} · {escape(date or '')}</div>
        </div>
      </div>
      <div class="body-text">{escape(text)}</div>
    </div>
  </div>
</body></html>"""


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--text", required=True, help="卡片正文")
    ap.add_argument("--name", default="", help="显示名字")
    ap.add_argument("--handle", default="", help="账号，如 @yourhandle")
    ap.add_argument("--date", default="", help="日期")
    ap.add_argument("--avatar", default="", help="头像图片URL，留空用占位头像")
    ap.add_argument("--bg", default="", help="背景图URL，留空用纯色背景")
    ap.add_argument("--out", required=True, help="输出PNG路径")
    args = ap.parse_args()

    chrome = find_chrome()
    if not chrome:
        print("错误：没找到系统已装的Chrome/Chromium，先装一个(google-chrome / chromium都行)。", file=sys.stderr)
        sys.exit(1)

    bg_data_uri = bg_to_data_uri(args.bg) if args.bg else None
    html_content = render_html(args.name, args.handle, args.date, args.avatar, args.text, bg_data_uri)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(html_content)
        html_path = f.name

    out_path = os.path.abspath(args.out)
    try:
        subprocess.run(
            [
                chrome,
                "--headless",
                "--disable-gpu",
                f"--screenshot={out_path}",
                "--window-size=1080,1440",
                "--force-device-scale-factor=2",
                "--default-background-color=00000000",
                "file://" + html_path,
            ],
            check=True,
            timeout=30,
        )
    finally:
        os.unlink(html_path)

    print(f"已生成：{out_path}")


if __name__ == "__main__":
    main()
