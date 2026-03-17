# Supabase 架構遷移行動指南 (IVC Project Edition)

> **版本**: 1.0.0 | **日期**: 2026-02-07 | **來源**: NotebookLM 知識蒸餾 + Claude Code 實測驗證
>
> 本指南專為 Allen 的 IVCO 專案量身打造。
> 從 Docker PostgreSQL 15 遷移至 Supabase 的完整操作手冊。

---

## 第一章：Region 選擇與 IPv4 連接策略

**TL;DR**: 台灣開發者選 Singapore (ap-northeast-1)。**強制使用 Supavisor Session Pooler** 來解決 IPv6 問題，無需購買 $4/月的 IPv4 Add-on。

### 1.1 背景問題

自 2024 年 1 月 15 日起，Supabase 新專案的 **Direct Connection 預設為 IPv6 Only**。
台灣多數 ISP（中華電信、固網）在家用環境下，macOS 預設無完整 IPv6 路由，
導致 `psql`、`node-postgres`、Payload CMS 全部無法連接。

### 1.2 Region 決策矩陣

| Region | 實測延遲 (台灣) | Pooler IPv4 | 推薦度 | 備註 |
|--------|-----------------|-------------|--------|------|
| Tokyo (ap-northeast-1) | **47ms avg** (46-49ms) | **已驗證** | 首選 | 延遲最低、最穩定 |
| Singapore (ap-southeast-1) | **54ms avg** (47-62ms) | **已驗證** | 備選 | 延遲略高、波動較大 |
| US West (us-west-1) | ~140-180ms (估計) | 支援 | 不推薦 | CMS 後台操作有明顯延遲 |

> **實測日期**: 2026-02-07，台灣家用網路環境。Tokyo 延遲比 Singapore 低 ~7ms 且更穩定。

### 1.3 三種連接方式的差異（重要）

這是最容易搞混的部分。Supabase 提供三種連接方式，**hostname 和 port 都不同**：

| 連接方式 | Hostname | Port | IPv4 | 適用場景 |
|----------|----------|------|------|----------|
| Direct Connection | `db.[ref].supabase.co` | 5432 | **否 (IPv6 only)** | 需 IPv6 網路或 $4/月 add-on |
| Supavisor Session Mode | `aws-0-[region].pooler.supabase.com` | **5432** | **是** | 長連線（Payload CMS、n8n） |
| Supavisor Transaction Mode | `aws-0-[region].pooler.supabase.com` | **6543** | **是** | Serverless（Edge Functions） |

> **關鍵區分**：Direct 和 Session Pooler 都用 Port 5432，但 **hostname 完全不同**。
> Direct 走 `db.xxx.supabase.co`（IPv6），Pooler 走 `aws-0-xxx.pooler.supabase.com`（IPv4）。

### 1.4 IVC 專案的連線策略

```
┌─────────────────────────────────────────────────────────────────────┐
│  Payload CMS (Runtime + Migration)                                  │
│  → Supavisor Session Mode (port 5432, IPv4)                        │
│  → postgresql://postgres.[ref]:[pwd]@aws-0-ap-northeast-1          │
│    .pooler.supabase.com:5432/postgres                              │
├─────────────────────────────────────────────────────────────────────┤
│  n8n (Docker 容器內)                                                │
│  → Supavisor Session Mode (port 5432, IPv4)                        │
│  → 同上格式（Docker 容器預設走 IPv4）                                │
├─────────────────────────────────────────────────────────────────────┤
│  ivco-collect / Python CLI                                          │
│  → Supabase REST API (https://[ref].supabase.co) 或                │
│  → Payload CMS API (http://localhost:3000/api)                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.5 IPv4 驗證步驟（已實測）

```bash
# 1. 驗證 Tokyo Pooler（首選）→ 應回傳 A 記錄（IPv4）
nslookup aws-0-ap-northeast-1.pooler.supabase.com
# 實測結果（2026-02-07）：
#   54.64.190.72
#   52.68.3.1
#   35.79.125.133  ← 全部 IPv4 ✅

