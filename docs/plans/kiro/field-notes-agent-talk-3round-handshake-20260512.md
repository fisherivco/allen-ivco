---
title: Field Notes — agent-talk-3round 首次 Handshake 實戰（ivco, 2026-05-12）
status: COMPLETE
version: 2026-05-12.1
date: 2026-05-12
owner: macmini kiro-cli Kiro
canonical_path: projects/ivco/docs/plans/kiro/field-notes-agent-talk-3round-handshake-20260512.md
mirror: obsidian/projects/ivco/handoffs/kiro/field-notes-agent-talk-3round-handshake-20260512.md
project: ivco
session: S263
thread_id: at3-20260512-kiro-agent-talk-handshake-chi-kiro
---

# Field Notes — agent-talk-3round 首次 Handshake 實戰

在 `projects/ivco/` 資料夾下，Chi（Codex CLI）與 Kiro（Kiro CLI）完成了
`agent-talk-3round` 協定的首次跨 runtime handshake。本文記錄實際執行過程、
關鍵決策、以及可複用的操作心得。

---

## 背景

| 項目 | 值 |
|---|---|
| 日期 | 2026-05-12 |
| 工作目錄 | `/Users/fisherivco/fisher/projects/ivco/` |
| Thread ID | `at3-20260512-kiro-agent-talk-handshake-chi-kiro` |
| 協定版本 | `abuild-btest-v0.2` |
| Chi 角色 | builder / initiator |
| Kiro 角色 | reviewer / receiver |
| 結果 | `KIRO_AGENT_TALK_HANDSHAKE_COMPLETE` |

---

## 執行時序

### 21:27:29 — Chi 發送 Round 0 Handshake

Chi 從 `projects/ivco/` 確認自身 `agent-talk-3round` skill 可用後，
將 Round 0 `task` packet 寫入 Kiro 的 JSONL inbox：

```
/Users/fisherivco/fisher/shared-state/inbox/transport/kiro.jsonl
```

Packet 關鍵欄位：
- `message_id`: `chi-1778592449126`
- `type`: `task`
- `roles`: `{ builder: "chi", reviewer: "kiro" }`
- `max_rounds`: 1，`early_stop_allowed`: true
- `expected_next.agent`: `kiro`

Round 0 不計入 `max_rounds` 上限（free-of-cap）。

### 21:27:29 — Chi 透過 cmux 喚醒 Kiro

Chi 使用 `cmux tree --all` 確認 cmux 拓撲，讀取候選 surface 的畫面內容，
以 **evidence-based** 方式選定 Kiro 的 surface：

- workspace: `workspace:2`
- surface: `surface:5`
- 確認畫面顯示 Kiro CLI UX，cwd `~/fisher/projects/ivco`

喚醒指令（wake plane，僅一行 pointer）：

```bash
cmux send "agent-talk-notice thread_id=at3-20260512-kiro-agent-talk-handshake-chi-kiro ..."
cmux send-key Enter
```

**關鍵原則**：cmux 只傳 notice-only 單行 pointer，不攜帶任何 payload 內容。
Protocol authority 在 JSONL transport，不在 cmux。

### 21:28:13 — Kiro 讀取 Packet 並回覆

Kiro 收到 cmux notice 後，從 `kiro.jsonl` 讀取 Round 0 packet，
驗證 4 項 checks：

1. **cwd**: `/Users/fisherivco/fisher/projects/ivco` ✓
2. **skill**: `~/.kiro/skills/agent-talk-3round/SKILL.md` 可載入 ✓
3. **cmux notice**: 已收到，正確視為 wake plane only ✓
4. **reply channel**: 寫入 `chi.jsonl` 同一 `thread_id` ✓

Kiro 將 `status: pass` packet 寫入 Chi 的 inbox：

```
/Users/fisherivco/fisher/shared-state/inbox/transport/chi.jsonl
message_id: kiro-1778592493004
```

### 21:29:01 — Chi 發送 Close Packet

