<!-- PROFILE:START -->
<p align="center">
  <img src="assets/header.svg?v=417cff65" alt="GitHub profile header" width="100%">
</p>

<p align="center">
  <img src="assets/stats.svg?v=7c53fe43" alt="GitHub stats" width="49%">
  <img src="assets/streak.svg?v=404eb147" alt="Contribution streak" width="49%">
</p>

<p align="center">
  <img src="assets/languages.svg?v=993b85df" alt="Top languages" width="49%">
  <img src="assets/repos.svg?v=15d9506e" alt="Repositories and stars" width="49%">
</p>

<p align="center">
  <img src="assets/contributions.svg?v=08979914" alt="Contribution graph" width="100%">
</p>

<p align="center">
  <img src="assets/activity.svg?v=222a3878" alt="Commit activity" width="100%">
</p>

<p align="center">
  <img src="assets/skills.svg?v=13b47c50" alt="Technology skills" width="100%">
</p>

<p align="center">
  <a href="https://github.com/soullessness1611?tab=repositories"><img src="assets/projects.svg?v=d05de26b" alt="Latest projects" width="100%"></a>
</p>

<p align="center">
  <img src="assets/waka-overview.svg?v=99faab60" alt="WakaTime coding time" width="100%">
</p>

<p align="center">
  <img src="assets/waka-ai.svg?v=7660c8cf" alt="AI coding" width="100%">
</p>

<p align="center">
  <img src="assets/waka-projects.svg?v=3419da42" alt="WakaTime projects" width="49%">
  <img src="assets/waka-tools.svg?v=596aa44d" alt="Editors and tools" width="49%">
</p>

<p align="center">
  <img src="assets/waka-rhythm.svg?v=56441ffb" alt="Coding rhythm" width="100%">
</p>
<!-- PROFILE:END -->

---

<details>
<summary><b>⚙️ วิธีทำงานและวิธีตั้งค่า (GitHub Profile Cards)</b></summary>

## มันคืออะไร

การ์ดทั้งหมดด้านบนเป็นไฟล์ SVG ที่สร้างเองด้วย Python (ใช้แค่ standard library ไม่มี dependency)
ดึงข้อมูลจาก GitHub GraphQL API และ WakaTime API แล้วเขียนไฟล์ลง `assets/`
GitHub Actions รันทุก 6 ชั่วโมงแล้ว commit การ์ดใหม่กลับเข้า repo เอง พร้อมแก้ส่วนรูปใน README
(ระหว่าง `<!-- PROFILE:START -->` กับ `<!-- PROFILE:END -->`) ให้ตรงกับ style ที่เลือก

### เลือก style

ตั้ง `"style"` ใน `config.json` แล้ว workflow จะสร้างรูปและแก้ README ให้เอง

| style | แบบ | หน้าตา |
|---|---|---|
| `zen-sumi` (ค่าเริ่มต้น) | การ์ด 14 ใบ | พื้นหมึกดำ ตัวอักษรสีงาช้าง ทอง/ชาด ตราประทับ 禅 |
| `zen-washi` | การ์ด 14 ใบ | กระดาษวาชิ หมึกดำ ตราประทับแดง |
| `cyberpunk` | การ์ด 14 ใบ | นีออน glitch เรืองแสง |
| `terminal` | การ์ด 14 ใบ | จอ CRT เขียว phosphor |
| `minimal` | การ์ด 14 ใบ | เรียบแบบหน้า GitHub |
| `garden` | ภาพเดียว (สว่าง/มืด) | สวนหินทราย contribution เป็นหินและวงคลื่น |
| `bento` | ภาพเดียว (สว่าง/มืด) | ช่อง ๆ แบบเบนโตะ ข้อมูลครบในภาพเดียว |
| `receipt` | ภาพเดียว | ใบเสร็จ บาร์โค้ดจาก contribution 84 วัน |
| `seigaiha` | ภาพเดียว (สว่าง/มืด) | ลายคลื่นญี่ปุ่น คลื่นหนึ่งลูกคือหนึ่งวัน |
| `constellation` | ภาพเดียว (มืด) | ท้องฟ้ากลางคืน วันที่ commit เป็นดาว |
| `sansui` | ภาพเดียว (สว่าง/มืด) | ภูเขาหมึก สันเขาวาดจาก contribution |

แบบภาพเดียวที่มีทั้งสว่างและมืดใช้ `<picture>` ให้ GitHub สลับตามธีมของผู้ชมเอง

### การ์ด (สำหรับ style แบบการ์ด)

| การ์ด | ไฟล์ | ข้อมูลที่แสดง |
|---|---|---|
| Header | `header.svg` | ชื่อ, tagline, ปีที่เริ่มใช้ GitHub |
| GitHub Stats | `stats.svg` | ดาว, commit ปีนี้/ทั้งหมด, PR, issue, repo ที่ร่วม contribute, followers |
| Streak | `streak.svg` | streak ปัจจุบัน, streak ยาวที่สุด, contribution ทั้งหมด |
| Top Languages | `languages.svg` | ภาษาที่ใช้มากสุดตามขนาดโค้ดใน repo ของตัวเอง |
| Repositories & Stars | `repos.svg` | จำนวน repo, ดาว, fork และ repo ดาวสูงสุด |
| Contribution Graph | `contributions.svg` | ตาราง contribution 1 ปีล่าสุด |
| Commit Activity | `activity.svg` | ช่วงเวลาที่ commit (ตาม `timezone`), วันในสัปดาห์, 12 เดือนล่าสุด |
| Technology Skills | `skills.svg` | รายการจาก `skills` ใน `config.json` |
| Latest Projects | `projects.svg` | repo ที่ push ล่าสุด (ไม่รวม archived) |
| WakaTime | `waka-overview.svg` | เวลาเขียนโค้ด 7 วัน, วันนี้, เฉลี่ยต่อวัน, วันที่มากสุด, ภาษา (ไม่ตั้ง token จะขึ้น LINK OFFLINE · API ตอบ error จะขึ้น LINK ERROR พร้อมเหตุผล) |
| AI Coding | `waka-ai.svg` | % AI-driven, AI/human lines, tokens, ค่าใช้จ่าย AI, sessions, prompts, model |
| Projects | `waka-projects.svg` | เวลาต่อโปรเจกต์ (แสดงแค่ชื่อ ไม่มีลิงก์) |
| Tools | `waka-tools.svg` | editor, OS, AI model, category, จำนวนเครื่อง (ไม่แสดงชื่อเครื่อง) |
| Rhythm | `waka-rhythm.svg` | AI/human lines รายวัน และชั่วโมงตามวันในสัปดาห์ (ต้องมี scope `read_summaries`) |