# 2. 驗證 Singapore Pooler（備選）
nslookup aws-0-ap-southeast-1.pooler.supabase.com
# 實測結果（2026-02-07）：
#   52.77.146.31
#   52.74.252.201
#   54.255.219.82  ← 全部 IPv4 ✅

# 3. 確認你的網路是否支援 IPv6（通常不支援）
curl -6 https://ifconfig.co/ip 2>&1
# 若超時或報錯 → 你是 IPv4-only 環境，必須用 Pooler

# 4. 開通 Supabase 專案後，驗證 TCP 連通性
nc -zv aws-0-ap-northeast-1.pooler.supabase.com 5432
nc -zv aws-0-ap-northeast-1.pooler.supabase.com 6543
```

> **IVCO 專案適用建議**: 使用 Supavisor Session Mode (Port 5432) 連接 Singapore region。
> 這能省下 $4/月 IPv4 add-on，同時完美支援 Payload CMS 的長連線需求。

---

## 第二章：Supabase CLI 操作手冊

**TL;DR**: CLI 是你的核心工具。將 Supabase CLI 視為遠端資料庫的 "Git"。注意與現有 Docker Compose 的端口隔離。

### 2.1 安裝與初始化

```bash
# macOS 安裝
brew install supabase/tap/supabase

# 驗證安裝
supabase --version

# 登入（會打開瀏覽器授權，Token 存於本機）
supabase login

# 在 IVCO 專案根目錄初始化（會建立 supabase/ 目錄）
cd /Users/allenchenmac/fisher/projects/allen-ivco
supabase init
```

### 2.2 與現有 Docker Compose 共存

你的 `docker-compose.yml` 佔用的 port：
- `5433` → Docker PostgreSQL
- `3000` → Payload CMS
- `5678` → n8n

Supabase CLI `supabase start` 預設佔用：
- `54322` → Supabase 本地 DB
- `54321` → Supabase Studio (Dashboard)
- `54323` → Supabase Auth
- 其他 54xxx 端口（約 10 個容器）

**不會衝突**，但會額外佔用約 1-2GB RAM。M1 Pro 16GB 同時跑兩套會吃緊。

> **建議**: 不要同時啟動。開發時用 Docker Compose（你的舊環境），
> 遷移測試時單獨跑 `supabase start`。

### 2.3 連結遠端專案

```bash
# 取得你的 Project Reference（在 Supabase Dashboard → Settings → General）
supabase link --project-ref [YOUR_PROJECT_REF]

# 拉取遠端 Schema 到本地 migration 檔
supabase db pull

# 查看遠端與本地的 Schema 差異
supabase db diff
```

### 2.4 常用指令速查表

| 任務 | 指令 | 說明 |
|------|------|------|
| 啟動本地環境 | `supabase start` | 啟動全套本地容器 |
| 停止本地環境 | `supabase stop` | 停止並保留數據 |
| 連結遠端專案 | `supabase link --project-ref [ref]` | 綁定 Cloud 專案 |
| 拉取遠端 Schema | `supabase db pull` | 遠端 → 本地 migration |
| 推送 Migration | `supabase db push` | 本地 migration → 遠端 |
| 重置本地 DB | `supabase db reset` | 清空重跑所有 migrations |
| Schema 差異 | `supabase db diff` | 比較本地與遠端差異 |
| 生成 TypeScript 型別 | `supabase gen types typescript` | Next.js 前端用 |
| 查看本地狀態 | `supabase status` | 列出所有服務的 URL 和 Key |

> **IVCO 專案適用建議**: 由於 Payload CMS 管理自己的 Schema（透過 `payload_migrations` 表），
> Supabase CLI 的 migration 系統與 Payload 的 migration 系統是**獨立的**。
> 初期以 Payload 為主，Supabase CLI 作為輔助工具（檢查狀態、備份、type gen）。

---

## 第三章：Database Migration 策略

**TL;DR**: 使用 `pg_dump -Fc` 全庫備份，`pg_restore` 還原至 Supabase。Payload CMS 只要看到完整的 `payload_migrations` 表，就會正常啟動。

### 3.1 遷移前 Checklist

- [ ] 停止所有寫入：暫停 n8n cron jobs、停止 `ivco-collect` 腳本
- [ ] 確認 Payload 版本一致：本地與部署環境的 Payload 版本必須相同
- [ ] 檢查未執行的 Migration：`npm run payload migrate:status`
- [ ] 備份現有 Docker 數據（見下方指令）
- [ ] 確認 Supabase 專案已建立，Region 為 Singapore
- [ ] 已驗證 Pooler IPv4 連通性（nslookup + nc）

### 3.2 備份指令（從 Docker PostgreSQL）

```bash
# 完整備份（Custom format，最穩健）
pg_dump -h localhost -p 5433 -U ivco_user -Fc ivco_dev \
  > /Users/allenchenmac/fisher/memory/backups/ivco_dev_$(date +%F).dump