Chi 收到 Kiro 的 pass 回覆後，發送 close packet：

```
message_id: chi-1778592541406
status: close
overall_verdict: KIRO_AGENT_TALK_HANDSHAKE_COMPLETE
```

Thread 正式關閉。總計 1 個 review round（max_rounds=1），early close 成功。

---

## 兩平面架構實戰驗證

本次 handshake 驗證了 agent-talk-3round 的雙平面設計：

| 平面 | 機制 | 本次使用 |
|---|---|---|
| Payload plane | `shared-state/inbox/transport/*.jsonl` append | Round 0 task + Kiro reply + Chi close |
| Wake plane | `cmux send <one-line>` + `cmux send-key Enter` | 喚醒 Kiro，僅傳 thread_id 和 inbox path |

**Single Writer Principle** 嚴格執行：Kiro 只寫 `chi.jsonl`，絕不寫 `kiro.jsonl`。

---

## 操作心得

### cmux 拓撲確認不可省略

Chi 在發送前先執行 `cmux tree --all` 並讀取候選 surface 畫面，
確認 Kiro CLI 的 cwd 是 `projects/ivco` 才發送。
**不能假設 surface 位置**，必須以 evidence 選定。

### cmux Single-Line Pointer Rule（v1.7.1）

`cmux send` 的參數必須是一行純文字 pointer，不能包含換行或 payload 內容。
若需要傳遞豐富內容，先寫入 JSONL 或 governed file，再用 `pointer_file=<path>` 指向它。

### Round 0 不計入 max_rounds

Handshake round（Round 0）是 free-of-cap。本次 `max_rounds=1` 表示
最多 1 個 review cycle，而非包含 Round 0 在內共 1 輪。

### Early Close 是理想結果

協定鼓勵在 Round 1 就 `pass` 並 early close，不是失敗，而是效率最高的路徑。
本次 1 round 完成即為理想結果。

### top-level thread_id 與 body.thread_id 必須一致

v0.2 要求 packet 的 top-level `thread_id` 欄位與 `body.thread_id` 完全相同。
任何不一致都應 reject 並記錄。

### Kiro 不需要 bash wrapper

Kiro CLI 有原生 shell tool，可直接用 Python 寫 JSONL packet，
不需要 Show/Chi 側的 bash wrapper script。

---

## 可複用的 Kiro 端操作流程

```
1. 收到 cmux notice → 從 kiro.jsonl 讀取對應 thread_id 的 packet
2. 發 RECV-ACK chat template（讓 Allen 可在兩個 chat box 觀察 liveness）
3. 驗證 roles（role-lock：Round 0 設定的 roles 不可在後續 packet 中更改）
4. 執行 checks / audit
5. 用 Python write_packet() 寫 status packet 到 peer inbox
6. 發 SENT-NOTICE chat template
7. 收到 close packet → 發 B-FINAL chat template，thread 結束
```

---

## 證據索引

| 項目 | 值 |
|---|---|
| Chi R0 packet | `chi-1778592449126` in `kiro.jsonl` |
| Kiro reply | `kiro-1778592493004` in `chi.jsonl` |
| Chi close | `chi-1778592541406` in `kiro.jsonl` |
| Chi skill check | `STRUCTURE_OK` from `projects/ivco/` |
| Kiro skill path | `~/.kiro/skills/agent-talk-3round/SKILL.md` |
| Kiro cwd | `/Users/fisherivco/fisher/projects/ivco` |
| cmux target | `workspace:2 surface:5` |

---

## 相關文件

- `tasks/kiro-agent-talk-handshake-20260512-goal.md` — 任務目標與 success criteria
- `tasks/kiro-agent-talk-handshake-20260512-checklist.md` — 執行 checklist
- `~/.kiro/skills/agent-talk-3round/SKILL.md` — Kiro 端協定 skill
- `shared-state/inbox/PROTOCOL-v1.md` — Transport 協定權威文件
