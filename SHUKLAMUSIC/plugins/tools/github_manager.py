# -----------------------------------------------
# 🔸 StrangerMusic Project — GitHub Management
# 🔹 Convert public repos to ZIP, push ZIPs to a repo, and manage repos
# 🔹 Uses the GitHub REST API only (no third-party GitHub library)
# -----------------------------------------------
import os
import io
import base64
import shutil
import zipfile
import aiohttp
from pyrogram import filters
from pyrogram.types import Message
from SHUKLAMUSIC import app
from SHUKLAMUSIC.core.mongo import mongodb
from config import BANNED_USERS, BOT_USERNAME

gh_tokens_db = mongodb.github_tokens

GITHUB_API = "https://api.github.com"

_E_OK = 5208748315805499400     # ✅ AttractivePack
_E_CAL = 5188168541920065191    # 🗓 Monochrome_Black_Style
_E_ERR = 5978715546865112655    # 🚩 ll_MR_DEVIL_KING
_E_GIFT = 5190811712038661224   # 🎁 Monochrome_Black_Style


def e(eid, fb):
    return f"<emoji id={eid}>{fb}</emoji>"


async def get_token(user_id: int):
    doc = await gh_tokens_db.find_one({"user_id": user_id})
    return doc["token"] if doc else None


async def save_token(user_id: int, token: str):
    await gh_tokens_db.update_one({"user_id": user_id}, {"$set": {"token": token}}, upsert=True)


async def remove_token(user_id: int):
    await gh_tokens_db.delete_one({"user_id": user_id})


def parse_repo(text: str):
    text = text.strip()
    if text.startswith("http"):
        text = text.rstrip("/")
        text = text.split("github.com/")[-1]
    parts = [p for p in text.split("/") if p]
    if len(parts) >= 2:
        return parts[0], parts[1]
    return None, None


GH_HELP = f"""
{e(_E_CAL,'🗓')} <b>GitHub Management — Command List</b>

<b>Setup (do this in DM, keep your token private)</b>
• <code>/setghtoken &lt;token&gt;</code> — save your GitHub personal access token
• <code>/mytoken</code> — check if a token is saved
• <code>/removetoken</code> — remove your saved token

<b>Repo → ZIP</b>
• <code>/repo2zip &lt;owner/repo or url&gt; [branch]</code> — download any public repo as a ZIP file

<b>Push ZIP → Repo</b>
• Reply to a .zip file with <code>/pushzip &lt;owner/repo&gt; [branch]</code> — extracts the zip and pushes every file to your repo (needs a saved token with repo scope)

<b>Manage Repos</b>
• <code>/myrepos</code> — list your repositories
• <code>/creategh &lt;name&gt; [private|public]</code> — create a new repository
• <code>/ghinfo &lt;owner/repo&gt;</code> — get repo info
• <code>/ghfiles &lt;owner/repo&gt; [path]</code> — list files/folders in a repo path
• <code>/ghfilecontent &lt;owner/repo&gt; &lt;path&gt;</code> — preview a file's content directly from a repo
• <code>/delghfile &lt;owner/repo&gt; &lt;path&gt;</code> — delete a single file from a repo
• <code>/delgh &lt;owner/repo&gt;</code> — permanently delete a repository (irreversible)
"""


def _auth_headers(token: str = None):
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


@app.on_message(filters.command("ghhelp") & ~BANNED_USERS)
async def gh_help_cmd(client, message: Message):
    await message.reply_text(GH_HELP, disable_web_page_preview=True)