# 驗證備份檔案大小
ls -lh /Users/allenchenmac/fisher/memory/backups/ivco_dev_*.dump

# 可選：同時產生 SQL 文字備份（方便人工檢視）
pg_dump -h localhost -p 5433 -U ivco_user --no-owner --no-acl ivco_dev \
  > /Users/allenchenmac/fisher/memory/backups/ivco_dev_$(date +%F).sql
```

### 3.3 還原至 Supabase

```bash
# 使用 Supavisor Session Mode (Port 5432, IPv4)
# 注意 username 格式：postgres.[project-ref]
pg_restore \
  -h aws-0-ap-northeast-1.pooler.supabase.com \
  -p 5432 \
  -U postgres.[YOUR_PROJECT_REF] \
  -d postgres \
  --no-owner \
  --no-acl \
  --clean \
  --if-exists \
  /Users/allenchenmac/fisher/memory/backups/ivco_dev_2026-02-07.dump

# 系統會要求輸入 Database Password（建立 Supabase 專案時設定的密碼）
```

**`--no-owner --no-acl` 的作用**：忽略本地 Docker 的 `ivco_user` 權限，
用 Supabase 的 `postgres` 超級用戶接管所有物件。

**`--clean --if-exists` 的作用**：先 DROP 再 CREATE，確保冪等（可重複執行）。

### 3.4 Payload CMS Migration 協調

Payload CMS 啟動時會檢查 `payload_migrations` 表：

| 情境 | Payload 行為 | 結果 |
|------|-------------|------|
| 全庫還原（含 payload_migrations） | 偵測到所有 migration 已執行，正常啟動 | **最佳路徑** |
| 只遷移業務數據 | 嘗試重建表格，報 `Table Already Exists` | 需手動處理 |
| 空資料庫 | 自動執行所有 migration | 只有結構，無數據 |

> **結論**: 永遠採用「全庫還原」策略。`pg_dump -Fc` 會包含 `payload_migrations`。

### 3.5 遷移後驗證

```bash
# 1. 透過 Pooler 連接 Supabase，確認表格存在
psql "postgresql://postgres.[ref]:[pwd]@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres" \
  -c "\dt"

# 2. 確認 payload_migrations 表有記錄
psql "postgresql://postgres.[ref]:[pwd]@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres" \
  -c "SELECT * FROM payload_migrations ORDER BY created_at;"

# 3. 確認業務數據完整
psql "postgresql://postgres.[ref]:[pwd]@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres" \
  -c "SELECT id, name, ticker FROM companies;"

# 4. 切換 Payload CMS 的 DATABASE_URL，啟動測試
DATABASE_URL="postgresql://postgres.[ref]:[pwd]@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres" \
  npm run dev
