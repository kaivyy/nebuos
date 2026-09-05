#!/usr/bin/env python3
"""
Comprehensive Audit Data Collector for NebuOS Documentation.
Scans and cross-references all 111 markdown documents.
"""

import os, glob, re, json

docs_dir = "/root/NebuOS/docs"
all_md = sorted(glob.glob(f"{docs_dir}/**/*.md", recursive=True) + glob.glob(f"{docs_dir}/*.md"))
all_md = sorted(list(set(all_md)))

print(f"Total markdown files: {len(all_md)}")

inventory = []

for f in all_md:
    rel_path = os.path.relpath(f, "/root/NebuOS")
    fname = os.path.basename(f)
    parent_dir = os.path.basename(os.path.dirname(f))
    domain = parent_dir if parent_dir != "docs" else "root"
    
    with open(f, "r", encoding="utf-8", errors="ignore") as fp:
        content = fp.read()
        lines = content.splitlines()
        line_count = len(lines)
        word_count = len(content.split())
    
    # Title
    title = fname
    status = "UNSPECIFIED"
    for l in lines[:15]:
        if l.strip().startswith("# "):
            title = l.strip()[2:].strip()
        if "**Status:**" in l or "Status:" in l:
            m = re.search(r"Status:\*?\*?\s*`?([A-Z_]+)`?", l)
            if m:
                status = m.group(1)

    # Links
    links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content)
    outbound = []
    dirpath = os.path.dirname(f)
    for text, link in links:
        if link.startswith("http") or link.startswith("#") or link.startswith("mailto:"):
            continue
        clean_link = link.split("#")[0]
        if not clean_link:
            continue
        target_path = os.path.normpath(os.path.join(dirpath, clean_link))
        outbound.append(os.path.relpath(target_path, "/root/NebuOS"))

    inventory.append({
        "path": rel_path,
        "name": fname,
        "domain": domain,
        "title": title,
        "lines": line_count,
        "words": word_count,
        "status": status,
        "outbound_links": outbound
    })

# Inbound link computation
inbound_map = {}
for item in inventory:
    for out in item["outbound_links"]:
        inbound_map.setdefault(out, []).append(item["path"])

for item in inventory:
    item["inbound_links"] = inbound_map.get(item["path"], [])

print(f"Processed {len(inventory)} documents.")

# Save temporary analysis JSON
with open("/root/NebuOS/build_docs/audit_data.json", "w") as fp:
    json.dump(inventory, fp, indent=2)

print("Saved /root/NebuOS/build_docs/audit_data.json")