## ตั้งค่าให้ใช้งาน

1. วางไฟล์ทั้งหมดใน repo ชื่อเดียวกับ username (`soullessness1611/soullessness1611`) เพื่อให้ README ขึ้นหน้าโปรไฟล์
2. แก้ `config.json` ตามต้องการ:

   | key | ความหมาย |
   |---|---|
   | `username` | GitHub username ที่จะดึงข้อมูล |
   | `style` | หน้าตาของโปรไฟล์ (ดูตารางเลือก style ด้านบน) |
   | `display_name`, `tagline` | ข้อความบน header |
   | `timezone` | โซนเวลาสำหรับกราฟ commit activity (เช่น `Asia/Bangkok`) |
   | `include_private_repos` | `true` = นับ repo private ด้วย (ต้องใช้ `GH_PAT`) |
   | `exclude_repos`, `exclude_languages` | repo / ภาษาที่ไม่ต้องนับ |
   | `top_languages_count`, `latest_projects_count` | จำนวนรายการบนการ์ด |
   | `commit_activity_repo_limit` | จำนวน repo ที่ใช้สุ่มเวลา commit |
   | `skills` | หมวด → รายการ skill บนการ์ด Technology Skills |

3. ตั้ง secret ใน **Settings → Secrets and variables → Actions** (ไม่บังคับ):
   - `GH_PAT` — classic token scope `read:user` (+ `repo` ถ้าอยากนับ private) ไม่ตั้งก็ได้ จะใช้ `GITHUB_TOKEN` ของ workflow ซึ่งเห็นแค่ข้อมูล public
   - `WAKATIME_TOKEN` — OAuth token ของ WakaTime (scope `read_stats` และ `read_summaries`)
     ใช้ API key ไม่ได้แล้ว เพราะ WakaTime ให้ API key ใช้ได้เฉพาะ plugin และจะตอบ HTTP 403 ถ้าเอามาอ่านสถิติ วิธีขอ token มีดังนี้
     1. สร้าง app ที่ <https://wakatime.com/apps> แล้วตั้ง Authorized Redirect URI เป็น `https://localhost`
     2. รัน `python3 scripts/wakatime_token.py | gh secret set WAKATIME_TOKEN -R soullessness1611/soullessness1611`
        ใส่ App ID / App Secret แล้วเปิดลิงก์ที่สคริปต์แสดง กด Authorize
        หน้าที่เบราว์เซอร์พาไปจะโหลดไม่ขึ้น ไม่เป็นไร คัดลอก URL ของหน้านั้นมาวาง
        token จะถูกตั้งเป็น secret โดยไม่แสดงบนจอ และใช้ได้ 100 ปี
4. ไปที่แท็บ **Actions → Update profile cards → Run workflow** เพื่อสร้างการ์ดครั้งแรก

## รันบนเครื่อง (Python 3.10+)

```bash
# ดูหน้าตาการ์ดด้วยข้อมูลตัวอย่าง ไม่ต้องใช้ token (ไม่แตะ README)
python -m generator --demo --out /tmp/cards
python -m generator --demo --style sansui --out /tmp/cards

# ใช้ข้อมูลจริง
GH_TOKEN=$(gh auth token) WAKATIME_TOKEN=waka_tok_xxx python -m generator

# รันเทสต์
python -m unittest discover -s tests -t .
```

ตัวเลือก: `--out <dir>` (ค่าเริ่มต้น `assets`), `--config <file>` (ค่าเริ่มต้น `config.json`)

## โครงสร้างไฟล์

```
generator/
  __main__.py    จุดเริ่ม: อ่าน config → ดึงข้อมูล → เขียน SVG → แก้ README
  github_api.py  GraphQL client + query โปรไฟล์ / contribution รายปี / เวลา commit
  wakatime.py    ดึงสถิติ 7 วันจาก WakaTime
  stats.py       คำนวณ streak, ภาษา, activity (pure functions)
  cards.py       การ์ด GitHub 9 ใบ
  waka_cards.py  การ์ด WakaTime 5 ใบ
  layouts.py     style แบบภาพเดียว 6 แบบ
  readme.py      เขียนส่วนรูปใน README ตาม style
  theme.py       style แบบการ์ด 5 แบบ: สี, ฟอนต์, กรอบ, animation
  demo.py        ข้อมูลตัวอย่างสำหรับ --demo
scripts/wakatime_token.py  ขอ WakaTime OAuth token สำหรับ secret WAKATIME_TOKEN
tests/           unittest ของ stats, การ์ด และ WakaTime
assets/          SVG ที่สร้างแล้ว (workflow เขียนทับ)
.github/workflows/update-stats.yml
.github/scripts/commit-assets.sh  commit รูป + README แล้ว push (rebase ก่อนถ้า main ขยับ)
```

</details>