```

### 3.6 回滾方案

如果遷移失敗，你的 Docker PostgreSQL 完全不受影響：

```bash
# 回到 Docker 環境
docker compose up -d
# 將 cms/.env 的 DATABASE_URL 改回 localhost:5433
# npm run dev — 一切如常
```

> **IVCO 專案適用建議**: 採用全庫遷移，不要手動同步 Schema。
> `pg_dump -Fc` 能完美處理 Foreign Key 約束順序。遷移失敗可一秒回到 Docker。

---

## 第四章：Row Level Security (RLS) 設計模式

**TL;DR**: Payload CMS 使用 `postgres` 超級用戶連接，**自動繞過 RLS**。初期不需要設定 RLS。

### 4.1 RLS 對 Payload CMS 的影響

Payload CMS 的 `@payloadcms/db-postgres` adapter 使用 `postgres` 用戶連接，
這等同於 Supabase 的 `service_role`，**Bypass RLS**。

| 連接來源 | 繞過 RLS？ | 說明 |
|----------|-----------|------|
| Payload CMS (Runtime) | 是 | postgres 超級用戶 |
| Payload CMS (Admin UI) | 是 | 透過 Payload API，走 postgres 連接 |
| Supabase Client (supabase-js) | **否** | 用 anon key，受 RLS 約束 |
| psql 手動連接 | 是 | 用 postgres 用戶 |

### 4.2 IVC 的 RLS 策略

**初期（現在）**: 不啟用 RLS。IVC 是單人系統，所有操作走 Payload CMS API。

**未來（如果前端直接用 supabase-js）**: 啟用 RLS 並設定公開唯讀 Policy：

```sql
-- 啟用 RLS
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE company_events ENABLE ROW LEVEL SECURITY;

-- 公開唯讀 Policy
CREATE POLICY "Public read access" ON companies
  FOR SELECT TO anon USING (true);

CREATE POLICY "Public read access" ON company_events
  FOR SELECT TO anon USING (true);
```

### 4.3 常見陷阱

| 陷阱 | 症狀 | 解法 |
|------|------|------|
| 開了 RLS 但沒寫 Policy | supabase-js 讀到空陣列 | 加 Policy 或關閉 RLS |
| Payload 正常但前端空白 | Payload 繞過 RLS，前端不繞過 | 為 anon role 加 Policy |
| 寫入被拒絕 | RLS 阻擋了 INSERT/UPDATE | 確認 Policy 涵蓋寫入操作 |

> **IVCO 專案適用建議**: 初期對所有 Table **不啟用 RLS**，避免遷移除錯困難。
> 等到需要前端直接拉資料時再鎖緊權限。

---

## 第五章：Connection Pooling 與效能優化

**TL;DR**: Payload CMS 必須用 **Session Mode (port 5432)**。Transaction Mode 可能導致 prepared statement 問題。

### 5.1 Supavisor 連接模式比較

| 特性 | Session Mode (5432) | Transaction Mode (6543) |
|------|--------------------|-----------------------|
| 連線持久性 | 保持到 Client 斷開 | 每個 Query/Transaction 結束後釋放 |
| Prepared Statements | **支援** | **不支援**（可能報錯） |
| 適用場景 | 長連線伺服器（CMS, n8n） | Serverless（Edge Functions） |
| IPv4 支援 | 是 | 是 |
| 連線數限制 (Free) | 200 (共享) | 200 (共享) |

### 5.2 Payload CMS 的 Driver 特性

Payload 3.x 使用 `@payloadcms/db-postgres`，底層是 `pg (node-postgres)` + Drizzle ORM。

**重要發現**: `node-postgres` 的 parameterized queries 使用 **unnamed prepared statements**，
在 Transaction Mode 下**通常不會報錯**。但 Payload 內部使用 transactions（`BEGIN...COMMIT`），
在 Transaction Mode 下可能因為連線重分配而丟失 transaction 狀態。

**結論**: **Session Mode 是唯一安全選擇**。

### 5.3 DATABASE_URL 格式

```bash
# Session Pooler（IVC 推薦）
# 注意 username 格式：postgres.[project-ref]（帶 project reference）
DATABASE_URL=postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres

