# Субагент: Review stages 4 and 6

- **Агент:** `a62651ca292513a30` (general-purpose), запущен из сессии [57049ae5](../2026-10-11_critical-analysis_57049ae5.md#t-oF43pw3aDZFo)
- **Период (UTC):** 2026-10-11 17:19 → 2026-10-12 05:46
- **Период (Киев):** 2026-10-11 20:19 → 2026-10-12 08:46
- **Сообщений:** 2 (задания и сообщения основного агента — 1, ответы субагента — 1); вызовов инструментов — 40
- **Исходный JSONL:** `ai_logs/claude_code/raw/claude_code_raw.zip → subagents/57049ae5_agent-a62651ca292513a30.jsonl`

> Служебные вставки (`<system-reminder>`, вложения с окружением и контекстом IDE, мета-сообщения — 76 записей) и блоки рассуждений (thinking — 28) сюда не включены: они есть в исходном JSONL. Время — киевское. Вызовы инструментов свёрнуты; аргументы обрезаны до 2000 символов, результаты — до 3000. Токен alerts.in.ua и email автора заменены на `[REDACTED_TOKEN]` / `[REDACTED_EMAIL]`.

---

<a id="m-5bf94e76"></a>

### 📨 Задание от основного агента · 2026-10-11 20:19

Рабочая папка проекта: d:\Flash\golova\KSE_AI\AAFS (Windows; доступны Bash (Git Bash) и PowerShell).

Прочитай файл `reviews/prompts/04_stages4-6.md` целиком и выполни задание из него в точности, включая все ограничения: не изменять файлы проекта, не запускать `scripts/run_all.py`, `scripts/api_check.py`, скрипты скачивания и `save_all`, не трогать git, не открывать токен. Параллельно с тобой в той же папке работают шесть других агентов-ревьюеров — пиши только в `reviews/stage4-6.md` и `reviews/scratch/stage4-6/`.

Когда отчёт записан, верни в ответе: резюме отчёта (5–10 строк) и список находок уровня «критично» и «существенно» — по одной строке на находку (id, суть, файл:строка, уровень проверки).

<details><summary>🔧 Read: reviews/prompts/04_stages4-6.md · 20:19</summary>

**Аргументы**

```json
{
 "file_path": "d:\\Flash\\golova\\KSE_AI\\AAFS\\reviews\\prompts\\04_stages4-6.md"
}
```

**Результат**

```
1	# Ревью проекта AAFS: этапы 4 и 6: бэктест, бейзлайны, метрики, модели, подбор
2	
3	Ты — независимый критический ревьюер. Параллельно с тобой другие агенты проверяют другие этапы того же проекта. Твоя зона — этапы 4 и 6: walk-forward бэктест, бейзлайны B0–B2, метрики и бутстреп, модели LR и LightGBM, подбор гиперпараметров, отчёты бэктеста. На соседние этапы смотри только тогда, когда без этого не понять твой.
4	
5	## Проект
6	
7	- Репозиторий — текущая папка (`AAFS`), ветка `stages-7-8`. Python-проект: прогноз воздушных тревог в Украине по районам. Для каждой единицы (район; Киев — одна единица), где в момент `t` (каждый час) тихо, модель выдаёт вероятность того, что тревога начнётся в `(t, t+h]`, h = 1, 3, 6 (основной — 3).
8	- Данные — снимок датасета Vadimkin (`dataset_repo/`, коммит `58ee75b`). Официальный ряд заканчивается 2026-09-07. Тест — 2026-08-10…2026-09-07, walk-forward с ежесуточным переобучением. Этап 8 — проверка на данных alerts.in.ua за сентябрь–октябрь.
9	- Это тестовое задание с дедлайном 12.10.2026 23:59 по Киеву. Проверяющие оценивают процесс: пойманные ошибки, обоснованность решений, отсутствие утечки из будущего. Найденная проблема ценна, даже если её не успеют исправить: тогда она уйдёт в раздел ограничений.
10	- Документы: `PLAN.md` (правила работы 1–13; у каждого этапа «Исходное задание» и «Как сделано»), `DECISIONS.md` (решения D00–D22, справочные цифры, журнал пойманных ошибок ИИ), `README.md` (на украинском), отчёты в `reports/`.
11	
12	Сначала прочитай раздел «Правила работы» в `PLAN.md`, описание своего этапа в `PLAN.md` и разделы `DECISIONS.md`: D14, D17 (частоты), D18, D20; README, раздел «Результат». Код и тесты своей зоны читай целиком, а не выборочно.
13	
14	## Твоя зона: файлы
15	
16	- `src/alerts/backtest.py`.
17	- `src/alerts/models/`: `baselines.py`, `learned.py`, `__init__.py`.
18	- `src/alerts/metrics.py`, `src/alerts/tuning.py`, `src/alerts/evaluation.py`.
19	- `config.yaml`: разделы `backtest`, `models`, `baselines`, `bootstrap`.
20	- Тесты: `tests/test_metrics.py`.
21	- Результаты: `reports/backtest_h{1,3,6}.md`, `reports/results.md`, `reports/tuning_h{1,3,6}.json`, `reports/figures/calibration_h*.png`, `data/predictions_h{1,3,6}.parquet`.
22	
23	## Что проверить
24	
25	1. **Walk-forward (`backtest.walk_forward`).**
26	   - Граница `t ≤ D − h` — верна ли она для всех h?
27	   - Что, если в какой-то день нет строк у части моделей?
28	   - Как в `run` выравниваются прогнозы разных моделей по индексу?
29	2. **Воспроизводимость.** Переобучи LightGBM и LR на одном дне теста (h = 3, 8 потоков) и сравни с `predictions_h3.parquet` бит в бит.
30	3. **Подбор гиперпараметров (`tuning.py`).**
31	   - Модель при подборе обучается один раз до `train_end`, а в бэктесте переобучается каждый день.
32	   - Число деревьев из ранней остановки переносится на обучающую выборку, которая к концу теста на ~2 месяца больше.
33	   - Разброс log loss кандидатов около 0.004 — больше ли это шума? Выбирается ли что-то осмысленное
… [обрезано: показано 3000 из 9280 символов]
```

</details>

<details><summary>🔧 Bash: List project structure and file sizes · 20:19</summary>

**Аргументы**

```bash
ls && ls reviews reviews/scratch 2>/dev/null; wc -l PLAN.md DECISIONS.md README.md src/alerts/*.py src/alerts/models/*.py tests/*.py config.yaml; ls reports data
```

**Результат**

```
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
    18 src/alerts/models/__init__.py
    81 src/alerts/models/baselines.py
    94 src/alerts/models/learned.py
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
   110 config.yaml
  4523 total
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

<details><summary>🔧 Read: DECISIONS.md · 20:19</summary>

**Аргументы**

```json
{
 "file_path": "d:\\Flash\\golova\\KSE_AI\\AAFS\\DECISIONS.md",
 "offset": 518,
 "limit": 200
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

<details><summary>🔧 Bash: Show backtest and model source files · 20:19</summary>

**Аргументы**

```bash
cat -n src/alerts/backtest.py src/alerts/models/__init__.py src/alerts/models/baselines.py src/alerts/models/learned.py
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
    
… [обрезано: показано 3000 из 12862 символов]
```

</details>

<details><summary>🔧 Bash: Show metrics, tuning, evaluation, tests · 20:19</summary>

**Аргументы**

```bash
cat -n src/alerts/metrics.py src/alerts/tuning.py src/alerts/evaluation.py tests/test_metrics.py
```

**Результат**

```
1	"""Metrics, day-block bootstrap and calibration (PLAN stage 4, D18).
     2	
     3	Units are strongly correlated within a moment (waves), so rows are not independent: the bootstrap
     4	resamples whole forecast days with replacement. The same day draws are used for every model,
     5	which gives paired confidence intervals for differences between models.
     6	
     7	PR-AUC and ROC-AUC are computed here with one sort per call and exact handling of tied scores
     8	(baselines produce many ties); tests check them against scikit-learn.
     9	"""
    10	import numpy as np
    11	import pandas as pd
    12	
    13	EPS = 1e-6
    14	METRICS = ['pr_auc', 'roc_auc', 'brier', 'log_loss']
    15	HIGHER_IS_BETTER = {'pr_auc': True, 'roc_auc': True, 'brier': False, 'log_loss': False}
    16	
    17	
    18	def score(y: np.ndarray, p: np.ndarray) -> dict:
    19	    y = np.asarray(y, dtype=float)
    20	    p = np.clip(np.asarray(p, dtype=float), EPS, 1 - EPS)
    21	    out = {'brier': float(np.mean((p - y) ** 2)),
    22	           'log_loss': float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))}
    23	    n_pos = y.sum()
    24	    n_neg = len(y) - n_pos
    25	    if n_pos == 0 or n_neg == 0:
    26	        return {'pr_auc': np.nan, 'roc_auc': np.nan, **out}
    27	    values, inverse, counts = np.unique(p, return_inverse=True, return_counts=True)   # ascending
    28	    pos = np.bincount(inverse, weights=y, minlength=len(values))
    29	    # ROC-AUC from average ranks (Mann-Whitney U)
    30	    avg_rank = np.cumsum(counts) - (counts - 1) / 2
    31	    out['roc_auc'] = float(((avg_rank * pos).sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg))
    32	    # PR-AUC as average precision over distinct thresholds, highest score first
    33	    tp = np.cumsum(pos[::-1])
    34	    seen = np.cumsum(counts[::-1])
    35	    recall_step = pos[::-1] / n_pos
    36	    out['pr_auc'] = float((recall_step * tp / seen).sum())
    37	    return {k: out[k] for k in METRICS}
    38	
    39	
    40	def bootstrap(preds: pd.DataFrame, models: list, n_reps: int, seed: int, ci: float = 0.95,
    41	              reference: str | None = None) -> pd.DataFrame:
    42	    """Point estimate and percentile CI per model and metric, resampling forecast days.
    43	
    44	    With `reference`, also the paired difference (model - reference) and its CI.
    45	    """
    46	    day = preds['day'].to_numpy()
    47	    uniq = np.unique(day)
    48	    by_day = [np.flatnonzero(day == d) for d in uniq]
    49	    y = preds['y'].to_numpy(dtype=float)
    50	    P = {m: preds[f'p_{m}'].to_numpy() for m in models}
    51	    rng = np.random.default_rng(seed)
    52	    draws = {m: {k: np.empty(n_reps) for k in METRICS} for m in models}
    53	    for r in range(n_reps):
    54	        idx = np.concatenate([by_day[i] for i in rng.integers(0, len(uniq), len(uniq))])
    55	        for m in models:
    56	            
… [обрезано: показано 3000 из 19112 символов]
```

</details>

<details><summary>🔧 Bash: Show config and pipeline · 20:20</summary>

**Аргументы**

```bash
cat -n config.yaml && cat -n src/alerts/pipeline.py
```

**Результат**

```
1	dataset:
     2	  repo_url: "https://github.com/Vadimkin/ukrainian-air-raid-sirens-dataset"
     3	  commit: "58ee75bc20113181b9ddf8029d4cbf3a62d8cd10"   # D01
     4	  repo_dir: "dataset_repo"
     5	  path: "dataset_repo/datasets/official_data_en.csv"
     6	  sha256: "b396f87696243069eec0219880e87dcd642b20beb0a7bae0d0e1f61e1ed20ec4"
     7	  path_uk: "dataset_repo/datasets/official_data_uk.csv"   # same records in Ukrainian, row by row (D22)
     8	  sha256_uk: "1f50085481d229f57b624d83b1ce723e884dea409c14afb5b7040c8a2f233e4f"
     9	
    10	volunteer:                                             # stage 8.4: triangulation, the newest volunteer series
    11	  commit: "bf0c323c78e3e4508721458797dcd38c95df13f3"
    12	  path: "datasets/volunteer_data_en.csv"               # read with git show, the pinned snapshot is untouched
    13	  sha256: "d03747ee8bf056032b2eeef50cdcf964d65fa60a92243e91862db48b31377465"
    14	
    15	data_end: "2026-09-07T00:00:00Z"                       # D13
    16	
    17	periods:                                               # D04, D14
    18	  work_start: "2025-11-07T00:00:00Z"
    19	  warmup_end: "2025-11-14T00:00:00Z"
    20	  train_end: "2026-07-13T00:00:00Z"
    21	  val_end: "2026-08-10T00:00:00Z"
    22	
    23	scope:                                                 # D05, D06
    24	  # Unknown oblast names raise an error, so the list must match the data exactly.
    25	  # Crimea and Sevastopol are not in the data at all.
    26	  excluded_oblasts: ["Luhanska oblast"]
    27	  input_only_oblasts: ["Donetska oblast"]              # D06: input features only, never a target
    28	  oblast_level_units: ["Kyiv City"]                    # D05: unit built from oblast-level records
    29	
    30	thresholds:
    31	  pause_merge_min: 15                                  # D12
    32	  long_alert_hours: 24                                 # D10, rule (a)
    33	  clone_jaccard: 0.997                                 # D07
    34	  similar_pairs_report: 0.95                           # D07, pairs saved for the report
    35	  outage_gap_hours: 6                                  # D15, rule (d)
    36	
    37	geo:                                                   # D19: neighbourhood from the snapshot's raion boundaries
    38	  path: "dataset_repo/example/ukr_admin2.geojson"
    39	  sha256: "2c2a73ef2425281cacff217d1b830b00bf3546f648172d07417f59d8b9f72070"
    40	  vertex_decimals: 5
    41	  min_shared_vertices: 2
    42	  renames:                                             # our raion -> boundary name (raions renamed in 2023-2024)
    43	    "Krasnohradskyi raion": "Berestynskyi"
    44	    "Chervonohradskyi raion": "Sheptytskyi"
    45	    "Volodymyr-Volynskyi raion": "Volodymyrskyi"
    46	
    47	history:                                               # D19: as-of view used by features
    48	  max_open_hours: 24                                   # an alert without an
… [обрезано: показано 3000 из 11107 символов]
```

</details>

<details><summary>🔧 Bash: Show run_all script and features module · 20:20</summary>

**Аргументы**

```bash
cat -n scripts/run_all.py && cat -n src/alerts/features.py
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
… [обрезано: показано 3000 из 12405 символов]
```

</details>

<details><summary>🔧 Bash: Show results, tuning and h3 backtest report · 20:20</summary>

**Аргументы**

```bash
cat reports/results.md && cat reports/tuning_h*.json && cat reports/backtest_h3.md
```

**Результат**

```
# Results: model x horizon (test part)

Walk-forward with daily retraining on the test part (2026-08-10 to 2026-09-07, D14). Intervals: 95% percentile, 1000 bootstrap draws of whole days; differences are paired (same draws). Hyperparameters chosen on validation for each horizon (D20). Details per horizon: `backtest_h<h>.md`.

## Metrics

| h | Rows | Base rate | Model | PR-AUC | ROC-AUC | Brier | Log loss |
|---|---|---|---|---|---|---|---|
| 1 | 46,574 | 0.121 | B0 | 0.131 [0.114, 0.151] | 0.526 [0.485, 0.563] | 0.107 [0.097, 0.118] | 0.373 [0.344, 0.404] |
| 1 | 46,574 | 0.121 | B1 | 0.398 [0.382, 0.418] | 0.830 [0.818, 0.844] | 0.088 [0.080, 0.098] | 0.287 [0.262, 0.318] |
| 1 | 46,574 | 0.121 | B2 | 0.130 [0.113, 0.147] | 0.526 [0.503, 0.545] | 0.107 [0.097, 0.118] | 0.372 [0.344, 0.402] |
| 1 | 46,574 | 0.121 | LR | 0.424 [0.401, 0.446] | 0.859 [0.848, 0.868] | 0.084 [0.077, 0.092] | 0.269 [0.250, 0.291] |
| 1 | 46,574 | 0.121 | LGBM | 0.434 [0.409, 0.458] | 0.862 [0.853, 0.872] | 0.083 [0.077, 0.092] | 0.265 [0.247, 0.286] |
| 3 | 46,270 | 0.255 | B0 | 0.272 [0.235, 0.307] | 0.525 [0.480, 0.563] | 0.191 [0.177, 0.207] | 0.572 [0.540, 0.607] |
| 3 | 46,270 | 0.255 | B1 | 0.674 [0.652, 0.702] | 0.866 [0.854, 0.881] | 0.126 [0.117, 0.136] | 0.381 [0.354, 0.411] |
| 3 | 46,270 | 0.255 | B2 | 0.253 [0.226, 0.279] | 0.498 [0.474, 0.519] | 0.192 [0.179, 0.208] | 0.575 [0.543, 0.610] |
| 3 | 46,270 | 0.255 | LR | 0.692 [0.661, 0.722] | 0.882 [0.869, 0.895] | 0.120 [0.112, 0.129] | 0.367 [0.345, 0.391] |
| 3 | 46,270 | 0.255 | LGBM | 0.701 [0.675, 0.726] | 0.883 [0.871, 0.895] | 0.119 [0.111, 0.128] | 0.360 [0.338, 0.384] |
| 6 | 45,767 | 0.360 | B0 | 0.369 [0.324, 0.414] | 0.507 [0.458, 0.549] | 0.231 [0.220, 0.243] | 0.656 [0.632, 0.679] |
| 6 | 45,767 | 0.360 | B1 | 0.814 [0.788, 0.841] | 0.896 [0.881, 0.913] | 0.125 [0.115, 0.135] | 0.386 [0.354, 0.418] |
| 6 | 45,767 | 0.360 | B2 | 0.351 [0.316, 0.384] | 0.495 [0.478, 0.512] | 0.233 [0.221, 0.244] | 0.659 [0.635, 0.682] |
| 6 | 45,767 | 0.360 | LR | 0.827 [0.793, 0.857] | 0.906 [0.890, 0.920] | 0.120 [0.111, 0.131] | 0.377 [0.353, 0.404] |
| 6 | 45,767 | 0.360 | LGBM | 0.832 [0.805, 0.858] | 0.907 [0.892, 0.920] | 0.119 [0.110, 0.128] | 0.367 [0.343, 0.393] |

## Difference from the best baseline (chosen on validation)

| h | Reference | Model | PR-AUC | Log loss | Brier |
|---|---|---|---|---|---|
| 1 | B1 | LR | +0.026 [+0.011, +0.040] | -0.018 [-0.028, -0.010] | -0.004 [-0.006, -0.003] |
| 1 | B1 | LGBM | +0.036 [+0.019, +0.050] | -0.022 [-0.033, -0.014] | -0.005 [-0.007, -0.003] |
| 3 | B1 | LR | +0.018 [-0.003, +0.036] | -0.014 [-0.027, -0.000] | -0.006 [-0.011, -0.001] |
| 3 | B1 | LGBM | +0.027 [+0.010, +0.041] | -0.021 [-0.033, -0.009] | -0.007 [-0.011, -0.003] |
| 6 | B1 | LR | +0.013 [-0.005, +0.029] | -0.009 [-0.029, +0.008] | -0.005 [-0.011, +0.002] |
| 6 | B1 | LGBM | +0.018 [+0.005, +0.030] | -0.019 [-0.033, -0.006] | -0.006 [-0.011, -0.002] |

F
… [обрезано: показано 3000 из 12781 символов]
```

</details>

<details><summary>🔧 Bash: Show h1 backtest report · 20:20</summary>

**Аргументы**

```bash
cat reports/backtest_h1.md | head -60 && sed -n '/Hyperparameters/,$p' reports/backtest_h1.md
```

**Результат**

```
# Backtest, h = 1

Walk-forward with daily retraining: a model for day D is fitted on rows with t <= D - h. Confidence intervals: 95% percentile, 1000 bootstrap draws of whole forecast days; the same draws for every model, so differences are paired. Reference for differences: **B1** (best baseline by log loss on validation). Decisions: DECISIONS.md, D18.

## Val: 57,865 rows, 7,007 positives, 28 days

| Model | pr_auc | roc_auc | brier | log_loss |
|---|---|---|---|---|
| B0 | 0.1228 [0.1152, 0.1302] | 0.5036 [0.4856, 0.5212] | 0.1074 [0.1009, 0.1138] | 0.3743 [0.3561, 0.3923] |
| B1 | 0.4124 [0.3951, 0.4296] | 0.8364 [0.8222, 0.8504] | 0.0870 [0.0815, 0.0923] | 0.2868 [0.2664, 0.3071] |
| B2 | 0.1180 [0.1080, 0.1292] | 0.4814 [0.4600, 0.5022] | 0.1075 [0.1010, 0.1140] | 0.3754 [0.3573, 0.3939] |
| LR | 0.4054 [0.3870, 0.4272] | 0.8443 [0.8300, 0.8578] | 0.0866 [0.0815, 0.0918] | 0.2792 [0.2634, 0.2956] |
| LGBM | 0.4262 [0.4055, 0.4491] | 0.8475 [0.8334, 0.8602] | 0.0853 [0.0804, 0.0903] | 0.2755 [0.2593, 0.2924] |

Difference from B1 (model - B1); PR-AUC and ROC-AUC: higher is better, Brier and log loss: lower is better:

| Model | pr_auc | roc_auc | brier | log_loss |
|---|---|---|---|---|
| B0 | -0.2896 [-0.3088, -0.2715] | -0.3328 [-0.3567, -0.3095] | +0.0204 [+0.0184, +0.0224] | +0.0875 [+0.0766, +0.0981] |
| B2 | -0.2944 [-0.3133, -0.2746] | -0.3550 [-0.3799, -0.3318] | +0.0205 [+0.0184, +0.0226] | +0.0886 [+0.0767, +0.0997] |
| LR | -0.0069 [-0.0197, +0.0062] | +0.0079 [+0.0016, +0.0137] | -0.0004 [-0.0016, +0.0008] | -0.0077 [-0.0139, -0.0019] |
| LGBM | +0.0138 [+0.0000, +0.0282] | +0.0111 [+0.0045, +0.0182] | -0.0016 [-0.0028, -0.0006] | -0.0113 [-0.0178, -0.0052] |

## Test: 46,574 rows, 5,624 positives, 24 days

| Model | pr_auc | roc_auc | brier | log_loss |
|---|---|---|---|---|
| B0 | 0.1315 [0.1135, 0.1507] | 0.5263 [0.4846, 0.5625] | 0.1069 [0.0969, 0.1181] | 0.3726 [0.3444, 0.4038] |
| B1 | 0.3982 [0.3817, 0.4179] | 0.8302 [0.8177, 0.8443] | 0.0882 [0.0802, 0.0977] | 0.2872 [0.2623, 0.3179] |
| B2 | 0.1302 [0.1130, 0.1474] | 0.5263 [0.5034, 0.5454] | 0.1067 [0.0968, 0.1176] | 0.3718 [0.3443, 0.4023] |
| LR | 0.4242 [0.4006, 0.4457] | 0.8587 [0.8481, 0.8682] | 0.0842 [0.0770, 0.0925] | 0.2690 [0.2497, 0.2914] |
| LGBM | 0.4344 [0.4094, 0.4576] | 0.8625 [0.8533, 0.8716] | 0.0835 [0.0765, 0.0917] | 0.2650 [0.2466, 0.2863] |

Difference from B1 (model - B1); PR-AUC and ROC-AUC: higher is better, Brier and log loss: lower is better:

| Model | pr_auc | roc_auc | brier | log_loss |
|---|---|---|---|---|
| B0 | -0.2667 [-0.2912, -0.2445] | -0.3039 [-0.3533, -0.2632] | +0.0187 [+0.0158, +0.0217] | +0.0854 [+0.0762, +0.0954] |
| B2 | -0.2680 [-0.2876, -0.2491] | -0.3039 [-0.3357, -0.2757] | +0.0185 [+0.0158, +0.0213] | +0.0846 [+0.0755, +0.0946] |
| LR | +0.0260 [+0.0105, +0.0403] | +0.0285 [+0.0178, +0.0377] | -0.0040 [-0.0057, -0.0025] | -0.0182 [-0.0283, -0.0102] |
| LGBM | +0.0362 [+0.0194, +0
… [обрезано: показано 3000 из 5177 символов]
```

</details>

<details><summary>🔧 Bash: Show h6 backtest report and list figures · 20:20</summary>

**Аргументы**

```bash
sed -n '1,50p' reports/backtest_h6.md && sed -n '/Hyperparameters/,$p' reports/backtest_h6.md; ls -la reports/figures data/*.parquet
```

**Результат**

```
# Backtest, h = 6

Walk-forward with daily retraining: a model for day D is fitted on rows with t <= D - h. Confidence intervals: 95% percentile, 1000 bootstrap draws of whole forecast days; the same draws for every model, so differences are paired. Reference for differences: **B1** (best baseline by log loss on validation). Decisions: DECISIONS.md, D18.

## Val: 57,865 rows, 21,971 positives, 28 days

| Model | pr_auc | roc_auc | brier | log_loss |
|---|---|---|---|---|
| B0 | 0.3931 [0.3575, 0.4275] | 0.5130 [0.4851, 0.5397] | 0.2387 [0.2306, 0.2473] | 0.6709 [0.6540, 0.6889] |
| B1 | 0.8322 [0.8125, 0.8534] | 0.8961 [0.8718, 0.9175] | 0.1251 [0.1139, 0.1381] | 0.4055 [0.3549, 0.4694] |
| B2 | 0.3627 [0.3370, 0.3892] | 0.4805 [0.4649, 0.4971] | 0.2400 [0.2323, 0.2486] | 0.6738 [0.6577, 0.6918] |
| LR | 0.8344 [0.8140, 0.8562] | 0.9025 [0.8827, 0.9199] | 0.1237 [0.1127, 0.1360] | 0.3878 [0.3577, 0.4238] |
| LGBM | 0.8388 [0.8169, 0.8619] | 0.8989 [0.8747, 0.9206] | 0.1231 [0.1114, 0.1367] | 0.3889 [0.3479, 0.4380] |

Difference from B1 (model - B1); PR-AUC and ROC-AUC: higher is better, Brier and log loss: lower is better:

| Model | pr_auc | roc_auc | brier | log_loss |
|---|---|---|---|---|
| B0 | -0.4391 [-0.4814, -0.3943] | -0.3831 [-0.4289, -0.3351] | +0.1136 [+0.1036, +0.1226] | +0.2654 [+0.2113, +0.3119] |
| B2 | -0.4695 [-0.5026, -0.4331] | -0.4156 [-0.4504, -0.3780] | +0.1149 [+0.1045, +0.1244] | +0.2683 [+0.2132, +0.3154] |
| LR | +0.0022 [-0.0072, +0.0107] | +0.0064 [-0.0014, +0.0152] | -0.0014 [-0.0054, +0.0030] | -0.0178 [-0.0482, +0.0061] |
| LGBM | +0.0066 [-0.0007, +0.0131] | +0.0028 [-0.0041, +0.0088] | -0.0019 [-0.0051, +0.0011] | -0.0166 [-0.0378, +0.0015] |

## Test: 45,767 rows, 16,472 positives, 23 days

| Model | pr_auc | roc_auc | brier | log_loss |
|---|---|---|---|---|
| B0 | 0.3694 [0.3240, 0.4136] | 0.5068 [0.4580, 0.5491] | 0.2314 [0.2198, 0.2425] | 0.6557 [0.6315, 0.6789] |
| B1 | 0.8137 [0.7881, 0.8408] | 0.8964 [0.8809, 0.9128] | 0.1248 [0.1147, 0.1348] | 0.3857 [0.3539, 0.4181] |
| B2 | 0.3513 [0.3159, 0.3839] | 0.4949 [0.4783, 0.5117] | 0.2330 [0.2214, 0.2439] | 0.6592 [0.6349, 0.6819] |
| LR | 0.8270 [0.7934, 0.8570] | 0.9061 [0.8900, 0.9200] | 0.1202 [0.1114, 0.1306] | 0.3768 [0.3533, 0.4044] |
| LGBM | 0.8317 [0.8047, 0.8577] | 0.9066 [0.8921, 0.9202] | 0.1187 [0.1099, 0.1277] | 0.3671 [0.3429, 0.3926] |

Difference from B1 (model - B1); PR-AUC and ROC-AUC: higher is better, Brier and log loss: lower is better:

| Model | pr_auc | roc_auc | brier | log_loss |
|---|---|---|---|---|
| B0 | -0.4443 [-0.4877, -0.4073] | -0.3896 [-0.4443, -0.3436] | +0.1066 [+0.0916, +0.1205] | +0.2700 [+0.2328, +0.3064] |
| B2 | -0.4624 [-0.4943, -0.4334] | -0.4015 [-0.4284, -0.3744] | +0.1082 [+0.0931, +0.1217] | +0.2735 [+0.2356, +0.3091] |
| LR | +0.0133 [-0.0053, +0.0286] | +0.0097 [-0.0009, +0.0189] | -0.0046 [-0.0113, +0.0019] | -0.0089 [-0.0288, +0.0085] |
| LGBM | +0.0180 [+0.0052, +0.0299] | +0.0102 [+0.0023, +0.0175] | 
… [обрезано: показано 3000 из 5920 символов]
```

</details>

<details><summary>🔧 Bash: Check Python environment and create scratch dir · 20:21</summary>

**Аргументы**

```bash
python --version && python -c "import pandas, numpy, lightgbm, sklearn; print(pandas.__version__, numpy.__version__, lightgbm.__version__, sklearn.__version__)" && nproc; mkdir -p reviews/scratch/stage4-6 && ls reviews/scratch; git log --oneline -3; git status --short | head
```

**Результат**

```
Python 3.12.9
3.0.6 2.5.3 4.7.0 1.9.1
12
stage0-1b
stage4-6
stage5-leakage
stage8
f47ddec reorganize for review
7afa7a4 Stages 7-8: report, model x horizon table, check on fresh alerts.in.ua data
03b3c5b Closed feature access and knowledge-time check (D21); figures module; archive
```

</details>

<details><summary>🔧 Write: reviews/scratch/stage4-6/01_recompute.py · 20:22</summary>

**Аргументы**

```
# file: reviews/scratch/stage4-6/01_recompute.py
"""Recompute report numbers from data/predictions_h{1,3,6}.parquet (read-only)."""
import numpy as np
import pandas as pd

from alerts.config import load_config
from alerts.metrics import bootstrap, score

cfg = load_config()
bs = cfg['bootstrap']
M = ['B0', 'B1', 'B2', 'LR', 'LGBM']
for h in [1, 3, 6]:
    P = pd.read_parquet(f'data/predictions_h{h}.parquet')
    print(f'\n===== h={h}: {len(P)} rows, cols={list(P.columns)}')
    print('index unique:', P.index.is_unique, 'dtypes day/t:', P['day'].dtype, P['t'].dtype)
    print('NaN per p col:', {m: int(P[f'p_{m}'].isna().sum()) for m in M})
    for part in ['val', 'test']:
        g = P[P['part'] == part]
        print(f'  {part}: rows {len(g)}, pos {int(g.y.sum())}, base {g.y.mean():.4f}, days {g.day.nunique()}, '
              f'day range {g.day.min()} .. {g.day.max()}')
        # day consistency: t in [day, day+1)
        bad = ((g['t'] < g['day']) | (g['t'] >= g['day'] + pd.Timedelta(days=1))).sum()
        print('   rows with t outside its day:', int(bad))
        print('   min/max p per model:', {m: (float(g[f'p_{m}'].min()), float(g[f'p_{m}'].max())) for m in M})
    test = P[P.part == 'test']
    b = bootstrap(test, M, bs['n_reps'], bs['seed'], bs['ci'], 'B1').set_index(['model', 'metric'])
    for m in M:
        print('  ', m, ' '.join(f"{k}={b.at[(m,k),'value']:.4f}[{b.at[(m,k),'lo']:.4f},{b.at[(m,k),'hi']:.4f}]"
                               for k in ['pr_auc', 'roc_auc', 'brier', 'log_loss']))
    for m in ['LR', 'LGBM']:
        print('   diff', m, '-B1', ' '.join(f"{k}={b.at[(m,k),'diff']:+.4f}[{b.at[(m,k),'diff_lo']:+.4f},{b.at[(m,k),'diff_hi']:+.4f}]"
                                          for k in ['pr_auc', 'roc_auc', 'brier', 'log_loss']))
    # days per test part with row counts
    print('  rows per test day:', test.groupby(test.day.dt.strftime('%m-%d')).size().to_dict())

```

**Результат**

```
File created successfully at: d:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage4-6\01_recompute.py (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Bash: Recompute metrics from prediction parquets · 20:22</summary>

**Аргументы**

```bash
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage4-6/01_recompute.py 2>&1 | tee reviews/scratch/stage4-6/01_out.txt
```

**Результат**

```
===== h=1: 104439 rows, cols=['day', 'p_B0', 'p_B1', 'p_B2', 'p_LR', 'p_LGBM', 'part', 'y', 't', 'unit_id', 'oblast']
index unique: True dtypes day/t: datetime64[ms, UTC] datetime64[ms, UTC]
NaN per p col: {'B0': 0, 'B1': 0, 'B2': 0, 'LR': 0, 'LGBM': 0}
  val: rows 57865, pos 7007, base 0.1211, days 28, day range 2026-07-13 00:00:00+00:00 .. 2026-08-09 00:00:00+00:00
   rows with t outside its day: 0
   min/max p per model: {'B0': (0.08883523094457565, 0.09199870081269815), 'B1': (0.00011872521699609957, 0.9270223787512285), 'B2': (0.04141684616109616, 0.7177863609276335), 'LR': (0.0032680150669662316, 0.885919781961662), 'LGBM': (0.0017281211607456264, 0.8011313205872994)}
  test: rows 46574, pos 5624, base 0.1208, days 24, day range 2026-08-10 00:00:00+00:00 .. 2026-09-06 00:00:00+00:00
   rows with t outside its day: 0
   min/max p per model: {'B0': (0.09211847875224052, 0.09423337989009124), 'B1': (0.0001968250527814151, 0.9242761591191481), 'B2': (0.04311482326417569, 0.20534211464000085), 'LR': (0.0034746642214949094, 0.8761607360402062), 'LGBM': (0.0023310740717710156, 0.7897327676933913)}
   B0 pr_auc=0.1315[0.1135,0.1507] roc_auc=0.5263[0.4846,0.5625] brier=0.1069[0.0969,0.1181] log_loss=0.3726[0.3444,0.4038]
   B1 pr_auc=0.3982[0.3817,0.4179] roc_auc=0.8302[0.8177,0.8443] brier=0.0882[0.0802,0.0977] log_loss=0.2872[0.2623,0.3179]
   B2 pr_auc=0.1302[0.1130,0.1474] roc_auc=0.5263[0.5034,0.5454] brier=0.1067[0.0968,0.1176] log_loss=0.3718[0.3443,0.4023]
   LR pr_auc=0.4242[0.4006,0.4457] roc_auc=0.8587[0.8481,0.8682] brier=0.0842[0.0770,0.0925] log_loss=0.2690[0.2497,0.2914]
   LGBM pr_auc=0.4344[0.4094,0.4576] roc_auc=0.8625[0.8533,0.8716] brier=0.0835[0.0765,0.0917] log_loss=0.2650[0.2466,0.2863]
   diff LR -B1 pr_auc=+0.0260[+0.0105,+0.0403] roc_auc=+0.0285[+0.0178,+0.0377] brier=-0.0040[-0.0057,-0.0025] log_loss=-0.0182[-0.0283,-0.0102]
   diff LGBM -B1 pr_auc=+0.0362[+0.0194,+0.0504] roc_auc=+0.0322[+0.0214,+0.0414] brier=-0.0048[-0.0065,-0.0032] log_loss=-0.0222[-0.0328,-0.0138]
  rows per test day: {'08-10': 2026, '08-11': 2140, '08-12': 2044, '08-13': 2111, '08-14': 2171, '08-15': 2160, '08-16': 1968, '08-17': 2142, '08-18': 2123, '08-19': 2178, '08-20': 1963, '08-21': 2131, '08-22': 1996, '08-23': 2111, '08-24': 2156, '08-25': 2070, '08-26': 2032, '08-27': 1799, '08-28': 1960, '08-29': 334, '09-03': 821, '09-04': 1959, '09-05': 1970, '09-06': 2209}

===== h=3: 104135 rows, cols=['day', 'p_B0', 'p_B1', 'p_B2', 'p_LR', 'p_LGBM', 'part', 'y', 't', 'unit_id', 'oblast']
index unique: True dtypes day/t: datetime64[ms, UTC] datetime64[ms, UTC]
NaN per p col: {'B0': 0, 'B1': 0, 'B2': 0, 'LR': 0, 'LGBM': 0}
  val: rows 57865, pos 15223, base 0.2631, days 28, day range 2026-07-13 00:00:00+00:00 .. 2026-08-09 00:00:00+00:00
   rows with t outside its day: 0
   min/max p per model: {'B0': (0.20870236395087557, 0.213969141884471), 'B1': (0.0002608940864464113, 0.9910742296597265), 'B2': (0.1263669286944138, 0.9178783485
… [обрезано: показано 3000 из 7244 символов]
```

</details>

<details><summary>🔧 Write: reviews/scratch/stage4-6/common.py · 20:23</summary>

**Аргументы**

```
# file: reviews/scratch/stage4-6/common.py
"""Shared helper: model data built in memory, cached outside the repo (session scratchpad)."""
import copy
import os
import time
from pathlib import Path

import pandas as pd

from alerts.config import load_config
from alerts.pipeline import build_all, model_data

CACHE = Path(os.environ.get('S46_CACHE', r'C:\Users\chyck\AppData\Local\Temp\claude\d--Flash-golova-KSE-AI-AAFS'
                                         r'\57049ae5-374c-471e-8191-1ff2343b8a66\scratchpad\s46_model_data.parquet'))


def get_cfg(threads: int = 2) -> dict:
    cfg = copy.deepcopy(load_config())
    cfg['models']['threads'] = threads
    return cfg


def get_data(cfg=None) -> pd.DataFrame:
    if CACHE.exists():
        return pd.read_parquet(CACHE)
    cfg = cfg or load_config()
    t0 = time.time()
    art = build_all(cfg)
    data = model_data(art, cfg)
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    data.to_parquet(CACHE)
    print(f'built model data {data.shape} in {time.time() - t0:.1f} s, cached to {CACHE}')
    return data

```

**Результат**

```
File created successfully at: d:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage4-6\common.py (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Write: reviews/scratch/stage4-6/02_reproduce.py · 20:23</summary>

**Аргументы**

```
# file: reviews/scratch/stage4-6/02_reproduce.py
"""Item 2: refit every model of the h=3 backtest on one or two test days with the run_all settings
(8 threads) and compare with data/predictions_h3.parquet bit for bit. Also caches model data."""
import json
import sys
import time

import numpy as np
import pandas as pd

from alerts.config import load_config
from alerts.models import registry
from alerts.pipeline import build_all, model_data

sys.path.insert(0, 'reviews/scratch/stage4-6')
from common import CACHE  # noqa: E402

cfg = load_config()                       # threads = 8 as in run_all
assert cfg['models']['threads'] == 8
t0 = time.time()
art = build_all(cfg)
data = model_data(art, cfg)
print(f'model data {data.shape} in {time.time() - t0:.1f} s; index unique {data.index.is_unique}')
CACHE.parent.mkdir(parents=True, exist_ok=True)
data.to_parquet(CACHE)

h = 3
tuned = json.loads(open(f'reports/tuning_h{h}.json').read())
models = registry(cfg, cfg['backtest']['baselines'] + cfg['backtest']['models'], tuned)
P = pd.read_parquet(f'data/predictions_h{h}.parquet')
ycol = f'y_{h}'
lab = data[data[ycol].notna()]
for day in [pd.Timestamp('2026-08-20', tz='UTC'), pd.Timestamp('2026-09-04', tz='UTC')]:
    train = lab[lab['t'] <= day - pd.Timedelta(hours=h)]
    test = lab[(lab['t'] >= day) & (lab['t'] < day + pd.Timedelta(days=1))]
    ref = P[(P['part'] == 'test') & (P['day'] == day)]
    print(f'\nday {day.date()}: train {len(train):,}, test {len(test):,}, parquet rows {len(ref):,}, '
          f'same index set {set(ref.index) == set(test.index)}')
    for name, make in models.items():
        t1 = time.time()
        p = make().fit(train, train[ycol].to_numpy(dtype=float)).predict_proba(test)
        q = ref.loc[test.index, f'p_{name}'].to_numpy()
        print(f'  {name}: bit-identical {np.array_equal(p, q)}, max |diff| {np.max(np.abs(p - q)):.3g}, '
              f'{time.time() - t1:.1f} s')

```

**Результат**

```
File created successfully at: d:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage4-6\02_reproduce.py (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Bash: Reproduce one test day predictions bit for bit · 20:23</summary>

**Аргументы**

```bash
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage4-6/02_reproduce.py 2>&1 | grep -v Warning | tee reviews/scratch/stage4-6/02_out.txt
```

**Результат**

```
Channel outage (D15): 2026-08-29 05:55:28+00:00 -> 2026-09-02 13:48:04+00:00 (4 days 07:52:36)
model data (615151, 27) in 19.1 s; index unique True

day 2026-08-20: train 589,462, test 1,963, parquet rows 1,963, same index set True
  B0: bit-identical True, max |diff| 0, 0.0 s
  B1: bit-identical True, max |diff| 0, 0.1 s
  B2: bit-identical True, max |diff| 0, 0.0 s
  LR: bit-identical True, max |diff| 0, 7.7 s
  LGBM: bit-identical True, max |diff| 0, 2.4 s

day 2026-09-04: train 608,634, test 1,959, parquet rows 1,959, same index set True
  B0: bit-identical True, max |diff| 0, 0.0 s
  B1: bit-identical True, max |diff| 0, 0.1 s
  B2: bit-identical True, max |diff| 0, 0.0 s
  LR: bit-identical True, max |diff| 0, 6.1 s
  LGBM: bit-identical True, max |diff| 0, 3.0 s
```

</details>

<details><summary>🔧 Write: reviews/scratch/stage4-6/03_tuning.py · 20:25</summary>

**Аргументы**

```
# file: reviews/scratch/stage4-6/03_tuning.py
"""Item 3: is the hyperparameter choice above noise? (validation only, never the test part)

For every h: refit all candidates as tuning.tune does (train t <= train_end - h, threads 2), keep the
validation predictions, then
 - paired day bootstrap of log loss differences between the winner and every other candidate;
 - share of bootstrap draws in which each candidate wins;
 - LightGBM winner: validation log loss as a function of the number of trees (flatness around the
   early-stopping value), and the early-stopping value when the training end moves 14 days later
   (train up to train_end + 14 d - h, early stopping on the last 14 validation days).
"""
import itertools
import sys
import warnings

import numpy as np
import pandas as pd

sys.path.insert(0, 'reviews/scratch/stage4-6')
from common import get_cfg, get_data  # noqa: E402

from alerts.config import ts  # noqa: E402
from alerts.metrics import score  # noqa: E402
from alerts.models.learned import GBMModel, LogisticModel  # noqa: E402

warnings.filterwarnings('ignore')
cfg = get_cfg(threads=2)
data = get_data(cfg)
m = cfg['models']
rng_seed = 20261012


def ll(y, p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return -(y * np.log(p) + (1 - y) * np.log(1 - p))


for h in [1, 3, 6]:
    ycol = f'y_{h}'
    lab = data[data[ycol].notna()]
    train = lab[lab['t'] <= ts(cfg['periods']['train_end']) - pd.Timedelta(hours=h)]
    val = lab[lab['part'] == 'val']
    y, yv = train[ycol].to_numpy(float), val[ycol].to_numpy(float)
    preds, rows = {}, []
    for C, hl in itertools.product(m['lr']['grid']['C'], m['lr']['grid']['half_life_days']):
        key = f'LR C={C} hl={hl}'
        preds[key] = LogisticModel(cfg, {'C': C, 'half_life_days': hl}).fit(train, y).predict_proba(val)
    g = m['lgbm']['grid']
    best_gbm = {}
    for nl, mcs, hl in itertools.product(g['num_leaves'], g['min_child_samples'], g['half_life_days']):
        params = {'num_leaves': nl, 'min_child_sample
… [обрезано: показано 2000 из 5028 символов]
```

**Результат**

```
File created successfully at: d:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage4-6\03_tuning.py (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Bash: Run tuning noise analysis on validation · 20:25</summary>

**Аргументы**

```bash
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage4-6/03_tuning.py > reviews/scratch/stage4-6/03_out.txt 2>&1
```

**Результат**

```
Command running in background with ID: bcfz042gs. Output is being written to: C:\Users\chyck\AppData\Local\Temp\claude\d--Flash-golova-KSE-AI-AAFS\57049ae5-374c-471e-8191-1ff2343b8a66\tasks\bcfz042gs.output. You will be notified when it completes. To check interim output, use Read on that file path.
```

</details>

<details><summary>🔧 Write: reviews/scratch/stage4-6/04_b1_variants.py · 20:25</summary>

**Аргументы**

```
# file: reviews/scratch/stage4-6/04_b1_variants.py
"""Item 6: is B1 an honest "best baseline"? Short-memory variants of B1 on the VALIDATION part only.

Variants (fixed before looking at any result, not tuned):
  B1_28   - the project's B1 re-implemented (sanity check against the parquet),
  B1_7    - same hierarchy, window 7 days,
  B1_14   - window 14 days,
  B1_exp7 - all training rows, exponential weight with half-life 7 days (weighted counts, same prior 5),
  U_7     - unit rate over 7 days only (no hour of day), smoothed to the global rate.
Walk-forward exactly as backtest.walk_forward (train t <= D - h), compared with LightGBM / LR / B1
validation predictions from data/predictions_h{h}.parquet with the paired day bootstrap of metrics.py.
"""
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, 'reviews/scratch/stage4-6')
from common import get_cfg, get_data  # noqa: E402

from alerts import backtest  # noqa: E402
from alerts.metrics import bootstrap  # noqa: E402

cfg = get_cfg(threads=2)
data = get_data(cfg)
PRIOR = cfg['baselines']['prior_strength']


class B1Var:
    def __init__(self, window_days=None, half_life_days=None, hour=True):
        self.w, self.hl, self.hour = window_days, half_life_days, hour

    def fit(self, X, y):
        t = X['t']
        tmax = t.max()
        if self.w is not None:
            keep = (t > tmax - pd.Timedelta(days=self.w)).to_numpy()
            wt = np.ones(keep.sum())
        else:
            keep = np.ones(len(X), bool)
            age = (tmax - t).dt.total_seconds().to_numpy() / 86400
            wt = 0.5 ** (age / self.hl)
        d = pd.DataFrame({'u': X['unit_id'].to_numpy()[keep], 'hr': X['hour_kyiv'].to_numpy().astype(int)[keep],
                          'wy': wt * y[keep], 'w': wt})
        self.g = d['wy'].sum() / d['w'].sum()
        u = d.groupby('u')[['wy', 'w']].sum()
        self.u = (u['wy'] + PRIOR * self.g) / (u['w'] + PRIOR)
        c = d.groupby(['u', 'hr'])[['wy', 'w']].sum()
  
… [обрезано: показано 2000 из 3911 символов]
```

**Результат**

```
File created successfully at: d:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage4-6\04_b1_variants.py (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Bash: Run B1 short-memory variants on validation · 20:25</summary>

**Аргументы**

```bash
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage4-6/04_b1_variants.py > reviews/scratch/stage4-6/04_out.txt 2>&1; tail -40 reviews/scratch/stage4-6/04_out.txt
```

**Результат**

```
===== h=1, validation (57,865 rows, 28 days); re-implemented B1 vs parquet max|diff| 0.00e+00
  model      PR-AUC   ROC-AUC  logloss   | diff vs LGBM: PR-AUC [95%]        log loss [95%]
  B1        0.4124   0.8364   0.2868   | -0.0138 [-0.0282, -0.0000]   +0.0113 [+0.0052, +0.0178]
  LR        0.4054   0.8443   0.2792   | -0.0208 [-0.0318, -0.0110]   +0.0036 [+0.0005, +0.0067]
  LGBM      0.4262   0.8475   0.2755   | +0.0000 [+0.0000, +0.0000]   +0.0000 [+0.0000, +0.0000]
  B1_7      0.3867   0.8321   0.2897   | -0.0395 [-0.0552, -0.0240]   +0.0141 [+0.0088, +0.0197]
  B1_14     0.3999   0.8354   0.2883   | -0.0264 [-0.0400, -0.0121]   +0.0127 [+0.0072, +0.0187]
  B1_exp7   0.4129   0.8395   0.2810   | -0.0133 [-0.0255, -0.0005]   +0.0055 [+0.0015, +0.0100]
  U_7       0.4011   0.8411   0.2796   | -0.0251 [-0.0405, -0.0095]   +0.0041 [-0.0010, +0.0089]

===== h=3, validation (57,865 rows, 28 days); re-implemented B1 vs parquet max|diff| 0.00e+00
  model      PR-AUC   ROC-AUC  logloss   | diff vs LGBM: PR-AUC [95%]        log loss [95%]
  B1        0.6900   0.8686   0.3948   | -0.0044 [-0.0128, +0.0045]   +0.0133 [+0.0015, +0.0261]
  LR        0.6826   0.8721   0.3862   | -0.0118 [-0.0258, -0.0007]   +0.0047 [-0.0059, +0.0144]
  LGBM      0.6945   0.8720   0.3815   | +0.0000 [+0.0000, +0.0000]   +0.0000 [+0.0000, +0.0000]
  B1_7      0.6803   0.8686   0.3921   | -0.0142 [-0.0254, -0.0028]   +0.0106 [+0.0004, +0.0210]
  B1_14     0.6844   0.8704   0.3923   | -0.0101 [-0.0187, -0.0011]   +0.0108 [-0.0004, +0.0227]
  B1_exp7   0.6969   0.8727   0.3810   | +0.0024 [-0.0048, +0.0106]   -0.0005 [-0.0072, +0.0061]
  U_7       0.6841   0.8709   0.3825   | -0.0104 [-0.0205, +0.0009]   +0.0010 [-0.0085, +0.0095]

===== h=6, validation (57,865 rows, 28 days); re-implemented B1 vs parquet max|diff| 0.00e+00
  model      PR-AUC   ROC-AUC  logloss   | diff vs LGBM: PR-AUC [95%]        log loss [95%]
  B1        0.8322   0.8961   0.4055   | -0.0066 [-0.0131, +0.0007]   +0.0166 [-0.0015, +0.0378]
  LR        0.8344   0.9025   0.3878   | -0.0044 [-0.0129, +0.0024]   -0.0011 [-0.0190, +0.0123]
  LGBM      0.8388   0.8989   0.3889   | +0.0000 [+0.0000, +0.0000]   +0.0000 [+0.0000, +0.0000]
  B1_7      0.8294   0.9002   0.3931   | -0.0095 [-0.0180, -0.0007]   +0.0042 [-0.0069, +0.0152]
  B1_14     0.8308   0.8998   0.4006   | -0.0080 [-0.0143, -0.0017]   +0.0117 [-0.0028, +0.0295]
  B1_exp7   0.8402   0.9015   0.3835   | +0.0013 [-0.0037, +0.0068]   -0.0054 [-0.0128, +0.0022]
  U_7       0.8350   0.9020   0.3824   | -0.0038 [-0.0107, +0.0035]   -0.0066 [-0.0157, +0.0018]
```

</details>

<details><summary>🔧 Write: reviews/scratch/stage4-6/05_stats.py · 20:31</summary>

**Аргументы**

```
# file: reviews/scratch/stage4-6/05_stats.py
"""Items 4-5 on the saved test predictions (read-only, no refitting):
 a) moving-block bootstrap over test days (blocks 1, 3, 7) for LGBM-B1 and LR-B1 at h = 1, 6 (and 3 for reference);
 b) multiplicity: Bonferroni-adjusted paired intervals (6 PR-AUC comparisons; 24 = x4 metrics);
 c) per-oblast: share of bootstrap draws without positives (dropped by metrics._quantile) and the
    paired differences LR-B1 / LGBM-B1 behind the README examples (Kyiv City, Kyivska).
"""
import numpy as np
import pandas as pd

from alerts.metrics import score

SEED = 20261012


def block_draws(n_days, block, n_reps, rng):
    """Moving-block bootstrap (non-circular) over the ordered forecast days."""
    starts = np.arange(n_days - block + 1)
    k = int(np.ceil(n_days / block))
    out = np.empty((n_reps, k * block), int)
    for r in range(n_reps):
        s = rng.choice(starts, k)
        out[r] = (s[:, None] + np.arange(block)).ravel()
    return out[:, :n_days]


def paired(test, models, ref, draws, metrics=('pr_auc', 'log_loss')):
    day = test['day'].to_numpy()
    uniq = np.unique(day)                            # chronological
    by_day = [np.flatnonzero(day == d) for d in uniq]
    y = test['y'].to_numpy(float)
    P = {m: test[f'p_{m}'].to_numpy() for m in models + [ref]}
    res = {m: {k: [] for k in metrics} for m in models}
    for dr in draws:
        idx = np.concatenate([by_day[i] for i in dr])
        sr = score(y[idx], P[ref][idx])
        for m in models:
            s = score(y[idx], P[m][idx])
            for k in metrics:
                res[m][k].append(s[k] - sr[k])
    return {m: {k: np.array(v) for k, v in d.items()} for m, d in res.items()}


rng = np.random.default_rng(SEED)
print('a) block bootstrap of test days, paired differences vs B1 (1000 draws)')
for h in [1, 3, 6]:
    P = pd.read_parquet(f'data/predictions_h{h}.parquet')
    test = P[P['part'] == 'test']
    nd = test['day'].nunique()
    for block in [
… [обрезано: показано 2000 из 4899 символов]
```

**Результат**

```
File created successfully at: d:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage4-6\05_stats.py (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Bash: Fix per-oblast section and start stats script · 20:31</summary>

**Аргументы**

```bash
python - <<'EOF'
import re
p='reviews/scratch/stage4-6/05_stats.py'
s=open(p,encoding='utf-8').read()
start=s.index("print('\\nc) per oblast")
s=s[:start]+'''print('\\nc) per oblast, h=3 test: share of bootstrap draws without positives (200 draws, seed as the report); paired PR-AUC diffs vs B1')
P = pd.read_parquet('data/predictions_h3.parquet')
test = P[P['part'] == 'test']
for ob, g in test.groupby('oblast'):
    y = g['y'].to_numpy(float)
    if y.sum() == 0:
        continue
    day = g['day'].to_numpy()
    uniq = np.unique(day)
    by_day = [np.flatnonzero(day == d) for d in uniq]
    pos_days = int((g.groupby('day')['y'].sum() > 0).sum())
    rr = np.random.default_rng(SEED)
    nan, diffs = 0, {m: [] for m in ['LR', 'LGBM']}
    for _ in range(200):
        idx = np.concatenate([by_day[i] for i in rr.integers(0, len(uniq), len(uniq))])
        if y[idx].sum() == 0:
            nan += 1
            continue
        s = {m: score(y[idx], g[f'p_{m}'].to_numpy()[idx])['pr_auc'] for m in ['B1', 'LR', 'LGBM']}
        for m in ['LR', 'LGBM']:
            diffs[m].append(s[m] - s['B1'])
    pt = {m: score(y, g[f'p_{m}'].to_numpy())['pr_auc'] for m in ['B1', 'LR', 'LGBM']}
    print(f'  {ob:24s} rows {len(g):5d} pos {int(y.sum()):5d} days with pos {pos_days:2d}/{len(uniq)} draws w/o pos {nan/200:.3f}; '
          + '; '.join(f'{m}-B1 {pt[m]-pt["B1"]:+.3f} [{np.quantile(diffs[m], .025):+.3f}, {np.quantile(diffs[m], .975):+.3f}]'
                      for m in ['LR', 'LGBM']))
'''
open(p,'w',encoding='utf-8').write(s)
EOF
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage4-6/05_stats.py > reviews/scratch/stage4-6/05_out.txt 2>&1 &
echo started
```

**Результат**

```
Traceback (most recent call last):
  File "<stdin>", line 4, in <module>
ValueError: substring not found
started
```

</details>

<details><summary>🔧 Bash: Stop stats script and inspect search string · 20:31</summary>

**Аргументы**

```bash
pkill -f 05_stats.py; sleep 1; grep -n "per oblast" reviews/scratch/stage4-6/05_stats.py | cat -A | head
```

**Результат**

```
/c/Users/chyck/.claude/shell-snapshots/snapshot-bash-1791739175993-k2ilth.sh: line 42: pkill: command not found
71:print('\nc) per oblast, h=3 test: share of draws without positives; paired diffs (200 draws like the report, and 2000)')$
```

</details>

<details><summary>🔧 PowerShell: Stop only my stats script process · 20:31</summary>

**Аргументы**

```powershell
Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -like '*stage4-6/05_stats.py*' } | ForEach-Object { $_.ProcessId; $_.CommandLine; Stop-Process -Id $_.ProcessId -Force -Confirm:$false }
```

**Результат**

```
28936
D:\Soft\miniconda\python.exe reviews/scratch/stage4-6/05_stats.py
```

</details>

<a id="m-1e0fe7f0"></a>

**🤖 Ассистент** · 2026-10-11 20:31

Now I'll rewrite the per-oblast section with the Edit tool.

<details><summary>🔧 Read: reviews/scratch/stage4-6/05_stats.py · 20:31</summary>

**Аргументы**

```json
{
 "file_path": "d:\\Flash\\golova\\KSE_AI\\AAFS\\reviews\\scratch\\stage4-6\\05_stats.py",
 "offset": 68
}
```

**Результат**

```
68	            line.append(f'{k} 95%{q(0.05)} 6x{q(0.05/6)} 24x{q(0.05/24)}')
69	        print(f'  h={h} {m}-B1: ' + ' | '.join(line))
70	
71	print('\nc) per oblast, h=3 test: share of draws without positives; paired diffs (200 draws like the report, and 2000)')
72	P = pd.read_parquet('data/predictions_h3.parquet')
73	test = P[P['part'] == 'test']
74	for ob, g in test.groupby('oblast'):
75	    if g['y'].sum() == 0:
76	        continue
77	    day = g['day'].to_numpy()
78	    uniq = np.unique(day)
79	    pos_days = g.groupby('day')['y'].sum()
80	    for n_reps in [200, 2000]:
81	        rr = np.random.default_rng(SEED)
82	        draws = [rr.integers(0, len(uniq), len(uniq)) for _ in range(n_reps)]
83	        by_day = [np.flatnonzero(day == d) for d in uniq]
84	        y = g['y'].to_numpy(float)
85	        nan = 0
86	        diffs = {m: [] for m in ['LR', 'LGBM']}
87	        vals = {m: [] for m in ['B1', 'LR', 'LGBM']}
88	        for dr in draws:
89	            idx = np.concatenate([by_day[i] for i in dr])
90	            if y[idx].sum() == 0:
91	                nan += 1
92	                continue
93	            s = {m: score(y[idx], g[f'p_{m}'].to_numpy()[idx])['pr_auc'] for m in ['B1', 'LR', 'LGBM']}
94	            for m in ['B1', 'LR', 'LGBM']:
95	                vals[m].append(s[m])
96	            for m in ['LR', 'LGBM']:
97	                diffs[m].append(s[m] - s['B1'])
98	        if n_reps == 200 and nan == 0 and ob not in ('Kyiv City', 'Kyivska oblast', 'Kirovohradska oblast', 'Poltavska oblast'):
99	            break
100	        pt = {m: score(y, g[f'p_{m}'].to_numpy())['pr_auc'] for m in ['B1', 'LR', 'LGBM']}
101	        print(f'  {ob:24s} n_reps={n_reps}: rows {len(g)}, pos {int(y.sum())}, days with pos {int((pos_days > 0).sum())}/{len(uniq)}, '
102	              f'draws w/o pos {nan / n_reps:.3f}; '
103	              + '; '.join(f'{m}-B1 {pt[m]-pt["B1"]:+.3f} [{np.quantile(diffs[m], .025):+.3f}, {np.quantile(diffs[m], .975):+.3f}]'
104	                          for m in ['LR', 'LGBM']))
105
```

</details>

<details><summary>🔧 Bash: Rewrite per-oblast section and check tuning output · 20:31</summary>

**Аргументы**

```bash
head -n 70 reviews/scratch/stage4-6/05_stats.py > reviews/scratch/stage4-6/05_tmp.py && cat >> reviews/scratch/stage4-6/05_tmp.py <<'EOF'
print('\nc) per oblast, h=3 test: share of bootstrap draws without positives (200 draws); paired PR-AUC diffs vs B1')
P = pd.read_parquet('data/predictions_h3.parquet')
test = P[P['part'] == 'test']
for ob, g in test.groupby('oblast'):
    y = g['y'].to_numpy(float)
    if y.sum() == 0:
        continue
    day = g['day'].to_numpy()
    uniq = np.unique(day)
    by_day = [np.flatnonzero(day == d) for d in uniq]
    pos_days = int((g.groupby('day')['y'].sum() > 0).sum())
    rr = np.random.default_rng(SEED)
    nan, diffs = 0, {m: [] for m in ['LR', 'LGBM']}
    for _ in range(200):
        idx = np.concatenate([by_day[i] for i in rr.integers(0, len(uniq), len(uniq))])
        if y[idx].sum() == 0:
            nan += 1
            continue
        s = {m: score(y[idx], g[f'p_{m}'].to_numpy()[idx])['pr_auc'] for m in ['B1', 'LR', 'LGBM']}
        for m in ['LR', 'LGBM']:
            diffs[m].append(s[m] - s['B1'])
    pt = {m: score(y, g[f'p_{m}'].to_numpy())['pr_auc'] for m in ['B1', 'LR', 'LGBM']}
    print(f'  {ob:24s} rows {len(g):5d} pos {int(y.sum()):5d} days with pos {pos_days:2d}/{len(uniq)} draws w/o pos {nan/200:.3f}; '
          + '; '.join(f'{m}-B1 {pt[m]-pt["B1"]:+.3f} [{np.quantile(diffs[m], .025):+.3f}, {np.quantile(diffs[m], .975):+.3f}]'
                      for m in ['LR', 'LGBM']))
EOF
mv reviews/scratch/stage4-6/05_tmp.py reviews/scratch/stage4-6/05_stats.py && tail -5 reviews/scratch/stage4-6/05_stats.py && cat reviews/scratch/stage4-6/03_out.txt
```

**Результат**

```
diffs[m].append(s[m] - s['B1'])
    pt = {m: score(y, g[f'p_{m}'].to_numpy())['pr_auc'] for m in ['B1', 'LR', 'LGBM']}
    print(f'  {ob:24s} rows {len(g):5d} pos {int(y.sum()):5d} days with pos {pos_days:2d}/{len(uniq)} draws w/o pos {nan/200:.3f}; '
          + '; '.join(f'{m}-B1 {pt[m]-pt["B1"]:+.3f} [{np.quantile(diffs[m], .025):+.3f}, {np.quantile(diffs[m], .975):+.3f}]'
                      for m in ['LR', 'LGBM']))
```

</details>

<details><summary>🔧 Bash: Run block bootstrap and multiplicity statistics · 20:31</summary>

**Аргументы**

```bash
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage4-6/05_stats.py > reviews/scratch/stage4-6/05_out.txt 2>&1
```

**Результат**

```
Command running in background with ID: bvx01inhr. Output is being written to: C:\Users\chyck\AppData\Local\Temp\claude\d--Flash-golova-KSE-AI-AAFS\57049ae5-374c-471e-8191-1ff2343b8a66\tasks\bvx01inhr.output. You will be notified when it completes. To check interim output, use Read on that file path.
```

</details>

<details><summary>🔧 Bash: Create B1 exponential half-life robustness script · 20:32</summary>

**Аргументы**

```bash
sed -e "s/^VARS = .*/VARS = {'B1_28': dict(window_days=28), 'B1_exp3': dict(half_life_days=3), 'B1_exp7': dict(half_life_days=7),/" -e "s/^        'B1_exp7': dict(half_life_days=7), 'U_7': dict(window_days=7, hour=False)}/        'B1_exp14': dict(half_life_days=14), 'B1_exp28': dict(half_life_days=28)}/" reviews/scratch/stage4-6/04_b1_variants.py > reviews/scratch/stage4-6/06_b1_exp_robust.py && sed -i "s/'B1', 'LR', 'LGBM'\] + \[n for n in VARS if n != 'B1_28'\]/'B1', 'LR', 'LGBM'] + [n for n in VARS if n != 'B1_28']/" reviews/scratch/stage4-6/06_b1_exp_robust.py && sed -i '1s/.*/"""Robustness of finding S46 (B1 with exponential weights): half-lives 3, 7, 14, 28 days, validation only./' reviews/scratch/stage4-6/06_b1_exp_robust.py && grep -n "VARS\|exp" reviews/scratch/stage4-6/06_b1_exp_robust.py | head
```

**Результат**

```
1:"""Robustness of finding S46 (B1 with exponential weights): half-lives 3, 7, 14, 28 days, validation only.
7:  B1_exp7 - all training rows, exponential weight with half-life 7 days (weighted counts, same prior 5),
62:VARS = {'B1_28': dict(window_days=28), 'B1_exp3': dict(half_life_days=3), 'B1_exp7': dict(half_life_days=7),
63:        'B1_exp14': dict(half_life_days=14), 'B1_exp28': dict(half_life_days=28)}
68:    for name, kw in VARS.items():
71:    assert V[[f'p_{n}' for n in VARS]].notna().all().all()
73:    models = ['B1', 'LR', 'LGBM'] + [n for n in VARS if n != 'B1_28']
```

</details>

<details><summary>🔧 Bash: Run half-life robustness check and view tuning output · 20:33</summary>

**Аргументы**

```bash
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage4-6/06_b1_exp_robust.py > reviews/scratch/stage4-6/06_out.txt 2>&1; cat reviews/scratch/stage4-6/06_out.txt; echo ----; cat reviews/scratch/stage4-6/03_out.txt
```

**Результат**

```
===== h=1, validation (57,865 rows, 28 days); re-implemented B1 vs parquet max|diff| 0.00e+00
  model      PR-AUC   ROC-AUC  logloss   | diff vs LGBM: PR-AUC [95%]        log loss [95%]
  B1        0.4124   0.8364   0.2868   | -0.0138 [-0.0282, -0.0000]   +0.0113 [+0.0052, +0.0178]
  LR        0.4054   0.8443   0.2792   | -0.0208 [-0.0318, -0.0110]   +0.0036 [+0.0005, +0.0067]
  LGBM      0.4262   0.8475   0.2755   | +0.0000 [+0.0000, +0.0000]   +0.0000 [+0.0000, +0.0000]
  B1_exp3   0.4020   0.8389   0.2813   | -0.0242 [-0.0368, -0.0112]   +0.0057 [+0.0019, +0.0098]
  B1_exp7   0.4129   0.8395   0.2810   | -0.0133 [-0.0255, -0.0005]   +0.0055 [+0.0015, +0.0100]
  B1_exp14  0.4183   0.8397   0.2817   | -0.0079 [-0.0203, +0.0052]   +0.0062 [+0.0018, +0.0107]
  B1_exp28  0.4205   0.8411   0.2831   | -0.0057 [-0.0190, +0.0070]   +0.0076 [+0.0036, +0.0119]

===== h=3, validation (57,865 rows, 28 days); re-implemented B1 vs parquet max|diff| 0.00e+00
  model      PR-AUC   ROC-AUC  logloss   | diff vs LGBM: PR-AUC [95%]        log loss [95%]
  B1        0.6900   0.8686   0.3948   | -0.0044 [-0.0128, +0.0045]   +0.0133 [+0.0015, +0.0261]
  LR        0.6826   0.8721   0.3862   | -0.0118 [-0.0258, -0.0007]   +0.0047 [-0.0059, +0.0144]
  LGBM      0.6945   0.8720   0.3815   | +0.0000 [+0.0000, +0.0000]   +0.0000 [+0.0000, +0.0000]
  B1_exp3   0.6915   0.8731   0.3805   | -0.0029 [-0.0114, +0.0062]   -0.0010 [-0.0083, +0.0063]
  B1_exp7   0.6969   0.8727   0.3810   | +0.0024 [-0.0048, +0.0106]   -0.0005 [-0.0072, +0.0061]
  B1_exp14  0.6979   0.8727   0.3823   | +0.0034 [-0.0040, +0.0118]   +0.0008 [-0.0053, +0.0072]
  B1_exp28  0.6976   0.8730   0.3868   | +0.0032 [-0.0042, +0.0114]   +0.0053 [-0.0024, +0.0134]

===== h=6, validation (57,865 rows, 28 days); re-implemented B1 vs parquet max|diff| 0.00e+00
  model      PR-AUC   ROC-AUC  logloss   | diff vs LGBM: PR-AUC [95%]        log loss [95%]
  B1        0.8322   0.8961   0.4055   | -0.0066 [-0.0131, +0.0007]   +0.0166 [-0.0015, +0.0378]
  LR        0.8344   0.9025   0.3878   | -0.0044 [-0.0129, +0.0024]   -0.0011 [-0.0190, +0.0123]
  LGBM      0.8388   0.8989   0.3889   | +0.0000 [+0.0000, +0.0000]   +0.0000 [+0.0000, +0.0000]
  B1_exp3   0.8365   0.9027   0.3816   | -0.0023 [-0.0093, +0.0049]   -0.0073 [-0.0155, +0.0004]
  B1_exp7   0.8402   0.9015   0.3835   | +0.0013 [-0.0037, +0.0068]   -0.0054 [-0.0128, +0.0022]
  B1_exp14  0.8404   0.9012   0.3865   | +0.0016 [-0.0038, +0.0073]   -0.0024 [-0.0146, +0.0078]
  B1_exp28  0.8409   0.9019   0.3942   | +0.0021 [-0.0041, +0.0082]   +0.0053 [-0.0118, +0.0203]
----

===== h=1: train 510,642, val 57,865 rows, 28 days
 LR: winner LR C=1.0 hl=28 (val log loss 0.2812)
   LR C=1.0 hl=28                         ll=0.2812  diff vs winner +0.0000 [+0.0000, +0.0000]  P(win)=0.67  pr_auc=0.4025
   LR C=0.1 hl=None                       ll=0.2815  diff vs winner +0.0003 [-0.0008, +0.0014]  P(win)=0.23  pr_auc=0.3971
   LR C=1.0 hl=No
… [обрезано: показано 3000 из 9448 символов]
```

</details>

<details><summary>🔔 Уведомление: Background command "Run tuning noise analysis on validation" completed (exit code 0) · 20:34</summary>

```
<task-notification>
<task-id>bcfz042gs</task-id>
<tool-use-id>toolu_01ETwbDX2wetynZnYskKVEdn</tool-use-id>
<output-file>C:\Users\chyck\AppData\Local\Temp\claude\d--Flash-golova-KSE-AI-AAFS\57049ae5-374c-471e-8191-1ff2343b8a66\tasks\bcfz042gs.output</output-file>
<status>completed</status>
<summary>Background command "Run tuning noise analysis on validation" completed (exit code 0)</summary>
</task-notification>
```

</details>

*[ошибка API · 20:39: You&#x27;ve hit your weekly limit · resets 2am (Europe/Kyiv)]*

<details><summary>🔧 Bash: List my scratch outputs and view stats output · 08:41</summary>

**Аргументы**

```bash
ls reviews/scratch/stage4-6/ && cat reviews/scratch/stage4-6/05_out.txt
```

**Результат**

```
01_out.txt
01_recompute.py
02_out.txt
02_reproduce.py
03_out.txt
03_tuning.py
04_b1_variants.py
04_out.txt
05_out.txt
05_stats.py
06_b1_exp_robust.py
06_out.txt
__pycache__
common.py
a) block bootstrap of test days, paired differences vs B1 (1000 draws)
  h=1 block=1: LGBM-B1 pr_auc [+0.0194, +0.0504]; LGBM-B1 log_loss [-0.0328, -0.0138]; LR-B1 pr_auc [+0.0105, +0.0403]; LR-B1 log_loss [-0.0283, -0.0102]
  h=1 block=3: LGBM-B1 pr_auc [+0.0144, +0.0465]; LGBM-B1 log_loss [-0.0379, -0.0123]; LR-B1 pr_auc [+0.0051, +0.0362]; LR-B1 log_loss [-0.0335, -0.0086]
  h=1 block=7: LGBM-B1 pr_auc [+0.0097, +0.0427]; LGBM-B1 log_loss [-0.0398, -0.0119]; LR-B1 pr_auc [+0.0001, +0.0327]; LR-B1 log_loss [-0.0353, -0.0076]
  h=3 block=1: LGBM-B1 pr_auc [+0.0113, +0.0441]; LGBM-B1 log_loss [-0.0348, -0.0098]; LR-B1 pr_auc [-0.0030, +0.0374]; LR-B1 log_loss [-0.0294, -0.0008]
  h=3 block=3: LGBM-B1 pr_auc [+0.0076, +0.0428]; LGBM-B1 log_loss [-0.0388, -0.0097]; LR-B1 pr_auc [-0.0069, +0.0365]; LR-B1 log_loss [-0.0324, -0.0004]
  h=3 block=7: LGBM-B1 pr_auc [+0.0023, +0.0399]; LGBM-B1 log_loss [-0.0400, -0.0108]; LR-B1 pr_auc [-0.0180, +0.0325]; LR-B1 log_loss [-0.0337, -0.0017]
  h=6 block=1: LGBM-B1 pr_auc [+0.0048, +0.0309]; LGBM-B1 log_loss [-0.0339, -0.0052]; LR-B1 pr_auc [-0.0056, +0.0303]; LR-B1 log_loss [-0.0303, +0.0094]
  h=6 block=3: LGBM-B1 pr_auc [+0.0022, +0.0329]; LGBM-B1 log_loss [-0.0350, -0.0065]; LR-B1 pr_auc [-0.0156, +0.0327]; LR-B1 log_loss [-0.0294, +0.0101]
  h=6 block=7: LGBM-B1 pr_auc [-0.0034, +0.0237]; LGBM-B1 log_loss [-0.0295, -0.0091]; LR-B1 pr_auc [-0.0270, +0.0238]; LR-B1 log_loss [-0.0262, +0.0088]

b) multiplicity: iid-day bootstrap, 5000 draws, percentile intervals at 95%, 99.17% (6 tests), 99.79% (24 tests)
  h=1 LGBM-B1: pr_auc 95%[+0.0204, +0.0525] 6x[+0.0168, +0.0589] 24x[+0.0149, +0.0642] | roc_auc 95%[+0.0224, +0.0421] 6x[+0.0197, +0.0457] 24x[+0.0182, +0.0469] | brier 95%[-0.0067, -0.0033] 6x[-0.0074, -0.0030] 24x[-0.0081, -0.0028] | log_loss 95%[-0.0331, -0.0139] 6x[-0.0372, -0.0118] 24x[-0.0392, -0.0110]
  h=1 LR-B1: pr_auc 95%[+0.0101, +0.0414] 6x[+0.0054, +0.0479] 24x[+0.0020, +0.0506] | roc_auc 95%[+0.0184, +0.0385] 6x[+0.0156, +0.0419] 24x[+0.0138, +0.0436] | brier 95%[-0.0058, -0.0025] 6x[-0.0065, -0.0022] 24x[-0.0070, -0.0020] | log_loss 95%[-0.0287, -0.0101] 6x[-0.0326, -0.0081] 24x[-0.0353, -0.0069]
  h=3 LGBM-B1: pr_auc 95%[+0.0106, +0.0429] 6x[+0.0059, +0.0482] 24x[+0.0033, +0.0506] | roc_auc 95%[+0.0077, +0.0246] 6x[+0.0051, +0.0272] 24x[+0.0033, +0.0295] | brier 95%[-0.0116, -0.0033] 6x[-0.0133, -0.0022] 24x[-0.0143, -0.0012] | log_loss 95%[-0.0343, -0.0098] 6x[-0.0393, -0.0065] 24x[-0.0422, -0.0041]
  h=3 LR-B1: pr_auc 95%[-0.0022, +0.0367] 6x[-0.0092, +0.0442] 24x[-0.0112, +0.0492] | roc_auc 95%[+0.0057, +0.0245] 6x[+0.0033, +0.0278] 24x[+0.0021, +0.0292] | brier 95%[-0.0112, -0.0017] 6x[-0.0130, -0.0005] 24x[-0.0144, +0.0001] | log_loss 95%[-0.0292, -0.0008] 6x[-0.0341, +0.0024] 24x[-0.0377, 
… [обрезано: показано 3000 из 6792 символов]
```

</details>

<details><summary>🔔 Уведомление: Background command "Run block bootstrap and multiplicity statistics" completed (exit code 0) · 20:40</summary>

```
<task-notification>
<task-id>bvx01inhr</task-id>
<tool-use-id>toolu_01U2vNQRoaTkKFA3LdaQaQ4W</tool-use-id>
<output-file>C:\Users\chyck\AppData\Local\Temp\claude\d--Flash-golova-KSE-AI-AAFS\57049ae5-374c-471e-8191-1ff2343b8a66\tasks\bvx01inhr.output</output-file>
<status>completed</status>
<summary>Background command "Run block bootstrap and multiplicity statistics" completed (exit code 0)</summary>
</task-notification>
```

</details>

<details><summary>🔧 Write: reviews/scratch/stage4-6/07_misc.py · 08:42</summary>

**Аргументы**

```
# file: reviews/scratch/stage4-6/07_misc.py
"""Items 7-8 leftovers:
 a) calibration tables on the test part from the parquet (README: "LR and LightGBM close to the diagonal");
 b) which features have NaN in training rows (LR missing-value indicators);
 c) LightGBM: same day refitted with threads=2 vs the parquet (threads=8): does the result depend on threads?
 d) LR: ConvergenceWarning on a full-size fit?
"""
import json
import sys
import warnings

import numpy as np
import pandas as pd

sys.path.insert(0, 'reviews/scratch/stage4-6')
from common import get_cfg, get_data  # noqa: E402

from alerts.metrics import calibration  # noqa: E402
from alerts.models.learned import GBMModel, LogisticModel, LR_FEATURES, GBM_FEATURES  # noqa: E402

print('a) calibration on test (10 equal-count bins): max |p_mean - y_rate|, weighted mean |.|, top-bin p_mean vs y_rate')
for h in [1, 3, 6]:
    P = pd.read_parquet(f'data/predictions_h{h}.parquet')
    T = P[P['part'] == 'test']
    for m in ['B1', 'LR', 'LGBM']:
        c = calibration(T['y'].to_numpy(), T[f'p_{m}'].to_numpy())
        dev = (c['p_mean'] - c['y_rate'])
        print(f'  h={h} {m:4s}: max|dev| {dev.abs().max():.3f}, mean|dev| {np.average(dev.abs(), weights=c["n"]):.3f}, '
              f'mean p {T[f"p_{m}"].mean():.3f} vs rate {T["y"].mean():.3f}; bins p/y: '
              + ' '.join(f'{a:.2f}/{b:.2f}' for a, b in zip(c['p_mean'], c['y_rate'])))

cfg = get_cfg(threads=2)
data = get_data(cfg)
h = 3
lab = data[data['y_3'].notna()]
day = pd.Timestamp('2026-08-20', tz='UTC')
train = lab[lab['t'] <= day - pd.Timedelta(hours=h)]
test = lab[(lab['t'] >= day) & (lab['t'] < day + pd.Timedelta(days=1))]
print('\nb) NaN share in training rows of that day, per feature:',
      {c: round(float(train[c].isna().mean()), 4) for c in LR_FEATURES if train[c].isna().any()})
print('   units with NaN oblast_active_share:', sorted(train.loc[train['oblast_active_share'].isna(), 'unit_id'].unique()))
print('   NaN since_end_log_h: first/las
… [обрезано: показано 2000 из 2905 символов]
```

**Результат**

```
File created successfully at: D:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage4-6\07_misc.py (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Bash: Run calibration, NaN, threads and LR convergence checks · 08:42</summary>

**Аргументы**

```bash
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage4-6/07_misc.py > reviews/scratch/stage4-6/07_out.txt 2>&1; cat reviews/scratch/stage4-6/07_out.txt
```

**Результат**

```
a) calibration on test (10 equal-count bins): max |p_mean - y_rate|, weighted mean |.|, top-bin p_mean vs y_rate
  h=1 B1  : max|dev| 0.064, mean|dev| 0.020, mean p 0.119 vs rate 0.121; bins p/y: 0.00/0.00 0.00/0.00 0.00/0.00 0.01/0.03 0.03/0.04 0.07/0.10 0.13/0.17 0.20/0.21 0.28/0.25 0.47/0.40
  h=1 LR  : max|dev| 0.019, mean|dev| 0.007, mean p 0.119 vs rate 0.121; bins p/y: 0.00/0.00 0.01/0.00 0.01/0.00 0.01/0.01 0.04/0.04 0.08/0.07 0.12/0.14 0.19/0.20 0.27/0.29 0.46/0.45
  h=1 LGBM: max|dev| 0.016, mean|dev| 0.006, mean p 0.118 vs rate 0.121; bins p/y: 0.00/0.00 0.00/0.00 0.01/0.00 0.01/0.01 0.04/0.03 0.08/0.08 0.13/0.14 0.20/0.21 0.28/0.29 0.44/0.45
  h=3 B1  : max|dev| 0.058, mean|dev| 0.020, mean p 0.256 vs rate 0.255; bins p/y: 0.00/0.00 0.00/0.00 0.02/0.03 0.04/0.03 0.10/0.11 0.22/0.28 0.34/0.35 0.45/0.46 0.59/0.55 0.80/0.74
  h=3 LR  : max|dev| 0.031, mean|dev| 0.019, mean p 0.256 vs rate 0.255; bins p/y: 0.02/0.00 0.03/0.00 0.04/0.00 0.05/0.04 0.11/0.11 0.20/0.23 0.31/0.34 0.44/0.46 0.59/0.58 0.79/0.78
  h=3 LGBM: max|dev| 0.026, mean|dev| 0.009, mean p 0.255 vs rate 0.255; bins p/y: 0.01/0.00 0.01/0.00 0.02/0.01 0.04/0.04 0.11/0.11 0.21/0.22 0.33/0.34 0.46/0.49 0.59/0.57 0.77/0.78
  h=6 B1  : max|dev| 0.053, mean|dev| 0.018, mean p 0.368 vs rate 0.360; bins p/y: 0.00/0.00 0.02/0.02 0.04/0.02 0.07/0.06 0.20/0.20 0.39/0.44 0.53/0.54 0.68/0.66 0.81/0.76 0.94/0.90
  h=6 LR  : max|dev| 0.057, mean|dev| 0.026, mean p 0.378 vs rate 0.360; bins p/y: 0.04/0.00 0.05/0.01 0.07/0.01 0.10/0.07 0.20/0.21 0.36/0.38 0.53/0.53 0.69/0.68 0.82/0.80 0.93/0.91
  h=6 LGBM: max|dev| 0.019, mean|dev| 0.011, mean p 0.368 vs rate 0.360; bins p/y: 0.01/0.00 0.02/0.01 0.04/0.02 0.08/0.07 0.22/0.20 0.39/0.37 0.54/0.54 0.68/0.68 0.80/0.79 0.91/0.91

b) NaN share in training rows of that day, per feature: {'oblast_active_share': 0.0136}
   units with NaN oblast_active_share: ['U001', 'U051']
   NaN since_end_log_h: first/last t [NaT, NaT]

c) LGBM threads=2 vs parquet (threads=8), day 2026-08-20: identical True, max|diff| 0
d) LR {'C': 0.1, 'half_life_days': None}: n_iter [64]
d) LR {'C': 1.0, 'half_life_days': None}: n_iter [60]
   warnings: []
```

</details>

<details><summary>🔧 Bash: Run metrics tests and locate doc lines to cite · 08:44</summary>

**Аргументы**

```bash
PYTHONIOENCODING=utf-8 python -m pytest -q tests/test_metrics.py 2>&1 | tail -3; grep -n "0.676\|не прогонялись\|около 10 минут\|все четыре\|наравне\|недооценивает" PLAN.md DECISIONS.md; grep -n "статистично значуща\|Калібрування\|зокрема вагу" README.md
```

**Результат**

```
..                                                                       [100%]
2 passed in 3.37s
PLAN.md:178:**Как сделано:** `backtest.py`, `models/baselines.py`, `metrics.py`, `evaluation.py`, `leakage.py`; решения и цифры — D18; отчёт — `reports/backtest_h3.md`; проверка утечки на реальных данных — `reports/leakage_check.json`, синтетическая — `tests/test_leakage.py`. Лучший бейзлайн — B1 (PR-AUC 0.676 на тесте). B2 хуже B0: число активных областей летом не измеряет волну (D18).
PLAN.md:221:**Как сделано:** `src/alerts/models/learned.py`, `src/alerts/tuning.py`, решения и цифры — D20, отчёт — `reports/backtest_h3.md`. Гиперпараметры выбраны один раз на валидации, включая вес свежих данных (у LightGBM полураспад 28 дней). На тесте LightGBM лучше лучшего бейзлайна B1: PR-AUC 0.701 против 0.674, разность +0.027 [+0.010, +0.041]; log loss −0.021 [−0.033, −0.009]. Проверка утечки пройдена для всех моделей. Горизонты 1 и 6 не прогонялись (сокращаются первыми).
DECISIONS.md:531:- Выбрано: LR — C = 0.1 без веса; LightGBM — 63 листа, `min_child_samples` = 200, полураспад 28 дней, 84 дерева. У LightGBM все четыре лучших варианта — с весом свежести.
DECISIONS.md:548:- Выигрыш моделей виден **внутри областей**, где B1 почти ничего не добавляет к B0. PR-AUC LR против B1: Киев 0.63 против 0.34, Киевская область 0.55 против 0.34, Кировоградская 0.53 против 0.38, Полтавская 0.66 против 0.57. Там, где всё решает идентичность единицы (Сумская, Харьковская), B1 и модели наравне. На западе положительных единицы или десятки, и интервалы слишком широки для выводов.
DECISIONS.md:549:- Калибровка LR и LightGBM на тесте близка к диагонали; B1 недооценивает средние вероятности (`reports/figures/calibration_h3.png`).
DECISIONS.md:555:**Время:** `run_all.py` целиком — около 10 минут, из них ежесуточные обучения LR — около 4 минут.
DECISIONS.md:557:**Горизонты 1 и 6** не прогонялись: по плану они сокращаются первыми. Включаются одной строкой — `config.backtest.horizons`.
23:прифронтових областей, і ця кількість перестає вимірювати «хвилю» (D18). Калібрування LR і LightGBM
26:Моделі кращі за найкращий бейзлайн, і різниця статистично значуща, але скромна. Основний виграш —
69:- **Моделі (D20):** логістична регресія і LightGBM. Гіперпараметри, зокрема вагу свіжих даних,
```

</details>

<details><summary>🔧 Bash: Clean pycache and create report folder · 08:44</summary>

**Аргументы**

```bash
rm -rf reviews/scratch/stage4-6/__pycache__ && mkdir -p reviews/claude && ls reviews/claude
```

**Результат**

```
stage0-1b.md
stage3.md
```

</details>

<details><summary>🔧 Write: reviews/claude/stage4-6.md · 08:45</summary>

**Аргументы**

```
# file: reviews/claude/stage4-6.md
# Ревью этапов 4 и 6: бэктест, бейзлайны, метрики, модели, подбор

Ревьюер: Claude (независимо от других отчётов). Скрипты и их выводы лежат в `reviews/scratch/stage4-6/` (`NN_*.py` → `NN_out.txt`). Запуск из корня: `PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage4-6/NN_*.py`. Тестовый период для подбора чего-либо не использовался: все альтернативы бейзлайнов и гиперпараметров проверены только на валидации.

## 1. Резюме

Механика зоны корректна. Граница `t ≤ D − h` верна. Прогнозы всех пяти моделей воспроизводятся из кода бит в бит (два дня × 5 моделей), а все числа в `results.md`, `backtest_h*.md`, README, D18 и D20 пересчитываются из parquet без расхождений. Метрики и парный бутстреп реализованы верно.

Главная проблема — честность опорного бейзлайна. B1 с жёстким окном 28 дней — слабая версия «частоты единицы × часа». Вариант того же B1 с экспоненциальным весом (полураспад 7 дней) заранее зафиксирован, не подбирался и устойчив к выбору полураспада. На валидации он догоняет LightGBM при h = 3 и 6 и по PR-AUC, и по log loss. Значит, заметная часть выигрыша модели над «лучшим бейзлайном» может объясняться памятью бейзлайна, а не признаками. На тесте это не проверялось: так требует задание ревью.

Второе. Выигрыш при h = 6 хрупкий: блоки по 7 дней и поправка на множественные сравнения опрокидывают интервал PR-AUC. LR значимо лучше B1 только при h = 1, тогда как README пишет «моделі кращі… різниця статистично значуща» во множественном числе.

Подбор гиперпараметров при h = 1 и 3 неотличим от шума, но тесту это не вредит. Остальное — устаревшие места в D20 и PLAN и мелкие неточности формулировок.

## 2. Находки

### S46-1. Бейзлайн B1 с экспоненциальным весом догоняет LightGBM на валидации при h = 3 и 6

- **Серьёзность:** критично для вывода README «моделі кращі за найкращий бейзлайн» (D18, D20, README:26). Проверено только на валидации, для теста это гипотеза.
- **Уверенность:** проверено на данных (валидация).
-
… [обрезано: показано 2000 из 17186 символов]
```

**Результат**

```
File created successfully at: D:\Flash\golova\KSE_AI\AAFS\reviews\claude\stage4-6.md (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Bash: Verify all units present in earliest training set · 08:46</summary>

**Аргументы**

```bash
PYTHONPATH=src PYTHONIOENCODING=utf-8 python -c "
import sys; sys.path.insert(0,'reviews/scratch/stage4-6')
from common import get_data
import pandas as pd
d=get_data()
tr=d[(d['t']<=pd.Timestamp('2026-07-13',tz='UTC')-pd.Timedelta(hours=6))&d['y_6'].notna()]
print('units in earliest training set:', tr['unit_id'].nunique(), 'units overall:', d['unit_id'].nunique())
" ; rm -rf reviews/scratch/stage4-6/__pycache__; git status --short | head
```

**Результат**

```
units in earliest training set: 104 units overall: 104
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

<details><summary>🔧 SubagentHandback: {"message": "Отчёт записан в `D:\\Flash\\golova\\KSE_AI\\AAFS\\reviews\\claude\\stage4-6.md` (по вашему указанию; `revi… · 08:46</summary>

**Аргументы**

```json
{
 "message": "Отчёт записан в `D:\\Flash\\golova\\KSE_AI\\AAFS\\reviews\\claude\\stage4-6.md` (по вашему указанию; `reviews/stage4-6.md` не трогал). Скрипты и их выводы лежат в `reviews/scratch/stage4-6/` (`01`–`07`, `*_out.txt`). Файлы проекта не менял, запрещённые скрипты не запускал. Тест для подбора чего-либо не использовался.\n\n**Резюме**\n- **Механика верна.** Граница `t ≤ D − h` правильна при любом h. У всех моделей одни и те же строки, выравнивание по индексу `row` безопасно, NaN в прогнозах нет. Метрики совпадают со sklearn, бутстреп парный.\n- **Воспроизводимость.** Все 5 моделей переобучены на днях 2026-08-20 и 2026-09-04 (h = 3, 8 потоков) и совпали с `predictions_h3.parquet` бит в бит. LightGBM с 2 потоками дал тот же результат бит в бит.\n- **Числа отчётов.** Все числа в `results.md`, `backtest_h{1,3,6}.md`, README, D18 и D20 пересчитаны из parquet и совпали.\n- **Главная проблема — опорный бейзлайн.** Это B1 с жёстким окном 28 дней, то есть слабая версия бейзлайна. B1 с экспоненциальным весом (полураспад 7 дней, задан заранее, не подбирался) на валидации догоняет LightGBM при h = 3 и 6. Результат устойчив к полураспаду 3–28 дней. Выигрыш модели при h = 3 и 6 может объясняться памятью бейзлайна. На тесте это не проверялось, как требует задание.\n- **h = 6 хрупкий.** Интервал PR-AUC пересекает ноль при блоках по 7 дней и при поправке Бонферрони на 24 сравнения. h = 1 и h = 3 устойчивы.\n- **LR не значимо лучше B1 при h = 3 и 6.** README утверждает значимость для «моделей» во множественном числе.\n- **Подбор гиперпараметров.** При h = 1 и 3 он неотличим от шума (вероятность победы выбранного кандидата 0.35–0.67), но тесту это не вредит. Перенос числа деревьев нормален: кривая плоская, при большей обучающей выборке оптимум не растёт.\n- **Остальное — мелочи:** устаревшие строки D20 и PLAN, утверждение «Сумская и Харьковская — наравне» (на деле B1 значимо лучше), калибровка LR при h = 6, условные интервалы для Запорожской области.\n\n**Критично**\n- **S4
… [обрезано: показано 2000 из 3424 символов]
```

**Результат**

```
{"success":true,"message":"Report delivered to your caller."}
```

</details>
