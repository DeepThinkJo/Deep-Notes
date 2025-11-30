import os
import re
import json
from pathlib import Path
import requests

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

NOTION_VERSION = "2022-06-28"
BASE_URL = "https://api.notion.com/v1"

OUTPUT_DIR = Path("notes")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def ensure_env():
    if not NOTION_API_KEY or not DATABASE_ID:
        raise SystemExit("Missing NOTION_API_KEY or NOTION_DATABASE_ID.")


def rich_text_to_plaintext(rich_text_array):
    return "".join([t["text"]["content"] for t in rich_text_array if "text" in t])


def query_database():
    url = f"{BASE_URL}/databases/{DATABASE_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }

    body = {
        "filter": {
            "property": "Status",
            "select": {"equals": "Completed"},
        }
    }

    response = requests.post(url, headers=headers, json=body)
    response.raise_for_status()

    data = response.json()
    results = data.get("results", [])

    while data.get("has_more"):
        body["start_cursor"] = data["next_cursor"]
        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()
        data = response.json()
        results.extend(data.get("results", []))

    return results


def get_page_blocks(page_id: str):
    url = f"{BASE_URL}/blocks/{page_id}/children?page_size=100"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": NOTION_VERSION,
    }

    blocks = []
    while True:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        blocks.extend(data.get("results", []))

        if not data.get("has_more"):
            break

        next_cursor = data.get("next_cursor")
        url = f"{BASE_URL}/blocks/{page_id}/children?page_size=100&start_cursor={next_cursor}"

    return blocks


def blocks_to_markdown(blocks):
    md = []

    for block in blocks:
        t = block.get("type")

        if t == "paragraph":
            md.append(rich_text_to_plaintext(block[t]["rich_text"]) + "\n")

        elif t == "heading_1":
            md.append("# " + rich_text_to_plaintext(block[t]["rich_text"]) + "\n")

        elif t == "heading_2":
            md.append("## " + rich_text_to_plaintext(block[t]["rich_text"]) + "\n")

        elif t == "heading_3":
            md.append("### " + rich_text_to_plaintext(block[t]["rich_text"]) + "\n")

        elif t == "bulleted_list_item":
            md.append("- " + rich_text_to_plaintext(block[t]["rich_text"]))

        elif t == "numbered_list_item":
            md.append("1. " + rich_text_to_plaintext(block[t]["rich_text"]))

        elif t == "quote":
            md.append("> " + rich_text_to_plaintext(block[t]["rich_text"]))

        elif t == "code":
            lang = block["code"].get("language", "")
            code_text = rich_text_to_plaintext(block["code"]["rich_text"])
            md.append(f"```{lang}\n{code_text}\n```")

    return "\n".join(md).strip() + "\n"


def convert_math(md_text: str) -> str:
    """
    Convert math syntax for MkDocs + MathJax:
    - Protect fenced code blocks ```...```
    - Convert block math: $$ ... $$  ->  \\[ ... \\]
    - Convert inline math: $ ... $   ->  \\( ... \\)
    """

    # 1) 코드 블록 보호
    code_block_pattern = r"```.*?```"
    code_blocks = list(re.finditer(code_block_pattern, md_text, flags=re.DOTALL))

    placeholders = []
    temp_text = md_text

    for i, m in enumerate(code_blocks):
        original = m.group(0)
        placeholder = f"__CODE_BLOCK_{i}__"
        placeholders.append((placeholder, original))
        temp_text = temp_text.replace(original, placeholder, 1)

    # 2) 블록 수식 변환: $$ ... $$  ->  \[ ... \]
    block_math_pattern = r"\$\$(.+?)\$\$"
    temp_text = re.sub(
        block_math_pattern,
        r"\\[\1\\]",
        temp_text,
        flags=re.DOTALL,
    )

    # 3) 인라인 수식 변환: $ ... $  ->  \( ... \)
    #    $$는 이미 처리되었으므로 단일 $만 남아 있음
    inline_math_pattern = r"(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)"
    temp_text = re.sub(inline_math_pattern, r"\\(\1\\)", temp_text)

    # 4) 코드 블록 복원
    for placeholder, original in placeholders:
        temp_text = temp_text.replace(placeholder, original)

    return temp_text


def extract_properties(page):
    props = page.get("properties", {})

    def s(prop, key):
        return props.get(prop, {}).get(key)

    def text(prop):
        rich = props.get(prop, {}).get("rich_text", [])
        return rich[0]["plain_text"] if rich else ""

    title = props.get("Title", {}).get("title", [])
    title = title[0]["plain_text"] if title else "Untitled"

    category = s("Category", "select")
    category = category["name"] if category else None

    subcategory = s("Subcategory", "select")
    subcategory = subcategory["name"] if subcategory else None

    language = s("Language", "select")
    language = language["name"] if language else None

    tags = props.get("Tags", {}).get("multi_select", [])
    tags = [t["name"] for t in tags] if tags else []

    created = props.get("Created", {}).get("created_time")

    sync_path = props.get("Sync_Path", {}).get("formula", {}).get("string")

    summary = text("Summary")
    last_edited = page.get("last_edited_time", "")

    return {
        "title": title,
        "category": category,
        "subcategory": subcategory,
        "language": language,
        "tags": tags,
        "created": created,
        "sync_path": sync_path,
        "summary": summary,
        "last_edited": last_edited,
    }


def save_markdown(page, markdown_body: str):
    meta = extract_properties(page)
    sync_path = meta["sync_path"]

    if not sync_path:
        raise ValueError(f"Sync_Path is missing for page '{meta['title']}'")

    filepath = OUTPUT_DIR / sync_path
    filepath.parent.mkdir(parents=True, exist_ok=True)

    fm = ["---"]
    fm.append(f'title: "{meta["title"]}"')
    fm.append(f'category: "{meta["category"]}"')
    if meta["subcategory"]:
        fm.append(f'subcategory: "{meta["subcategory"]}"')
    if meta["language"]:
        fm.append(f'language: "{meta["language"]}"')
    if meta["created"]:
        fm.append(f'created: "{meta["created"]}"')
    fm.append(f'last_updated: "{meta["last_edited"]}"')
    fm.append(f"tags: {meta['tags']}")
    if meta["summary"]:
        fm.append(f'summary: "{meta["summary"]}"')
    fm.append("---\n")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(fm))
        f.write(markdown_body)

    print(f"Saved: {filepath}")


def main():
    ensure_env()
    pages = query_database()

    if not pages:
        print("No pages with Status = 'Completed'.")
        return

    for page in pages:
        blocks = get_page_blocks(page["id"])
        markdown_body = blocks_to_markdown(blocks)
        # 🔥 수식 변환: 코드 블록 보호 + 블록/인라인 수식 변환
        markdown_body = convert_math(markdown_body)
        save_markdown(page, markdown_body)

    print("Sync completed.")


if __name__ == "__main__":
    main()