# Direct Connection（需 IPv6，台灣環境不可用）
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres

# Transaction Pooler（不建議 Payload 使用）
DATABASE_URL=postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-ap-northeast-1.pooler.supabase.com:6543/postgres
```

### 5.4 Payload CMS config 設定

你目前的 `cms/src/payload.config.ts` 已經正確，無需修改：

```typescript
db: postgresAdapter({
  pool: {
    connectionString: process.env.DATABASE_URL || '',
  },
}),
```

只需切換 `.env` 中的 `DATABASE_URL` 即可。

### 5.5 連接數限制

| Compute Tier | 方案 | Direct Connections | Pooler Connections |
|---|---|---|---|
| Nano | Free | 60 | 200 |
| Micro | Pro ($25/月) | 60 | 200 |
| Small | Pro + $15/月 | 90 | 400 |

IVC 專案只有 Payload CMS + n8n + 偶爾的 psql 手動連接，
200 個 Pooler 連線數遠遠足夠。

> **IVCO 專案適用建議**: 使用 Session Pooler (port 5432)。
> Payload config 不需要改，只切換 DATABASE_URL 環境變數。

---

## 第六章：Supabase Auth 與 Edge Functions

**TL;DR**: 不用 Supabase Auth。不用 Edge Functions。繼續用 Payload CMS 內建的 Auth 和 n8n。

### 6.1 Auth 決策

| 功能 | Payload Auth | Supabase Auth |
|------|-------------|---------------|
| 認證方式 | HTTP Cookies | JWT |
| User 儲存 | `users` collection | `auth.users` 系統表 |
| 整合度 | 原生整合 CMS | 需額外接線 |
| 適用場景 | CMS 後台管理 | SaaS 多租戶前端 |

**決策**: IVC 是單人後台估值系統，Payload Auth 足夠。
混用兩套 Auth 需要維護 User ID 映射，增加不必要的複雜度（違反 Principle VII: YAGNI）。

### 6.2 Edge Functions 決策

| 功能 | n8n (現有) | Edge Functions |
|------|-----------|---------------|
| 觸發方式 | Cron / Webhook | HTTP Request |
| 語言 | 視覺化 + JavaScript | TypeScript (Deno) |
| 已有設定 | Docker 容器已運行 | 需重新建立 |
| 適用場景 | 複雜工作流 | 簡單 API 端點 |

**決策**: 繼續用 n8n + Python CLI。不需要為了 Edge Functions 重寫 `ivco-collect`。

> **IVCO 專案適用建議**: 將 Supabase 純粹作為 **PostgreSQL 雲端資料庫**使用。
> Auth、Storage、Edge Functions 全部忽略，保持架構簡單。

---

## 第七章：備份、監控與成本控制

**TL;DR**: Free Plan 有 500MB DB + **7 天自動暫停**。生產環境建議 Pro Plan ($25/月)。

### 7.1 Free Plan 的致命限制：自動暫停

> **重要**: Supabase Free Plan 在 **7 天無活動後自動暫停資料庫**。
> 暫停後需要手動從 Dashboard 恢復，恢復需要數分鐘。

**對 IVCO 的影響**：
- 你的 cron job（每日 3 次 X 情報收集）如果連續 7 天全部失敗（例如 Bird CLI cookie 過期），
  Supabase DB 會被暫停，導致 Payload CMS 也無法啟動。
- **Free Plan 不適合生產環境**。

### 7.2 成本估算

| 方案 | 月費 | 適用階段 |
|------|------|----------|
| Free Plan | $0 | 初期測試（有 7 天暫停風險） |
| Pro Plan | $25 | 生產環境（無暫停、8GB DB、每日備份） |
| Pro + IPv4 Add-on | $29 | 如果需要 Direct Connection（但 Pooler 已足夠） |

IVCO 專案的數據量估算：
- Companies: ~10 筆 → 極小
- CompanyEvents: 每日 ~18 筆（3 次 × 2 關鍵字 × 3 筆）→ 年 ~6,500 筆 → ~10MB
- Financial_Data: 未來 → 每公司 ~100 筆年度數據 → 極小
- **500MB Free Plan 初期完全足夠**，但自動暫停是問題。

### 7.3 自製備份方案（CLI-First）

```bash
# 加入你的 crontab（每日凌晨 3:00 備份）
0 3 * * * /usr/local/bin/python3 -c "print('backup')" && \
  pg_dump "postgresql://postgres.[ref]:[pwd]@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres" \
  | gzip > /Users/allenchenmac/fisher/memory/backups/supabase_$(date +\%F).sql.gz
