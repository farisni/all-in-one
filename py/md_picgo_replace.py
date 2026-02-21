#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys
import os
import subprocess
from pathlib import Path
from urllib.parse import urlparse, unquote

# Match inline image: ![alt](url) or ![](url)
IMG_RE = re.compile(r'!\[[^\]]*?\]\(\s*(<?)([^)\n]+?)(>?)\s*\)')
URL_LINE_RE = re.compile(r'^https?://\S+$', re.IGNORECASE)
PICGO_HOSTS = {"faris-note-picture.oss-cn-guangzhou.aliyuncs.com"}

def is_remote(link: str) -> bool:
    l = link.strip().lower()
    return l.startswith("http://") or l.startswith("https://") or l.startswith("data:")

def strip_angle(link: str) -> str:
    link = link.strip()
    if link.startswith("<") and link.endswith(">"):
        return link[1:-1].strip()
    return link

def extract_target(raw_link: str) -> str:
    """
    Extract the actual link target from markdown link text.
    Supports title: ![alt](url "title") or ![alt](<url> "title")
    """
    s = raw_link.strip()
    if s.startswith("<"):
        end = s.find(">")
        if end != -1:
            return s[1:end].strip()
        return s
    # take the first token as URL/path (titles start after whitespace)
    return s.split(None, 1)[0]

def resolve_local_path(link: str, md_dir: Path, base_dir: Path | None = None) -> Path | None:
    """
    Resolve a markdown image link to a local filesystem path.
    Supports relative, absolute, and file:// links.
    """
    link = strip_angle(link)

    if is_remote(link):
        return None

    if link.startswith("file://"):
        p = urlparse(link)
        return Path(unquote(p.path))

    # For filesystem lookup, strip ?query and #hash
    clean = link.split("?", 1)[0].split("#", 1)[0]

    p = Path(clean)
    if p.is_absolute():
        return p
    # If user provides a base dir, use it first for non-absolute paths
    if base_dir is not None:
        return (base_dir / p).resolve()
    return (md_dir / p).resolve()

