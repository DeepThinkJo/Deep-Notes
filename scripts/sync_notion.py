import os
import re
import json
from pathlib import Path

import requests

# ─────────────────────────────────────────
# 환경 변수에서 Notion API 키, DB ID 불러오기
# ─────────────────────────────────────────
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

NOTION_VERSION = "2022-06-28"
BASE_URL = "https://api.notion.com/v1"

# 출력 Markdown이 들어갈 기본 디렉토리
OUTPUT_DIR = Path("notes")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def ensure_env():
    """환경 변수가 없을 때 친절하게 에러 메시지 출력하고 종료."""
    missing = []
    if not NOTION_API_KEY:
        missing.append("NOTION_API_KEY")
    if not DATABASE_ID:
        missing.append("NOTION_DATABASE_ID")

    if missing:
        print("❌ Missing required environment variables:")
        for name in missing:
            print(f"   - {name}")
        print("GitHub Secrets에 NOTION_API_KEY, NOTION_DATABASE_ID가 설정되어 있는지 확인하세요.")
        raise SystemExit(1)


def slugify(text: str) -> str:
    """
    파일/폴더 이름으로 쓸 수 있게 슬러그화.
    - 소문자 변환
    - 공백 -> '-'
    - 영어/숫자/-/_/. 외의 문자는 제거
    """
    text = (text or "").strip().lower()
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"[^a-z0-9\-_.]", "", text)
    return text or "untitled"


def query_database():
    """Status = 'Published' 인 페이지들을 Notion DB에서 가져오기."""
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

    # 디버깅 및 친절한 에러 출력
    if response.status_code != 200:
        print("⚠ Notion API returned an error when querying database:")
        print("Status code:", response.status_code)
        try:
            print("Response JSON:", json.dumps(response.json(), indent=2))
        except Exception:
            print("Response text:", response.text)
        raise SystemExit(1)

    data = response.json()
    results = data.get("results", [])

    # 페이지네이션 대응 (여러 페이지일 경우)
    while data.get("has_more"):
        body["start_cursor"] = data["next_cursor"]
        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()
        data = response.json()
        results.extend(data.get("results", []))

    return results


def get_page_blocks(page_id: str):
    """페이지의 block 들(본문)을 전부 가져오기 (페이지네이션 포함)."""
    url = f"{BASE_URL}/blocks/{page_id}/children?page_size=100"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": NOTION_VERSION,
    }

    all_blocks = []
    while True:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        all_blocks.extend(data.get("results", []))

        if not data.get("has_more"):
            break

        next_cursor = data.get("next_cursor")
        url = f"{BASE_URL}/blocks/{page_id}/children?page_size=100&start_cursor={next_cursor}"

    return all_blocks


def rich_text_to_plaintext(rich_text_array):
    """Notion rich_text 배열을 일반 문자열로 변환."""
    text = ""
    for part in rich_text_array:
        if "text" in part and part["text"] is not None:
            text += part["text"]["content"]
    return text


def blocks_to_markdown(blocks):
    """Notion block들을 Markdown 문자열로 변환."""
    md_lines = []

    for block in blocks:
        block_type = block.get("type")

        if block_type == "paragraph":
            md_lines.append(rich_text_to_plaintext(block["paragraph"].get("rich_text", [])))
            md_lines.append("")

        elif block_type == "heading_1":
            md_lines.append("# " + rich_text_to_plaintext(block["heading_1"].get("rich_text", [])))
            md_lines.append("")

        elif block_type == "heading_2":
            md_lines.append("## " + rich_text_to_plaintext(block["heading_2"].get("rich_text", [])))
            md_lines.append("")

        elif block_type == "heading_3":
            md_lines.append("### " + rich_text_to_plaintext(block["heading_3"].get("rich_text", [])))
            md_lines.append("")

        elif block_type == "bulleted_list_item":
            md_lines.append("- " + rich_text_to_plaintext(block["bulleted_list_item"].get("rich_text", [])))

        elif block_type == "numbered_list_item":
            md_lines.append("1. " + rich_text_to_plaintext(block["numbered_list_item"].get("rich_text", [])))

        elif block_type == "quote":
            text = rich_text_to_plaintext(block["quote"].get("rich_text", []))
            md_lines.append("> " + text)

        elif block_type == "code":
            language = block["code"].get("language", "")
            code_text = rich_text_to_plaintext(block["code"].get("rich_text", []))
            md_lines.append(f"```{language}")
            md_lines.append(code_text)
            md_lines.append("```")
            md_lines.append("")

        # TODO: 필요하면 다른 block 타입들도 추가 가능 (todo, toggle 등)

    # 마지막에 개행 정리
    return "\n".join(md_lines).strip() + "\n"