```

保留最近 7 天備份的清理腳本：

```bash
# 刪除 7 天前的備份
find /Users/allenchenmac/fisher/memory/backups/ \
  -name "supabase_*.sql.gz" -mtime +7 -delete
```

### 7.4 Free Plan 防暫停策略

如果你決定先用 Free Plan 測試，可以設定 keep-alive cron：

```bash
# 每 5 天 ping 一次資料庫，防止自動暫停
0 9 */5 * * psql "postgresql://postgres.[ref]:[pwd]@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres" \
  -c "SELECT 1;" >> /Users/allenchenmac/fisher/memory/daily/supabase-keepalive.log 2>&1
```

但這是 workaround，不是長久之計。生產環境請升級 Pro Plan。

> **IVCO 專案適用建議**: 初期測試用 Free Plan + keep-alive cron。
> 確認遷移成功後升級 Pro Plan ($25/月)，消除暫停風險。

---

## 第八章：安全最佳實踐

**TL;DR**: 保護好 Database Password 和 service_role key。AI Agent 不能直接讀取 `.env`。

### 8.1 API Key 分類

| Key | 安全等級 | 用途 | 可公開？ |
|-----|---------|------|---------|
| `anon` key | 低風險 | 前端 supabase-js | 可以（受 RLS 保護） |
| `service_role` key | **最高機密** | 繞過 RLS 的後端操作 | **絕對不可** |
| Database Password | **最高機密** | psql / Payload 連接 | **絕對不可** |

### 8.2 環境變數隔離（Agent-Safe）

```
allen-ivco/
├── cms/.env                 # 本地開發（Docker PG）— gitignored
├── cms/.env.production      # Supabase 生產 — gitignored
├── cms/.env.example         # 只有 key 名稱，無值 — 可 commit
├── .env.docker              # Docker Compose 用 — gitignored
└── .gitignore               # 確保排除所有 .env* (除 .example)
```

### 8.3 .env.example 更新

遷移至 Supabase 後，更新 `.env.example`：

```bash
# Development (Docker PostgreSQL)
DATABASE_URL=postgresql://ivco_user:ivco_password@db:5432/ivco_dev

# Production (Supabase Session Pooler)
# DATABASE_URL=postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres

