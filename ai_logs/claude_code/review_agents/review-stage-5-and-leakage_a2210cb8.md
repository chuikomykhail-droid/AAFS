# Субагент: Review stage 5 and leakage

- **Агент:** `a2210cb84c207f584` (general-purpose), запущен из сессии [57049ae5](../2026-10-11_critical-analysis_57049ae5.md#t-GrbY31RcsUMc)
- **Период (UTC):** 2026-10-11 17:19 → 2026-10-12 05:53
- **Период (Киев):** 2026-10-11 20:19 → 2026-10-12 08:53
- **Сообщений:** 1 (задания и сообщения основного агента — 1, ответы субагента — 0); вызовов инструментов — 85
- **Исходный JSONL:** `ai_logs/claude_code/raw/claude_code_raw.zip → subagents/57049ae5_agent-a2210cb84c207f584.jsonl`

> Служебные вставки (`<system-reminder>`, вложения с окружением и контекстом IDE, мета-сообщения — 98 записей) и блоки рассуждений (thinking — 57) сюда не включены: они есть в исходном JSONL. Время — киевское. Вызовы инструментов свёрнуты; аргументы обрезаны до 2000 символов, результаты — до 3000. Токен alerts.in.ua и email автора заменены на `[REDACTED_TOKEN]` / `[REDACTED_EMAIL]`.

---

<a id="m-d14f4dbf"></a>

### 📨 Задание от основного агента · 2026-10-11 20:19

Рабочая папка проекта: d:\Flash\golova\KSE_AI\AAFS (Windows; доступны Bash (Git Bash) и PowerShell).

Прочитай файл `reviews/prompts/05_stage5-leakage.md` целиком и выполни задание из него в точности, включая все ограничения: не изменять файлы проекта, не запускать `scripts/run_all.py`, `scripts/api_check.py`, скрипты скачивания и `save_all`, не трогать git, не открывать токен. Параллельно с тобой в той же папке работают шесть других агентов-ревьюеров — пиши только в `reviews/stage5-leakage.md` и `reviews/scratch/stage5-leakage/`.

Когда отчёт записан, верни в ответе: резюме отчёта (5–10 строк) и список находок уровня «критично» и «существенно» — по одной строке на находку (id, суть, файл:строка, уровень проверки).

<details><summary>🔧 Read: reviews/prompts/05_stage5-leakage.md · 20:19</summary>

**Аргументы**

```json
{
 "file_path": "d:\\Flash\\golova\\KSE_AI\\AAFS\\reviews\\prompts\\05_stage5-leakage.md"
}
```

**Результат**

```
1	# Ревью проекта AAFS: этап 5 и защита от утечки
2	
3	Ты — независимый критический ревьюер. Параллельно с тобой другие агенты проверяют другие этапы того же проекта. Твоя зона — этап 5 и защита от утечки: признаки, соседство по границам районов, проверки «порча будущего» и «знание на момент среза». На соседние этапы смотри только тогда, когда без этого не понять твой.
4	
5	## Проект
6	
7	- Репозиторий — текущая папка (`AAFS`), ветка `stages-7-8`. Python-проект: прогноз воздушных тревог в Украине по районам. Для каждой единицы (район; Киев — одна единица), где в момент `t` (каждый час) тихо, модель выдаёт вероятность того, что тревога начнётся в `(t, t+h]`, h = 1, 3, 6 (основной — 3).
8	- Данные — снимок датасета Vadimkin (`dataset_repo/`, коммит `58ee75b`). Официальный ряд заканчивается 2026-09-07. Тест — 2026-08-10…2026-09-07, walk-forward с ежесуточным переобучением. Этап 8 — проверка на данных alerts.in.ua за сентябрь–октябрь.
9	- Это тестовое задание с дедлайном 12.10.2026 23:59 по Киеву. Проверяющие оценивают процесс: пойманные ошибки, обоснованность решений, отсутствие утечки из будущего. Найденная проблема ценна, даже если её не успеют исправить: тогда она уйдёт в раздел ограничений.
10	- Документы: `PLAN.md` (правила работы 1–13; у каждого этапа «Исходное задание» и «Как сделано»), `DECISIONS.md` (решения D00–D22, справочные цифры, журнал пойманных ошибок ИИ), `README.md` (на украинском), отчёты в `reports/`.
11	
12	Сначала прочитай раздел «Правила работы» в `PLAN.md`, описание своего этапа в `PLAN.md` и разделы `DECISIONS.md`: D06, D15, D16, D18 (проверка утечки), D19, D21; README, раздел «Захист від витоку». Код и тесты своей зоны читай целиком, а не выборочно.
13	
14	## Твоя зона: файлы
15	
16	- `src/alerts/features.py`, `src/alerts/geo.py`.
17	- `src/alerts/history.py` — интерфейс, который видят признаки.
18	- `src/alerts/leakage.py`; `src/alerts/pipeline.py`: `model_data`, `alert_history`.
19	- Тесты: `tests/test_features.py`, `tests/test_leakage.py`, `tests/test_knowledge.py`.
20	- Результаты: `data/neighbors.csv`, `reports/leakage_check.json`.
21	- Источник границ: `dataset_repo/example/ukr_admin2.geojson`.
22	
23	## Что проверить
24	
25	1. **Независимый пересчёт признаков.**
26	   - Возьми ~300 случайных строк сетки и пересчитай каждый признак напрямую из исходных записей: `select_scope` плюс правила `open_until` и 24 ч, без `AlertHistory`. Сравни.
27	   - Особое внимание: границы окон; `oblast_active_share` (своя единица исключается); `oblasts_active` (24 области вместе с Киевом и Донецкой); соседи; календарь в киевском времени (попадают ли в сетку переходы на летнее и зимнее время?).
28	2. **Правила перерыва канала (D19).** `lookback_ok`, масштабирование `starts_7d`, `since_obs`: корректны ли они и как меняют распределение признаков после 02.09?
29	3. **Соседство (`geo.py`).**
30	   - Соседи определяются по общим вершинам после округления до 1e-5°. Нет ли ложных пар (касание в точке, совпадение вершин у несоседей)? Нет ли пропу
… [обрезано: показано 3000 из 9190 символов]
```

</details>

<details><summary>🔧 Bash: List project files and sizes · 20:19</summary>

**Аргументы**

```bash
ls && ls reviews reviews/scratch 2>/dev/null && wc -l PLAN.md DECISIONS.md README.md src/alerts/*.py tests/*.py && git log --oneline | head -3
```

**Результат** (ошибка)

```
Exit code 2
DECISIONS.md
PLAN.md
README.md
alerts_api
archive
config.yaml
data
dataset_repo
pyproject.toml
reports
requirements.txt
reviews
scripts
src
tests
reviews:
prompts
```

</details>

<details><summary>🔧 Bash: Show file sizes and data listing · 20:19</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; wc -l PLAN.md DECISIONS.md README.md src/alerts/*.py tests/*.py; ls reviews/prompts; ls data reports
```

**Результат**

```
424 PLAN.md
   704 DECISIONS.md
   147 README.md
     0 src/alerts/__init__.py
   193 src/alerts/api_check.py
    66 src/alerts/backtest.py
    51 src/alerts/config.py
   144 src/alerts/evaluation.py
   115 src/alerts/features.py
   257 src/alerts/figures.py
    74 src/alerts/geo.py
   156 src/alerts/grid.py
   123 src/alerts/history.py
    89 src/alerts/intervals.py
   107 src/alerts/leakage.py
   117 src/alerts/mask.py
    87 src/alerts/metrics.py
    93 src/alerts/pipeline.py
    42 src/alerts/processor.py
   192 src/alerts/report.py
    72 src/alerts/scope.py
    73 src/alerts/spans.py
    49 src/alerts/store.py
    21 src/alerts/timeutil.py
    57 src/alerts/tuning.py
   115 src/alerts/units.py
    56 tests/conftest.py
    62 tests/test_features.py
    99 tests/test_grid.py
   104 tests/test_history.py
   100 tests/test_intervals.py
    33 tests/test_knowledge.py
    46 tests/test_leakage.py
    19 tests/test_load.py
    78 tests/test_mask.py
    31 tests/test_metrics.py
    24 tests/test_units.py
  4220 total
01_stages0-1b.md
02_stage2.md
03_stage3.md
04_stages4-6.md
05_stage5-leakage.md
06_stage7.md
07_stage8.md
08_synthesis.md
data:
alerts_in_ua_locations.csv
grid.parquet
intervals.csv
mask.csv
neighbors.csv
predictions_h1.parquet
predictions_h3.parquet
predictions_h6.parquet
raw
seen.csv
units.csv

reports:
api_check.md
backtest_h1.md
backtest_h3.md
backtest_h6.md
figures
high_sim_pairs.csv
leakage_check.json
results.md
stage1_summary.md
stage2_summary.md
stage3_summary.md
tuning_h1.json
tuning_h3.json
tuning_h6.json
```

</details>

<details><summary>🔧 Read: PLAN.md · 20:19</summary>

**Аргументы**

```json
{
 "file_path": "d:\\Flash\\golova\\KSE_AI\\AAFS\\PLAN.md"
}
```

**Результат**

```
1	# План: прогноз воздушных тревог в Украине (MVP)
2	
3	## Контекст задачи
4	
5	- Тестовое задание: мини pet-проект на Python, анализ временных рядов воздушных тревог в Украине.
6	- Дедлайн: понедельник, 12.10.2026, 23:59 по Киеву.
7	- Требования: работать с самыми свежими данными, оценивать решение на последнем периоде, не допускать утечки. Ни обучение, ни входы модели не используют ничего, что появилось после момента прогноза.
8	- Что сдаём: ссылку на GitHub-репозиторий с рабочим кодом, полный лог работы с ИИ (чат планирования, сессии Claude Code и Antigravity), рефлексию (~100 слов).
9	- Проверяющие в первую очередь оценивают процесс: итерации, пойманные ошибки ИИ, обоснованные решения.
10	
11	## Данные
12	
13	- Источник: `github.com/Vadimkin/ukrainian-air-raid-sirens-dataset`, файл `datasets/official_data_en.csv`. Время в UTC, лицензия MIT. Данные собираются процессором из Telegram-канала `air_alert_ua`.
14	- **Снимок:** коммит `58ee75b`, SHA-256 файла `b396f87696243069eec0219880e87dcd642b20beb0a7bae0d0e1f61e1ed20ec4` (D01).
15	- **Официальный ряд заканчивается 7 сентября 2026**, потому что канал перестал публиковать посты. Ежедневные коммиты после этой даты меняют только волонтёрские данные уровня областей (D02).
16	- **Как подать в README.** Это первый пункт раздела «Данные»: что обнаружено, как проверено (история коммитов, ID последнего поста, ручная проверка канала), какие альтернативы рассмотрены и почему отклонены. В ограничениях одной строкой: модель месяц не видела данных, то есть в реальном развёртывании её пришлось бы переобучать.
17	- Все решения и цифры по данным — в `DECISIONS.md`. Краткая сводка:
18	  - в файле 38% точных дубликатов; дедупликация — первый шаг загрузки (D03);
19	  - районный режим действует для всех областей с 2025-11-07 (D04);
20	  - охват: 110 районов в 22 областях плюс Киев; после склейки клонов — 104 единицы (D05, D07);
21	  - Донецкая область есть в данных по районам, но это списочные общеобластные тревоги; из целевых переменных она исключена (D06);
22	  - длинные тревоги и тревоги с выдуманным процессором концом помечаются маской «статус неизвестен», а не обрезаются (D10);
23	  - посты об угрозах с 🔴 процессор записывает как начало тревоги; влияние на районный уровень нужно проверить (D09).
24	
25	## Ключевые решения
26	
27	| Решение | Выбор | Где подробно |
28	|---|---|---|
29	| Единица прогноза | Район (Киев — одна единица); практически одинаковые ряды склеиваются | D05, D07 |
30	| Период | С 2025-11-07 00:00 UTC до 2026-09-07 00:00 UTC | D04, D13 |
31	| Исключаем | Донецкую и Луганскую области, Крым (в данных нет), уровень громад | D05, D06, D08 |
32	| Время | Внутри всё в UTC; киевское время только для календарных признаков | — |
33	| Момент прогноза | Каждый час, в начале часа | — |
34	| Целевая переменная | Для единицы, где в момент `t` тихо: начнётся ли тревога в `(t, t+h]` | — |
35	| Тип цели | Бинарная, отдельная модель на каждый h | — |
36	| Горизонт | Основной h = 3; затем 1 и 6. Окончательный на
… [обрезано: показано 3000 из 40113 символов]
```

</details>

<details><summary>🔧 Read: DECISIONS.md · 20:19</summary>

**Аргументы**

```json
{
 "file_path": "d:\\Flash\\golova\\KSE_AI\\AAFS\\DECISIONS.md"
}
```

**Результат**

```
1	# Журнал решений (DECISIONS.md)
2	
3	Формат записи: **находка → решение → почему → альтернативы → статус.**
4	Статусы: «зафиксировано» — решение принято и проверено на данных; «доработать (1б.N)» — нужна задача N из этапа 1б в `PLAN.md`.
5	
6	Все числа ниже посчитаны на зафиксированном снимке (D01) **после дедупликации** (D03). Если повторный подсчёт даёт другие числа, сначала разбираемся в причине, потом идём дальше.
7	
8	---
9	
10	## D00. Как проходил этап 1
11	
12	Этап 1 выполняли три агента независимо: Claude Opus, Gemini Pro и Gemini Flash. Их выводы расходились, и расхождения проверялись короткими скриптами на данных, а не голосованием. Каждый агент где-то ошибся (см. раздел «Пойманные ошибки ИИ»). Совпадение выводов тоже ничего не гарантирует: все трое сообщили о десятках тысяч перекрытий, которых нет (D11), и никто не заметил, что официальные данные заморожены (D02).
13	
14	**Решение:** параллельные агенты используем для анализа (перекрёстная проверка), а код дальше пишем в одной ветке.
15	
16	---
17	
18	## D01. Снимок данных
19	
20	**Находка:** файл `datasets/official_data_en.csv` последний раз менялся в коммите `58ee75b` (2026-09-08 03:44 UTC). В более поздних коммитах, включая `7ccd436` от 2026-10-10, этот файл побайтно тот же (git blob `4c9ef9bf023fefcbfd50cf45188ef36b5119aebe`). Разные снимки у агентов — формальность, данные одинаковые.
21	
22	**Решение:** фиксируем коммит `58ee75b`. Загрузчик проверяет SHA-256 файла `b396f87696243069eec0219880e87dcd642b20beb0a7bae0d0e1f61e1ed20ec4` и падает при несовпадении.
23	
24	**Статус:** зафиксировано; проверка хэша в коде реализована в `src/alerts/ingest/vadimkin.py`.
25	
26	---
27	
28	## D02. Свежесть данных: официальный ряд остановился 7 сентября
29	
30	**Находка:**
31	- Ежедневные коммиты «Add new data» после 8 сентября меняют только волонтёрские файлы (уровень областей, источник eTryvoga).
32	- Официальный процессор читает Telegram-канал `air_alert_ua`. Его последний обработанный пост (ID 338380) — это и последний пост самого канала. Это подтверждено вручную: последний пост в канале датирован сентябрём.
33	- По данным канал остановился утром 7 сентября (около 06:09 UTC). Последняя завершённая тревога в CSV: начало 2026-09-07 05:28:22 UTC, конец 05:39:33 UTC.
34	- Других открытых источников районных тревог за 8 сентября – 10 октября без ключа нет.
35	
36	**Решение:**
37	- Тестовый период — последние 4 полные недели перед концом данных (D14).
38	- В README явно написать, что это самые свежие открытые районные данные и почему.
39	- Дополнительная проверка на сентябре–октябре через API alerts.in.ua — вне MVP, если успеют выдать токен.
40	
41	**Почему:** склеивать два источника прямо на тестовом периоде рискованно. Разная разметка даст сдвиг, который невозможно отличить от ошибки модели.
42	
43	**Альтернативы:**
44	- Волонтёрские данные покрывают сентябрь–октябрь, но только на уровне областей. Для районных целей они не подходят.
45	- Собственный парсер того же канала ничего не даст: новых по
… [обрезано: показано 3000 из 43140 символов]
```

</details>

<details><summary>🔧 Read: README.md · 20:19</summary>

**Аргументы**

```json
{
 "file_path": "d:\\Flash\\golova\\KSE_AI\\AAFS\\README.md"
}
```

**Результат**

```
1	# AAFS — прогноз повітряних тривог за районами України
2	
3	Щогодини для кожного району, де зараз тихо, модель оцінює ймовірність того, що найближчими
4	`h` годинами (1, 3 або 6; основний — 3) там почнеться повітряна тривога. Оцінка — на останніх
5	чотирьох тижнях доступних даних, зі щодобовим перенавчанням і перевірками на витік із майбутнього.
6	
7	Подробиці рішень — у [`DECISIONS.md`](DECISIONS.md) (D00–D22, а також журнал помилок ШІ, які вдалося
8	впіймати), план і статус етапів — у [`PLAN.md`](PLAN.md), усі цифри — у [`reports/`](reports/).
9	
10	## Результат
11	
12	Тест — 2026-08-10 – 2026-09-07, щодобове перенавчання; у квадратних дужках — 95% інтервал
13	бутстрепу за днями, різниці парні (повна таблиця всіх моделей — [`reports/results.md`](reports/results.md)):
14	
15	| h | Частота | B1 (одиниця × година), PR-AUC | LightGBM, PR-AUC | LightGBM − B1, PR-AUC | LightGBM − B1, log loss |
16	|---|---|---|---|---|---|
17	| 1 | 0.121 | 0.398 | 0.434 | **+0.036** [+0.019, +0.050] | −0.022 [−0.033, −0.014] |
18	| 3 | 0.255 | 0.674 | 0.701 | **+0.027** [+0.010, +0.041] | −0.021 [−0.033, −0.009] |
19	| 6 | 0.360 | 0.814 | 0.832 | **+0.018** [+0.005, +0.030] | −0.019 [−0.033, −0.006] |
20	
21	Логістична регресія — між B1 і LightGBM. B0 (загальна частота) і B2 (кількість областей під
22	тривогою) майже не кращі за випадковий прогноз: улітку під тривогою завжди є хоча б кілька
23	прифронтових областей, і ця кількість перестає вимірювати «хвилю» (D18). Калібрування LR і LightGBM
24	близьке до діагоналі (`reports/figures/calibration_h*.png`).
25	
26	Моделі кращі за найкращий бейзлайн, і різниця статистично значуща, але скромна. Основний виграш —
27	усередині областей: B1 майже повністю тримається на відмінності «схід проти заходу», а модель
28	розрізняє моменти й сусідні райони. Наприклад, на тесті при h = 3 PR-AUC у Києві — 0.63 у LR проти
29	0.34 у B1, у Київській області — 0.55 проти 0.34 (`reports/backtest_h3.md`).
30	
31	![Прогноз проти факту](reports/figures/forecast_vs_fact.png)
32	
33	## Дані
34	
35	**Чому дані закінчуються 7 вересня 2026 (D01, D02).** Джерело — офіційний ряд
36	[Vadimkin/ukrainian-air-raid-sirens-dataset](https://github.com/Vadimkin/ukrainian-air-raid-sirens-dataset),
37	який збирається з Telegram-каналу `air_alert_ua`. Щоденні коміти в датасет тривають, але файл
38	`official_data_en.csv` не змінюється з коміту `58ee75b` (8 вересня): після цієї дати оновлюються лише
39	волонтерські дані рівня областей.
40	- Як перевірено: історія комітів (файл побайтово той самий до 10 жовтня); останній оброблений пост
41	  (ID 338380) — це останній пост самого каналу; ручна перевірка каналу.
42	- Що розглянуто й відхилено: волонтерський ряд (лише області, а не райони); власний розбір того самого
43	  каналу (нових постів немає); API alerts.in.ua — джерело з іншою обробкою, його не можна склеювати з
44	  тестом. Його використано окремо, як перевірку через місяць (розділ нижче).
45	- Знімок зафіксовано: коміт `58ee75b`, SHA-256 файлу перевіряєть
… [обрезано: показано 3000 из 9364 символов]
```

</details>

<details><summary>🔧 Bash: Print zone source files with line numbers · 20:19</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; for f in features geo history leakage pipeline; do echo "=== $f"; cat -n src/alerts/$f.py; done
```

**Результат**

```
<persisted-output>
Output too large (30.4KB). Full output saved to: C:\Users\chyck\.claude\projects\d--Flash-golova-KSE-AI-AAFS\57049ae5-374c-471e-8191-1ff2343b8a66\tool-results\bpzuck82j.txt

Preview (first 2KB):
=== features
     1	"""Features for every grid row, computed as of t and vectorised over all moments (PLAN stage 5; D16, D19).
     2	
     3	The builder receives an AlertHistory and never the raw tables (intervals, seen, masks): a new
     4	feature can only use what was known at t. tests/test_knowledge.py checks every feature against a
     5	replay of what the dataset contained at a cut, so a feature that slips past this rule fails there.
     6	The state of a unit "now" comes from the seen table (no bridged pauses, invented ends kept open,
     7	alerts without an all-clear dropped after history.max_open_hours). Oblast and country features
     8	include the input-only unit of Donetsk oblast (D06). Neighbours come from the raion boundaries (geo).
     9	
    10	Channel outages (D15): counts over 7 days are scaled to the observed part of the window, the time
    11	since the last end counts observed time only, and rows whose last 24 hours overlap an outage are
    12	not usable (`lookback_ok` is False): their 6- and 24-hour windows are incomplete.
    13	"""
    14	import numpy as np
    15	import pandas as pd
    16	
    17	from alerts.history import AlertHistory
    18	from alerts.timeutil import to_sec
    19	
    20	KYIV = 'Europe/Kyiv'
    21	HOUR = pd.Timedelta(hours=1)
    22	MINUTE = pd.Timedelta(minutes=1)
    23	
    24	GROUPS = {
    25	    'own': ['since_end_log_h', 'starts_6h', 'starts_24h', 'starts_7d', 'active_share_24h'],
    26	    'oblast': ['oblast_active_share', 'oblast_starts_30m', 'oblast_starts_60m'],
    27	    'country': ['oblasts_active', 'country_starts_30m', 'country_starts_60m'],
    28	    'neighbours': ['neighbor_oblasts_active_share', 'neighbor_units_active_share', 'neighbor_starts_60m'],
    29	    'calendar': ['hour_kyiv', 'dow_kyiv', 'hour_sin', 'hour_cos', 'dow_sin', 'dow_cos'],
    30	}
    31	NUMERIC = [f for g in GROUPS.values() for f in g]
    32	
    33	
    34	class FeatureBuilder:
...
</persisted-output>
```

</details>

<details><summary>🔧 Read: DECISIONS.md · 20:19</summary>

**Аргументы**

```json
{
 "file_path": "d:\\Flash\\golova\\KSE_AI\\AAFS\\DECISIONS.md",
 "offset": 518,
 "limit": 190
}
```

**Результат**

```
518	
519	**Статус:** зафиксировано.
520	
521	---
522	
523	## D20. Модели (этап 6)
524	
525	**Модели** (`src/alerts/models/learned.py`). На каждом шаге бэктеста всё обучается заново только на обучающих строках этого шага: импутация, нормализация, список категорий.
526	- **M1, логистическая регрессия:** числовые признаки с медианной импутацией и индикаторами пропуска, затем стандартизация; час и день недели — через sin/cos; `unit_id` — one-hot; L2-регуляризация.
527	- **M2, LightGBM:** одна модель на все единицы, `unit_id` — категориальный признак. Фиксировано заранее: скорость обучения 0.05, подвыборки строк и признаков по 0.8, λ₂ = 1. Режим детерминированный (`deterministic`, фиксированные число потоков и seed): иначе проверка утечки «бит в бит» не имела бы смысла.
528	
529	**Гиперпараметры выбираются один раз на валидации** (`src/alerts/tuning.py`, таблица — в `reports/backtest_h3.md`). Кандидаты обучаются на строках с `t ≤ train_end − h`, побеждает минимальный log loss на валидации. Число деревьев LightGBM — из ранней остановки на той же валидации; в бэктесте оно фиксировано.
530	- Сетка: LR — C ∈ {0.01, 0.1, 1} × вес свежести {нет, полураспад 28 дней}; LightGBM — листья {15, 63} × `min_child_samples` {200, 1000} × вес свежести {нет, 28 дней}. Вес свежести — гиперпараметр, потому что частота дрейфует: 0.21 в обучении против 0.26 летом (D17).
531	- Выбрано: LR — C = 0.1 без веса; LightGBM — 63 листа, `min_child_samples` = 200, полураспад 28 дней, 84 дерева. У LightGBM все четыре лучших варианта — с весом свежести.
532	- Метрики LR и LightGBM на валидации оптимистичны: гиперпараметры выбирались на ней. Окончательное сравнение — только по тесту.
533	
534	**Результаты, h = 3, тест** (46 270 строк, 24 дня; интервалы — бутстреп по дням; разности парные):
535	
536	| | PR-AUC | ROC-AUC | Brier | log loss |
537	|---|---|---|---|---|
538	| B1 (лучший бейзлайн) | 0.674 [0.652, 0.702] | 0.867 | 0.126 | 0.381 |
539	| M1, LR | 0.692 [0.661, 0.722] | 0.882 | 0.120 | 0.367 |
540	| M2, LightGBM | **0.701** [0.675, 0.726] | **0.883** | **0.119** | **0.360** |
541	| LightGBM − B1 | **+0.027** [+0.010, +0.041] | +0.017 [+0.007, +0.024] | −0.007 [−0.011, −0.003] | **−0.021** [−0.033, −0.009] |
542	| LR − B1 | +0.018 [−0.003, +0.036] | +0.016 [+0.005, +0.024] | −0.006 [−0.011, −0.001] | −0.014 [−0.027, −0.000] |
543	| LightGBM − LR | +0.009 [−0.003, +0.022] | +0.001 | −0.001 | −0.007 [−0.013, −0.002] |
544	
545	**Как это читать:**
546	- Преимущество над лучшим бейзлайном реальное, но скромное: +0.027 PR-AUC и −0.021 log loss, интервалы не пересекают ноль. Это порядок «+0.03» из урока Kizashi; подавать как есть, без преувеличения.
547	- LightGBM лучше LR по log loss, а по ранжированию разница незначима.
548	- Выигрыш моделей виден **внутри областей**, где B1 почти ничего не добавляет к B0. PR-AUC LR против B1: Киев 0.63 против 0.34, Киевская область 0.55 против 0.34, Кировоградская 0.53 против 0.38, Полтавская 0.66 против 0.57. Там, где всё решает идентичность единиц
… [обрезано: показано 3000 из 23586 символов]
```

</details>

<details><summary>🔧 Read: src/alerts/features.py · 20:20</summary>

**Аргументы**

```json
{
 "file_path": "d:\\Flash\\golova\\KSE_AI\\AAFS\\src\\alerts\\features.py"
}
```

**Результат**

```
1	"""Features for every grid row, computed as of t and vectorised over all moments (PLAN stage 5; D16, D19).
2	
3	The builder receives an AlertHistory and never the raw tables (intervals, seen, masks): a new
4	feature can only use what was known at t. tests/test_knowledge.py checks every feature against a
5	replay of what the dataset contained at a cut, so a feature that slips past this rule fails there.
6	The state of a unit "now" comes from the seen table (no bridged pauses, invented ends kept open,
7	alerts without an all-clear dropped after history.max_open_hours). Oblast and country features
8	include the input-only unit of Donetsk oblast (D06). Neighbours come from the raion boundaries (geo).
9	
10	Channel outages (D15): counts over 7 days are scaled to the observed part of the window, the time
11	since the last end counts observed time only, and rows whose last 24 hours overlap an outage are
12	not usable (`lookback_ok` is False): their 6- and 24-hour windows are incomplete.
13	"""
14	import numpy as np
15	import pandas as pd
16	
17	from alerts.history import AlertHistory
18	from alerts.timeutil import to_sec
19	
20	KYIV = 'Europe/Kyiv'
21	HOUR = pd.Timedelta(hours=1)
22	MINUTE = pd.Timedelta(minutes=1)
23	
24	GROUPS = {
25	    'own': ['since_end_log_h', 'starts_6h', 'starts_24h', 'starts_7d', 'active_share_24h'],
26	    'oblast': ['oblast_active_share', 'oblast_starts_30m', 'oblast_starts_60m'],
27	    'country': ['oblasts_active', 'country_starts_30m', 'country_starts_60m'],
28	    'neighbours': ['neighbor_oblasts_active_share', 'neighbor_units_active_share', 'neighbor_starts_60m'],
29	    'calendar': ['hour_kyiv', 'dow_kyiv', 'hour_sin', 'hour_cos', 'dow_sin', 'dow_cos'],
30	}
31	NUMERIC = [f for g in GROUPS.values() for f in g]
32	
33	
34	class FeatureBuilder:
35	    def __init__(self, history: AlertHistory, units: pd.DataFrame, neighbors: pd.DataFrame, cfg: dict):
36	        self.cfg = cfg
37	        self.history = history
38	        u = units.drop_duplicates('unit_id').set_index('unit_id').loc[history.unit_ids].reset_index()
39	        self.unit_ids = history.unit_ids                         # target and input units
40	        self.col = {uid: j for j, uid in enumerate(self.unit_ids)}
41	        self.oblasts = sorted(u['oblast'].unique())
42	        ob_idx = {ob: i for i, ob in enumerate(self.oblasts)}
43	        self.unit_oblast = u['oblast'].map(ob_idx).to_numpy()
44	        self.OB = np.zeros((len(self.unit_ids), len(self.oblasts)))
45	        self.OB[np.arange(len(self.unit_ids)), self.unit_oblast] = 1
46	
47	        nu = neighbors[neighbors['level'] == 'unit']
48	        self.A = np.zeros((len(self.unit_ids), len(self.unit_ids)))
49	        self.A[nu['a'].map(self.col).to_numpy(), nu['b'].map(self.col).to_numpy()] = 1
50	        no = neighbors[neighbors['level'] == 'oblast']
51	        self.O = np.zeros((len(self.oblasts), len(self.oblasts)))
52	        self.O[no['a'].map(ob_idx).to_numpy(), no['b'].map(ob_idx).to_numpy()] = 1
5
… [обрезано: показано 3000 из 6506 символов]
```

</details>

<details><summary>🔧 Read: src/alerts/history.py · 20:20</summary>

**Аргументы**

```json
{
 "file_path": "d:\\Flash\\golova\\KSE_AI\\AAFS\\src\\alerts\\history.py"
}
```

**Результат**

```
1	"""As-of access to alert history (D16): the only way features should read intervals.
2	
3	Information set at moment t: everything a real-time observer of the channel had seen by t.
4	An alert that started at or before t and had not been seen to end by t is active; its end is
5	never returned. The target uses (t, t+h], so the two never share an event.
6	
7	The state is read from the `seen` table (intervals.build_seen), not from the recorded end:
8	  * an invented end start + 1 h (alerts.processor) is written only at the next start, so until
9	    then the alert stays open, as the observer saw it (no all-clear arrived);
10	  * an alert without an all-clear for more than history.max_open_hours stops counting (D19);
11	  * nothing is bridged across pauses (D12), so a unit in a short pause is quiet.
12	
13	What is deliberately not exposed, because it depends on the future:
14	  * episode ends;
15	  * masks of rules (a), (b) and the `uncertain` flag (known only after 24 h or at the next start).
16	Outages (D15) are exposed clipped at t: a silent channel is observable while it is silent.
17	
18	All methods take moments T (DatetimeIndex, tz-aware) and return arrays of shape
19	(len(T), len(unit_ids)). Every query is a binary search, so the cost is O(len(T) * log n).
20	"""
21	import numpy as np
22	import pandas as pd
23	
24	from alerts.mask import OUTAGE
25	from alerts.spans import union
26	from alerts.timeutil import to_sec
27	
28	
29	class AlertHistory:
30	    def __init__(self, seen: pd.DataFrame, intervals: pd.DataFrame, unit_ids, masks: pd.DataFrame | None = None):
31	        """seen: intervals.build_seen() (state); intervals: segments with episode ids (episode starts)."""
32	        self.unit_ids = list(unit_ids)
33	        seen = union(seen, 'unit_id')
34	        self._seg = {}
35	        self._ep_start = {}
36	        for u in self.unit_ids:
37	            g = seen[seen['unit_id'] == u]
38	            s, e = to_sec(g['start']), to_sec(g['end'])
39	            # cumulative duration of all intervals before interval k
40	            before = np.concatenate([[0], np.cumsum(e - s)[:-1]]) if len(s) else np.zeros(0, np.int64)
41	            self._seg[u] = (s, e, before)
42	            ep = intervals[intervals['unit_id'] == u]
43	            self._ep_start[u] = np.sort(to_sec(ep.groupby('episode')['start_utc'].min()))
44	        out = (masks[masks['reason'] == OUTAGE] if masks is not None else pd.DataFrame(columns=['start', 'end']))
45	        out = union(out.assign(k=0), 'k') if len(out) else out
46	        self._outage = (to_sec(out['start']), to_sec(out['end'])) if len(out) else (np.zeros(0, np.int64),) * 2
47	
48	    # --- state now ---------------------------------------------------------------------------
49	    def active(self, T) -> np.ndarray:
50	        """Unit under alert at t: the last segment starting at or before t has not ended by t."""
51	        t = to_sec(T)
52	
53	        def f(s, e, _):
54	            if len(s) == 0:
55	            
… [обрезано: показано 3000 из 6844 символов]
```

</details>

<details><summary>🔧 Read: src/alerts/geo.py · 20:20</summary>

**Аргументы**

```json
{
 "file_path": "d:\\Flash\\golova\\KSE_AI\\AAFS\\src\\alerts\\geo.py"
}
```

**Результат**

```
1	"""Neighbourhood of units and oblasts from the raion boundaries in the dataset snapshot (D19, PLAN rule 9).
2	
3	Source: dataset_repo/example/ukr_admin2.geojson (OCHA admin-2 boundaries, valid from 2025-09-01),
4	pinned by SHA-256. Two raions are neighbours when their boundaries share at least
5	geo.min_shared_vertices vertices (rounded to geo.vertex_decimals): the polygons come from one
6	topologically consistent dataset, so a shared border is a run of identical vertices.
7	
8	Names: geo adm1 "Kharkivska" is our "Kharkivska oblast", geo "Kyiv" is "Kyiv City"; raion names
9	match ours without the " raion" suffix except renamed raions, mapped explicitly in geo.renames
10	and checked: every location of the units table must map to exactly one polygon.
11	"""
12	import itertools
13	import json
14	from collections import defaultdict
15	
16	import pandas as pd
17	
18	from alerts.config import ROOT
19	from alerts.ingest.vadimkin import file_sha256
20	
21	
22	def _our_name(adm1: str, adm2: str, renames_back: dict) -> tuple[str, str]:
23	    if adm1 == 'Kyiv':
24	        return 'Kyiv City', 'Kyiv City'
25	    raion = renames_back.get(adm2, f'{adm2} raion')
26	    return f'{adm1} oblast', raion
27	
28	
29	def raion_adjacency(cfg: dict) -> pd.DataFrame:
30	    """Pairs of neighbouring raions in our naming: columns oblast_a, raion_a, oblast_b, raion_b."""
31	    g = cfg['geo']
32	    p = ROOT / g['path']
33	    if file_sha256(p) != g['sha256']:
34	        raise ValueError(f'SHA-256 mismatch for {p}')
35	    with open(p, encoding='utf-8') as f:
36	        features = json.load(f)['features']
37	    back = {geo: ours for ours, geo in g['renames'].items()}
38	    names = [_our_name(ft['properties']['adm1_name'], ft['properties']['adm2_name'], back) for ft in features]
39	
40	    vertex_owners = defaultdict(set)
41	    for i, ft in enumerate(features):
42	        geom = ft['geometry']
43	        polys = geom['coordinates'] if geom['type'] == 'MultiPolygon' else [geom['coordinates']]
44	        for ring in (r for poly in polys for r in poly):
45	            for x, y in ring:
46	                vertex_owners[(round(x, g['vertex_decimals']), round(y, g['vertex_decimals']))].add(i)
47	    shared = defaultdict(int)
48	    for owners in vertex_owners.values():
49	        for a, b in itertools.combinations(sorted(owners), 2):
50	            shared[(a, b)] += 1
51	    pairs = [(names[a], names[b]) for (a, b), n in shared.items() if n >= g['min_shared_vertices']]
52	    rows = [(*x, *y) for x, y in pairs] + [(*y, *x) for x, y in pairs]
53	    return pd.DataFrame(rows, columns=['oblast_a', 'raion_a', 'oblast_b', 'raion_b']).drop_duplicates()
54	
55	
56	def neighbours(units: pd.DataFrame, cfg: dict) -> pd.DataFrame:
57	    """Neighbour pairs (both directions) of units and of oblasts: columns level, a, b."""
58	    adj = raion_adjacency(cfg)
59	    geo_locs = set(zip(adj['oblast_a'], adj['raion_a']))
60	    missing = [loc for loc in zip(units['oblast'], units['raion']) if 
… [обрезано: показано 3000 из 3941 символов]
```

</details>

<details><summary>🔧 Read: src/alerts/leakage.py · 20:20</summary>

**Аргументы**

```json
{
 "file_path": "d:\\Flash\\golova\\KSE_AI\\AAFS\\src\\alerts\\leakage.py"
}
```

**Результат**

```
1	"""Leakage check (PLAN stage 4, D18): corrupt everything after a cut, rebuild, compare forecasts at the cut.
2	
3	Corruption keeps the start times of future records (the density of channel events, so that outage
4	detection sees the same activity) and shuffles everything else among them: locations, levels and
5	durations. Alerts open at the cut get a random end after the cut. Then every table is rebuilt from
6	the corrupted records, models are fitted on rows with t <= cut - h and predict the rows at t = cut.
7	
8	Must be equal bit for bit: the units table, the training rows with their labels and all features,
9	the features and forecasts of the rows at t = cut. The set of rows at t = cut itself may differ
10	by rows inside a bridged pause (D12: bridging a pause needs the next start); they are reported.
11	
12	Corruption cannot see leaks made by the source itself: a record written later than its own
13	timestamps (the invented end start + 1 h appears only at the next start, D16). knowledge_check
14	covers them: it replays what the dataset contained at the cut (known_at) and requires every feature
15	of the last days before the cut to be equal to the features computed from the full data (D21).
16	"""
17	import numpy as np
18	import pandas as pd
19	
20	from alerts.features import NUMERIC, FeatureBuilder
21	from alerts.pipeline import alert_history, build_tables, model_data
22	from alerts.processor import flag_records
23	
24	LOCATION = ['oblast', 'raion', 'hromada', 'level']
25	
26	
27	def corrupt_after(df: pd.DataFrame, cut: pd.Timestamp, seed: int = 0) -> pd.DataFrame:
28	    rng = np.random.default_rng(seed)
29	    out = df.copy().reset_index(drop=True)
30	    future = np.flatnonzero((out['started_at'] > cut).to_numpy())
31	    perm = rng.permutation(future)
32	    cols = [c for c in LOCATION if c in out.columns]
33	    out.loc[future, cols] = out.loc[perm, cols].to_numpy()
34	    durations = pd.to_timedelta(out.loc[perm, 'duration'].to_numpy(), unit='s')
35	    out.loc[future, 'finished_at'] = out.loc[future, 'started_at'] + durations
36	    open_at_cut = ((out['started_at'] <= cut) & (out['finished_at'] > cut)).to_numpy()
37	    out.loc[open_at_cut, 'finished_at'] = cut + pd.to_timedelta(rng.integers(1, 48 * 3600, open_at_cut.sum()), unit='s')
38	    out['duration'] = (out['finished_at'] - out['started_at']).dt.total_seconds()
39	    return out
40	
41	
42	def known_at(df: pd.DataFrame, cut: pd.Timestamp, cfg: dict) -> pd.DataFrame:
43	    """The records as the dataset contained them at `cut`.
44	
45	    A record exists once it has been written: at its all-clear, or for an invented end at the next
46	    start of its location. Records started by the cut but not yet written were open alerts; they are
47	    kept with the end cut + 1 s, which is "still open at the cut" without adding a far-future event
48	    (that would create a fake channel outage after the last real event).
49	    """
50	    key = [c for c in LOCATION if c in df.columns]
51	  
… [обрезано: показано 3000 из 6968 символов]
```

</details>

<details><summary>🔧 Read: src/alerts/pipeline.py · 20:20</summary>

**Аргументы**

```json
{
 "file_path": "d:\\Flash\\golova\\KSE_AI\\AAFS\\src\\alerts\\pipeline.py"
}
```

**Результат**

```
1	"""End-to-end build: tables of stages 1b-3, features (stage 5), backtests (stages 4, 6).
2	
3	Computation only; saving is a separate step (save_all) and is done by scripts/run_all.py.
4	"""
5	import logging
6	from dataclasses import dataclass
7	
8	import pandas as pd
9	
10	from alerts import store
11	from alerts.config import ROOT
12	from alerts.features import FeatureBuilder
13	from alerts.geo import neighbours
14	from alerts.grid import build_grid
15	from alerts.history import AlertHistory
16	from alerts.ingest.vadimkin import load_official
17	from alerts.intervals import build_intervals, build_seen
18	from alerts.mask import build_masks
19	from alerts.scope import select_scope
20	from alerts.units import build_units
21	
22	logger = logging.getLogger(__name__)
23	
24	
25	@dataclass
26	class Artifacts:
27	    df: pd.DataFrame          # whole cleaned file (D03)
28	    scope_all: pd.DataFrame   # scope records of all time (mask rule (b) needs neighbours)
29	    scope: pd.DataFrame       # scope records overlapping [work_start, data_end)
30	    units: pd.DataFrame
31	    neighbors: pd.DataFrame   # unit and oblast neighbours from the boundaries (D19)
32	    pairs: pd.DataFrame       # Jaccard of every same-oblast pair (train period)
33	    masks: pd.DataFrame
34	    outages: pd.DataFrame
35	    mask_stats: dict
36	    intervals: pd.DataFrame
37	    seen: pd.DataFrame        # as-of state seen in real time (D16, D19)
38	    grid: pd.DataFrame        # stage 3: (unit, t) rows with targets
39	    grid_stats: dict
40	
41	
42	def build_all(cfg: dict) -> Artifacts:
43	    df = load_official(ROOT / cfg['dataset']['path'], cfg['dataset']['sha256'])
44	    return build_tables(df, cfg)
45	
46	
47	def build_tables(df: pd.DataFrame, cfg: dict, units: pd.DataFrame | None = None,
48	                 neighbors: pd.DataFrame | None = None) -> Artifacts:
49	    """All tables from cleaned records. `units` and `neighbors` can be given (tests)."""
50	    scope_all = select_scope(df, cfg, period=False)
51	    scope = select_scope(df, cfg, period=True)
52	    logger.info(f'Scope records: {len(scope_all):,} of all time, {len(scope):,} overlap the working period')
53	
54	    pairs = pd.DataFrame(columns=['oblast', 'raion1', 'raion2', 'jaccard'])
55	    if units is None:
56	        units, pairs = build_units(scope, cfg)
57	    if neighbors is None:
58	        neighbors = neighbours(units, cfg)
59	    masks, outages, mask_stats = build_masks(df, scope_all, units, cfg)
60	    for o in outages.itertuples():
61	        logger.warning(f'Channel outage (D15): {o.start} -> {o.end} ({o.end - o.start})')
62	    intervals = build_intervals(scope, units, masks, cfg)
63	    seen = build_seen(scope, units, cfg)
64	    grid, grid_stats = build_grid(seen, intervals, masks, units, cfg)
65	    logger.info(f'Grid: {len(grid):,} rows')
66	    return Artifacts(df, scope_all, scope, units, neighbors, pairs, masks, outages, mask_stats, intervals, seen, grid, grid_stats)
67	
68	
69	def alert_
… [обрезано: показано 3000 из 4345 символов]
```

</details>

<details><summary>🔧 Bash: Print supporting modules and config · 20:20</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; for f in processor intervals spans scope timeutil store config; do echo "=== $f"; cat -n src/alerts/$f.py; done; echo "=== config.yaml"; cat -n config.yaml
```

**Результат**

```
=== processor
     1	"""Artifacts of the official channel processor (D09, D10, D16).
     2	
     3	What the processor does for one source location (dataset_repo/processors/official_channel_processor.py):
     4	  * "Повітряна тривога" opens an alert in memory; nothing is written yet;
     5	  * "Відбій" closes it and writes the record with the real end;
     6	  * a new alert while one is still open (its all-clear was lost):
     7	      - more than 3 h after the open start: the open alert is written with end = start + 1 h,
     8	        and this invented end appears in the CSV only now, at the new start;
     9	      - within 3 h: the open alert is replaced, its start disappears from the CSV without a trace.
    10	
    11	So an invented end carries the timestamp start + 1 h but becomes known only at the next start.
    12	"""
    13	import pandas as pd
    14	
    15	
    16	def flag_records(records: pd.DataFrame, cfg: dict, key: list[str]) -> pd.DataFrame:
    17	    """Add per-record columns, computed over all records of the same source location `key`.
    18	
    19	    next_start   start of the next record of the location (NaT for the last one);
    20	    is_long      rule (a): longer than long_alert_hours;
    21	    is_fake_end  rule (b): exactly fake_end_duration_s and the next start more than
    22	                 fake_end_next_start_h later. Retrospective: it needs the next start, so it is
    23	                 for masks (target side) only;
    24	    open_until   until when the alert looked open to a real-time observer (D16). A record of
    25	                 exactly fake_end_duration_s is treated as never closed by an all-clear and stays
    26	                 open until the next start of its location. Decided from the record itself, not
    27	                 from the 3-hour test, because that test needs the future.
    28	    """
    29	    rec = records.sort_values(key + ['started_at'])
    30	    rec['next_start'] = rec.groupby(key, sort=False)['started_at'].shift(-1)
    31	
    32	    fake_s = cfg['processor']['fake_end_duration_s']
    33	    fake_gap = pd.Timedelta(hours=cfg['processor']['fake_end_next_start_h'])
    34	    rec['is_long'] = rec['duration'] > cfg['thresholds']['long_alert_hours'] * 3600
    35	    invented_length = rec['duration'] == fake_s
    36	    if not cfg['processor']['enabled']:         # another source has no such artifact (stage 8, D22)
    37	        invented_length = pd.Series(False, index=rec.index)
    38	    rec['is_fake_end'] = invented_length & ((rec['next_start'] - rec['started_at']) > fake_gap)
    39	
    40	    later_start = rec['next_start'].where(rec['next_start'] > rec['finished_at'])
    41	    rec['open_until'] = rec['finished_at'].where(~invented_length | later_start.isna(), later_start)
    42	    return rec.sort_index()
=== intervals
     1	"""Unit-level alert intervals (stage 2; D11, D12, D16). Pure functions: nothing is written
… [обрезано: показано 3000 из 27832 символов]
```

</details>

<details><summary>🔧 Bash: Print mask, grid, units modules and tests · 20:20</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; for f in mask grid units; do echo "=== $f"; cat -n src/alerts/$f.py; done; for f in conftest test_features test_leakage test_knowledge test_history; do echo "=== $f"; cat -n tests/$f.py; done
```

**Результат**

```
<persisted-output>
Output too large (39.8KB). Full output saved to: C:\Users\chyck\.claude\projects\d--Flash-golova-KSE-AI-AAFS\57049ae5-374c-471e-8191-1ff2343b8a66\tool-results\bd9odaizc.txt

Preview (first 2KB):
=== mask
     1	"""Mask of "status unknown" (D10, D13, D15). Pure functions: nothing is written to disk here.
     2	
     3	Rules, all evaluated retrospectively (they use the future, so they are target-side only):
     4	  (a) long_24h       alert longer than long_alert_hours: the alert itself;
     5	  (b) fake_1h        processor-invented end (exactly fake_end_duration_s, next start of the same
     6	                     source location more than fake_end_next_start_h later): (start, next_start);
     7	  (c) after_data_end everything from data_end to the end of the file;
     8	  (d) outage         channel silence: no event of any record for more than outage_gap_hours.
     9	Rules (a) and (b) are applied to source locations (the processor works per location) and then
    10	moved to units; (c) and (d) apply to every unit.
    11	
    12	The mask table keeps one row per (unit, reason, merged interval): intervals are disjoint within a
    13	reason but may overlap across reasons. Use spans.union() for the total masked time.
    14	"""
    15	import pandas as pd
    16	
    17	from alerts.config import ts
    18	from alerts.scope import ROLE_TARGET, attach_units
    19	from alerts.spans import clipped_seconds, union
    20	
    21	LONG = 'long_24h'
    22	FAKE_END = 'fake_1h'
    23	AFTER_END = 'after_data_end'
    24	OUTAGE = 'outage'
    25	REASONS = [LONG, FAKE_END, AFTER_END, OUTAGE]
    26	# Reasons that make an alert's own end unreliable (`uncertain` flag in intervals)
    27	UNCERTAIN_REASONS = [LONG, FAKE_END, OUTAGE]
    28	
    29	MASK_COLUMNS = ['unit_id', 'start', 'end', 'reason']
    30	
    31	
    32	def detect_outages(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    33	    """D15: silences of the whole channel inside [work_start, data_end).
    34	
    35	    Events are the starts and ends of every record in the file, at any level and in any oblast:
...
</persisted-output>
```

</details>

<details><summary>🔧 Read: C:/Users/chyck/.claude/projects/d--Flash-golova-KSE-AI-AAFS/57049ae5-374c-471e-8191-1ff2343b8a66/tool-results/bd9odaizc… · 20:20</summary>

**Аргументы**

```json
{
 "file_path": "C:\\Users\\chyck\\.claude\\projects\\d--Flash-golova-KSE-AI-AAFS\\57049ae5-374c-471e-8191-1ff2343b8a66\\tool-results\\bd9odaizc.txt"
}
```

**Результат**

```
1	=== mask
2	     1	"""Mask of "status unknown" (D10, D13, D15). Pure functions: nothing is written to disk here.
3	     2	
4	     3	Rules, all evaluated retrospectively (they use the future, so they are target-side only):
5	     4	  (a) long_24h       alert longer than long_alert_hours: the alert itself;
6	     5	  (b) fake_1h        processor-invented end (exactly fake_end_duration_s, next start of the same
7	     6	                     source location more than fake_end_next_start_h later): (start, next_start);
8	     7	  (c) after_data_end everything from data_end to the end of the file;
9	     8	  (d) outage         channel silence: no event of any record for more than outage_gap_hours.
10	     9	Rules (a) and (b) are applied to source locations (the processor works per location) and then
11	    10	moved to units; (c) and (d) apply to every unit.
12	    11	
13	    12	The mask table keeps one row per (unit, reason, merged interval): intervals are disjoint within a
14	    13	reason but may overlap across reasons. Use spans.union() for the total masked time.
15	    14	"""
16	    15	import pandas as pd
17	    16	
18	    17	from alerts.config import ts
19	    18	from alerts.scope import ROLE_TARGET, attach_units
20	    19	from alerts.spans import clipped_seconds, union
21	    20	
22	    21	LONG = 'long_24h'
23	    22	FAKE_END = 'fake_1h'
24	    23	AFTER_END = 'after_data_end'
25	    24	OUTAGE = 'outage'
26	    25	REASONS = [LONG, FAKE_END, AFTER_END, OUTAGE]
27	    26	# Reasons that make an alert's own end unreliable (`uncertain` flag in intervals)
28	    27	UNCERTAIN_REASONS = [LONG, FAKE_END, OUTAGE]
29	    28	
30	    29	MASK_COLUMNS = ['unit_id', 'start', 'end', 'reason']
31	    30	
32	    31	
33	    32	def detect_outages(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
34	    33	    """D15: silences of the whole channel inside [work_start, data_end).
35	    34	
36	    35	    Events are the starts and ends of every record in the file, at any level and in any oblast:
37	    36	    while the channel posts, some event appears every few hours (longest normal gap is 3.7 h).
38	    37	    Returns columns start (last event before the gap), end (first event after it).
39	    38	    """
40	    39	    work_start, data_end = ts(cfg['periods']['work_start']), ts(cfg['data_end'])
41	    40	    min_gap = pd.Timedelta(hours=cfg['thresholds']['outage_gap_hours'])
42	    41	    events = pd.concat([df['started_at'], df['finished_at']]).sort_values().drop_duplicates()
43	    42	    events = events.reset_index(drop=True)
44	    43	    gap = events.diff()
45	    44	    i = gap.index[gap > min_gap]
46	    45	    out = pd.DataFrame({'start': events[i - 1].reset_index(drop=True),
47	    46	                        'end': events[i].reset_index(drop=True)})
48	    47	    return out[(out['start'] < data_end) & (out['end'] > work_start)].reset_index(drop=True)
49	    48	
50	    49	
51	    50	def build_masks(df: pd.DataFrame, scope_all: pd.DataFrame, units: pd.DataFrame, cfg:
… [обрезано: показано 3000 из 42860 символов]
```

</details>

<details><summary>🔧 Bash: Show leakage report and its call sites · 20:20</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; cat reports/leakage_check.json; echo; grep -n "leak\|knowledge" scripts/run_all.py src/alerts/*.py | grep -v "^src/alerts/leakage.py"; head -5 data/neighbors.csv; wc -l data/neighbors.csv; ls -la reviews/scratch 2>/dev/null
```

**Результат** (ошибка)

```
Exit code 2
[
 {
  "check": "corrupted_future",
  "cut": "2026-08-10 00:00:00+00:00",
  "h": 3,
  "training_rows": 568326,
  "rows_at_cut": 89,
  "rows_at_cut_only_one_version": 0,
  "future_changed": true
 },
 {
  "check": "known_at_cut",
  "cut": "2026-08-10 00:00:00+00:00",
  "rows": 14450,
  "open_at_cut": 31
 },
 {
  "check": "corrupted_future",
  "cut": "2026-08-21 14:00:00+00:00",
  "h": 3,
  "training_rows": 592629,
  "rows_at_cut": 95,
  "rows_at_cut_only_one_version": 0,
  "future_changed": true
 },
 {
  "check": "known_at_cut",
  "cut": "2026-08-21 14:00:00+00:00",
  "rows": 14715,
  "open_at_cut": 24
 }
]
scripts/run_all.py:7:leakage check fails.
scripts/run_all.py:18:from alerts import figures, leakage, report  # noqa: E402
scripts/run_all.py:53:            if h == cfg['leakage_check']['horizon']:
scripts/run_all.py:59:        lc = cfg['leakage_check']
scripts/run_all.py:62:        checks = {'corrupted_future': lambda c: leakage.check(art.df, cfg, c, lc['horizon'], models),
scripts/run_all.py:63:                  'known_at_cut': lambda c: leakage.knowledge_check(art.df, cfg, c)}
scripts/run_all.py:72:        (out / 'leakage_check.json').write_text(json.dumps(results, indent=1), encoding='utf-8')
src/alerts/config.py:23:    'leakage_check': ['cuts', 'horizon'],
src/alerts/features.py:4:feature can only use what was known at t. tests/test_knowledge.py checks every feature against a
level,a,b
oblast,Cherkaska oblast,Kirovohradska oblast
oblast,Cherkaska oblast,Kyivska oblast
oblast,Cherkaska oblast,Poltavska oblast
oblast,Cherkaska oblast,Vinnytska oblast
633 data/neighbors.csv
```

</details>

<details><summary>🔧 Bash: Show run_all and environment versions · 20:20</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; cat -n scripts/run_all.py; ls src/alerts/models; python --version; python -c "import pandas, numpy, lightgbm; print(pandas.__version__, numpy.__version__, lightgbm.__version__)"; nproc
```

**Результат**

```
1	"""One command from scratch: snapshot -> tables (stages 1b-3) -> features -> backtests -> reports.
     2	
     3	    python scripts/run_all.py              # everything
     4	    python scripts/run_all.py --no-backtest
     5	
     6	Exits with code 1 if a recomputed number differs from the DECISIONS.md reference table or if the
     7	leakage check fails.
     8	"""
     9	import argparse
    10	import json
    11	import logging
    12	import sys
    13	import time
    14	from pathlib import Path
    15	
    16	sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
    17	
    18	from alerts import figures, leakage, report  # noqa: E402
    19	from alerts.config import load_config, path, ts  # noqa: E402
    20	from alerts.evaluation import evaluate, write_report, write_summary  # noqa: E402
    21	from alerts.models import registry  # noqa: E402
    22	from alerts.pipeline import build_all, model_data, save_all  # noqa: E402
    23	from alerts.spans import union  # noqa: E402
    24	from alerts.tuning import tune  # noqa: E402
    25	from fetch_data import ensure_snapshot  # noqa: E402
    26	
    27	
    28	def main() -> int:
    29	    ap = argparse.ArgumentParser()
    30	    ap.add_argument('--no-backtest', action='store_true', help='stop after the tables and their reports')
    31	    args = ap.parse_args()
    32	    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(name)s: %(message)s')
    33	    t0 = time.time()
    34	    cfg = load_config()
    35	    ensure_snapshot(cfg)
    36	    art = build_all(cfg)
    37	    save_all(art, cfg)
    38	    failed = bool(report.write_all(art, cfg))
    39	
    40	    if not args.no_backtest:
    41	        out = path(cfg, 'reports')
    42	        bt = cfg['backtest']
    43	        data = model_data(art, cfg)
    44	        tuned, summaries = {}, []
    45	        for h in bt['horizons']:
    46	            tuned[h], table = tune(data, h, cfg)
    47	            (out / f'tuning_h{h}.json').write_text(json.dumps(tuned[h], indent=1), encoding='utf-8')
    48	            models = registry(cfg, bt['baselines'] + bt['models'], tuned[h])
    49	            res = evaluate(data, h, models, bt['baselines'], cfg)
    50	            write_report(res, cfg, out, _tuning_md(table))
    51	            res['preds'].to_parquet(str(path(cfg, 'predictions')).format(h=h))
    52	            summaries.append({k: v for k, v in res.items() if k != 'preds'})
    53	            if h == cfg['leakage_check']['horizon']:
    54	                rp = cfg['report']
    55	                outage = union(art.masks[art.masks['reason'] == 'outage'].assign(k=0), 'k')
    56	                figures.forecast_vs_fact(res['preds'], art.intervals, outage, art.units, rp['forecast_units'],
    57	                                         rp['forecast_days'], h, out / 'figures' / 'forecast_vs_fact.png')
    58	        write_summary(summaries, cfg, out)
… [обрезано: показано 3000 из 5420 символов]
```

</details>

<details><summary>🔧 Bash: Build pipeline artifacts in memory and cache to scratch · 20:20</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; mkdir -p reviews/scratch/stage5-leakage; cat > reviews/scratch/stage5-leakage/build_cache.py <<'EOF'
"""Build artifacts in memory and cache them (pickle) inside the scratch folder only."""
import pickle, time, logging
from pathlib import Path
import alerts.config, alerts.pipeline
HERE = Path(__file__).resolve().parent
t0 = time.time()
cfg = alerts.config.load_config()
art = alerts.pipeline.build_all(cfg)
print('build', time.time() - t0)
data = alerts.pipeline.model_data(art, cfg)
print('model_data', time.time() - t0, len(data))
from alerts.features import FeatureBuilder
fb = FeatureBuilder(alerts.pipeline.alert_history(art), art.units, art.neighbors, cfg)
feat = fb.build(art.grid)
with open(HERE / 'art.pkl', 'wb') as f:
    pickle.dump({'art': art, 'feat': feat}, f)
print('done', time.time() - t0)
EOF
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage5-leakage/build_cache.py
```

**Результат**

```
Channel outage (D15): 2026-08-29 05:55:28+00:00 -> 2026-09-02 13:48:04+00:00 (4 days 07:52:36)
build 12.119507789611816
model_data 13.960264921188354 615151
done 15.908385038375854
```

</details>

<details><summary>🔧 Bash: Inspect model registry, shapely, feature importance · 20:24</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; cat src/alerts/models/__init__.py | head -60; python -c "import shapely; print(shapely.__version__)"; python -c "import geopandas" 2>&1 | tail -1; grep -n "gain\|neighbor\|oblast_" reports/backtest_h3.md | head -40
```

**Результат**

```
"""Model registry: name -> factory of a fresh unfitted model with fit(X, y) / predict_proba(X)."""
from alerts.models.baselines import BASELINES
from alerts.models.learned import LEARNED


def registry(cfg: dict, names: list, params: dict | None = None) -> dict:
    """Factories for the named models. Learned models need their tuned `params[name]`."""
    out = {}
    for name in names:
        if name in BASELINES:
            out[name] = (lambda cls=BASELINES[name]: cls(cfg))
        elif name in LEARNED:
            if not params or name not in params:
                raise KeyError(f'{name} needs tuned parameters')
            out[name] = (lambda cls=LEARNED[name], p=params[name]: cls(cfg, p))
        else:
            raise KeyError(f'unknown model {name}')
    return out
Traceback (most recent call last):
  File "<string>", line 1, in <module>
ModuleNotFoundError: No module named 'shapely'
ModuleNotFoundError: No module named 'geopandas'
52:## LightGBM feature importance (gain share, model of the last test day)
60:| neighbor_oblasts_active_share | 0.043 |
67:| neighbor_units_active_share | 0.005 |
68:| neighbor_starts_60m | 0.003 |
70:| oblast_starts_60m | 0.002 |
71:| oblast_active_share | 0.002 |
72:| oblast_starts_30m | 0.000 |
```

</details>

<details><summary>🔧 Bash: Show feature importance table and git status · 20:24</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; sed -n 50,80p reports/backtest_h3.md; git status --short | head
```

**Результат**

```
| LGBM | +0.0088 [-0.0034, +0.0216] | +0.0010 [-0.0034, +0.0058] | -0.0012 [-0.0032, +0.0010] | -0.0074 [-0.0126, -0.0019] |

## LightGBM feature importance (gain share, model of the last test day)

| Feature | Gain share |
|---|---|
| starts_7d | 0.530 |
| unit_id | 0.145 |
| active_share_24h | 0.079 |
| since_end_log_h | 0.052 |
| neighbor_oblasts_active_share | 0.043 |
| hour_kyiv | 0.037 |
| starts_24h | 0.026 |
| dow_kyiv | 0.024 |
| country_starts_60m | 0.021 |
| oblasts_active | 0.017 |
| country_starts_30m | 0.013 |
| neighbor_units_active_share | 0.005 |
| neighbor_starts_60m | 0.003 |
| starts_6h | 0.002 |
| oblast_starts_60m | 0.002 |
| oblast_active_share | 0.002 |
| oblast_starts_30m | 0.000 |

## Test by oblast

200 bootstrap draws of days within the oblast. Few positives mean wide intervals; "—": no positives in the test part, PR-AUC undefined. Within an oblast the ranking has to separate moments and nearby units, not east from west.

| Oblast | Rows | Positives | PR-AUC B0 | PR-AUC B1 | PR-AUC B2 | PR-AUC LR | PR-AUC LGBM |
|---|---|---|---|---|---|---|---|
| Ivano-Frankivska oblast | 3,234 | 0 | — | — | — | — | — |
```

</details>

<details><summary>🔧 Write: reviews/scratch/stage5-leakage/recompute.py · 20:25</summary>

**Аргументы**

```
# file: reviews/scratch/stage5-leakage/recompute.py
"""Task 1: independent recomputation of every feature for random grid rows, straight from source records.

No AlertHistory, no spans.union, no intervals/seen tables: records from select_scope (open_until is
the processor rule) -> per-unit Python loops. Compares with FeatureBuilder output (cached in art.pkl).
"""
import pickle
import sys
from collections import defaultdict
from datetime import timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

import alerts.config
from alerts.scope import select_scope
from alerts.timeutil import to_sec

HERE = Path(__file__).resolve().parent
cfg = alerts.config.load_config()
D = pickle.load(open(HERE / 'art.pkl', 'rb'))
art, feat = D['art'], D['feat']
grid = art.grid
units = art.units

# ---------- records per unit ----------
sc = select_scope(art.df, cfg, period=True)
key = dict(zip(zip(units['oblast'], units['raion']), units['unit_id']))
sc['unit_id'] = [key[(o, r)] for o, r in zip(sc['oblast'], sc['raion'])]
CAP = cfg['history']['max_open_hours'] * 3600
PAUSE = cfg['thresholds']['pause_merge_min'] * 60

recs = defaultdict(list)
for u, s, e, ou in zip(sc['unit_id'], to_sec(sc['started_at']), to_sec(sc['finished_at']), to_sec(sc['open_until'])):
    recs[u].append((int(s), int(e), int(ou)))

def merge(iv, gap=0):
    iv = sorted(iv)
    out = []
    for s, e in iv:
        if out and s - out[-1][1] <= gap:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return out

seen, ep_starts = {}, {}
for u, rr in recs.items():
    seen[u] = merge([(s, min(ou, s + CAP)) for s, e, ou in rr])        # observer view
    segs = merge([(s, e) for s, e, ou in rr])                           # recorded ends
    eps = merge([tuple(x) for x in segs], gap=PAUSE)
    ep_starts[u] = sorted(x[0] for x in eps)

# ---------- outages, independently: gaps > 6 h between any event of the whole file ----------
ev = n
… [обрезано: показано 2000 из 6337 символов]
```

**Результат**

```
File created successfully at: d:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage5-leakage\recompute.py (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Bash: Run independent feature recomputation · 20:25</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; time PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage5-leakage/recompute.py
```

**Результат**

```
outages [(Timestamp('2026-08-29 05:55:28'), Timestamp('2026-09-02 13:48:04'))]
oblasts 24
rows checked 300 features 21
all features equal on all rows

real	0m27.397s
user	0m0.000s
sys	0m0.047s
```

</details>

<details><summary>🔧 Bash: Recompute features for rows with starts on window edges · 20:26</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; cat > reviews/scratch/stage5-leakage/boundary.py <<'EOF'
"""Rows where some episode start lies exactly on a window edge (t or t - w): recompute them independently."""
import runpy, sys
import numpy as np, pandas as pd
ns = runpy.run_path(str(__import__('pathlib').Path(__file__).with_name('recompute.py')).replace('recompute.py','recompute_lib.py')) if False else None
EOF
sed -n '1,/^rng = /p' reviews/scratch/stage5-leakage/recompute.py | head -n -1 > reviews/scratch/stage5-leakage/recompute_lib.py
cat > reviews/scratch/stage5-leakage/boundary.py <<'EOF'
"""Rows where an episode start lies exactly on a window edge (t or t - w): recompute them independently."""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent))
from collections import defaultdict
import numpy as np, pandas as pd
from recompute_lib import *   # noqa

allst = np.array(sorted(s for u in ep_starts for s in ep_starts[u]))
print('episode starts', len(allst), 'exactly on the hour', int((allst % 3600 == 0).sum()), 'on :30', int((allst % 1800 == 0).sum()))
T = to_sec(grid['t'])
edge = set()
for w in [0, 1800, 3600, 6 * 3600, 86400, 7 * 86400]:
    on = set((allst[allst % 1800 == 0] + w).tolist())
    hit = np.flatnonzero(np.isin(T, list(on)))
    print('w', w, 'rows with a start exactly at t - w:', len(hit))
    rng = np.random.default_rng(w)
    edge |= set(rng.choice(hit, min(25, len(hit)), replace=False).tolist()) if len(hit) else set()
bad = defaultdict(list)
for i in sorted(edge):
    u, t = grid.at[i, 'unit_id'], int(T[i])
    mine = compute(u, t)
    for c, v in mine.items():
        w = feat.loc[i, c]
        ok = (bool(v) == bool(w)) if c == 'lookback_ok' else ((np.isnan(v) and np.isnan(w)) or np.isclose(np.float32(v), w, rtol=1e-6, atol=1e-6))
        if not ok:
            bad[c].append((i, u, grid.at[i, 't'], v, w))
print('edge rows checked', len(edge), 'mismatches', {c: len(l) for c, l in bad.items()})
EOF
PYTHONPATH=src PYTHONIOENCO
… [обрезано: показано 2000 из 2060 символов]
```

**Результат**

```
outages [(Timestamp('2026-08-29 05:55:28'), Timestamp('2026-09-02 13:48:04'))]
oblasts 24
episode starts 66644 exactly on the hour 15 on :30 33
w 0 rows with a start exactly at t - w: 1017
w 1800 rows with a start exactly at t - w: 1470
w 3600 rows with a start exactly at t - w: 971
w 21600 rows with a start exactly at t - w: 991
w 86400 rows with a start exactly at t - w: 1040
w 604800 rows with a start exactly at t - w: 984
edge rows checked 150 mismatches {}
```

</details>

<details><summary>🔧 Bash: Analyze outage rules effect on features after 02.09 · 20:27</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; cat > reviews/scratch/stage5-leakage/outage_rules.py <<'EOF'
"""Task 2: D19 outage rules (lookback_ok, starts_7d scaling, since_obs) and how features shift after 02.09."""
import pickle
from pathlib import Path
import numpy as np, pandas as pd
import alerts.config
from alerts.pipeline import alert_history
from alerts.timeutil import to_sec
HERE = Path(__file__).resolve().parent
cfg = alerts.config.load_config()
D = pickle.load(open(HERE / 'art.pkl', 'rb')); art, feat = D['art'], D['feat']
g = pd.concat([art.grid, feat], axis=1)
H = pd.Timestamp
o_s, o_e = H('2026-08-29 05:55:28', tz='UTC'), H('2026-09-02 13:48:04', tz='UTC')
test = g[g['part'] == 'test']
print('test grid rows', len(test), 'lookback_ok False', int((~test['lookback_ok']).sum()),
      'range of dropped t:', test.loc[~test['lookback_ok'], 't'].min(), test.loc[~test['lookback_ok'], 't'].max())
# unscaled starts_7d
hist = alert_history(art)
T = pd.DatetimeIndex(np.sort(g['t'].unique()))
ti = np.searchsorted(to_sec(T), to_sec(g['t']))
col = {u: j for j, u in enumerate(hist.unit_ids)}
uj = g['unit_id'].map(col).to_numpy()
raw7 = hist.starts(T, pd.Timedelta(days=7))[ti, uj]
g['starts_7d_raw'] = raw7
g['scale'] = g['starts_7d'] / np.where(raw7 > 0, raw7, np.nan)
post = g[(g['t'] >= H('2026-09-03 14:00', tz='UTC')) & g['lookback_ok']]
pre = g[(g['t'] >= H('2026-08-22 00:00', tz='UTC')) & (g['t'] < H('2026-08-29 00:00', tz='UTC'))]
mid = g[(g['t'] >= H('2026-08-10 00:00', tz='UTC')) & (g['t'] < H('2026-08-29 00:00', tz='UTC'))]
print('post-outage usable rows', len(post), 'scale range', post['scale'].min(), post['scale'].max())
for name, d in [('test 08-10..08-29', mid), ('08-22..08-29', pre), ('post 09-03 14:00..', post)]:
    print(f'{name:22s} rows {len(d):6d} starts_7d mean {d.starts_7d.mean():.2f} median {d.starts_7d.median():.2f} '
          f'raw mean {d.starts_7d_raw.mean():.2f}; since_end_log_h mean {d.since_end_log_h.mean():.3f}; '
          f'starts_24h mean {d.starts_
… [обрезано: показано 2000 из 3542 символов]
```

**Результат**

```
test grid rows 48402 lookback_ok False 1758 range of dropped t: 2026-09-02 14:00:00+00:00 2026-09-03 13:00:00+00:00
post-outage usable rows 6959 scale range 1.5969749733253762 2.6199512481689453
test 08-10..08-29      rows  39281 starts_7d mean 14.83 median 11.00 raw mean 14.83; since_end_log_h mean 3.114; starts_24h mean 2.104; y3 0.249
08-22..08-29           rows  14124 starts_7d mean 14.14 median 7.00 raw mean 14.14; since_end_log_h mean 3.187; starts_24h mean 2.348; y3 0.282
post 09-03 14:00..     rows   6959 starts_7d mean 21.16 median 18.34 raw mean 9.49; since_end_log_h mean 2.959; starts_24h mean 2.571; y3 0.286
per-unit means (units with rows in both): 104
          pre  post_scaled  post_raw
count  104.00       104.00    104.00
mean    17.73        24.40     10.95
std     16.23        18.74      8.47
min      0.00         0.00      0.00
25%      2.13         5.05      2.16
50%     15.03        28.63     12.68
75%     32.67        41.47     18.88
max     57.41        63.84     29.92
median ratio post_scaled/pre 1.5158483982086182 post_raw/pre 0.6921044017692155
start_utc
2026-08-20 00:00:00+00:00    271
2026-08-21 00:00:00+00:00    235
2026-08-22 00:00:00+00:00    280
2026-08-23 00:00:00+00:00    251
2026-08-24 00:00:00+00:00    271
2026-08-25 00:00:00+00:00    318
2026-08-26 00:00:00+00:00    318
2026-08-27 00:00:00+00:00    381
2026-08-28 00:00:00+00:00    426
2026-08-29 00:00:00+00:00     78
2026-09-02 00:00:00+00:00    195
2026-09-03 00:00:00+00:00    348
2026-09-04 00:00:00+00:00    363
2026-09-05 00:00:00+00:00    296
2026-09-06 00:00:00+00:00    262
Name: count, dtype: int64
h=1 before 08-29       rows  39615 y 0.118  LGBM 0.114  LR 0.115  B1 0.118
h=1 after 09-03 14:00  rows   6959 y 0.134  LGBM 0.144  LR 0.146  B1 0.125
h=3 before 08-29       rows  39500 y 0.249  LGBM 0.247  LR 0.249  B1 0.255
h=3 after 09-03 14:00  rows   6770 y 0.286  LGBM 0.304  LR 0.299  B1 0.261
h=6 before 08-29       rows  39281 y 0.352  LGBM 0.359  LR 0.368  B1 0.369
h=6 after 09-03 14:00  rows   6486 y 0.407  LGBM 0.422  LR 0.438  B1 0.365
```

</details>

<details><summary>🔧 Bash: Read backtest, evaluation, learned models, tuning · 20:27</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; cat -n src/alerts/backtest.py; sed -n 1,60p src/alerts/evaluation.py; cat -n src/alerts/models/learned.py | head -120; cat reports/tuning_h3.json
```

**Результат**

```
1	"""Walk-forward backtest with daily retraining (PLAN stage 4, D18).
     2	
     3	For every forecast day D (UTC midnight to midnight) a fresh model is fitted on the rows with
     4	t <= D - h, whose labels (t, t+h] are fully known by D, and predicts the rows with t in [D, D + 1 day).
     5	Rows without a label for this horizon (D17) are never used.
     6	"""
     7	import logging
     8	import time
     9	
    10	import numpy as np
    11	import pandas as pd
    12	
    13	from alerts.config import ts
    14	
    15	logger = logging.getLogger(__name__)
    16	DAY = pd.Timedelta(days=1)
    17	
    18	
    19	def days(cfg: dict, part: str) -> pd.DatetimeIndex:
    20	    """Forecast days of the validation or test part."""
    21	    p = cfg['periods']
    22	    lo, hi = {'val': (p['train_end'], p['val_end']), 'test': (p['val_end'], cfg['data_end'])}[part]
    23	    return pd.date_range(ts(lo), ts(hi), freq='D', inclusive='left')
    24	
    25	
    26	def walk_forward(data: pd.DataFrame, h: int, forecast_days, make_model) -> pd.DataFrame:
    27	    """Predictions for every labelled row of the forecast days: columns row (index of data), day, p.
    28	
    29	    make_model() returns a fresh unfitted model with fit(X, y) / predict_proba(X).
    30	    """
    31	    ycol = f'y_{h}'
    32	    lab = data[data[ycol].notna()]
    33	    t = lab['t']
    34	    y = lab[ycol].to_numpy(dtype=float)
    35	    out = []
    36	    for day in forecast_days:
    37	        train = (t <= day - pd.Timedelta(hours=h)).to_numpy()
    38	        test = ((t >= day) & (t < day + DAY)).to_numpy()
    39	        if not test.any():
    40	            continue
    41	        model = make_model().fit(lab[train], y[train])
    42	        out.append(pd.DataFrame({'row': lab.index[test], 'day': day, 'p': model.predict_proba(lab[test])}))
    43	    return pd.concat(out, ignore_index=True)
    44	
    45	
    46	def run(data: pd.DataFrame, h: int, models: dict, cfg: dict, parts=('val', 'test')) -> pd.DataFrame:
    47	    """All models on the given parts. Returns one row per (part, labelled row): y, day, oblast, p_<model>."""
    48	    ycol = f'y_{h}'
    49	    frames = []
    50	    for part in parts:
    51	        fd = days(cfg, part)
    52	        preds = None
    53	        for name, make in models.items():
    54	            t0 = time.time()
    55	            p = walk_forward(data, h, fd, make).set_index('row')
    56	            logger.info(f'h={h} {part} {name}: {len(p):,} rows, {time.time() - t0:.1f} s')
    57	            if preds is None:
    58	                preds = p[['day']].copy()
    59	            preds[f'p_{name}'] = p['p']
    60	        preds['part'] = part
    61	        src = data.loc[preds.index]
    62	        preds['y'] = src[ycol].astype(int)
    63	        for c in ['t', 'unit_id', 'oblast']:
    64	            preds[c] = src[c]
    65	        frames.append(preds)
    
… [обрезано: показано 3000 из 11287 символов]
```

</details>

<details><summary>🔧 Write: reviews/scratch/stage5-leakage/phantom.py · 20:28</summary>

**Аргументы**

```
# file: reviews/scratch/stage5-leakage/phantom.py
"""Episode starts are cut by the RECORDED end (intervals), including invented ends written later.

In a unit made of several source locations (clone groups, Donetsk I00), location A with an invented
end s_A + 1 h is still open for a real-time observer until A's next start w_A. A start of another
location B in (s_A + 1 h + 15 min, w_A) is an episode start in the full data, but in the data as known
at t < w_A it falls inside A's open record, so it is not. List these 'phantom' starts and the grid
rows whose count features differ between full data and knowledge at t.
"""
import pickle
from pathlib import Path

import numpy as np
import pandas as pd

import alerts.config
from alerts.scope import attach_units
from alerts.timeutil import to_sec

HERE = Path(__file__).resolve().parent
cfg = alerts.config.load_config()
D = pickle.load(open(HERE / 'art.pkl', 'rb')); art, feat = D['art'], D['feat']
units = art.units
nloc = units.groupby('unit_id').size()
multi = nloc[nloc > 1]
print('multi-location units:', multi.to_dict())

rec = attach_units(art.scope, units)
ep_start = art.intervals.groupby('episode').agg(unit_id=('unit_id', 'first'), s=('start_utc', 'min'))
rows = []
for u in multi.index:
    r = rec[rec['unit_id'] == u]
    fake = r[r['is_fake_end']]
    es = ep_start[ep_start['unit_id'] == u]['s']
    for a in fake.itertuples():
        # episode starts of the unit after A's recorded end and before A is written
        ph = es[(es > a.finished_at) & (es < a.next_start)]
        for s in ph:
            rows.append({'unit_id': u, 'loc_A': a.raion, 's_A': a.started_at, 'written_A': a.next_start, 's_B': s})
ph = pd.DataFrame(rows).drop_duplicates(['unit_id', 's_B'])
print('fake-end records in multi-location units:',
      int(rec[rec['unit_id'].isin(multi.index) & rec['is_fake_end']].shape[0]))
print('phantom episode starts:', len(ph))
if len(ph):
    ph['delay_h'] = (ph['written_A'] - ph['s_B']).dt.total_seconds() / 3600
  
… [обрезано: показано 2000 из 3743 символов]
```

**Результат**

```
File created successfully at: d:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage5-leakage\phantom.py (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Bash: Find phantom episode starts from invented ends · 20:28</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage5-leakage/phantom.py
```

**Результат**

```
multi-location units: {'I00': 8, 'U001': 5, 'U003': 2, 'U025': 3}
fake-end records in multi-location units: 6
phantom episode starts: 0
{} any feature: 0
```

</details>

<details><summary>🔧 Bash: List real one-hour records and held-open moments · 20:28</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; cat > reviews/scratch/stage5-leakage/real1h.py <<'EOF'
"""Records of exactly 1 h that are real (next start <= 3 h): seen keeps them open until the next start.
Which hourly moments fall inside (end, next_start)? Those are cuts where known_at disagrees with seen."""
import pickle
from pathlib import Path
import pandas as pd
import alerts.config
from alerts.scope import attach_units
HERE = Path(__file__).resolve().parent
D = pickle.load(open(HERE / 'art.pkl', 'rb')); art = D['art']
rec = attach_units(art.scope, art.units)
r = rec[(rec['duration'] == 3600)]
print('records of exactly 3600 s in scope (period):', len(r), ' fake (rule b):', int(r.is_fake_end.sum()))
real = r[~r['is_fake_end'] & (r['open_until'] > r['finished_at'])]
print(real[['unit_id', 'oblast', 'raion', 'started_at', 'finished_at', 'next_start']].to_string())
for x in real.itertuples():
    hrs = pd.date_range(x.finished_at.ceil('h'), x.next_start, freq='h', inclusive='left')
    hrs = [h for h in hrs if h > x.finished_at]
    print(x.unit_id, x.raion, 'hourly moments inside (end, next_start):', [str(h) for h in hrs])
fk = rec[rec['is_fake_end'] & rec['unit_id'].isin(['I00', 'U001', 'U003', 'U025'])]
print(fk[['unit_id', 'raion', 'started_at', 'finished_at', 'next_start']].to_string())
EOF
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage5-leakage/real1h.py
```

**Результат**

```
records of exactly 3600 s in scope (period): 82  fake (rule b): 76
      unit_id                  oblast                 raion                started_at               finished_at                next_start
20302    U066           Sumska oblast      Okhtyrskyi raion 2026-01-27 09:44:35+00:00 2026-01-27 10:44:35+00:00 2026-01-27 11:29:38+00:00
21101    U008       Kharkivska oblast  Bohodukhivskyi raion 2026-01-31 23:46:52+00:00 2026-02-01 00:46:52+00:00 2026-02-01 01:19:00+00:00
29331    U083           Sumska oblast         Sumskyi raion 2026-03-04 16:29:41+00:00 2026-03-04 17:29:41+00:00 2026-03-04 19:03:54+00:00
44683    U065           Odeska oblast         Odeskyi raion 2026-04-28 18:23:58+00:00 2026-04-28 19:23:58+00:00 2026-04-28 19:30:26+00:00
53065    U077  Dnipropetrovska oblast     Samarivskyi raion 2026-05-27 09:24:20+00:00 2026-05-27 10:24:20+00:00 2026-05-27 12:06:06+00:00
53066    U019  Dnipropetrovska oblast     Dniprovskyi raion 2026-05-27 09:24:20+00:00 2026-05-27 10:24:20+00:00 2026-05-27 12:06:11+00:00
U066 Okhtyrskyi raion hourly moments inside (end, next_start): ['2026-01-27 11:00:00+00:00']
U008 Bohodukhivskyi raion hourly moments inside (end, next_start): ['2026-02-01 01:00:00+00:00']
U083 Sumskyi raion hourly moments inside (end, next_start): ['2026-03-04 18:00:00+00:00', '2026-03-04 19:00:00+00:00']
U065 Odeskyi raion hourly moments inside (end, next_start): []
U077 Samarivskyi raion hourly moments inside (end, next_start): ['2026-05-27 11:00:00+00:00', '2026-05-27 12:00:00+00:00']
U019 Dniprovskyi raion hourly moments inside (end, next_start): ['2026-05-27 11:00:00+00:00', '2026-05-27 12:00:00+00:00']
      unit_id              raion                started_at               finished_at                next_start
75239    U025   Skadovskyi raion 2026-08-03 01:39:54+00:00 2026-08-03 02:39:54+00:00 2026-08-03 05:38:36+00:00
75240    U025   Kakhovskyi raion 2026-08-03 01:39:54+00:00 2026-08-03 02:39:54+00:00 2026-08-03 05:38:36+00:00
75241    U025  Henicheskyi raion 2026-08-03 01:39:54+00:00 2026-08-03 02:39:54+00:00 2026-08-03 05:38:36+00:00
84933    U025   Skadovskyi raion 2026-08-29 02:34:52+00:00 2026-08-29 03:34:52+00:00 2026-09-03 07:02:50+00:00
84934    U025   Kakhovskyi raion 2026-08-29 02:34:52+00:00 2026-08-29 03:34:52+00:00 2026-09-03 07:02:50+00:00
84935    U025  Henicheskyi raion 2026-08-29 02:34:52+00:00 2026-08-29 03:34:52+00:00 2026-09-03 07:02:50+00:00
```

</details>

<details><summary>🔧 Bash: Run knowledge_check at real one-hour alert cuts · 20:29</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; cat > reviews/scratch/stage5-leakage/kcheck.py <<'EOF'
"""Run leakage.knowledge_check exactly as run_all.py does, on the cuts given on the command line."""
import pickle, sys, time, logging
from pathlib import Path
import pandas as pd
import alerts.config
from alerts import leakage
logging.disable(logging.WARNING)
HERE = Path(__file__).resolve().parent
cfg = alerts.config.load_config()
art = pickle.load(open(HERE / 'art.pkl', 'rb'))['art']
for c in sys.argv[1:]:
    cut = alerts.config.ts(c)
    t0 = time.time()
    try:
        res = leakage.knowledge_check(art.df, cfg, cut)
        print('PASS', res, f'{time.time() - t0:.0f} s', flush=True)
    except AssertionError as e:
        msg = str(e)
        print('FAIL', c, f'{time.time() - t0:.0f} s', msg[:1500].replace('\n', ' | '), flush=True)
EOF
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage5-leakage/kcheck.py 2026-03-04T18:00:00Z 2026-05-27T12:00:00Z
```

**Результат**

```
FAIL 2026-03-04T18:00:00Z 24 s features known at 2026-03-04 18:00:00+00:00.iloc[:, 5] (column name="oblast_active_share") are different |  | features known at 2026-03-04 18:00:00+00:00.iloc[:, 5] (column name="oblast_active_share") values are different (0.02652 %) | [index]: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, ...] | [left]:  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.6666667, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.6666667, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.6666667, nan, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.25, 0.0, 0.5, 0.0, 0.0, 0.0, 0.25, 0.0, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ...] | [right]: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.6666667, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.6666667, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.6666667, nan, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
FAIL 2026-05-27T12:00:00Z 22 s features known at 2026-05-27 12:00:00+00:00.iloc[:, 5] (column name="oblast_active_share") are different |  | features known at 2026-05-27 12:00:00+00:00.iloc[:, 5] (column name="oblast_active_share") values are different (0.01379 %) | [index]: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, ...] | [left]:  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.5, 0.5, 0.0, 0.16666667, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.6666667, 0.0, 0.0, 0.16666667, 0.0, 0.0, 0.0, 0.0, 0.6666667, 0.0, 0.0, 0.6666667, 0.6666667, 0.0, 0.16666667, nan, 0.6666667, 0.0, 0.0, 0.0, 0.0, 0.16666667, 0.0, 0.0, 0.0, 0.16666667, 0.0, 0.0, 0.6666667, 0.0, 0.0, 0.0, 0.16666667, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 1.0, 0.0, 0.0, 1.0, 0.6666667, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.0, 0.6666667, 0.16666667, 0.0, 0.0, 0.0, 0.2, 0.0, 0.6666667, 0.0, 0.16666667, 0.0, 0.5, 0.0, 0.0, 0.6666667, 0.0, 0.5, 0.0, 0.16666667, nan, 0.5, ...] | [right]: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.5, 0.5, 0.0, 0.16666667, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.6666667, 0.0, 0.0, 0.16666667, 0.0, 0.0
… [обрезано: показано 3000 из 3084 символов]
```

</details>

<details><summary>🔧 Bash: Find hourly moments inside bridged pauses · 20:30</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; cat > reviews/scratch/stage5-leakage/find_cuts.py <<'EOF'
import pickle
from pathlib import Path
import pandas as pd
art = pickle.load(open(Path(__file__).resolve().parent / 'art.pkl', 'rb'))['art']
iv = art.intervals.sort_values(['unit_id', 'start_utc'])
iv['next_start'] = iv.groupby('unit_id')['start_utc'].shift(-1)
iv['next_ep'] = iv.groupby('unit_id')['episode'].shift(-1)
br = iv[(iv['next_ep'] == iv['episode'])]
br = br.assign(h=br['end_utc'].dt.ceil('h'))
br = br[(br['h'] < br['next_start']) & (br['h'] > br['end_utc'])]
print('bridged pauses containing an hourly moment:', len(br))
print(br[br['h'] >= '2026-08-01'][['unit_id', 'end_utc', 'next_start', 'h']].head(10).to_string())
EOF
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage5-leakage/find_cuts.py
```

**Результат**

```
bridged pauses containing an hourly moment: 816
     unit_id                   end_utc                next_start                         h
743      I00 2026-08-18 04:55:26+00:00 2026-08-18 05:04:59+00:00 2026-08-18 05:00:00+00:00
766      I00 2026-08-26 13:58:59+00:00 2026-08-26 14:01:54+00:00 2026-08-26 14:00:00+00:00
768      I00 2026-08-26 16:52:56+00:00 2026-08-26 17:04:19+00:00 2026-08-26 17:00:00+00:00
783      I00 2026-09-05 17:46:59+00:00 2026-09-05 18:00:40+00:00 2026-09-05 18:00:00+00:00
3287    U001 2026-08-23 04:53:36+00:00 2026-08-23 05:08:17+00:00 2026-08-23 05:00:00+00:00
3322    U001 2026-09-02 13:56:55+00:00 2026-09-02 14:09:55+00:00 2026-09-02 14:00:00+00:00
5513    U005 2026-08-25 11:59:06+00:00 2026-08-25 12:06:01+00:00 2026-08-25 12:00:00+00:00
8774    U008 2026-08-02 09:59:13+00:00 2026-08-02 10:05:25+00:00 2026-08-02 10:00:00+00:00
8778    U008 2026-08-02 16:54:25+00:00 2026-08-02 17:05:26+00:00 2026-08-02 17:00:00+00:00
8785    U008 2026-08-03 15:53:23+00:00 2026-08-03 16:02:45+00:00 2026-08-03 16:00:00+00:00
```

</details>

<details><summary>🔧 Bash: Run knowledge_check on targeted cuts · 20:30</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage5-leakage/kcheck.py 2026-08-03T04:00:00Z 2026-08-29T04:00:00Z 2026-09-02T14:00:00Z 2026-08-25T12:00:00Z 2026-09-03T06:00:00Z 2>&1 | cut -c1-600
```

**Результат**

```
PASS {'cut': '2026-08-03 04:00:00+00:00', 'rows': 14371, 'open_at_cut': 53} 27 s
PASS {'cut': '2026-08-29 04:00:00+00:00', 'rows': 14068, 'open_at_cut': 51} 28 s
FAIL 2026-09-02T14:00:00Z 29 s features known at 2026-09-02 14:00:00+00:00.iloc[:, 0] (column name="since_end_log_h") are different |  | features known at 2026-09-02 14:00:00+00:00.iloc[:, 0] (column name="since_end_log_h") values are different (1.41901 %) | [index]: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 8
PASS {'cut': '2026-08-25 12:00:00+00:00', 'rows': 14605, 'open_at_cut': 30} 29 s
PASS {'cut': '2026-09-03 06:00:00+00:00', 'rows': 4985, 'open_at_cut': 49} 32 s
```

</details>

<details><summary>🔧 Bash: Diagnose knowledge_check failure after outage · 20:33</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; cat > reviews/scratch/stage5-leakage/diag_0902.py <<'EOF'
"""Why knowledge_check fails at 2026-09-02 14:00: compare the full and the known-at-cut artifacts."""
import pickle, sys, logging
from pathlib import Path
import numpy as np, pandas as pd
import alerts.config
from alerts.features import FeatureBuilder, NUMERIC
from alerts.leakage import known_at
from alerts.pipeline import alert_history, build_tables
logging.disable(logging.WARNING)
HERE = Path(__file__).resolve().parent
cfg = alerts.config.load_config()
art = pickle.load(open(HERE / 'art.pkl', 'rb'))['art']
cut = alerts.config.ts(sys.argv[1] if len(sys.argv) > 1 else '2026-09-02T14:00:00Z')
kdf = known_at(art.df, cut, cfg)
known = build_tables(kdf, cfg, art.units, art.neighbors)
print('outages full :', art.outages.to_dict('records'))
print('outages known:', known.outages.to_dict('records'))
# what is the event at the full outage start?
o = art.outages.iloc[0]
ev = art.df[(art.df['started_at'] == o.start) | (art.df['finished_at'] == o.start)]
print('records with an event at the full outage start:\n', ev[['oblast', 'raion', 'hromada', 'level', 'started_at', 'finished_at', 'duration']].to_string())
rows = art.grid[(art.grid['t'] > cut - pd.Timedelta(days=7)) & (art.grid['t'] <= cut)][['unit_id', 't']].reset_index(drop=True)
ff = FeatureBuilder(alert_history(art), art.units, art.neighbors, cfg).build(rows)
fk = FeatureBuilder(alert_history(known), art.units, art.neighbors, cfg).build(rows)
for c in NUMERIC + ['lookback_ok']:
    a, b = ff[c].to_numpy(dtype=float), fk[c].to_numpy(dtype=float)
    d = ~((a == b) | (np.isnan(a) & np.isnan(b)))
    if d.any():
        print(f'{c}: {d.sum()} rows differ; moments {rows.loc[d, "t"].min()} .. {rows.loc[d, "t"].max()}; '
              f'example full={a[d][:3]} known={b[d][:3]}')
EOF
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage5-leakage/diag_0902.py
```

**Результат**

```
outages full : [{'start': Timestamp('2026-08-29 05:55:28+0000', tz='UTC'), 'end': Timestamp('2026-09-02 13:48:04+0000', tz='UTC')}]
outages known: [{'start': Timestamp('2026-08-29 05:48:13+0000', tz='UTC'), 'end': Timestamp('2026-09-02 13:48:04+0000', tz='UTC')}]
records with an event at the full outage start:
                   oblast             raion hromada  level                started_at               finished_at  duration
183485  Poltavska oblast  Poltavskyi raion     NaN  raion 2026-08-29 04:55:28+00:00 2026-08-29 05:55:28+00:00    3600.0
since_end_log_h: 70 rows differ; moments 2026-09-02 14:00:00+00:00 .. 2026-09-02 14:00:00+00:00; example full=[3.11337948 6.25362253 1.40827322] known=[3.10799384 6.25339031 1.37827623]
starts_7d: 52 rows differ; moments 2026-09-02 14:00:00+00:00 .. 2026-09-02 14:00:00+00:00; example full=[18.33965874 49.77907181 39.29926682] known=[18.37428284 49.87305069 39.37346268]
```

</details>

<details><summary>🔧 Bash: Inspect events around the outage start · 20:33</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; cat > reviews/scratch/stage5-leakage/diag_outage_edge.py <<'EOF'
import pickle
from pathlib import Path
import pandas as pd
art = pickle.load(open(Path(__file__).resolve().parent / 'art.pkl', 'rb'))['art']
df = art.df
p = df[(df.oblast == 'Poltavska oblast') & (df.raion == 'Poltavskyi raion') & (df.level == 'raion')].sort_values('started_at')
print(p[(p.started_at > '2026-08-28 20:00')][['started_at', 'finished_at', 'duration']].head(4).to_string())
lo, hi = pd.Timestamp('2026-08-29 05:30', tz='UTC'), pd.Timestamp('2026-08-29 06:00', tz='UTC')
ev = df[((df.started_at >= lo) & (df.started_at <= hi)) | ((df.finished_at >= lo) & (df.finished_at <= hi))]
print(ev[['oblast', 'raion', 'hromada', 'level', 'started_at', 'finished_at', 'duration']].sort_values('finished_at').to_string())
# all records ending exactly 1 h after start whose end lies in the last hour before the gap
EOF
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage5-leakage/diag_outage_edge.py
```

**Результат**

```
started_at               finished_at  duration
183288 2026-08-28 20:08:45+00:00 2026-08-28 20:28:09+00:00    1164.0
183337 2026-08-28 22:49:11+00:00 2026-08-28 23:24:20+00:00    2109.0
183353 2026-08-28 23:26:23+00:00 2026-08-29 04:13:15+00:00   17212.0
183485 2026-08-29 04:55:28+00:00 2026-08-29 05:55:28+00:00    3600.0
                        oblast                 raion hromada  level                started_at               finished_at  duration
183474      Mykolaivska oblast    Voznesenskyi raion     NaN  raion 2026-08-29 04:33:18+00:00 2026-08-29 05:33:18+00:00    3600.0
183475     Chernihivska oblast      Nizhynskyi raion     NaN  raion 2026-08-29 04:33:34+00:00 2026-08-29 05:33:34+00:00    3600.0
183476      Mykolaivska oblast    Pervomaiskyi raion     NaN  raion 2026-08-29 04:38:53+00:00 2026-08-29 05:38:53+00:00    3600.0
183478    Kirovohradska oblast   Holovanivskyi raion     NaN  raion 2026-08-29 04:40:52+00:00 2026-08-29 05:40:52+00:00    3600.0
183481       Kharkivska oblast  Krasnohradskyi raion     NaN  raion 2026-08-29 04:47:58+00:00 2026-08-29 05:47:58+00:00    3600.0
183482  Dnipropetrovska oblast     Samarivskyi raion     NaN  raion 2026-08-29 04:48:13+00:00 2026-08-29 05:48:13+00:00    3600.0
183485        Poltavska oblast      Poltavskyi raion     NaN  raion 2026-08-29 04:55:28+00:00 2026-08-29 05:55:28+00:00    3600.0
```

</details>

<details><summary>🔧 Bash: Find last real event before outage · 20:34</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; cat >> reviews/scratch/stage5-leakage/diag_outage_edge.py <<'EOF'
print('Poltavskyi next start:', p[p.started_at > '2026-08-29 04:55:28'].started_at.min())
o_s = pd.Timestamp('2026-08-29 05:55:28', tz='UTC')
real_end = df[(df.duration != 3600) & (df.finished_at <= o_s)].finished_at.max()
last_start = df[df.started_at <= o_s].started_at.max()
print('last start before the gap:', last_start, ' last end of a record not exactly 1 h:', real_end)
n3600 = df[(df.duration == 3600) & (df.finished_at <= o_s) & (df.finished_at > max(real_end, last_start))]
print('exactly-1h ends after the last real event:', len(n3600))
EOF
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage5-leakage/diag_outage_edge.py | tail -4
```

**Результат**

```
183485        Poltavska oblast      Poltavskyi raion     NaN  raion 2026-08-29 04:55:28+00:00 2026-08-29 05:55:28+00:00    3600.0
Poltavskyi next start: 2026-09-02 14:17:15+00:00
last start before the gap: 2026-08-29 04:55:28+00:00  last end of a record not exactly 1 h: 2026-08-29 04:42:39+00:00
exactly-1h ends after the last real event: 12
```

</details>

<details><summary>🔧 Bash: Count pending invented ends at cuts · 20:34</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; cat > reviews/scratch/stage5-leakage/pending.py <<'EOF'
"""How many invented ends are 'pending' (end <= cut < written) at a cut? Without one, knowledge_check
cannot see the D16 class at that cut."""
import pickle
from pathlib import Path
import numpy as np, pandas as pd
import alerts.config
from alerts.grid import moments
art = pickle.load(open(Path(__file__).resolve().parent / 'art.pkl', 'rb'))['art']
cfg = alerts.config.load_config()
sc = art.scope
fk = sc[sc['is_fake_end']]
print('invented-end records in scope (period):', len(fk))
T = moments(cfg)
pend = np.array([int(((fk.finished_at <= t) & (fk.next_start > t)).sum()) for t in T])
print('hourly moments:', len(T), ' with >=1 pending invented end:', int((pend > 0).sum()),
      f'({(pend > 0).mean():.1%})')
part = pd.Series(np.where(T < alerts.config.ts(cfg['periods']['train_end']), 'train',
                 np.where(T < alerts.config.ts(cfg['periods']['val_end']), 'val', 'test')))
print(pd.Series(pend > 0).groupby(part.values).mean())
for c in cfg['leakage_check']['cuts'] + ['2026-08-03T04:00:00Z', '2026-03-04T18:00:00Z', '2026-09-02T14:00:00Z']:
    t = alerts.config.ts(c)
    print(c, 'pending invented ends at the cut:', int(((fk.finished_at <= t) & (fk.next_start > t)).sum()))
# hours of the test part outside the outage with a pending invented end
EOF
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage5-leakage/pending.py
```

**Результат**

```
invented-end records in scope (period): 76
hourly moments: 7128  with >=1 pending invented end: 354 (5.0%)
test     0.191964
train    0.031985
val      0.059524
dtype: float64
2026-08-10T00:00:00Z pending invented ends at the cut: 0
2026-08-21T14:00:00Z pending invented ends at the cut: 0
2026-08-03T04:00:00Z pending invented ends at the cut: 6
2026-03-04T18:00:00Z pending invented ends at the cut: 0
2026-09-02T14:00:00Z pending invented ends at the cut: 13
```

</details>

<details><summary>🔧 Write: reviews/scratch/stage5-leakage/mutations.py · 20:36</summary>

**Аргументы**

```
# file: reviews/scratch/stage5-leakage/mutations.py
"""Task 4: mutation testing of leakage.check (corrupted future) and leakage.knowledge_check (known at cut).

Nothing in the project is edited: mutations are monkeypatches applied in this process only.
usage: python mutations.py syn                      # synthetic data of tests/, every mutation, both checks
       python mutations.py real CUT [CUT ...]       # real data, every mutation, both checks
"""
import logging
import pickle
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tests'))
logging.disable(logging.WARNING)

import alerts.config  # noqa: E402
import alerts.leakage as L  # noqa: E402
import alerts.pipeline as P  # noqa: E402
from alerts.features import FeatureBuilder  # noqa: E402
from alerts.history import AlertHistory  # noqa: E402
from alerts.intervals import build_seen  # noqa: E402
from alerts.mask import FAKE_END, LONG  # noqa: E402
from alerts.models import registry  # noqa: E402
from alerts.spans import covers, union  # noqa: E402
from alerts.timeutil import to_sec  # noqa: E402

ORIG_AH = P.alert_history
ORIG_BUILD = FeatureBuilder.build
HOUR = pd.Timedelta(hours=1)


def ah_attach(art):
    h = ORIG_AH(art)
    h._art = art
    return h


def ah_end_utc(art):
    """m2: state from the recorded segments (end_utc), as before D16."""
    seg = art.intervals.rename(columns={'start_utc': 'start', 'end_utc': 'end'})[['unit_id', 'start', 'end']]
    h = AlertHistory(seg, art.intervals, art.units['unit_id'].drop_duplicates().tolist(), art.masks)
    h._art = art
    return h


def ah_no_open_until(art, cfg):
    """m5: seen built without open_until (invented end = all-clear), the 24 h cap kept."""
    sc = art.scope.assign(open_until=art.scope['finished_at'])
    h = AlertHistory(build_seen(sc, art.units, cfg), art.intervals,
                     art.units['unit_id'].drop_duplicates().toli
… [обрезано: показано 2000 из 6919 символов]
```

**Результат**

```
File created successfully at: d:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage5-leakage\mutations.py (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Bash: Run mutation tests on synthetic data · 20:36</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; python - <<'EOF'
p='reviews/scratch/stage5-leakage/mutations.py'
s=open(p,encoding='utf-8').read()
s=s.replace("""        muts = MUTATIONS if len(sys.argv) < 4 or not sys.argv[-1].startswith('m') else [sys.argv[-1]]
        cuts = [c for c in sys.argv[2:] if not c.startswith('m') and c != 'none']""","""        muts = MUTATIONS
        cuts = sys.argv[2:]""")
open(p,'w',encoding='utf-8').write(s)
EOF
time PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage5-leakage/mutations.py syn
```

**Результат**

```
SYN none                         corrupted_future: pass   [pass; pass; pass; pass] | known_at: pass (2s) 257; pass (2s) 230
SYN m1_window+1h                 corrupted_future: CAUGHT [CAUGHT; CAUGHT; pass; pass] | known_at: CAUGHT (2s) features known at 2026-02-20 12:00:00+00:00.iloc[:, 2] (column name="starts_24h") are different; pass (2s) 230
SYN m2_end_utc                   corrupted_future: pass   [pass; pass; pass; pass] | known_at: CAUGHT (2s) features known at 2026-02-20 12:00:00+00:00.iloc[:, 8] (column name="oblasts_active") are different; CAUGHT (1s) features known at 2026-02-20 12:00:00+00:00.iloc[:, 8] (column name="oblasts_active") are different
SYN m3_uncertain                 corrupted_future: CAUGHT [pass; pass; CAUGHT; CAUGHT] | known_at: CAUGHT (2s) features known at 2026-02-20 12:00:00+00:00.iloc[:, 9] (column name="country_starts_30m") are different; pass (2s) 230
SYN m4_masks_ab                  corrupted_future: CAUGHT [pass; pass; CAUGHT; CAUGHT] | known_at: CAUGHT (2s) features known at 2026-02-20 12:00:00+00:00.iloc[:, 10] (column name="country_starts_60m") are different; CAUGHT (2s) features known at 2026-02-20 12:00:00+00:00.iloc[:, 10] (column name="country_starts_60m") are different
SYN m5_seen_without_open_until   corrupted_future: pass   [pass; pass; pass; pass] | known_at: CAUGHT (2s) features known at 2026-02-20 12:00:00+00:00.iloc[:, 8] (column name="oblasts_active") are different; CAUGHT (2s) features known at 2026-02-20 12:00:00+00:00.iloc[:, 8] (column name="oblasts_active") are different

real	1m9.787s
user	0m0.015s
sys	0m0.016s
```

</details>

*[ошибка API · 20:37: You&#x27;ve hit your weekly limit · resets 2am (Europe/Kyiv)]*

<details><summary>🔧 Bash: Check scratch files and repo status · 08:41</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; ls -la reviews/scratch/stage5-leakage/; grep -n "muts =\|cuts =" reviews/scratch/stage5-leakage/mutations.py; git status --short | head -20
```

**Результат**

```
total 134447
drwxr-xr-x 1 chyck 197609         0 Oct 11 20:36 .
drwxr-xr-x 1 chyck 197609         0 Oct 11 20:24 ..
drwxr-xr-x 1 chyck 197609         0 Oct 11 20:26 __pycache__
-rw-r--r-- 1 chyck 197609 137602027 Oct 11 20:20 art.pkl
-rw-r--r-- 1 chyck 197609      1378 Oct 11 20:26 boundary.py
-rw-r--r-- 1 chyck 197609       708 Oct 11 20:20 build_cache.py
-rw-r--r-- 1 chyck 197609      1747 Oct 11 20:33 diag_0902.py
-rw-r--r-- 1 chyck 197609      1366 Oct 11 20:34 diag_outage_edge.py
-rw-r--r-- 1 chyck 197609       635 Oct 11 20:30 find_cuts.py
-rw-r--r-- 1 chyck 197609       748 Oct 11 20:29 kcheck.py
-rw-r--r-- 1 chyck 197609      6905 Oct 11 20:36 mutations.py
-rw-r--r-- 1 chyck 197609      3354 Oct 11 20:27 outage_rules.py
-rw-r--r-- 1 chyck 197609      1270 Oct 11 20:34 pending.py
-rw-r--r-- 1 chyck 197609      3693 Oct 11 20:28 phantom.py
-rw-r--r-- 1 chyck 197609         2 Oct 11 20:28 phantom_starts.csv
-rw-r--r-- 1 chyck 197609      1213 Oct 11 20:28 real1h.py
-rw-r--r-- 1 chyck 197609      6285 Oct 11 20:25 recompute.py
-rw-r--r-- 1 chyck 197609      4943 Oct 11 20:26 recompute_lib.py
158:        muts = MUTATIONS
159:        cuts = sys.argv[2:]
 M .gitignore
?? reviews/SUMMARY.md
?? reviews/stage0-1b.md
?? reviews/stage2.md
?? reviews/stage3.md
?? reviews/stage4-6.md
?? reviews/stage5-leakage.md
?? reviews/stage7.md
?? reviews/stage8.md
```

</details>

<details><summary>🔧 Bash: Run mutation tests on real data cuts · 08:42</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; git log --oneline | head -2; PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage5-leakage/mutations.py real 2026-08-21T14:00:00Z 2026-08-03T04:00:00Z > reviews/scratch/stage5-leakage/mutations_real.out 2>&1
```

**Результат**

```
Command running in background with ID: bmlnykvij. Output is being written to: C:\Users\chyck\AppData\Local\Temp\claude\d--Flash-golova-KSE-AI-AAFS\57049ae5-374c-471e-8191-1ff2343b8a66\tasks\bmlnykvij.output. You will be notified when it completes. To check interim output, use Read on that file path.
Session cwd remains D:\Flash\golova\KSE_AI\AAFS; directory changes made by the backgrounded command do not apply to subsequent commands.
```

</details>

<details><summary>🔧 Bash: Save synthetic results; inspect geojson · 08:42</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; cat > reviews/scratch/stage5-leakage/mutations_syn.out <<'EOF'
(output of: python mutations.py syn, 2026-10-11)
SYN none                         corrupted_future: pass   [pass; pass; pass; pass] | known_at: pass (2s) 257; pass (2s) 230
SYN m1_window+1h                 corrupted_future: CAUGHT [CAUGHT; CAUGHT; pass; pass] | known_at: CAUGHT starts_24h (seed 0); pass (seed 1)
SYN m2_end_utc                   corrupted_future: pass   [pass; pass; pass; pass] | known_at: CAUGHT oblasts_active; CAUGHT oblasts_active
SYN m3_uncertain                 corrupted_future: CAUGHT [pass; pass; CAUGHT; CAUGHT] | known_at: CAUGHT country_starts_30m (seed 0); pass (seed 1)
SYN m4_masks_ab                  corrupted_future: CAUGHT [pass; pass; CAUGHT; CAUGHT] | known_at: CAUGHT country_starts_60m; CAUGHT country_starts_60m
SYN m5_seen_without_open_until   corrupted_future: pass   [pass; pass; pass; pass] | known_at: CAUGHT oblasts_active; CAUGHT oblasts_active
order of corrupted_future: cut 02-16 00:00 h=1, h=3; cut 02-20 13:00 h=1, h=3
EOF
python - <<'EOF'
import json
g=json.load(open('dataset_repo/example/ukr_admin2.geojson',encoding='utf-8'))
fs=g['features']; print(len(fs)); print(fs[0]['properties'])
from collections import Counter
print(Counter(f['geometry']['type'] for f in fs))
print(sorted(set(f['properties']['adm1_name'] for f in fs)))
EOF
```

**Результат** (ошибка)

```
Exit code 1
139
Traceback (most recent call last):
  File "<stdin>", line 3, in <module>
  File "D:\Soft\miniconda\Lib\encodings\cp1252.py", line 19, in encode
    return codecs.charmap_encode(input,self.errors,encoding_table)[0]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
UnicodeEncodeError: 'charmap' codec can't encode characters in position 49-63: character maps to <undefined>
```

</details>

<details><summary>🔧 Bash: Inspect geojson and oblast neighbour pairs · 08:42</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; PYTHONIOENCODING=utf-8 python - <<'EOF'
import json
from collections import Counter
g=json.load(open('dataset_repo/example/ukr_admin2.geojson',encoding='utf-8'))
fs=g['features']; print(len(fs)); print({k:v for k,v in fs[0]['properties'].items()})
print(Counter(f['geometry']['type'] for f in fs))
print(sorted(set(f['properties']['adm1_name'] for f in fs)))
nv=[sum(len(r) for p in (f['geometry']['coordinates'] if f['geometry']['type']=='MultiPolygon' else [f['geometry']['coordinates']]) for r in p) for f in fs]
print('vertices total', sum(nv), 'max', max(nv), 'min', min(nv))
import scipy; print('scipy', scipy.__version__)
EOF
PYTHONPATH=src PYTHONIOENCODING=utf-8 python -c "
import pandas as pd
n=pd.read_csv('data/neighbors.csv'); print(n.level.value_counts())
o=n[n.level=='oblast']; print(o[o.a<o.b].to_string())
"
```

**Результат**

```
139
{'adm2_name': 'Bakhchysaraiskyi', 'adm2_name1': 'Бахчисарайський', 'adm2_name2': None, 'adm2_name3': None, 'adm2_pcode': 'UA0102', 'adm1_name': 'Autonomous Republic of Crimea', 'adm1_name1': 'Автономна Республіка Крим', 'adm1_name2': None, 'adm1_name3': None, 'adm1_pcode': 'UA01', 'adm0_name': 'Ukraine', 'adm0_name1': 'Україна', 'adm0_name2': None, 'adm0_name3': None, 'adm0_pcode': 'UA', 'valid_on': '2025-09-01', 'valid_to': None, 'area_sqkm': 2381.30724866, 'version': 'v05', 'lang': 'en', 'lang1': 'uk', 'lang2': None, 'lang3': None, 'center_lat': None, 'center_lon': None}
Counter({'Polygon': 109, 'MultiPolygon': 30})
['Autonomous Republic of Crimea', 'Cherkaska', 'Chernihivska', 'Chernivetska', 'Dnipropetrovska', 'Donetska', 'Ivano-Frankivska', 'Kharkivska', 'Khersonska', 'Khmelnytska', 'Kirovohradska', 'Kyiv', 'Kyivska', 'Luhanska', 'Lvivska', 'Mykolaivska', 'Odeska', 'Poltavska', 'Rivnenska', 'Sevastopol', 'Sumska', 'Ternopilska', 'Vinnytska', 'Volynska', 'Zakarpatska', 'Zaporizka', 'Zhytomyrska']
vertices total 611152 max 13716 min 536
scipy 1.18.1
level
unit      532
oblast    100
Name: count, dtype: int64
     level                        a                        b
0   oblast         Cherkaska oblast     Kirovohradska oblast
1   oblast         Cherkaska oblast           Kyivska oblast
2   oblast         Cherkaska oblast         Poltavska oblast
3   oblast         Cherkaska oblast         Vinnytska oblast
4   oblast      Chernihivska oblast           Kyivska oblast
5   oblast      Chernihivska oblast         Poltavska oblast
6   oblast      Chernihivska oblast            Sumska oblast
7   oblast      Chernivetska oblast  Ivano-Frankivska oblast
8   oblast      Chernivetska oblast       Khmelnytska oblast
9   oblast      Chernivetska oblast       Ternopilska oblast
10  oblast      Chernivetska oblast         Vinnytska oblast
11  oblast   Dnipropetrovska oblast          Donetska oblast
12  oblast   Dnipropetrovska oblast        Kharkivska oblast
13  oblast   Dnipropetrovska oblast        Khersonska oblast
14  oblast   Dnipropetrovska oblast     Kirovohradska oblast
15  oblast   Dnipropetrovska oblast       Mykolaivska oblast
16  oblast   Dnipropetrovska oblast         Poltavska oblast
17  oblast   Dnipropetrovska oblast         Zaporizka oblast
19  oblast          Donetska oblast        Kharkivska oblast
20  oblast          Donetska oblast         Zaporizka oblast
22  oblast  Ivano-Frankivska oblast           Lvivska oblast
23  oblast  Ivano-Frankivska oblast       Ternopilska oblast
24  oblast  Ivano-Frankivska oblast       Zakarpatska oblast
27  oblast        Kharkivska oblast         Poltavska oblast
28  oblast        Kharkivska oblast            Sumska oblast
30  oblast        Khersonska oblast       Mykolaivska oblast
31  oblast        Khersonska oblast         Zaporizka oblast
33  oblast       Khmelnytska oblast         Rivnenska oblast
34  oblast       Khmelnytska oblast       Ternopilska oblas
… [обрезано: показано 3000 из 4303 символов]
```

</details>

<details><summary>🔧 Write: reviews/scratch/stage5-leakage/geo_check.py · 08:43</summary>

**Аргументы**

```
# file: reviews/scratch/stage5-leakage/geo_check.py
"""Task 3: neighbourhood. An independent criterion (vertices of two polygons within ~100 m, KD-tree)
against geo.py (>= 2 identical vertices after rounding to 1e-5). Shared border length, single-point
contacts, renamed raions, neighbours of merged units."""
import json
from collections import defaultdict
from itertools import combinations

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

import alerts.config
from alerts.geo import _our_name
from alerts.store import load_units

cfg = alerts.config.load_config()
g = cfg['geo']
fs = json.load(open(alerts.config.ROOT / g['path'], encoding='utf-8'))['features']
back = {geo: ours for ours, geo in g['renames'].items()}
names = [_our_name(f['properties']['adm1_name'], f['properties']['adm2_name'], back) for f in fs]

pts, owner, rings = [], [], []
for i, f in enumerate(fs):
    geom = f['geometry']
    polys = geom['coordinates'] if geom['type'] == 'MultiPolygon' else [geom['coordinates']]
    for poly in polys:
        for r in poly:
            a = np.asarray(r, dtype=float)
            rings.append((i, a))
            pts.append(a); owner.append(np.full(len(a), i))
P = np.vstack(pts); O = np.concatenate(owner)
lat0 = np.deg2rad(48.5)
XY = np.c_[P[:, 0] * 111.32 * np.cos(lat0), P[:, 1] * 110.57]          # km, local equirectangular

# exact (geo.py rule)
vo = defaultdict(set)
for (x, y), i in zip(np.round(P, g['vertex_decimals']), O):
    vo[(x, y)].add(int(i))
exact = defaultdict(int)
for s in vo.values():
    for a, b in combinations(sorted(s), 2):
        exact[(a, b)] += 1

# shared border length: segments whose both ends are vertices shared by the same pair
key = lambda p: (round(p[0], g['vertex_decimals']), round(p[1], g['vertex_decimals']))  # noqa: E731
shared_km = defaultdict(float)
for i, a in rings:
    for p, q in zip(a[:-1], a[1:]):
        common = (vo[key(p)] & vo[key(q)]) - {i}
        if common:
            d = np.hypot((p[0] - q
… [обрезано: показано 2000 из 4990 символов]
```

**Результат**

```
File created successfully at: D:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage5-leakage\geo_check.py (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Bash: Independent neighbourhood check from boundaries · 08:43</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; time PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage5-leakage/geo_check.py
```

**Результат**

```
pairs with any exact shared vertex: 347  with exactly one: 0
geo.py pairs (>=2 exact): 347
pairs within 100 m but not geo.py neighbours:
                                                              a                                       b  exact  near100m  shared_km  geo_py
115  (Autonomous Republic of Crimea oblast, Dzhankoiskyi raion)  (Khersonska oblast, Henicheskyi raion)      0         8        0.0   False
geo.py pairs with the shortest shared border:
                                                             a                                                   b  exact  near100m  shared_km  geo_py
30   (Autonomous Republic of Crimea oblast, Kerchenskyi raion)              (Khersonska oblast, Henicheskyi raion)      4         8       0.71    True
250                    (Zakarpatska oblast, Tiachivskyi raion)  (Ivano-Frankivska oblast, Ivano-Frankivskyi raion)      8        18       0.87    True
31                      (Poltavska oblast, Myrhorodskyi raion)                   (Sumska oblast, Okhtyrskyi raion)      4        10       1.36    True
65                     (Zaporizka oblast, Melitopolskyi raion)               (Khersonska oblast, Kakhovskyi raion)      4        11       1.57    True
337                (Dnipropetrovska oblast, Nikopolskyi raion)               (Khersonska oblast, Kakhovskyi raion)      7        16       2.29    True
170                 (Dnipropetrovska oblast, Kamianskyi raion)            (Poltavska oblast, Kremenchutskyi raion)     19        39       3.71    True
342                        (Donetska oblast, Horlivskyi raion)          (Luhanska oblast, Siverskodonetskyi raion)     31        73       3.92    True
224                           (Volynska oblast, Lutskyi raion)                (Lvivska oblast, Zolochivskyi raion)     20        57       4.55    True
266  (Autonomous Republic of Crimea oblast, Perekopskyi raion)               (Khersonska oblast, Kakhovskyi raion)      9        18       4.64    True
119                         (Rivnenska oblast, Varaskyi raion)                (Rivnenska oblast, Rivnenskyi raion)     26        60       5.05    True
154                      (Vinnytska oblast, Zhmerynskyi raion)     (Khmelnytska oblast, Kamianets-Podilskyi raion)     37        83       5.05    True
297                   (Zhytomyrska oblast, Korostenskyi raion)                  (Kyivska oblast, Buchanskyi raion)    224       455       6.10    True
unit pairs: recomputed 532 neighbors.csv 532 equal True
neighbours per unit: min 2 max 9
U001 Berdianskyi raion + Melitopolskyi raion + Polohivskyi raion + Vasylivskyi raion + Zaporizkyi raion -> ['Dniprovskyi raion', 'Donetska oblast', 'Henicheskyi raion + Kakhovskyi raion + Skadovskyi raion', 'Nikopolskyi raion', 'Synelnykivskyi raion']
U025 Henicheskyi raion + Kakhovskyi raion + Skadovskyi raion -> ['Berdianskyi raion + Melitopolskyi raion + Polohivskyi raion + Vasylivskyi raion + Zaporizkyi raion', 'Beryslavskyi raion', 'Khersonskyi raion', '
… [обрезано: показано 3000 из 5478 символов]
```

</details>

<details><summary>🔧 Bash: List unmatched Kyiv oblast polygons · 08:45</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; PYTHONPATH=src PYTHONIOENCODING=utf-8 python - <<'EOF'
import json, alerts.config
from alerts.geo import _our_name
from alerts.store import load_units
cfg=alerts.config.load_config(); g=cfg['geo']
fs=json.load(open(alerts.config.ROOT/g['path'],encoding='utf-8'))['features']
back={v:k for k,v in g['renames'].items()}
names=[_our_name(f['properties']['adm1_name'],f['properties']['adm2_name'],back) for f in fs]
u=load_units(cfg); key=set(zip(u.oblast,u.raion))
print([n for n in names if n not in key and n[0] not in ('Autonomous Republic of Crimea oblast','Luhanska oblast','Sevastopol oblast')])
print(sorted(u[u.oblast=='Kyivska oblast'].raion))
print(len(u), u.unit_id.nunique())
EOF
```

**Результат**

```
[('Kyivska oblast', 'Chornobyl Exclusion Zone raion')]
['Bilotserkivskyi raion', 'Boryspilskyi raion', 'Brovarskyi raion', 'Buchanskyi raion', 'Fastivskyi raion', 'Obukhivskyi raion', 'Vyshhorodskyi raion']
119 105
```

</details>

<details><summary>🔧 Bash: Show Chornobyl zone and Vyshhorod neighbours · 08:45</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; PYTHONIOENCODING=utf-8 python -c "
import pandas as pd
t=pd.read_csv('reviews/scratch/stage5-leakage/geo_pairs.csv')
z=t[t.a.str.contains('Chornobyl')|t.b.str.contains('Chornobyl')]
print(z.to_string())
v=t[(t.a.str.contains('Vyshhorod')|t.b.str.contains('Vyshhorod'))&t.geo_py]
print(v[['a','b','shared_km']].to_string())
"
```

**Результат**

```
a                                                     b  exact  near100m  shared_km  geo_py    ua    ub
153  ('Kyivska oblast', 'Chornobyl Exclusion Zone raion')             ('Kyivska oblast', 'Vyshhorodskyi raion')   3079      6161     224.07    True   NaN  U095
175          ('Zhytomyrska oblast', 'Korostenskyi raion')  ('Kyivska oblast', 'Chornobyl Exclusion Zone raion')    185       377      57.76    True  U042   NaN
181  ('Kyivska oblast', 'Chornobyl Exclusion Zone raion')        ('Chernihivska oblast', 'Chernihivskyi raion')    158       321      31.45    True   NaN  U014
                                                        a                                               b  shared_km
120             ('Kyivska oblast', 'Vyshhorodskyi raion')  ('Chernihivska oblast', 'Chernihivskyi raion')     109.62
153  ('Kyivska oblast', 'Chornobyl Exclusion Zone raion')       ('Kyivska oblast', 'Vyshhorodskyi raion')     224.07
162          ('Zhytomyrska oblast', 'Korostenskyi raion')       ('Kyivska oblast', 'Vyshhorodskyi raion')      74.21
204                ('Kyivska oblast', 'Brovarskyi raion')       ('Kyivska oblast', 'Vyshhorodskyi raion')      54.73
317                ('Kyivska oblast', 'Buchanskyi raion')       ('Kyivska oblast', 'Vyshhorodskyi raion')     115.59
332             ('Kyivska oblast', 'Vyshhorodskyi raion')                      ('Kyiv City', 'Kyiv City')      21.71
```

</details>

<details><summary>🔧 Write: reviews/scratch/stage5-leakage/neighbor_lead.py · 08:45</summary>

**Аргументы**

```
# file: reviews/scratch/stage5-leakage/neighbor_lead.py
"""Task 6: do neighbours lead? For every episode start of a target unit, the lag to the latest episode start
of a neighbouring unit at or before it; and at the hourly grid, what neighbour features add over the
unit's own state."""
import pickle
from pathlib import Path

import numpy as np
import pandas as pd

from alerts.timeutil import to_sec

HERE = Path(__file__).resolve().parent
D = pickle.load(open(HERE / 'art.pkl', 'rb')); art, feat = D['art'], D['feat']
units = art.units
tgt = set(units.loc[units.role == 'target', 'unit_id'])
ep = art.intervals.groupby('episode').agg(unit_id=('unit_id', 'first'), s=('start_utc', 'min'))
st = {u: np.sort(to_sec(g['s'])) for u, g in ep.groupby('unit_id')}
nb = art.neighbors[art.neighbors.level == 'unit'].groupby('a')['b'].apply(list).to_dict()
ob = units.drop_duplicates('unit_id').set_index('unit_id')['oblast']
same_ob = {u: [v for v in ob.index if ob[v] == ob[u] and v != u] for u in ob.index}
alls = np.sort(np.concatenate([st[u] for u in st]))

def lags(u, others):
    """seconds from the latest start of `others` at or before each start of u (inf if none)"""
    s = st[u]
    pool = np.sort(np.concatenate([st[v] for v in others if v in st])) if others else np.zeros(0)
    k = np.searchsorted(pool, s, side='right') - 1
    return np.where(k >= 0, s - pool[np.maximum(k, 0)], np.inf)

rows = []
for u in sorted(tgt):
    for name, others in [('neighbour units', nb.get(u, [])), ('same oblast', same_ob[u]),
                         ('any other unit', [v for v in st if v != u])]:
        lg = lags(u, others)
        rows.append(pd.DataFrame({'unit': u, 'group': name, 'lag': lg}))
L = pd.concat(rows)
bins = [-1, 60, 5 * 60, 15 * 60, 60 * 60, 3 * 3600, np.inf]
labels = ['<=1 min (same post)', '1-5 min', '5-15 min', '15-60 min', '1-3 h', '>3 h / none']
L['cls'] = pd.cut(L['lag'], bins=bins, labels=labels)
print('target-unit episode starts:', int((L.group == 'any other unit').sum())
… [обрезано: показано 2000 из 3500 символов]
```

**Результат**

```
File created successfully at: D:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage5-leakage\neighbor_lead.py (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Bash: Analyze neighbour lead times and features · 08:45</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage5-leakage/neighbor_lead.py 2>&1 | tee reviews/scratch/stage5-leakage/neighbor_lead.out; echo; cat reviews/scratch/stage5-leakage/mutations_real.out
```

**Результат**

```
Traceback (most recent call last):
  File "D:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage5-leakage\neighbor_lead.py", line 34, in <module>
    lg = lags(u, others)
         ^^^^^^^^^^^^^^^
  File "D:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage5-leakage\neighbor_lead.py", line 28, in lags
    return np.where(k >= 0, s - pool[np.maximum(k, 0)], np.inf)
                                ~~~~^^^^^^^^^^^^^^^^^^
IndexError: index 0 is out of bounds for axis 0 with size 0

REAL 2026-08-21T14:00:00Z none                         corrupted_future: pass (28s) 592629 | known_at: pass (25s) 14715
REAL 2026-08-21T14:00:00Z m1_window+1h                 corrupted_future: CAUGHT (28s) features and forecasts at the cut.iloc[:, 3] (column name="starts_24h") are different | known_at: CAUGHT (22s) features known at 2026-08-21 14:00:00+00:00.iloc[:, 2] (column name="starts_24h") are different
REAL 2026-08-21T14:00:00Z m2_end_utc                   corrupted_future: pass (27s) 592629 | known_at: pass (18s) 14715
REAL 2026-08-21T14:00:00Z m3_uncertain                 corrupted_future: CAUGHT (32s) training rows, labels and features.iloc[:, 12] (column name="country_starts_30m") are different | known_at: pass (20s) 14715
```

</details>

<details><summary>🔧 Bash: Rerun neighbour lead analysis · 08:46</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; python - <<'EOF'
p='reviews/scratch/stage5-leakage/neighbor_lead.py'
s=open(p,encoding='utf-8').read()
s=s.replace("""    k = np.searchsorted(pool, s, side='right') - 1""","""    if len(pool) == 0:
        return np.full(len(s), np.inf)
    k = np.searchsorted(pool, s, side='right') - 1""")
open(p,'w',encoding='utf-8').write(s)
EOF
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage5-leakage/neighbor_lead.py 2>&1 | tee reviews/scratch/stage5-leakage/neighbor_lead.out
```

**Результат**

```
target-unit episode starts: 66078
Traceback (most recent call last):
  File "D:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage5-leakage\neighbor_lead.py", line 43, in <module>
    print(pd.crosstab(L['group'], L['cls'], normalize='index').round(3).to_string())
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\Soft\miniconda\Lib\site-packages\pandas\core\reshape\pivot.py", line 1099, in crosstab
    df = DataFrame(data, index=common_idx)
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\Soft\miniconda\Lib\site-packages\pandas\core\frame.py", line 769, in __init__
    mgr = dict_to_mgr(data, index, columns, dtype=dtype, copy=copy)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\Soft\miniconda\Lib\site-packages\pandas\core\internals\construction.py", line 460, in dict_to_mgr
    return arrays_to_mgr(arrays, columns, index, dtype=dtype, consolidate=copy)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\Soft\miniconda\Lib\site-packages\pandas\core\internals\construction.py", line 118, in arrays_to_mgr
    arrays, refs = _homogenize(arrays, index, dtype)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\Soft\miniconda\Lib\site-packages\pandas\core\internals\construction.py", line 568, in _homogenize
    val = val.reindex(index)
          ^^^^^^^^^^^^^^^^^^
  File "D:\Soft\miniconda\Lib\site-packages\pandas\core\series.py", line 5525, in reindex
    return super().reindex(
           ^^^^^^^^^^^^^^^^
  File "D:\Soft\miniconda\Lib\site-packages\pandas\core\generic.py", line 5464, in reindex
    return self._reindex_axes(
           ^^^^^^^^^^^^^^^^^^^
  File "D:\Soft\miniconda\Lib\site-packages\pandas\core\generic.py", line 5486, in _reindex_axes
    new_index, indexer = ax.reindex(
                         ^^^^^^^^^^^
  File "D:\Soft\miniconda\Lib\site-packages\pandas\core\indexes\base.py", line 4253, in reindex
    raise ValueError("cannot reindex on an axis with duplicate labels")
ValueError: cannot reindex on an axis with duplicate labels
```

</details>

<details><summary>🔧 Bash: Fix concat index and rerun lead analysis · 08:46</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; sed -i "s/^L = pd.concat(rows)$/L = pd.concat(rows, ignore_index=True)/" reviews/scratch/stage5-leakage/neighbor_lead.py; PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage5-leakage/neighbor_lead.py 2>&1 | tee reviews/scratch/stage5-leakage/neighbor_lead.out
```

**Результат**

```
target-unit episode starts: 66078
cls              <=1 min (same post)  1-5 min  5-15 min  15-60 min  1-3 h  >3 h / none
group                                                                                 
any other unit                 0.581    0.130     0.162      0.116  0.011        0.000
neighbour units                0.513    0.045     0.089      0.157  0.131        0.065
same oblast                    0.490    0.030     0.069      0.141  0.140        0.130
neighbor_starts_60m: share of rows > 0 = 0.149; P(y1=1 | >0) = 0.241, P(y1=1 | 0) = 0.069; share of positives (y1=1) with >0: 0.381
oblast_starts_60m: share of rows > 0 = 0.123; P(y1=1 | >0) = 0.257, P(y1=1 | 0) = 0.072; share of positives (y1=1) with >0: 0.334
country_starts_60m: share of rows > 0 = 0.944; P(y1=1 | >0) = 0.096, P(y1=1 | 0) = 0.068; share of positives (y1=1) with >0: 0.960
neighbor_units_active_share: share > 0 = 0.176; P(y1|>0) = 0.259; P(y1|0) = 0.059
neighbor_oblasts_active_share: share > 0 = 0.419; P(y1|>0) = 0.184; P(y1|0) = 0.030
oblast_active_share: share > 0 = 0.143; P(y1|>0) = 0.269; P(y1|0) = 0.065
units with >=30 rows having a neighbour start in the last hour: 104; median within-unit lift of P(y1=1): 2.50 [IQR 1.53-9.85]
```

</details>

<details><summary>🔧 Bash: Read metrics score function · 08:46</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; sed -n 1,40p src/alerts/metrics.py
```

**Результат**

```
"""Metrics, day-block bootstrap and calibration (PLAN stage 4, D18).

Units are strongly correlated within a moment (waves), so rows are not independent: the bootstrap
resamples whole forecast days with replacement. The same day draws are used for every model,
which gives paired confidence intervals for differences between models.

PR-AUC and ROC-AUC are computed here with one sort per call and exact handling of tied scores
(baselines produce many ties); tests check them against scikit-learn.
"""
import numpy as np
import pandas as pd

EPS = 1e-6
METRICS = ['pr_auc', 'roc_auc', 'brier', 'log_loss']
HIGHER_IS_BETTER = {'pr_auc': True, 'roc_auc': True, 'brier': False, 'log_loss': False}


def score(y: np.ndarray, p: np.ndarray) -> dict:
    y = np.asarray(y, dtype=float)
    p = np.clip(np.asarray(p, dtype=float), EPS, 1 - EPS)
    out = {'brier': float(np.mean((p - y) ** 2)),
           'log_loss': float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))}
    n_pos = y.sum()
    n_neg = len(y) - n_pos
    if n_pos == 0 or n_neg == 0:
        return {'pr_auc': np.nan, 'roc_auc': np.nan, **out}
    values, inverse, counts = np.unique(p, return_inverse=True, return_counts=True)   # ascending
    pos = np.bincount(inverse, weights=y, minlength=len(values))
    # ROC-AUC from average ranks (Mann-Whitney U)
    avg_rank = np.cumsum(counts) - (counts - 1) / 2
    out['roc_auc'] = float(((avg_rank * pos).sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg))
    # PR-AUC as average precision over distinct thresholds, highest score first
    tp = np.cumsum(pos[::-1])
    seen = np.cumsum(counts[::-1])
    recall_step = pos[::-1] / n_pos
    out['pr_auc'] = float((recall_step * tp / seen).sum())
    return {k: out[k] for k in METRICS}


def bootstrap(preds: pd.DataFrame, models: list, n_reps: int, seed: int, ci: float = 0.95,
```

</details>

<details><summary>🔧 Bash: Run validation ablation of neighbour features · 08:46</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; cat > reviews/scratch/stage5-leakage/ablation_val.py <<'EOF'
"""Task 6 (supporting): does the neighbour/oblast group add information given the rest? Validation only
(fit on t <= train_end - h, score on the validation rows), tuned LightGBM params of D20, threads = 2.
Dropping a feature = setting it to NaN (LightGBM then never splits on it)."""
import copy, json, pickle, logging
from pathlib import Path
import numpy as np, pandas as pd
import alerts.config
from alerts.pipeline import model_data
from alerts.models.learned import GBMModel
from alerts.metrics import score
logging.disable(logging.WARNING)
HERE = Path(__file__).resolve().parent
cfg = copy.deepcopy(alerts.config.load_config()); cfg['models']['threads'] = 2
art = pickle.load(open(HERE / 'art.pkl', 'rb'))['art']
data = model_data(art, cfg)
te = alerts.config.ts(cfg['periods']['train_end'])
NB = ['neighbor_oblasts_active_share', 'neighbor_units_active_share', 'neighbor_starts_60m']
OB = ['oblast_active_share', 'oblast_starts_30m', 'oblast_starts_60m']
for h in [1, 3]:
    p = json.load(open(f'reports/tuning_h{h}.json'))['LGBM']
    y = f'y_{h}'
    tr = data[(data['t'] <= te - pd.Timedelta(hours=h)) & data[y].notna()]
    va = data[(data['part'] == 'val') & data[y].notna()]
    for name, drop in [('all features', []), ('minus neighbours', NB), ('minus neighbours+oblast', NB + OB),
                       ('minus neighbour units only', NB[1:])]:
        X, V = tr.copy(), va.copy()
        X[drop] = np.nan; V[drop] = np.nan
        m = GBMModel(cfg, p).fit(X, X[y].to_numpy(dtype=float))
        s = score(V[y].to_numpy(dtype=float), m.predict_proba(V))
        gi = m.gain_importance() if not drop else None
        print(f'h={h} {name:28s} val PR-AUC {s["pr_auc"]:.4f} log loss {s["log_loss"]:.4f}', flush=True)
        if gi is not None:
            print('   gain:', gi.loc[NB + OB].round(4).to_dict())
EOF
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage5-leakage/abl
… [обрезано: показано 2000 из 2067 символов]
```

**Результат**

```
Command running in background with ID: bwwvqe3s9. Output is being written to: C:\Users\chyck\AppData\Local\Temp\claude\d--Flash-golova-KSE-AI-AAFS\57049ae5-374c-471e-8191-1ff2343b8a66\tasks\bwwvqe3s9.output. You will be notified when it completes. To check interim output, use Read on that file path.
Session cwd remains D:\Flash\golova\KSE_AI\AAFS; directory changes made by the backgrounded command do not apply to subsequent commands.
```

</details>

<details><summary>🔧 Bash: Prepare starts_7d scaling sensitivity script · 08:47</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; cat > reviews/scratch/stage5-leakage/scaling_sens.py <<'EOF'
"""Task 2 (supporting): effect of the starts_7d scaling on post-outage forecasts. Reviewer's sensitivity
check only (no selection): for test days 09-03..09-06 fit LightGBM exactly as the backtest does
(t <= D - h, D20 params, threads = 2) and predict the post-outage rows with the project's scaled
starts_7d and with the raw (unscaled) count."""
import copy, json, pickle, logging
from pathlib import Path
import numpy as np, pandas as pd
import alerts.config
from alerts.pipeline import model_data, alert_history
from alerts.models.learned import GBMModel
from alerts.metrics import score
from alerts.timeutil import to_sec
logging.disable(logging.WARNING)
HERE = Path(__file__).resolve().parent
cfg = copy.deepcopy(alerts.config.load_config()); cfg['models']['threads'] = 2
art = pickle.load(open(HERE / 'art.pkl', 'rb'))['art']
data = model_data(art, cfg)
hist = alert_history(art)
T = pd.DatetimeIndex(np.sort(data['t'].unique()))
ti = np.searchsorted(to_sec(T), to_sec(data['t']))
col = {u: j for j, u in enumerate(hist.unit_ids)}
raw = hist.starts(T, pd.Timedelta(days=7))[ti, data['unit_id'].map(col).to_numpy()].astype('float32')
h = 3; y = f'y_{h}'
p = json.load(open(f'reports/tuning_h{h}.json'))['LGBM']
pred = pd.read_parquet(f'data/predictions_h{h}.parquet')
res = []
for day in pd.date_range('2026-09-03', '2026-09-06', freq='D', tz='UTC'):
    tr = data[(data['t'] <= day - pd.Timedelta(hours=h)) & data[y].notna()]
    te = data[(data['t'] >= day) & (data['t'] < day + pd.Timedelta(days=1)) & data[y].notna()]
    m = GBMModel(cfg, p).fit(tr, tr[y].to_numpy(dtype=float))
    a = m.predict_proba(te)
    te2 = te.copy(); te2['starts_7d'] = raw[data.index.get_indexer(te.index)]
    b = m.predict_proba(te2)
    res.append(pd.DataFrame({'t': te['t'], 'y': te[y].astype(float), 'p_scaled': a, 'p_raw': b}, index=te.index))
    print(day.date(), len(te), flush=True)
r = pd.concat(res)
pp = pre
… [обрезано: показано 2000 из 2422 символов]
```

**Результат**

```
ok
```

</details>

<details><summary>🔧 Bash: Check background job outputs · 08:47</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; cat reviews/scratch/stage5-leakage/mutations_real.out; echo ---; cat reviews/scratch/stage5-leakage/ablation_val.out
```

**Результат**

```
REAL 2026-08-21T14:00:00Z none                         corrupted_future: pass (28s) 592629 | known_at: pass (25s) 14715
REAL 2026-08-21T14:00:00Z m1_window+1h                 corrupted_future: CAUGHT (28s) features and forecasts at the cut.iloc[:, 3] (column name="starts_24h") are different | known_at: CAUGHT (22s) features known at 2026-08-21 14:00:00+00:00.iloc[:, 2] (column name="starts_24h") are different
REAL 2026-08-21T14:00:00Z m2_end_utc                   corrupted_future: pass (27s) 592629 | known_at: pass (18s) 14715
REAL 2026-08-21T14:00:00Z m3_uncertain                 corrupted_future: CAUGHT (32s) training rows, labels and features.iloc[:, 12] (column name="country_starts_30m") are different | known_at: pass (20s) 14715
REAL 2026-08-21T14:00:00Z m4_masks_ab                  corrupted_future: CAUGHT (29s) training rows, labels and features.iloc[:, 13] (column name="country_starts_60m") are different | known_at: pass (23s) 14715
REAL 2026-08-21T14:00:00Z m5_seen_without_open_until   corrupted_future: pass (33s) 592629 | known_at: pass (24s) 14715
---
h=1 all features                 val PR-AUC 0.4211 log loss 0.2788
   gain: {'neighbor_oblasts_active_share': 0.2204, 'neighbor_units_active_share': 0.0179, 'neighbor_starts_60m': 0.0078, 'oblast_active_share': 0.0101, 'oblast_starts_30m': 0.0011, 'oblast_starts_60m': 0.0004}
h=1 minus neighbours             val PR-AUC 0.4183 log loss 0.2793
h=1 minus neighbours+oblast      val PR-AUC 0.4149 log loss 0.2807
h=1 minus neighbour units only   val PR-AUC 0.4233 log loss 0.2784
h=3 all features                 val PR-AUC 0.6924 log loss 0.3867
   gain: {'neighbor_oblasts_active_share': 0.0789, 'neighbor_units_active_share': 0.007, 'neighbor_starts_60m': 0.0006, 'oblast_active_share': 0.0047, 'oblast_starts_30m': 0.0005, 'oblast_starts_60m': 0.0006}
h=3 minus neighbours             val PR-AUC 0.6890 log loss 0.3881
h=3 minus neighbours+oblast      val PR-AUC 0.6878 log loss 0.3886
h=3 minus neighbour units only   val PR-AUC 0.6918 log loss 0.3868
```

</details>

<details><summary>🔔 Уведомление: Background command "Run validation ablation of neighbour features" completed (exit code 0) · 08:47</summary>

```
<task-notification>
<task-id>bwwvqe3s9</task-id>
<tool-use-id>toolu_01MzNd5vFrz5CWnEMs3c6tLd</tool-use-id>
<output-file>C:\Users\chyck\AppData\Local\Temp\claude\d--Flash-golova-KSE-AI-AAFS\57049ae5-374c-471e-8191-1ff2343b8a66\tasks\bwwvqe3s9.output</output-file>
<status>completed</status>
<summary>Background command "Run validation ablation of neighbour features" completed (exit code 0)</summary>
</task-notification>
```

</details>

<details><summary>🔧 Bash: Run starts_7d scaling sensitivity check · 08:47</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage5-leakage/scaling_sens.py > reviews/scratch/stage5-leakage/scaling_sens.out 2>&1
```

**Результат**

```
Command running in background with ID: b8wrphola. Output is being written to: C:\Users\chyck\AppData\Local\Temp\claude\d--Flash-golova-KSE-AI-AAFS\57049ae5-374c-471e-8191-1ff2343b8a66\tasks\b8wrphola.output. You will be notified when it completes. To check interim output, use Read on that file path.
Session cwd remains D:\Flash\golova\KSE_AI\AAFS; directory changes made by the backgrounded command do not apply to subsequent commands.
```

</details>

<details><summary>🔧 Bash: Prepare disk-read mutation script · 08:47</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; cat > reviews/scratch/stage5-leakage/mutation_disk.py <<'EOF'
"""m6: the same leak as m2 (state from recorded end_utc), but the feature reads data/intervals.csv from
disk through store + cfg instead of the history it was given. Both checks rebuild from df, the file on
disk is the same in both versions."""
import pickle, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import mutations as M
from alerts import store
from alerts.history import AlertHistory
import alerts.config
cfg = alerts.config.load_config()
art = pickle.load(open(Path(__file__).resolve().parent / 'art.pkl', 'rb'))['art']
disk_iv = store.load_intervals(cfg)

def ah_disk(a):
    seg = disk_iv.rename(columns={'start_utc': 'start', 'end_utc': 'end'})[['unit_id', 'start', 'end']]
    return AlertHistory(seg, a.intervals, a.units['unit_id'].drop_duplicates().tolist(), a.masks)

M.P.alert_history = ah_disk; M.L.alert_history = ah_disk
M.FeatureBuilder.build = M.ORIG_BUILD
models = M.registry(cfg, ['B0'])
for cut in sys.argv[1:]:
    c = M.run('c', lambda: M.L.check(art.df, cfg, alerts.config.ts(cut), 3, models)['training_rows'])
    k = M.run('k', lambda: M.L.knowledge_check(art.df, cfg, alerts.config.ts(cut))['rows'])
    print(f'REAL {cut} m6_end_utc_from_disk corrupted_future: {c} | known_at: {k}', flush=True)
EOF
echo ok
```

**Результат**

```
ok
```

</details>

<details><summary>🔧 Bash: Wait and check job progress · 08:48</summary>

**Аргументы**

```bash
sleep 60; cd /d/Flash/golova/KSE_AI/AAFS; cat reviews/scratch/stage5-leakage/mutations_real.out | tail -6; cat reviews/scratch/stage5-leakage/scaling_sens.out
```

**Результат** (ошибка)

```
<tool_use_error>Blocked: sleep 60 followed by: cd /d/Flash/golova/KSE_AI/AAFS cat reviews/scratch/stage5-leakage/mutations_real.out tail -6 cat reviews/scratch/stage5-leakage/scaling_sens.out. To wait for a condition, use Monitor with an until-loop (e.g. `until <check>; do sleep 2; done`). To wait for a command you started, use run_in_background: true. Do not chain shorter sleeps to work around this block.</tool_use_error>
```

</details>

<details><summary>🔔 Уведомление: Background command "Run starts_7d scaling sensitivity check" completed (exit code 0) · 08:48</summary>

```
<task-notification>
<task-id>b8wrphola</task-id>
<tool-use-id>toolu_01K8BW1v5hCtgtByyUvS7MTZ</tool-use-id>
<output-file>C:\Users\chyck\AppData\Local\Temp\claude\d--Flash-golova-KSE-AI-AAFS\57049ae5-374c-471e-8191-1ff2343b8a66\tasks\b8wrphola.output</output-file>
<status>completed</status>
<summary>Background command "Run starts_7d scaling sensitivity check" completed (exit code 0)</summary>
</task-notification>
```

</details>

<details><summary>🔧 Bash: Show scaling and mutation outputs · 08:48</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; cat reviews/scratch/stage5-leakage/scaling_sens.out; echo ---; cat reviews/scratch/stage5-leakage/mutations_real.out | tail -6
```

**Результат**

```
2026-09-03 821
2026-09-04 1959
2026-09-05 1970
2026-09-06 2020
max |p_scaled - parquet p_LGBM| (8 vs 2 threads): 0.0
p_scaled: rows 6770 mean p 0.304 (y 0.286) PR-AUC 0.7231 log loss 0.3749
p_raw: rows 6770 mean p 0.252 (y 0.286) PR-AUC 0.7113 log loss 0.3902
---
REAL 2026-08-21T14:00:00Z m1_window+1h                 corrupted_future: CAUGHT (28s) features and forecasts at the cut.iloc[:, 3] (column name="starts_24h") are different | known_at: CAUGHT (22s) features known at 2026-08-21 14:00:00+00:00.iloc[:, 2] (column name="starts_24h") are different
REAL 2026-08-21T14:00:00Z m2_end_utc                   corrupted_future: pass (27s) 592629 | known_at: pass (18s) 14715
REAL 2026-08-21T14:00:00Z m3_uncertain                 corrupted_future: CAUGHT (32s) training rows, labels and features.iloc[:, 12] (column name="country_starts_30m") are different | known_at: pass (20s) 14715
REAL 2026-08-21T14:00:00Z m4_masks_ab                  corrupted_future: CAUGHT (29s) training rows, labels and features.iloc[:, 13] (column name="country_starts_60m") are different | known_at: pass (23s) 14715
REAL 2026-08-21T14:00:00Z m5_seen_without_open_until   corrupted_future: pass (33s) 592629 | known_at: pass (24s) 14715
REAL 2026-08-03T04:00:00Z none                         corrupted_future: pass (34s) 554237 | known_at: pass (24s) 14371
```

</details>

<details><summary>🔧 Bash: Run disk-read mutation at pending cut · 08:48</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage5-leakage/mutation_disk.py 2026-08-03T04:00:00Z > reviews/scratch/stage5-leakage/mutation_disk.out 2>&1
```

**Результат**

```
Command running in background with ID: b8mm5ijlj. Output is being written to: C:\Users\chyck\AppData\Local\Temp\claude\d--Flash-golova-KSE-AI-AAFS\57049ae5-374c-471e-8191-1ff2343b8a66\tasks\b8mm5ijlj.output. You will be notified when it completes. To check interim output, use Read on that file path.
Session cwd remains D:\Flash\golova\KSE_AI\AAFS; directory changes made by the backgrounded command do not apply to subsequent commands.
```

</details>

<details><summary>🔧 Monitor: Wait for mutation runs to finish · 08:48</summary>

**Аргументы**

```json
{
 "command": "cd /d/Flash/golova/KSE_AI/AAFS; until [ $(grep -c \"2026-08-03\" reviews/scratch/stage5-leakage/mutations_real.out) -ge 6 ] && [ -s reviews/scratch/stage5-leakage/mutation_disk.out ]; do sleep 5; done; echo done",
 "description": "Wait for mutation runs to finish",
 "timeout": "900000"
}
```

**Результат**

```
Monitor started (task bvqf8vltj, expires in 5m unless the source ends first; you get one notice at expiry — re-arm if you still need the watch). You will be notified on each event. Keep working — do not poll or sleep. Events may arrive while you are waiting for the user — an event is not their reply.
```

</details>

<details><summary>🔧 Bash: Show interim mutation results · 08:49</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; cat reviews/scratch/stage5-leakage/mutations_real.out | grep 2026-08-03; cat reviews/scratch/stage5-leakage/mutation_disk.out
```

**Результат**

```
REAL 2026-08-03T04:00:00Z none                         corrupted_future: pass (34s) 554237 | known_at: pass (24s) 14371
```

</details>

<details><summary>🔧 Monitor: Wait for mutation runs to finish · 08:49</summary>

**Аргументы**

```json
{
 "command": "cd /d/Flash/golova/KSE_AI/AAFS; until [ $(grep -c \"2026-08-03\" reviews/scratch/stage5-leakage/mutations_real.out) -ge 6 ] && [ -s reviews/scratch/stage5-leakage/mutation_disk.out ]; do sleep 5; done; echo done",
 "description": "Wait for mutation runs to finish",
 "timeout": "900000"
}
```

**Результат**

```
Monitor started (task br538yntl, expires in 5m unless the source ends first; you get one notice at expiry — re-arm if you still need the watch). You will be notified on each event. Keep working — do not poll or sleep. Events may arrive while you are waiting for the user — an event is not their reply.
```

</details>

<details><summary>🔧 Bash: Locate outage start mentions in docs · 08:49</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; grep -n "05:55:28\|4.3 доб\|4\.3 суток\|7 ч 52" DECISIONS.md README.md PLAN.md reports/*.md | head; grep -n "subst\|підмін" README.md
```

**Результат**

```
DECISIONS.md:333:- С **2026-08-29 05:55:28 UTC по 2026-09-02 13:48:04 UTC (4 дня 7 ч 52 мин)** в файле нет ни одного события — ни начала, ни конца — ни на каком уровне и ни в какой области. Начал тревог по суткам: 27.08 — 558, 28.08 — 598, 29.08 — 88, 30.08–01.09 — 0, 02.09 — 241. Медиана рабочего периода — 298 в сутки. Второй по длине перерыв между событиями за весь период — 3 ч 43 мин.
DECISIONS.md:666:| Перерывы канала (D15) | 2026-08-29 05:55:28 → 2026-09-02 13:48:04 UTC |
DECISIONS.md:690:| 13 | Перерыв канала 29.08–02.09 (4.3 суток) внутри теста не замечен. Его след — «тревоги по 4.7 суток» с 28.08 — описан в D10 как «пачки, похоже на артефакт», без поиска причины | Все агенты этапа 1, ассистент планирования | Ревью этапа 2 (Claude Code): поиск самой длинной паузы между событиями по всему файлу, затем история коммитов датасета (`last_processed_id` 334744 → 334745 → 335351); подтверждено пользователем | D15, правило маски (г) |
README.md:54:- **з 29 серпня по 2 вересня канал мовчав 4.3 доби** (знайдено під час рев'ю, D15). Цю перерву
reports/stage1_summary.md:16:| channel outages (D15) | 2026-08-29 05:55:28 -> 2026-09-02 13:48:04 | 2026-08-29 05:55:28 -> 2026-09-02 13:48:04 | ok |
reports/stage2_summary.md:30:- 2026-08-29 05:55:28+00:00 -> 2026-09-02 13:48:04+00:00 (4 days 07:52:36)
83:  і в тестах на синтетиці; кожну перевірено підміною з витоком.
```

</details>

<details><summary>🔧 Monitor: Wait for mutation runs and print results · 08:49</summary>

**Аргументы**

```json
{
 "command": "cd /d/Flash/golova/KSE_AI/AAFS; until [ $(grep -c \"2026-08-03\" reviews/scratch/stage5-leakage/mutations_real.out) -ge 6 ] && [ -s reviews/scratch/stage5-leakage/mutation_disk.out ]; do sleep 5; done; cat reviews/scratch/stage5-leakage/mutations_real.out | grep 2026-08-03; cat reviews/scratch/stage5-leakage/mutation_disk.out",
 "description": "Wait for mutation runs and print results",
 "timeout": "900000"
}
```

**Результат**

```
Monitor started (task bqwbd0zwq, expires in 5m unless the source ends first; you get one notice at expiry — re-arm if you still need the watch). You will be notified on each event. Keep working — do not poll or sleep. Events may arrive while you are waiting for the user — an event is not their reply.
```

</details>

<details><summary>🔧 Bash: Check mutation progress and reviews folder · 08:49</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; cat reviews/scratch/stage5-leakage/mutations_real.out | grep 2026-08-03; cat reviews/scratch/stage5-leakage/mutation_disk.out; ls reviews
```

**Результат**

```
REAL 2026-08-03T04:00:00Z none                         corrupted_future: pass (34s) 554237 | known_at: pass (24s) 14371
REAL 2026-08-03T04:00:00Z m1_window+1h                 corrupted_future: CAUGHT (34s) features and forecasts at the cut.iloc[:, 3] (column name="starts_24h") are different | known_at: pass (24s) 14371
SUMMARY.md
claude
prompts
scratch
stage0-1b.md
stage2.md
stage3.md
stage4-6.md
stage5-leakage.md
stage7.md
stage8.md
```

</details>

<details><summary>🔧 Monitor: Wait for remaining mutation results · 08:49</summary>

**Аргументы**

```json
{
 "command": "cd /d/Flash/golova/KSE_AI/AAFS; until [ $(grep -c \"2026-08-03\" reviews/scratch/stage5-leakage/mutations_real.out) -ge 6 ] && [ -s reviews/scratch/stage5-leakage/mutation_disk.out ]; do sleep 5; done; cat reviews/scratch/stage5-leakage/mutations_real.out | grep 2026-08-03; cat reviews/scratch/stage5-leakage/mutation_disk.out",
 "description": "Wait for remaining mutation results",
 "timeout": "900000"
}
```

**Результат**

```
Monitor started (task bj6ekeepp, expires in 5m unless the source ends first; you get one notice at expiry — re-arm if you still need the watch). You will be notified on each event. Keep working — do not poll or sleep. Events may arrive while you are waiting for the user — an event is not their reply.
```

</details>

<details><summary>🔔 Уведомление: Background command "Run disk-read mutation at pending cut" completed (exit code 0) · 08:49</summary>

```
<task-notification>
<task-id>b8mm5ijlj</task-id>
<tool-use-id>toolu_01SKGTbCvdPemmuYSpMR1Wz6</tool-use-id>
<output-file>C:\Users\chyck\AppData\Local\Temp\claude\d--Flash-golova-KSE-AI-AAFS\57049ae5-374c-471e-8191-1ff2343b8a66\tasks\b8mm5ijlj.output</output-file>
<status>completed</status>
<summary>Background command "Run disk-read mutation at pending cut" completed (exit code 0)</summary>
</task-notification>
```

</details>

<details><summary>🔧 Bash: Show disk mutation result · 08:49</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; cat reviews/scratch/stage5-leakage/mutation_disk.out; grep 2026-08-03 reviews/scratch/stage5-leakage/mutations_real.out
```

**Результат**

```
REAL 2026-08-03T04:00:00Z m6_end_utc_from_disk corrupted_future: pass (33s) 554237 | known_at: pass (24s) 14371
REAL 2026-08-03T04:00:00Z none                         corrupted_future: pass (34s) 554237 | known_at: pass (24s) 14371
REAL 2026-08-03T04:00:00Z m1_window+1h                 corrupted_future: CAUGHT (34s) features and forecasts at the cut.iloc[:, 3] (column name="starts_24h") are different | known_at: pass (24s) 14371
```

</details>

<details><summary>🔧 Monitor: Wait for last mutation results at 08-03 · 08:49</summary>

**Аргументы**

```json
{
 "command": "cd /d/Flash/golova/KSE_AI/AAFS; until [ $(grep -c \"2026-08-03\" reviews/scratch/stage5-leakage/mutations_real.out) -ge 6 ]; do sleep 5; done; grep 2026-08-03 reviews/scratch/stage5-leakage/mutations_real.out | tail -4",
 "description": "Wait for last mutation results at 08-03",
 "timeout": "900000"
}
```

**Результат**

```
Monitor started (task bdm10ems0, expires in 5m unless the source ends first; you get one notice at expiry — re-arm if you still need the watch). You will be notified on each event. Keep working — do not poll or sleep. Events may arrive while you are waiting for the user — an event is not their reply.
```

</details>

<details><summary>🔧 Write: reviews/claude/stage5-leakage.md · 08:51</summary>

**Аргументы**

```
# file: reviews/claude/stage5-leakage.md
# Ревью: этап 5 и защита от утечки

Ревьюер — Claude. Ветка `stages-7-8`, коммит `f47ddec`. Все расчёты сделаны в памяти, файлы проекта не менялись.
Скрипты и их выводы лежат в `reviews/scratch/stage5-leakage/`, запуск из корня:
`PYTHONPATH=src python reviews/scratch/stage5-leakage/<скрипт>.py`. Артефакты собраны через `pipeline.build_all` и закешированы в `art.pkl` (`build_cache.py`).

## 1. Резюме

Признаки посчитаны правильно. Независимый пересчёт из исходных записей совпал на 300 случайных строках и ещё на 150 строках, где начало тревоги лежит ровно на границе окна: все 21 колонка. Соседство по границам тоже верно: независимый геометрический критерий дал те же 532 пары единиц.

Слабое место — проверки утечки, точнее то, что о них утверждают README и D21. На реальных данных проверка знания в обоих срезах конфига не видит класс утечки, ради которого её писали (D16): в эти два момента нет ни одного выдуманного конца, который был бы ещё не записан. Мутация, повторяющая утечку из D16, проходит на этих срезах обе проверки. Её ловит только срез, где такой конец есть, например 2026-08-03 04:00.

Кроме того, на реальных данных проверка знания падает в семи часовых срезах. Причин две. Первая — расхождение правила `open_until` с моделью записи `known_at` на шести настоящих тревогах длиной ровно 1 ч. Вторая — начало перерыва D15 (05:55:28) само является выдуманным концом, записанным уже после перерыва.

На цифры результата ни одна находка заметно не влияет. Вердикт: утечки, которая меняла бы метрики, я не нашёл. Но формулировки «каждая проверка проверена подменой с утечкой» и «признаки совпадают со знанием на момент t» сейчас верны только на синтетике.

## 2. Находки

### S5-1. Проверка знания на реальных данных не видит утечку D16 в срезах из конфига
- **Серьёзность:** существенно (вывод README о силе защиты); на метрики не влияет. **Уверенность:** проверено на данных.
- **Где:** `config.yaml:78` (срезы 2026-08-10 00:00 и 2026-08-21
… [обрезано: показано 2000 из 18965 символов]
```

**Результат**

```
File created successfully at: D:\Flash\golova\KSE_AI\AAFS\reviews\claude\stage5-leakage.md (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Bash: Check remaining mutation results · 08:51</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; grep 2026-08-03 reviews/scratch/stage5-leakage/mutations_real.out | cut -c1-260
```

**Результат**

```
REAL 2026-08-03T04:00:00Z none                         corrupted_future: pass (34s) 554237 | known_at: pass (24s) 14371
REAL 2026-08-03T04:00:00Z m1_window+1h                 corrupted_future: CAUGHT (34s) features and forecasts at the cut.iloc[:, 3] (column name="starts_24h") are different | known_at: pass (24s) 14371
REAL 2026-08-03T04:00:00Z m2_end_utc                   corrupted_future: pass (34s) 554237 | known_at: CAUGHT (23s) features known at 2026-08-03 04:00:00+00:00.iloc[:, 5] (column name="oblast_active_share") are different
REAL 2026-08-03T04:00:00Z m3_uncertain                 corrupted_future: CAUGHT (29s) training rows, labels and features.iloc[:, 12] (column name="country_starts_30m") are different | known_at: CAUGHT (18s) features known at 2026-08-03 04:00:00+00:00.iloc[:, 9
```

</details>

<details><summary>🔧 Monitor: Wait for m4 and m5 results · 08:51</summary>

**Аргументы**

```json
{
 "command": "cd /d/Flash/golova/KSE_AI/AAFS; until [ $(grep -c \"2026-08-03\" reviews/scratch/stage5-leakage/mutations_real.out) -ge 6 ]; do sleep 5; done; grep 2026-08-03 reviews/scratch/stage5-leakage/mutations_real.out | tail -2 | cut -c1-300",
 "description": "Wait for m4 and m5 results",
 "timeout": "600000"
}
```

**Результат**

```
Monitor started (task bom5er665, expires in 5m unless the source ends first; you get one notice at expiry — re-arm if you still need the watch). You will be notified on each event. Keep working — do not poll or sleep. Events may arrive while you are waiting for the user — an event is not their reply.
```

</details>

<details><summary>🔧 Monitor: Wait for m4 and m5 results · 08:51</summary>

**Аргументы**

```json
{
 "command": "cd /d/Flash/golova/KSE_AI/AAFS; until [ $(grep -c \"2026-08-03\" reviews/scratch/stage5-leakage/mutations_real.out) -ge 6 ]; do sleep 5; done; grep 2026-08-03 reviews/scratch/stage5-leakage/mutations_real.out | tail -2 | cut -c1-300",
 "description": "Wait for m4 and m5 results",
 "timeout": "600000"
}
```

**Результат**

```
Monitor started (task buxiiux55, expires in 5m unless the source ends first; you get one notice at expiry — re-arm if you still need the watch). You will be notified on each event. Keep working — do not poll or sleep. Events may arrive while you are waiting for the user — an event is not their reply.
```

</details>

<details><summary>🔧 Edit: reviews/claude/stage5-leakage.md · 08:51</summary>

**Аргументы**

```
# file: reviews/claude/stage5-leakage.md
--- old_string ---
  | Убранные признаки | h = 1, PR-AUC | h = 3, PR-AUC |
  |---|---|---|
  | ничего (0.421 / 0.692) | — | — |
  | соседи | −0.003 | −0.003 |
--- new_string ---
  | Убранные признаки | h = 1, PR-AUC | h = 3, PR-AUC |
  |---|---|---|
  | ничего (полный набор) | 0.421 | 0.692 |
  | соседи | −0.003 | −0.003 |
```

**Результат**

```
The file D:\Flash\golova\KSE_AI\AAFS\reviews\claude\stage5-leakage.md has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Edit: reviews/claude/stage5-leakage.md · 08:51</summary>

**Аргументы**

```
# file: reviews/claude/stage5-leakage.md
--- old_string ---
| 2026-08-03 04:00 | 6 висящих выдуманных концов (U025 и др.) | PASS, 14 371 строка, 53 открытых |
| 2026-08-29 04:00 | ≈ 2 ч до перерыва | PASS, 14 068, 51 |
--- new_string ---
| 2026-08-03 04:00 | 6 висящих выдуманных концов | PASS, 14 371 строка, 53 открытых |
| 2026-08-29 04:00 | ≈ 2 ч до перерыва по D15 (≈ 1 ч до настоящей тишины, S5-3) | PASS, 14 068, 51 |
```

**Результат**

```
The file D:\Flash\golova\KSE_AI\AAFS\reviews\claude\stage5-leakage.md has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Edit: reviews/claude/stage5-leakage.md · 08:52</summary>

**Аргументы**

```
# file: reviews/claude/stage5-leakage.md
--- old_string ---
  - m1 ловится, только если в ближайший час после среза у какой-то тихой единицы есть начало;
--- new_string ---
  - m1 проверка знания ловит, только если в ближайший час после среза начинается тревога у единицы, которая в срезе тихая (в 08-03 04:00 такой нет);
```

**Результат**

```
The file D:\Flash\golova\KSE_AI\AAFS\reviews\claude\stage5-leakage.md has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Monitor: Wait for m4 and m5 results · 08:52</summary>

**Аргументы**

```json
{
 "command": "cd /d/Flash/golova/KSE_AI/AAFS; until [ $(grep -c \"2026-08-03\" reviews/scratch/stage5-leakage/mutations_real.out) -ge 6 ]; do sleep 5; done; grep 2026-08-03 reviews/scratch/stage5-leakage/mutations_real.out | tail -2 | cut -c1-300",
 "description": "Wait for m4 and m5 results",
 "timeout": "600000"
}
```

**Результат**

```
Monitor started (task b892g54ep, expires in 5m unless the source ends first; you get one notice at expiry — re-arm if you still need the watch). You will be notified on each event. Keep working — do not poll or sleep. Events may arrive while you are waiting for the user — an event is not their reply.
```

</details>

<details><summary>🔧 Bash: Check mutation run is still progressing · 08:52</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; grep -c 2026-08-03 reviews/scratch/stage5-leakage/mutations_real.out; tasklist 2>/dev/null | grep -i python | head
```

**Результат**

```
5
python.exe                   23344 Console                    1      7�860 K
python.exe                   16920 Console                    1    423�592 K
```

</details>

<details><summary>🔧 Bash: Show m4 result line · 08:52</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; grep 2026-08-03 reviews/scratch/stage5-leakage/mutations_real.out | tail -2 | cut -c1-320
```

**Результат**

```
REAL 2026-08-03T04:00:00Z m3_uncertain                 corrupted_future: CAUGHT (29s) training rows, labels and features.iloc[:, 12] (column name="country_starts_30m") are different | known_at: CAUGHT (18s) features known at 2026-08-03 04:00:00+00:00.iloc[:, 9] (column name="country_starts_30m") are different
REAL 2026-08-03T04:00:00Z m4_masks_ab                  corrupted_future: CAUGHT (24s) training rows, labels and features.iloc[:, 13] (column name="country_starts_60m") are different | known_at: CAUGHT (17s) features known at 2026-08-03 04:00:00+00:00.iloc[:, 10] (column name="country_starts_60m") are different
```

</details>

<details><summary>🔧 Monitor: Wait for m5 result · 08:52</summary>

**Аргументы**

```json
{
 "command": "cd /d/Flash/golova/KSE_AI/AAFS; until [ $(grep -c \"2026-08-03\" reviews/scratch/stage5-leakage/mutations_real.out) -ge 6 ]; do sleep 5; done; grep 2026-08-03 reviews/scratch/stage5-leakage/mutations_real.out | tail -1 | cut -c1-320",
 "description": "Wait for m5 result",
 "timeout": "300000"
}
```

**Результат**

```
Monitor started (task bejznjrdb, expires in 5m unless the source ends first; you get one notice at expiry — re-arm if you still need the watch). You will be notified on each event. Keep working — do not poll or sleep. Events may arrive while you are waiting for the user — an event is not their reply.
```

</details>

<details><summary>🔧 Bash: Fill known mutation results into report · 08:52</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; python - <<'EOF'
p='reviews/claude/stage5-leakage.md'
s=open(p,encoding='utf-8').read()
s=s.replace("| m2 состояние по `end_utc` | нет 0/4 | ловит 2/2 | **нет / нет** | [ЗАПОЛНИТЬ] |","| m2 состояние по `end_utc` | нет 0/4 | ловит 2/2 | **нет / нет** | нет / **ловит** (`oblast_active_share`) |")
s=s.replace("| m3 флаг `uncertain` | ловит 2/4 | ловит 1/2 | ловит (обучающие строки) / нет | [ЗАПОЛНИТЬ] |","| m3 флаг `uncertain` | ловит 2/4 | ловит 1/2 | ловит (обучающие строки) / нет | ловит / ловит |")
s=s.replace("| m4 маски (а) и (б) | ловит 2/4 | ловит 2/2 | ловит (обучающие строки) / нет | [ЗАПОЛНИТЬ] |","| m4 маски (а) и (б) | ловит 2/4 | ловит 2/2 | ловит (обучающие строки) / нет | ловит / ловит |")
s=s.replace("хотя m2 в том же срезе ловится [ЗАПОЛНИТЬ]","хотя m2 в том же срезе проверка знания ловит (`oblast_active_share`)")
open(p,'w',encoding='utf-8').write(s)
print(s.count('[ЗАПОЛНИТЬ]'))
EOF
```

**Результат**

```
2
```

</details>

<details><summary>🔔 Уведомление: Background command "Run mutation tests on real data cuts" completed (exit code 0) · 08:52</summary>

```
<task-notification>
<task-id>bmlnykvij</task-id>
<tool-use-id>toolu_01CAKZJpteVA9vGq8LThtvsq</tool-use-id>
<output-file>C:\Users\chyck\AppData\Local\Temp\claude\d--Flash-golova-KSE-AI-AAFS\57049ae5-374c-471e-8191-1ff2343b8a66\tasks\bmlnykvij.output</output-file>
<status>completed</status>
<summary>Background command "Run mutation tests on real data cuts" completed (exit code 0)</summary>
</task-notification>
```

</details>

<details><summary>🔔 Уведомление: Monitor "Wait for m4 and m5 results" stream ended · 08:52</summary>

```
<task-notification>
<task-id>buxiiux55</task-id>
<tool-use-id>toolu_017ANpdMdhSLavwxf5KBV2D9</tool-use-id>
<output-file>C:\Users\chyck\AppData\Local\Temp\claude\d--Flash-golova-KSE-AI-AAFS\57049ae5-374c-471e-8191-1ff2343b8a66\tasks\buxiiux55.output</output-file>
<status>completed</status>
<summary>Monitor "Wait for m4 and m5 results" stream ended</summary>
<event>REAL 2026-08-03T04:00:00Z m4_masks_ab                  corrupted_future: CAUGHT (24s) training rows, labels and features.iloc[:, 13] (column name="country_starts_60m") are different | known_at: CAUGHT (17s) features known at 2026-08-03 04:00:00+00:00.iloc[:, 10] (column name="country_starts_60m") ar
REAL 2026-08-03T04:00:00Z m5_seen_without_open_until   corrupted_future: pass (22s) 554237 | known_at: CAUGHT (16s) features known at 2026-08-03 04:00:00+00:00.iloc[:, 5] (column name="oblast_active_share") are different</event>
</task-notification>
```

</details>

<details><summary>🔔 Уведомление: Monitor "Wait for last mutation results at 08-03" stream ended · 08:52</summary>

```
<task-notification>
<task-id>bdm10ems0</task-id>
<tool-use-id>toolu_01Dhbm9B5WDmqTDPUS2MCazG</tool-use-id>
<output-file>C:\Users\chyck\AppData\Local\Temp\claude\d--Flash-golova-KSE-AI-AAFS\57049ae5-374c-471e-8191-1ff2343b8a66\tasks\bdm10ems0.output</output-file>
<status>completed</status>
<summary>Monitor "Wait for last mutation results at 08-03" stream ended</summary>
<event>REAL 2026-08-03T04:00:00Z m2_end_utc                   corrupted_future: pass (34s) 554237 | known_at: CAUGHT (23s) features known at 2026-08-03 04:00:00+00:00.iloc[:, 5] (column name="oblast_active_share") are different
REAL 2026-08-03T04:00:00Z m3_uncertain                 corrupted_future: CAUGHT (29s) training rows, labels and features.iloc[:, 12] (column name="country_starts_30m") are different | known_at: CAUGHT (18s) features known at 2026-08-03 04:00:00+00:00.iloc[:, 9] (column name="country_starts_30m") are different
REAL 2026-08-03T04:00:00Z m4_masks_ab                  corrupted_future: CAUGHT (24s) training rows, labels and features.iloc[:, 13] (column name="country_starts_60m") are different | known_at: CAUGHT (17s) features known at 2026-08-03 04:00:00+00:00.iloc[:, 10] (column name="country_starts_60m") are different
REAL 2026-08-03T04:00:00Z m5_seen_without_open_until   corrupted_future: pass (22s) 554237 | known_at: CAUGHT (16s) features known at 2026-08-03 04:00:00+00:00.iloc[:, 5] (column name="oblast_active_share") are different</event>
</task-notification>
```

</details>

<details><summary>🔔 Уведомление: Monitor "Wait for m5 result" stream ended · 08:52</summary>

```
<task-notification>
<task-id>bejznjrdb</task-id>
<tool-use-id>toolu_01Vq8krQz83rGhnhkVh8pJ83</tool-use-id>
<output-file>C:\Users\chyck\AppData\Local\Temp\claude\d--Flash-golova-KSE-AI-AAFS\57049ae5-374c-471e-8191-1ff2343b8a66\tasks\bejznjrdb.output</output-file>
<status>completed</status>
<summary>Monitor "Wait for m5 result" stream ended</summary>
<event>REAL 2026-08-03T04:00:00Z m5_seen_without_open_until   corrupted_future: pass (22s) 554237 | known_at: CAUGHT (16s) features known at 2026-08-03 04:00:00+00:00.iloc[:, 5] (column name="oblast_active_share") are different</event>
</task-notification>
```

</details>

<details><summary>🔔 Уведомление: Monitor "Wait for remaining mutation results" stream ended · 08:52</summary>

```
<task-notification>
<task-id>bj6ekeepp</task-id>
<tool-use-id>toolu_01PP87S8SwH1xKXnnAjt2Pm8</tool-use-id>
<output-file>C:\Users\chyck\AppData\Local\Temp\claude\d--Flash-golova-KSE-AI-AAFS\57049ae5-374c-471e-8191-1ff2343b8a66\tasks\bj6ekeepp.output</output-file>
<status>completed</status>
<summary>Monitor "Wait for remaining mutation results" stream ended</summary>
<event>REAL 2026-08-03T04:00:00Z none                         corrupted_future: pass (34s) 554237 | known_at: pass (24s) 14371
REAL 2026-08-03T04:00:00Z m1_window+1h                 corrupted_future: CAUGHT (34s) features and forecasts at the cut.iloc[:, 3] (column name="starts_24h") are different | known_at: pass (24s) 14371
REAL 2026-08-03T04:00:00Z m2_end_utc                   corrupted_future: pass (34s) 554237 | known_at: CAUGHT (23s) features known at 2026-08-03 04:00:00+00:00.iloc[:, 5] (column name="oblast_active_share") are different
REAL 2026-08-03T04:00:00Z m3_uncertain                 corrupted_future: CAUGHT (29s) training rows, labels and features.iloc[:, 12] (column name="country_starts_30m") are different | known_at: CAUGHT (18s) features known at 2026-08-03 04:00:00+00:00.iloc[:, 9] (column name="country_starts_30m") are different
REAL 2026-08-03T04:00:00Z m4_masks_ab                  corrupted_future: CAUGHT (24s) training rows, labels and features.iloc[:, 13] (column name="country_starts_60m") are different | known_at: CAUGHT (17s) features known at 2026-08-03 04:00:00+00:00.iloc[:, 10] (column name="country_starts_60m") are different
REAL 2026-08-03T04:00:00Z m5_seen_without_open_until   corrupted_future: pass (22s) 554237 | known_at: CAUGHT (16s) features known at 2026-08-03 04:00:00+00:00.iloc[:, 5] (column name="oblast_active_share") are different
REAL 2026-08-03T04:00:00Z m6_end_utc_from_disk corrupted_future: pass (33s) 554237 | known_at: pass (24s) 14371</event>
</task-notification>
```

</details>

<details><summary>🔔 Уведомление: Monitor "Wait for mutation runs to finish" stream ended · 08:52</summary>

```
<task-notification>
<task-id>bvqf8vltj</task-id>
<tool-use-id>toolu_01H3aShczCCuRZiS9P99weya</tool-use-id>
<output-file>C:\Users\chyck\AppData\Local\Temp\claude\d--Flash-golova-KSE-AI-AAFS\57049ae5-374c-471e-8191-1ff2343b8a66\tasks\bvqf8vltj.output</output-file>
<status>completed</status>
<summary>Monitor "Wait for mutation runs to finish" stream ended</summary>
<event>done</event>
</task-notification>
```

</details>

<details><summary>🔔 Уведомление: Monitor "Wait for mutation runs and print results" stream ended · 08:52</summary>

```
<task-notification>
<task-id>bqwbd0zwq</task-id>
<tool-use-id>toolu_017DrthdvpTPJ1jwAzfJ4zhw</tool-use-id>
<output-file>C:\Users\chyck\AppData\Local\Temp\claude\d--Flash-golova-KSE-AI-AAFS\57049ae5-374c-471e-8191-1ff2343b8a66\tasks\bqwbd0zwq.output</output-file>
<status>completed</status>
<summary>Monitor "Wait for mutation runs and print results" stream ended</summary>
<event>REAL 2026-08-03T04:00:00Z none                         corrupted_future: pass (34s) 554237 | known_at: pass (24s) 14371
REAL 2026-08-03T04:00:00Z m1_window+1h                 corrupted_future: CAUGHT (34s) features and forecasts at the cut.iloc[:, 3] (column name="starts_24h") are different | known_at: pass (24s) 14371
REAL 2026-08-03T04:00:00Z m2_end_utc                   corrupted_future: pass (34s) 554237 | known_at: CAUGHT (23s) features known at 2026-08-03 04:00:00+00:00.iloc[:, 5] (column name="oblast_active_share") are different
REAL 2026-08-03T04:00:00Z m3_uncertain                 corrupted_future: CAUGHT (29s) training rows, labels and features.iloc[:, 12] (column name="country_starts_30m") are different | known_at: CAUGHT (18s) features known at 2026-08-03 04:00:00+00:00.iloc[:, 9] (column name="country_starts_30m") are different
REAL 2026-08-03T04:00:00Z m4_masks_ab                  corrupted_future: CAUGHT (24s) training rows, labels and features.iloc[:, 13] (column name="country_starts_60m") are different | known_at: CAUGHT (17s) features known at 2026-08-03 04:00:00+00:00.iloc[:, 10] (column name="country_starts_60m") are different
REAL 2026-08-03T04:00:00Z m5_seen_without_open_until   corrupted_future: pass (22s) 554237 | known_at: CAUGHT (16s) features known at 2026-08-03 04:00:00+00:00.iloc[:, 5] (column name="oblast_active_share") are different
REAL 2026-08-03T04:00:00Z m6_end_utc_from_disk corrupted_future: pass (33s) 554237 | known_at: pass (24s) 14371</event>
</task-notification>
```

</details>

<details><summary>🔔 Уведомление: Monitor "Wait for mutation runs to finish" stream ended · 08:52</summary>

```
<task-notification>
<task-id>br538yntl</task-id>
<tool-use-id>toolu_01LFd8NWK6PHWbM76x7Cenbx</tool-use-id>
<output-file>C:\Users\chyck\AppData\Local\Temp\claude\d--Flash-golova-KSE-AI-AAFS\57049ae5-374c-471e-8191-1ff2343b8a66\tasks\br538yntl.output</output-file>
<status>completed</status>
<summary>Monitor "Wait for mutation runs to finish" stream ended</summary>
<event>done</event>
</task-notification>
```

</details>

<details><summary>🔔 Уведомление: Monitor "Wait for m4 and m5 results" stream ended · 08:52</summary>

```
<task-notification>
<task-id>bom5er665</task-id>
<tool-use-id>toolu_01NNrtxZQxYbcCGwZtSLDU7C</tool-use-id>
<output-file>C:\Users\chyck\AppData\Local\Temp\claude\d--Flash-golova-KSE-AI-AAFS\57049ae5-374c-471e-8191-1ff2343b8a66\tasks\bom5er665.output</output-file>
<status>completed</status>
<summary>Monitor "Wait for m4 and m5 results" stream ended</summary>
<event>REAL 2026-08-03T04:00:00Z m4_masks_ab                  corrupted_future: CAUGHT (24s) training rows, labels and features.iloc[:, 13] (column name="country_starts_60m") are different | known_at: CAUGHT (17s) features known at 2026-08-03 04:00:00+00:00.iloc[:, 10] (column name="country_starts_60m") ar
REAL 2026-08-03T04:00:00Z m5_seen_without_open_until   corrupted_future: pass (22s) 554237 | known_at: CAUGHT (16s) features known at 2026-08-03 04:00:00+00:00.iloc[:, 5] (column name="oblast_active_share") are different</event>
</task-notification>
```

</details>

<details><summary>🔔 Уведомление: Monitor "Wait for m4 and m5 results" stream ended · 08:52</summary>

```
<task-notification>
<task-id>b892g54ep</task-id>
<tool-use-id>toolu_012XFDiN7wvpf88NXKurypyu</tool-use-id>
<output-file>C:\Users\chyck\AppData\Local\Temp\claude\d--Flash-golova-KSE-AI-AAFS\57049ae5-374c-471e-8191-1ff2343b8a66\tasks\b892g54ep.output</output-file>
<status>completed</status>
<summary>Monitor "Wait for m4 and m5 results" stream ended</summary>
<event>REAL 2026-08-03T04:00:00Z m4_masks_ab                  corrupted_future: CAUGHT (24s) training rows, labels and features.iloc[:, 13] (column name="country_starts_60m") are different | known_at: CAUGHT (17s) features known at 2026-08-03 04:00:00+00:00.iloc[:, 10] (column name="country_starts_60m") ar
REAL 2026-08-03T04:00:00Z m5_seen_without_open_until   corrupted_future: pass (22s) 554237 | known_at: CAUGHT (16s) features known at 2026-08-03 04:00:00+00:00.iloc[:, 5] (column name="oblast_active_share") are different</event>
</task-notification>
```

</details>

<details><summary>🔧 Bash: Fill final mutation results into report · 08:52</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; python - <<'EOF'
p='reviews/claude/stage5-leakage.md'
s=open(p,encoding='utf-8').read()
s=s.replace("| m5 `seen` без `open_until` | нет 0/4 | ловит 2/2 | **нет / нет** | [ЗАПОЛНИТЬ] |","| m5 `seen` без `open_until` | нет 0/4 | ловит 2/2 | **нет / нет** | нет / **ловит** (`oblast_active_share`) |")
s=s.replace("В срезе 08-03 04:00 их ловит проверка знания: [ЗАПОЛНИТЬ].","В срезе 08-03 04:00 обе ловит проверка знания (`oblast_active_share`), а порча будущего — ни одну.")
open(p,'w',encoding='utf-8').write(s)
print(s.count('ЗАПОЛНИТЬ'), len(s.splitlines()))
EOF
grep -n "ЗАПОЛН\|08-03 04:00" reviews/claude/stage5-leakage.md | head
```

**Результат**

```
0 188
11:Слабое место — проверки утечки, точнее то, что о них утверждают README и D21. На реальных данных проверка знания в обоих срезах конфига не видит класс утечки, ради которого её писали (D16): в эти два момента нет ни одного выдуманного конца, который был бы ещё не записан. Мутация, повторяющая утечку из D16, проходит на этих срезах обе проверки. Её ловит только срез, где такой конец есть, например 2026-08-03 04:00.
24:  - `pending.py`: выдуманных концов, висящих в срезе, — 0 и в 08-10 00:00, и в 08-21 14:00. Хотя бы один висит в 5.0% часовых моментов: обучение — 3.2%, валидация — 6.0%, тест — 19% (это из-за перерыва). Например, в 2026-08-03 04:00 их 6.
25:  - Мутационное тестирование (`mutations.py`, monkeypatch, исходники не трогались; таблица ниже). Мутации m2 (состояние по записанному `end_utc`) и m5 (`seen` без `open_until`) — это ровно утечка D16. В срезе 08-21 14:00 обе проходят **обе** проверки. В срезе 08-03 04:00 обе ловит проверка знания (`oblast_active_share`), а порча будущего — ни одну. На синтетике `tests/test_knowledge.py` ловит их, потому что в `with_invented_end` висящий конец задан намеренно.
69:- **Доказательство** (`mutation_disk.py`). Мутация m6 — та же утечка, что m2 (состояние по `end_utc`), но из `data/intervals.csv`. В срезе 2026-08-03 04:00 она проходит обе проверки, хотя m2 в том же срезе проверка знания ловит (`oblast_active_share`).
133:| Мутация | Синт.: порча будущего | Синт.: знание на момент среза | 08-21 14:00: порча / знание | 08-03 04:00: порча / знание |
146:  - m1 проверка знания ловит, только если в ближайший час после среза начинается тревога у единицы, которая в срезе тихая (в 08-03 04:00 такой нет);
154:| 2026-08-03 04:00 | 6 висящих выдуманных концов | PASS, 14 371 строка, 53 открытых |
181:- `known_at` верно моделирует выдуманный конец: в срезе он открыт, пока не наступило следующее начало (PASS в 08-03 04:00 при 6 висящих). Внутри склеенной паузы проверка проходит. Отклонение — только у настоящих тревог ровно на 1 ч (S5-2а).
```

</details>

<details><summary>🔧 Read: reviews/claude/stage5-leakage.md · 08:52</summary>

**Аргументы**

```json
{
 "file_path": "D:\\Flash\\golova\\KSE_AI\\AAFS\\reviews\\claude\\stage5-leakage.md",
 "limit": 60
}
```

**Результат**

```
1	# Ревью: этап 5 и защита от утечки
2	
3	Ревьюер — Claude. Ветка `stages-7-8`, коммит `f47ddec`. Все расчёты сделаны в памяти, файлы проекта не менялись.
4	Скрипты и их выводы лежат в `reviews/scratch/stage5-leakage/`, запуск из корня:
5	`PYTHONPATH=src python reviews/scratch/stage5-leakage/<скрипт>.py`. Артефакты собраны через `pipeline.build_all` и закешированы в `art.pkl` (`build_cache.py`).
6	
7	## 1. Резюме
8	
9	Признаки посчитаны правильно. Независимый пересчёт из исходных записей совпал на 300 случайных строках и ещё на 150 строках, где начало тревоги лежит ровно на границе окна: все 21 колонка. Соседство по границам тоже верно: независимый геометрический критерий дал те же 532 пары единиц.
10	
11	Слабое место — проверки утечки, точнее то, что о них утверждают README и D21. На реальных данных проверка знания в обоих срезах конфига не видит класс утечки, ради которого её писали (D16): в эти два момента нет ни одного выдуманного конца, который был бы ещё не записан. Мутация, повторяющая утечку из D16, проходит на этих срезах обе проверки. Её ловит только срез, где такой конец есть, например 2026-08-03 04:00.
12	
13	Кроме того, на реальных данных проверка знания падает в семи часовых срезах. Причин две. Первая — расхождение правила `open_until` с моделью записи `known_at` на шести настоящих тревогах длиной ровно 1 ч. Вторая — начало перерыва D15 (05:55:28) само является выдуманным концом, записанным уже после перерыва.
14	
15	На цифры результата ни одна находка заметно не влияет. Вердикт: утечки, которая меняла бы метрики, я не нашёл. Но формулировки «каждая проверка проверена подменой с утечкой» и «признаки совпадают со знанием на момент t» сейчас верны только на синтетике.
16	
17	## 2. Находки
18	
19	### S5-1. Проверка знания на реальных данных не видит утечку D16 в срезах из конфига
20	- **Серьёзность:** существенно (вывод README о силе защиты); на метрики не влияет. **Уверенность:** проверено на данных.
21	- **Где:** `config.yaml:78` (срезы 2026-08-10 00:00 и 2026-08-21 14:00); `leakage.py:63-74`; README:82-83 («кожну перевірено підміною з витоком»); DECISIONS D21 «Проверка проверки».
22	- **Что не так.** `knowledge_check` находит только те записи, у которых метка времени не позже среза, а записаны они позже среза. В этом проекте такие записи — выдуманные концы (`s + 1 ч`, записываются при следующем начале). Если в момент среза ни один выдуманный конец не «висит», то есть его метка уже прошла, а запись ещё не появилась, проверка сравнивает полные данные с почти теми же полными данными. Признаки строк, отстоящих от среза на дни, к этому моменту тоже почти полностью «записаны». Поэтому 14–15 тысяч сравниваемых строк создают ложное ощущение охвата.
23	- **Доказательство.**
24	  - `pending.py`: выдуманных концов, висящих в срезе, — 0 и в 08-10 00:00, и в 08-21 14:00. Хотя бы один висит в 5.0% часовых моментов: обучение — 3.2%, валидация — 6.0%, тест — 19% (это из-за перерыва). Например, в 2026-08-03 04:00 их 6.
25	  - Мутационное тестировани
… [обрезано: показано 3000 из 7545 символов]
```

</details>

<details><summary>🔧 Bash: Fix wording and verify git status · 08:52</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; sed -i 's/Это выдуманные концы, их записали при оживлении канала 02.09./Это выдуманные концы: следующее начало у этих локаций наступило только после перерыва, и записаны они 02.09 или позже./' reviews/claude/stage5-leakage.md; grep -n "следующее начало у этих" reviews/claude/stage5-leakage.md; git status --short
```

**Результат**

```
57:  - Все 12 «событий» в интервале (04:55:28, 05:55:28] — концы записей ровно на 3600 с, следующее начало которых наступает после перерыва. Это выдуманные концы: следующее начало у этих локаций наступило только после перерыва, и записаны они 02.09 или позже.
 M .gitignore
?? reviews/SUMMARY.md
?? reviews/claude/
?? reviews/stage0-1b.md
?? reviews/stage2.md
?? reviews/stage3.md
?? reviews/stage4-6.md
?? reviews/stage5-leakage.md
?? reviews/stage7.md
?? reviews/stage8.md
```

</details>

<details><summary>🔧 Bash: Check whether scratch cache is git-ignored · 08:52</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS; git check-ignore -v reviews/scratch/stage5-leakage/art.pkl reviews/claude/stage5-leakage.md; echo rc=$?
```

**Результат**

```
.gitignore:8:reviews/scratch/	reviews/scratch/stage5-leakage/art.pkl
rc=0
```

</details>

<details><summary>🔧 SubagentHandback: {"message": "Отчёт записан в `D:\\Flash\\golova\\KSE_AI\\AAFS\\reviews\\claude\\stage5-leakage.md` (188 строк). Старого… · 08:53</summary>

**Аргументы**

```json
{
 "message": "Отчёт записан в `D:\\Flash\\golova\\KSE_AI\\AAFS\\reviews\\claude\\stage5-leakage.md` (188 строк). Старого отчёта в `reviews/stage5-leakage.md` у меня не было: до остановки я его не успел написать, так что восстанавливать было нечего. Файлы другого набора ревьюеров я не читал. Файлы проекта не менял, запрещённые скрипты не запускал, в git ничего не делал. `.gitignore` изменён не мной.\n\n**Резюме**\n- **Признаки посчитаны правильно.** Я пересчитал их независимо, прямо из исходных записей. Все 21 колонка совпали на 300 случайных строках (в том числе после перерыва канала и в ночь перехода на летнее время) и ещё на 150 строках, где начало тревоги лежит ровно на границе окна.\n- **Соседство по границам верно.** Независимая проверка «вершины ближе 100 м» дала те же 532 пары единиц. Пропущенных пар в охвате нет, касаний в одной точке нет, переименованные районы и склеенные единицы в порядке.\n- **Утечки, которая меняла бы метрики, не нашёл.**\n- **Слабое место — проверки утечки и то, что о них пишут README и D21.** В обоих срезах из конфига проверка знания на реальных данных не может увидеть утечку того типа, ради которого её писали (D16). Подмена с этой утечкой проходит там обе проверки и ловится только в срезе, где есть выдуманный конец, ещё не записанный в файл.\n- **На реальных данных проверка знания падает в 7 часовых срезах.** Это ложные тревоги, а не утечка в метриках.\n- **Мелочи:**\n  - начало перерыва D15 (05:55:28) — выдуманный конец, на самом деле канал замолчал на час раньше;\n  - «закрытый доступ» для признаков держится на соглашении: признак, читающий таблицу с диска, проходит обе проверки;\n  - пересчёт `starts_7d` после перерыва даёт значения примерно в 1.5 раза выше, и модель завышает прогноз на 1–2 п.п., но без пересчёта результат хуже;\n  - признаки соседей: на половине тревог соседи действительно не дают опережения, а низкий gain объясняется тем, что их информацию уже несёт `neighbor_oblasts_active_share`.\n\n**Находки уровня «критично
… [обрезано: показано 2000 из 3510 символов]
```

**Результат**

```
{"success":true,"message":"Report delivered to your caller."}
```

</details>