@app.on_message(filters.command("setghtoken") & ~BANNED_USERS)
async def set_gh_token(client, message: Message):
    # Hard-reject in group chats — token must never be exposed in group history
    if message.chat.id != message.from_user.id:
        return await message.reply_text(
            f"{e(_E_ERR,'🚩')} <b>ᴅᴍ ᴏɴʟʏ ᴄᴏᴍᴍᴀɴᴅ!</b>\n\n"
            f"ᴜsɪɴɢ /setghtoken ɪɴ ᴀ ɢʀᴏᴜᴘ ᴄᴏᴜʟᴅ ᴇxᴩᴏsᴇ ʏᴏᴜʀ ɢɪᴛʜᴜʙ ᴛᴏᴋᴇɴ.\n\n"
            f"👉 <a href='https://t.me/{BOT_USERNAME}?start=setghtoken'>ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ᴏᴘᴇɴ ᴅᴍ →</a>",
            disable_web_page_preview=True,
        )
    if len(message.command) != 2:
        return await message.reply_text(f"{e(_E_ERR,'🚩')} Usage: <code>/setghtoken &lt;your_github_token&gt;</code>")
    token = message.command[1].strip()
    try:
        await message.delete()
    except Exception:
        pass
    mystic = await message.reply_text(f"{e(_E_CAL,'🗓')} Verifying your token with GitHub...")
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{GITHUB_API}/user", headers=_auth_headers(token)) as resp:
            if resp.status != 200:
                return await mystic.edit_text(f"{e(_E_ERR,'🚩')} Invalid token — GitHub rejected it. Make sure you copied the full token correctly.")
            data = await resp.json()
    await save_token(message.from_user.id, token)
    await mystic.edit_text(f"{e(_E_OK,'✅')} Token saved for GitHub account <b>{data.get('login')}</b>.\n<i>Your message with the token has been deleted for safety.</i>")


@app.on_message(filters.command("mytoken") & ~BANNED_USERS)
async def my_token_cmd(client, message: Message):
    token = await get_token(message.from_user.id)
    if token:
        await message.reply_text(f"{e(_E_OK,'✅')} You have a GitHub token saved.")
    else:
        await message.reply_text(f"{e(_E_ERR,'🚩')} No token saved. Use <code>/setghtoken</code> in DM.")


@app.on_message(filters.command("removetoken") & ~BANNED_USERS)
async def remove_token_cmd(client, message: Message):
    await remove_token(message.from_user.id)
    await message.reply_text(f"{e(_E_OK,'✅')} Token removed.")


