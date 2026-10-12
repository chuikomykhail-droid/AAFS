# Логи роботи з ШІ (AI Work Logs)
Ця папка містить повні вивантаження сесій роботи з ШІ-асистентом **Antigravity** (Google DeepMind) у форматі Markdown для перевірки та рефлексії.

## 📑 Зміст

### 1. Основний діалог
- [**Основний діалог парного програмування**](main_dialogue.md) — повний контекст планування, обговорення рішень, аналізу бектесту, перевірки гіпотез, дебагу та бутстрепу.

### 2. Логи 7 паралельних агентів незалежного аудиту (Stage Reviews)
Для перевірки етапів проекту було запущено 7 автономних агентів на моделі `gemini-3.1-pro`. Їхні транскрипти зафіксовані в окремих файлах:

| Етап / Роль агента | Файл логу | Conversation ID |
|---|---|---|
| **Stage 0-1b Reviewer** | [subagent_stage0-1b.md](subagent_stage0-1b.md) | `b332d638-ef75-4d4c-bf37-6eadf5c8e77b` |
| **Stage 2 Reviewer** | [subagent_stage2.md](subagent_stage2.md) | `cee41021-7e92-4b46-90f0-42105516e562` |
| **Stage 3 Reviewer** | [subagent_stage3.md](subagent_stage3.md) | `6552c240-9157-4af3-a10e-742ddbd58963` |
| **Stages 4-6 Reviewer** | [subagent_stage4-6.md](subagent_stage4-6.md) | `45125e28-3c4a-4c78-8284-4279186495fb` |
| **Stage 5 Leakage Reviewer** | [subagent_stage5-leakage.md](subagent_stage5-leakage.md) | `67c1f704-96d1-43c1-9521-32cdcd68c96f` |
| **Stage 7 Reviewer** | [subagent_stage7.md](subagent_stage7.md) | `62308d1b-a9a4-41c2-ae56-9318291ff1d1` |
| **Stage 8 Reviewer** | [subagent_stage8.md](subagent_stage8.md) | `282406ef-ba69-4110-b3bb-66d4dd03b171` |


### 3. Сирі JSONL-файли (Raw Transcripts)
Для машинного аналізу або верифікації всі первинні логи доступні у підпапці [`ai_logs/raw/`](raw/):
- `main_dialogue_full.jsonl` та `main_dialogue.jsonl`
- `subagent_stage*_full.jsonl` та `subagent_stage*.jsonl` для кожного з 7 агентів.

---
*Згенеровано автоматично для відповідності критеріям здачі курсу (PLAN.md).*