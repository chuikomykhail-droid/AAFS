# Субагент: Review stage 7 report

- **Агент:** `a897305da3557170d` (general-purpose), запущен из сессии [57049ae5](../2026-10-11_critical-analysis_57049ae5.md#t-sCiKkyFs94oU)
- **Период (UTC):** 2026-10-11 17:19 → 2026-10-12 05:45
- **Период (Киев):** 2026-10-11 20:19 → 2026-10-12 08:45
- **Сообщений:** 2 (задания и сообщения основного агента — 1, ответы субагента — 1); вызовов инструментов — 66
- **Исходный JSONL:** `ai_logs/claude_code/raw/claude_code_raw.zip → subagents/57049ae5_agent-a897305da3557170d.jsonl`

> Служебные вставки (`<system-reminder>`, вложения с окружением и контекстом IDE, мета-сообщения — 120 записей) и блоки рассуждений (thinking — 55) сюда не включены: они есть в исходном JSONL. Время — киевское. Вызовы инструментов свёрнуты; аргументы обрезаны до 2000 символов, результаты — до 3000. Токен alerts.in.ua и email автора заменены на `[REDACTED_TOKEN]` / `[REDACTED_EMAIL]`.

---

<a id="m-e6f3e2c7"></a>

### 📨 Задание от основного агента · 2026-10-11 20:19

Рабочая папка проекта: d:\Flash\golova\KSE_AI\AAFS (Windows; доступны Bash (Git Bash) и PowerShell).

Прочитай файл `reviews/prompts/06_stage7.md` целиком и выполни задание из него в точности, включая все ограничения: не изменять файлы проекта, не запускать `scripts/run_all.py`, `scripts/api_check.py`, скрипты скачивания и `save_all`, не трогать git (чтение `git log` разрешено), не открывать токен и не выводить найденные секреты. Параллельно с тобой в той же папке работают шесть других агентов-ревьюеров — пиши только в `reviews/stage7.md` и `reviews/scratch/stage7/`.

Когда отчёт записан, верни в ответе: резюме отчёта (5–10 строк) и список находок уровня «критично» и «существенно» — по одной строке на находку (id, суть, файл:строка, уровень проверки).

<details><summary>🔧 Read: reviews/prompts/06_stage7.md · 20:19</summary>

**Аргументы**

```json
{
 "file_path": "d:\\Flash\\golova\\KSE_AI\\AAFS\\reviews\\prompts\\06_stage7.md"
}
```

**Результат**

```
1	# Ревью проекта AAFS: этап 7: отчёт, README и соответствие документов цифрам
2	
3	Ты — независимый критический ревьюер. Параллельно с тобой другие агенты проверяют другие этапы того же проекта. Твоя зона — этап 7: README, отчёты, графики, согласованность PLAN / DECISIONS / README с цифрами, воспроизводимость и комплект сдачи. На соседние этапы смотри только тогда, когда без этого не понять твой.
4	
5	## Проект
6	
7	- Репозиторий — текущая папка (`AAFS`), ветка `stages-7-8`. Python-проект: прогноз воздушных тревог в Украине по районам. Для каждой единицы (район; Киев — одна единица), где в момент `t` (каждый час) тихо, модель выдаёт вероятность того, что тревога начнётся в `(t, t+h]`, h = 1, 3, 6 (основной — 3).
8	- Данные — снимок датасета Vadimkin (`dataset_repo/`, коммит `58ee75b`). Официальный ряд заканчивается 2026-09-07. Тест — 2026-08-10…2026-09-07, walk-forward с ежесуточным переобучением. Этап 8 — проверка на данных alerts.in.ua за сентябрь–октябрь.
9	- Это тестовое задание с дедлайном 12.10.2026 23:59 по Киеву. Проверяющие оценивают процесс: пойманные ошибки, обоснованность решений, отсутствие утечки из будущего. Найденная проблема ценна, даже если её не успеют исправить: тогда она уйдёт в раздел ограничений.
10	- Документы: `PLAN.md` (правила работы 1–13; у каждого этапа «Исходное задание» и «Как сделано»), `DECISIONS.md` (решения D00–D22, справочные цифры, журнал пойманных ошибок ИИ), `README.md` (на украинском), отчёты в `reports/`.
11	
12	Сначала прочитай раздел «Правила работы» в `PLAN.md`, описание своего этапа в `PLAN.md` и разделы `DECISIONS.md`: все, особенно «Справочные цифры» и «Пойманные ошибки ИИ». Код и тесты своей зоны читай целиком, а не выборочно.
13	
14	## Твоя зона: файлы
15	
16	- `README.md`, `PLAN.md`, `DECISIONS.md`.
17	- `reports/*.md`, `reports/*.json`, `reports/figures/*.png`.
18	- `src/alerts/report.py`, `src/alerts/figures.py`; `src/alerts/evaluation.py`: `write_report`, `write_summary`.
19	- `scripts/run_all.py` — только читать.
20	- `requirements.txt`, `pyproject.toml`, `.gitignore`, `archive/`.
21	
22	## Что проверить
23	
24	1. **Аудит утверждений.**
25	   - Выпиши каждое число и каждое качественное утверждение из README (на украинском), из разделов «Как сделано» в PLAN и из D17–D22.
26	   - Для каждого найди источник в `reports/` или пересчитай из `data/*.parquet`. Оформи таблицей: утверждение → источник → совпадает или нет.
27	   - Особенно: «біт у біт», «кожну перевірку перевірено підміною з витоком», «модель розрізняє моменти», «калібрування близьке до діагоналі», «27 випадків», время работы `run_all`.
28	2. **Противоречия** между PLAN, DECISIONS, README и отчётами; фразы, устаревшие после этапов 7–8.
29	3. **Сдача по заданию** (`PLAN.md`, раздел «Контекст задачи»).
30	   - Нужны ссылка на репозиторий с рабочим кодом, полный лог работы с ИИ и рефлексия примерно на 100 слов. Что из этого есть в репозитории и где? Чего не хватает?
31	   - Пройди «Критерий готовности MVP» в `PLAN.md`: выполнен ли каждый п
… [обрезано: показано 3000 из 8591 символов]
```

</details>

<details><summary>🔧 Bash: List project structure and git log · 20:19</summary>

**Аргументы**

```bash
ls -la && git log --oneline | head -40 && ls reports reports/figures archive data scripts src/alerts tests reviews reviews/scratch 2>&1 | head -150
```

**Результат**

```
total 219
drwxr-xr-x 1 chyck 197609      0 Oct 11 20:11 .
drwxr-xr-x 1 chyck 197609      0 Oct 10 17:03 ..
drwxr-xr-x 1 chyck 197609      0 Oct 11 20:18 .git
-rw-r--r-- 1 chyck 197609    186 Oct 11 20:18 .gitignore
drwxr-xr-x 1 chyck 197609      0 Oct 10 23:56 .pytest_cache
drwxr-xr-x 1 chyck 197609      0 Oct 11 20:18 .vs
-rw-r--r-- 1 chyck 197609 105719 Oct 11 12:25 DECISIONS.md
-rw-r--r-- 1 chyck 197609  62729 Oct 11 12:26 PLAN.md
-rw-r--r-- 1 chyck 197609  14301 Oct 11 13:34 README.md
drwxr-xr-x 1 chyck 197609      0 Oct 11 11:39 alerts_api
drwxr-xr-x 1 chyck 197609      0 Oct 11 11:43 archive
-rw-r--r-- 1 chyck 197609   5527 Oct 11 11:51 config.yaml
drwxr-xr-x 1 chyck 197609      0 Oct 11 12:18 data
drwxr-xr-x 1 chyck 197609      0 Oct 10 23:33 dataset_repo
-rw-r--r-- 1 chyck 197609     78 Oct 11 02:08 pyproject.toml
drwxr-xr-x 1 chyck 197609      0 Oct 11 12:19 reports
-rw-r--r-- 1 chyck 197609    134 Oct 11 02:59 requirements.txt
drwxr-xr-x 1 chyck 197609      0 Oct 11 20:11 reviews
drwxr-xr-x 1 chyck 197609      0 Oct 11 11:54 scripts
drwxr-xr-x 1 chyck 197609      0 Oct 10 23:24 src
drwxr-xr-x 1 chyck 197609      0 Oct 11 11:43 tests
f47ddec reorganize for review
7afa7a4 Stages 7-8: report, model x horizon table, check on fresh alerts.in.ua data
03b3c5b Closed feature access and knowledge-time check (D21); figures module; archive
dad94ba Add step 8 for validation with alerts.in.ua API
83270dc Fix typo in project name in README
6b14327 Merge pull request #2 from chuikomykhail-droid/stages-3-6
4c6e5d8 Stages 3-6: grid and targets, backtest with baselines, features, models
3a71c1b Merge pull request #1 from chuikomykhail-droid/stage2-review-refactor
4203bc2 Fix as-of leak from processor-invented alert ends (D16)
53e2373 Stage 2 review: channel outage mask, as-of history, refactor
6452885 Finish Stage 1b: proper mask stats and interval merging
782342d Update decision.md with new checks
157dc85 Add test for dataset loader
6de9f3d Complete Stage 1b: Implement dataset loader, unit merging, and uncertain status masking
bcb4b85 Fix formatting in PLAN.md
106ec45 Merge branch 'gemini-flash' into main: import EDA script, reports, config, requirements, and decisions
045793a Add .gitignore
1ad74e8 Revise data source checks and procedures in PLAN.md
9da2848 Create DECISIONS.md with project decision log
a9b8fe1 Revise PLAN.md with updated project details
920259e Track DECISIONS-gemini-flash.md in sync with DECISIONS.md
acb241d Complete Stage 0 and Stage 1: EDA, transition analysis, decisions, and plots
3a6224b Add .gitignore
46c2cb0 Enhance PLAN.md with new sections and clarifications
50ab7f7 Add project plan for air raid forecast MVP
6418ef0 initial commit
bdd5a95 Initial commit
ls: cannot access 'reviews/scratch': No such file or directory
archive:
README.md
stage1_gemini_flash
stage1b_scratch

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
see
… [обрезано: показано 3000 из 4004 символов]
```

</details>

<details><summary>🔧 Bash: Count document lines, show config files · 20:19</summary>

**Аргументы**

```bash
wc -l PLAN.md DECISIONS.md README.md reports/*.md && cat .gitignore requirements.txt pyproject.toml
```

**Результат**

```
424 PLAN.md
   704 DECISIONS.md
   147 README.md
   263 reports/api_check.md
   125 reports/backtest_h1.md
   125 reports/backtest_h3.md
   125 reports/backtest_h6.md
    36 reports/results.md
    36 reports/stage1_summary.md
    30 reports/stage2_summary.md
    65 reports/stage3_summary.md
  2080 total
.vs/
venv/
dataset_repo/
__pycache__/
*.pyc
.pytest_cache/
data/*.parquet
reviews/scratch/

# secrets: never in version control
alerts_api/token.txt
*.token
.env
data/raw/
pandas==3.0.6
numpy==2.5.3
matplotlib==3.11.2
pyyaml==6.0.3
scikit-learn==1.9.1
lightgbm==4.7.0
pytest==9.1.1
pyarrow==25.0.1
[tool.pytest.ini_options]
pythonpath = ["src", "tests"]
testpaths = ["tests"]
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

<details><summary>🔧 Read: DECISIONS.md · 20:19</summary>

**Аргументы**

```json
{
 "file_path": "d:\\Flash\\golova\\KSE_AI\\AAFS\\DECISIONS.md",
 "offset": 519,
 "limit": 200
}
```

**Результат**

```
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
548	- Выигрыш моделей виден **внутри областей**, где B1 почти ничего не добавляет к B0. PR-AUC LR против B1: Киев 0.63 против 0.34, Киевская область 0.55 против 0.34, Кировоградская 0.53 против 0.38, Полтавская 0.66 против 0.57. Там, где всё решает идентичность единицы (Су
… [обрезано: показано 3000 из 23581 символов]
```

</details>

<details><summary>🔧 Bash: Show README with line numbers · 20:19</summary>

**Аргументы**

```bash
cat -n README.md
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
    43	  каналу (нових постів немає); API alerts.in.ua — джерело з іншою обробко
… [обрезано: показано 3000 из 9904 символов]
```

</details>

<details><summary>🔧 Bash: Show results and h3 backtest reports · 20:20</summary>

**Аргументы**

```bash
cat -n reports/results.md && cat -n reports/backtest_h3.md
```

**Результат**

```
1	# Results: model x horizon (test part)
     2	
     3	Walk-forward with daily retraining on the test part (2026-08-10 to 2026-09-07, D14). Intervals: 95% percentile, 1000 bootstrap draws of whole days; differences are paired (same draws). Hyperparameters chosen on validation for each horizon (D20). Details per horizon: `backtest_h<h>.md`.
     4	
     5	## Metrics
     6	
     7	| h | Rows | Base rate | Model | PR-AUC | ROC-AUC | Brier | Log loss |
     8	|---|---|---|---|---|---|---|---|
     9	| 1 | 46,574 | 0.121 | B0 | 0.131 [0.114, 0.151] | 0.526 [0.485, 0.563] | 0.107 [0.097, 0.118] | 0.373 [0.344, 0.404] |
    10	| 1 | 46,574 | 0.121 | B1 | 0.398 [0.382, 0.418] | 0.830 [0.818, 0.844] | 0.088 [0.080, 0.098] | 0.287 [0.262, 0.318] |
    11	| 1 | 46,574 | 0.121 | B2 | 0.130 [0.113, 0.147] | 0.526 [0.503, 0.545] | 0.107 [0.097, 0.118] | 0.372 [0.344, 0.402] |
    12	| 1 | 46,574 | 0.121 | LR | 0.424 [0.401, 0.446] | 0.859 [0.848, 0.868] | 0.084 [0.077, 0.092] | 0.269 [0.250, 0.291] |
    13	| 1 | 46,574 | 0.121 | LGBM | 0.434 [0.409, 0.458] | 0.862 [0.853, 0.872] | 0.083 [0.077, 0.092] | 0.265 [0.247, 0.286] |
    14	| 3 | 46,270 | 0.255 | B0 | 0.272 [0.235, 0.307] | 0.525 [0.480, 0.563] | 0.191 [0.177, 0.207] | 0.572 [0.540, 0.607] |
    15	| 3 | 46,270 | 0.255 | B1 | 0.674 [0.652, 0.702] | 0.866 [0.854, 0.881] | 0.126 [0.117, 0.136] | 0.381 [0.354, 0.411] |
    16	| 3 | 46,270 | 0.255 | B2 | 0.253 [0.226, 0.279] | 0.498 [0.474, 0.519] | 0.192 [0.179, 0.208] | 0.575 [0.543, 0.610] |
    17	| 3 | 46,270 | 0.255 | LR | 0.692 [0.661, 0.722] | 0.882 [0.869, 0.895] | 0.120 [0.112, 0.129] | 0.367 [0.345, 0.391] |
    18	| 3 | 46,270 | 0.255 | LGBM | 0.701 [0.675, 0.726] | 0.883 [0.871, 0.895] | 0.119 [0.111, 0.128] | 0.360 [0.338, 0.384] |
    19	| 6 | 45,767 | 0.360 | B0 | 0.369 [0.324, 0.414] | 0.507 [0.458, 0.549] | 0.231 [0.220, 0.243] | 0.656 [0.632, 0.679] |
    20	| 6 | 45,767 | 0.360 | B1 | 0.814 [0.788, 0.841] | 0.896 [0.881, 0.913] | 0.125 [0.115, 0.135] | 0.386 [0.354, 0.418] |
    21	| 6 | 45,767 | 0.360 | B2 | 0.351 [0.316, 0.384] | 0.495 [0.478, 0.512] | 0.233 [0.221, 0.244] | 0.659 [0.635, 0.682] |
    22	| 6 | 45,767 | 0.360 | LR | 0.827 [0.793, 0.857] | 0.906 [0.890, 0.920] | 0.120 [0.111, 0.131] | 0.377 [0.353, 0.404] |
    23	| 6 | 45,767 | 0.360 | LGBM | 0.832 [0.805, 0.858] | 0.907 [0.892, 0.920] | 0.119 [0.110, 0.128] | 0.367 [0.343, 0.393] |
    24	
    25	## Difference from the best baseline (chosen on validation)
    26	
    27	| h | Reference | Model | PR-AUC | Log loss | Brier |
    28	|---|---|---|---|---|---|
    29	| 1 | B1 | LR | +0.026 [+0.011, +0.040] | -0.018 [-0.028, -0.010] | -0.004 [-0.006, -0.003] |
    30	| 1 | B1 | LGBM | +0.036 [+0.019, +0.050] | -0.022 [-0.033, -0.014] | -0.005 [-0.007, -0.003] |
    31	| 3 | B1 | LR | +0.018 [-0.003, +0.036] | -0.014 [-0.027, -0.000] | -0.006 [-0.011, -0.001] |
    32	| 3 | B1 | LGBM | +0.027 [+0.010, +0.041] | -0.021 [-0.033, -0.009] | -0.
… [обрезано: показано 3000 из 13389 символов]
```

</details>

<details><summary>🔧 Bash: Show API check report · 20:20</summary>

**Аргументы**

```bash
cat -n reports/api_check.md
```

**Результат**

```
1	# Check on fresh data: alerts.in.ua (stage 8)
     2	
     3	Generated by `scripts/api_check.py`. Decisions: DECISIONS.md, D22. The sources are not joined (D02): models are fitted once on the Vadimkin data and only predict here.
     4	
     5	## Download and adapter (8.1, 8.2)
     6	
     7	- Requests: 28, statuses {200: 28}; request times 2026-10-11T08:45:39.672979+00:00 to 2026-10-11T08:59:35.582412+00:00
     8	- Alerts downloaded (unique id): 16,532; by type {'air_raid': 16249, 'artillery_shelling': 282, 'urban_fights': 1}
     9	- air_raid by location type: {'raion': 14168, 'hromada': 932, 'city': 929, 'oblast': 220}
    10	- Oblast-wide records expanded to raions: 1; city and hromada records dropped: 1,644; open at download: 60
    11	- Raion titles not in the location table: none
    12	- Records in our schema: 14,389; locations of the units table found: 119 of 119
    13	
    14	Names: our English key, Ukrainian name used for matching, the English title of the API (an independent spelling, for the manual check):
    15	
    16	| Oblast | Raion (ours) | Ukrainian name | API title (en) | Name from |
    17	|---|---|---|---|---|
    18	| Cherkaska oblast | Cherkaskyi raion | Черкаський район | Cherkasy raion | official_data_uk |
    19	| Cherkaska oblast | Umanskyi raion | Уманський район | Uman raion | official_data_uk |
    20	| Cherkaska oblast | Zolotoniskyi raion | Золотоніський район | Zolotonosha raion | official_data_uk |
    21	| Cherkaska oblast | Zvenyhorodskyi raion | Звенигородський район | Zvenyhorodka raion | official_data_uk |
    22	| Chernihivska oblast | Chernihivskyi raion | Чернігівський район | Chernihiv raion | official_data_uk |
    23	| Chernihivska oblast | Koriukivskyi raion | Корюківський район | Koriukivka raion | official_data_uk |
    24	| Chernihivska oblast | Nizhynskyi raion | Ніжинський район | Nizhyn raion | official_data_uk |
    25	| Chernihivska oblast | Novhorod-Siverskyi raion | Новгород-Сіверський район | Novhorod-Siverskyi raion | official_data_uk |
    26	| Chernihivska oblast | Prylutskyi raion | Прилуцький район | Pryluky raion | official_data_uk |
    27	| Chernivetska oblast | Chernivetskyi raion | Чернівецький район | Chernivtsi raion | official_data_uk |
    28	| Chernivetska oblast | Dnistrovskyi raion | Дністровський район | Dnistrovskyi raion | official_data_uk |
    29	| Chernivetska oblast | Vyzhnytskyi raion | Вижницький район | Vyzhnytsia raion | official_data_uk |
    30	| Dnipropetrovska oblast | Dniprovskyi raion | Дніпровський район | Dnipro raion | official_data_uk |
    31	| Dnipropetrovska oblast | Kamianskyi raion | Кам’янський район | Kamianka raion | official_data_uk |
    32	| Dnipropetrovska oblast | Kryvorizkyi raion | Криворізький район | Kryvyi Rih raion | official_data_uk |
    33	| Dnipropetrovska oblast | Nikopolskyi raion | Нікопольський район | Nikopol raion | official_data_uk |
    34	| Dnipropetrovska oblast | Pavlohradskyi rai
… [обрезано: показано 3000 из 22238 символов]
```

</details>

<details><summary>🔧 Bash: List review prompts and their zones · 20:20</summary>

**Аргументы**

```bash
ls reviews/prompts && head -30 reviews/prompts/07*.md 2>/dev/null; for f in reviews/prompts/*.md; do echo "== $f"; sed -n '/Твоя зона/,/Что проверить/p' "$f" | head -20; done
```

**Результат**

```
01_stages0-1b.md
02_stage2.md
03_stage3.md
04_stages4-6.md
05_stage5-leakage.md
06_stage7.md
07_stage8.md
08_synthesis.md
# Ревью проекта AAFS: этап 8: проверка на свежих данных alerts.in.ua

Ты — независимый критический ревьюер. Параллельно с тобой другие агенты проверяют другие этапы того же проекта. Твоя зона — этап 8: адаптер alerts.in.ua, профиль источника, триангуляция через волонтёрский ряд, замороженные модели, проверка утечки на периоде API. На соседние этапы смотри только тогда, когда без этого не понять твой.

## Проект

- Репозиторий — текущая папка (`AAFS`), ветка `stages-7-8`. Python-проект: прогноз воздушных тревог в Украине по районам. Для каждой единицы (район; Киев — одна единица), где в момент `t` (каждый час) тихо, модель выдаёт вероятность того, что тревога начнётся в `(t, t+h]`, h = 1, 3, 6 (основной — 3).
- Данные — снимок датасета Vadimkin (`dataset_repo/`, коммит `58ee75b`). Официальный ряд заканчивается 2026-09-07. Тест — 2026-08-10…2026-09-07, walk-forward с ежесуточным переобучением. Этап 8 — проверка на данных alerts.in.ua за сентябрь–октябрь.
- Это тестовое задание с дедлайном 12.10.2026 23:59 по Киеву. Проверяющие оценивают процесс: пойманные ошибки, обоснованность решений, отсутствие утечки из будущего. Найденная проблема ценна, даже если её не успеют исправить: тогда она уйдёт в раздел ограничений.
- Документы: `PLAN.md` (правила работы 1–13; у каждого этапа «Исходное задание» и «Как сделано»), `DECISIONS.md` (решения D00–D22, справочные цифры, журнал пойманных ошибок ИИ), `README.md` (на украинском), отчёты в `reports/`.

Сначала прочитай раздел «Правила работы» в `PLAN.md`, описание своего этапа в `PLAN.md` и разделы `DECISIONS.md`: D02, D22; в PLAN — этап 8 и «Вне MVP» (риски склейки источников). Код и тесты своей зоны читай целиком, а не выборочно.

## Твоя зона: файлы

- `src/alerts/ingest/alerts_in_ua.py`, `src/alerts/api_check.py`.
- `scripts/api_check.py` и `scripts/fetch_alerts_in_ua.py` — **только читать, не запускать.**
- `config.yaml`: разделы `api`, `volunteer`, `processor.enabled`.
- `data/alerts_in_ua_locations.csv`, `reports/api_check.md`, `reports/figures/api_vs_vadimkin.png`.
- Сырые ответы API `data/raw/alerts_in_ua/*.json` — читать можно, в сеть не ходить.

`scripts/api_check.py` пересобирает всё (2–3 минуты) и пишет в `reports/api_check.md` и `data/alerts_in_ua_locations.csv`. Не запускай его: для пересчёта копируй нужные куски в scratch, без записи файлов.

## Что проверить

1. **Адаптер.**
   - Сопоставление 119 локаций: апострофы, Киев, переименования.
   - Записи уровня области разворачиваются на районы. Нет ли двойного счёта, если для тех же районов есть и районные записи?
   - Тревоги, открытые на момент скачивания; отброшенные типы и уровни; объединение по `id` и `updated_at`.
2. **Окно `month_ago`.**
== reviews/prompts/01_stages0-1b.md
Ты — независимый критический ревьюер. Параллельно с тобой другие агенты проверяют другие этапы того же проекта. Твоя зона 
… [обрезано: показано 3000 из 17749 символов]
```

</details>

<details><summary>🔧 Bash: Count code lines and show run_all.py · 20:20</summary>

**Аргументы**

```bash
wc -l src/alerts/*.py src/alerts/*/*.py scripts/*.py tests/*.py && cat -n scripts/run_all.py
```

**Результат**

```
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
     0 src/alerts/ingest/__init__.py
   127 src/alerts/ingest/alerts_in_ua.py
    47 src/alerts/ingest/vadimkin.py
    18 src/alerts/models/__init__.py
    81 src/alerts/models/baselines.py
    94 src/alerts/models/learned.py
   214 scripts/api_check.py
   123 scripts/fetch_alerts_in_ua.py
    42 scripts/fetch_data.py
   100 scripts/run_all.py
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
  3791 total
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
    38	    failed = bool(repor
… [обрезано: показано 3000 из 6662 символов]
```

</details>

<details><summary>🔧 Bash: Show evaluation.py and config.yaml · 20:20</summary>

**Аргументы**

```bash
cat -n src/alerts/evaluation.py && cat -n config.yaml
```

**Результат**

```
1	"""Backtest evaluation (PLAN stages 4 and 6; D18): run models, bootstrap, per-oblast tables, calibration.
     2	
     3	The reference for paired differences is chosen on the validation part only (lowest log loss among
     4	the baselines), never on the test part (PLAN rule 6).
     5	"""
     6	import logging
     7	
     8	import numpy as np
     9	import pandas as pd
    10	
    11	from alerts import backtest, figures
    12	from alerts.metrics import METRICS, bootstrap, calibration, score
    13	
    14	logger = logging.getLogger(__name__)
    15	
    16	
    17	def evaluate(data: pd.DataFrame, h: int, models: dict, baselines: list, cfg: dict) -> dict:
    18	    """Backtest every model on val and test; return predictions and all tables."""
    19	    preds = backtest.run(data, h, models, cfg)
    20	    names = list(models)
    21	    bs = cfg['bootstrap']
    22	    val = preds[preds['part'] == 'val']
    23	    reference = min(baselines, key=lambda m: score(val['y'], val[f'p_{m}'])['log_loss'])
    24	    tables = {part: bootstrap(preds[preds['part'] == part], names, bs['n_reps'], bs['seed'], bs['ci'], reference)
    25	              for part in ['val', 'test']}
    26	    test = preds[preds['part'] == 'test']
    27	    vs_lr = (bootstrap(test, names, bs['n_reps'], bs['seed'], bs['ci'], 'LR') if 'LR' in names else None)
    28	    by_oblast = _by_oblast(test, names, reference, bs)
    29	    calib = {m: calibration(test['y'].to_numpy(), test[f'p_{m}'].to_numpy()) for m in names}
    30	    return {'h': h, 'preds': preds, 'reference': reference, 'tables': tables, 'vs_lr': vs_lr,
    31	            'by_oblast': by_oblast, 'calibration': calib, 'models': names,
    32	            'importance': _importance(data, h, models, cfg) if 'LGBM' in models else None}
    33	
    34	
    35	def _importance(data: pd.DataFrame, h: int, models: dict, cfg: dict) -> pd.Series:
    36	    """Gain importance of the LightGBM model of the last test day (PLAN: gain, not split counts)."""
    37	    last = backtest.days(cfg, 'test')[-1]
    38	    ycol = f'y_{h}'
    39	    train = data[(data['t'] <= last - pd.Timedelta(hours=h)) & data[ycol].notna()]
    40	    return models['LGBM']().fit(train, train[ycol].to_numpy(dtype=float)).gain_importance()
    41	
    42	
    43	def _by_oblast(test: pd.DataFrame, names: list, reference: str, bs: dict) -> pd.DataFrame:
    44	    rows = []
    45	    for ob, g in test.groupby('oblast'):
    46	        b = bootstrap(g, names, bs['n_reps_oblast'], bs['seed'], bs['ci'], reference)
    47	        b = b[b['metric'].isin(['pr_auc', 'brier'])].assign(oblast=ob, rows=len(g), positives=int(g['y'].sum()))
    48	        rows.append(b)
    49	    return pd.concat(rows, ignore_index=True)
    50	
    51	
    52	def write_report(res: dict, cfg: dict, out_dir, extra_md: str = '') -> None:
    53	    h, ref, names = res['h'], res['reference'], res['models']
    54	    lines = [f'# 
… [обрезано: показано 3000 из 15947 символов]
```

</details>

<details><summary>🔧 Bash: Show fetch_data, config, report modules · 20:20</summary>

**Аргументы**

```bash
cat -n scripts/fetch_data.py && cat -n src/alerts/config.py && cat -n src/alerts/report.py
```

**Результат**

```
1	"""Get the pinned dataset snapshot (D01): clone if missing, check out the commit, verify SHA-256."""
     2	import logging
     3	import subprocess
     4	import sys
     5	from pathlib import Path
     6	
     7	sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
     8	
     9	from alerts.config import ROOT, load_config  # noqa: E402
    10	from alerts.ingest.vadimkin import file_sha256  # noqa: E402
    11	
    12	logger = logging.getLogger(__name__)
    13	
    14	
    15	def _git(*args):
    16	    subprocess.run(['git', *args], check=True)
    17	
    18	
    19	def ensure_snapshot(cfg: dict) -> Path:
    20	    ds = cfg['dataset']
    21	    target, repo = ROOT / ds['path'], ROOT / ds['repo_dir']
    22	    if target.exists() and file_sha256(target) == ds['sha256']:
    23	        logger.info(f'Snapshot present and verified: {target}')
    24	        return target
    25	
    26	    if not (repo / '.git').exists():
    27	        logger.info(f'Cloning {ds["repo_url"]} into {repo}')
    28	        _git('clone', ds['repo_url'], str(repo))
    29	    else:
    30	        _git('-C', str(repo), 'fetch', 'origin')
    31	    _git('-C', str(repo), 'checkout', '--quiet', ds['commit'])
    32	
    33	    got = file_sha256(target)
    34	    if got != ds['sha256']:
    35	        raise ValueError(f'SHA-256 mismatch after checkout of {ds["commit"]}: {got}')
    36	    logger.info(f'Snapshot {ds["commit"][:7]} checked out and verified')
    37	    return target
    38	
    39	
    40	if __name__ == '__main__':
    41	    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    42	    ensure_snapshot(load_config())
     1	"""Loading config.yaml. Every threshold and date lives there, none in the code (PLAN 1б.6)."""
     2	from pathlib import Path
     3	
     4	import pandas as pd
     5	import yaml
     6	
     7	ROOT = Path(__file__).resolve().parents[2]
     8	
     9	_REQUIRED = {
    10	    'dataset': ['repo_url', 'commit', 'repo_dir', 'path', 'sha256', 'path_uk', 'sha256_uk'],
    11	    'volunteer': ['commit', 'path', 'sha256'],
    12	    'periods': ['work_start', 'warmup_end', 'train_end', 'val_end'],
    13	    'scope': ['excluded_oblasts', 'input_only_oblasts', 'oblast_level_units'],
    14	    'thresholds': ['pause_merge_min', 'long_alert_hours', 'clone_jaccard',
    15	                   'similar_pairs_report', 'outage_gap_hours'],
    16	    'processor': ['enabled', 'fake_end_duration_s', 'fake_end_next_start_h'],
    17	    'history': ['max_open_hours'],
    18	    'geo': ['path', 'sha256', 'vertex_decimals', 'min_shared_vertices', 'renames'],
    19	    'backtest': ['horizons', 'baselines', 'models'],
    20	    'models': ['threads', 'seed', 'lr', 'lgbm'],
    21	    'baselines': ['b1_window_days', 'prior_strength'],
    22	    'bootstrap': ['n_reps', 'n_reps_oblast', 'ci', 'seed'],
    23	    'leakage_check': ['cuts', 'horizon'],
    24	    'report': ['forecast_units', '
… [обрезано: показано 3000 из 17347 символов]
```

</details>

<details><summary>🔧 Bash: Show stage summaries and JSON reports · 20:20</summary>

**Аргументы**

```bash
cat reports/stage1_summary.md reports/stage2_summary.md reports/stage3_summary.md && cat reports/leakage_check.json && cat reports/tuning_h*.json
```

**Результат**

```
# Stage 1 summary

Generated by `scripts/run_all.py`. Reference values: DECISIONS.md, "Справочные цифры".

| Quantity | Value | Reference | |
|---|---|---|---|
| rows raw / dedup / cleaned | 299275 / 185430 / 185428 | 299275 / 185430 / 185428 | ok |
| last start / last end in the file (UTC) | 2026-09-07 05:28:22 / 2026-09-07 05:39:33 | 2026-09-07 05:28:22 / 2026-09-07 05:39:33 | ok |
| scope records, start >= work_start | 80194 | 80194 | ok |
| alerts per location: min / p10 / median / p90 / max | 87 / 92 / 604 / 1567 / 2253 | 87 / 92 / 604 / 1567 / 2253 | ok |
| duration, min: median / p75 / p99 | 47 / 113 / 760 | 47 / 113 / 760 | ok |
| alerts > 24 h / > 72 h / > 24 h in test | 119 / 22 / 33 | 119 / 22 / 33 | ok |
| records of exactly 3600 s / in test | 82 / 21 | 82 / 21 | ok |
| overlaps within a location | 0 | 0 | ok |
| locations / units | 111 / 104 | 111 / 104 | ok |
| channel outages (D15) | 2026-08-29 05:55:28 -> 2026-09-02 13:48:04 | 2026-08-29 05:55:28 -> 2026-09-02 13:48:04 | ok |
| grid rows h=3: train / val / test (D17) | 510642 / 57865 / 48028 | 510642 / 57865 / 48028 | ok |
| base rate train: h=1 / h=3 / h=6 (D17) | 0.089 / 0.209 / 0.321 | 0.089 / 0.209 / 0.321 | ok |

## Mask (D10, D15)

Counts of masked source records and of merged unit-level intervals (target units, records overlapping the working period).

| Rule | Locations | Locations in test | Units | Units in test |
|---|---|---|---|---|
| long_24h | 119 | 33 | 66 | 21 |
| fake_1h | 76 | 21 | 71 | 19 |

Masked share of target unit-hours, %:

| Reason | Train | Val | Test |
|---|---|---|---|
| long_24h | 0.23 | 0.15 | 2.70 |
| fake_1h | 0.24 | 0.23 | 2.82 |
| outage | 0.00 | 0.00 | 15.46 |
| total | 0.46 | 0.38 | 15.93 |
# Stage 2 summary

Generated by `scripts/run_all.py`.

## Records to intervals

- Source records overlapping the working period: 86,455 (target 80,159, input 6,296)
- Records outside the period, all time: 15,114 (not used)
- Segments (union of overlapping records): 73,737; records absorbed by the union: 12,718
- Episodes (pauses <= 15 min bridged): 66,644; pauses bridged: 7,093
- Target units: hours under alert 115,749 by segments, 116,617 by episodes (+868 h of bridged pauses)

## Uncertain episodes (target units, by start)

| Part | Episodes | Uncertain |
|---|---|---|
| train | 51,227 | 80 |
| val | 8,013 | 17 |
| test | 6,827 | 40 |

## As-of state on the hourly grid (D12, D16)

- Hourly moments from warmup_end to data_end: 7,128
- Bridged pauses: episode says "alert", recorded segments say "quiet": 791 unit-moments, 425 moments (6.0%)
- Invented ends: recorded segments say "quiet", but no all-clear had been seen, so AlertHistory keeps the alert open: 1,046 unit-moments, 153 moments (2.1%)
- Features read the state only through AlertHistory

## Outages (D15)

- 2026-08-29 05:55:28+00:00 -> 2026-09-02 13:48:04+00:00 (4 days 07:52:36)
# Stage 3 summary

Generated by `scripts/run_all.py`. D
… [обрезано: показано 3000 из 7791 символов]
```

</details>

<details><summary>🔧 Bash: Show git log with file stats · 20:21</summary>

**Аргументы**

```bash
git log --stat --format='==== %h %ad %an %s' --date=iso | head -250
```

**Результат**

```
==== f47ddec 2026-10-11 20:18:17 +0300 Chuiko Mykhail reorganize for review

 .gitignore                           |  1 +
 reviews/prompts/01_stages0-1b.md     | 91 ++++++++++++++++++++++++++++++++++
 reviews/prompts/02_stage2.md         | 83 +++++++++++++++++++++++++++++++
 reviews/prompts/03_stage3.md         | 91 ++++++++++++++++++++++++++++++++++
 reviews/prompts/04_stages4-6.md      | 94 ++++++++++++++++++++++++++++++++++++
 reviews/prompts/05_stage5-leakage.md | 84 ++++++++++++++++++++++++++++++++
 reviews/prompts/06_stage7.md         | 92 +++++++++++++++++++++++++++++++++++
 reviews/prompts/07_stage8.md         | 88 +++++++++++++++++++++++++++++++++
 reviews/prompts/08_synthesis.md      | 35 ++++++++++++++
 9 files changed, 659 insertions(+)
==== 7afa7a4 2026-10-11 13:34:14 +0300 Chuiko Mykhail Stages 7-8: report, model x horizon table, check on fresh alerts.in.ua data

 DECISIONS.md                         |  67 +++++++++
 PLAN.md                              |  25 +++-
 README.md                            | 149 +++++++++++++++++++-
 config.yaml                          |  24 +++-
 data/alerts_in_ua_locations.csv      | 120 ++++++++++++++++
 reports/api_check.md                 | 263 +++++++++++++++++++++++++++++++++++
 reports/backtest_h1.md               | 125 +++++++++++++++++
 reports/backtest_h3.md               |  28 ++--
 reports/backtest_h6.md               | 125 +++++++++++++++++
 reports/figures/api_vs_vadimkin.png  | Bin 0 -> 91730 bytes
 reports/figures/calibration_h1.png   | Bin 0 -> 94173 bytes
 reports/figures/calibration_h6.png   | Bin 0 -> 103164 bytes
 reports/figures/forecast_vs_fact.png | Bin 0 -> 240579 bytes
 reports/results.md                   |  36 +++++
 reports/tuning_h1.json               |  12 ++
 reports/tuning_h6.json               |  12 ++
 scripts/api_check.py                 | 214 ++++++++++++++++++++++++++++
 scripts/fetch_alerts_in_ua.py        | 123 ++++++++++++++++
 scripts/run_all.py                   |  14 +-
 src/alerts/api_check.py              | 193 +++++++++++++++++++++++++
 src/alerts/config.py                 |   8 +-
 src/alerts/evaluation.py             |  32 +++++
 src/alerts/figures.py                |  60 ++++++++
 src/alerts/grid.py                   |   5 +-
 src/alerts/ingest/alerts_in_ua.py    | 127 +++++++++++++++++
 src/alerts/mask.py                   |   2 +-
 src/alerts/processor.py              |   2 +
 tests/conftest.py                    |   8 +-
 28 files changed, 1743 insertions(+), 31 deletions(-)
==== 03b3c5b 2026-10-11 11:43:57 +0300 Chuiko Mykhail Closed feature access and knowledge-time check (D21); figures module; archive

 .gitignore                                         |   7 +-
 DECISIONS.md                                       |  27 +++
 archive/README.md                                  |  10 ++
 .../stage1_gemini_flash/DECISIONS-gemini-flash.md  |   0
 .../alert_duration_distribution.png                | Bin
 .../stage1_gemini_flash/eda_stage1.py             
… [обрезано: показано 3000 из 13564 символов]
```

</details>

<details><summary>🔧 Bash: Show backtest_h3.md diffs in recent commits · 20:21</summary>

**Аргументы**

```bash
git show 7afa7a4 -- reports/backtest_h3.md | head -80; git show 03b3c5b --stat -- reports/ ; git show 03b3c5b -- reports/backtest_h3.md | head -60
```

**Результат**

```
commit 7afa7a4425a92b1143d355a174d9a1feb22ac4bf
Author: Chuiko Mykhail <chuikomykhail@gmail.com>
Date:   Sun Oct 11 13:34:14 2026 +0300

    Stages 7-8: report, model x horizon table, check on fresh alerts.in.ua data
    
    Stage 7: backtests for h = 1, 3, 6 (LightGBM beats B1 on all: PR-AUC
    +0.036 / +0.027 / +0.018); reports/results.md; calibration per horizon;
    forecast-vs-fact figure; README (Ukrainian).
    
    Stage 8 (D22): scripts/fetch_alerts_in_ua.py (token only from a
    git-ignored file or env, header only, 31 s pause, stop on 401/403);
    adapter matching all 119 locations through official_data_uk names
    (apostrophe U+2019 vs U+0027 normalised; Kyiv is type oblast in the API);
    processor rules switched off by config; comparison of sources and
    triangulation with the volunteer series; frozen models with a B1
    refitted on API data as the fair reference; leakage checks on the API
    period. Raw API data stay out of git.
    
    DECISIONS: D22, AI error log rows 24-27; PLAN: stages 7-8 done.
    
    Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>

diff --git a/reports/backtest_h3.md b/reports/backtest_h3.md
index a8d3850..be871d3 100644
--- a/reports/backtest_h3.md
+++ b/reports/backtest_h3.md
@@ -109,17 +109,17 @@ Fitted on rows with t <= train_end - h, scored on the validation rows; the lowes
 
 | model | C | num_leaves | min_child_samples | half_life_days | n_estimators | log_loss | pr_auc | brier | seconds |
 |---|---|---|---|---|---|---|---|---|---|
-| LGBM |  | 63 | 200 | 28 | 84 | 0.3867 | 0.6924 | 0.1273 | 4.3 |
-| LGBM |  | 15 | 1000 | 28 | 104 | 0.3869 | 0.6916 | 0.1273 | 3.5 |
-| LGBM |  | 15 | 200 | 28 | 123 | 0.3874 | 0.6896 | 0.1275 | 3.8 |
-| LGBM |  | 63 | 1000 | 28 | 71 | 0.3877 | 0.6920 | 0.1273 | 4.2 |
-| LGBM |  | 15 | 1000 |  | 107 | 0.3881 | 0.6929 | 0.1276 | 3.5 |
-| LGBM |  | 15 | 200 |  | 131 | 0.3887 | 0.6912 | 0.1279 | 3.1 |
-| LGBM |  | 63 | 1000 |  | 101 | 0.3890 | 0.6912 | 0.1281 | 4.6 |
-| LGBM |  | 63 | 200 |  | 103 | 0.3903 | 0.6897 | 0.1286 | 4.5 |
-| LR | 0.1000 |  |  |  |  | 0.3873 | 0.6829 | 0.1276 | 4.8 |
-| LR | 1.0000 |  |  | 28 |  | 0.3874 | 0.6841 | 0.1280 | 5.5 |
-| LR | 0.0100 |  |  |  |  | 0.3877 | 0.6785 | 0.1273 | 5.9 |
-| LR | 1.0000 |  |  |  |  | 0.3878 | 0.6831 | 0.1279 | 4.5 |
-| LR | 0.1000 |  |  | 28 |  | 0.3881 | 0.6790 | 0.1280 | 5.1 |
-| LR | 0.0100 |  |  | 28 |  | 0.3919 | 0.6706 | 0.1289 | 3.7 |
+| LGBM |  | 63 | 200 | 28 | 84 | 0.3867 | 0.6924 | 0.1273 | 3.4 |
+| LGBM |  | 15 | 1000 | 28 | 104 | 0.3869 | 0.6916 | 0.1273 | 2.8 |
+| LGBM |  | 15 | 200 | 28 | 123 | 0.3874 | 0.6896 | 0.1275 | 3.0 |
+| LGBM |  | 63 | 1000 | 28 | 71 | 0.3877 | 0.6920 | 0.1273 | 3.4 |
+| LGBM |  | 15 | 1000 |  | 107 | 0.3881 | 0.6929 | 0.1276 | 2.7 |
+| LGBM |  | 15 | 200 |  | 131 | 0.3887 | 0.6912 | 0.1279 | 2.9 |
+| LGBM |  | 63 | 1000 |  | 101 | 0.3890 | 0.6912 | 0.1281 | 3.7 |
+| LGBM |  | 63 | 200 |  | 103 | 0.3903 | 0.6897 | 0.1286 | 3.6 |
+| LR | 0.1000 |  |  |  
… [обрезано: показано 3000 из 8028 символов]
```

</details>

<details><summary>🔧 Bash: Show figures module · 20:21</summary>

**Аргументы**

```bash
cat -n src/alerts/figures.py
```

**Результат**

```
1	"""All figures of the reports (data, clones, outage, calibration). Numbers and tables live elsewhere:
     2	alerts.report (stage summaries) and alerts.evaluation (backtest tables).
     3	
     4	Palette and marks follow one design method: the first three validated categorical slots, thin
     5	marks, recessive grid, text in ink colours, never in series colours.
     6	"""
     7	import matplotlib
     8	
     9	matplotlib.use('Agg')
    10	import matplotlib.pyplot as plt  # noqa: E402
    11	import matplotlib.ticker  # noqa: E402
    12	import numpy as np  # noqa: E402
    13	import pandas as pd  # noqa: E402
    14	
    15	from alerts.config import ts  # noqa: E402
    16	from alerts.intervals import episodes  # noqa: E402
    17	from alerts.scope import ROLE_TARGET  # noqa: E402
    18	
    19	# Reference palette of the dataviz method: first three categorical slots (validated all-pairs)
    20	SURFACE, INK, INK_2, GRID, BAND = '#fcfcfb', '#0b0b0b', '#52514e', '#e4e3df', '#d9d8d3'
    21	SERIES = ['#2a78d6', '#eb6834', '#1baf7a']
    22	
    23	
    24	def style(ax, grid_axis='y'):
    25	    ax.set_facecolor(SURFACE)
    26	    for side in ['top', 'right']:
    27	        ax.spines[side].set_visible(False)
    28	    for side in ['left', 'bottom']:
    29	        ax.spines[side].set_color(GRID)
    30	    ax.tick_params(colors=INK_2, labelsize=9, length=0)
    31	    ax.grid(axis=grid_axis, color=GRID, linewidth=0.8)
    32	    ax.set_axisbelow(True)
    33	
    34	
    35	def title(fig, title, subtitle):
    36	    fig.text(0.01, 0.985, title, ha='left', va='top', fontsize=13, color=INK, weight='bold')
    37	    fig.text(0.01, 0.94, subtitle, ha='left', va='top', fontsize=9.5, color=INK_2)
    38	
    39	
    40	def save(fig, file):
    41	    fig.savefig(file, dpi=150, facecolor=SURFACE)
    42	    plt.close(fig)
    43	
    44	
    45	def stage_figures(art, cfg, out) -> None:
    46	    """Figures of stages 1-2 (data, clones, outage) into `out`."""
    47	    work_start, data_end = ts(cfg['periods']['work_start']), ts(cfg['data_end'])
    48	    _fig_levels(art.df, work_start, out / 'level_transition.png')
    49	    _fig_units(art, cfg, out / 'alerts_per_unit.png')
    50	    _fig_durations(art, cfg, out / 'durations.png')
    51	    _fig_jaccard(art.pairs, cfg['thresholds']['clone_jaccard'], cfg['thresholds']['similar_pairs_report'],
    52	                 out / 'jaccard.png')
    53	    _fig_outage(art, cfg, out / 'outage.png')
    54	
    55	
    56	def _fig_levels(df, work_start, file):
    57	    d = df[df['started_at'] >= pd.Timestamp('2024-01-01', tz='UTC')]
    58	    month = d['started_at'].dt.tz_localize(None).dt.to_period('M')
    59	    share = pd.crosstab(month, d['level'], normalize='index')[['raion', 'oblast', 'hromada']]
    60	    x = share.index.to_timestamp()
    61	    fig, ax = plt.subplots(figsize=(10, 4.8))
    62	    fig.subplots_adjust(top=0.82, lef
… [обрезано: показано 3000 из 16345 символов]
```

</details>

<details><summary>🔧 Read: reports/figures/calibration_h3.png · 20:21</summary>

**Аргументы**

```json
{
 "file_path": "d:\\Flash\\golova\\KSE_AI\\AAFS\\reports\\figures\\calibration_h3.png"
}
```

**Результат**

```
[изображение опущено]
```

</details>

<details><summary>🔧 Read: reports/figures/calibration_h1.png · 20:21</summary>

**Аргументы**

```json
{
 "file_path": "d:\\Flash\\golova\\KSE_AI\\AAFS\\reports\\figures\\calibration_h1.png"
}
```

**Результат**

```
[изображение опущено]
```

</details>

<details><summary>🔧 Read: reports/figures/calibration_h6.png · 20:21</summary>

**Аргументы**

```json
{
 "file_path": "d:\\Flash\\golova\\KSE_AI\\AAFS\\reports\\figures\\calibration_h6.png"
}
```

**Результат**

```
[изображение опущено]
```

</details>

<details><summary>🔧 Read: reports/figures/forecast_vs_fact.png · 20:21</summary>

**Аргументы**

```json
{
 "file_path": "d:\\Flash\\golova\\KSE_AI\\AAFS\\reports\\figures\\forecast_vs_fact.png"
}
```

**Результат**

```
[изображение опущено]
```

</details>

<details><summary>🔧 Read: reports/figures/outage.png · 20:21</summary>

**Аргументы**

```json
{
 "file_path": "d:\\Flash\\golova\\KSE_AI\\AAFS\\reports\\figures\\outage.png"
}
```

**Результат**

```
[изображение опущено]
```

</details>

<details><summary>🔧 Read: reports/figures/durations.png · 20:21</summary>

**Аргументы**

```json
{
 "file_path": "d:\\Flash\\golova\\KSE_AI\\AAFS\\reports\\figures\\durations.png"
}
```

**Результат**

```
[изображение опущено]
```

</details>

<details><summary>🔧 Read: reports/figures/alerts_per_unit.png · 20:21</summary>

**Аргументы**

```json
{
 "file_path": "d:\\Flash\\golova\\KSE_AI\\AAFS\\reports\\figures\\alerts_per_unit.png"
}
```

**Результат**

```
[изображение опущено]
```

</details>

<details><summary>🔧 Read: reports/figures/jaccard.png · 20:21</summary>

**Аргументы**

```json
{
 "file_path": "d:\\Flash\\golova\\KSE_AI\\AAFS\\reports\\figures\\jaccard.png"
}
```

**Результат**

```
[изображение опущено]
```

</details>

<details><summary>🔧 Read: reports/figures/level_transition.png · 20:22</summary>

**Аргументы**

```json
{
 "file_path": "d:\\Flash\\golova\\KSE_AI\\AAFS\\reports\\figures\\level_transition.png"
}
```

**Результат**

```
[изображение опущено]
```

</details>

<details><summary>🔧 Read: reports/figures/api_vs_vadimkin.png · 20:22</summary>

**Аргументы**

```json
{
 "file_path": "d:\\Flash\\golova\\KSE_AI\\AAFS\\reports\\figures\\api_vs_vadimkin.png"
}
```

**Результат**

```
[изображение опущено]
```

</details>

<details><summary>🔧 Bash: Show leakage module and leakage tests · 20:22</summary>

**Аргументы**

```bash
cat -n src/alerts/leakage.py tests/test_leakage.py tests/test_knowledge.py tests/conftest.py
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
    47	    kept
… [обрезано: показано 3000 из 15292 символов]
```

</details>

<details><summary>🔧 Bash: Show backtest and pipeline, find backtest tests · 20:22</summary>

**Аргументы**

```bash
cat -n src/alerts/backtest.py src/alerts/pipeline.py && grep -rn "backtest" tests/ | head
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
    
… [обрезано: показано 3000 из 8238 символов]
```

</details>

<details><summary>🔧 Bash: Show tuning, metrics, model registry · 20:23</summary>

**Аргументы**

```bash
cat -n src/alerts/tuning.py src/alerts/metrics.py src/alerts/models/__init__.py
```

**Результат**

```
1	"""Hyperparameters chosen once on the validation part (PLAN stage 6, D20), never on the test part.
     2	
     3	Every candidate is fitted on the rows with t <= train_end - h (labels known when validation starts)
     4	and scored by log loss on the validation rows. For LightGBM the number of trees comes from early
     5	stopping on the same validation rows; the backtest then uses that fixed number.
     6	"""
     7	import itertools
     8	import logging
     9	import time
    10	
    11	import pandas as pd
    12	
    13	from alerts.config import ts
    14	from alerts.metrics import score
    15	from alerts.models.learned import GBMModel, LogisticModel
    16	
    17	logger = logging.getLogger(__name__)
    18	
    19	
    20	def tune(data: pd.DataFrame, h: int, cfg: dict) -> tuple[dict, pd.DataFrame]:
    21	    ycol = f'y_{h}'
    22	    lab = data[data[ycol].notna()]
    23	    train = lab[lab['t'] <= ts(cfg['periods']['train_end']) - pd.Timedelta(hours=h)]
    24	    val = lab[lab['part'] == 'val']
    25	    y, yv = train[ycol].to_numpy(dtype=float), val[ycol].to_numpy(dtype=float)
    26	    m = cfg['models']
    27	    rows = []
    28	
    29	    for C, hl in itertools.product(m['lr']['grid']['C'], m['lr']['grid']['half_life_days']):
    30	        params = {'C': C, 'half_life_days': hl}
    31	        t0 = time.time()
    32	        p = LogisticModel(cfg, params).fit(train, y).predict_proba(val)
    33	        rows.append({'model': 'LR', **params, **score(yv, p), 'seconds': time.time() - t0})
    34	
    35	    g = m['lgbm']['grid']
    36	    for nl, mcs, hl in itertools.product(g['num_leaves'], g['min_child_samples'], g['half_life_days']):
    37	        params = {'num_leaves': nl, 'min_child_samples': mcs, 'half_life_days': hl,
    38	                  'n_estimators': m['lgbm']['max_estimators']}
    39	        t0 = time.time()
    40	        model = GBMModel(cfg, params).fit(train, y, eval_set=(val, yv))
    41	        params['n_estimators'] = int(model.model_.best_iteration_ or m['lgbm']['max_estimators'])
    42	        rows.append({'model': 'LGBM', **params, **score(yv, model.predict_proba(val)), 'seconds': time.time() - t0})
    43	
    44	    table = pd.DataFrame(rows)
    45	    best = {}
    46	    for name, keys in [('LR', ['C', 'half_life_days']),
    47	                       ('LGBM', ['num_leaves', 'min_child_samples', 'half_life_days', 'n_estimators'])]:
    48	        r = table[table['model'] == name].sort_values('log_loss').iloc[0]
    49	        best[name] = {k: _value(k, r[k]) for k in keys}
    50	        logger.info(f'h={h} tuned {name}: {best[name]} (val log loss {r["log_loss"]:.4f})')
    51	    return best, table
    52	
    53	
    54	def _value(key, v):
    55	    if pd.isna(v):
    56	        return None
    57	    return float(v) if key == 'C' else int(v)
    58	"""Metrics, day-block bootstrap and calibration (PLAN stage 4, D18).
    59	
    60	
… [обрезано: показано 3000 из 8478 символов]
```

</details>

<details><summary>🔧 Bash: Check Python env versions and archive contents · 20:23</summary>

**Аргументы**

```bash
which python; python --version; python -m pip list 2>/dev/null | grep -i -E "pandas|numpy|matplotlib|pyyaml|scikit|lightgbm|pytest|pyarrow|scipy" ; ls venv 2>/dev/null | head; cat archive/README.md; ls -R archive | head -30
```

**Результат**

```
/d/Soft/miniconda/python
Python 3.12.9
lightgbm                     4.7.0
matplotlib                   3.11.2
numpy                        2.5.3
pandas                       3.0.6
pyarrow                      25.0.1
pytest                       9.1.1
PyYAML                       6.0.3
scikit-learn                 1.9.1
scipy                        1.18.1
# Архив

Файлы ранних этапов, которые конвейер больше не создаёт и не использует. Они сохранены как часть
истории работы (PLAN, «Пойманные ошибки ИИ» в DECISIONS.md), но не поддерживаются: пути и API в них
устарели, запускать их не нужно. Всё актуальное строит `python scripts/run_all.py`.

| Папка | Что это | Чем заменено |
|---|---|---|
| `stage1_gemini_flash/` | Разведка этапа 1 в ветке агента Gemini Flash: `eda_stage1.py`, его журнал решений и четыре графика | `DECISIONS.md` (D00–D14), `reports/stage1_summary.md`, `reports/figures/` |
| `stage1b_scratch/` | Одноразовый скрипт агента этапа 1б для печати статистики масок (импортирует `src.alerts…`, старый API) | `reports/stage1_summary.md`, `src/alerts/mask.py` |
archive:
README.md
stage1_gemini_flash
stage1b_scratch

archive/stage1_gemini_flash:
DECISIONS-gemini-flash.md
alert_duration_distribution.png
eda_stage1.py
pauses_distribution.png
raion_alert_frequencies.png
transition_timeline.png

archive/stage1b_scratch:
print_stats.py
```

</details>

<details><summary>🔧 Bash: List tracked non-code files and data dir · 20:23</summary>

**Аргументы**

```bash
git ls-files | grep -v -E "^(src|tests)/" ; echo; git status --short | head; echo; ls -la data data/raw alerts_api 2>&1 | head -40
```

**Результат**

```
.gitignore
DECISIONS.md
PLAN.md
README.md
archive/README.md
archive/stage1_gemini_flash/DECISIONS-gemini-flash.md
archive/stage1_gemini_flash/alert_duration_distribution.png
archive/stage1_gemini_flash/eda_stage1.py
archive/stage1_gemini_flash/pauses_distribution.png
archive/stage1_gemini_flash/raion_alert_frequencies.png
archive/stage1_gemini_flash/transition_timeline.png
archive/stage1b_scratch/print_stats.py
config.yaml
data/alerts_in_ua_locations.csv
data/intervals.csv
data/mask.csv
data/neighbors.csv
data/seen.csv
data/units.csv
pyproject.toml
reports/api_check.md
reports/backtest_h1.md
reports/backtest_h3.md
reports/backtest_h6.md
reports/figures/alerts_per_unit.png
reports/figures/api_vs_vadimkin.png
reports/figures/calibration_h1.png
reports/figures/calibration_h3.png
reports/figures/calibration_h6.png
reports/figures/durations.png
reports/figures/forecast_vs_fact.png
reports/figures/jaccard.png
reports/figures/level_transition.png
reports/figures/outage.png
reports/high_sim_pairs.csv
reports/leakage_check.json
reports/results.md
reports/stage1_summary.md
reports/stage2_summary.md
reports/stage3_summary.md
reports/tuning_h1.json
reports/tuning_h3.json
reports/tuning_h6.json
requirements.txt
reviews/prompts/01_stages0-1b.md
reviews/prompts/02_stage2.md
reviews/prompts/03_stage3.md
reviews/prompts/04_stages4-6.md
reviews/prompts/05_stage5-leakage.md
reviews/prompts/06_stage7.md
reviews/prompts/07_stage8.md
reviews/prompts/08_synthesis.md
scripts/api_check.py
scripts/fetch_alerts_in_ua.py
scripts/fetch_data.py
scripts/run_all.py


alerts_api:
total 5
drwxr-xr-x 1 chyck 197609  0 Oct 11 11:39 .
drwxr-xr-x 1 chyck 197609  0 Oct 11 20:11 ..
-rw-r--r-- 1 chyck 197609 46 Oct 11 11:41 token.txt

data:
total 19772
drwxr-xr-x 1 chyck 197609       0 Oct 11 12:18 .
drwxr-xr-x 1 chyck 197609       0 Oct 11 20:11 ..
-rw-r--r-- 1 chyck 197609   16608 Oct 11 12:55 alerts_in_ua_locations.csv
-rw-r--r-- 1 chyck 197609  714571 Oct 11 12:26 grid.parquet
-rw-r--r-- 1 chyck 197609 5295409 Oct 11 12:26 intervals.csv
-rw-r--r-- 1 chyck 197609   26592 Oct 11 12:26 mask.csv
-rw-r--r-- 1 chyck 197609   12935 Oct 11 12:26 neighbors.csv
-rw-r--r-- 1 chyck 197609 3364600 Oct 11 12:37 predictions_h1.parquet
-rw-r--r-- 1 chyck 197609 3239205 Oct 11 12:45 predictions_h3.parquet
-rw-r--r-- 1 chyck 197609 3261065 Oct 11 12:53 predictions_h6.parquet
drwxr-xr-x 1 chyck 197609       0 Oct 11 11:45 raw
-rw-r--r-- 1 chyck 197609 4273136 Oct 11 12:26 seen.csv
-rw-r--r-- 1 chyck 197609    8620 Oct 11 12:26 units.csv

data/raw:
total 8
drwxr-xr-x 1 chyck 197609 0 Oct 11 11:45 .
drwxr-xr-x 1 chyck 197609 0 Oct 11 12:18 ..
drwxr-xr-x 1 chyck 197609 0 Oct 11 11:59 alerts_in_ua
```

</details>

<details><summary>🔧 Bash: Show report file modification times · 20:23</summary>

**Аргументы**

```bash
ls -la --time-style=full-iso reports reports/figures data/raw/alerts_in_ua | head -60
```

**Результат**

```
data/raw/alerts_in_ua:
total 8087
drwxr-xr-x 1 chyck 197609       0 2026-10-11 11:59:35.872482400 +0300 .
drwxr-xr-x 1 chyck 197609       0 2026-10-11 11:45:39.671979000 +0300 ..
-rw-r--r-- 1 chyck 197609  220212 2026-10-11 11:48:39.386819300 +0300 10_20261011T084839Z.json
-rw-r--r-- 1 chyck 197609    7804 2026-10-11 11:49:10.526232500 +0300 11_20261011T084910Z.json
-rw-r--r-- 1 chyck 197609  530357 2026-10-11 11:49:42.250200800 +0300 12_20261011T084941Z.json
-rw-r--r-- 1 chyck 197609   18796 2026-10-11 11:50:13.405361300 +0300 13_20261011T085013Z.json
-rw-r--r-- 1 chyck 197609  618910 2026-10-11 11:50:44.703457800 +0300 14_20261011T085044Z.json
-rw-r--r-- 1 chyck 197609  507192 2026-10-11 11:51:15.960873900 +0300 15_20261011T085115Z.json
-rw-r--r-- 1 chyck 197609     554 2026-10-11 11:51:47.135911800 +0300 16_20261011T085146Z.json
-rw-r--r-- 1 chyck 197609  413136 2026-10-11 11:52:18.392743700 +0300 17_20261011T085218Z.json
-rw-r--r-- 1 chyck 197609  372293 2026-10-11 11:52:49.716236500 +0300 18_20261011T085249Z.json
-rw-r--r-- 1 chyck 197609  325015 2026-10-11 11:53:20.992073700 +0300 19_20261011T085320Z.json
-rw-r--r-- 1 chyck 197609  440247 2026-10-11 11:53:52.265608800 +0300 20_20261011T085351Z.json
-rw-r--r-- 1 chyck 197609   55150 2026-10-11 11:54:23.451580900 +0300 21_20261011T085423Z.json
-rw-r--r-- 1 chyck 197609 1034093 2026-10-11 11:45:40.124773500 +0300 22_20261011T084539Z.json
-rw-r--r-- 1 chyck 197609 1034093 2026-10-11 11:54:54.957950600 +0300 22_20261011T085454Z.json
-rw-r--r-- 1 chyck 197609  164911 2026-10-11 11:55:26.196451400 +0300 23_20261011T085525Z.json
-rw-r--r-- 1 chyck 197609  262475 2026-10-11 11:55:57.460275000 +0300 24_20261011T085557Z.json
-rw-r--r-- 1 chyck 197609  317828 2026-10-11 11:56:28.751933600 +0300 25_20261011T085628Z.json
-rw-r--r-- 1 chyck 197609   21876 2026-10-11 11:56:59.928197600 +0300 26_20261011T085659Z.json
-rw-r--r-- 1 chyck 197609   20383 2026-10-11 11:57:31.072438200 +0300 27_20261011T085730Z.json
-rw-r--r-- 1 chyck 197609  242589 2026-10-11 11:58:02.290790400 +0300 28_20261011T085802Z.json
-rw-r--r-- 1 chyck 197609     675 2026-10-11 11:58:33.436349800 +0300 29_20261011T085833Z.json
-rw-r--r-- 1 chyck 197609     158 2026-10-11 11:59:04.580541700 +0300 30_20261011T085904Z.json
-rw-r--r-- 1 chyck 197609   81896 2026-10-11 11:59:35.873499000 +0300 31_20261011T085935Z.json
-rw-r--r-- 1 chyck 197609   86410 2026-10-11 11:46:03.123933600 +0300 3_20261011T084602Z.json
-rw-r--r-- 1 chyck 197609  207662 2026-10-11 11:46:34.419907400 +0300 4_20261011T084634Z.json
-rw-r--r-- 1 chyck 197609  133371 2026-10-11 11:47:05.632063500 +0300 5_20261011T084705Z.json
-rw-r--r-- 1 chyck 197609   59617 2026-10-11 11:47:36.789003800 +0300 8_20261011T084736Z.json
-rw-r--r-- 1 chyck 197609 1043015 2026-10-11 11:48:08.157332200 +0300 9_20261011T084807Z.json
-rw-r--r-- 1 chyck 197609    4844 2026-10-11 11:59:35.876746400 +0300 manifest.jsonl

reports:
total 96
drwxr-xr-x 1 chyck 197609     0 2026-10-11 12:19:47.429229000 
… [обрезано: показано 3000 из 4682 символов]
```

</details>

<details><summary>🔧 Bash: List branches, stashes, commit counts · 20:23</summary>

**Аргументы**

```bash
git branch -a && git stash list && git log --all --oneline | wc -l && git rev-list --all | wc -l
```

**Результат**

```
+ GPT
+ claude-opus
+ gemini-flash
+ gemini-pro
  knowledge-check-cleanup
  main
  stage2-review-refactor
  stages-3-6
* stages-7-8
  remotes/origin/HEAD -> origin/main
  remotes/origin/knowledge-check-cleanup
  remotes/origin/main
  remotes/origin/stage2-review-refactor
  remotes/origin/stages-3-6
  remotes/origin/stages-7-8
29
29
```

</details>

<details><summary>🔧 Bash: Scan git history for secret-like strings, redacted · 20:23</summary>

**Аргументы**

```bash
mkdir -p /d/Flash/golova/KSE_AI/AAFS/reviews/scratch/stage7 && cat > /d/Flash/golova/KSE_AI/AAFS/reviews/scratch/stage7/secrets_scan.py <<'EOF'
"""Scan all git history (all refs) for secret-like strings. Never prints a matched value:
long strings are redacted to <LEN:n>; known-legit hashes are counted separately."""
import re
import subprocess
import sys
from collections import Counter, defaultdict

out = subprocess.run(['git', 'log', '--all', '-p', '--no-color', '--format=COMMIT %H', '--', '.',
                      ':(exclude)data/intervals.csv', ':(exclude)data/seen.csv'],
                     capture_output=True, text=True, encoding='utf-8', errors='replace').stdout
# legit long hex: commit ids of this repo and known sha256/blob values from config/DECISIONS
legit = set(subprocess.run(['git', 'rev-list', '--all'], capture_output=True, text=True).stdout.split())
cfgtxt = open('config.yaml', encoding='utf-8').read() + open('DECISIONS.md', encoding='utf-8').read()
legit |= set(re.findall(r'\b[0-9a-f]{32,64}\b', cfgtxt))
# also all historical config/decisions versions
for f in ['config.yaml', 'DECISIONS.md', 'PLAN.md']:
    revs = subprocess.run(['git', 'log', '--all', '--format=%H', '--', f], capture_output=True, text=True).stdout.split()
    for r in revs:
        txt = subprocess.run(['git', 'show', f'{r}:{f}'], capture_output=True, text=True, encoding='utf-8', errors='replace').stdout
        legit |= set(re.findall(r'\b[0-9a-f]{32,64}\b', txt))

HEX = re.compile(r'\b[0-9a-fA-F]{32,}\b')
B64 = re.compile(r'[A-Za-z0-9+/_\-]{28,}={0,2}')
KW = re.compile(r'(?i)(authorization|bearer|x-api-key|api[_-]?key|secret|password|token)')
commit, file = None, None
hits = defaultdict(Counter)
kw_lines = []
for line in out.splitlines():
    if line.startswith('COMMIT '):
        commit = line[7:15]
        continue
    if line.startswith('+++ b/'):
        file = line[6:]
        continue
    if not line.startswith('+') or line.startswith('+++'):
        continue
    body = line
… [обрезано: показано 2000 из 3234 символов]
```

**Результат**

```
== hex_legit: 15 matches in 14 (commit, file, len) groups
== keyword lines with a long string (redacted): 0
```

</details>

<details><summary>🔧 Bash: Second secret scan pass and history of sensitive paths · 20:24</summary>

**Аргументы**

```bash
echo "token file in history:"; git log --all --oneline -- alerts_api/token.txt '*.token' .env alerts_api | head; echo "files ever under alerts_api or raw:"; git log --all --name-only --format='' | grep -E "alerts_api|data/raw|\.env|token" | sort -u; cat > reviews/scratch/stage7/secrets_scan2.py <<'EOF'
"""Second pass: any >=24-char token of letters+digits (any case) not in the legit set; redacted output.
Includes the big CSVs. Prints only commit, file, length, and a character-class signature."""
import re, subprocess
from collections import Counter
out = subprocess.run(['git', 'log', '--all', '-p', '--no-color', '--format=COMMIT %H'],
                     capture_output=True, text=True, encoding='utf-8', errors='replace').stdout
legit = set(subprocess.run(['git', 'rev-list', '--all'], capture_output=True, text=True).stdout.split())
for f in ['config.yaml', 'DECISIONS.md', 'PLAN.md']:
    for r in subprocess.run(['git', 'log', '--all', '--format=%H', '--', f], capture_output=True, text=True).stdout.split():
        txt = subprocess.run(['git', 'show', f'{r}:{f}'], capture_output=True, text=True, encoding='utf-8', errors='replace').stdout
        legit |= set(re.findall(r'\b[0-9a-f]{32,64}\b', txt))
TOK = re.compile(r'(?<![A-Za-z0-9])[A-Za-z0-9]{24,}(?![A-Za-z0-9])')
c = Counter(); commit = file = None
for line in out.splitlines():
    if line.startswith('COMMIT '): commit = line[7:15]; continue
    if line.startswith('+++ b/'): file = line[6:]; continue
    if not line.startswith('+') or line.startswith('+++'): continue
    for m in TOK.finditer(line[1:]):
        v = m.group(0)
        if v.lower() in legit or not re.search(r'\d', v) or not re.search(r'[A-Za-z]', v):
            continue
        sig = ('U' if re.search('[A-Z]', v) else '') + ('l' if re.search('[a-z]', v) else '') + 'd'
        c[(commit, file, len(v), sig)] += 1
print(len(c), 'groups')
for k, n in sorted(c.items(), key=lambda x: x[0][1] or '')[:80]:
    print(*k, 'x', n)
EOF
PYTHONIOENCODING=utf-8 p
… [обрезано: показано 2000 из 2045 символов]
```

**Результат**

```
token file in history:
files ever under alerts_api or raw:
0 groups
```

</details>

<details><summary>🔧 Bash: Check raw manifest and fetch script for token handling · 20:24</summary>

**Аргументы**

```bash
head -c 400 data/raw/alerts_in_ua/manifest.jsonl | sed -E 's/[A-Za-z0-9]{24,}/<REDACTED>/g'; echo; grep -c -i -E "authorization|bearer|token" data/raw/alerts_in_ua/manifest.jsonl; grep -n -i "token" scripts/fetch_alerts_in_ua.py | sed -E 's/[A-Za-z0-9]{30,}/<R>/g'
```

**Результат**

```
{"uid": "22", "status": 200, "requested_utc": "2026-10-11T08:45:39.672979+00:00", "bytes": 1034093, "last_modified": null, "file": "22_20261011T084539Z.json", "alerts": 2373}
{"uid": "3", "status": 200, "requested_utc": "2026-10-11T08:46:02.785124+00:00", "bytes": 86410, "last_modified": null, "file": "3_20261011T084602Z.json", "alerts": 197}
{"uid": "4", "status": 200, "requested_utc": "2026-10
0
6:The token is read from the environment variable named in config.api.token_env, or else from the
7:git-ignored file config.api.token_file. It is sent only in the Authorization header and is never
13:block the IP and the token. Hence a pause of config.api.pause_seconds between requests, a stop on
35:    """An answer after which no further request may be sent (bad token, blocked IP)."""
38:def read_token(api: dict) -> str:
39:    token = os.environ.get(api['token_env'], '').strip()
40:    if not token:
41:        p = ROOT / api['token_file']
42:        token = p.read_text(encoding='utf-8').strip() if p.exists() else ''
43:    if not token:
44:        raise Stop(f"no token: set {api['token_env']} or put it into {api['token_file']}")
45:    return token
48:def get(url: str, token: str, if_modified_since: str | None = None) -> tuple[int, bytes, dict]:
49:    headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/json',
57:    except urllib.error.HTTPError as e:              # the message never contains the token
63:    token = read_token(api)
74:            status, body, headers = get(url, token)
```

</details>

<details><summary>🔧 Bash: Show store module and inspect prediction parquet files · 20:24</summary>

**Аргументы**

```bash
cat -n src/alerts/store.py && python -c "
import pandas as pd
for h in (1,3,6):
    p=pd.read_parquet(f'data/predictions_h{h}.parquet'); print(h, p.shape, p.dtypes.to_dict() if h==1 else '', p['part'].value_counts().to_dict())
print(p.head(3).T)
"
```

**Результат**

```
1	"""Reading and writing pipeline tables with explicit types (CSV keeps them diffable in git)."""
     2	import pandas as pd
     3	
     4	from alerts.config import path
     5	from alerts.intervals import INTERVAL_COLUMNS, SEEN_COLUMNS
     6	from alerts.mask import MASK_COLUMNS
     7	
     8	UNIT_COLUMNS = ['oblast', 'raion', 'unit_id', 'unit_name', 'role']
     9	
    10	
    11	def _utc(s: pd.Series) -> pd.Series:
    12	    return pd.to_datetime(s, utc=True).dt.as_unit('s')
    13	
    14	
    15	def save(df: pd.DataFrame, cfg: dict, key: str) -> None:
    16	    p = path(cfg, key)
    17	    p.parent.mkdir(parents=True, exist_ok=True)
    18	    df.to_csv(p, index=False)
    19	
    20	
    21	def save_parquet(df: pd.DataFrame, cfg: dict, key: str) -> None:
    22	    """Large derived tables: parquet keeps types and stays small; they are not tracked in git."""
    23	    p = path(cfg, key)
    24	    p.parent.mkdir(parents=True, exist_ok=True)
    25	    df.to_parquet(p, index=False)
    26	
    27	
    28	def load_grid(cfg: dict) -> pd.DataFrame:
    29	    return pd.read_parquet(path(cfg, 'grid'))
    30	
    31	
    32	def load_seen(cfg: dict) -> pd.DataFrame:
    33	    s = pd.read_csv(path(cfg, 'seen'))[SEEN_COLUMNS]
    34	    return s.assign(start=_utc(s['start']), end=_utc(s['end']))
    35	
    36	
    37	def load_units(cfg: dict) -> pd.DataFrame:
    38	    return pd.read_csv(path(cfg, 'units'))[UNIT_COLUMNS]
    39	
    40	
    41	def load_masks(cfg: dict) -> pd.DataFrame:
    42	    m = pd.read_csv(path(cfg, 'mask'))[MASK_COLUMNS]
    43	    return m.assign(start=_utc(m['start']), end=_utc(m['end']))
    44	
    45	
    46	def load_intervals(cfg: dict) -> pd.DataFrame:
    47	    iv = pd.read_csv(path(cfg, 'intervals'))[INTERVAL_COLUMNS]
    48	    return iv.assign(start_utc=_utc(iv['start_utc']), end_utc=_utc(iv['end_utc']),
    49	                     uncertain=iv['uncertain'].astype(bool))
1 (104439, 11) {'day': datetime64[ms, UTC], 'p_B0': dtype('float64'), 'p_B1': dtype('float64'), 'p_B2': dtype('float64'), 'p_LR': dtype('float64'), 'p_LGBM': dtype('float64'), 'part': <StringDtype(na_value=nan)>, 'y': dtype('int64'), 't': datetime64[ms, UTC], 'unit_id': <StringDtype(na_value=nan)>, 'oblast': <StringDtype(na_value=nan)>} {'val': 57865, 'test': 46574}
3 (104135, 11)  {'val': 57865, 'test': 46270}
6 (103632, 11)  {'val': 57865, 'test': 45767}
row                         510642  ...                     510644
day      2026-07-13 00:00:00+00:00  ...  2026-07-13 00:00:00+00:00
p_B0                      0.320906  ...                   0.320906
p_B1                      0.580244  ...                   0.039427
p_B2                      0.339161  ...                   0.339161
p_LR                       0.57366  ...                    0.04268
p_LGBM                    0.508155  ...                   0.039222
part                           val  ...                        va
… [обрезано: показано 3000 из 3298 символов]
```

</details>

<details><summary>🔧 Bash: Recompute metrics and calibration from predictions · 20:24</summary>

**Аргументы**

```bash
cat > /d/Flash/golova/KSE_AI/AAFS/reviews/scratch/stage7/audit_preds.py <<'EOF'
"""Recompute report numbers from data/predictions_h*.parquet (read-only) and audit README claims."""
import numpy as np
import pandas as pd

from alerts.config import load_config
from alerts.metrics import bootstrap, score, calibration

cfg = load_config()
bs = cfg['bootstrap']
M = ['B0', 'B1', 'B2', 'LR', 'LGBM']
for h in (1, 3, 6):
    p = pd.read_parquet(f'data/predictions_h{h}.parquet')
    te = p[p['part'] == 'test']
    print(f'\n===== h={h}: test rows {len(te)}, pos {te.y.sum()}, base {te.y.mean():.4f}, days {te.day.nunique()}')
    t = bootstrap(te, M, bs['n_reps'], bs['seed'], bs['ci'], 'B1')
    for m in M:
        r = t[t.model == m].set_index('metric')
        print(f"  {m:5s} " + ' '.join(f"{k}={r.at[k,'value']:.4f}[{r.at[k,'lo']:.3f},{r.at[k,'hi']:.3f}] d={r.at[k,'diff']:+.4f}[{r.at[k,'diff_lo']:+.3f},{r.at[k,'diff_hi']:+.3f}]" for k in ['pr_auc', 'log_loss']))
    # calibration: ECE over 10 quantile bins and daily calibration-in-the-large
    for m in ['B1', 'LR', 'LGBM']:
        c = calibration(te['y'].to_numpy(), te[f'p_{m}'].to_numpy())
        ece = float((c['n'] * (c['p_mean'] - c['y_rate']).abs()).sum() / c['n'].sum())
        g = te.groupby('day').agg(p=(f'p_{m}', 'mean'), y=('y', 'mean'), n=('y', 'size'))
        d = g['p'] - g['y']
        print(f'  calib {m:5s} ECE={ece:.4f} max_bin_gap={float((c.p_mean-c.y_rate).abs().max()):.3f} '
              f'| daily mean(p)-mean(y): mean={d.mean():+.3f} MAE={d.abs().mean():.3f} min={d.min():+.3f} max={d.max():+.3f}')
EOF
cd /d/Flash/golova/KSE_AI/AAFS && PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage7/audit_preds.py
```

**Результат**

```
===== h=1: test rows 46574, pos 5624, base 0.1208, days 24
  B0    pr_auc=0.1315[0.114,0.151] d=-0.2667[-0.291,-0.244] log_loss=0.3726[0.344,0.404] d=+0.0854[+0.076,+0.095]
  B1    pr_auc=0.3982[0.382,0.418] d=+0.0000[+0.000,+0.000] log_loss=0.2872[0.262,0.318] d=+0.0000[+0.000,+0.000]
  B2    pr_auc=0.1302[0.113,0.147] d=-0.2680[-0.288,-0.249] log_loss=0.3718[0.344,0.402] d=+0.0846[+0.076,+0.095]
  LR    pr_auc=0.4242[0.401,0.446] d=+0.0260[+0.011,+0.040] log_loss=0.2690[0.250,0.291] d=-0.0182[-0.028,-0.010]
  LGBM  pr_auc=0.4344[0.409,0.458] d=+0.0362[+0.019,+0.050] log_loss=0.2650[0.247,0.286] d=-0.0222[-0.033,-0.014]
  calib B1    ECE=0.0201 max_bin_gap=0.064 | daily mean(p)-mean(y): mean=-0.006 MAE=0.033 min=-0.099 max=+0.059
  calib LR    ECE=0.0074 max_bin_gap=0.019 | daily mean(p)-mean(y): mean=-0.002 MAE=0.022 min=-0.054 max=+0.070
  calib LGBM  ECE=0.0063 max_bin_gap=0.016 | daily mean(p)-mean(y): mean=-0.004 MAE=0.022 min=-0.067 max=+0.050

===== h=3: test rows 46270, pos 11785, base 0.2547, days 24
  B0    pr_auc=0.2716[0.235,0.307] d=-0.4021[-0.440,-0.370] log_loss=0.5718[0.540,0.607] d=+0.1907[+0.168,+0.214]
  B1    pr_auc=0.6737[0.652,0.702] d=+0.0000[+0.000,+0.000] log_loss=0.3811[0.354,0.411] d=+0.0000[+0.000,+0.000]
  B2    pr_auc=0.2527[0.226,0.279] d=-0.4210[-0.451,-0.394] log_loss=0.5746[0.543,0.610] d=+0.1934[+0.171,+0.216]
  LR    pr_auc=0.6920[0.661,0.722] d=+0.0183[-0.003,+0.036] log_loss=0.3673[0.345,0.391] d=-0.0139[-0.027,-0.000]
  LGBM  pr_auc=0.7008[0.675,0.726] d=+0.0271[+0.010,+0.041] log_loss=0.3599[0.338,0.384] d=-0.0213[-0.033,-0.009]
  calib B1    ECE=0.0198 max_bin_gap=0.058 | daily mean(p)-mean(y): mean=-0.008 MAE=0.061 min=-0.183 max=+0.125
  calib LR    ECE=0.0187 max_bin_gap=0.031 | daily mean(p)-mean(y): mean=+0.000 MAE=0.042 min=-0.118 max=+0.101
  calib LGBM  ECE=0.0094 max_bin_gap=0.026 | daily mean(p)-mean(y): mean=-0.004 MAE=0.044 min=-0.131 max=+0.093

===== h=6: test rows 45767, pos 16472, base 0.3599, days 23
  B0    pr_auc=0.3694[0.324,0.414] d=-0.4443[-0.488,-0.407] log_loss=0.6557[0.632,0.679] d=+0.2700[+0.233,+0.306]
  B1    pr_auc=0.8137[0.788,0.841] d=+0.0000[+0.000,+0.000] log_loss=0.3857[0.354,0.418] d=+0.0000[+0.000,+0.000]
  B2    pr_auc=0.3513[0.316,0.384] d=-0.4624[-0.494,-0.433] log_loss=0.6592[0.635,0.682] d=+0.2735[+0.236,+0.309]
  LR    pr_auc=0.8270[0.793,0.857] d=+0.0133[-0.005,+0.029] log_loss=0.3768[0.353,0.404] d=-0.0089[-0.029,+0.008]
  LGBM  pr_auc=0.8317[0.805,0.858] d=+0.0180[+0.005,+0.030] log_loss=0.3671[0.343,0.393] d=-0.0186[-0.033,-0.006]
  calib B1    ECE=0.0181 max_bin_gap=0.053 | daily mean(p)-mean(y): mean=+0.005 MAE=0.073 min=-0.189 max=+0.182
  calib LR    ECE=0.0261 max_bin_gap=0.057 | daily mean(p)-mean(y): mean=+0.020 MAE=0.059 min=-0.142 max=+0.152
  calib LGBM  ECE=0.0111 max_bin_gap=0.019 | daily mean(p)-mean(y): mean=+0.008 MAE=0.059 min=-0.158 max=+0.157
```

</details>

<details><summary>🔧 Bash: Per-oblast paired diffs and AUC decomposition · 20:26</summary>

**Аргументы**

```bash
cat > /d/Flash/golova/KSE_AI/AAFS/reviews/scratch/stage7/audit_oblast.py <<'EOF'
"""README: 'main gain is within oblasts' and the Kyiv example. Paired per-oblast bootstrap; AUC decomposition."""
import numpy as np
import pandas as pd

from alerts.config import load_config
from alerts.metrics import bootstrap, score

cfg = load_config()
bs = cfg['bootstrap']
for h in (3,):
    te = pd.read_parquet(f'data/predictions_h{h}.parquet').query("part == 'test'")
    rows = []
    for ob, g in te.groupby('oblast'):
        if g.y.sum() == 0:
            continue
        t = bootstrap(g, ['B0', 'B1', 'LR', 'LGBM'], 1000, bs['seed'], bs['ci'], 'B1')
        r = t[t.metric == 'pr_auc'].set_index('model')
        rows.append(dict(oblast=ob, pos=int(g.y.sum()), B1=r.at['B1', 'value'], LR=r.at['LR', 'value'], LGBM=r.at['LGBM', 'value'],
                         d_LR=r.at['LR', 'diff'], d_LR_lo=r.at['LR', 'diff_lo'], d_LR_hi=r.at['LR', 'diff_hi'],
                         d_GBM=r.at['LGBM', 'diff'], d_GBM_lo=r.at['LGBM', 'diff_lo'], d_GBM_hi=r.at['LGBM', 'diff_hi']))
    d = pd.DataFrame(rows).sort_values('pos')
    pd.set_option('display.width', 250)
    print(d.round(3).to_string(index=False))
    print('oblasts with LGBM-B1 CI > 0:', int((d.d_GBM_lo > 0).sum()), 'of', len(d), '; < 0:', int((d.d_GBM_hi < 0).sum()))
    print('oblasts with LR-B1 CI > 0:', int((d.d_LR_lo > 0).sum()), 'of', len(d), '; < 0:', int((d.d_LR_hi < 0).sum()))

    # ROC-AUC decomposition: same-oblast pairs vs cross-oblast pairs
    def auc_parts(col):
        tot = score(te.y.to_numpy(), te[col].to_numpy())['roc_auc']
        npos, nneg = te.y.sum(), (1 - te.y).sum()
        within_w = within_s = 0.0
        for ob, g in te.groupby('oblast'):
            a, b = g.y.sum(), (1 - g.y).sum()
            if a == 0 or b == 0:
                continue
            within_s += score(g.y.to_numpy(), g[col].to_numpy())['roc_auc'] * a * b
            within_w += a * b
        cross = (tot * npos * nneg - within_s) / (n
… [обрезано: показано 2000 из 2455 символов]
```

**Результат**

```
oblast  pos    B1    LR  LGBM   d_LR  d_LR_lo  d_LR_hi  d_GBM  d_GBM_lo  d_GBM_hi
   Chernivetska oblast   18 0.015 0.024 0.019  0.009    0.000    0.042  0.003    -0.008     0.010
       Volynska oblast   21 0.014 0.018 0.026  0.004   -0.017    0.015  0.012    -0.000     0.029
    Ternopilska oblast   45 0.027 0.059 0.073  0.033   -0.004    0.073  0.046     0.011     0.161
      Zaporizka oblast   54 1.000 0.998 0.991 -0.002   -0.006   -0.000 -0.009    -0.032    -0.005
      Rivnenska oblast   81 0.049 0.098 0.091  0.049    0.001    0.110  0.042    -0.003     0.083
    Khmelnytska oblast   88 0.058 0.115 0.112  0.057    0.017    0.098  0.054     0.003     0.128
             Kyiv City  138 0.344 0.631 0.592  0.287    0.087    0.404  0.248     0.081     0.368
    Zhytomyrska oblast  269 0.168 0.213 0.201  0.045   -0.041    0.143  0.033    -0.043     0.129
      Vinnytska oblast  380 0.161 0.211 0.225  0.050   -0.035    0.122  0.065    -0.011     0.146
      Cherkaska oblast  608 0.362 0.459 0.444  0.098   -0.007    0.196  0.082    -0.017     0.179
     Khersonska oblast  629 0.599 0.587 0.591 -0.013   -0.062    0.032 -0.008    -0.054     0.038
  Kirovohradska oblast  700 0.379 0.529 0.483  0.150    0.080    0.225  0.104     0.039     0.166
      Poltavska oblast  801 0.570 0.657 0.642  0.087   -0.002    0.154  0.071     0.003     0.125
    Mykolaivska oblast  831 0.693 0.665 0.705 -0.028   -0.060    0.007  0.012    -0.012     0.039
         Sumska oblast  918 0.846 0.779 0.815 -0.067   -0.115   -0.013 -0.030    -0.061     0.004
   Chernihivska oblast  948 0.584 0.636 0.635  0.052   -0.000    0.094  0.050     0.004     0.086
        Kyivska oblast 1010 0.341 0.551 0.514  0.210    0.063    0.305  0.173     0.049     0.256
     Kharkivska oblast 1236 0.952 0.935 0.950 -0.017   -0.035   -0.001 -0.002    -0.015     0.008
Dnipropetrovska oblast 1404 0.689 0.727 0.731  0.038   -0.003    0.073  0.042    -0.002     0.075
         Odeska oblast 1606 0.563 0.598 0.607  0.035   -0.011    0.080  0.044     0.004     0.074
oblasts with LGBM-B1 CI > 0: 8 of 20 ; < 0: 1
oblasts with LR-B1 CI > 0: 6 of 20 ; < 0: 3
h=3 B0    ROC-AUC all=0.5246  same-oblast pairs=0.5435  cross-oblast pairs=0.5240  (same-oblast share of pairs 0.032)
h=3 B1    ROC-AUC all=0.8665  same-oblast pairs=0.5780  cross-oblast pairs=0.8759  (same-oblast share of pairs 0.032)
h=3 LR    ROC-AUC all=0.8819  same-oblast pairs=0.6497  cross-oblast pairs=0.8895  (same-oblast share of pairs 0.032)
h=3 LGBM  ROC-AUC all=0.8829  same-oblast pairs=0.6533  cross-oblast pairs=0.8904  (same-oblast share of pairs 0.032)
```

</details>

<details><summary>🔧 Bash: Inspect learned models threading settings · 20:27</summary>

**Аргументы**

```bash
sed -n 1,60p src/alerts/models/learned.py && grep -n "threads\|deterministic\|n_jobs" -r src/alerts | head -20
```

**Результат**

```
"""Learned models of PLAN stage 6 (D20): M1 logistic regression, M2 LightGBM.

Same interface as the baselines: fit(X, y) / predict_proba(X), where X is the backtest frame.
Every fit starts from scratch: scaling, imputation and category lists are learned on the
training rows of that backtest step only (PLAN rule 3). Optional recency weighting gives a row of
age a days the weight 0.5 ** (a / half_life_days); the age is counted from the last training row.
"""
import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from alerts.features import NUMERIC

LR_FEATURES = [f for f in NUMERIC if f not in ('hour_kyiv', 'dow_kyiv')]        # cyclic sin/cos instead
GBM_FEATURES = [f for f in NUMERIC if f not in ('hour_sin', 'hour_cos', 'dow_sin', 'dow_cos')] + ['unit_id']


def recency_weights(t: pd.Series, half_life_days) -> np.ndarray | None:
    if half_life_days is None:
        return None
    age = (t.max() - t).dt.total_seconds().to_numpy() / 86400
    return 0.5 ** (age / half_life_days)


class LogisticModel:
    """M1: standardised numeric features (median imputation with missing-value indicators), cyclic
    calendar, one-hot unit identity, L2-regularised logistic regression."""
    name = 'LR'

    def __init__(self, cfg: dict, params: dict):
        self.params = params
        self.cfg = cfg

    def fit(self, X: pd.DataFrame, y: np.ndarray):
        prep = ColumnTransformer([
            ('num', make_pipeline(SimpleImputer(strategy='median', add_indicator=True), StandardScaler()), LR_FEATURES),
            ('unit', OneHotEncoder(handle_unknown='ignore'), ['unit_id'])])
        self.model_ = make_pipeline(prep, LogisticRegression(C=self.params['C'], max_iter=1000))
        w = recency_weights(X['t'], self.params['half_life_days'])
        self.model_.fit(X, y.astype(int), logisticregression__sample_weight=w)
        return self

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        return self.model_.predict_proba(X)[:, 1]


class GBMModel:
    """M2: one LightGBM model for all units; unit identity as a categorical feature."""
    name = 'LGBM'

    def __init__(self, cfg: dict, params: dict):
        self.params = params
        self.cfg = cfg

    def _frame(self, X: pd.DataFrame) -> pd.DataFrame:
src/alerts/config.py:20:    'models': ['threads', 'seed', 'lr', 'lgbm'],
src/alerts/models/learned.py:71:            deterministic=True, force_row_wise=True, n_jobs=m['threads'], random_state=m['seed'], verbose=-1)
Binary file src/alerts/models/__pycache__/learned.cpython-312.pyc matches
Binary file src/alerts/__pycache__/config.cpython-312.pyc matches
```

</details>

<details><summary>🔧 Bash: Rebuild in memory and compare to committed artifacts · 20:28</summary>

**Аргументы**

```bash
cat > /d/Flash/golova/KSE_AI/AAFS/reviews/scratch/stage7/repro.py <<'EOF'
"""Clean-clone reproducibility, in memory only (nothing is written to data/ or reports/):
1) committed data/*.csv vs tables rebuilt by the current code;
2) committed stage summaries vs regenerated markdown; stage figures vs regenerated PNG bytes;
3) backtest day 2026-08-10, h = 3: forecasts of the current code vs data/predictions_h3.parquet, bit for bit.
"""
import io
import json
import time

import numpy as np
import pandas as pd

from alerts import figures, report, store
from alerts.config import load_config, path, ts
from alerts.models import registry
from alerts.pipeline import build_all, model_data
from alerts.backtest import walk_forward

cfg = load_config()
t0 = time.time()
art = build_all(cfg)
print(f'build_all {time.time() - t0:.1f} s')

# 1) committed CSVs
def cmp(name, a, b):
    a = a.reset_index(drop=True); b = b.reset_index(drop=True)
    try:
        pd.testing.assert_frame_equal(a, b, check_dtype=False, check_exact=True)
        print(f'  {name}: identical ({len(a)} rows)')
    except AssertionError as e:
        print(f'  {name}: DIFFERENT: {str(e)[:300]}')

print('1) committed data/*.csv vs current code')
cmp('units', store.load_units(cfg), art.units[store.UNIT_COLUMNS])
cmp('mask', store.load_masks(cfg), art.masks[list(store.load_masks(cfg).columns)])
iv = store.load_intervals(cfg)
cmp('intervals', iv, art.intervals[list(iv.columns)])
sn = store.load_seen(cfg)
cmp('seen', sn, art.seen[list(sn.columns)])
nb = pd.read_csv(path(cfg, 'neighbors'))
cmp('neighbors', nb, art.neighbors[list(nb.columns)])
sp = pd.read_csv(path(cfg, 'similar_pairs'))
cmp('high_sim_pairs', sp, art.pairs[art.pairs['jaccard'] >= cfg['thresholds']['similar_pairs_report']][list(sp.columns)])
g = pd.read_parquet(path(cfg, 'grid'))
cmp('grid.parquet (local, not in git)', g, art.grid[list(g.columns)])

# 2) summaries and figures
print('2) committed reports vs regenerated (in memory)')
actual = report.referenc
… [обрезано: показано 2000 из 4400 символов]
```

**Результат**

```
Channel outage (D15): 2026-08-29 05:55:28+00:00 -> 2026-09-02 13:48:04+00:00 (4 days 07:52:36)
build_all 20.5 s
1) committed data/*.csv vs current code
  units: identical (119 rows)
  mask: identical (392 rows)
  intervals: identical (73737 rows)
  seen: identical (73688 rows)
  neighbors: identical (632 rows)
  high_sim_pairs: DIFFERENT: DataFrame.iloc[:, 3] (column name="jaccard") are different

DataFrame.iloc[:, 3] (column name="jaccard") values are different (33.33333 %)
[index]: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38]
[left
  grid.parquet (local, not in git): identical (616909 rows)
2) committed reports vs regenerated (in memory)
  stage1_summary.md: identical
  stage2_summary.md: identical
  stage3_summary.md: identical
  reference mismatches: []
  level_transition.png: identical bytes
  alerts_per_unit.png: identical bytes
  durations.png: identical bytes
  jaccard.png: identical bytes
  outage.png: identical bytes
3) backtest day 2026-08-10, h=3 vs parquet
  model_data 3.0 s, 615,151 rows
  B0: rows 2026 vs 2026, same rows True, max |diff| 0, bit-equal True (0.4 s)
  B1: rows 2026 vs 2026, same rows True, max |diff| 0, bit-equal True (0.6 s)
  B2: rows 2026 vs 2026, same rows True, max |diff| 0, bit-equal True (0.5 s)
  LR: rows 2026 vs 2026, same rows True, max |diff| 0, bit-equal True (8.8 s)
  LGBM: rows 2026 vs 2026, same rows True, max |diff| 0, bit-equal True (3.4 s)
```

</details>

<details><summary>🔧 Bash: Check magnitude of high_sim_pairs difference · 20:29</summary>

**Аргументы**

```bash
cat > /d/Flash/golova/KSE_AI/AAFS/reviews/scratch/stage7/pairs_diff.py <<'EOF'
import io
import numpy as np, pandas as pd
from alerts.config import load_config, path
from alerts.pipeline import build_all
cfg = load_config(); art = build_all(cfg)
sp = pd.read_csv(path(cfg, 'similar_pairs'))
new = art.pairs[art.pairs['jaccard'] >= cfg['thresholds']['similar_pairs_report']].reset_index(drop=True)
print('max abs diff jaccard:', np.abs(sp['jaccard'].to_numpy() - new['jaccard'].to_numpy()).max())
buf = io.StringIO(); new.to_csv(buf, index=False)
print('CSV text identical to committed file:', buf.getvalue() == path(cfg, 'similar_pairs').read_text(encoding='utf-8').replace('\r\n', '\n'))
EOF
cd /d/Flash/golova/KSE_AI/AAFS && PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage7/pairs_diff.py 2>&1 | grep -v -E "^INFO|WARNING|Channel"
```

**Результат**

```
max abs diff jaccard: 1.1102230246251565e-16
CSV text identical to committed file: False
```

</details>

<details><summary>🔧 Bash: Find encoding-less IO and git usage · 20:29</summary>

**Аргументы**

```bash
grep -n -E "open\(|read_text\(|write_text\(|\\\\\\\\|os\.sep|subprocess|'git'|\"git\"" -r src scripts | grep -v "encoding=" ; echo ---; grep -n -E "git" src/alerts/api_check.py scripts/api_check.py | head -20
```

**Результат**

```
src/alerts/api_check.py:9:import subprocess
src/alerts/api_check.py:99:    blob = subprocess.run(['git', '-C', str(ROOT / cfg['dataset']['repo_dir']), 'show', f"{v['commit']}:{v['path']}"],
src/alerts/figures.py:114:    ax.text(long_h * 1.08, ax.get_ylim()[1] * 0.5, f'{long_h} h: {n_long} longer alerts\nmasked, rule (a)',
src/alerts/figures.py:164:        ax.text(s + (e - s) / 2, top * 0.97, f'channel silent\n{(o.end - o.start).total_seconds() / 86400:.1f} days',
src/alerts/ingest/vadimkin.py:11:    with open(path, 'rb') as f:
Binary file src/alerts/ingest/__pycache__/alerts_in_ua.cpython-312.pyc matches
Binary file src/alerts/ingest/__pycache__/vadimkin.cpython-312.pyc matches
Binary file src/alerts/ingest/__pycache__/__init__.cpython-312.pyc matches
Binary file src/alerts/models/__pycache__/baselines.cpython-312.pyc matches
Binary file src/alerts/models/__pycache__/learned.cpython-312.pyc matches
Binary file src/alerts/models/__pycache__/__init__.cpython-312.pyc matches
src/alerts/report.py:110:    return '\n'.join(lines) + '\n'
src/alerts/report.py:155:    return '\n'.join(lines) + '\n'
src/alerts/report.py:186:    return '\n'.join(lines) + '\n'
Binary file src/alerts/__pycache__/api_check.cpython-312.pyc matches
Binary file src/alerts/__pycache__/backtest.cpython-312.pyc matches
Binary file src/alerts/__pycache__/config.cpython-312.pyc matches
Binary file src/alerts/__pycache__/evaluation.cpython-312.pyc matches
Binary file src/alerts/__pycache__/features.cpython-312.pyc matches
Binary file src/alerts/__pycache__/figures.cpython-312.pyc matches
Binary file src/alerts/__pycache__/geo.cpython-312.pyc matches
Binary file src/alerts/__pycache__/grid.cpython-312.pyc matches
Binary file src/alerts/__pycache__/history.cpython-312.pyc matches
Binary file src/alerts/__pycache__/intervals.cpython-312.pyc matches
Binary file src/alerts/__pycache__/leakage.cpython-312.pyc matches
Binary file src/alerts/__pycache__/mask.cpython-312.pyc matches
Binary file src/alerts/__pycache__/metrics.cpython-312.pyc matches
Binary file src/alerts/__pycache__/pipeline.cpython-312.pyc matches
Binary file src/alerts/__pycache__/processor.cpython-312.pyc matches
Binary file src/alerts/__pycache__/report.cpython-312.pyc matches
Binary file src/alerts/__pycache__/scope.cpython-312.pyc matches
Binary file src/alerts/__pycache__/spans.cpython-312.pyc matches
Binary file src/alerts/__pycache__/store.cpython-312.pyc matches
Binary file src/alerts/__pycache__/timeutil.cpython-312.pyc matches
Binary file src/alerts/__pycache__/tuning.cpython-312.pyc matches
Binary file src/alerts/__pycache__/units.cpython-312.pyc matches
Binary file src/alerts/__pycache__/__init__.cpython-312.pyc matches
scripts/fetch_alerts_in_ua.py:55:        with urllib.request.urlopen(req, timeout=60) as r:
scripts/fetch_alerts_in_ua.py:94:            m.write(json.dumps(rec, ensure_ascii=False) + '\n')
scripts/fetch_data.py:3:import subprocess
scripts/fetch_data.py:16:    subprocess.run(['git', *args], check=Tr
… [обрезано: показано 3000 из 3536 символов]
```

</details>

<details><summary>🔧 Bash: Check dataset repo size and pinned commits · 20:29</summary>

**Аргументы**

```bash
du -sh dataset_repo/.git dataset_repo 2>/dev/null; git -C dataset_repo log --oneline -1; git -C dataset_repo rev-list --count HEAD 2>/dev/null; git -C dataset_repo status --short | head -3; git -C dataset_repo cat-file -t bf0c323 2>&1
```

**Результат**

```
678M	dataset_repo/.git
113M	dataset_repo
58ee75b Add new data
1630
commit
```

</details>

<details><summary>🔧 Bash: Run test suite without writing cache · 20:29</summary>

**Аргументы**

```bash
timeout 300 python -m pytest -q -p no:cacheprovider 2>&1 | tail -5; cat tests/test_load.py | head -20
```

**Результат**

```
..........................                                               [100%]
26 passed in 29.02s
import pytest

from alerts.config import ROOT, load_config
from alerts.ingest.vadimkin import load_official


def test_load_official():
    cfg = load_config()
    path = ROOT / cfg['dataset']['path']
    if not path.exists():
        pytest.skip('Dataset not found locally: run scripts/fetch_data.py')

    df = load_official(path, cfg['dataset']['sha256'])

    assert df.attrs['row_counts'] == {'raw': 299_275, 'dedup': 185_430, 'cleaned': 185_428}
    assert len(df) == len(df.drop_duplicates()), 'Dataframe contains duplicates'
    for col in ['started_at', 'finished_at']:
        assert str(df[col].dt.tz) == 'UTC', f'{col} is not tz-aware UTC'
    assert (df['finished_at'] > df['started_at']).all(), 'Found duration <= 0'
```

</details>

<details><summary>🔧 Bash: Show features module and history API · 20:30</summary>

**Аргументы**

```bash
cat -n src/alerts/features.py && sed -n 1,123p src/alerts/history.py | grep -n "def \|return" 
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
    49	        self.A[nu['a'].map(self.col).to_numpy(), nu['
… [обрезано: показано 3000 из 8855 символов]
```

</details>

<details><summary>🔧 Bash: Run leakage tests under in-memory mutations · 20:30</summary>

**Аргументы**

```bash
cat > /d/Flash/golova/KSE_AI/AAFS/reviews/scratch/stage7/mutations.py <<'EOF'
"""README: 'кожну перевірено підміною з витоком'. In-memory mutations, synthetic tests only (no files written)."""
import copy
import sys
import traceback

import numpy as np
import pandas as pd

sys.path.insert(0, 'tests')
import conftest  # noqa: E402
import test_leakage  # noqa: E402
import test_knowledge  # noqa: E402
from alerts import features  # noqa: E402
from alerts.history import AlertHistory  # noqa: E402

HOUR = pd.Timedelta(hours=1)
orig_starts = AlertHistory.starts
orig_build = features.FeatureBuilder.build


def run(name):
    res = {}
    for tname, fn in [('test_leakage', test_leakage.test_forecasts_at_the_cut_do_not_change),
                      ('test_knowledge', test_knowledge.test_features_use_only_what_was_known)]:
        try:
            fn(copy.deepcopy(conftest._BASE_CFG))
            res[tname] = 'PASSES'
        except AssertionError as e:
            res[tname] = 'fails: ' + str(e).splitlines()[0][:90]
    print(f'{name}:')
    for k, v in res.items():
        print(f'   {k}: {v}')


run('no mutation')

# M1: own-unit counters look one hour ahead (window (t-w+1h, t+1h])
AlertHistory.starts = lambda self, T, w: orig_starts(self, T + HOUR, w)
run('M1 every starts_* window shifted 1 h into the future')
AlertHistory.starts = orig_starts


# M4: only the country-level count looks ahead: starts in (t, t+60m] summed over all units
def build_m4(self, grid):
    f = orig_build(self, grid)
    T = pd.DatetimeIndex(np.sort(grid['t'].unique()))
    ti = np.searchsorted(T.as_unit('s').asi8 if hasattr(T, 'asi8') else T, grid['t'])
    fut = orig_starts(self.history, T + HOUR, HOUR).sum(axis=1)
    f['country_starts_60m'] = fut[ti].astype('float32')
    return f


features.FeatureBuilder.build = build_m4
run('M4 country_starts_60m counts starts in (t, t+60m] (future timing only)')
features.FeatureBuilder.build = orig_build
EOF
cd /d/Flash/golova/KSE_AI/AAFS && PYTHONPATH=src
… [обрезано: показано 2000 из 2112 символов]
```

**Результат**

```
no mutation:
   test_leakage: PASSES
   test_knowledge: PASSES
M1 every starts_* window shifted 1 h into the future:
   test_leakage: fails: features and forecasts at the cut.iloc[:, 2] (column name="starts_6h") are different
   test_knowledge: fails: features known at 2026-02-20 12:00:00+00:00.iloc[:, 1] (column name="starts_6h") are diffe
Traceback (most recent call last):
  File "D:\Soft\miniconda\Lib\site-packages\numpy\_core\fromnumeric.py", line 54, in _wrapfunc
    return bound(*args, **kwds)
           ^^^^^^^^^^^^^^^^^^^^
TypeError: '<' not supported between instances of 'int' and 'Timestamp'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "D:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage7\mutations.py", line 54, in <module>
    run('M4 country_starts_60m counts starts in (t, t+60m] (future timing only)')
  File "D:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage7\mutations.py", line 26, in run
    fn(copy.deepcopy(conftest._BASE_CFG))
  File "D:\Flash\golova\KSE_AI\AAFS\tests\test_leakage.py", line 45, in test_forecasts_at_the_cut_do_not_change
    res = check(df, cfg, utc(cut), h, models, units=UNITS, neighbors=NEIGHBORS)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\Flash\golova\KSE_AI\AAFS\src\alerts\leakage.py", line 96, in check
    train_a, fc_a = forecasts_at(model_data(clean, cfg), cut, h, models)
                                 ^^^^^^^^^^^^^^^^^^^^^^
  File "D:\Flash\golova\KSE_AI\AAFS\src\alerts\pipeline.py", line 80, in model_data
    data = pd.concat([art.grid, fb.build(art.grid)], axis=1)
                                ^^^^^^^^^^^^^^^^^^
  File "D:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage7\mutations.py", line 47, in build_m4
    ti = np.searchsorted(T.as_unit('s').asi8 if hasattr(T, 'asi8') else T, grid['t'])
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\Soft\miniconda\Lib\site-packages\numpy\_core\fromnumeric.py", line 1539, in searchsorted
    return _wrapfunc(a, 'searchsorted', v, side=side, sorter=sorter)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\Soft\miniconda\Lib\site-packages\numpy\_core\fromnumeric.py", line 63, in _wrapfunc
    return _wrapit(obj, method, *args, **kwds)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\Soft\miniconda\Lib\site-packages\numpy\_core\fromnumeric.py", line 43, in _wrapit
    result = getattr(arr, method)(*args, **kwds)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: '<' not supported between instances of 'int' and 'Timestamp'
```

</details>

<a id="m-73f5e58a"></a>

**🤖 Ассистент** · 2026-10-11 20:31

Fix the index computation using the project's `to_sec` (rule 11).

<details><summary>🔧 Bash: Rerun only the country-level future-start mutation · 20:31</summary>

**Аргументы**

```bash
python - <<'EOF'
p='reviews/scratch/stage7/mutations.py'
s=open(p,encoding='utf-8').read()
s=s.replace("    ti = np.searchsorted(T.as_unit('s').asi8 if hasattr(T, 'asi8') else T, grid['t'])\n",
            "    ti = np.searchsorted(to_sec(T), to_sec(grid['t']))\n")
s=s.replace("from alerts.history import AlertHistory  # noqa: E402\n","from alerts.history import AlertHistory  # noqa: E402\nfrom alerts.timeutil import to_sec  # noqa: E402\n")
s=s.replace("run('no mutation')\n","")
s=s.replace("AlertHistory.starts = lambda self, T, w: orig_starts(self, T + HOUR, w)\nrun('M1 every starts_* window shifted 1 h into the future')\n","")
open(p,'w',encoding='utf-8').write(s)
EOF
PYTHONPATH=src PYTHONIOENCODING=utf-8 timeout 900 python reviews/scratch/stage7/mutations.py 2>&1 | grep -v -E "^INFO|WARNING"
```

**Результат**

```
M4 country_starts_60m counts starts in (t, t+60m] (future timing only):
   test_leakage: fails: features and forecasts at the cut.iloc[:, 11] (column name="country_starts_60m") are diffe
   test_knowledge: fails: features known at 2026-02-20 12:00:00+00:00.iloc[:, 10] (column name="country_starts_60m")
```

</details>

<details><summary>🔧 Bash: Restore M1 in mutation script, confirm no backtest tests · 20:31</summary>

**Аргументы**

```bash
python - <<'EOF'
p='reviews/scratch/stage7/mutations.py'
s=open(p,encoding='utf-8').read()
s=s.replace("# M1: own-unit counters look one hour ahead (window (t-w+1h, t+1h])\nAlertHistory.starts = orig_starts\n",
"run('no mutation')\n\n# M1: own-unit counters look one hour ahead (window (t-w+1h, t+1h])\nAlertHistory.starts = lambda self, T, w: orig_starts(self, T + HOUR, w)\nrun('M1 every starts_* window shifted 1 h into the future')\nAlertHistory.starts = orig_starts\n")
s+="\n# M2 (by code, not run): backtest.walk_forward has its own filter t <= day - h; leakage.forecasts_at re-implements\n# it as t <= cut - h, and no test imports alerts.backtest, so changing walk_forward to t <= day breaks nothing.\n"
open(p,'w',encoding='utf-8').write(s)
EOF
grep -n "run(\|M1\|M2\|M4" reviews/scratch/stage7/mutations.py; grep -rln "backtest" tests/*.py
```

**Результат**

```
22:def run(name):
37:run('no mutation')
39:# M1: own-unit counters look one hour ahead (window (t-w+1h, t+1h])
41:run('M1 every starts_* window shifted 1 h into the future')
45:# M4: only the country-level count looks ahead: starts in (t, t+60m] summed over all units
56:run('M4 country_starts_60m counts starts in (t, t+60m] (future timing only)')
59:# M2 (by code, not run): backtest.walk_forward has its own filter t <= day - h; leakage.forecasts_at re-implements
tests/conftest.py
tests/test_leakage.py
```

</details>

<details><summary>🔧 Bash: Compare leakage-check forecasts with backtest predictions · 20:32</summary>

**Аргументы**

```bash
cat > /d/Flash/golova/KSE_AI/AAFS/reviews/scratch/stage7/bridge.py <<'EOF'
"""Does the real-data leakage check exercise the backtest? Compare leakage.forecasts_at (clean data, cut 2026-08-10)
with the backtest predictions in data/predictions_h3.parquet for the rows at t = cut. 8 threads as in config."""
import json
import numpy as np
import pandas as pd
from alerts.config import load_config, path, ts
from alerts.leakage import forecasts_at
from alerts.models import registry
from alerts.pipeline import build_all, model_data

cfg = load_config()
data = model_data(build_all(cfg), cfg)
tuned = json.loads((path(cfg, 'reports') / 'tuning_h3.json').read_text())
models = registry(cfg, cfg['backtest']['baselines'] + cfg['backtest']['models'], tuned)
cut = ts('2026-08-10T00:00:00Z')
train, fc = forecasts_at(data, cut, 3, models)
pq = pd.read_parquet('data/predictions_h3.parquet')
ref = pq[pq['t'] == cut].sort_values('unit_id').reset_index(drop=True)
print('training rows', len(train), '(leakage_check.json: 568326); rows at cut', len(fc), 'vs parquet', len(ref))
for m in ['B0', 'B1', 'B2', 'LR', 'LGBM']:
    a, b = fc[f'p_{m}'].to_numpy(), ref[f'p_{m}'].to_numpy()
    print(m, 'same units', fc['unit_id'].tolist() == ref['unit_id'].tolist(), 'bit-equal', bool((a == b).all()))
EOF
cd /d/Flash/golova/KSE_AI/AAFS && PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage7/bridge.py 2>&1 | grep -v -E "^INFO|WARNING|Channel"
```

**Результат**

```
training rows 568326 (leakage_check.json: 568326); rows at cut 89 vs parquet 89
B0 same units True bit-equal True
B1 same units True bit-equal True
B2 same units True bit-equal True
LR same units True bit-equal True
LGBM same units True bit-equal True
```

</details>

<details><summary>🔧 Bash: Compare main with stages-7-8 and show main README · 20:33</summary>

**Аргументы**

```bash
git remote -v | sed -E 's#//[^@/]*@#//<cred>@#'; echo; git log --oneline main..stages-7-8; echo; git log --oneline origin/main -3; echo; git log --oneline origin/stages-7-8 -2; echo; git show origin/main:README.md | head -20
```

**Результат**

```
origin	https://github.com/chuikomykhail-droid/AAFS.git (fetch)
origin	https://github.com/chuikomykhail-droid/AAFS.git (push)

f47ddec reorganize for review
7afa7a4 Stages 7-8: report, model x horizon table, check on fresh alerts.in.ua data
03b3c5b Closed feature access and knowledge-time check (D21); figures module; archive
dad94ba Add step 8 for validation with alerts.in.ua API
83270dc Fix typo in project name in README
6b14327 Merge pull request #2 from chuikomykhail-droid/stages-3-6
4c6e5d8 Stages 3-6: grid and targets, backtest with baselines, features, models
3a71c1b Merge pull request #1 from chuikomykhail-droid/stage2-review-refactor
4203bc2 Fix as-of leak from processor-invented alert ends (D16)
53e2373 Stage 2 review: channel outage mask, as-of history, refactor

052b815 Merge pull request #3 from chuikomykhail-droid/stages-7-8
7afa7a4 Stages 7-8: report, model x horizon table, check on fresh alerts.in.ua data
03b3c5b Closed feature access and knowledge-time check (D21); figures module; archive

7afa7a4 Stages 7-8: report, model x horizon table, check on fresh alerts.in.ua data
03b3c5b Closed feature access and knowledge-time check (D21); figures module; archive

# AAFS — прогноз повітряних тривог за районами України

Щогодини для кожного району, де зараз тихо, модель оцінює ймовірність того, що найближчими
`h` годинами (1, 3 або 6; основний — 3) там почнеться повітряна тривога. Оцінка — на останніх
чотирьох тижнях доступних даних, зі щодобовим перенавчанням і перевірками на витік із майбутнього.

Подробиці рішень — у [`DECISIONS.md`](DECISIONS.md) (D00–D22, а також журнал помилок ШІ, які вдалося
впіймати), план і статус етапів — у [`PLAN.md`](PLAN.md), усі цифри — у [`reports/`](reports/).

## Результат

Тест — 2026-08-10 – 2026-09-07, щодобове перенавчання; у квадратних дужках — 95% інтервал
бутстрепу за днями, різниці парні (повна таблиця всіх моделей — [`reports/results.md`](reports/results.md)):

| h | Частота | B1 (одиниця × година), PR-AUC | LightGBM, PR-AUC | LightGBM − B1, PR-AUC | LightGBM − B1, log loss |
|---|---|---|---|---|---|
| 1 | 0.121 | 0.398 | 0.434 | **+0.036** [+0.019, +0.050] | −0.022 [−0.033, −0.014] |
| 3 | 0.255 | 0.674 | 0.701 | **+0.027** [+0.010, +0.041] | −0.021 [−0.033, −0.009] |
| 6 | 0.360 | 0.814 | 0.832 | **+0.018** [+0.005, +0.030] | −0.019 [−0.033, −0.006] |
```

</details>

<details><summary>🔧 Bash: Search for AI logs and reflection in repo · 20:33</summary>

**Аргументы**

```bash
grep -n -i -E "рефлекс|reflection|лог |логи|логів|log of|transcript|сесі|session" README.md PLAN.md DECISIONS.md | head -20; git ls-files | grep -i -E "log|chat|session|reflect" | head
```

**Результат**

```
PLAN.md:8:- Что сдаём: ссылку на GitHub-репозиторий с рабочим кодом, полный лог работы с ИИ (чат планирования, сессии Claude Code и Antigravity), рефлексию (~100 слов).
PLAN.md:43:1. **Не предполагать структуру данных.** Сначала показать реальные колонки, `head()` и `value_counts()`, и только потом писать логику.
PLAN.md:77:- в лог вывести число строк на каждом шаге. **Ожидаемо:** 299 275 → 185 430 → 185 428.
PLAN.md:224:- **M1, логистическая регрессия.** Нормализация обучается только на train внутри каждого шага бэктеста.
PLAN.md:260:- **Токен никогда не вставлять в чат с ИИ и в вывод команд**: логи сессий сдаются проверяющим.
PLAN.md:291:- LightGBM сравнён с тремя бейзлайнами и логистической регрессией, с доверительными интервалами.
PLAN.md:301:- **Понедельник, вечер:** README, рефлексия, экспорт логов (чат планирования, сессии Claude Code и Antigravity).
PLAN.md:302:- Если не успеваем: горизонты 1 и 6 и логистическая регрессия сокращаются первыми. Тест на утечку и бейзлайны не сокращаются.
PLAN.md:315:    1. У источника другая обработка: свои метки времени, свои правила для пропущенных отбоев (у Vadimkin конец «начало + 1 час»), своя логика уровней. Областная тревога может быть записана одной записью там, где у Vadimkin было несколько районных, и наоборот.
PLAN.md:341:  - добавить «климатологию» как признаки, считая её строго по данным до момента прогноза;
DECISIONS.md:498:| Календарь | `hour_kyiv`, `dow_kyiv` и их sin/cos (для логистической регрессии) |
DECISIONS.md:526:- **M1, логистическая регрессия:** числовые признаки с медианной импутацией и индикаторами пропуска, затем стандартизация; час и день недели — через sin/cos; `unit_id` — one-hot; L2-регуляризация.
```

</details>

<details><summary>🔧 Bash: Show code changes to core modules in stage 7-8 commit · 20:34</summary>

**Аргументы**

```bash
git show 7afa7a4 -- src/alerts/grid.py src/alerts/mask.py src/alerts/processor.py src/alerts/config.py tests/conftest.py scripts/run_all.py | head -200
```

**Результат**

```
commit 7afa7a4425a92b1143d355a174d9a1feb22ac4bf
Author: Chuiko Mykhail <chuikomykhail@gmail.com>
Date:   Sun Oct 11 13:34:14 2026 +0300

    Stages 7-8: report, model x horizon table, check on fresh alerts.in.ua data
    
    Stage 7: backtests for h = 1, 3, 6 (LightGBM beats B1 on all: PR-AUC
    +0.036 / +0.027 / +0.018); reports/results.md; calibration per horizon;
    forecast-vs-fact figure; README (Ukrainian).
    
    Stage 8 (D22): scripts/fetch_alerts_in_ua.py (token only from a
    git-ignored file or env, header only, 31 s pause, stop on 401/403);
    adapter matching all 119 locations through official_data_uk names
    (apostrophe U+2019 vs U+0027 normalised; Kyiv is type oblast in the API);
    processor rules switched off by config; comparison of sources and
    triangulation with the volunteer series; frozen models with a B1
    refitted on API data as the fair reference; leakage checks on the API
    period. Raw API data stay out of git.
    
    DECISIONS: D22, AI error log rows 24-27; PLAN: stages 7-8 done.
    
    Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>

diff --git a/scripts/run_all.py b/scripts/run_all.py
index 9cd840c..daaf838 100644
--- a/scripts/run_all.py
+++ b/scripts/run_all.py
@@ -15,11 +15,12 @@ from pathlib import Path
 
 sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
 
-from alerts import leakage, report  # noqa: E402
+from alerts import figures, leakage, report  # noqa: E402
 from alerts.config import load_config, path, ts  # noqa: E402
-from alerts.evaluation import evaluate, write_report  # noqa: E402
+from alerts.evaluation import evaluate, write_report, write_summary  # noqa: E402
 from alerts.models import registry  # noqa: E402
 from alerts.pipeline import build_all, model_data, save_all  # noqa: E402
+from alerts.spans import union  # noqa: E402
 from alerts.tuning import tune  # noqa: E402
 from fetch_data import ensure_snapshot  # noqa: E402
 
@@ -40,7 +41,7 @@ def main() -> int:
         out = path(cfg, 'reports')
         bt = cfg['backtest']
         data = model_data(art, cfg)
-        tuned = {}
+        tuned, summaries = {}, []
         for h in bt['horizons']:
             tuned[h], table = tune(data, h, cfg)
             (out / f'tuning_h{h}.json').write_text(json.dumps(tuned[h], indent=1), encoding='utf-8')
@@ -48,6 +49,13 @@ def main() -> int:
             res = evaluate(data, h, models, bt['baselines'], cfg)
             write_report(res, cfg, out, _tuning_md(table))
             res['preds'].to_parquet(str(path(cfg, 'predictions')).format(h=h))
+            summaries.append({k: v for k, v in res.items() if k != 'preds'})
+            if h == cfg['leakage_check']['horizon']:
+                rp = cfg['report']
+                outage = union(art.masks[art.masks['reason'] == 'outage'].assign(k=0), 'k')
+                figures.forecast_vs_fact(res['preds'], art.intervals, outage, art.units, rp['forecast_units'],
+                                         rp['
… [обрезано: показано 3000 из 9299 символов]
```

</details>

<details><summary>🔧 Bash: Read frozen-model part of API check · 20:34</summary>

**Аргументы**

```bash
sed -n 100,193p src/alerts/api_check.py && sed -n 100,214p scripts/api_check.py
```

**Результат**

```
check=True, capture_output=True).stdout
    if hashlib.sha256(blob).hexdigest() != v['sha256']:
        raise ValueError('SHA-256 mismatch for the volunteer series')
    d = pd.read_csv(io.BytesIO(blob))
    for c in ['started_at', 'finished_at']:
        d[c] = pd.to_datetime(d[c], utc=True).dt.as_unit('s')
    return d.rename(columns={'region': 'oblast'})


def oblast_intervals(art) -> pd.DataFrame:
    """Oblast under alert when at least one of its units (target or input) is: columns oblast, start, end."""
    ob = art.units.drop_duplicates('unit_id').set_index('unit_id')['oblast']
    iv = art.intervals.assign(oblast=art.intervals['unit_id'].map(ob))
    return union(iv.rename(columns={'start_utc': 'start', 'end_utc': 'end'})[['oblast', 'start', 'end']], 'oblast')


def triangulate(src: pd.DataFrame, vol: pd.DataFrame, lo, hi, tol_min: int = 10) -> dict:
    """Agreement of a source with the volunteer series at oblast level on [lo, hi).

    Starts are matched within tol_min minutes; lags of matched starts reveal a time-zone error (a
    shift by whole hours). The hourly cross-correlation of start counts must peak at lag 0.
    """
    v = union(vol[['oblast', 'started_at', 'finished_at']].rename(columns={'started_at': 'start', 'finished_at': 'end'}),
              'oblast')
    common = sorted(set(src['oblast']) & set(v['oblast']))
    s = src[src['oblast'].isin(common) & (src['start'] >= lo) & (src['start'] < hi)]
    v = v[v['oblast'].isin(common) & (v['start'] >= lo) & (v['start'] < hi)]
    tol = tol_min * 60
    lags, matched_src, matched_vol = [], 0, 0
    for ob in common:
        a, b = np.sort(to_sec(s.loc[s['oblast'] == ob, 'start'])), np.sort(to_sec(v.loc[v['oblast'] == ob, 'start']))
        if len(a) == 0 or len(b) == 0:
            continue
        d = _to_nearest(a, b)
        lags += list(d[np.abs(d) <= tol])
        matched_src += int((np.abs(d) <= tol).sum())
        matched_vol += int((np.abs(_to_nearest(b, a)) <= tol).sum())
    hours = pd.date_range(lo, hi, freq='h', inclusive='left')
    cs = s['start'].dt.floor('h').value_counts().reindex(hours, fill_value=0).to_numpy(float)
    cv = v['start'].dt.floor('h').value_counts().reindex(hours, fill_value=0).to_numpy(float)
    xcorr = {lag: float(np.corrcoef(np.roll(cs, lag)[3:-3], cv[3:-3])[0, 1]) for lag in range(-3, 4)}
    return {'oblasts': len(common), 'source_starts': len(s), 'volunteer_starts': len(v),
            'source_starts_matched': matched_src / max(len(s), 1), 'volunteer_starts_matched': matched_vol / max(len(v), 1),
            'median_lag_s': float(np.median(lags)) if lags else np.nan,
            'best_lag_h': max(xcorr, key=xcorr.get), 'xcorr': xcorr}


def _to_nearest(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """For each sorted point of a, a minus the nearest point of sorted, non-empty b."""
    k = np.searchsorted(b, a)
    left, right = b[np.clip(k - 1, 0, len(b) - 1)], b[np.clip(k, 0, len(b) - 1)]
    return np.where(np.abs(right - a) < np.abs(
… [обрезано: показано 3000 из 13927 символов]
```

</details>

<details><summary>🔧 Bash: Read API check script setup part · 20:34</summary>

**Аргументы**

```bash
sed -n 1,100p scripts/api_check.py
```

**Результат**

```
"""Stage 8: check the frozen models on fresh alerts.in.ua data (PLAN stage 8, D22).

    python scripts/fetch_alerts_in_ua.py --all-oblasts     # needs your own token
    python scripts/api_check.py

Needs the main pipeline outputs (python scripts/run_all.py): units, neighbours, tuned hyperparameters.
Writes data/alerts_in_ua_locations.csv and reports/api_check.md; raw API data stay in the git-ignored
data/raw/alerts_in_ua.
"""
import json
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from alerts import api_check as ac  # noqa: E402
from alerts import figures, leakage, store  # noqa: E402
from alerts.config import ROOT, load_config, path, ts  # noqa: E402
from alerts.backtest import walk_forward  # noqa: E402
from alerts.ingest.alerts_in_ua import KYIV_UK, build_locations, load_alerts_in_ua, norm, read_raw  # noqa: E402
from alerts.metrics import bootstrap  # noqa: E402
from alerts.models.baselines import UnitHourRate  # noqa: E402
from alerts.metrics import METRICS  # noqa: E402
from alerts.models import registry  # noqa: E402
from alerts.pipeline import build_all, build_tables, model_data  # noqa: E402

logger = logging.getLogger('api_check')


def main() -> int:
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(name)s: %(message)s')
    t0 = time.time()
    cfg = load_config()
    out = path(cfg, 'reports')
    md = ['# Check on fresh data: alerts.in.ua (stage 8)', '',
          'Generated by `scripts/api_check.py`. Decisions: DECISIONS.md, D22. The sources are not joined (D02): '
          'models are fitted once on the Vadimkin data and only predict here.', '']

    # 8.1-8.2: raw data, locations, adapter
    raw_dir = ROOT / cfg['api']['raw_dir']
    manifest = pd.read_json(raw_dir / 'manifest.jsonl', lines=True)
    raw = read_raw(raw_dir)
    units = store.load_units(cfg)
    neighbors = pd.read_csv(path(cfg, 'neighbors'))
    locations = build_locations(units, cfg)
    locations.to_csv(ROOT / 'data' / 'alerts_in_ua_locations.csv', index=False)
    recs, st = load_alerts_in_ua(raw, locations)
    have = set(zip(recs['oblast'], recs['raion'].fillna(recs['oblast'])))
    missing = [k for k in zip(locations['oblast'], locations['raion']) if k not in have]
    api_names = raw[(raw['location_type'] == 'raion') | (raw['location_title'] == KYIV_UK)]
    api_names = api_names.drop_duplicates(['location_oblast', 'location_title'])
    api_names = api_names.assign(o=norm(api_names['location_oblast']), n=norm(api_names['location_title']))
    pairs = api_names.merge(locations.assign(o=norm(locations['oblast_uk']), n=norm(locations['title_uk'])), on=['o', 'n'])
    pairs.loc[pairs['oblast'] == 'Kyiv City', 'o'] = KYIV_UK            # Kyiv: matched by title, its oblast is itself
    md += ['## Download and adapter (8.1, 8.2)', '',
           f"- Requests: {len(manifest)}, statuse
… [обрезано: показано 3000 из 5879 символов]
```

</details>

<details><summary>🔧 Bash: Recompute frozen B1 on API data in memory · 20:35</summary>

**Аргументы**

```bash
cat > /d/Flash/golova/KSE_AI/AAFS/reviews/scratch/stage7/api_b1.py <<'EOF'
"""api_check.md h=1 frozen B1 PR-AUC 0.398 [0.382, 0.418] equals results.md h=1 B1 to 3 digits. Coincidence or bug?
Recompute the frozen baselines in memory (raw API files read locally, no network, nothing written)."""
import pandas as pd
from alerts import api_check as ac, store
from alerts.config import ROOT, load_config, path, ts
from alerts.ingest.alerts_in_ua import build_locations, load_alerts_in_ua, read_raw
from alerts.metrics import bootstrap
from alerts.models import registry
from alerts.pipeline import build_all, build_tables, model_data

cfg = load_config()
raw = read_raw(ROOT / cfg['api']['raw_dir'])
units = store.load_units(cfg)
neighbors = pd.read_csv(path(cfg, 'neighbors'))
recs, st = load_alerts_in_ua(raw, build_locations(units, cfg))
cfg_a = ac.api_config(cfg, raw)
data_a = model_data(build_tables(recs, cfg_a, units=units, neighbors=neighbors), cfg_a)
data_v = model_data(build_all(cfg), cfg)
bs = cfg['bootstrap']
main = pd.read_parquet('data/predictions_h1.parquet').query("part == 'test'")
for h in (1,):
    preds = ac.frozen_predictions(data_v, ts(cfg['data_end']), data_a, h, registry(cfg, ['B0', 'B1', 'B2']))
    t = bootstrap(preds, ['B0', 'B1', 'B2'], bs['n_reps'], bs['seed'], bs['ci'], 'B1')
    r = t[(t.model == 'B1') & (t.metric == 'pr_auc')].iloc[0]
    print(f"API frozen B1 h={h}: rows {len(preds)}, pos {preds.y.sum()}, days {preds.day.nunique()}, "
          f"PR-AUC {r.value:.5f} [{r.lo:.5f}, {r.hi:.5f}]")
    tm = bootstrap(main, ['B1'], bs['n_reps'], bs['seed'], bs['ci'])
    r = tm[tm.metric == 'pr_auc'].iloc[0]
    print(f"main test B1 h={h}: rows {len(main)}, PR-AUC {r.value:.5f} [{r.lo:.5f}, {r.hi:.5f}]")
    print('same prediction vectors?', len(preds) == len(main))
EOF
cd /d/Flash/golova/KSE_AI/AAFS && PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage7/api_b1.py 2>&1 | grep -v -E "^INFO|WARNING|Channel"
```

**Результат**

```
API frozen B1 h=1: rows 42151, pos 7501, days 23, PR-AUC 0.39842 [0.38161, 0.41785]
main test B1 h=1: rows 46574, PR-AUC 0.39820 [0.38171, 0.41786]
same prediction vectors? False
```

</details>

<details><summary>🔧 Bash: Rebuild grid without outage mask to check README claim · 20:36</summary>

**Аргументы**

```bash
cat > /d/Flash/golova/KSE_AI/AAFS/reviews/scratch/stage7/no_outage_mask.py <<'EOF'
"""README:54-55 / D15: 'без маски 13% тестових рядків були б хибними нулями' (7 457 rows, 13.4%, 0.5% positive)."""
import copy
import pandas as pd
from alerts.config import load_config, ts
from alerts.pipeline import build_all

cfg = load_config()
c2 = copy.deepcopy(cfg)
c2['thresholds']['outage_gap_hours'] = 10 ** 6
art = build_all(c2)
g = art.grid[(art.grid['part'] == 'test') & art.grid['y_3'].notna()]
o0, o1 = ts('2026-08-29T05:55:28Z'), ts('2026-09-02T13:48:04Z')
inside = g[(g['t'] >= o0) & (g['t'] < o1)]
print(f'test rows h=3 with label, no outage mask: {len(g):,}; inside the outage: {len(inside):,} '
      f'({len(inside) / len(g):.1%}); positives inside {inside["y_3"].mean():.3%}; outside {g.drop(inside.index)["y_3"].mean():.3f}; '
      f'base rate all {g["y_3"].mean():.3f}')
print('units with rows inside the outage:', inside['unit_id'].nunique())
EOF
cd /d/Flash/golova/KSE_AI/AAFS && PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage7/no_outage_mask.py 2>&1 | grep -v -E "^INFO|WARNING|Channel"
```

**Результат**

```
test rows h=3 with label, no outage mask: 55,493; inside the outage: 7,280 (13.1%); positives inside 0.522%; outside 0.259; base rate all 0.226
units with rows inside the outage: 70
```

</details>

<details><summary>🔧 Bash: Check whether all reference rows are verified in code · 20:36</summary>

**Аргументы**

```bash
grep -rn -E "14389|14 389|42004|42 004|15\.93|0\.46" src scripts tests --include=*.py; echo "exit $?"; grep -n "DECISIONS" src/alerts/report.py scripts/run_all.py
```

**Результат**

```
exit 1
src/alerts/report.py:3:Every number of the DECISIONS.md reference table is recomputed and compared (PLAN rule 8).
src/alerts/report.py:20:# DECISIONS.md, "Справочные цифры". Records: target scope, start >= work_start, after D03 cleaning.
src/alerts/report.py:96:             'Generated by `scripts/run_all.py`. Reference values: DECISIONS.md, "Справочные цифры".', '',
src/alerts/report.py:160:    lines = ['# Stage 3 summary', '', 'Generated by `scripts/run_all.py`. Decisions: DECISIONS.md, D17.', '',
scripts/run_all.py:6:Exits with code 1 if a recomputed number differs from the DECISIONS.md reference table or if the
```

</details>

*[ошибка API · 20:36: You&#x27;ve hit your weekly limit · resets 2am (Europe/Kyiv)]*

<details><summary>🔧 Bash: Count invisible isolated forecasts in figure · 08:42</summary>

**Аргументы**

```bash
cat > /d/Flash/golova/KSE_AI/AAFS/reviews/scratch/stage7/fig_gaps.py <<'EOF'
"""forecast_vs_fact.png: how many hourly forecasts are invisible (isolated points of a line without markers)
and what causes the gaps (unit under alert or not)."""
import pandas as pd
from alerts.config import load_config
from alerts import store
cfg = load_config()
p = pd.read_parquet('data/predictions_h3.parquet').query("part == 'test'")
p = p[p['t'] < p['t'].min() + pd.Timedelta(days=cfg['report']['forecast_days'])]
units = store.load_units(cfg)
pick = units[units['raion'].isin(cfg['report']['forecast_units'])].drop_duplicates('unit_id')
g = pd.read_parquet('data/grid.parquet')
for _, u in pick.iterrows():
    s = p[p['unit_id'] == u['unit_id']].set_index('t').sort_index()
    full = pd.date_range(s.index.min(), s.index.max(), freq='h')
    has = pd.Series(full.isin(s.index), index=full)
    iso = has & ~has.shift(1, fill_value=False) & ~has.shift(-1, fill_value=False)
    miss = full[~has.to_numpy()]
    gu = g[(g['unit_id'] == u['unit_id'])].set_index('t')
    st = gu.reindex(miss)['status'].fillna('no candidate').value_counts().to_dict() if 'status' in gu else {}
    print(f"{u['raion']}: hours {len(full)}, forecasts {int(has.sum())}, invisible isolated points {int(iso.sum())}, "
          f"gaps {len(miss)}; grid status of gap hours: {st}")
EOF
cd /d/Flash/golova/KSE_AI/AAFS && python -c "import pandas as pd; print(pd.read_parquet('data/grid.parquet').columns.tolist())"; PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage7/fig_gaps.py
```

**Результат**

```
['unit_id', 't', 'oblast', 'part', 'y_1', 'y_3', 'y_6']
Dniprovskyi raion: hours 168, forecasts 134, invisible isolated points 7, gaps 34; grid status of gap hours: {}
Kyiv City: hours 168, forecasts 158, invisible isolated points 0, gaps 10; grid status of gap hours: {}
Odeskyi raion: hours 168, forecasts 134, invisible isolated points 2, gaps 34; grid status of gap hours: {}
```

</details>

<details><summary>🔧 Bash: Collect line numbers for findings · 08:42</summary>

**Аргументы**

```bash
grep -n -E "Таблицу сверяет|Строк сетки при h = 3|Дополнительная проверка на сентябре|Основной горизонт — h = 3|B1 и модели наравне|Калибровка LR и LightGBM|завышен втрое|Выигрыш моделей виден|Тревог на единицу|Записей в охвате|рабочий период для всех|Совпасть бит в бит|Реальная версия — в|Синтетическая версия" DECISIONS.md; grep -n -E "втрое|Критерий|Что сдаём|reports/backtest_h\*|predictions_h3|tuning_h3|Одна команда" PLAN.md; grep -n -E "Моделі кращі|Калібрування|Основний виграш|звіряє|кожну перевірено|30 днів|Процес|27 випадків|Запуск|pip install" README.md
```

**Результат**

```
39:- Дополнительная проверка на сентябре–октябре через API alerts.in.ua — вне MVP, если успеют выдать токен.
82:**Решение:** рабочий период для всех единиц начинается **2025-11-07 00:00 UTC**.
442:**Бэктест** (`src/alerts/backtest.py`): для каждого дня `D` (сутки UTC) новая модель обучается на строках с `t ≤ D − h`, чьи метки к `D` уже известны, и прогнозирует строки с `t ∈ [D, D + 1 сут)`. Строки без метки (D17) не используются. Валидация — 28 дней, тест — 24 дня: в три дня перерыва канала строк нет, а 2 сентября после конца перерыва остаются только строки с неполным окном за 24 часа (D19). У всех моделей один интерфейс `fit(X, y)` / `predict_proba(X)`. Основной горизонт — h = 3 (`config.backtest.horizons`).
467:- Совпасть бит в бит должны прогнозы, обучающие строки с их метками и таблица единиц.
468:- Синтетическая версия — `tests/test_leakage.py` (два среза, h = 1 и 3); падает, если признак взять на час позже или обучаться на `t ≤ cut`.
469:- Реальная версия — в `run_all.py`, срезы 2026-08-10 00:00 и 2026-08-21 14:00, результат в `reports/leakage_check.json`. Проверка пройдена: 568 и 593 тысячи обучающих строк, будущее после среза действительно изменилось.
548:- Выигрыш моделей виден **внутри областей**, где B1 почти ничего не добавляет к B0. PR-AUC LR против B1: Киев 0.63 против 0.34, Киевская область 0.55 против 0.34, Кировоградская 0.53 против 0.38, Полтавская 0.66 против 0.57. Там, где всё решает идентичность единицы (Сумская, Харьковская), B1 и модели наравне. На западе положительных единицы или десятки, и интервалы слишком широки для выводов.
549:- Калибровка LR и LightGBM на тесте близка к диагонали; B1 недооценивает средние вероятности (`reports/figures/calibration_h3.png`).
553:**Проверка утечки** пройдена для всех пяти моделей в обоих срезах на реальных данных (`reports/leakage_check.json`): обучающие строки, метки, признаки и прогнозы совпали бит в бит, набор строк в момент среза совпал полностью. Синтетическая версия (`tests/test_leakage.py`) включает LR и LightGBM с весом свежести.
653:Определения: записи целевого охвата (D05) с началом `≥ work_start`, после очистки D03. Таблицу сверяет `scripts/run_all.py`: при любом расхождении он завершается с кодом 1, а сверка лежит в `reports/stage1_summary.md`.
659:| Записей в охвате (начало ≥ work_start, 111 локаций) | 80 194 (было 80 196: в число входили 2 записи нулевой длительности; при старом фильтре «начало ≤ data_end» отчёт давал 80 148) |
660:| Тревог на единицу: min / p10 / медиана / p90 / max | 87 / 92 / 604 / 1 567 / 2 253 |
669:| Строк сетки при h = 3: обучение / валидация / тест (D17) | 510 642 / 57 865 / 48 028 |
703:| 26 | Вывод «модель через месяц на новом источнике выигрывает у B1 +0.09 PR-AUC» был бы завышен втрое: замороженный B1 устарел вместе со своей таблицей | Claude Code, этап 8 | Разбор результата: откуда вдруг втрое больший выигрыш, чем на основном тесте | Добавлен B1, обновляемый на данных API; против него +0.021 при h = 3 (D22) |
8:- Что сдаём: ссылку на GitHub-ре
… [обрезано: показано 3000 из 5198 символов]
```

</details>

<details><summary>🔧 Bash: Check line endings of committed files · 08:42</summary>

**Аргументы**

```bash
git ls-files --eol data/*.csv reports/*.md reports/*.csv README.md | head -20; git config --get core.autocrlf; ls .gitattributes 2>&1
```

**Результат** (ошибка)

```
Exit code 2
i/lf    w/lf    attr/                 	README.md
i/lf    w/crlf  attr/                 	data/alerts_in_ua_locations.csv
i/lf    w/crlf  attr/                 	data/intervals.csv
i/lf    w/crlf  attr/                 	data/mask.csv
i/lf    w/crlf  attr/                 	data/neighbors.csv
i/lf    w/crlf  attr/                 	data/seen.csv
i/lf    w/crlf  attr/                 	data/units.csv
i/lf    w/crlf  attr/                 	reports/api_check.md
i/lf    w/crlf  attr/                 	reports/backtest_h1.md
i/lf    w/crlf  attr/                 	reports/backtest_h3.md
i/lf    w/crlf  attr/                 	reports/backtest_h6.md
i/lf    w/crlf  attr/                 	reports/high_sim_pairs.csv
i/lf    w/crlf  attr/                 	reports/results.md
i/lf    w/crlf  attr/                 	reports/stage1_summary.md
i/lf    w/crlf  attr/                 	reports/stage2_summary.md
i/lf    w/crlf  attr/                 	reports/stage3_summary.md
true
ls: cannot access '.gitattributes': No such file or directory
```

</details>

<details><summary>🔧 Bash: Create report folder and list my scratch scripts · 08:43</summary>

**Аргументы**

```bash
mkdir -p reviews/claude && ls reviews/claude reviews/scratch/stage7
```

**Результат**

```
reviews/claude:
stage0-1b.md

reviews/scratch/stage7:
api_b1.py
audit_oblast.py
audit_preds.py
bridge.py
fig_gaps.py
mutations.py
no_outage_mask.py
pairs_diff.py
repro.py
secrets_scan.py
secrets_scan2.py
```

</details>

<details><summary>🔧 Write: reviews/claude/stage7.md · 08:44</summary>

**Аргументы**

```
# file: reviews/claude/stage7.md
# Ревью этапа 7: отчёт, README, соответствие документов цифрам, воспроизводимость, сдача

Скрипты лежат в `reviews/scratch/stage7/`. Запуск из корня: `PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage7/<x>.py`. Все скрипты только читают данные и ничего не пишут в `data/` и `reports/`.

## 1. Резюме

Цифры отчётов воспроизводятся полностью:
- `results.md` и `backtest_h*.md` точно пересчитываются из `data/predictions_h*.parquet`;
- текущий код на одном дне теста выдаёт прогнозы, побитно совпадающие с parquet;
- закоммиченные `data/*.csv`, сводки этапов 1–3 и пять графиков данных совпадают с пересборкой в памяти;
- в истории git нет секретов.

Слабые места — в тексте и комплекте сдачи, а не в числах:
1. Раздел README «Результат» говорит больше, чем показывают данные. Значимость есть только у LightGBM. Тезис «основной выигрыш — внутри областей» данными не подтверждается: пары из одной области дают около 15% прироста общего ROC-AUC.
2. Проверка утечки на реальных данных и синтетический тест вообще не вызывают код бэктеста: отбор обучающих строк в них — собственная копия.
3. В репозитории нет логов работы с ИИ и рефлексии, а дедлайн — сегодня (12.10) в 23:59.

Остальное — мелочи формулировок и устаревшие фразы. **Вердикт:** результаты надёжны; README и DECISIONS нужно поправить за 1–2 часа, `run_all.py` перезапускать не нужно.

## 2. Находки

### S7-1. README «Результат»: утверждения сильнее данных
- **Серьёзность:** существенно (вывод README).
- **Уверенность:** проверено на данных.
- **Где:** `README.md:26-29`; DECISIONS D20, `DECISIONS.md:548`.

**(а) «Моделі кращі… різниця статистично значуща».** Это верно только для LightGBM. Логистическая регрессия против B1 по `results.md`:
- PR-AUC при h = 3: +0.018 [−0.003, +0.036];
- PR-AUC при h = 6: +0.013 [−0.005, +0.029];
- log loss при h = 6: −0.009 [−0.029, +0.008].

**(б) «Основний виграш — усередині областей».** ROC-AUC при h = 3 я разложил на пары «положительная строка ×
… [обрезано: показано 2000 из 17077 символов]
```

**Результат**

```
File created successfully at: D:\Flash\golova\KSE_AI\AAFS\reviews\claude\stage7.md (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Bash: Adjust Python version wording, check report length · 08:44</summary>

**Аргументы**

```bash
sed -i 's/строки «Python ≥ 3.12; первый запуск клонирует около 0.7 ГБ»/строки «проверено на Python 3.12; первый запуск клонирует около 0.7 ГБ»/' reviews/claude/stage7.md && grep -n "Python 3.12" reviews/claude/stage7.md && wc -l reviews/claude/stage7.md && git status --short
```

**Результат**

```
193:**Что сделать (10 мин):** строки «проверено на Python 3.12; первый запуск клонирует около 0.7 ГБ».
246 reviews/claude/stage7.md
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

<details><summary>🔧 SubagentHandback: {"message": "Отчёт по этапу 7 записан в `D:\\Flash\\golova\\KSE_AI\\AAFS\\reviews\\claude\\stage7.md` (246 строк). Скри… · 08:45</summary>

**Аргументы**

```json
{
 "message": "Отчёт по этапу 7 записан в `D:\\Flash\\golova\\KSE_AI\\AAFS\\reviews\\claude\\stage7.md` (246 строк). Скрипты лежат в `reviews/scratch/stage7/`. Файлы проекта, git, токен и чужие отчёты не трогал. `.gitignore` в рабочей копии помечен как изменённый — это сделал не я.\n\n**Резюме**\n- Цифры отчётов воспроизводятся полностью:\n  - `results.md` и `backtest_h*.md` точно пересчитываются из `data/predictions_h*.parquet` с сидом конфига;\n  - текущий код на дне теста 2026-08-10 (h=3, все 5 моделей, 2 026 строк) даёт прогнозы, побитно равные parquet;\n  - `data/*.csv`, сводки этапов 1–3 и 5 графиков данных совпадают с пересборкой в памяти.\n- 26 тестов проходят. Секретов во всех 29 коммитах на всех ветках нет.\n- Совпадение B1 при h=1 в `api_check.md` и `results.md` (0.398 [0.382, 0.418]) — случайность: 0.39842 против 0.39820, векторы прогнозов разные.\n- Подмены «признак видит будущее» (`starts_*` сдвинуты на час; страновой счётчик смотрит вперёд) ловят оба теста на утечку. А отбор обучающих строк бэктеста не проверяет никто.\n- README в разделе «Результат» говорит больше, чем показывают данные. Значимость есть только у LightGBM. Пары из одной области дают лишь около 15% прироста общего ROC-AUC.\n- В репозитории нет логов работы с ИИ и рефлексии на ~100 слов, а дедлайн сегодня (12.10) в 23:59.\n- Мелочи:\n  - калибровка LR при h=6 хуже, чем у B1 (ECE 0.026 против 0.018);\n  - `run_all.py` сверяет зашитую в `report.py` копию справочных цифр, и две строки таблицы не сверяются нигде;\n  - четыре разных числа «тестовых строк» без пояснения;\n  - устаревшие фразы: D02, D18, «завышен втрое» (на деле 4.5× при h=3);\n  - подпись графика «прогноз против факта» неполна, часть одиночных точек не видна.\n- **Вердикт:** результаты надёжны. Нужно 1–2 часа правок текста и комплекта сдачи; `run_all.py` перезапускать не нужно.\n\n**Критично:** нет.\n\n**Существенно:**\n- **S7-1.** Раздел «Результат» в README завышает выводы.\n  - «Моделі… статистично значуща» верно только дл
… [обрезано: показано 2000 из 3442 символов]
```

**Результат**

```
{"success":true,"message":"Report delivered to your caller."}
```

</details>
