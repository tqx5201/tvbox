import aiohttp
import asyncio

LIST_FILE = 'proxy_m3u8_all.txt'

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
    try:
        with open(LIST_FILE, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"读取文件失败: {e}")
        return

    print(f"共 {len(lines)} 条，开始异步检测...\n")

    valid_lines = []
    invalid_lines = []

    async with aiohttp.ClientSession() as session:
        tasks = []
        for line in lines:
            if "," not in line:
                invalid_lines.append(line)
                continue
            _, url = line.split(",", 1)
            tasks.append((line, check_m3u8(session, url.strip())))

        results = await asyncio.gather(*[t[1] for t in tasks])

        for (line, _), ok in zip(tasks, results):
            if ok:
                valid_lines.append(line)
                print(f"✅ 有效 | {line}")
            else:
                invalid_lines.append(line)
                print(f"❌ 无效 | {line}")

    # 写入对应文件
    with open("proxy_m3u8.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(valid_lines))

    with open("cannotplay.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(invalid_lines))

    print("\n===== 检测完成 =====")
    print(f"有效：{len(valid_lines)} 条 → proxy_m3u8.txt")
    print(f"无效：{len(invalid_lines)} 条 → cannotplay.txt")

if __name__ == "__main__":
    asyncio.run(main())