def picgo_upload_get_url(file_path: Path, picgo_cmd: str) -> str:
    """
    Run: picgo upload <file>
    Parse output:
      [PicGo SUCCESS]:
      https://...
    Return the first line that is exactly a URL.
    """
    proc = subprocess.run(
        [picgo_cmd, "upload", str(file_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False
    )
    out = proc.stdout or ""

    if proc.returncode != 0:
        raise RuntimeError(f"picgo upload failed (code {proc.returncode}). Output:\n{out}")

    for line in out.splitlines():
        line = line.strip()
        if URL_LINE_RE.match(line):
            return line

    # fallback
    m = re.search(r"(https?://\S+)", out)
    if m:
        return m.group(1)

    raise RuntimeError(f"Upload succeeded but no URL found in output:\n{out}")

def replace_img(md_path: str, default_base_dir:str):
    # 要替换的图片地址的父级地址 -- >media/media/image1.png 的父级
    # images/e698167be1d2702aeeb934d --- > ? 找目录 06、ElasticSearch.pdf-80d6d78b-38da-4476-acdb-d700caf9244d
    #default_base_dir = Path("/Users/nidazhong/My-Vault/My Vault/Test")
    
    default_picgo_cmd = "/Users/nidazhong/.nvm/versions/node/v20.19.0/bin/picgo"

    # if len(sys.argv) < 2:
    #     print("Usage: python3 md_picgo_replace.py /path/to/doc.md [base_dir] [picgo_cmd]")
    #     sys.exit(1)

    # md_path = Path(sys.argv[1]).expanduser().resolve()
    # if not md_path.exists():
    #     print(f"Markdown not found: {md_path}")
    #     sys.exit(1)

    md_dir = md_path.parent
    base_dir = default_base_dir
    picgo_cmd = default_picgo_cmd
    if len(sys.argv) >= 3:
        base_dir = Path(sys.argv[2]).expanduser().resolve()
    if len(sys.argv) >= 4:
        picgo_cmd = sys.argv[3]
    content = md_path.read_text(encoding="utf-8")

    matches = list(IMG_RE.finditer(content))
    if not matches:
        print("No inline markdown image links found.")
        sys.exit(0)

    path_to_url: dict[Path, str] = {}   # dedupe uploads
    link_to_url: dict[str, str] = {}    # exact replacement by original link text

    for m in matches:
        raw_link = m.group(2).strip()
        target = extract_target(raw_link)

        # skip already remote links
        if is_remote(strip_angle(target)):
            try:
                host = urlparse(strip_angle(target)).netloc.lower()
            except Exception:
                host = ""
            # already picgo-hosted, do not replace
            if host in PICGO_HOSTS:
                continue
            continue

        local_path = resolve_local_path(target, md_dir, base_dir)
        if local_path is None:
            continue

        if not local_path.exists() or not local_path.is_file():
            print(f"[WARN] Not found, skip: {raw_link} -> {local_path}")
            continue

        if local_path in path_to_url:
            link_to_url[raw_link] = path_to_url[local_path]
            continue

        try:
            print(f"[UPLOAD] {local_path}")
            url = picgo_upload_get_url(local_path, picgo_cmd)
            print(f"[OK] {url}")
            path_to_url[local_path] = url
            link_to_url[raw_link] = url
        except Exception as e:
            print(f"[ERROR] {e}")
            continue

    if not link_to_url:
        print("No local images uploaded; nothing to replace.")
        sys.exit(0)

    def replace_fn(match: re.Match) -> str:
        link = match.group(2).strip()
        target = extract_target(link)
        new_url = link_to_url.get(link)
        if not new_url:
            return match.group(0)
        # replace only the URL/path part, keep any title text
        replaced = link.replace(target, new_url, 1)
        return match.group(0).replace(match.group(2), replaced, 1)

    new_content = IMG_RE.sub(replace_fn, content)

    out_path = md_path.with_suffix(md_path.suffix + ".picgo.md")
    out_path.write_text(new_content, encoding="utf-8")

    print("\nDone.")
    print(f"Output: {out_path}")
    print(f"Uploaded files: {len(path_to_url)} | Replaced links: {len(link_to_url)}")



def get_mineru_md_subdirs(root_path):
    """
    扫描 root_path 下的所有直接子文件夹，
    若子文件夹中存在且仅需一个 'MinerU_markdown*.md' 文件，
    则返回 (子文件夹绝对路径, 匹配文件绝对路径) 的列表。
    
    假设：每个子文件夹最多只有一个匹配文件。
    
    返回:
        list of tuple: [(subdir_path, file_path), ...]
    """
    if not os.path.isdir(root_path):
        raise ValueError(f"路径 '{root_path}' 不是一个有效的目录。")
    
    result = []
    
    for item in os.listdir(root_path):
        subdir = os.path.join(root_path, item)
        if os.path.isdir(subdir):
            abs_subdir = os.path.abspath(subdir)
            try:
                # 如果同级已有 .picgo.md 文件，则跳过该子文件夹
                if any(
                    fname.endswith(".picgo.md")
                    and os.path.isfile(os.path.join(abs_subdir, fname))
                    for fname in os.listdir(abs_subdir)
                ):
                    continue
                matched_files = []
                for filename in os.listdir(abs_subdir):
                    # 检查是否是文件，并匹配命名规则
                    if (filename.startswith('MinerU_markdown') and 
                        filename.endswith('.md') and
                        os.path.isfile(os.path.join(abs_subdir, filename))):
                        matched_files.append(filename)

                # 如果匹配文件数不为 1，则跳过
                if len(matched_files) != 1:
                    continue

                file_path = os.path.abspath(os.path.join(abs_subdir, matched_files[0]))
                result.append((abs_subdir, file_path))
            except OSError as e:
                print(f"警告：无法访问目录 {abs_subdir} - {e}")
                continue
    
    return result

if __name__ == "__main__":
    target_path = "/Users/nidazhong/MinerU/"  # 可替换为你想扫描的路径
    
    try:
        matches = get_mineru_md_subdirs(target_path)
        
        if matches:
            print("找到以下包含 MinerU_markdown*.md 文件的子文件夹：\n")
            for folder, md_file in matches:
                print(f"📁 子文件夹: {folder}")
                print(f"📄 匹配文件: {md_file}\n")
                replace_img(md_path=Path(md_file), default_base_dir = Path(folder))
        else:
            print("未找到任何包含 MinerU_markdown*.md 文件的子文件夹。")
    except ValueError as e:
        print(f"错误: {e}")
