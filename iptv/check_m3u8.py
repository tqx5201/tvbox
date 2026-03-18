import aiohttp
import asyncio

LIST_URL = "https://tvbox.stncp.dpdns.org/iptv/proxy_m3u8_all.txt"

async def check_m3u8(session, url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        async with session.get(url, headers=headers, timeout=8) as resp:
            if resp.status not in (200, 206):
                return False
            chunk = await resp.text(errors="ignore")
            return "#EXTM3U" in chunk.upper()
    except:
        return False

async def main():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(LIST_URL, timeout=15) as resp:
                text = await resp.text("utf-8", errors="ignore")
                lines = [l.strip() for l in text.splitlines() if l.strip()]
        except Exception as e:
            print("获取列表失败:", e)
            return

    print(f"共 {len(lines)} 条")

    valid = []
    invalid = []

    async with aiohttp.ClientSession() as session:
        tasks = []
        for line in lines:
            if "," not in line:
                invalid.append(line)
                continue
            _, url = line.split(",", 1)
            tasks.append((line, check_m3u8(session, url.strip())))

        results = await asyncio.gather(*[t[1] for t in tasks])

        for (line, _), ok in zip(tasks, results):
            if ok:
                valid.append(line)
                print("✅ 有效 |", line)
            else:
                invalid.append(line)
                print("❌ 无效 |", line)

    with open("proxy_m3u8.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(valid))
    with open("cannotplay.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(invalid))

    print("\n完成！")
    print("有效：", len(valid), "→ valid.txt")
    print("无效：", len(invalid), "→ invalid.txt")

# 通用运行
if __name__ == "__main__":
    asyncio.run(main())