@app.on_message(filters.command("repo2zip") & ~BANNED_USERS)
async def repo2zip_cmd(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(f"{e(_E_ERR,'🚩')} Usage: <code>/repo2zip owner/repo [branch]</code>")
    owner, repo = parse_repo(message.command[1])
    if not owner or not repo:
        return await message.reply_text(f"{e(_E_ERR,'🚩')} Could not parse the repo. Use <code>owner/repo</code> or a GitHub URL.")
    branch = message.command[2] if len(message.command) > 2 else None
    mystic = await message.reply_text(f"{e(_E_CAL,'🗓')} Fetching repo info...")

    token = await get_token(message.from_user.id)
    async with aiohttp.ClientSession() as session:
        if not branch:
            async with session.get(f"{GITHUB_API}/repos/{owner}/{repo}", headers=_auth_headers(token)) as resp:
                if resp.status != 200:
                    return await mystic.edit_text(f"{e(_E_ERR,'🚩')} Repo not found or private (need a token for private repos).")
                info = await resp.json()
                branch = info.get("default_branch", "main")

        await mystic.edit_text(f"{e(_E_CAL,'🗓')} Downloading <b>{owner}/{repo}</b> ({branch}) as ZIP...")
        zip_url = f"https://codeload.github.com/{owner}/{repo}/zip/refs/heads/{branch}"
        async with session.get(zip_url, headers=_auth_headers(token)) as resp:
            if resp.status != 200:
                return await mystic.edit_text(f"{e(_E_ERR,'🚩')} Failed to download ZIP (branch may not exist).")
            content = await resp.read()

    zip_path = f"downloads/{owner}_{repo}_{branch}.zip"
    os.makedirs("downloads", exist_ok=True)
    with open(zip_path, "wb") as f:
        f.write(content)

    await mystic.delete()
    await message.reply_document(
        zip_path,
        caption=f"{e(_E_OK,'✅')} <b>{owner}/{repo}</b> ({branch}) converted to ZIP.",
    )
    try:
        os.remove(zip_path)
    except Exception:
        pass


@app.on_message(filters.command("pushzip") & filters.reply & ~BANNED_USERS)
async def pushzip_cmd(client, message: Message):
    replied = message.reply_to_message
    if not replied or not replied.document or not replied.document.file_name.lower().endswith(".zip"):
        return await message.reply_text(f"{e(_E_ERR,'🚩')} Reply to a .zip file with this command.")
    if len(message.command) < 2:
        return await message.reply_text(f"{e(_E_ERR,'🚩')} Usage: reply to a zip with <code>/pushzip owner/repo [branch]</code>")

    owner, repo = parse_repo(message.command[1])
    if not owner or not repo:
        return await message.reply_text(f"{e(_E_ERR,'🚩')} Could not parse the repo.")
    branch = message.command[2] if len(message.command) > 2 else "main"

    token = await get_token(message.from_user.id)
    if not token:
        return await message.reply_text(f"{e(_E_ERR,'🚩')} Save a GitHub token first with <code>/setghtoken</code> in DM.")

    mystic = await message.reply_text(f"{e(_E_CAL,'🗓')} Downloading your ZIP...")
    zip_path = f"downloads/push_{message.id}.zip"
    os.makedirs("downloads", exist_ok=True)
    extract_dir = f"downloads/push_{message.id}_extracted"
    try:
        await replied.download(zip_path)
        os.makedirs(extract_dir, exist_ok=True)
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(extract_dir)

        files_to_push = []
        for root, _, files in os.walk(extract_dir):
            for fn in files:
                full_path = os.path.join(root, fn)
                rel_path = os.path.relpath(full_path, extract_dir)
                files_to_push.append((full_path, rel_path))

        if not files_to_push:
            return await mystic.edit_text(f"{e(_E_ERR,'🚩')} The ZIP file is empty.")

        await mystic.edit_text(f"{e(_E_CAL,'🗓')} Pushing {len(files_to_push)} files to <b>{owner}/{repo}</b> ({branch})...")

        pushed, failed = 0, 0
        async with aiohttp.ClientSession() as session:
            for full_path, rel_path in files_to_push:
                rel_path_url = rel_path.replace(os.sep, "/")
                try:
                    with open(full_path, "rb") as f:
                        content_b64 = base64.b64encode(f.read()).decode()

                    sha = None
                    async with session.get(
                        f"{GITHUB_API}/repos/{owner}/{repo}/contents/{rel_path_url}",
                        headers=_auth_headers(token),
                        params={"ref": branch},
                    ) as resp:
                        if resp.status == 200:
                            existing = await resp.json()
                            sha = existing.get("sha")

                    payload = {
                        "message": f"Push {rel_path_url} via SHUKLAMUSIC GitHub Management",
                        "content": content_b64,
                        "branch": branch,
                    }
                    if sha:
                        payload["sha"] = sha

                    async with session.put(
                        f"{GITHUB_API}/repos/{owner}/{repo}/contents/{rel_path_url}",
                        headers=_auth_headers(token),
                        json=payload,
                    ) as resp:
                        if resp.status in (200, 201):
                            pushed += 1
                        else:
                            failed += 1
                except Exception:
                    failed += 1

        await mystic.edit_text(
            f"{e(_E_OK,'✅')} Push complete for <b>{owner}/{repo}</b> ({branch})\n"
            f"• Pushed: <b>{pushed}</b>\n• Failed: <b>{failed}</b>"
        )
    finally:
        for p in (zip_path,):
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass
        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir, ignore_errors=True)


@app.on_message(filters.command("myrepos") & ~BANNED_USERS)
async def my_repos_cmd(client, message: Message):
    token = await get_token(message.from_user.id)
    if not token:
        return await message.reply_text(f"{e(_E_ERR,'🚩')} Save a GitHub token first with <code>/setghtoken</code> in DM.")
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{GITHUB_API}/user/repos", headers=_auth_headers(token), params={"per_page": 20, "sort": "updated"}) as resp:
            if resp.status != 200:
                return await message.reply_text(f"{e(_E_ERR,'🚩')} Failed to fetch repos.")
            repos = await resp.json()
    if not repos:
        return await message.reply_text("You have no repositories yet.")
    text = f"{e(_E_CAL,'🗓')} <b>Your Repositories:</b>\n\n"
    for r in repos:
        vis = "🔒 Private" if r.get("private") else "🌐 Public"
        text += f"• <a href='{r['html_url']}'>{r['full_name']}</a> ({vis})\n"
    await message.reply_text(text, disable_web_page_preview=True)