PAYLOAD_SECRET=YOUR_SECRET_HERE
```

### 8.4 Agent-Safe Security Checklist

- [ ] `.env` 檔案不在 git 歷史中（已用 `git-filter-repo` 清除過）
- [ ] Openclaw `exec.ask: always` + `security: allowlist`
- [ ] AI Agent 不能直接讀取含密碼的 `.env`（只讀 `.env.example`）
- [ ] Supabase Dashboard 密碼不存在任何純文字檔案中
- [ ] `service_role` key 只用於伺服器端，永不暴露至前端

> **IVCO 專案適用建議**: 遵循現有的 Constitution Principle VI (Agent-Safe Security)。
> 新增 Supabase 相關的 secrets 到同一套管理流程。

---

## 第九章：實戰 Checklist — 從零到部署

### Phase 1: 基礎建設

- [ ] 安裝 Supabase CLI: `brew install supabase/tap/supabase`
- [ ] 註冊/登入 Supabase: `supabase login`
- [ ] 建立新專案，選擇 **Tokyo (ap-northeast-1)** region（實測延遲最低）
- [ ] **記下 Database Password**（只顯示一次！）
- [ ] 在 Dashboard → Settings → Database，複製 Session Pooler Connection String
- [ ] 驗證 IPv4: `nslookup aws-0-ap-northeast-1.pooler.supabase.com`
- [ ] 驗證 TCP: `nc -zv aws-0-ap-northeast-1.pooler.supabase.com 5432`
- [ ] 連結本地專案: `supabase link --project-ref [ref]`

### Phase 2: 遷移數據

- [ ] 停止 n8n cron jobs 和 `ivco-collect` 腳本
- [ ] `pg_dump -h localhost -p 5433 -U ivco_user -Fc ivco_dev > ivco_dev.dump`
- [ ] `pg_restore` 到 Supabase（見第三章指令）
- [ ] 用 `psql` 確認 `companies` 和 `payload_migrations` 表都有數據
- [ ] 在 Supabase Dashboard 確認資料（視覺確認）

### Phase 3: 應用程式切換

- [ ] 建立 `cms/.env.production`，寫入 Supabase Session Pooler URL
- [ ] 本地測試: `DATABASE_URL="..." npm run dev`
- [ ] 開啟 CMS 後台 (localhost:3000/admin)，測試 CRUD
- [ ] 修改 n8n Postgres Node，指向 Supabase Session Pooler
- [ ] 重啟 `ivco-collect` cron（如果 ivco-collect 直接寫 DB 而非走 Payload API）
- [ ] 全功能回歸測試

### Phase 4: 驗證與上線

- [ ] 監控 Payload CMS 日誌 24 小時，確認無 Connection Timeout
- [ ] 確認 `ivco-collect` Python 腳本能正常寫入
- [ ] 設定每日備份 cron（見第七章）
- [ ] 決定是否升級 Pro Plan
- [ ] 更新 `CLAUDE.md` 和 `constitution.md` 的 Technology Constraints
- [ ] 更新 `project-mac-system-config.json` 記錄 Supabase 部署資訊

---

## 常見錯誤與排錯

| 錯誤訊息 | 原因 | 解法 |
|----------|------|------|
| `connection to server ... is unreachable` | IPv6 Direct Connection，台灣網路不支援 | 改用 `.pooler.supabase.com` hostname |
| `prepared statement "s1" already exists` | Transaction Mode 下 prepared statement 衝突 | 改用 Session Mode (port 5432) |
| `password authentication failed` | 密碼錯誤或 username 格式不對 | Pooler 的 username 是 `postgres.[ref]`，不是 `postgres` |
| `relation "xxx" does not exist` | Migration 未執行或還原不完整 | 確認 `payload_migrations` 表存在且有記錄 |
| `too many connections` | 超過 Pooler 連線數限制 | Free/Micro 限 200，檢查是否有連線洩漏 |
| `FATAL: Project is paused` | Free Plan 7 天自動暫停 | 到 Dashboard 手動恢復，或升級 Pro Plan |
| `could not translate host name` | DNS 解析失敗 | 確認 hostname 拼寫正確，測試 `nslookup` |

---

## 附錄：環境變數快速參考

```bash
# ===== 開發環境 (Docker PostgreSQL) =====
DATABASE_URL=postgresql://ivco_user:ivco_password@localhost:5433/ivco_dev

# ===== 開發環境 (Docker Compose 容器內) =====
DATABASE_URL=postgresql://ivco_user:ivco_password@db:5432/ivco_dev

# ===== 生產環境 (Supabase Session Pooler) =====
DATABASE_URL=postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres

# ===== 備份用 (Supabase Session Pooler, 同上) =====
BACKUP_DATABASE_URL=postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres
```

---

## 版本歷史

| 版本 | 日期 | 變更 |
|------|------|------|
| 1.0.0 | 2026-02-07 | 初版：NotebookLM 蒸餾 + Claude Code 實測驗證 + 7 項修正補完 |
