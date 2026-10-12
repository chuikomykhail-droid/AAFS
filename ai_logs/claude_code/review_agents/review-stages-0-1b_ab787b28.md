# Субагент: Review stages 0-1b

- **Агент:** `ab787b2839342da9d` (general-purpose), запущен из сессии [57049ae5](../2026-10-11_critical-analysis_57049ae5.md#t-bG6vGNikvn2G)
- **Период (UTC):** 2026-10-11 17:19 → 2026-10-12 05:43
- **Период (Киев):** 2026-10-11 20:19 → 2026-10-12 08:43
- **Сообщений:** 1 (задания и сообщения основного агента — 1, ответы субагента — 0); вызовов инструментов — 67
- **Исходный JSONL:** `ai_logs/claude_code/raw/claude_code_raw.zip → subagents/57049ae5_agent-ab787b2839342da9d.jsonl`

> Служебные вставки (`<system-reminder>`, вложения с окружением и контекстом IDE, мета-сообщения — 126 записей) и блоки рассуждений (thinking — 43) сюда не включены: они есть в исходном JSONL. Время — киевское. Вызовы инструментов свёрнуты; аргументы обрезаны до 2000 символов, результаты — до 3000. Токен alerts.in.ua и email автора заменены на `[REDACTED_TOKEN]` / `[REDACTED_EMAIL]`.

---

<a id="m-677ecd30"></a>

### 📨 Задание от основного агента · 2026-10-11 20:19

Рабочая папка проекта: d:\Flash\golova\KSE_AI\AAFS (Windows; доступны Bash (Git Bash) и PowerShell).

Прочитай файл `reviews/prompts/01_stages0-1b.md` целиком и выполни задание из него в точности, включая все ограничения: не изменять файлы проекта, не запускать `scripts/run_all.py`, `scripts/api_check.py`, скрипты скачивания и `save_all`, не трогать git, не открывать токен. Параллельно с тобой в той же папке работают шесть других агентов-ревьюеров — пиши только в `reviews/stage0-1b.md` и `reviews/scratch/stage0-1b/`.

Когда отчёт записан, верни в ответе: резюме отчёта (5–10 строк) и список находок уровня «критично» и «существенно» — по одной строке на находку (id, суть, файл:строка, уровень проверки).

<details><summary>🔧 Read: reviews/prompts/01_stages0-1b.md · 20:19</summary>

**Аргументы**

```json
{
 "file_path": "d:\\Flash\\golova\\KSE_AI\\AAFS\\reviews\\prompts\\01_stages0-1b.md"
}
```

**Результат**

```
1	# Ревью проекта AAFS: этапы 0–1б: снимок, загрузка, охват, клоны, маски
2	
3	Ты — независимый критический ревьюер. Параллельно с тобой другие агенты проверяют другие этапы того же проекта. Твоя зона — этапы 0, 1 и 1б: снимок данных, загрузка и дедупликация, охват, единицы и склейка клонов, маски «статус неизвестен» (правила (а)–(г)), конфиг. На соседние этапы смотри только тогда, когда без этого не понять твой.
4	
5	## Проект
6	
7	- Репозиторий — текущая папка (`AAFS`), ветка `stages-7-8`. Python-проект: прогноз воздушных тревог в Украине по районам. Для каждой единицы (район; Киев — одна единица), где в момент `t` (каждый час) тихо, модель выдаёт вероятность того, что тревога начнётся в `(t, t+h]`, h = 1, 3, 6 (основной — 3).
8	- Данные — снимок датасета Vadimkin (`dataset_repo/`, коммит `58ee75b`). Официальный ряд заканчивается 2026-09-07. Тест — 2026-08-10…2026-09-07, walk-forward с ежесуточным переобучением. Этап 8 — проверка на данных alerts.in.ua за сентябрь–октябрь.
9	- Это тестовое задание с дедлайном 12.10.2026 23:59 по Киеву. Проверяющие оценивают процесс: пойманные ошибки, обоснованность решений, отсутствие утечки из будущего. Найденная проблема ценна, даже если её не успеют исправить: тогда она уйдёт в раздел ограничений.
10	- Документы: `PLAN.md` (правила работы 1–13; у каждого этапа «Исходное задание» и «Как сделано»), `DECISIONS.md` (решения D00–D22, справочные цифры, журнал пойманных ошибок ИИ), `README.md` (на украинском), отчёты в `reports/`.
11	
12	Сначала прочитай раздел «Правила работы» в `PLAN.md`, описание своего этапа в `PLAN.md` и разделы `DECISIONS.md`: D00–D15 и «Справочные цифры». Код и тесты своей зоны читай целиком, а не выборочно.
13	
14	## Твоя зона: файлы
15	
16	- `scripts/fetch_data.py` — только читать; `config.yaml`; `src/alerts/config.py`; `src/alerts/timeutil.py`.
17	- `src/alerts/ingest/vadimkin.py`, `src/alerts/scope.py`, `src/alerts/processor.py` (флаги правил (а) и (б)), `src/alerts/units.py`, `src/alerts/mask.py`.
18	- Функции из `src/alerts/spans.py`, которые используют маски.
19	- `src/alerts/report.py` — сверка справочных цифр.
20	- Тесты: `tests/test_load.py`, `tests/test_units.py`, `tests/test_mask.py`.
21	- Результаты: `data/units.csv`, `data/mask.csv`, `reports/stage1_summary.md`, `reports/high_sim_pairs.csv`.
22	- Код процессора датасета, по которому моделировались правила: `dataset_repo/processors/official_channel_processor.py`.
23	
24	## Что проверить
25	
26	1. **Снимок и загрузка.**
27	   - Что делает `ensure_snapshot`, если в `dataset_repo` есть локальные изменения или выбран другой коммит? Проверяется ли хэш именно того файла, который потом читается?
28	   - `drop_duplicates()` идёт по всем колонкам. Нет ли «почти дубликатов»: разница в долях секунды, пробелах, NaN против пустой строки, в колонке без смысловой нагрузки?
29	   - В каких форматах время в CSV: есть ли смещения, не-UTC, дробные секунды? Что теряется при `as_unit('s')`?
30	2. **Охват.** Ключ локации — `(oblast, raion)`.
31	   - 
… [обрезано: показано 3000 из 9091 символов]
```

</details>

<details><summary>🔧 Bash: List project structure and doc sizes · 20:19</summary>

**Аргументы**

```bash
ls && ls reviews reviews/scratch 2>/dev/null; wc -l PLAN.md DECISIONS.md README.md; ls src/alerts tests scripts data reports
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
  1275 total
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

scripts:
__pycache__
api_check.py
fetch_alerts_in_ua.py
fetch_data.py
run_all.py

src/alerts:
__init__.py
__pycache__
api_check.py
backtest.py
config.py
evaluation.py
features.py
figures.py
geo.py
grid.py
history.py
ingest
intervals.py
leakage.py
mask.py
metrics.py
models
pipeline.py
processor.py
report.py
scope.py
spans.py
store.py
timeutil.py
tuning.py
units.py

tests:
__pycache__
conftest.py
test_features.py
test_grid.py
test_history.py
test_intervals.py
test_knowledge.py
test_leakage.py
test_load.py
test_mask.py
test_metrics.py
test_units.py
```

</details>

<details><summary>🔧 Bash: Show PLAN.md headings · 20:19</summary>

**Аргументы**

```bash
grep -n "^#" PLAN.md | head -80
```

**Результат**

```
1:# План: прогноз воздушных тревог в Украине (MVP)
3:## Контекст задачи
11:## Данные
25:## Ключевые решения
41:## Правила работы (для ассистента в Claude Code / Antigravity)
57:## Этапы
59:### Этап 0. Каркас — выполнено
63:### Этап 1. Разведка структуры данных — выполнено
67:### Этап 1б. Доработка этапа 1 — выполнено
134:### Этап 2. Нормализация в интервалы — выполнено (после ревью и рефакторинга)
156:### Этап 3. Сетка и целевая переменная — выполнено
176:### Этап 4. Бэктест и бейзлайны (до любых моделей) — выполнено
194:### Этап 5. Признаки — выполнено
219:### Этап 6. Модели — выполнено (h = 3)
228:### Этап 7. Отчёт — выполнено
241:### Этап 8. Проверка на свежих данных alerts.in.ua (после этапа 7) — выполнено
287:## Критерий готовности MVP
295:## Расписание (пересмотрено в субботу вечером)
304:## Уроки из предыдущих решений (репозиторий Kizashi, прошлый поток отбора)
311:## Вне MVP (если останется время)
350:## Целевая структура репозитория
```

</details>

<details><summary>🔧 Read: PLAN.md · 20:19</summary>

**Аргументы**

```json
{
 "file_path": "d:\\Flash\\golova\\KSE_AI\\AAFS\\PLAN.md",
 "limit": 160
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
… [обрезано: показано 3000 из 14364 символов]
```

</details>

<details><summary>🔧 Bash: Show DECISIONS.md headings · 20:19</summary>

**Аргументы**

```bash
grep -n "^#" DECISIONS.md | head -80
```

**Результат**

```
1:# Журнал решений (DECISIONS.md)
10:## D00. Как проходил этап 1
18:## D01. Снимок данных
28:## D02. Свежесть данных: официальный ряд остановился 7 сентября
51:## D03. Дубликаты
65:## D04. Переход на районы и начало рабочего периода
94:## D05. Единицы прогноза и охват
114:## D06. Донецкая область
128:## D07. Клоны районов
165:## D08. Громады
181:## D09. Сообщения об угрозах в канале
210:## D10. Длинные тревоги и «статус неизвестен»
265:## D11. Перекрытия
275:## D12. Порог склейки коротких пауз
299:## D13. Правый край данных
313:## D14. Разбиение по времени
330:## D15. Перерыв в работе канала в тестовом окне
357:## D16. Доступ к истории «на момент t»
402:## D17. Сетка и целевая переменная (этап 3)
440:## D18. Бэктест, бейзлайны, метрики, проверка утечки (этап 4)
477:## D19. Признаки (этап 5)
523:## D20. Модели (этап 6)
563:## D21. Признаки видят только то, что было известно: закрытый доступ и проверка знания
589:## D22. Проверка на свежих данных alerts.in.ua (этап 8)
651:## Справочные цифры (для проверки повторного подсчёта)
674:## Пойманные ошибки ИИ
```

</details>

<details><summary>🔧 Read: DECISIONS.md · 20:19</summary>

**Аргументы**

```json
{
 "file_path": "d:\\Flash\\golova\\KSE_AI\\AAFS\\DECISIONS.md",
 "limit": 360
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
… [обрезано: показано 3000 из 26667 символов]
```

</details>

<details><summary>🔧 Read: DECISIONS.md · 20:19</summary>

**Аргументы**

```json
{
 "file_path": "d:\\Flash\\golova\\KSE_AI\\AAFS\\DECISIONS.md",
 "offset": 640,
 "limit": 70
}
```

**Результат**

```
640	- порча будущего — пять моделей, обучающие строки и прогнозы совпали.
641	
642	**Ограничения:**
643	- данные скачаны один раз, в воскресенье. Повторное скачивание объединяется по `id` с более поздним `updated_at` (`read_raw`);
644	- у API своя обработка: точные правила закрытия тревог неизвестны, а записи на всю область разворачиваются на районы;
645	- воспроизведение требует своего токена.
646	
647	**Статус:** зафиксировано.
648	
649	---
650	
651	## Справочные цифры (для проверки повторного подсчёта)
652	
653	Определения: записи целевого охвата (D05) с началом `≥ work_start`, после очистки D03. Таблицу сверяет `scripts/run_all.py`: при любом расхождении он завершается с кодом 1, а сверка лежит в `reports/stage1_summary.md`.
654	
655	| Величина | Значение |
656	|---|---|
657	| Строк в файле / после дедупликации / после удаления длительностей ≤ 0 | 299 275 / 185 430 / 185 428 |
658	| Последнее начало / последний конец в файле | 2026-09-07 05:28:22 UTC / 05:39:33 UTC |
659	| Записей в охвате (начало ≥ work_start, 111 локаций) | 80 194 (было 80 196: в число входили 2 записи нулевой длительности; при старом фильтре «начало ≤ data_end» отчёт давал 80 148) |
660	| Тревог на единицу: min / p10 / медиана / p90 / max | 87 / 92 / 604 / 1 567 / 2 253 |
661	| Длительность: медиана / p75 / p99 | 47 / 113 / 760 минут |
662	| Тревог > 24 ч / > 72 ч / > 24 ч в тестовом окне | 119 / 22 / 33 |
663	| Записей ровно 3600 с / из них в тестовом окне | 82 / 21 |
664	| Перекрытий после дедупликации | 0 |
665	| Единиц до / после склейки клонов | 111 / 104 |
666	| Перерывы канала (D15) | 2026-08-29 05:55:28 → 2026-09-02 13:48:04 UTC |
667	| Замаскировано единице-часов: обучение / валидация / тест | 0.46% / 0.38% / 15.93% |
668	| API: локаций найдено / записей в схеме / строк h = 3 (D22, на тех же сырых данных) | 119 из 119 / 14 389 / 42 004 |
669	| Строк сетки при h = 3: обучение / валидация / тест (D17) | 510 642 / 57 865 / 48 028 |
670	| Базовая частота в обучении: h = 1 / 3 / 6 (D17) | 0.089 / 0.209 / 0.321 |
671	
672	---
673	
674	## Пойманные ошибки ИИ
675	
676	| № | Ошибка | Кто | Как обнаружено | Исправление |
677	|---|---|---|---|---|
678	| 1 | «16 областей имели районные тревоги с марта 2022, параллельный режим длился годами» — вывод по наивному `groupby().min()` | Claude, Gemini Pro | Первым заметил Gemini Flash; подтверждено помесячной долей: в 2024 году 0.000–0.001 | D04 |
679	| 2 | Перекрытия считались на данных с дубликатами (32 945 / 18 044 / 30 294) | Все три; Claude — вопреки собственному D02 | Пересчёт после дедупликации: 0 | D11 |
680	| 3 | Дубликаты не замечены, все счётчики завышены | Gemini Flash, Gemini Pro | Сравнение с D02 Claude и проверка на данных | D03 |
681	| 4 | «Донецкая область не разбита на районы» | Gemini Flash | В данных 8 районов со списочными постами | D06 |
682	| 5 | Порог склейки пауз «подбираем на валидации» | Claude | Методический разбор: порог определяет саму целевую переменную | D12 |
683	| 6 | Громады «нужно сопоставлять с р
… [обрезано: показано 3000 из 10807 символов]
```

</details>

<details><summary>🔧 Bash: Read config files and timeutil · 20:19</summary>

**Аргументы**

```bash
cat -n config.yaml && cat -n src/alerts/config.py && cat -n src/alerts/timeutil.py
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
… [обрезано: показано 3000 из 9952 символов]
```

</details>

<details><summary>🔧 Bash: Read fetch_data and vadimkin loader · 20:20</summary>

**Аргументы**

```bash
cat -n scripts/fetch_data.py; ls src/alerts/ingest; cat -n src/alerts/ingest/vadimkin.py
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
__init__.py
__pycache__
alerts_in_ua.py
vadimkin.py
     1	import hashlib
     2	import logging
     3	
     4	import pandas as pd
     5	
     6	logger = logging.getLogger(__name__)
     7	
     8	
     9	def file_sha256(path) -> str:
    10	    h = hashlib.sha256()
    11	    with open(path, 'rb') as f:
    12	        for block in iter(lambda: f.read(1 << 20), b''):
    13	            h.update(block)
    14	    return h.hexdigest()
    15	
    16	
    17	def load_official(path, expected_sha256: str) -> pd.DataFrame:
    18	    """Load the official Vadimkin dataset (D01, D03).
    19	
    20	    SHA-256 check, UTC parsing, drop_duplicates, then drop durations <= 0.
    21	    Row counts of every step are logged and kept in df.attrs['row_counts'].
    22	    """
    23	    file_hash = file_sha256(path)
    24	    if file_hash != expected_sha256:
    25	        raise ValueError(f'SHA-256 mismatch! Expected {expected_sha256}, got {file_hash}')
    26	    logger.info('SHA-256 hash verified.')
    27	
    28	    df = pd.read_csv(path)
    29	    initial_rows = len(df)
    30	
    31	    df['started_at'] = pd.to_datetime(df['started_at'], utc=True).dt.as_unit('s')
    32	    df['finished_at'] = pd.to_datetime(df['finished_at'], utc=True).dt.as_unit('s')
    33	
    34	    df = df.drop_duplicates()
    35
… [обрезано: показано 3000 из 3606 символов]
```

</details>

<details><summary>🔧 Bash: Read scope and processor modules · 20:20</summary>

**Аргументы**

```bash
cat -n src/alerts/scope.py src/alerts/processor.py
```

**Результат**

```
1	"""Forecast scope (D05, D06): which source records feed which unit, over which period.
     2	
     3	The only place where scope rules live; every stage gets its records from select_scope().
     4	"""
     5	import numpy as np
     6	import pandas as pd
     7	
     8	from alerts.config import ts
     9	from alerts.processor import flag_records
    10	
    11	LEVEL_RAION = 'raion'
    12	LEVEL_OBLAST = 'oblast'
    13	ROLE_TARGET = 'target'
    14	ROLE_INPUT = 'input'
    15	
    16	LOC_KEY = ['oblast', 'raion']
    17	
    18	
    19	def select_scope(df: pd.DataFrame, cfg: dict, period: bool = True) -> pd.DataFrame:
    20	    """Source records in scope, one row per record.
    21	
    22	    role='target': raion-level records outside excluded and input-only oblasts, plus
    23	        oblast-level records of `oblast_level_units` (Kyiv, D05); for those, raion = oblast name.
    24	    role='input': raion-level records of input-only oblasts (Donetsk, D06): features only.
    25	
    26	    Processor flags (next_start, is_long, is_fake_end, open_until; see alerts.processor) are
    27	    computed over all records of a location before the period filter, so that a next start
    28	    beyond data_end is still seen.
    29	
    30	    period=True keeps records that overlap [work_start, data_end) and does not clip them:
    31	    clipping would invent an alert start at work_start.
    32	    """
    33	    sc = cfg['scope']
    34	    _check_oblast_names(df, sc)
    35	
    36	    is_raion = df['level'] == LEVEL_RAION
    37	    special = df['oblast'].isin(sc['oblast_level_units'])
    38	    if (is_raion & special).any():
    39	        raise ValueError('raion-level records appeared for an oblast-level unit; D05 needs revisiting')
    40	    if df.loc[is_raion, 'raion'].isna().any():
    41	        raise ValueError('raion-level records without a raion name')
    42	
    43	    not_target = sc['excluded_oblasts'] + sc['input_only_oblasts']
    44	    target = (is_raion & ~df['oblast'].isin(not_target)) | ((df['level'] == LEVEL_OBLAST) & special)
    45	    inputs = is_raion & df['oblast'].isin(sc['input_only_oblasts'])
    46	
    47	    cols = ['oblast', 'raion', 'level', 'started_at', 'finished_at', 'duration']
    48	    out = df.loc[target | inputs, cols].copy()
    49	    out['role'] = np.where(inputs[target | inputs], ROLE_INPUT, ROLE_TARGET)
    50	    out['raion'] = out['raion'].fillna(out['oblast'])
    51	    out = flag_records(out, cfg, LOC_KEY)
    52	
    53	    if period:
    54	        work_start, data_end = ts(cfg['periods']['work_start']), ts(cfg['data_end'])
    55	        out = out[(out['started_at'] < data_end) & (out['finished_at'] > work_start)]
    56	    return out.reset_index(drop=True)
    57	
    58	
    59	def attach_units(records: pd.DataFrame, units: pd.DataFrame) -> pd.DataFrame:
    60	    """Add unit_id by the (oblast, raion) key. Every record must map: nothing is dropped silently."""
    61	    out = records.me
… [обрезано: показано 3000 из 6562 символов]
```

</details>

<details><summary>🔧 Bash: Read units and mask modules · 20:20</summary>

**Аргументы**

```bash
cat -n src/alerts/units.py src/alerts/mask.py
```

**Результат**

```
1	"""Units and clone merging (D05, D06, D07). Pure functions: nothing is written to disk here."""
     2	import logging
     3	
     4	import numpy as np
     5	import pandas as pd
     6	
     7	from alerts.config import ts
     8	from alerts.scope import LOC_KEY, ROLE_INPUT, ROLE_TARGET
     9	from alerts.timeutil import to_sec
    10	
    11	logger = logging.getLogger(__name__)
    12	
    13	
    14	def build_units(scope: pd.DataFrame, cfg: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    15	    """Map every location to a unit.
    16	
    17	    Target locations: Jaccard similarity of 1-minute "under alert" series on the train period
    18	    within each oblast; connected components over edges >= clone_jaccard become one unit (D07).
    19	    Input-only oblasts (D06): one unit per oblast, `I00`, `I01`, ...
    20	
    21	    Returns (units, pairs): units has columns oblast, raion, unit_id, unit_name, role;
    22	    pairs holds the Jaccard similarity of every same-oblast pair of target locations.
    23	    """
    24	    target = scope[scope['role'] == ROLE_TARGET]
    25	    locs = target[LOC_KEY].drop_duplicates().sort_values(LOC_KEY).reset_index(drop=True)
    26	    logger.info(f'Target locations (raions + Kyiv): {len(locs)}')
    27	
    28	    grid = _minute_grid(target, locs, ts(cfg['periods']['work_start']), ts(cfg['periods']['train_end']))
    29	    pairs = _pair_similarity(grid, locs)
    30	
    31	    edges = pairs.loc[pairs['jaccard'] >= cfg['thresholds']['clone_jaccard'], ['i', 'j']].to_numpy()
    32	    comp = _components(len(locs), edges)
    33	
    34	    # Stable ids: components ordered by their alphabetically first raion
    35	    members = pd.DataFrame({'comp': comp, 'raion': locs['raion'], 'oblast': locs['oblast']})
    36	    first = members.sort_values(['raion', 'oblast']).groupby('comp')['raion'].first()
    37	    order = first.sort_values(kind='stable').index
    38	    comp_to_id = {c: f'U{i:03d}' for i, c in enumerate(order)}
    39	    names = members.sort_values('raion').groupby('comp')['raion'].agg(' + '.join)
    40	
    41	    units = locs.assign(unit_id=[comp_to_id[c] for c in comp],
    42	                        unit_name=[names[c] for c in comp],
    43	                        role=ROLE_TARGET)
    44	    logger.info(f'Target units after clone merging: {units["unit_id"].nunique()}')
    45	
    46	    inputs = scope.loc[scope['role'] == ROLE_INPUT, LOC_KEY].drop_duplicates().sort_values(LOC_KEY)
    47	    input_ids = {ob: f'I{i:02d}' for i, ob in enumerate(sorted(inputs['oblast'].unique()))}
    48	    inputs = inputs.assign(unit_id=inputs['oblast'].map(input_ids), unit_name=inputs['oblast'], role=ROLE_INPUT)
    49	
    50	    units = pd.concat([units, inputs], ignore_index=True)
    51	    pairs = pairs.drop(columns=['i', 'j']).sort_values('jaccard', ascending=False, kind='stable')
    52	    return units, pairs.reset_index(drop=True)
    53	
    54	
    55	def _minute_grid(records: pd.DataFram
… [обрезано: показано 3000 из 13084 символов]
```

</details>

<details><summary>🔧 Bash: Read spans module and size other files · 20:20</summary>

**Аргументы**

```bash
cat -n src/alerts/spans.py; wc -l src/alerts/report.py src/alerts/pipeline.py src/alerts/store.py src/alerts/intervals.py
```

**Результат**

```
1	"""Vectorised interval operations shared by masks, intervals and reports."""
     2	import numpy as np
     3	import pandas as pd
     4	
     5	
     6	def merge_labels(df: pd.DataFrame, key: str, start: str, end: str,
     7	                 gap: pd.Timedelta = pd.Timedelta(0)) -> np.ndarray:
     8	    """Group ids for rows of `df` sorted by (key, start).
     9	
    10	    A row joins the current group of its key if it starts no later than `gap` after the
    11	    running maximum end of that group. gap=0 is a union of overlapping or touching intervals;
    12	    gap>0 also bridges short pauses. Equivalent to the classic sort-and-extend loop.
    13	    """
    14	    if df.empty:
    15	        return np.zeros(0, dtype=np.int64)
    16	    d = df[[key, start, end]].reset_index(drop=True)  # positional alignment, index may repeat
    17	    running_end = d.groupby(key, sort=False)[end].cummax()
    18	    prev_end = running_end.groupby(d[key], sort=False).shift(1)
    19	    new_group = prev_end.isna() | ((d[start] - prev_end) > gap)
    20	    return new_group.to_numpy().cumsum() - 1
    21	
    22	
    23	def union(df: pd.DataFrame, key: str, start: str = 'start', end: str = 'end',
    24	          gap: pd.Timedelta = pd.Timedelta(0)) -> pd.DataFrame:
    25	    """Disjoint union of intervals per key, columns [key, start, end]."""
    26	    df = df.sort_values([key, start, end])
    27	    labels = merge_labels(df, key, start, end, gap)
    28	    return (df.groupby(labels)
    29	              .agg(**{key: (key, 'first'), start: (start, 'min'), end: (end, 'max')})
    30	              .reset_index(drop=True))
    31	
    32	
    33	def clipped_seconds(start: pd.Series, end: pd.Series, lo: pd.Timestamp, hi: pd.Timestamp) -> float:
    34	    """Total seconds of [start, end) intervals inside [lo, hi). Intervals must be disjoint per key."""
    35	    s = start.where(start > lo, lo)
    36	    e = end.where(end < hi, hi)
    37	    return float(((e - s).dt.total_seconds()).clip(lower=0).sum())
    38	
    39	
    40	def covers(s: np.ndarray, e: np.ndarray, x: np.ndarray) -> np.ndarray:
    41	    """Is each moment x inside one of the disjoint sorted half-open intervals [s, e)? int64 seconds."""
    42	    if len(s) == 0:
    43	        return np.zeros(len(x), dtype=bool)
    44	    k = np.searchsorted(s, x, side='right') - 1
    45	    return (k >= 0) & (e[np.maximum(k, 0)] > x)
    46	
    47	
    48	def reaches(s: np.ndarray, e: np.ndarray, lo: np.ndarray, hi: np.ndarray) -> np.ndarray:
    49	    """Does the open window (lo, hi) overlap one of the disjoint sorted intervals [s, e)?"""
    50	    if len(s) == 0:
    51	        return np.zeros(len(lo), dtype=bool)
    52	    j = np.searchsorted(e, lo, side='right')  # first interval ending after lo; ends are sorted
    53	    jj = np.minimum(j, len(s) - 1)
    54	    return (j < len(s)) & (s[jj] < hi)
    55	
    56	
    57	def count_in(points: np.ndarray, lo: np.ndarray, hi: np.ndarray)
… [обрезано: показано 3000 из 3985 символов]
```

</details>

<details><summary>🔧 Bash: Read report module · 20:20</summary>

**Аргументы**

```bash
cat -n src/alerts/report.py
```

**Результат**

```
1	"""Stage summaries: numbers and markdown (figures: alerts.figures).
     2	
     3	Every number of the DECISIONS.md reference table is recomputed and compared (PLAN rule 8).
     4	"""
     5	import logging
     6	
     7	import numpy as np
     8	import pandas as pd
     9	
    10	from alerts import figures
    11	from alerts.config import path, ts
    12	from alerts.history import AlertHistory
    13	from alerts.intervals import episodes
    14	from alerts.mask import FAKE_END, LONG
    15	from alerts.scope import LOC_KEY, ROLE_INPUT, ROLE_TARGET
    16	from alerts.timeutil import to_sec
    17	
    18	logger = logging.getLogger(__name__)
    19	
    20	# DECISIONS.md, "Справочные цифры". Records: target scope, start >= work_start, after D03 cleaning.
    21	REFERENCE = {
    22	    'rows raw / dedup / cleaned': '299275 / 185430 / 185428',
    23	    'last start / last end in the file (UTC)': '2026-09-07 05:28:22 / 2026-09-07 05:39:33',
    24	    'scope records, start >= work_start': '80194',
    25	    'alerts per location: min / p10 / median / p90 / max': '87 / 92 / 604 / 1567 / 2253',
    26	    'duration, min: median / p75 / p99': '47 / 113 / 760',
    27	    'alerts > 24 h / > 72 h / > 24 h in test': '119 / 22 / 33',
    28	    'records of exactly 3600 s / in test': '82 / 21',
    29	    'overlaps within a location': '0',
    30	    'locations / units': '111 / 104',
    31	    'channel outages (D15)': '2026-08-29 05:55:28 -> 2026-09-02 13:48:04',
    32	    'grid rows h=3: train / val / test (D17)': '510642 / 57865 / 48028',
    33	    'base rate train: h=1 / h=3 / h=6 (D17)': '0.089 / 0.209 / 0.321',
    34	}
    35	
    36	def write_all(art, cfg) -> list[str]:
    37	    """Write summaries and figures; return the reference values that do not match."""
    38	    out = path(cfg, 'reports')
    39	    (out / 'figures').mkdir(parents=True, exist_ok=True)
    40	    actual = reference_numbers(art, cfg)
    41	    mismatches = [k for k, v in REFERENCE.items() if actual[k] != v]
    42	    (out / 'stage1_summary.md').write_text(_stage1_md(actual, mismatches, art.mask_stats), encoding='utf-8')
    43	    (out / 'stage2_summary.md').write_text(_stage2_md(art, cfg), encoding='utf-8')
    44	    (out / 'stage3_summary.md').write_text(_stage3_md(art.grid_stats), encoding='utf-8')
    45	    figures.stage_figures(art, cfg, out / 'figures')
    46	    for k in mismatches:
    47	        logger.error(f'Reference mismatch: {k}: expected {REFERENCE[k]}, got {actual[k]}')
    48	    return mismatches
    49	
    50	
    51	# --- numbers -------------------------------------------------------------------------------
    52	def reference_numbers(art, cfg) -> dict:
    53	    work_start, test_start = ts(cfg['periods']['work_start']), ts(cfg['periods']['val_end'])
    54	    df = art.df
    55	    rec = art.scope_all[(art.scope_all['role'] == ROLE_TARGET) & (art.scope_all['started_at'] >= work_start)]
… [обрезано: показано 3000 из 12957 символов]
```

</details>

<details><summary>🔧 Bash: Read stage 1/2 summaries and high-sim pairs · 20:20</summary>

**Аргументы**

```bash
cat reports/stage1_summary.md; cat reports/stage2_summary.md; head -30 reports/high_sim_pairs.csv; wc -l reports/high_sim_pairs.csv
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
oblast,raion1,raion2,jaccard
Zaporizka oblast,Melitopols
… [обрезано: показано 3000 из 5148 символов]
```

</details>

<details><summary>🔧 Bash: Read pipeline, store, run_all · 20:20</summary>

**Аргументы**

```bash
cat -n src/alerts/pipeline.py src/alerts/store.py; cat -n scripts/run_all.py | head -80
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
    63
… [обрезано: показано 3000 из 11100 символов]
```

</details>

<details><summary>🔧 Bash: Read conftest and load/units tests · 20:20</summary>

**Аргументы**

```bash
cat -n tests/conftest.py tests/test_load.py tests/test_units.py
```

**Результат**

```
1	import copy
     2	
     3	import pandas as pd
     4	import pytest
     5	
     6	_BASE_CFG = {
     7	    'dataset': {'repo_url': '', 'commit': '', 'repo_dir': '', 'path': '', 'sha256': '', 'path_uk': '', 'sha256_uk': ''},
     8	    'volunteer': {'commit': '', 'path': '', 'sha256': ''},
     9	    'data_end': '2026-03-01T00:00:00Z',
    10	    'periods': {'work_start': '2026-01-01T00:00:00Z', 'warmup_end': '2026-01-02T00:00:00Z',
    11	                'train_end': '2026-02-01T00:00:00Z', 'val_end': '2026-02-15T00:00:00Z'},
    12	    'scope': {'excluded_oblasts': [], 'input_only_oblasts': [], 'oblast_level_units': []},
    13	    # Synthetic data is sparse: the outage rule is switched off unless a test turns it on.
    14	    'thresholds': {'pause_merge_min': 15, 'long_alert_hours': 24, 'clone_jaccard': 0.997,
    15	                   'similar_pairs_report': 0.95, 'outage_gap_hours': 1_000_000},
    16	    'processor': {'enabled': True, 'fake_end_duration_s': 3600, 'fake_end_next_start_h': 3},
    17	    'history': {'max_open_hours': 24},
    18	    'geo': {'path': '', 'sha256': '', 'vertex_decimals': 5, 'min_shared_vertices': 2, 'renames': {}},
    19	    'backtest': {'horizons': [3], 'baselines': ['B0', 'B1', 'B2'], 'models': ['LR', 'LGBM']},
    20	    'models': {'threads': 2, 'seed': 1,
    21	               'lr': {'grid': {'C': [1.0], 'half_life_days': [None, 28]}},
    22	               'lgbm': {'learning_rate': 0.1, 'max_estimators': 60, 'early_stopping_rounds': 10,
    23	                        'grid': {'num_leaves': [7], 'min_child_samples': [20], 'half_life_days': [None, 28]}}},
    24	    'baselines': {'b1_window_days': 28, 'prior_strength': 5},
    25	    'bootstrap': {'n_reps': 50, 'n_reps_oblast': 20, 'ci': 0.95, 'seed': 1},
    26	    'leakage_check': {'cuts': [], 'horizon': 3},
    27	    'report': {'forecast_units': [], 'forecast_days': 7},
    28	    'api': {'base_url': '', 'history_path': '', 'token_env': '', 'token_file': '', 'pause_seconds': 0,
    29	            'retry_after_429_seconds': 0, 'raw_dir': '', 'oblast_uids': []},
    30	    'horizons': [1, 3, 6],
    31	    'paths': {'units': '', 'mask': '', 'intervals': '', 'seen': '', 'neighbors': '', 'grid': '', 'predictions': '', 'similar_pairs': '', 'reports': ''},
    32	}
    33	
    34	
    35	@pytest.fixture
    36	def cfg():
    37	    return copy.deepcopy(_BASE_CFG)
    38	
    39	
    40	def records(rows) -> pd.DataFrame:
    41	    """Source records in the loader's format from (oblast, raion | None, level, start, end) tuples."""
    42	    df = pd.DataFrame(rows, columns=['oblast', 'raion', 'level', 'started_at', 'finished_at'])
    43	    for c in ['started_at', 'finished_at']:
    44	        df[c] = pd.to_datetime(df[c], utc=True).dt.as_unit('s')
    45	    df['duration'] = (df['finished_at'] - df['started_at']).dt.total_seconds()
    46	    return df
    47	
    48	
    49	def units_table(rows) -> pd.DataFra
… [обрезано: показано 3000 из 5533 символов]
```

</details>

<details><summary>🔧 Bash: Read mask tests · 20:20</summary>

**Аргументы**

```bash
cat -n tests/test_mask.py
```

**Результат**

```
1	import pandas as pd
     2	from conftest import records, units_table, utc
     3	
     4	from alerts.intervals import build_intervals
     5	from alerts.mask import FAKE_END, LONG, OUTAGE, build_masks
     6	from alerts.scope import select_scope
     7	
     8	UNITS = units_table([
     9	    ('A', 'Raion 1', 'U_A'),
    10	    ('A', 'Raion 2', 'U_A'),  # clone of Raion 1
    11	    ('B', 'Raion 3', 'U_B'),
    12	])
    13	
    14	
    15	def run(rows, cfg):
    16	    df = records(rows)
    17	    masks, outages, stats = build_masks(df, select_scope(df, cfg, period=False), UNITS, cfg)
    18	    intervals = build_intervals(select_scope(df, cfg), UNITS, masks, cfg)
    19	    return masks, outages, intervals
    20	
    21	
    22	def test_long_alert_goes_to_mask(cfg):
    23	    """Rule (a): an alert longer than 24 h is masked whole, on its unit, and flagged uncertain."""
    24	    rows = [
    25	        ('A', 'Raion 1', 'raion', '2026-01-10T08:00:00Z', '2026-01-11T14:00:00Z'),  # 30 h
    26	        ('A', 'Raion 2', 'raion', '2026-01-10T08:00:05Z', '2026-01-10T09:00:00Z'),  # its clone, normal end
    27	        ('B', 'Raion 3', 'raion', '2026-01-10T08:00:00Z', '2026-01-11T07:59:59Z'),  # 23:59:59: no mask
    28	    ]
    29	    masks, _, intervals = run(rows, cfg)
    30	    long = masks[masks['reason'] == LONG]
    31	    assert long[['unit_id', 'start', 'end']].values.tolist() == [
    32	        ['U_A', utc('2026-01-10T08:00:00Z'), utc('2026-01-11T14:00:00Z')]]
    33	    assert intervals.set_index('unit_id')['uncertain'].to_dict() == {'U_A': True, 'U_B': False}
    34	
    35	
    36	def test_fake_end_goes_to_mask(cfg):
    37	    """Rule (b): exactly 1 h and the next start of the same source location more than 3 h later.
    38	
    39	    The mask runs from the start to that next start; the next alert itself is not uncertain.
    40	    """
    41	    rows = [
    42	        # fake end: next start of Raion 3 is 5 h after this start
    43	        ('B', 'Raion 3', 'raion', '2026-01-10T08:00:00Z', '2026-01-10T09:00:00Z'),
    44	        ('B', 'Raion 3', 'raion', '2026-01-10T13:00:00Z', '2026-01-10T13:40:00Z'),
    45	        # exactly 1 h, but the next start comes after 2 h: a real end
    46	        ('B', 'Raion 3', 'raion', '2026-01-12T08:00:00Z', '2026-01-12T09:00:00Z'),
    47	        ('B', 'Raion 3', 'raion', '2026-01-12T10:00:00Z', '2026-01-12T10:30:00Z'),
    48	        # 3599 s: not the processor's value
    49	        ('B', 'Raion 3', 'raion', '2026-01-14T08:00:00Z', '2026-01-14T08:59:59Z'),
    50	        ('B', 'Raion 3', 'raion', '2026-01-14T20:00:00Z', '2026-01-14T20:30:00Z'),
    51	        # the processor works per source location: the clone's start 1 h later does not matter,
    52	        # Raion 1's own next start is 4 h later
    53	        ('A', 'Raion 1', 'raion', '2026-01-16T08:00:00Z', '2026-01-16T09:00:00Z'),
    54	        ('A', 'Raion 2', 'raion', '2026-01-16T09:00:00Z', '2026-01-16T09:20:00Z'),
    55	      
… [обрезано: показано 3000 из 4578 символов]
```

</details>

<details><summary>🔧 Bash: Read official channel processor · 20:20</summary>

**Аргументы**

```bash
wc -l dataset_repo/processors/official_channel_processor.py && cat -n dataset_repo/processors/official_channel_processor.py
```

**Результат**

```
344 dataset_repo/processors/official_channel_processor.py
     1	import csv
     2	import datetime
     3	import json
     4	import logging
     5	import os.path
     6	import pathlib
     7	import pickle
     8	from typing import Optional, List
     9	
    10	from telethon.tl.types import Message
    11	
    12	from .legacy_states import get_new_name
    13	from .tg_dataclasses import OfficialAirRaidAlertChannelAlert, PLACE_LEVEL
    14	
    15	logging.basicConfig()
    16	logger = logging.getLogger(__name__)
    17	logger.setLevel(logging.DEBUG)
    18	
    19	data_uk_file_path = pathlib.Path(__file__).parent.resolve() / "../datasets/official_data_uk.csv"
    20	data_en_file_path = pathlib.Path(__file__).parent.resolve() / "../datasets/official_data_en.csv"
    21	
    22	last_processed_id_path = pathlib.Path(__file__).parent.resolve() / "pkl" / "official_last_processed_id.txt"
    23	pkl_file_path = pathlib.Path(__file__).parent.resolve() / "pkl" / "official_active_alerts.pkl"
    24	
    25	
    26	class OfficialAirAlertProcessor:
    27	    channel_name = "air_alert_ua"
    28	
    29	    # State
    30	    # key is place name in hashtag format, value is tuple (oblast name, raion name, hromada name, level)
    31	    hash_states_by_name: dict[str, tuple[str, str, str, PLACE_LEVEL]] = {}
    32	
    33	    active_alerts_by_location: dict[str, OfficialAirRaidAlertChannelAlert] = {}
    34	    completed_alerts: list[OfficialAirRaidAlertChannelAlert] = []
    35	
    36	    last_processed_id: int = 0
    37	
    38	    def __init__(self, client):
    39	        self.client = client
    40	
    41	        self.load_states()
    42	        self.load_active_alerts()
    43	        self.load_last_processed_id()
    44	
    45	    async def process(self):
    46	        previous_day = None
    47	
    48	        logging.info("Starting processing official channel messages from %s", self.last_processed_id)
    49	
    50	        # TODO Fetch latest days from .csv file and just append it
    51	        async for message in self.client.iter_messages(self.channel_name, reverse=True, min_id=self.last_processed_id):
    52	            if not previous_day or previous_day != message.date.date():
    53	                previous_day = message.date.date()
    54	                logger.info("Processing day %s", previous_day)
    55	
    56	            if not message.message:
    57	                continue
    58	
    59	            self.process_message(message)
    60	
    61	            self.last_processed_id = message.id
    62	
    63	        logging.info("Finished processing official channel messages at %s", self.last_processed_id)
    64	        self.write()
    65	
    66	    def load_active_alerts(self):
    67	        if not os.path.exists(pkl_file_path):
    68	            return
    69	
    70	        with open(pkl_file_path, "rb") as f:
    71	            self.active_alerts_by_locat
… [обрезано: показано 3000 из 17092 символов]
```

</details>

<details><summary>🔧 Bash: Inspect raw CSV and dataset repo state · 20:21</summary>

**Аргументы**

```bash
head -5 dataset_repo/datasets/official_data_en.csv && tail -3 dataset_repo/datasets/official_data_en.csv && git -C dataset_repo status --short | head; git -C dataset_repo log --oneline -3; git -C dataset_repo rev-parse HEAD
```

**Результат**

```
oblast,raion,hromada,level,started_at,finished_at,source
Vinnytska oblast,,,oblast,2022-03-15 16:10:34+00:00,2022-03-15 16:50:07+00:00,official
Zhytomyrska oblast,,,oblast,2022-03-15 16:11:25+00:00,2022-03-15 16:54:23+00:00,official
Cherkaska oblast,Umanskyi raion,Umanska terytorialna hromada,hromada,2022-03-15 16:11:50+00:00,2022-03-15 16:54:47+00:00,official
Mykolaivska oblast,Pervomaiskyi raion,m. Pervomaisk ta Pervomaiska terytorialna hromada,hromada,2022-03-15 16:14:46+00:00,2022-03-15 16:57:08+00:00,official
Poltavska oblast,Poltavskyi raion,,raion,2026-09-07 04:38:21+00:00,2026-09-07 04:56:59+00:00,official
Sumska oblast,Konotopskyi raion,,raion,2026-09-07 05:12:16+00:00,2026-09-07 05:38:04+00:00,official
Dnipropetrovska oblast,Kamianskyi raion,,raion,2026-09-07 05:28:22+00:00,2026-09-07 05:38:32+00:00,official
58ee75b Add new data
2cbbd62 Add new data
308bb92 Add new data
58ee75bc20113181b9ddf8029d4cbf3a62d8cd10
```

</details>

<details><summary>🔧 Bash: Create scratch dir and check Python versions · 20:21</summary>

**Аргументы**

```bash
mkdir -p /d/Flash/golova/KSE_AI/AAFS/reviews/scratch/stage0-1b && cd /d/Flash/golova/KSE_AI/AAFS && python --version && python -c "import pandas, numpy; print(pandas.__version__, numpy.__version__)"
```

**Результат**

```
Python 3.12.9
3.0.6 2.5.3
```

</details>

<details><summary>🔧 Write: reviews/scratch/stage0-1b/s01_raw_formats.py · 20:21</summary>

**Аргументы**

```
# file: reviews/scratch/stage0-1b/s01_raw_formats.py
"""Stage 0-1b review: raw CSV formats, near-duplicates, as_unit('s') effects. Read-only."""
import re
from collections import Counter

import pandas as pd

from alerts.config import ROOT, load_config

cfg = load_config()
path = ROOT / cfg['dataset']['path']
raw = pd.read_csv(path, dtype=str, keep_default_na=False)
print('raw rows', len(raw), 'cols', list(raw.columns))

# 1. timestamp formats
for c in ['started_at', 'finished_at']:
    pat = raw[c].str.replace(r'\d', 'D', regex=True)
    print(c, Counter(pat).most_common(10))

# 2. columns: value counts of level and source, empty strings
for c in ['level', 'source']:
    print(c, raw[c].value_counts().to_dict())
for c in raw.columns:
    v = raw[c]
    print(f'{c}: empty={int((v == "").sum())}, leading/trailing ws={int((v != v.str.strip()).sum())}, '
          f'double space={int(v.str.contains("  ").sum())}')

# 3. exact duplicates on raw strings vs after parsing
print('dups raw strings:', raw.duplicated().sum())
nd = pd.read_csv(path)
print('dups default read:', nd.duplicated().sum())
# near-duplicates: same everything except source
key_nosrc = [c for c in raw.columns if c != 'source']
dedup = raw.drop_duplicates()
print('after dedup, dup on all cols but source:', dedup.duplicated(key_nosrc).sum())
# same location and start, different end
loc = ['oblast', 'raion', 'hromada', 'level']
print('after dedup, same loc+start (different end):', dedup.duplicated(loc + ['started_at']).sum())
print('after dedup, same loc+end (different start):', dedup.duplicated(loc + ['finished_at']).sum())
# NaN vs empty: default read gives NaN for empty; compare dup counts
print('max multiplicity of a record:', raw.groupby(list(raw.columns)).size().max())

# 4. as_unit('s') loss
p = pd.to_datetime(nd['started_at'], utc=True)
print('parsed unit', p.dt.unit, 'nonzero subsecond:', int((p.dt.microsecond != 0).sum() + (p.dt.nanosecond != 0).sum()))

```

**Результат**

```
File created successfully at: d:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage0-1b\s01_raw_formats.py (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Bash: Run raw format and duplicate checks · 20:21</summary>

**Аргументы**

```bash
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage0-1b/s01_raw_formats.py
```

**Результат**

```
raw rows 299275 cols ['oblast', 'raion', 'hromada', 'level', 'started_at', 'finished_at', 'source']
started_at [('DDDD-DD-DD DD:DD:DD+DD:DD', 299275)]
finished_at [('DDDD-DD-DD DD:DD:DD+DD:DD', 299275)]
level {'raion': 132251, 'oblast': 130235, 'hromada': 36789}
source {'official': 299275}
oblast: empty=0, leading/trailing ws=0, double space=0
raion: empty=130235, leading/trailing ws=0, double space=0
hromada: empty=262486, leading/trailing ws=0, double space=0
level: empty=0, leading/trailing ws=0, double space=0
started_at: empty=0, leading/trailing ws=0, double space=0
finished_at: empty=0, leading/trailing ws=0, double space=0
source: empty=0, leading/trailing ws=0, double space=0
dups raw strings: 113845
dups default read: 113845
after dedup, dup on all cols but source: 0
after dedup, same loc+start (different end): 0
after dedup, same loc+end (different start): 0
max multiplicity of a record: 2
parsed unit us nonzero subsecond: 0
```

</details>

<details><summary>🔧 Bash: Check timezone offsets, field counts, quotes · 20:22</summary>

**Аргументы**

```bash
cut -d, -f5,6 dataset_repo/datasets/official_data_en.csv | tail -n +2 | grep -o '+[0-9][0-9]:[0-9][0-9]' | sort | uniq -c; awk -F, 'NR>1{print NF}' dataset_repo/datasets/official_data_en.csv | sort | uniq -c; grep -c '"' dataset_repo/datasets/official_data_en.csv
```

**Результат**

```
598550 +00:00
 299275 7
0
```

</details>

<details><summary>🔧 Write: reviews/scratch/stage0-1b/s02_scope.py · 20:22</summary>

**Аргументы**

```
# file: reviews/scratch/stage0-1b/s02_scope.py
"""Stage 0-1b review: scope - renames inside the period, duplicate raion names, Kyiv levels. Read-only."""
import pandas as pd

from alerts.config import ROOT, load_config, ts
from alerts.ingest.vadimkin import load_official

cfg = load_config()
df = load_official(ROOT / cfg['dataset']['path'], cfg['dataset']['sha256'])
ws, de = ts(cfg['periods']['work_start']), ts(cfg['data_end'])
te = ts(cfg['periods']['train_end'])
per = df[(df['started_at'] < de) & (df['finished_at'] > ws)]

r = per[per['level'] == 'raion']
g = r.groupby(['oblast', 'raion'])['started_at'].agg(['min', 'max', 'size']).reset_index()
print('raion locations in period:', len(g))
# locations that start late or end early (possible rename or appearance)
late = g[g['min'] > ws + pd.Timedelta(days=14)]
early = g[g['max'] < de - pd.Timedelta(days=14)]
print('locations whose first record is >14 days after work_start:\n', late.to_string())
print('locations whose last record is >14 days before data_end:\n', early.to_string())

# same raion name in different oblasts (whole file and period)
for name, d in [('all', df[df['level'] == 'raion']), ('period', r)]:
    m = d.groupby('raion')['oblast'].nunique()
    print(name, 'raion names in >1 oblast:', m[m > 1].to_dict())
# near-identical names within an oblast (normalised)
norm = lambda s: s.str.lower().str.replace(r"[^a-z]", '', regex=True)
gg = g.assign(n=norm(g['raion']))
print('normalised collisions in period:', gg[gg.duplicated(['oblast', 'n'], keep=False)].to_string())
# all raion names in the whole file per oblast: renamed variants over time
allr = df[df['level'] == 'raion'].groupby(['oblast', 'raion'])['started_at'].agg(['min', 'max', 'size']).reset_index()
print('raion locations all time:', len(allr))
notin = allr.merge(g[['oblast', 'raion']], how='left', indicator=True)
print('raion locations outside the period only:\n', notin[notin['_merge'] == 'left_only'].to_string())
print('raions per oblast in period:', 
… [обрезано: показано 2000 из 3158 символов]
```

**Результат**

```
File created successfully at: d:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage0-1b\s02_scope.py (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Bash: Run scope checks for renames and Kyiv · 20:22</summary>

**Аргументы**

```bash
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage0-1b/s02_scope.py
```

**Результат**

```
raion locations in period: 118
locations whose first record is >14 days after work_start:
 Empty DataFrame
Columns: [oblast, raion, min, max, size]
Index: []
locations whose last record is >14 days before data_end:
                       oblast                      raion                       min                       max  size
27   Ivano-Frankivska oblast    Ivano-Frankivskyi raion 2025-11-07 21:25:01+00:00 2026-08-07 14:46:23+00:00    96
28   Ivano-Frankivska oblast             Kaluskyi raion 2025-11-07 21:26:55+00:00 2026-08-07 14:46:23+00:00    92
29   Ivano-Frankivska oblast          Kolomyiskyi raion 2025-11-07 21:26:55+00:00 2026-08-07 14:46:23+00:00    91
30   Ivano-Frankivska oblast            Kosivskyi raion 2025-11-07 21:25:01+00:00 2026-08-07 14:46:23+00:00    95
31   Ivano-Frankivska oblast       Nadvirnianskyi raion 2025-11-07 21:26:55+00:00 2026-08-07 14:46:23+00:00    92
32   Ivano-Frankivska oblast        Verkhovynskyi raion 2025-11-07 21:27:01+00:00 2026-08-07 14:46:23+00:00    94
59            Lvivska oblast     Chervonohradskyi raion 2025-11-07 21:26:55+00:00 2026-08-07 14:45:56+00:00    93
60            Lvivska oblast         Drohobytskyi raion 2025-11-07 21:25:40+00:00 2026-08-07 14:45:56+00:00    87
61            Lvivska oblast             Lvivskyi raion 2025-11-07 21:25:55+00:00 2026-08-07 14:45:56+00:00    94
62            Lvivska oblast           Sambirskyi raion 2025-11-07 21:25:45+00:00 2026-08-07 14:45:56+00:00    87
63            Lvivska oblast            Stryiskyi raion 2025-11-07 21:26:01+00:00 2026-08-07 14:45:56+00:00    93
64            Lvivska oblast          Yavorivskyi raion 2025-11-07 21:24:58+00:00 2026-08-07 14:45:56+00:00    88
65            Lvivska oblast         Zolochivskyi raion 2025-11-07 21:24:52+00:00 2026-08-07 14:45:56+00:00    95
102          Volynska oblast  Volodymyr-Volynskyi raion 2025-11-07 21:26:55+00:00 2026-08-07 14:46:04+00:00    91
103       Zakarpatska oblast          Berehivskyi raion 2025-11-07 21:24:32+00:00 2026-08-07 14:46:02+00:00    88
104       Zakarpatska oblast            Khustskyi raion 2025-11-07 21:24:39+00:00 2026-08-07 14:46:02+00:00    89
105       Zakarpatska oblast         Mukachivskyi raion 2025-11-07 21:24:33+00:00 2026-08-07 14:46:02+00:00    88
106       Zakarpatska oblast           Rakhivskyi raion 2025-11-07 21:24:32+00:00 2026-08-07 14:46:02+00:00    88
107       Zakarpatska oblast          Tiachivskyi raion 2025-11-07 21:24:33+00:00 2026-08-07 14:46:02+00:00    89
108       Zakarpatska oblast         Uzhhorodskyi raion 2025-11-07 21:24:39+00:00 2026-08-07 14:46:02+00:00    88
all raion names in >1 oblast: {}
period raion names in >1 oblast: {}
normalised collisions in period: Empty DataFrame
Columns: [oblast, raion, min, max, size, n]
Index: []
raion locations all time: 118
raion locations outside the period only:
 Empty DataFrame
Columns: [oblast, raion, min, max, size, _merge]
Index: []
raions per oblast in period: {'Che
… [обрезано: показано 3000 из 4489 символов]
```

</details>

<details><summary>🔧 Bash: List dataset repo and read legacy_states · 20:22</summary>

**Аргументы**

```bash
ls dataset_repo dataset_repo/processors dataset_repo/datasets; cat dataset_repo/processors/legacy_states.py | head -80
```

**Результат**

```
dataset_repo:
LICENSE
README.md
config.py.EXAMPLE
datasets
example
process.py
processors
pyproject.toml
requirements.txt

dataset_repo/datasets:
README.md
official_data_en.csv
official_data_uk.csv
volunteer_data_en.csv
volunteer_data_uk.csv

dataset_repo/processors:
__init__.py
legacy_states.py
official_channel_processor.py
pkl
states.json
tg_dataclasses.py
volunteer_etryvoga_processor.py
"""
Mapper for legacy state names to new state names.

This module provides a function to map old community and raion names
from states_legacy.json to new names in states.json.
"""

from typing import Optional, Tuple


# Mapping of renamed raions: (oblast, old_raion) -> new_raion
_RAION_RENAMES = {
    ("Дніпропетровська область", "Новомосковський район"): "Самарівський район",
    ("Житомирська область", "Новоград-Волинський район"): "Звягельський район",
}

# Mapping of renamed communities: (oblast, raion, old_community) -> new_community
_COMMUNITY_RENAMES = {
    ("Сумська область", "Сумський район", "Миколаївська сільська територіальна громада"): "Миколаївська територіальна громада",
}


def get_new_name(
    oblast: str,
    raion: str,
    community: Optional[str] = None
) -> Optional[Tuple[str, Optional[str]]]:
    """
    Map old raion and community names to their new names.

    Args:
        oblast: The oblast (state) name.
        raion: The raion (district) name.
        community: The community name (optional).

    Returns:
        A tuple (new_raion, new_community) if either raion or community has been renamed.
        Returns None if no renaming is needed.

        If only raion was renamed, new_community will be the same as input community.
        If only community was renamed, new_raion will be the same as input raion.
    """
    new_raion = _RAION_RENAMES.get((oblast, raion))

    new_community = None
    if community is not None:
        # Use the new raion name if it exists, otherwise use original
        lookup_raion = new_raion if new_raion else raion
        new_community = _COMMUNITY_RENAMES.get((oblast, lookup_raion, community))

        # Also try with the original raion name in case community rename was recorded with old raion
        if new_community is None:
            new_community = _COMMUNITY_RENAMES.get((oblast, raion, community))

    # Return tuple if any renaming occurred
    if new_raion is not None or new_community is not None:
        return (
            new_raion if new_raion else raion,
            new_community if new_community else community
        )

    return None
```

</details>

<details><summary>🔧 Bash: Search processor states.json for renamed raions · 20:22</summary>

**Аргументы**

```bash
python - <<'EOF'
import json
s=json.load(open('dataset_repo/processors/states.json',encoding='utf-8'))
for st in s['states']:
    for d in st['districts']:
        n=d['districtName']
        if any(k in n for k in ['Шепт','Червоноград','Берестин','Красноград','Володимир','Самарів','Новомосков','Звягель','Новоград']):
            print(st['stateName'], '|', n)
print(len(s['states']), sum(len(st['districts']) for st in s['states']))
EOF
```

**Результат** (ошибка)

```
Exit code 1
Traceback (most recent call last):
  File "<stdin>", line 7, in <module>
  File "D:\Soft\miniconda\Lib\encodings\cp1252.py", line 19, in encode
    return codecs.charmap_encode(input,self.errors,encoding_table)[0]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
UnicodeEncodeError: 'charmap' codec can't encode characters in position 0-8: character maps to <undefined>
```

</details>

<details><summary>🔧 Bash: Search states.json for renamed raions with utf-8 · 20:23</summary>

**Аргументы**

```bash
PYTHONIOENCODING=utf-8 python - <<'EOF'
import json
s=json.load(open('dataset_repo/processors/states.json',encoding='utf-8'))
for st in s['states']:
    for d in st['districts']:
        n=d['districtName']
        if any(k in n for k in ['Шепт','Червоноград','Берестин','Красноград','Володимир','Самарів','Новомосков','Звягель','Новоград']):
            print(st['stateName'], '|', n)
print(len(s['states']), sum(len(st['districts']) for st in s['states']))
EOF
```

**Результат**

```
Волинська область | Володимир-Волинський район
Дніпропетровська область | Новомосковський район
Житомирська область | Новоград-Волинський район
Львівська область | Червоноградський район
Харківська область | Красноградський район
25 122
```

</details>

<details><summary>🔧 Bash: Inspect volunteer dataset header and size · 20:23</summary>

**Аргументы**

```bash
head -3 dataset_repo/datasets/volunteer_data_en.csv; wc -l dataset_repo/datasets/volunteer_data_en.csv; git -C dataset_repo log -1 --format='%h %ci' -- datasets/volunteer_data_en.csv
```

**Результат**

```
region,started_at,finished_at,naive
Kyiv City,2022-02-25 16:36:22+00:00,2022-02-25 17:06:22+00:00,True
Cherkaska oblast,2022-02-25 18:36:21+00:00,2022-02-25 19:32:11+00:00,False
111004 dataset_repo/datasets/volunteer_data_en.csv
58ee75b 2026-09-08 03:44:23 +0000
```

</details>

<details><summary>🔧 Write: reviews/scratch/stage0-1b/s03_west_gap.py · 20:23</summary>

**Аргументы**

```
# file: reviews/scratch/stage0-1b/s03_west_gap.py
"""Stage 0-1b review: western raions silent from 2026-08-07 to the end. Real quiet or lost posts?

Compares the official raion series with the volunteer oblast-level series (same snapshot) per oblast.
Read-only.
"""
import pandas as pd

from alerts.config import ROOT, load_config, ts
from alerts.ingest.vadimkin import load_official

cfg = load_config()
df = load_official(ROOT / cfg['dataset']['path'], cfg['dataset']['sha256'])
ws, de = ts(cfg['periods']['work_start']), ts(cfg['data_end'])
vol = pd.read_csv(ROOT / 'dataset_repo/datasets/volunteer_data_en.csv')
for c in ['started_at', 'finished_at']:
    vol[c] = pd.to_datetime(vol[c], utc=True)
vol = vol.drop_duplicates()

r = df[(df['level'] == 'raion') & (df['started_at'] >= ws) & (df['started_at'] < de)]

# 1. longest gap between consecutive starts per raion, and where it sits
r = r.sort_values(['oblast', 'raion', 'started_at'])
r['gap_d'] = r.groupby(['oblast', 'raion'])['started_at'].diff().dt.total_seconds() / 86400
last = r.groupby(['oblast', 'raion'])['started_at'].max()
tail_gap = (de - last).dt.total_seconds() / 86400
mx = r.groupby(['oblast', 'raion'])['gap_d'].max()
t = pd.DataFrame({'max_inner_gap_d': mx.round(1), 'tail_gap_d': tail_gap.round(1)})
print(t.sort_values('tail_gap_d', ascending=False).head(25).to_string())

# 2. per oblast: official raion starts vs volunteer oblast starts, by period, Jul-Sep 2026
bins = [ts('2026-06-01T00:00:00Z'), ts('2026-07-01T00:00:00Z'), ts('2026-07-13T00:00:00Z'),
        ts('2026-08-07T00:00:00Z'), ts('2026-08-10T00:00:00Z'), ts('2026-09-07T00:00:00Z')]
lab = ['Jun', 'Jul1-12', 'Jul13-Aug6', 'Aug7-9', 'Aug10-Sep6(test)']
west = ['Lvivska oblast', 'Ivano-Frankivska oblast', 'Zakarpatska oblast', 'Volynska oblast',
        'Ternopilska oblast', 'Chernivetska oblast', 'Rivnenska oblast', 'Khmelnytska oblast']
rows = []
for ob in west:
    o = r[r['oblast'] == ob]
    # official: distinct start minutes of any raion of the 
… [обрезано: показано 2000 из 3050 символов]
```

**Результат**

```
File created successfully at: d:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage0-1b\s03_west_gap.py (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Bash: Compare western raions with volunteer data · 20:23</summary>

**Аргументы**

```bash
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage0-1b/s03_west_gap.py
```

**Результат**

```
max_inner_gap_d  tail_gap_d
oblast                  raion                                                 
Ivano-Frankivska oblast Verkhovynskyi raion                   24.1        30.4
                        Nadvirnianskyi raion                  24.1        30.4
                        Kosivskyi raion                       24.1        30.4
                        Ivano-Frankivskyi raion               24.1        30.4
                        Kolomyiskyi raion                     24.1        30.4
                        Kaluskyi raion                        24.1        30.4
Zakarpatska oblast      Mukachivskyi raion                    33.4        30.4
Lvivska oblast          Stryiskyi raion                       24.1        30.4
Zakarpatska oblast      Tiachivskyi raion                     33.4        30.4
                        Uzhhorodskyi raion                    33.4        30.4
                        Berehivskyi raion                     33.4        30.4
                        Khustskyi raion                       33.4        30.4
Volynska oblast         Volodymyr-Volynskyi raion             24.1        30.4
Zakarpatska oblast      Rakhivskyi raion                      33.4        30.4
Lvivska oblast          Sambirskyi raion                      24.1        30.4
                        Chervonohradskyi raion                24.1        30.4
                        Yavorivskyi raion                     24.1        30.4
                        Zolochivskyi raion                    24.1        30.4
                        Lvivskyi raion                        24.1        30.4
                        Drohobytskyi raion                    24.1        30.4
Volynska oblast         Kovelskyi raion                       24.1         9.9
Ternopilska oblast      Chortkivskyi raion                    21.8         3.9
                        Ternopilskyi raion                    21.8         3.9
                        Kremenetskyi raion                    21.8         3.9
Rivnenska oblast        Varaskyi raion                        24.0         2.9
oblast                Lvivska oblast  Ivano-Frankivska oblast  Zakarpatska oblast  Volynska oblast  Ternopilska oblast  Chernivetska oblast  Rivnenska oblast  Khmelnytska oblast
off Jun                           12                        9                   9               25                  10                   14                49                  21
off Jul1-12                        1                        1                   0                2                   3                    3                 5                   6
off Jul13-Aug6                     2                        3                   2                2                   2                    3                 4                   3
off Aug7-9                         1                        1                   1                1                   1                    1                 4                  
… [обрезано: показано 3000 из 7920 символов]
```

</details>

<details><summary>🔧 Write: reviews/scratch/stage0-1b/s04_west_monthly.py · 20:24</summary>

**Аргументы**

```
# file: reviews/scratch/stage0-1b/s04_west_monthly.py
"""Stage 0-1b review: official raion posts vs volunteer oblast alerts by month, western oblasts. Read-only.

Official: distinct start minutes over the raions of the oblast (one post = one minute).
Volunteer: starts of the oblast series. Also: share of volunteer starts that have an official start of
the same oblast within +-15 min.
"""
import numpy as np
import pandas as pd

from alerts.config import ROOT, load_config, ts
from alerts.ingest.vadimkin import load_official
from alerts.timeutil import to_sec

cfg = load_config()
df = load_official(ROOT / cfg['dataset']['path'], cfg['dataset']['sha256'])
ws, de = ts(cfg['periods']['work_start']), ts(cfg['data_end'])
vol = pd.read_csv(ROOT / 'dataset_repo/datasets/volunteer_data_en.csv').drop_duplicates()
for c in ['started_at', 'finished_at']:
    vol[c] = pd.to_datetime(vol[c], utc=True).dt.as_unit('s')
r = df[(df['level'] == 'raion') & (df['started_at'] >= ws) & (df['started_at'] < de)]
vol = vol[(vol['started_at'] >= ws) & (vol['started_at'] < de)]

obs = ['Lvivska oblast', 'Volynska oblast', 'Ivano-Frankivska oblast', 'Zakarpatska oblast',
       'Ternopilska oblast', 'Rivnenska oblast', 'Kharkivska oblast', 'Kyivska oblast']
for ob in obs:
    om = r.loc[r['oblast'] == ob, 'started_at'].dt.floor('min').drop_duplicates()
    v = vol.loc[vol['region'] == ob, 'started_at']
    o_s = np.sort(to_sec(om))
    v_s = to_sec(v)
    j = np.searchsorted(o_s, v_s)
    near = np.zeros(len(v_s), bool)
    for k in (j - 1, j):
        kk = np.clip(k, 0, len(o_s) - 1)
        near |= (np.abs(o_s[kk] - v_s) <= 900) if len(o_s) else False
    month = v.dt.strftime('%Y-%m')
    t = pd.DataFrame({'off': om.dt.strftime('%Y-%m').value_counts(),
                      'vol': month.value_counts(),
                      'vol_matched': month[near].value_counts()}).fillna(0).astype(int).sort_index()
    print(ob)
    print(t.T.to_string())

```

**Результат**

```
File created successfully at: d:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage0-1b\s04_west_monthly.py (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Bash: Monthly official vs volunteer counts by oblast · 20:24</summary>

**Аргументы**

```bash
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage0-1b/s04_west_monthly.py
```

**Результат**

```
Lvivska oblast
started_at   2025-11  2025-12  2026-01  2026-02  2026-03  2026-04  2026-05  2026-06  2026-07  2026-08  2026-09
off               23       16       16       27       19       13       17       12        2        2        0
vol              106       88       44       59       68       55       61       61      103      141       37
vol_matched       10        9       11       14       13        6       13       11        1        2        0
Volynska oblast
started_at   2025-11  2025-12  2026-01  2026-02  2026-03  2026-04  2026-05  2026-06  2026-07  2026-08  2026-09
off               11       21       30       39       15       14       21       25        3        6        6
vol               65       77       87       92      114       95      128      112      116      105       22
vol_matched        8        9       15       22       11        8       17       16        2        4        4
Ivano-Frankivska oblast
started_at   2025-11  2025-12  2026-01  2026-02  2026-03  2026-04  2026-05  2026-06  2026-07  2026-08  2026-09
off               20       10        9       16       13       15       20        9        2        3        0
vol               13       11        9       16       12        8       15       10        2        2        1
vol_matched       12        8        9       13       10        7       13        9        1        1        0
Zakarpatska oblast
started_at   2025-11  2025-12  2026-01  2026-02  2026-03  2026-04  2026-05  2026-06  2026-07  2026-08
off               18        9        9       13       10        9       15        9        1        2
vol               12        9        9       13       10        8       15        9        1        0
vol_matched       12        9        9       12       10        7       14        9        1        0
Ternopilska oblast
started_at   2025-11  2025-12  2026-01  2026-02  2026-03  2026-04  2026-05  2026-06  2026-07  2026-08  2026-09
off               13       10       12       16       16        9       16       10        4        7        2
vol               14       10       12       14       15        7       15        9        4        4        5
vol_matched       11        8       12       10       12        5       12        8        3        3        0
Rivnenska oblast
started_at   2025-11  2025-12  2026-01  2026-02  2026-03  2026-04  2026-05  2026-06  2026-07  2026-08  2026-09
off               19       24       54       53       22       14       47       49        8       16       13
vol               14       15       34       34       14       10       30       33        7       17        8
vol_matched       12       12       26       26       13        8       22       26        6       12        4
Kharkivska oblast
started_at   2025-11  2025-12  2026-01  2026-02  2026-03  2026-04  2026-05  2026-06  2026-07  2026-08  2026-09
off              487      593      677      683      966      933     1083     1206     1141     1194
… [обрезано: показано 3000 из 3697 символов]
```

</details>

<details><summary>🔧 Write: reviews/scratch/stage0-1b/s05_clones.py · 20:24</summary>

**Аргументы**

```
# file: reviews/scratch/stage0-1b/s05_clones.py
"""Stage 0-1b review: clone groups (D07). Read-only, nothing saved.

1. minute-grid Jaccard (as in units.py) vs exact Jaccard in seconds, train period;
2. groups on train / val / test / whole period at thresholds 0.996, 0.997, 0.998;
3. transitivity: components whose member pairs are not all above the threshold.
"""
import numpy as np
import pandas as pd

from alerts.config import ROOT, load_config, ts
from alerts.ingest.vadimkin import load_official
from alerts.scope import LOC_KEY, ROLE_TARGET, select_scope
from alerts.spans import union
from alerts.units import _components, _minute_grid, _pair_similarity

cfg = load_config()
df = load_official(ROOT / cfg['dataset']['path'], cfg['dataset']['sha256'])
scope = select_scope(df, cfg, period=True)
target = scope[scope['role'] == ROLE_TARGET]
locs = target[LOC_KEY].drop_duplicates().sort_values(LOC_KEY).reset_index(drop=True)
p = cfg['periods']
P = {'train': (ts(p['work_start']), ts(p['train_end'])),
     'val': (ts(p['train_end']), ts(p['val_end'])),
     'test': (ts(p['val_end']), ts(cfg['data_end'])),
     'all': (ts(p['work_start']), ts(cfg['data_end']))}


def exact_pairs(t0, t1):
    rec = target[(target['started_at'] < t1) & (target['finished_at'] > t0)].copy()
    rec['start'] = rec['started_at'].where(rec['started_at'] > t0, t0)
    rec['end'] = rec['finished_at'].where(rec['finished_at'] < t1, t1)
    rec['loc'] = rec['oblast'] + '|' + rec['raion']
    u = union(rec[['loc', 'start', 'end']], 'loc')
    u['sec'] = (u['end'] - u['start']).dt.total_seconds()
    size = u.groupby('loc')['sec'].sum()
    out = {}
    for ob, g in locs.groupby('oblast'):
        names = (g['oblast'] + '|' + g['raion']).tolist()
        for a in range(len(names)):
            for b in range(a + 1, len(names)):
                both = u[u['loc'].isin([names[a], names[b]])].assign(k=0)
                uni = union(both, 'k')
                us = (uni['end'] - uni['start']).dt.total_seconds(
… [обрезано: показано 2000 из 4686 символов]
```

**Результат**

```
File created successfully at: d:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage0-1b\s05_clones.py (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Bash: Run clone stability and rounding analysis · 20:24</summary>

**Аргументы**

```bash
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage0-1b/s05_clones.py 2>&1 | tail -120
```

**Результат**

```
Khersonska oblast       Henicheskyi raion           Skadovskyi raion           0.99754  0.99926  0.99942  0.99787
Odeska oblast           Berezivskyi raion           Podilskyi raion            0.99688  0.99760  0.99301  0.99643
                        Podilskyi raion             Rozdilnianskyi raion       0.99606  0.99520  0.99218  0.99549
                        Berezivskyi raion           Rozdilnianskyi raion       0.99576  0.99554  0.99301  0.99538
Ternopilska oblast      Chortkivskyi raion          Kremenetskyi raion         0.99573  1.00000  1.00000  0.99595
Odeska oblast           Bolhradskyi raion           Izmailskyi raion           0.99511  0.99189  0.99289  0.99441
                        Bilhorod-Dnistrovskyi raion Bolhradskyi raion          0.99507  0.99459  0.99304  0.99476
                                                    Izmailskyi raion           0.99478  0.99385  0.99540  0.99472
Zakarpatska oblast      Khustskyi raion             Tiachivskyi raion          0.99123  1.00000  0.00000  0.99143
                                                    Uzhhorodskyi raion         0.99067  1.00000  0.00000  0.99089
Ivano-Frankivska oblast Kosivskyi raion             Verkhovynskyi raion        0.99001  1.00000  0.00000  0.99025
Ternopilska oblast      Kremenetskyi raion          Ternopilskyi raion         0.98852  1.00000  1.00000  0.98911
                        Chortkivskyi raion          Ternopilskyi raion         0.98460  1.00000  1.00000  0.98539
Zakarpatska oblast      Tiachivskyi raion           Uzhhorodskyi raion         0.98391  1.00000  0.00000  0.98429
Lvivska oblast          Drohobytskyi raion          Sambirskyi raion           0.98293  1.00000  0.00000  0.98334
Zakarpatska oblast      Rakhivskyi raion            Uzhhorodskyi raion         0.98255  1.00000  0.00000  0.98296
Ivano-Frankivska oblast Kaluskyi raion              Nadvirnianskyi raion       0.97645  1.00000  0.00000  0.97704
Zakarpatska oblast      Khustskyi raion             Rakhivskyi raion           0.97634  1.00000  0.00000  0.97689
Chernivetska oblast     Chernivetskyi raion         Vyzhnytskyi raion          0.97466  1.00000  0.00000  0.97026
Zakarpatska oblast      Rakhivskyi raion            Tiachivskyi raion          0.96829  1.00000  0.00000  0.96902
Ivano-Frankivska oblast Nadvirnianskyi raion        Verkhovynskyi raion        0.96816  1.00000  0.00000  0.96895
Vinnytska oblast        Mohyliv-Podilskyi raion     Zhmerynskyi raion          0.96711  0.99909  0.83610  0.96131
Ivano-Frankivska oblast Kosivskyi raion             Nadvirnianskyi raion       0.96428  1.00000  0.00000  0.96515
                        Kaluskyi raion              Verkhovynskyi raion        0.96203  1.00000  0.00000  0.96296
                                                    Kosivskyi raion            0.95513  1.00000  0.00000  0.95623
                        Kolomyiskyi raion           Nadvirnianskyi raion       0.95217  1.00000  0.00000  0.95333
          
… [обрезано: показано 3000 из 12466 символов]
```

</details>

<details><summary>🔧 Bash: Show head of clone analysis output · 20:25</summary>

**Аргументы**

```bash
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage0-1b/s05_clones.py 2>&1 | head -45
```

**Результат**

```
train thr=0.996: units=102 groups=['Berdianskyi+Melitopolskyi+Polohivskyi+Vasylivskyi+Zaporizkyi', 'Berehivskyi+Mukachivskyi', 'Berezivskyi+Podilskyi+Rozdilnianskyi', 'Henicheskyi+Kakhovskyi+Skadovskyi']
train thr=0.997: units=104 groups=['Berdianskyi+Melitopolskyi+Polohivskyi+Vasylivskyi+Zaporizkyi', 'Berehivskyi+Mukachivskyi', 'Henicheskyi+Kakhovskyi+Skadovskyi']
train thr=0.998: units=104 groups=['Berdianskyi+Melitopolskyi+Polohivskyi+Vasylivskyi+Zaporizkyi', 'Berehivskyi+Mukachivskyi', 'Henicheskyi+Kakhovskyi+Skadovskyi']
train: same-component pairs below 0.997: 0 
val   thr=0.996: units=79 groups=['Berdianskyi+Melitopolskyi+Polohivskyi+Vasylivskyi+Zaporizkyi', 'Berehivskyi+Khustskyi+Mukachivskyi+Rakhivskyi+Tiachivskyi+Uzhhorodskyi', 'Berezivskyi+Podilskyi', 'Chernivetskyi+Dnistrovskyi+Vyzhnytskyi', 'Chervonohradskyi+Drohobytskyi+Lvivskyi+Sambirskyi+Stryiskyi+Yavorivskyi+Zolochivskyi', 'Chortkivskyi+Kremenetskyi+Ternopilskyi', 'Dubenskyi+Varaskyi', 'Henicheskyi+Kakhovskyi+Skadovskyi', 'Kaluskyi+Kolomyiskyi+Kosivskyi+Nadvirnianskyi+Verkhovynskyi', 'Kamianets-Podilskyi+Khmelnytskyi', 'Kamin-Kashyrskyi+Kovelskyi+Lutskyi+Volodymyr-Volynskyi', 'Mohyliv-Podilskyi+Zhmerynskyi']
val   thr=0.997: units=79 groups=['Berdianskyi+Melitopolskyi+Polohivskyi+Vasylivskyi+Zaporizkyi', 'Berehivskyi+Khustskyi+Mukachivskyi+Rakhivskyi+Tiachivskyi+Uzhhorodskyi', 'Berezivskyi+Podilskyi', 'Chernivetskyi+Dnistrovskyi+Vyzhnytskyi', 'Chervonohradskyi+Drohobytskyi+Lvivskyi+Sambirskyi+Stryiskyi+Yavorivskyi+Zolochivskyi', 'Chortkivskyi+Kremenetskyi+Ternopilskyi', 'Dubenskyi+Varaskyi', 'Henicheskyi+Kakhovskyi+Skadovskyi', 'Kaluskyi+Kolomyiskyi+Kosivskyi+Nadvirnianskyi+Verkhovynskyi', 'Kamianets-Podilskyi+Khmelnytskyi', 'Kamin-Kashyrskyi+Kovelskyi+Lutskyi+Volodymyr-Volynskyi', 'Mohyliv-Podilskyi+Zhmerynskyi']
val   thr=0.998: units=80 groups=['Berdianskyi+Melitopolskyi+Polohivskyi+Vasylivskyi+Zaporizkyi', 'Berehivskyi+Khustskyi+Mukachivskyi+Rakhivskyi+Tiachivskyi+Uzhhorodskyi', 'Chernivetskyi+Dnistrovskyi+Vyzhnytskyi', 'Chervonohradskyi+Drohobytskyi+Lvivskyi+Sambirskyi+Stryiskyi+Yavorivskyi+Zolochivskyi', 'Chortkivskyi+Kremenetskyi+Ternopilskyi', 'Dubenskyi+Varaskyi', 'Henicheskyi+Kakhovskyi+Skadovskyi', 'Kaluskyi+Kolomyiskyi+Kosivskyi+Nadvirnianskyi+Verkhovynskyi', 'Kamianets-Podilskyi+Khmelnytskyi', 'Kamin-Kashyrskyi+Kovelskyi+Lutskyi+Volodymyr-Volynskyi', 'Mohyliv-Podilskyi+Zhmerynskyi']
val: same-component pairs below 0.997: 0 
test  thr=0.996: units=103 groups=['Berdianskyi+Melitopolskyi+Polohivskyi+Vasylivskyi+Zaporizkyi', 'Chortkivskyi+Kremenetskyi+Ternopilskyi', 'Henicheskyi+Kakhovskyi+Skadovskyi']
test  thr=0.997: units=103 groups=['Berdianskyi+Melitopolskyi+Polohivskyi+Vasylivskyi+Zaporizkyi', 'Chortkivskyi+Kremenetskyi+Ternopilskyi', 'Henicheskyi+Kakhovskyi+Skadovskyi']
test  thr=0.998: units=103 groups=['Berdianskyi+Melitopolskyi+Polohivskyi+Vasylivskyi+Zaporizkyi', 'Chortkivskyi+Kremenetskyi+Ternopilskyi', 'Henicheskyi+Kakhovskyi+Skadovskyi']
test: sa
… [обрезано: показано 3000 из 6932 символов]
```

</details>

<details><summary>🔧 Write: reviews/scratch/stage0-1b/s06_odesa_seconds.py · 20:25</summary>

**Аргументы**

```
# file: reviews/scratch/stage0-1b/s06_odesa_seconds.py
"""Independent check: Jaccard of Odesa pairs on the train period with a 1-second grid. Read-only.

Also: alternative minute discretisations (ceil of the end, round both ends) for the same pair, and
the diff of the two series in minutes and seconds.
"""
import numpy as np

from alerts.config import ROOT, load_config, ts
from alerts.ingest.vadimkin import load_official
from alerts.scope import ROLE_TARGET, select_scope
from alerts.timeutil import to_sec

cfg = load_config()
df = load_official(ROOT / cfg['dataset']['path'], cfg['dataset']['sha256'])
scope = select_scope(df, cfg, period=True)
t0, t1 = ts(cfg['periods']['work_start']), ts(cfg['periods']['train_end'])
od = scope[(scope['role'] == ROLE_TARGET) & (scope['oblast'] == 'Odeska oblast')
           & (scope['started_at'] < t1) & (scope['finished_at'] > t0)]
n = int(to_sec(t1) - to_sec(t0))
base = to_sec(t0)


def series(raion, unit, start_fn, end_fn):
    r = od[od['raion'] == raion]
    s = np.clip(start_fn(to_sec(r['started_at']) - base, unit), 0, n // unit)
    e = np.clip(end_fn(to_sec(r['finished_at']) - base, unit), 0, n // unit)
    d = np.zeros(n // unit + 1, np.int32)
    np.add.at(d, s[s < e], 1)
    np.add.at(d, e[s < e], -1)
    return np.cumsum(d[:-1]) > 0


floor = lambda x, u: x // u
ceil = lambda x, u: -((-x) // u)
rnd = lambda x, u: (x + u // 2) // u
pairs = [('Berezivskyi raion', 'Podilskyi raion'), ('Podilskyi raion', 'Rozdilnianskyi raion'),
         ('Berezivskyi raion', 'Rozdilnianskyi raion')]
for a, b in pairs:
    out = []
    for name, unit, sf, ef in [('seconds', 1, floor, floor), ('minute floor/floor (code)', 60, floor, floor),
                               ('minute floor/ceil', 60, floor, ceil), ('minute round/round', 60, rnd, rnd)]:
        A, B = series(a, unit, sf, ef), series(b, unit, sf, ef)
        j = (A & B).sum() / (A | B).sum()
        out.append(f'{name}: {j:.5f} (A^B {(A ^ B).sum() * unit / 3600:.1f} h)')
    print(a
… [обрезано: показано 2000 из 2031 символов]
```

**Результат**

```
File created successfully at: d:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage0-1b\s06_odesa_seconds.py (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Bash: Verify Odesa Jaccard with second grid · 20:25</summary>

**Аргументы**

```bash
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage0-1b/s06_odesa_seconds.py
```

**Результат**

```
Berezivskyi raion - Podilskyi raion | seconds: 0.99735 (A^B 1.3 h); minute floor/floor (code): 0.99688 (A^B 1.5 h); minute floor/ceil: 0.99687 (A^B 1.6 h); minute round/round: 0.99764 (A^B 1.1 h)
Podilskyi raion - Rozdilnianskyi raion | seconds: 0.99637 (A^B 1.8 h); minute floor/floor (code): 0.99606 (A^B 1.9 h); minute floor/ceil: 0.99603 (A^B 2.0 h); minute round/round: 0.99675 (A^B 1.6 h)
Berezivskyi raion - Rozdilnianskyi raion | seconds: 0.99596 (A^B 2.0 h); minute floor/floor (code): 0.99576 (A^B 2.1 h); minute floor/ceil: 0.99573 (A^B 2.1 h); minute round/round: 0.99617 (A^B 1.9 h)
```

</details>

<details><summary>🔧 Write: reviews/scratch/stage0-1b/s07_outage_events.py · 20:26</summary>

**Аргументы**

```
# file: reviews/scratch/stage0-1b/s07_outage_events.py
"""Stage 0-1b review: events around the D15 outage and the effect of non-post events. Read-only.

Events in detect_outages are starts and ends of every record. A processor-invented end (start + 1 h,
duration exactly 3600 s, next start of the location > 3 h later) is not a channel post.
"""
import pandas as pd

from alerts.config import ROOT, load_config, ts
from alerts.ingest.vadimkin import load_official
from alerts.mask import detect_outages

cfg = load_config()
df = load_official(ROOT / cfg['dataset']['path'], cfg['dataset']['sha256'])
key = ['oblast', 'raion', 'hromada', 'level']
d = df.copy()
for c in ['raion', 'hromada']:
    d[c] = d[c].fillna('')
d = d.sort_values(key + ['started_at'])
d['next_start'] = d.groupby(key)['started_at'].shift(-1)
d['fake'] = (d['duration'] == 3600) & ((d['next_start'] - d['started_at']) > pd.Timedelta(hours=3))
d['fake_any'] = d['duration'] == 3600

ev = pd.concat([
    pd.DataFrame({'t': d['started_at'], 'kind': 'start', 'fake': False, 'dur_h': d['duration'] / 3600,
                  'level': d['level'], 'oblast': d['oblast'], 'raion': d['raion']}),
    pd.DataFrame({'t': d['finished_at'], 'kind': 'end', 'fake': d['fake'], 'dur_h': d['duration'] / 3600,
                  'level': d['level'], 'oblast': d['oblast'], 'raion': d['raion']}),
]).sort_values('t')

lo, hi = ts('2026-08-29T03:00:00Z'), ts('2026-09-02T14:30:00Z')
w = ev[(ev['t'] >= lo) & (ev['t'] <= hi)]
g = w.groupby(['t', 'kind', 'fake']).agg(n=('oblast', 'size'), dur_h=('dur_h', 'max'),
                                         lvl=('level', lambda s: ','.join(sorted(set(s)))),
                                         ob=('oblast', lambda s: ','.join(sorted(set(s))[:3]))).reset_index()
print(g.to_string())

print('\nDetected outages (code):')
print(detect_outages(df, cfg).to_string())

# Same detection without invented ends (exclude ends of 3600-s records whose next start is > 3 h later)
real = ev[~ev['fake']]['t'].
… [обрезано: показано 2000 из 3010 символов]
```

**Результат**

```
File created successfully at: d:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage0-1b\s07_outage_events.py (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Bash: Inspect events around the channel outage · 20:26</summary>

**Аргументы**

```bash
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage0-1b/s07_outage_events.py
```

**Результат**

```
t   kind   fake  n       dur_h      lvl                                    ob
0   2026-08-29 03:02:04+00:00    end  False  7    0.459722    raion                         Odeska oblast
1   2026-08-29 03:03:36+00:00    end  False  4    0.479444    raion                    Mykolaivska oblast
2   2026-08-29 03:13:54+00:00    end  False  1    0.658611    raion                      Cherkaska oblast
3   2026-08-29 03:13:57+00:00    end  False  1    2.285278    raion                   Chernihivska oblast
4   2026-08-29 03:13:58+00:00    end  False  1    0.658611    raion                      Cherkaska oblast
5   2026-08-29 03:14:01+00:00    end  False  4    1.488056    raion                  Kirovohradska oblast
6   2026-08-29 03:14:05+00:00    end  False  1    2.695278    raion                   Chernihivska oblast
7   2026-08-29 03:19:49+00:00    end   True  1    1.000000    raion                     Khersonska oblast
8   2026-08-29 03:20:20+00:00    end  False  1    4.030278    raion                     Kharkivska oblast
9   2026-08-29 03:20:25+00:00    end  False  1    2.939167    raion                     Kharkivska oblast
10  2026-08-29 03:21:38+00:00  start  False  1    1.000000    raion                    Mykolaivska oblast
11  2026-08-29 03:21:47+00:00    end  False  1    0.791944    raion                     Kharkivska oblast
12  2026-08-29 03:22:01+00:00    end  False  1    1.346389    raion                        Kyivska oblast
13  2026-08-29 03:22:04+00:00    end  False  1    0.736389    raion                         Sumska oblast
14  2026-08-29 03:22:15+00:00    end  False  1    0.743333    raion                         Sumska oblast
15  2026-08-29 03:22:22+00:00    end  False  1    0.799722    raion                Dnipropetrovska oblast
16  2026-08-29 03:22:27+00:00    end  False  2    0.801111    raion  Dnipropetrovska oblast,Sumska oblast
17  2026-08-29 03:22:32+00:00    end  False  1    0.802500    raion                Dnipropetrovska oblast
18  2026-08-29 03:22:37+00:00    end  False  1    0.803889    raion                Dnipropetrovska oblast
19  2026-08-29 03:27:56+00:00  start  False  1    1.000000    raion                    Mykolaivska oblast
20  2026-08-29 03:29:10+00:00  start  False  1    0.735556    raion                   Chernihivska oblast
21  2026-08-29 03:31:26+00:00    end  False  1    0.894722    raion                         Sumska oblast
22  2026-08-29 03:33:20+00:00  start  False  1    0.664722    raion                   Chernihivska oblast
23  2026-08-29 03:34:52+00:00    end   True  4    1.000000    raion                     Khersonska oblast
24  2026-08-29 03:48:29+00:00  start  False  1    1.000000    raion                         Sumska oblast
25  2026-08-29 03:52:17+00:00    end  False  1    8.895278  hromada                Dnipropetrovska oblast
26  2026-08-29 03:55:50+00:00  start  False  1  105.954167    raion                Dnipropetrovska oblast
27  2026-08-29 04:08:37+00:00   
… [обрезано: показано 3000 из 13826 символов]
```

</details>

<details><summary>🔧 Bash: Read grid module to understand mask use · 20:27</summary>

**Аргументы**

```bash
sed -n 1,200p src/alerts/grid.py | cat -n | head -220
```

**Результат**

```
1	"""Stage 3: hourly grid of (unit, t) and binary targets (PLAN stage 3; D10, D12, D16, D17).
     2	
     3	A row exists for a target unit at an hourly moment t in [warmup_end, data_end) when the unit is
     4	quiet at t. The status of every candidate (unit, t) is decided in this order:
     5	  alert          inside an episode by the recorded segments;
     6	  bridged_pause  inside an episode only because a pause <= pause_merge_min was bridged (D12);
     7	  masked_*       inside a mask: outage (d), after_data_end (c), long_24h (a), fake_1h (b);
     8	  held_open      quiet by the records, but no all-clear had been seen yet (AlertHistory, D16):
     9	                 a real-time observer would not have asked for a forecast;
    10	  quiet          a row.
    11	
    12	y_h = 1 if an episode of the unit starts in (t, t+h]. y_h is missing (NA) when the window
    13	(t, t+h) reaches a mask whose start is not an event: (c) after data_end or (d) an outage; this
    14	selection depends on time only, not on the outcome. Windows that reach a mask of rule (a) or (b)
    15	keep their label: such a mask starts with a real alert start, so y_h = 1 is known (D10).
    16	"""
    17	import numpy as np
    18	import pandas as pd
    19	
    20	from alerts.config import ts
    21	from alerts.history import AlertHistory
    22	from alerts.intervals import episodes
    23	from alerts.mask import AFTER_END, FAKE_END, LONG, OUTAGE
    24	from alerts.scope import ROLE_TARGET
    25	from alerts.spans import count_in, covers, reaches, union
    26	from alerts.timeutil import to_sec
    27	
    28	STATUSES = ['quiet', 'alert', 'bridged_pause', 'masked_outage', 'masked_after_data_end',
    29	            'masked_long_24h', 'masked_fake_1h', 'held_open']
    30	_MASK_ORDER = [OUTAGE, AFTER_END, LONG, FAKE_END]   # precedence when masks overlap
    31	_UNLABELLED = [AFTER_END, OUTAGE]                    # masks whose start is not an event
    32	_KNOWN_START = [LONG, FAKE_END]                      # masks that start with a real alert start
    33	PARTS = ['train', 'val', 'test']
    34	
    35	
    36	def moments(cfg: dict) -> pd.DatetimeIndex:
    37	    """Hourly forecast moments from the end of the warm-up week to data_end (exclusive)."""
    38	    return pd.date_range(ts(cfg['periods']['warmup_end']), ts(cfg['data_end']), freq='h', inclusive='left')
    39	
    40	
    41	def part_of(t: pd.Series, cfg: dict) -> pd.Series:
    42	    """train / val / test by the moment t (D14)."""
    43	    p = cfg['periods']
    44	    edges = [ts(p['warmup_end']), ts(p['train_end']), ts(p['val_end']), ts(cfg['data_end'])]
    45	    # searchsorted, not pd.cut: a part may be empty (another source has no train or val, stage 8)
    46	    k = np.searchsorted(to_sec(pd.DatetimeIndex(edges)), to_sec(t), side='right')
    47	    labels = np.array(['before'] + PARTS + ['after'])
    48	    return pd.Series(labels[k], index=t.index)
    49	
    50	
    51	def build_grid(seen: pd.Da
… [обрезано: показано 3000 из 9166 символов]
```

</details>

<details><summary>🔧 Bash: Read intervals and mask use in history · 20:27</summary>

**Аргументы**

```bash
cat -n src/alerts/intervals.py && grep -n "outage\|mask" src/alerts/history.py | head -40
```

**Результат**

```
1	"""Unit-level alert intervals (stage 2; D11, D12, D16). Pure functions: nothing is written here.
     2	
     3	One table, two levels:
     4	  segment  maximal union of overlapping or touching source records of a unit (clones, D07;
     5	           overlaps, D11). Segments are the as-of truth for "is the unit under alert at t".
     6	  episode  segments separated by pauses <= pause_merge_min (D12). An episode is the alert the
     7	           target counts. Merging a pause needs the next start, so the episode END and the
     8	           "under alert" state inside a bridged pause come from the future (D16): never read
     9	           them as of t; use alerts.history.AlertHistory instead.
    10	
    11	`end_utc` is the recorded end. What a real-time observer saw is a separate table, `seen`
    12	(build_seen): an invented end start + 1 h is written only at the next start (alerts.processor),
    13	and an alert open longer than history.max_open_hours stops counting as active (D16, D19).
    14	AlertHistory reads the state from `seen`, never from end_utc.
    15	"""
    16	import logging
    17	
    18	import numpy as np
    19	import pandas as pd
    20	
    21	from alerts.mask import UNCERTAIN_REASONS
    22	from alerts.scope import attach_units
    23	from alerts.spans import merge_labels, overlaps, union
    24	from alerts.timeutil import to_sec
    25	
    26	logger = logging.getLogger(__name__)
    27	
    28	INTERVAL_COLUMNS = ['unit_id', 'start_utc', 'end_utc', 'uncertain', 'episode', 'n_records']
    29	SEEN_COLUMNS = ['unit_id', 'start', 'end']
    30	
    31	
    32	def build_intervals(scope: pd.DataFrame, units: pd.DataFrame, masks: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    33	    """Segments of every unit with an episode id.
    34	
    35	    `uncertain`: the segment overlaps a mask of rules (a), (b) or (d), so its end is unreliable.
    36	    The flag is retrospective (it depends on the future) and must not become a feature.
    37	    """
    38	    rec = attach_units(scope, units)[['unit_id', 'started_at', 'finished_at']]
    39	    rec = rec.sort_values(['unit_id', 'started_at', 'finished_at']).reset_index(drop=True)
    40	    rec['uncertain'] = _overlaps_masks(rec, masks)
    41	
    42	    seg_id = merge_labels(rec, 'unit_id', 'started_at', 'finished_at')
    43	    seg = (rec.groupby(seg_id)
    44	              .agg(unit_id=('unit_id', 'first'), start_utc=('started_at', 'min'),
    45	                   end_utc=('finished_at', 'max'), uncertain=('uncertain', 'any'),
    46	                   n_records=('unit_id', 'size'))
    47	              .reset_index(drop=True))
    48	
    49	    pause = pd.Timedelta(minutes=cfg['thresholds']['pause_merge_min'])
    50	    seg['episode'] = merge_labels(seg, 'unit_id', 'start_utc', 'end_utc', gap=pause)
    51	
    52	    logger.info(f'{len(rec):,} records -> {len(seg):,} segments -> {seg["episode"].nunique():,} episodes')
… [обрезано: показано 3000 из 6255 символов]
```

</details>

<details><summary>🔧 Write: reviews/scratch/stage0-1b/s08_build_compare.py · 20:28</summary>

**Аргументы**

```
# file: reviews/scratch/stage0-1b/s08_build_compare.py
"""Stage 0-1b review: rebuild in memory, compare with saved tables; effect of the outage start
defined by the last real event (04:55:28) instead of an invented end (05:55:28). Nothing is saved.
"""
import pandas as pd

from alerts import store
from alerts.config import load_config, ts
from alerts.grid import build_grid
from alerts.intervals import build_intervals
from alerts.mask import OUTAGE, _stats
from alerts.pipeline import build_all

cfg = load_config()
art = build_all(cfg)

# 1. saved tables vs in-memory build
u_saved = store.load_units(cfg)
m_saved = store.load_masks(cfg)
u_mem = art.units[u_saved.columns].reset_index(drop=True)
print('units equal:', u_saved.equals(u_mem), len(u_saved), u_saved['unit_id'].nunique())
m_mem = art.masks.reset_index(drop=True)
print('masks equal:', m_saved.reset_index(drop=True).equals(m_mem), len(m_saved), len(m_mem))
print(m_saved['reason'].value_counts().to_dict())
pairs_saved = pd.read_csv('reports/high_sim_pairs.csv')
pm = art.pairs[art.pairs['jaccard'] >= cfg['thresholds']['similar_pairs_report']].reset_index(drop=True)
print('pairs equal:', len(pairs_saved) == len(pm) and (pairs_saved['jaccard'].round(12) == pm['jaccard'].round(12)).all())

# 2. outage start from the last real event
new_start = ts('2026-08-29T04:55:28Z')
m2 = art.masks.copy()
sel = (m2['reason'] == OUTAGE) & (m2['start'] == ts('2026-08-29T05:55:28Z'))
print('outage rows changed:', int(sel.sum()))
m2.loc[sel, 'start'] = new_start
iv2 = build_intervals(art.scope, art.units, m2, cfg)
g2, st2 = build_grid(art.seen, iv2, m2, art.units, cfg)
g1, st1 = art.grid, art.grid_stats
print('uncertain segments: before', int(art.intervals['uncertain'].sum()), 'after', int(iv2['uncertain'].sum()))
for h in cfg['horizons']:
    a, b = st1['horizons'][h], st2['horizons'][h]
    print(f"h={h}: rows {a['rows']} -> {b['rows']}; positives {a['positives']} -> {b['positives']}; "
          f"base test {a['base_rate']['test']:
… [обрезано: показано 2000 из 2471 символов]
```

**Результат**

```
File created successfully at: d:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage0-1b\s08_build_compare.py (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Bash: Rebuild tables and quantify outage shift effect · 20:28</summary>

**Аргументы**

```bash
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage0-1b/s08_build_compare.py 2>&1 | grep -v "^INFO"
```

**Результат**

```
Channel outage (D15): 2026-08-29 05:55:28+00:00 -> 2026-09-02 13:48:04+00:00 (4 days 07:52:36)
units equal: True 119 105
masks equal: True 392 392
{'long_24h': 111, 'outage': 105, 'after_data_end': 105, 'fake_1h': 71}
pairs equal: True
outage rows changed: 105
uncertain segments: before 183 after 183
h=1: rows {'train': 510642, 'val': 57865, 'test': 48332} -> {'train': 510642, 'val': 57865, 'test': 48262}; positives {'train': 45363, 'val': 7007, 'test': 6003} -> {'train': 45363, 'val': 7007, 'test': 5995}; base test 0.1242 -> 0.1242
h=3: rows {'train': 510642, 'val': 57865, 'test': 48028} -> {'train': 510642, 'val': 57865, 'test': 47954}; positives {'train': 106576, 'val': 15223, 'test': 12502} -> {'train': 106576, 'val': 15223, 'test': 12473}; base test 0.2603 -> 0.2601
h=6: rows {'train': 510642, 'val': 57865, 'test': 47525} -> {'train': 510642, 'val': 57865, 'test': 47431}; positives {'train': 163848, 'val': 21971, 'test': 17388} -> {'train': 163848, 'val': 21971, 'test': 17333}; base test 0.3659 -> 0.3654
grid rows (any label): 616909 -> 616839
masked % test: before {'long_24h': 2.7, 'fake_1h': 2.82, 'outage': 15.46, 'total': 15.93} after {'long_24h': 2.7, 'fake_1h': 2.82, 'outage': 15.61, 'total': 16.03}
```

</details>

<details><summary>🔧 Write: reviews/scratch/stage0-1b/s09_rules_ab.py · 20:29</summary>

**Аргументы**

```
# file: reviews/scratch/stage0-1b/s09_rules_ab.py
"""Stage 0-1b review: rules (a) and (b) details. Read-only.

- durations around 24 h and around 3600 s (coincidence rate of a genuine 1-h alert);
- 3600-s records not masked by (b): their next start;
- next start searched among raion records only vs among raion + hromada records of the same raion;
- renamed raions in the data.
"""
import pandas as pd

from alerts.config import ROOT, load_config, ts
from alerts.ingest.vadimkin import load_official
from alerts.scope import ROLE_TARGET, select_scope

cfg = load_config()
df = load_official(ROOT / cfg['dataset']['path'], cfg['dataset']['sha256'])
ws, de, te = ts(cfg['periods']['work_start']), ts(cfg['data_end']), ts(cfg['periods']['val_end'])
sa = select_scope(df, cfg, period=False)
sp = select_scope(df, cfg, period=True)
t = sp[sp['role'] == ROLE_TARGET]

print('raion names, Dnipro / Zhytomyr:',
      sorted(df.loc[(df['oblast'] == 'Dnipropetrovska oblast') & (df['level'] == 'raion'), 'raion'].unique()),
      sorted(df.loc[(df['oblast'] == 'Zhytomyrska oblast') & (df['level'] == 'raion'), 'raion'].unique()))

d = t['duration']
print('exactly 86400 s:', int((d == 86400).sum()), '; in (23h, 25h]:', int(((d > 23 * 3600) & (d <= 25 * 3600)).sum()),
      '; in (24h, 25h]:', int(((d > 24 * 3600) & (d <= 25 * 3600)).sum()))
print('long > 24 h in scope (target, period):', int((d > 86400).sum()))
near = d[(d >= 3590) & (d <= 3610)].value_counts().sort_index()
print('durations 3590..3610 s, target, period:', near.to_dict())
for lo, hi in [(3000, 3599), (3601, 4200)]:
    n = int(((d >= lo) & (d <= hi)).sum())
    print(f'mean count per second in [{lo},{hi}]: {n / (hi - lo + 1):.2f}')
dd = d[(d == 1800)]
print('exactly 1800 s:', len(dd), '; 1799/1801:', int((d == 1799).sum()), int((d == 1801).sum()))

# 3600-s records not flagged by (b)
f = t[t['duration'] == 3600]
print('3600-s target records in period:', len(f), 'flagged (b):', int(f['is_fake_end'].sum()))
nf = f[~f['is_fake_en
… [обрезано: показано 2000 из 3335 символов]
```

**Результат**

```
File created successfully at: d:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage0-1b\s09_rules_ab.py (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Bash: Check rules (a) and (b) details · 20:29</summary>

**Аргументы**

```bash
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage0-1b/s09_rules_ab.py
```

**Результат**

```
raion names, Dnipro / Zhytomyr: ['Dniprovskyi raion', 'Kamianskyi raion', 'Kryvorizkyi raion', 'Nikopolskyi raion', 'Pavlohradskyi raion', 'Samarivskyi raion', 'Synelnykivskyi raion'] ['Berdychivskyi raion', 'Korostenskyi raion', 'Zhytomyrskyi raion', 'Zviahelskyi raion']
exactly 86400 s: 0 ; in (23h, 25h]: 28 ; in (24h, 25h]: 10
long > 24 h in scope (target, period): 119
durations 3590..3610 s, target, period: {3590.0: 8, 3591.0: 5, 3592.0: 6, 3593.0: 3, 3594.0: 5, 3595.0: 6, 3596.0: 9, 3597.0: 5, 3598.0: 13, 3599.0: 6, 3600.0: 82, 3601.0: 5, 3602.0: 7, 3603.0: 5, 3604.0: 9, 3605.0: 17, 3606.0: 9, 3607.0: 9, 3608.0: 4, 3609.0: 10, 3610.0: 10}
mean count per second in [3000,3599]: 7.54
mean count per second in [3601,4200]: 6.35
exactly 1800 s: 11 ; 1799/1801: 32 25
3600-s target records in period: 82 flagged (b): 76
                       oblast                 raion                started_at                next_start     gap_h
20302           Sumska oblast      Okhtyrskyi raion 2026-01-27 09:44:35+00:00 2026-01-27 11:29:38+00:00  1.750833
21101       Kharkivska oblast  Bohodukhivskyi raion 2026-01-31 23:46:52+00:00 2026-02-01 01:19:00+00:00  1.535556
29331           Sumska oblast         Sumskyi raion 2026-03-04 16:29:41+00:00 2026-03-04 19:03:54+00:00  2.570278
44683           Odeska oblast         Odeskyi raion 2026-04-28 18:23:58+00:00 2026-04-28 19:30:26+00:00  1.107778
53065  Dnipropetrovska oblast     Samarivskyi raion 2026-05-27 09:24:20+00:00 2026-05-27 12:06:06+00:00  2.696111
53066  Dnipropetrovska oblast     Dniprovskyi raion 2026-05-27 09:24:20+00:00 2026-05-27 12:06:11+00:00  2.697500
gap of flagged (h): min 3.26 median 13.75 max 134.56
non-3600 records 50-70 min: share next start > 3 h: 0.501
rule (b) with next start among raion+hromada records: 73 vs code 76
```

</details>

<details><summary>🔧 Write: reviews/scratch/stage0-1b/s10_decisions_numbers.py · 20:30</summary>

**Аргументы**

```
# file: reviews/scratch/stage0-1b/s10_decisions_numbers.py
"""Stage 0-1b review: numbers of D02-D15 that report.py does not check. Read-only, nothing saved."""
import numpy as np
import pandas as pd

from alerts.config import ROOT, load_config, ts
from alerts.intervals import episodes
from alerts.pipeline import build_all
from alerts.scope import ROLE_INPUT, ROLE_TARGET

cfg = load_config()
art = build_all(cfg)
df = art.df
ws, de = ts(cfg['periods']['work_start']), ts(cfg['data_end'])
te, ve = ts(cfg['periods']['train_end']), ts(cfg['periods']['val_end'])

# D02: last records
last = df[df['finished_at'] >= ts('2026-09-07T05:00:00Z')].sort_values('finished_at')
print('D02 last records:\n', last[['oblast', 'raion', 'level', 'started_at', 'finished_at']].tail(6).to_string())

# D03: duplicates inside the working period
raw = pd.read_csv(ROOT / cfg['dataset']['path'])
for c in ['started_at', 'finished_at']:
    raw[c] = pd.to_datetime(raw[c], utc=True)
dup = raw[raw.duplicated()]
print('D03 duplicates total', len(dup), '; start >= work_start', int((dup['started_at'] >= ws).sum()),
      '; overlapping period', int(((dup['started_at'] < de) & (dup['finished_at'] > ws)).sum()))

# D04: raion share by month (all records), and last oblast-level record per western oblast
m = df.assign(month=df['started_at'].dt.strftime('%Y-%m'))
share = m.groupby('month')['level'].apply(lambda s: (s == 'raion').mean())
print('D04 raion share:', share.loc['2025-01':'2025-12'].round(3).to_dict())
west = ['Volynska oblast', 'Zakarpatska oblast', 'Ivano-Frankivska oblast', 'Ternopilska oblast']
ob = df[(df['level'] == 'oblast') & (df['oblast'].isin(west))].groupby('oblast')['started_at'].max()
print('D04 last oblast-level record, western:', ob.astype(str).to_dict())
print('D04 oblast-level records starting >= work_start, by oblast:',
      df[(df['level'] == 'oblast') & (df['started_at'] >= ws)]['oblast'].value_counts().to_dict())

# D06: Donetsk
dn = art.scope[art.scope['role'] == ROLE_INPUT]
p
… [обрезано: показано 2000 из 6830 символов]
```

**Результат**

```
File created successfully at: d:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage0-1b\s10_decisions_numbers.py (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Bash: Recompute unchecked DECISIONS numbers · 20:30</summary>

**Аргументы**

```bash
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage0-1b/s10_decisions_numbers.py 2>&1 | grep -v "^INFO\|Warning\|warn"
```

**Результат**

```
Channel outage (D15): 2026-08-29 05:55:28+00:00 -> 2026-09-02 13:48:04+00:00 (4 days 07:52:36)
D02 last records:
                  oblast               raion  level                started_at               finished_at
185401  Donetska oblast   Bakhmutskyi raion  raion 2026-09-06 23:57:37+00:00 2026-09-07 05:39:33+00:00
185400  Donetska oblast     Donetskyi raion  raion 2026-09-06 23:57:37+00:00 2026-09-07 05:39:33+00:00
185399  Donetska oblast  Mariupolskyi raion  raion 2026-09-06 23:57:37+00:00 2026-09-07 05:39:33+00:00
185398  Donetska oblast    Horlivskyi raion  raion 2026-09-06 23:57:37+00:00 2026-09-07 05:39:33+00:00
185397  Donetska oblast  Kramatorskyi raion  raion 2026-09-06 23:57:37+00:00 2026-09-07 05:39:33+00:00
185396  Donetska oblast    Kalmiuskyi raion  raion 2026-09-06 23:57:37+00:00 2026-09-07 05:39:33+00:00
D03 duplicates total 113845 ; start >= work_start 21501 ; overlapping period 21525
D04 raion share: {'2025-01': 0.076, '2025-02': 0.064, '2025-03': 0.065, '2025-04': 0.042, '2025-05': 0.14, '2025-06': 0.14, '2025-07': 0.195, '2025-08': 0.582, '2025-09': 0.731, '2025-10': 0.713, '2025-11': 0.893, '2025-12': 0.911}
D04 last oblast-level record, western: {'Ivano-Frankivska oblast': '2025-11-02 21:35:47+00:00', 'Ternopilska oblast': '2025-11-02 21:36:59+00:00', 'Volynska oblast': '2025-11-02 21:36:49+00:00', 'Zakarpatska oblast': '2025-11-02 21:35:25+00:00'}
D04 oblast-level records starting >= work_start, by oblast: {'Kyiv City': 500}
D06 Donetsk records overlapping period 6296 ; start in [ws, de) 6288 ; raions 8
D06 I00 share of time under alert (union of raions): 0.899
D06 mean per-raion share under alert: 0.899
D07 share of target records matching another unit to the minute: 0.483
D07 min train records per target location: 84 locations 111
D08 hromada records overlapping period: {'Kharkivska oblast': 2168, 'Dnipropetrovska oblast': 2143, 'Zaporizka oblast': 1465, 'Donetska oblast': 751, 'Zhytomyrska oblast': 55} ; empty raion: 0
D08 hromada records start in period: {'Kharkivska oblast': 2166, 'Dnipropetrovska oblast': 2140, 'Zaporizka oblast': 1465, 'Donetska oblast': 751, 'Zhytomyrska oblast': 55}
D10 long: n 119 ; distinct end minutes 56 ; overlapping outage 20 ; spanning whole outage 20
D15 records of the whole file spanning the outage: 31 {'raion': 28, 'hromada': 3}
D15 starts per day (all records): {'2026-08-27': 558, '2026-08-28': 598, '2026-08-29': 88, '2026-09-02': 241}
D15 median starts per day in period (all records): 299.0
D15 starts per day (target scope): {'2026-08-27': 509, '2026-08-28': 526, '2026-08-29': 86, '2026-09-02': 225}
D15 median starts per day (target scope): 254.0
D12 pauses 72846 median 131.1 {5: 3.14, 10: 6.24, 15: 9.43, 30: 17.84, 60: 30.95}
D10 (b) unit masks: n 71 median h 13.7 ; outside outage median 12.0 p75 17.6 max 134.6
D10 rows reaching known mask (stage3): {1: 99, 3: 230, 6: 381}
```

</details>

<details><summary>🔧 Bash: Read stage 3 summary head · 20:31</summary>

**Аргументы**

```bash
sed -n 1,30p reports/stage3_summary.md
```

**Результат**

```
# Stage 3 summary

Generated by `scripts/run_all.py`. Decisions: DECISIONS.md, D17.

Candidates: 104 target units x 7,128 hourly moments = 741,312.

## Status of candidates (unit, t)

| Status | Train | Val | Test |
|---|---|---|---|
| quiet | 510,642 | 57,865 | 48,402 |
| alert | 88,866 | 11,790 | 12,147 |
| bridged_pause | 600 | 86 | 105 |
| masked_outage | 0 | 0 | 9,152 |
| masked_after_data_end | 0 | 0 | 0 |
| masked_long_24h | 0 | 0 | 0 |
| masked_fake_1h | 1,420 | 147 | 82 |
| held_open | 8 | 0 | 0 |

Only `quiet` candidates become rows. `masked_long_24h` is empty because a long alert is itself an alert; its windows are counted below.

## Targets

| h | Part | Rows | Unlabelled (window reaches mask (c)/(d)) | Positives | Base rate | Positives with >= 2 starts |
|---|---|---|---|---|---|---|
| 1 | train | 510,642 | 0 | 45,363 | 0.089 | 1.2% |
| 1 | val | 57,865 | 0 | 7,007 | 0.121 | 1.2% |
| 1 | test | 48,332 | 70 | 6,003 | 0.124 | 1.5% |
| 3 | train | 510,642 | 0 | 106,576 | 0.209 | 13.1% |
| 3 | val | 57,865 | 0 | 15,223 | 0.263 | 20.4% |
```

</details>

<details><summary>🔧 Write: reviews/scratch/stage0-1b/s11_more_numbers.py · 20:32</summary>

**Аргументы**

```
# file: reviews/scratch/stage0-1b/s11_more_numbers.py
"""Stage 0-1b review: definitions behind D04, D06, D07, D08, D10, D12 numbers; train-only statistics. Read-only."""
import numpy as np
import pandas as pd

from alerts.config import ROOT, load_config, ts
from alerts.ingest.vadimkin import load_official
from alerts.scope import ROLE_INPUT, ROLE_TARGET, select_scope
from alerts.spans import union

cfg = load_config()
df = load_official(ROOT / cfg['dataset']['path'], cfg['dataset']['sha256'])
ws, de = ts(cfg['periods']['work_start']), ts(cfg['data_end'])
te = ts(cfg['periods']['train_end'])
sa = select_scope(df, cfg, period=False)
rec = sa[(sa['role'] == ROLE_TARGET) & (sa['started_at'] >= ws)]

# D04 first raion record of western oblasts
west = ['Volynska oblast', 'Zakarpatska oblast', 'Ivano-Frankivska oblast', 'Ternopilska oblast']
r = df[(df['level'] == 'raion') & df['oblast'].isin(west) & (df['started_at'] >= ts('2025-10-01T00:00:00Z'))]
print('D04 first raion record after 2025-10-01:', r.groupby('oblast')['started_at'].min().astype(str).to_dict())

# D07 57%: records matching a record of another LOCATION to the minute (start and end)
k = rec.assign(sm=rec['started_at'].dt.floor('min'), em=rec['finished_at'].dt.floor('min'),
               loc=rec['oblast'] + '|' + rec['raion'])
n = k.groupby(['sm', 'em'])['loc'].transform('nunique')
print('D07 share matching another location to the minute:', round(float((n > 1).mean()), 3))
k2 = k.assign(ss=k['started_at'], ee=k['finished_at'])
n2 = k2.groupby(['ss', 'ee'])['loc'].transform('nunique')
print('D07 share matching another location to the second:', round(float((n2 > 1).mean()), 3))

# D08 Kharkiv hromada variants
h = df[(df['level'] == 'hromada') & (df['oblast'] == 'Kharkivska oblast')]
print('D08 Kharkiv hromada: start>=ws', int((h['started_at'] >= ws).sum()),
      '; start in [ws,de)', int(((h['started_at'] >= ws) & (h['started_at'] < de)).sum()),
      '; overlap', int(((h['started_at'] < de) & (h['finished_at'
… [обрезано: показано 2000 из 4877 символов]
```

**Результат**

```
File created successfully at: d:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage0-1b\s11_more_numbers.py (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Bash: Check definitions behind DECISIONS numbers · 20:32</summary>

**Аргументы**

```bash
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage0-1b/s11_more_numbers.py 2>&1 | grep -v "^INFO"
```

**Результат**

```
D04 first raion record after 2025-10-01: {'Ivano-Frankivska oblast': '2025-11-06 14:42:07+00:00', 'Ternopilska oblast': '2025-11-06 09:07:13+00:00', 'Volynska oblast': '2025-11-06 14:41:50+00:00', 'Zakarpatska oblast': '2025-11-06 14:43:16+00:00'}
D07 share matching another location to the minute: 0.571
D07 share matching another location to the second: 0.32
D08 Kharkiv hromada: start>=ws 2169 ; start in [ws,de) 2166 ; overlap 2168
D08 hromada with duplicates, start >= ws: {'Dnipropetrovska oblast': 2804, 'Kharkivska oblast': 2595, 'Zaporizka oblast': 1785}
D06 Donetsk mean raion share under alert, period: 0.899 min 0.899 max 0.899
D06 ... without records > 24 h, period: 0.657
D06 Donetsk mean raion share under alert, train: 0.884 min 0.884 max 0.884
D06 ... without records > 24 h, train: 0.675
D10 (b) location masks: 76 outside outage 56 median 12.0 p75 15.0
D12 pauses (all period): 80083 median 121.3 {5: 3.42, 10: 6.83, 15: 10.36, 30: 19.51, 60: 32.97}
D12 pauses (train only): 62129 median 133.4 {5: 3.18, 10: 6.39, 15: 9.78, 30: 18.31, 60: 31.1}
D10 durations (all): median 47, p75 113, p99 760, > 24 h 119
D10 durations (train): median 49, p75 119, p99 745, > 24 h 78
D15 longest gap in train (h): 3.72
```

</details>

<details><summary>🔧 Grep: sha256|file_sha256 в src · 20:32</summary>

**Аргументы**

```json
{
 "pattern": "sha256|file_sha256",
 "path": "d:\\Flash\\golova\\KSE_AI\\AAFS\\src",
 "output_mode": "content"
}
```

**Результат**

```
src\alerts\api_check.py:101:    if hashlib.sha256(blob).hexdigest() != v['sha256']:
src\alerts\geo.py:19:from alerts.ingest.vadimkin import file_sha256
src\alerts\geo.py:33:    if file_sha256(p) != g['sha256']:
src\alerts\config.py:10:    'dataset': ['repo_url', 'commit', 'repo_dir', 'path', 'sha256', 'path_uk', 'sha256_uk'],
src\alerts\config.py:11:    'volunteer': ['commit', 'path', 'sha256'],
src\alerts\config.py:18:    'geo': ['path', 'sha256', 'vertex_decimals', 'min_shared_vertices', 'renames'],
src\alerts\pipeline.py:43:    df = load_official(ROOT / cfg['dataset']['path'], cfg['dataset']['sha256'])
src\alerts\ingest\alerts_in_ua.py:22:from alerts.ingest.vadimkin import file_sha256
src\alerts\ingest\alerts_in_ua.py:59:    for key, sha in [('path', 'sha256'), ('path_uk', 'sha256_uk')]:
src\alerts\ingest\alerts_in_ua.py:60:        if file_sha256(ROOT / ds[key]) != ds[sha]:
src\alerts\ingest\vadimkin.py:9:def file_sha256(path) -> str:
src\alerts\ingest\vadimkin.py:10:    h = hashlib.sha256()
src\alerts\ingest\vadimkin.py:17:def load_official(path, expected_sha256: str) -> pd.DataFrame:
src\alerts\ingest\vadimkin.py:23:    file_hash = file_sha256(path)
src\alerts\ingest\vadimkin.py:24:    if file_hash != expected_sha256:
src\alerts\ingest\vadimkin.py:25:        raise ValueError(f'SHA-256 mismatch! Expected {expected_sha256}, got {file_hash}')
```

</details>

<details><summary>🔧 Bash: Check blob vs working file hash portability · 20:32</summary>

**Аргументы**

```bash
cd /d/Flash/golova/KSE_AI/AAFS/dataset_repo && git config --get core.autocrlf; git ls-tree 58ee75b datasets/official_data_en.csv; git hash-object datasets/official_data_en.csv; git show 58ee75b:datasets/official_data_en.csv | sha256sum; sha256sum datasets/official_data_en.csv; head -c 200 datasets/official_data_en.csv | od -c | head -5; cat .gitattributes 2>/dev/null
```

**Результат** (ошибка)

```
Exit code 1
true
100644 blob 4c9ef9bf023fefcbfd50cf45188ef36b5119aebe	datasets/official_data_en.csv
f7a3fcaa6d52c7d8a2ce0e59012ea666e238e90c
b396f87696243069eec0219880e87dcd642b20beb0a7bae0d0e1f61e1ed20ec4 *-
b396f87696243069eec0219880e87dcd642b20beb0a7bae0d0e1f61e1ed20ec4 *datasets/official_data_en.csv
0000000   o   b   l   a   s   t   ,   r   a   i   o   n   ,   h   r   o
0000020   m   a   d   a   ,   l   e   v   e   l   ,   s   t   a   r   t
0000040   e   d   _   a   t   ,   f   i   n   i   s   h   e   d   _   a
0000060   t   ,   s   o   u   r   c   e  \r  \n   V   i   n   n   y   t
0000100   s   k   a       o   b   l   a   s   t   ,   ,   ,   o   b   l
```

</details>

<details><summary>🔧 Bash: Run zone tests without writing cache · 20:33</summary>

**Аргументы**

```bash
PYTHONIOENCODING=utf-8 python -m pytest -q tests/test_load.py tests/test_units.py tests/test_mask.py -p no:cacheprovider 2>&1 | tail -5
```

**Результат**

```
.....                                                                    [100%]
5 passed in 6.30s
```

</details>

<details><summary>🔧 Write: reviews/scratch/stage0-1b/s12_renamed_raions.py · 20:34</summary>

**Аргументы**

```
# file: reviews/scratch/stage0-1b/s12_renamed_raions.py
"""Stage 0-1b review: raions renamed in 2023-2024 that the processor knows only by the old hashtag
(Krasnohradskyi, Chervonohradskyi, Volodymyr-Volynskyi): monthly record counts next to the other raions
of the same oblast. A switch of the channel to the new hashtag would drop whole posts. Read-only."""
import pandas as pd

from alerts.config import ROOT, load_config, ts
from alerts.ingest.vadimkin import load_official

cfg = load_config()
df = load_official(ROOT / cfg['dataset']['path'], cfg['dataset']['sha256'])
ws, de = ts(cfg['periods']['work_start']), ts(cfg['data_end'])
r = df[(df['level'] == 'raion') & (df['started_at'] >= ws) & (df['started_at'] < de)]
for ob, name in [('Kharkivska oblast', 'Krasnohradskyi raion'), ('Lvivska oblast', 'Chervonohradskyi raion'),
                 ('Volynska oblast', 'Volodymyr-Volynskyi raion')]:
    o = r[r['oblast'] == ob]
    t = o.groupby([o['started_at'].dt.strftime('%Y-%m'), 'raion']).size().unstack(fill_value=0)
    print(ob)
    print(t.T.to_string())

```

**Результат**

```
File created successfully at: d:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage0-1b\s12_renamed_raions.py (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Bash: Monthly counts for renamed raions · 20:34</summary>

**Аргументы**

```bash
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage0-1b/s12_renamed_raions.py 2>&1 | grep -v "^INFO"
```

**Результат**

```
Kharkivska oblast
started_at            2025-11  2025-12  2026-01  2026-02  2026-03  2026-04  2026-05  2026-06  2026-07  2026-08  2026-09
raion                                                                                                                  
Bohodukhivskyi raion       99      125      164      149      219      212      242      277      259      239       44
Chuhuivskyi raion         113      153      168      143      201      191      232      248      246      231       42
Iziumskyi raion            90      147      165      155      211      174      223      226      194      208       33
Kharkivskyi raion         129      167      191      160      232      241      288      298      265      235       44
Krasnohradskyi raion       98       90      131      130      112      104      127      144      166      182       30
Kupianskyi raion          106      160      157      136      182      162      214      228      212      210       34
Lozivskyi raion            92      114      156      143      148      121      155      192      200      244       41
Lvivska oblast
started_at              2025-11  2025-12  2026-01  2026-02  2026-03  2026-04  2026-05  2026-06  2026-07  2026-08
raion                                                                                                           
Chervonohradskyi raion       10       10       10       16       12        7       14       10        2        2
Drohobytskyi raion           10        9        9       13       11        7       15        9        2        2
Lvivskyi raion               10        9       11       16       12        7       15       10        2        2
Sambirskyi raion             10        9        9       13       11        7       15        9        2        2
Stryiskyi raion              11        9        9       17       12        7       15        9        2        2
Yavorivskyi raion            11        9       10       13       11        6       14       10        2        2
Zolochivskyi raion           10        9       12       16       12        8       14       10        2        2
Volynska oblast
started_at                 2025-11  2025-12  2026-01  2026-02  2026-03  2026-04  2026-05  2026-06  2026-07  2026-08  2026-09
raion                                                                                                                       
Kamin-Kashyrskyi raion           8       13       17       21       12        7       16       16        2        2        3
Kovelskyi raion                  8       15       15       19       11        8       14       14        2        3        0
Lutskyi raion                    9       11       16       22       11        9       15       13        3        5        4
Volodymyr-Volynskyi raion        9        9        9       18       11        8       13       10        2        2        0
```

</details>

<details><summary>🔧 Write: reviews/scratch/stage0-1b/s13_d15_numbers.py · 20:35</summary>

**Аргументы**

```
# file: reviews/scratch/stage0-1b/s13_d15_numbers.py
"""Stage 0-1b review: D15 motivation numbers (grid without rule (d)). Nothing is saved."""
import pandas as pd

from alerts.config import load_config, ts
from alerts.grid import build_grid
from alerts.intervals import build_intervals
from alerts.mask import OUTAGE
from alerts.pipeline import build_all

cfg = load_config()
art = build_all(cfg)
m0 = art.masks[art.masks['reason'] != OUTAGE]
iv0 = build_intervals(art.scope, art.units, m0, cfg)
g0, st0 = build_grid(art.seen, iv0, m0, art.units, cfg)
o = art.outages.iloc[0]
test = g0[g0['part'] == 'test']
inside = (test['t'] >= o.start) & (test['t'] < o.end)
y = test['y_3']
print('h=3 test rows without (d):', int(y.notna().sum()), '; inside outage:', int((inside & y.notna()).sum()),
      f"({(inside & y.notna()).sum() / y.notna().sum():.1%})",
      '; positives inside', round(float(y[inside].dropna().mean()), 4), 'outside', round(float(y[~inside].dropna().mean()), 4),
      '; base test', round(float(y.dropna().mean()), 4), 'vs with (d)', round(st0 and art.grid_stats['horizons'][3]['base_rate']['test'], 4))
# units that look quiet through the whole outage (no alert / mask at any hourly t inside)
T = pd.date_range(o.start.ceil('h'), o.end, freq='h', inclusive='left')
quiet_units = test[inside].groupby('unit_id')['t'].nunique()
print('units with a quiet row at every hourly moment inside the outage:', int((quiet_units == len(T)).sum()), 'of',
      art.units.loc[art.units['role'] == 'target', 'unit_id'].nunique(), '; hourly moments', len(T))

```

**Результат**

```
File created successfully at: d:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage0-1b\s13_d15_numbers.py (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Bash: Recompute D15 motivation numbers · 20:35</summary>

**Аргументы**

```bash
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage0-1b/s13_d15_numbers.py 2>&1 | grep -v "^INFO"
```

**Результат**

```
Channel outage (D15): 2026-08-29 05:55:28+00:00 -> 2026-09-02 13:48:04+00:00 (4 days 07:52:36)
h=3 test rows without (d): 55493 ; inside outage: 7280 (13.1%) ; positives inside 0.0052 outside 0.2595 ; base test 0.2261 vs with (d) 0.2603
units with a quiet row at every hourly moment inside the outage: 70 of 104 ; hourly moments 104
```

</details>

<details><summary>🔧 Bash: Find zone-related claims in README · 20:36</summary>

**Аргументы**

```bash
grep -n "104\|0\.997\|0,997\|15[.,]9\|05:55\|29\.08\|клон\|Жаккар\|299 275\|185 4\|дублік\|маск" README.md | head -40
```

**Результат**

```
48:- 38% рядків файлу — точні дублікати; дедуплікація — перший крок;
51:  склеєно: 104 одиниці. Донецька область — лише вхід для ознак;
52:- тривоги, довші за добу, і тривоги з кінцем, вигаданим процесором датасету, маскуються як «статус
55:  замасковано; без маски 13% тестових рядків були б хибними «нулями».
123:- Маски (D10, D15) прибирають із тесту 15.9% одиниць-годин, майже все — перерва в роботі каналу.
```

</details>

<details><summary>🔧 Bash: Read README data section and limitations · 20:36</summary>

**Аргументы**

```bash
sed -n 40,60p README.md; sed -n 115,130p README.md
```

**Результат**

```
- Як перевірено: історія комітів (файл побайтово той самий до 10 жовтня); останній оброблений пост
  (ID 338380) — це останній пост самого каналу; ручна перевірка каналу.
- Що розглянуто й відхилено: волонтерський ряд (лише області, а не райони); власний розбір того самого
  каналу (нових постів немає); API alerts.in.ua — джерело з іншою обробкою, його не можна склеювати з
  тестом. Його використано окремо, як перевірку через місяць (розділ нижче).
- Знімок зафіксовано: коміт `58ee75b`, SHA-256 файлу перевіряється під час кожного завантаження.

**Підготовка (D03–D15):**
- 38% рядків файлу — точні дублікати; дедуплікація — перший крок;
- районний режим діє в усіх областях із 2025-11-07: це початок робочого періоду;
- 110 районів у 22 областях плюс Київ. Райони з практично однаковими рядами (спискові пости каналу)
  склеєно: 104 одиниці. Донецька область — лише вхід для ознак;
- тривоги, довші за добу, і тривоги з кінцем, вигаданим процесором датасету, маскуються як «статус
  невідомий», а не обрізаються;
- **з 29 серпня по 2 вересня канал мовчав 4.3 доби** (знайдено під час рев'ю, D15). Цю перерву
  замасковано; без маски 13% тестових рядків були б хибними «нулями».

**Розбиття (D14):** навчання — до 2026-07-13, валідація — 4 тижні, тест — 2026-08-10 – 2026-09-07.

## Як влаштовано


## Обмеження

- Модель місяць не бачила даних: основний ряд закінчився 7 вересня. У реальному розгортанні її
  довелося б перенавчати.
- Пости про загрози на рівні районів перевірено вибіркою з 60 постів, а не повним архівом каналу (D09).
- Якщо відбій втрачено, а нова тривога прийшла протягом трьох годин, процесор датасету мовчки
  замінює першу тривогу: такі випадки неможливо ні знайти, ні виправити (D09).
- Маски (D10, D15) прибирають із тесту 15.9% одиниць-годин, майже все — перерва в роботі каналу.
- Правий край: тривоги, не закриті до зупинки каналу, у даних відсутні (D13).
- У тесті немає жодної тривоги у Львівській, Івано-Франківській і Закарпатській областях:
  метрики для них не визначені.
- На заході райони майже завжди оголошуються разом, районна диференціація там слабка; на сході й
  у центрі вона справді працює (D07).

## Запуск
```

</details>

<details><summary>🔧 Bash: Compute precise Odesa pair margin to threshold · 20:37</summary>

**Аргументы**

```bash
cat > reviews/scratch/stage0-1b/s14_odesa_margin.py <<'EOF'
"""Precise margin of the Odesa pair to the 0.997 threshold on the train period (minute floor grid, as in units.py)."""
import numpy as np
from alerts.config import load_config, ts
from alerts.pipeline import build_all  # noqa: F401  (not used; keep imports light)
from alerts.config import ROOT
from alerts.ingest.vadimkin import load_official
from alerts.scope import LOC_KEY, ROLE_TARGET, select_scope
from alerts.units import _minute_grid

cfg = load_config()
df = load_official(ROOT / cfg['dataset']['path'], cfg['dataset']['sha256'])
sc = select_scope(df, cfg, period=True)
t = sc[sc['role'] == ROLE_TARGET]
locs = t[LOC_KEY].drop_duplicates().sort_values(LOC_KEY).reset_index(drop=True)
g = _minute_grid(t, locs, ts(cfg['periods']['work_start']), ts(cfg['periods']['train_end']))
ix = {r: i for i, r in enumerate(locs['raion'])}
a, b = g[ix['Berezivskyi raion']], g[ix['Podilskyi raion']]
U, X = int((a | b).sum()), int((a ^ b).sum())
print(f'union {U} min ({U/60:.1f} h), sym diff {X} min, J={1 - X / U:.5f}, '
      f'sym diff allowed at 0.997: {0.003 * U:.1f} min, margin {X - 0.003 * U:.1f} min')
EOF
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage0-1b/s14_odesa_margin.py 2>&1 | grep -v "^INFO"
```

**Результат**

```
union 29201 min (486.7 h), sym diff 91 min, J=0.99688, sym diff allowed at 0.997: 87.6 min, margin 3.4 min
```

</details>

*[ошибка API · 20:37: You&#x27;ve hit your weekly limit · resets 2am (Europe/Kyiv)]*

<details><summary>🔧 Bash: Confirm line numbers for citations · 08:41</summary>

**Аргументы**

```bash
grep -n "events = \|'start': events\|def detect_outages\|in_period = \|rule_b\['next_start'\]" src/alerts/mask.py; grep -n "next_start'\] = \|is_fake_end'\] = \|open_until'\] = " src/alerts/processor.py; grep -n "flag_records(out" src/alerts/scope.py; grep -n "start_m = \|end_m = \|keep = \|_minute_grid(target" src/alerts/units.py; grep -n "^REFERENCE\|Every number\|'base rate train" src/alerts/report.py; grep -n "Последняя завершённая\|около 86%\|около 400\|960 точек\|960 (0.147\|Таблицу сверяет\|05:55:28 UTC по\|следующая пара\|весь рабочий период):" DECISIONS.md; ls reviews
```

**Результат**

```
32:def detect_outages(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
41:    events = pd.concat([df['started_at'], df['finished_at']]).sort_values().drop_duplicates()
42:    events = events.reset_index(drop=True)
45:    out = pd.DataFrame({'start': events[i - 1].reset_index(drop=True),
59:    in_period = lambda m: m[(m['start'] < data_end) & (m['end'] > work_start)]
69:                      'end': rule_b['next_start'], 'reason': FAKE_END, 'role': rule_b['role']}),
30:    rec['next_start'] = rec.groupby(key, sort=False)['started_at'].shift(-1)
38:    rec['is_fake_end'] = invented_length & ((rec['next_start'] - rec['started_at']) > fake_gap)
41:    rec['open_until'] = rec['finished_at'].where(~invented_length | later_start.isna(), later_start)
51:    out = flag_records(out, cfg, LOC_KEY)
28:    grid = _minute_grid(target, locs, ts(cfg['periods']['work_start']), ts(cfg['periods']['train_end']))
65:    start_m = np.clip((to_sec(rec['started_at']) - base) // 60, 0, n_min)
66:    end_m = np.clip((to_sec(rec['finished_at']) - base) // 60, 0, n_min)
67:    keep = start_m < end_m
3:Every number of the DECISIONS.md reference table is recomputed and compared (PLAN rule 8).
21:REFERENCE = {
33:    'base rate train: h=1 / h=3 / h=6 (D17)': '0.089 / 0.209 / 0.321',
83:        'base rate train: h=1 / h=3 / h=6 (D17)':
33:- По данным канал остановился утром 7 сентября (около 06:09 UTC). Последняя завершённая тревога в CSV: начало 2026-09-07 05:28:22 UTC, конец 05:39:33 UTC.
116:**Находка:** в рабочем периоде 6 288 районных записей по всем 8 районам, включая оккупированные (Донецкий, Горловский, Кальмиусский, Мариупольский). Это общеобластные тревоги, записанные списком районов: один пост в канале перечисляет несколько районов. Районы под тревогой около 86% времени.
132:- Совпадение рядов — не случай «да или нет», а непрерывная шкала. Сходство Жаккара по времени под тревогой (весь рабочий период):
147:- Порог 0.997 выбран, потому что при нём единицы расходятся меньше чем в 0.3% времени под тревогой, то есть фактически это задержки публикации на секунды. Чётко выраженного разрыва в распределении нет (следующая пара — Одесская область, 0.996), поэтому порог фиксируем заранее и не подбираем.
259:**Семантика для этапа 3.** Маски (а) и (б) начинаются с настоящего начала тревоги: пост «Повітряна тривога» был, неизвестен только конец. Поэтому строка с `t <` начала маски `≤ t+h` имеет известную метку `y = 1`, и выбрасывать её нельзя: это был бы отбор строк по будущему (что тревога окажется длинной или с потерянным отбоем). На рабочем периоде при h = 3 таких строк около 400. Новое правило записано в PLAN, этап 3.
280:- **Влияние на целевую переменную ничтожно.** Из 652 843 «тихих» часовых точек внутрь пауз короче 10 минут попадают 449 (0.069%), короче 15 минут — 960 (0.147%), короче 30 минут — 3 695 (0.566%).
295:- строки сетки, где `t` попадает в склеенную паузу своей единицы, не создаются (960 точек, 0.15%). Это отбор по будущему, но порог 15 минут определяет саму цель, и
… [обрезано: показано 3000 из 4636 символов]
```

</details>

<details><summary>🔧 Bash: List claude review folder and my scratch · 08:42</summary>

**Аргументы**

```bash
ls reviews/claude; ls reviews/scratch/stage0-1b
```

**Результат**

```
s01_raw_formats.py
s02_scope.py
s03_west_gap.py
s04_west_monthly.py
s05_clones.py
s06_odesa_seconds.py
s07_outage_events.py
s08_build_compare.py
s09_rules_ab.py
s10_decisions_numbers.py
s11_more_numbers.py
s12_renamed_raions.py
s13_d15_numbers.py
s14_odesa_margin.py
```

</details>

<details><summary>🔧 Write: reviews/claude/stage0-1b.md · 08:43</summary>

**Аргументы**

```
# file: reviews/claude/stage0-1b.md
# Ревью этапов 0–1б: снимок, загрузка, охват, клоны, маски

Ревьюер: Claude (независимо от других отчётов в `reviews/`). Скрипты: `reviews/scratch/stage0-1b/s01…s14_*.py`, запуск из корня:
`PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage0-1b/<файл>`. Ничего в `data/`, `reports/`, `src/` не записывалось.

## 1. Резюме

Загрузка, дедупликация, охват и правило (б) реализованы корректно и совпадают с поведением процессора датасета. Сохранённые `data/units.csv`, `data/mask.csv` и `reports/high_sim_pairs.csv` совпадают с пересборкой в памяти. Главная находка: начало перерыва канала (D15, правило (г)) задаёт не пост канала, а выдуманный процессором конец `начало + 1 ч`. На самом деле канал замолчал на час раньше, в 04:55:28, и справочная цифра D15 неверна. На метрики это почти не влияет: меняются около 74 тестовых строк из 48 028 при h = 3. Вторая находка: решение «3 группы клонов, 104 единицы» держится на способе дискретизации. На обучающем периоде одесская пара Березовский–Подольский отстоит от порога 0.997 на 3.4 минуты расхождения за 8 месяцев, а при точном расчёте в секундах она выше порога (0.99735), то есть её пришлось бы склеить. Автоматическая сверка не охватывает долю маски (15.93%), хотя DECISIONS утверждает обратное. Ещё четыре числа D02–D12 расходятся с данными. Вердикт: критичных ошибок в зоне нет. Есть две существенные: семантика правила (г) и хрупкость порога клонов. Плюс пробел в сверке и несколько неточностей в документах.

## 2. Находки

### S1-1. Начало перерыва канала задаёт выдуманный конец, а не пост канала
- **Серьёзность:** существенно (неверны справочная цифра и описание D15; на метрики влияние ничтожно). **Уверенность:** проверено на данных.
- **Где:** `src/alerts/mask.py:41` (события = все `started_at` и `finished_at` файла), `mask.py:45` (начало перерыва = последнее событие перед паузой); DECISIONS D15:333, справочная таблица:666.
- **Что не так.** Выдуманный конец `начало + 1 ч` (`official
… [обрезано: показано 2000 из 15984 символов]
```

**Результат**

```
File created successfully at: D:\Flash\golova\KSE_AI\AAFS\reviews\claude\stage0-1b.md (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Bash: Verify README line references and report length · 08:43</summary>

**Аргументы**

```bash
grep -n "15.9%\|жодної тривоги" README.md; wc -l reviews/claude/stage0-1b.md
```

**Результат**

```
123:- Маски (D10, D15) прибирають із тесту 15.9% одиниць-годин, майже все — перерва в роботі каналу.
125:- У тесті немає жодної тривоги у Львівській, Івано-Франківській і Закарпатській областях:
115 reviews/claude/stage0-1b.md
```

</details>

<details><summary>🔧 Edit: reviews/claude/stage0-1b.md · 08:43</summary>

**Аргументы**

```
# file: reviews/claude/stage0-1b.md
--- old_string ---
README:126 это уже отмечает.
--- new_string ---
README:125 это уже отмечает.
```

**Результат**

```
The file D:\Flash\golova\KSE_AI\AAFS\reviews\claude\stage0-1b.md has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 SubagentHandback: {"message": "Ревью этапов 0–1б записано в `D:\\Flash\\golova\\KSE_AI\\AAFS\\reviews\\claude\\stage0-1b.md` (115 строк).… · 08:43</summary>

**Аргументы**

```json
{
 "message": "Ревью этапов 0–1б записано в `D:\\Flash\\golova\\KSE_AI\\AAFS\\reviews\\claude\\stage0-1b.md` (115 строк). Критичных находок нет, существенных три. Мои скрипты лежат в `reviews/scratch/stage0-1b/` (s01–s14). В старое место `reviews/stage0-1b.md` я ничего не писал, поэтому восстанавливать было нечего. Чужие отчёты и папку `scratch-gpro/` не открывал, в `src/`, `data/`, `reports/` ничего не менял.\n\n**Резюме:**\n- Загрузка, дедупликация, охват и правило (б) реализованы верно. Поиск следующего начала идёт только среди районных записей той же `(oblast, raion)` — так же работает процессор датасета.\n- Сохранённые `data/units.csv`, `data/mask.csv`, `reports/high_sim_pairs.csv` совпадают с пересборкой в памяти. Тесты зоны проходят (5 passed).\n- В CSV все отметки времени вида `…+00:00` без дробных секунд, поэтому `as_unit('s')` ничего не теряет. «Почти дубликатов» нет. Переименований районов внутри данных и одинаковых названий районов в разных областях нет. У Киева есть только записи уровня `oblast`.\n- Начало перерыва канала (D15) задаёт выдуманный процессором конец «начало + 1 ч», а не пост канала. Канал замолчал на час раньше, в 04:55:28. На метрики это почти не влияет.\n- Решение «3 группы клонов, 104 единицы» зависит от того, как время округляется до минут. Одесская пара на обучающем периоде отстоит от порога на 3.4 минуты расхождения за 8 месяцев, а при расчёте в секундах она выше порога 0.997.\n- Автоматическая сверка не проверяет долю маски (15.93%), хотя DECISIONS утверждает, что проверяется вся таблица.\n- Мелочи:\n  - статистики для порогов 15 мин и 0.997 тоже посчитаны по всему периоду, включая тест; на обучающем периоде выводы те же;\n  - правило (б) по оценке маскирует 3–6 настоящих часовых тревог из 76;\n  - расходятся с данными числа D02:33, D06:116 (86% против 89.9%), D12:295 (960 против 791) и формулировка README:123.\n- Тишина на западе в тесте (20 локаций без тревог с 07.08) настоящая: это подтверждает волонтёрский ряд.\n\n**Существенные
… [обрезано: показано 2000 из 3456 символов]
```

**Результат**

```
{"success":true,"message":"Report delivered to your caller."}
```

</details>