@app.on_message(filters.command("creategh") & ~BANNED_USERS)
async def create_gh_cmd(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(f"{e(_E_ERR,'🚩')} Usage: <code>/creategh name [private|public]</code>")
    token = await get_token(message.from_user.id)
    if not token:
        return await message.reply_text(f"{e(_E_ERR,'🚩')} Save a GitHub token first with <code>/setghtoken</code> in DM.")
    name = message.command[1]
    private = len(message.command) > 2 and message.command[2].lower() == "private"
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{GITHUB_API}/user/repos",
            headers=_auth_headers(token),
            json={"name": name, "private": private},
        ) as resp:
            data = await resp.json()
            if resp.status not in (200, 201):
                return await message.reply_text(f"{e(_E_ERR,'🚩')} Failed: {data.get('message', 'unknown error')}")
    await message.reply_text(f"{e(_E_GIFT,'🎁')} Repository created: <a href='{data['html_url']}'>{data['full_name']}</a>", disable_web_page_preview=True)


@app.on_message(filters.command("ghinfo") & ~BANNED_USERS)
async def gh_info_cmd(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(f"{e(_E_ERR,'🚩')} Usage: <code>/ghinfo owner/repo</code>")
    owner, repo = parse_repo(message.command[1])
    if not owner or not repo:
        return await message.reply_text(f"{e(_E_ERR,'🚩')} Could not parse the repo.")
    token = await get_token(message.from_user.id)
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{GITHUB_API}/repos/{owner}/{repo}", headers=_auth_headers(token)) as resp:
            if resp.status != 200:
                return await message.reply_text(f"{e(_E_ERR,'🚩')} Repo not found.")
            r = await resp.json()
    text = (
        f"{e(_E_CAL,'🗓')} <b>{r['full_name']}</b>\n\n"
        f"⭐ Stars: {r.get('stargazers_count', 0)}\n"
        f"🍴 Forks: {r.get('forks_count', 0)}\n"
        f"📝 Language: {r.get('language') or 'N/A'}\n"
        f"🌿 Default branch: {r.get('default_branch')}\n"
        f"🔗 <a href='{r['html_url']}'>Open on GitHub</a>"
    )
    await message.reply_text(text, disable_web_page_preview=True)


@app.on_message(filters.command("ghfiles") & ~BANNED_USERS)
async def gh_files_cmd(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(f"{e(_E_ERR,'🚩')} Usage: <code>/ghfiles owner/repo [path]</code>")
    owner, repo = parse_repo(message.command[1])
    if not owner or not repo:
        return await message.reply_text(f"{e(_E_ERR,'🚩')} Could not parse the repo.")
    path = message.command[2] if len(message.command) > 2 else ""
    token = await get_token(message.from_user.id)
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{GITHUB_API}/repos/{owner}/{repo}/contents/{path}", headers=_auth_headers(token)) as resp:
            if resp.status != 200:
                return await message.reply_text(f"{e(_E_ERR,'🚩')} Path not found.")
            items = await resp.json()
    if isinstance(items, dict):
        return await message.reply_text(f"{e(_E_OK,'✅')} That path is a file, not a folder.")
    text = f"{e(_E_CAL,'🗓')} <b>{owner}/{repo}/{path}</b>\n\n"
    for item in items:
        icon = "📁" if item["type"] == "dir" else "📄"
        text += f"{icon} {item['name']}\n"
    await message.reply_text(text or "Empty folder.")


@app.on_message(filters.command("ghfilecontent") & ~BANNED_USERS)
async def gh_file_content_cmd(client, message: Message):
    if len(message.command) < 3:
        return await message.reply_text(f"{e(_E_ERR,'🚩')} Usage: <code>/ghfilecontent owner/repo path/to/file</code>")
    owner, repo = parse_repo(message.command[1])
    if not owner or not repo:
        return await message.reply_text(f"{e(_E_ERR,'🚩')} Could not parse the repo.")
    path = message.command[2]
    token = await get_token(message.from_user.id)
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{GITHUB_API}/repos/{owner}/{repo}/contents/{path}",
            headers=_auth_headers(token),
        ) as resp:
            if resp.status != 200:
                return await message.reply_text(f"{e(_E_ERR,'🚩')} File not found.")
            data = await resp.json()

    if isinstance(data, list):
        return await message.reply_text(f"{e(_E_ERR,'🚩')} That path is a folder, not a file. Use <code>/ghfiles</code> instead.")
    if data.get("encoding") != "base64":
        return await message.reply_text(f"{e(_E_ERR,'🚩')} Cannot preview this file's content.")

    try:
        raw = base64.b64decode(data["content"]).decode("utf-8", errors="replace")
    except Exception:
        return await message.reply_text(f"{e(_E_ERR,'🚩')} File appears to be binary and can't be previewed as text.")

    size = data.get("size", 0)
    if size > 3500 or len(raw) > 3500:
        preview = raw[:3500]
        text = (
            f"{e(_E_CAL,'🗓')} <b>{owner}/{repo}/{path}</b> ({size} bytes, truncated)\n\n"
            f"<pre>{preview}</pre>"
        )
    else:
        text = f"{e(_E_CAL,'🗓')} <b>{owner}/{repo}/{path}</b> ({size} bytes)\n\n<pre>{raw}</pre>"

    try:
        await message.reply_text(text)
    except Exception:
        file_path = f"downloads/preview_{message.id}.txt"
        os.makedirs("downloads", exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(raw)
        await message.reply_document(file_path, caption=f"{e(_E_OK,'✅')} <b>{owner}/{repo}/{path}</b>")
        os.remove(file_path)


@app.on_message(filters.command("delghfile") & ~BANNED_USERS)
async def del_gh_file_cmd(client, message: Message):
    if len(message.command) < 3:
        return await message.reply_text(f"{e(_E_ERR,'🚩')} Usage: <code>/delghfile owner/repo path/to/file</code>")
    owner, repo = parse_repo(message.command[1])
    path = message.command[2]
    token = await get_token(message.from_user.id)
    if not token:
        return await message.reply_text(f"{e(_E_ERR,'🚩')} Save a GitHub token first with <code>/setghtoken</code> in DM.")
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{GITHUB_API}/repos/{owner}/{repo}/contents/{path}", headers=_auth_headers(token)) as resp:
            if resp.status != 200:
                return await message.reply_text(f"{e(_E_ERR,'🚩')} File not found.")
            data = await resp.json()
        async with session.delete(
            f"{GITHUB_API}/repos/{owner}/{repo}/contents/{path}",
            headers=_auth_headers(token),
            json={"message": f"Delete {path} via SHUKLAMUSIC", "sha": data["sha"]},
        ) as resp:
            if resp.status not in (200, 201):
                return await message.reply_text(f"{e(_E_ERR,'🚩')} Failed to delete file.")
    await message.reply_text(f"{e(_E_OK,'✅')} Deleted <code>{path}</code> from <b>{owner}/{repo}</b>.")


@app.on_message(filters.command("delgh") & ~BANNED_USERS)
async def delete_repo_cmd(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(f"{e(_E_ERR,'🚩')} Usage: <code>/delgh owner/repo</code>")
    owner, repo = parse_repo(message.command[1])
    token = await get_token(message.from_user.id)
    if not token:
        return await message.reply_text(f"{e(_E_ERR,'🚩')} Save a GitHub token first with <code>/setghtoken</code> in DM.")
    async with aiohttp.ClientSession() as session:
        async with session.delete(f"{GITHUB_API}/repos/{owner}/{repo}", headers=_auth_headers(token)) as resp:
            if resp.status != 204:
                return await message.reply_text(f"{e(_E_ERR,'🚩')} Failed to delete (check token has 'delete_repo' scope).")
    await message.reply_text(f"{e(_E_OK,'✅')} Repository <b>{owner}/{repo}</b> deleted.")