def extract_properties(page):
    """Notion page 객체에서 우리가 필요한 정보들을 안전하게 꺼내기."""
    props = page.get("properties", {})

    # Title
    title_prop = props.get("Title", {})
    title_rich = title_prop.get("title", [])
    title = title_rich[0]["plain_text"] if title_rich else "Untitled"

    # Category
    category_prop = props.get("Category", {}).get("select")
    category = category_prop["name"] if category_prop else "Uncategorized"

    # Subcategory
    subcategory_prop = props.get("Subcategory", {}).get("select")
    subcategory = subcategory_prop["name"] if subcategory_prop else None

    # Language (optional, Programming 에서만 의미 있음)
    language_prop = props.get("Language", {}).get("select")
    language = language_prop["name"] if language_prop else None

    # Tags
    tags_prop = props.get("Tags", {}).get("multi_select", [])
    tags = [t.get("name", "") for t in tags_prop] if tags_prop else []

    # Summary
    summary = ""
    if "Summary" in props:
        rich = props["Summary"].get("rich_text", [])
        if rich:
            summary = rich[0].get("plain_text", "")

    # Created (Notion 속성)
    created = None
    if "Created" in props and "created_time" in props["Created"]:
        created = props["Created"]["created_time"]

    # Sync_Path (Formula)
    sync_path = None
    if "Sync_Path" in props and "formula" in props["Sync_Path"]:
        sync_path = props["Sync_Path"]["formula"].get("string")

    # Last edited time (페이지 최종 수정 시간)
    last_edited = page.get("last_edited_time", "")

    return {
        "title": title,
        "category": category,
        "subcategory": subcategory,
        "language": language,
        "tags": tags,
        "summary": summary,
        "created": created,
        "sync_path": sync_path,
        "last_edited": last_edited,
    }



def save_markdown(page, markdown_body: str):
    """한 개의 Notion 페이지를 notes/<Sync_Path> 로 저장."""
    meta = extract_properties(page)

    title = meta["title"]
    category = meta["category"]
    subcategory = meta["subcategory"]
    language = meta["language"]
    tags = meta["tags"]
    last_edited = meta["last_edited"]
    summary = meta["summary"]
    created = meta["created"]
    sync_path = meta["sync_path"]

    # Sync_Path가 Notion에서 정상적으로 계산되지 않은 경우를 대비한 안전장치
    if not sync_path:
        print(f"⚠ Sync_Path is missing for page '{title}'. Falling back to simple path.")
        # 기존 방식으로라도 저장 (최악의 경우)
        category_slug = slugify(category)
        title_slug = slugify(title)
        sync_path = f"{category_slug}/{title_slug}.md"

    # notes/ + Sync_Path
    filepath = OUTPUT_DIR / sync_path

    # 중간 디렉토리들 생성
    filepath.parent.mkdir(parents=True, exist_ok=True)

    # Front matter 구성
    frontmatter = "---\n"
    frontmatter += f'title: "{title}"\n'
    frontmatter += f'category: "{category}"\n'
    if subcategory:
        frontmatter += f'subcategory: "{subcategory}"\n'
    if language:
        frontmatter += f'language: "{language}"\n'
    if created:
        frontmatter += f'created: "{created}"\n'
    frontmatter += f'last_updated: "{last_edited}"\n'
    frontmatter += f"tags: {tags}\n"
    if summary:
        frontmatter += f'summary: "{summary}"\n'
    frontmatter += "---\n\n"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(frontmatter)
        f.write(markdown_body)

    print(f"✅ Saved: {filepath}")



def main():
    ensure_env()
    print("🔍 Fetching Published pages from Notion...")

    pages = query_database()

    if not pages:
        print("ℹ No pages with Status = 'Published' found. Nothing to sync.")
        return

    for page in pages:
        page_id = page.get("id")
        print(f"Processing page: {page_id}")
        blocks = get_page_blocks(page_id)
        markdown_body = blocks_to_markdown(blocks)
        save_markdown(page, markdown_body)

    print("\n✅ Sync completed successfully!")


if __name__ == "__main__":
    main()
