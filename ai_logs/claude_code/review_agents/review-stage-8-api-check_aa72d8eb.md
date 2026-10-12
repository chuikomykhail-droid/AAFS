# Субагент: Review stage 8 API check

- **Агент:** `aa72d8eb6398717fd` (general-purpose), запущен из сессии [57049ae5](../2026-10-11_critical-analysis_57049ae5.md#t-LtgVbN8GGr6C)
- **Период (UTC):** 2026-10-11 17:19 → 2026-10-12 05:46
- **Период (Киев):** 2026-10-11 20:19 → 2026-10-12 08:46
- **Сообщений:** 1 (задания и сообщения основного агента — 1, ответы субагента — 0); вызовов инструментов — 67
- **Исходный JSONL:** `ai_logs/claude_code/raw/claude_code_raw.zip → subagents/57049ae5_agent-aa72d8eb6398717fd.jsonl`

> Служебные вставки (`<system-reminder>`, вложения с окружением и контекстом IDE, мета-сообщения — 112 записей) и блоки рассуждений (thinking — 38) сюда не включены: они есть в исходном JSONL. Время — киевское. Вызовы инструментов свёрнуты; аргументы обрезаны до 2000 символов, результаты — до 3000. Токен alerts.in.ua и email автора заменены на `[REDACTED_TOKEN]` / `[REDACTED_EMAIL]`.

---

<a id="m-0b251fde"></a>

### 📨 Задание от основного агента · 2026-10-11 20:19

Рабочая папка проекта: d:\Flash\golova\KSE_AI\AAFS (Windows; доступны Bash (Git Bash) и PowerShell).

Прочитай файл `reviews/prompts/07_stage8.md` целиком и выполни задание из него в точности, включая все ограничения: не изменять файлы проекта, не запускать `scripts/run_all.py`, `scripts/api_check.py`, скрипты скачивания и `save_all`, не обращаться к API alerts.in.ua, не трогать git, не открывать токен. Параллельно с тобой в той же папке работают шесть других агентов-ревьюеров — пиши только в `reviews/stage8.md` и `reviews/scratch/stage8/`.

Когда отчёт записан, верни в ответе: резюме отчёта (5–10 строк) и список находок уровня «критично» и «существенно» — по одной строке на находку (id, суть, файл:строка, уровень проверки).

<details><summary>🔧 Read: reviews/prompts/07_stage8.md · 20:19</summary>

**Аргументы**

```json
{
 "file_path": "d:\\Flash\\golova\\KSE_AI\\AAFS\\reviews\\prompts\\07_stage8.md"
}
```

**Результат**

```
1	# Ревью проекта AAFS: этап 8: проверка на свежих данных alerts.in.ua
2	
3	Ты — независимый критический ревьюер. Параллельно с тобой другие агенты проверяют другие этапы того же проекта. Твоя зона — этап 8: адаптер alerts.in.ua, профиль источника, триангуляция через волонтёрский ряд, замороженные модели, проверка утечки на периоде API. На соседние этапы смотри только тогда, когда без этого не понять твой.
4	
5	## Проект
6	
7	- Репозиторий — текущая папка (`AAFS`), ветка `stages-7-8`. Python-проект: прогноз воздушных тревог в Украине по районам. Для каждой единицы (район; Киев — одна единица), где в момент `t` (каждый час) тихо, модель выдаёт вероятность того, что тревога начнётся в `(t, t+h]`, h = 1, 3, 6 (основной — 3).
8	- Данные — снимок датасета Vadimkin (`dataset_repo/`, коммит `58ee75b`). Официальный ряд заканчивается 2026-09-07. Тест — 2026-08-10…2026-09-07, walk-forward с ежесуточным переобучением. Этап 8 — проверка на данных alerts.in.ua за сентябрь–октябрь.
9	- Это тестовое задание с дедлайном 12.10.2026 23:59 по Киеву. Проверяющие оценивают процесс: пойманные ошибки, обоснованность решений, отсутствие утечки из будущего. Найденная проблема ценна, даже если её не успеют исправить: тогда она уйдёт в раздел ограничений.
10	- Документы: `PLAN.md` (правила работы 1–13; у каждого этапа «Исходное задание» и «Как сделано»), `DECISIONS.md` (решения D00–D22, справочные цифры, журнал пойманных ошибок ИИ), `README.md` (на украинском), отчёты в `reports/`.
11	
12	Сначала прочитай раздел «Правила работы» в `PLAN.md`, описание своего этапа в `PLAN.md` и разделы `DECISIONS.md`: D02, D22; в PLAN — этап 8 и «Вне MVP» (риски склейки источников). Код и тесты своей зоны читай целиком, а не выборочно.
13	
14	## Твоя зона: файлы
15	
16	- `src/alerts/ingest/alerts_in_ua.py`, `src/alerts/api_check.py`.
17	- `scripts/api_check.py` и `scripts/fetch_alerts_in_ua.py` — **только читать, не запускать.**
18	- `config.yaml`: разделы `api`, `volunteer`, `processor.enabled`.
19	- `data/alerts_in_ua_locations.csv`, `reports/api_check.md`, `reports/figures/api_vs_vadimkin.png`.
20	- Сырые ответы API `data/raw/alerts_in_ua/*.json` — читать можно, в сеть не ходить.
21	
22	`scripts/api_check.py` пересобирает всё (2–3 минуты) и пишет в `reports/api_check.md` и `data/alerts_in_ua_locations.csv`. Не запускай его: для пересчёта копируй нужные куски в scratch, без записи файлов.
23	
24	## Что проверить
25	
26	1. **Адаптер.**
27	   - Сопоставление 119 локаций: апострофы, Киев, переименования.
28	   - Записи уровня области разворачиваются на районы. Нет ли двойного счёта, если для тех же районов есть и районные записи?
29	   - Тревоги, открытые на момент скачивания; отброшенные типы и уровни; объединение по `id` и `updated_at`.
30	2. **Окно `month_ago`.**
31	   - По какому полю API обрезает историю: по началу или по концу? Что происходит с тревогами, начавшимися до окна?
32	   - Верно ли выбраны `work_start`, разогрев и `data_end` в `api_config`?
33	   - Часть `test` начинается по
… [обрезано: показано 3000 из 8899 символов]
```

</details>

<details><summary>🔧 Bash: List project structure and file sizes · 20:19</summary>

**Аргументы**

```bash
ls && ls reviews reviews/scratch 2>/dev/null; wc -l PLAN.md DECISIONS.md README.md src/alerts/ingest/alerts_in_ua.py src/alerts/api_check.py scripts/api_check.py scripts/fetch_alerts_in_ua.py config.yaml reports/api_check.md; ls src/alerts src/alerts/ingest tests data data/raw/alerts_in_ua | head -100
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
   127 src/alerts/ingest/alerts_in_ua.py
   193 src/alerts/api_check.py
   214 scripts/api_check.py
   123 scripts/fetch_alerts_in_ua.py
   110 config.yaml
   263 reports/api_check.md
  2305 total
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

data/raw/alerts_in_ua:
10_20261011T084839Z.json
11_20261011T084910Z.json
12_20261011T084941Z.json
13_20261011T085013Z.json
14_20261011T085044Z.json
15_20261011T085115Z.json
16_20261011T085146Z.json
17_20261011T085218Z.json
18_20261011T085249Z.json
19_20261011T085320Z.json
20_20261011T085351Z.json
21_20261011T085423Z.json
22_20261011T084539Z.json
22_20261011T085454Z.json
23_20261011T085525Z.json
24_20261011T085557Z.json
25_20261011T085628Z.json
26_20261011T085659Z.json
27_20261011T085730Z.json
28_20261011T085802Z.json
29_20261011T085833Z.json
30_20261011T085904Z.json
31_20261011T085935Z.json
3_20261011T084602Z.json
4_20261011T084634Z.json
5_20261011T084705Z.json
8_20261011T084736Z.json
9_20261011T084807Z.json
manifest.jsonl

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

src/alerts/ingest:
__init__.py
__pycache__
alerts_in_ua.py
vadimkin.py

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
 "offset": 1,
 "limit": 60
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
… [обрезано: показано 3000 из 5878 символов]
```

</details>

<details><summary>🔧 Read: PLAN.md · 20:19</summary>

**Аргументы**

```json
{
 "file_path": "d:\\Flash\\golova\\KSE_AI\\AAFS\\PLAN.md",
 "offset": 228,
 "limit": 196
}
```

**Результат**

```
228	### Этап 7. Отчёт — выполнено
229	
230	**Как сделано:** `README.md`; таблица «модель × горизонт» с интервалами — `reports/results.md` (бэктест для h = 1, 3, 6); калибровка — `reports/figures/calibration_h{1,3,6}.png`; разбивка по областям — `reports/backtest_h*.md`; «прогноз против факта» — `reports/figures/forecast_vs_fact.png` (первая неделя теста; Киев, Одесский и Днепровский районы: крупные города с тихими промежутками). Графики — в `src/alerts/figures.py`. LightGBM лучше B1 на всех горизонтах: PR-AUC +0.036 / +0.027 / +0.018.
231	
232	**Исходное задание:**
233	
234	- Таблица «модель × горизонт» с доверительными интервалами бутстрепа.
235	- Калибровочные кривые.
236	- Разбивка метрик по областям.
237	- График «прогноз против факта» для 2–3 единиц в тестовом периоде.
238	- README: постановка, снимок данных и почему он заканчивается 7 сентября, ключевые решения, результаты, ограничения (угрозы, правый край, маска), запуск одной командой.
239	- Наблюдение для README: на востоке и в центре районная дифференциация реально работает, на западе районы в основном объявляются вместе (D07).
240	
241	### Этап 8. Проверка на свежих данных alerts.in.ua (после этапа 7) — выполнено
242	
243	**Как сделано:** скачивание — `scripts/fetch_alerts_in_ua.py` (11.10, 28 запросов, все 200); адаптер — `src/alerts/ingest/alerts_in_ua.py` (119 из 119 локаций; апостроф и Киев — D22); проверка — `scripts/api_check.py` и `src/alerts/api_check.py`, отчёт — `reports/api_check.md`; решения и цифры — D22. Сверх плана — B1, обновляемый на данных API: без него выигрыш замороженной модели был бы завышен втрое. Итог: против обновляемого B1 модель, замороженная месяц назад, сохраняет преимущество при h = 1 и 3 (PR-AUC +0.052 и +0.021), при h = 6 — нет. **Повторное скачивание в понедельник** объединится по `id` автоматически: `python scripts/fetch_alerts_in_ua.py --all-oblasts`, затем `python scripts/api_check.py`.
244	
245	**Исходное задание:**
246	
247	**Зачем.** Основной тест заканчивается 7 сентября (D02). API alerts.in.ua даёт историю примерно за последний месяц, то есть с 11 сентября по сегодня. Это проверка, сохраняется ли преимущество модели **через месяц и на другом источнике**. Основной тест (D18, D20) не меняется, источники не склеиваются (D02).
248	
249	**Что известно из документации** (`devs.alerts.in.ua`):
250	- история: `GET /v1/regions/{uid}/alerts/month_ago.json`, только период `month_ago` («місяць від поточної дати»); `uid` — область, район или громада;
251	- лимит для истории — **2 запроса в минуту** (общий: 8–10 мягкий, 12 жёсткий; за систематические нарушения блокируют IP и токен); кешировать через `If-Modified-Since`;
252	- поля записи: `id`, `location_title`, `location_type` (oblast / raion / city / hromada / unknown), `location_uid`, `location_oblast`, `location_raion`, `started_at`, `finished_at` (`null`, если тревога идёт), `updated_at`, `alert_type` (air_raid / artillery_shelling / urban_fights / chemical / nuclear), `notes`;
253	- время в ISO 8601 с с
… [обрезано: показано 3000 из 19120 символов]
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
 "offset": 1,
 "limit": 60
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
… [обрезано: показано 3000 из 3731 символов]
```

</details>

<details><summary>🔧 Read: DECISIONS.md · 20:19</summary>

**Аргументы**

```json
{
 "file_path": "d:\\Flash\\golova\\KSE_AI\\AAFS\\DECISIONS.md",
 "offset": 560,
 "limit": 145
}
```

**Результат**

```
560	
561	---
562	
563	## D21. Признаки видят только то, что было известно: закрытый доступ и проверка знания
564	
565	**Проблема (вопрос пользователя после этапа 6):** при добавлении признака нужно помнить, какую таблицу брать. `intervals`, эпизоды, маски и `uncertain` — сторона цели, они восстановлены задним числом. Признакам можно только то, что было известно к `t`: `seen` и начала эпизодов. А `FeatureBuilder` получал сырые таблицы, так что ошибиться было легко. Хуже того, тест «порча будущего» (D18) такую ошибку не ловит: признак, читающий `end_utc` выдуманного конца, даёт одинаковый ответ в обеих версиях, потому что запись лежит *до* среза. Проверено подменой: тест с утечкой из D16 проходит.
566	
567	**Решение:**
568	1. **Закрытый доступ.** `FeatureBuilder(history, units, neighbors, cfg)` получает только `AlertHistory`, собранную в `pipeline.alert_history()`. Сырые таблицы ему недоступны. В `AlertHistory` добавлен `seconds_since_start`, чтобы новым признакам не требовался прямой доступ к таблицам. Правило одно: признаки — только через `AlertHistory`.
569	2. **Проверка знания на момент среза** (`leakage.known_at`, `leakage.knowledge_check`). Она воспроизводит, что лежало в датасете к моменту среза:
570	   - запись с настоящим отбоем появляется в момент отбоя, а запись с выдуманным концом — только при следующем начале своей локации (правило процессора, D16);
571	   - тревога, ещё открытая в срезе, видна как открытая. Её конец ставится в «срез + 1 с»: конец в далёком будущем создал бы ложный перерыв канала сразу после последнего события.
572	
573	   Признаки всех строк сетки за 7 дней до среза, посчитанные по такому знанию, должны совпасть с посчитанными по полным данным бит в бит. Тест не зависит от конкретных признаков: каждый новый признак проверяется автоматически.
574	
575	**Проверка проверки:**
576	- `tests/test_knowledge.py` падает на утечке из D16 (подмена `build_seen` старым поведением: расходится `oblasts_active`), а `tests/test_leakage.py` на той же подмене проходит. Тесты дополняют друг друга: один ловит будущее после среза, другой — записи, написанные позже своих меток времени.
577	- На реальных данных проверка выполняется в `run_all.py` в обоих срезах: 14 450 и 14 715 строк, в момент среза были открыты 31 и 24 тревоги. Признаки совпали.
578	
579	**Почему не одна таблица и не полный двухвременной журнал:**
580	- `seen` и `intervals` отвечают на разные вопросы; одна таблица со смешанным смыслом опаснее двух.
581	- Двухвременной журнал (у события время и момент, когда о нём узнали) — принципиально правильное направление, и `seen` в нём получался бы автоматически. Но это крупная перестройка, а проверка знания даёт почти ту же защиту. Записано во «Вне MVP».
582	
583	**Попутно:** графики вынесены из `report.py` и `evaluation.py` в `src/alerts/figures.py`; картинки после переноса совпали побайтно. Старые файлы этапа 1 (ветка Gemini Flash, одноразовый скрипт этапа 1б) перенесены в `archive/` с пояснением.
584	
585	**Статус:** зафиксировано
… [обрезано: показано 3000 из 19329 символов]
```

</details>

<details><summary>🔧 Bash: Read alerts_in_ua adapter · 20:20</summary>

**Аргументы**

```bash
cat -n src/alerts/ingest/alerts_in_ua.py
```

**Результат**

```
1	"""alerts.in.ua history -> records in the schema of load_official (PLAN stage 8, D22).
     2	
     3	Raw responses (scripts/fetch_alerts_in_ua.py) are merged by `id`; when an alert was downloaded more
     4	than once, the version with the later `updated_at` wins. Only `air_raid` alerts are kept.
     5	Locations are matched by their Ukrainian names through data/alerts_in_ua_locations.csv
     6	(build_locations): Vadimkin publishes the same records in English and in Ukrainian row by row, so
     7	the English keys of our units get their Ukrainian names from official_data_uk.csv; raions renamed
     8	in 2023-2024 take the new name from the boundaries (geo.renames + adm2_name1).
     9	
    10	Levels: `raion` records map to raions; Kyiv city (`м. Київ`) maps to the Kyiv City unit whatever
    11	its location_type; `oblast` records are expanded to every raion of the oblast; `city` and `hromada`
    12	records are dropped, as hromadas in D08. An alert still open at download time (finished_at = null)
    13	ends at the request time of its file, which lies after data_end of this source.
    14	"""
    15	import json
    16	from pathlib import Path
    17	
    18	import numpy as np
    19	import pandas as pd
    20	
    21	from alerts.config import ROOT
    22	from alerts.ingest.vadimkin import file_sha256
    23	
    24	KYIV_UK = 'м. Київ'
    25	# Vadimkin writes the apostrophe as U+2019, the API as U+0027 ("Кам'янський район"): match on a normal form
    26	APOSTROPHES = str.maketrans({c: "'" for c in '’ʼ‘`′'})
    27	COLUMNS = ['oblast', 'raion', 'hromada', 'level', 'started_at', 'finished_at', 'duration', 'source']
    28	
    29	
    30	def norm(name: pd.Series) -> pd.Series:
    31	    return name.str.translate(APOSTROPHES).str.strip()
    32	
    33	
    34	def _utc(s: pd.Series) -> pd.Series:
    35	    return pd.to_datetime(s, utc=True, format='ISO8601').dt.floor('s').dt.as_unit('s')
    36	
    37	
    38	def read_raw(raw_dir) -> pd.DataFrame:
    39	    """All downloaded alerts, one row per id (latest updated_at), with the request time of its file."""
    40	    frames = []
    41	    for f in sorted(Path(raw_dir).glob('*_*.json')):
    42	        body = json.loads(f.read_text(encoding='utf-8'))
    43	        a = pd.DataFrame(body['alerts'])
    44	        a['requested_utc'] = pd.to_datetime(f.stem.split('_', 1)[1], format='%Y%m%dT%H%M%SZ', utc=True).as_unit('s')
    45	        a['file'] = f.name
    46	        frames.append(a)
    47	    if not frames:
    48	        raise FileNotFoundError(f'no responses in {raw_dir}: run scripts/fetch_alerts_in_ua.py')
    49	    a = pd.concat(frames, ignore_index=True)
    50	    for c in ['started_at', 'finished_at', 'updated_at']:
    51	        a[c] = _utc(a[c])
    52	    a = a.sort_values(['id', 'updated_at', 'requested_utc']).drop_duplicates('id', keep='last')
    53	    return a.reset_index(drop=True)
    54	
    55	
    56	def build_loc
… [обрезано: показано 3000 из 8198 символов]
```

</details>

<details><summary>🔧 Bash: Read api_check module · 20:20</summary>

**Аргументы**

```bash
cat -n src/alerts/api_check.py
```

**Результат**

```
1	"""Stage 8: frozen models on fresh alerts.in.ua data (PLAN stage 8, D22). Computation only.
     2	
     3	The two sources are never joined (D02): models are fitted once on Vadimkin rows and then only
     4	predict; features on the API period are computed from API data alone, through the same AlertHistory.
     5	"""
     6	import copy
     7	import hashlib
     8	import io
     9	import subprocess
    10	
    11	import numpy as np
    12	import pandas as pd
    13	
    14	from alerts.config import ROOT
    15	from alerts.intervals import episodes
    16	from alerts.metrics import bootstrap
    17	from alerts.scope import ROLE_TARGET
    18	from alerts.spans import union
    19	from alerts.timeutil import to_sec
    20	
    21	KYIV = 'Europe/Kyiv'
    22	
    23	
    24	# --- source profile (8.3) ------------------------------------------------------------------
    25	def api_config(cfg: dict, raw: pd.DataFrame, window_days: int = 30) -> dict:
    26	    """Config of the API source: processor rules off, its own periods.
    27	
    28	    data_end: the earliest request time floored to the hour. The history covers about `window_days`
    29	    before each request; the latest such start, ceiled to midnight, opens the period, and the first
    30	    week is the feature warm-up. Everything after the warm-up is the evaluation ("test") part.
    31	    """
    32	    c = copy.deepcopy(cfg)
    33	    first, last = raw['requested_utc'].min(), raw['requested_utc'].max()
    34	    start = (last - pd.Timedelta(days=window_days)).ceil('D')
    35	    warm = start + pd.Timedelta(days=7)
    36	    c['processor']['enabled'] = False
    37	    c['data_end'] = first.floor('h').isoformat()
    38	    c['periods'] = {'work_start': start.isoformat(), 'warmup_end': warm.isoformat(),
    39	                    'train_end': warm.isoformat(), 'val_end': warm.isoformat()}
    40	    c['scope']['excluded_oblasts'] = []        # Luhansk is not among the mapped locations at all
    41	    return c
    42	
    43	
    44	# --- comparison of sources without models (8.4) -------------------------------------------
    45	def unit_profile(art, lo: pd.Timestamp, hi: pd.Timestamp) -> pd.DataFrame:
    46	    """Per target unit on [lo, hi): alerts per day, share of time under alert, median duration."""
    47	    days = (hi - lo).total_seconds() / 86400
    48	    ep = episodes(art.intervals)
    49	    ep = ep[(ep['start_utc'] >= lo) & (ep['start_utc'] < hi)]
    50	    iv = art.intervals
    51	    s = iv['start_utc'].where(iv['start_utc'] > lo, lo)
    52	    e = iv['end_utc'].where(iv['end_utc'] < hi, hi)
    53	    cover = ((e - s).dt.total_seconds().clip(lower=0)).groupby(iv['unit_id']).sum() / (days * 86400)
    54	    tgt = art.units.loc[art.units['role'] == ROLE_TARGET].drop_duplicates('unit_id').set_index('unit_id')
    55	    out = pd.DataFrame({'oblast': tgt['oblast'], 'unit_name': tgt['unit_name']})
    5
… [обрезано: показано 3000 из 11794 символов]
```

</details>

<details><summary>🔧 Bash: Read api_check script · 20:20</summary>

**Аргументы**

```bash
cat -n scripts/api_check.py
```

**Результат**

```
1	"""Stage 8: check the frozen models on fresh alerts.in.ua data (PLAN stage 8, D22).
     2	
     3	    python scripts/fetch_alerts_in_ua.py --all-oblasts     # needs your own token
     4	    python scripts/api_check.py
     5	
     6	Needs the main pipeline outputs (python scripts/run_all.py): units, neighbours, tuned hyperparameters.
     7	Writes data/alerts_in_ua_locations.csv and reports/api_check.md; raw API data stay in the git-ignored
     8	data/raw/alerts_in_ua.
     9	"""
    10	import json
    11	import logging
    12	import sys
    13	import time
    14	from pathlib import Path
    15	
    16	sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
    17	
    18	import numpy as np  # noqa: E402
    19	import pandas as pd  # noqa: E402
    20	
    21	from alerts import api_check as ac  # noqa: E402
    22	from alerts import figures, leakage, store  # noqa: E402
    23	from alerts.config import ROOT, load_config, path, ts  # noqa: E402
    24	from alerts.backtest import walk_forward  # noqa: E402
    25	from alerts.ingest.alerts_in_ua import KYIV_UK, build_locations, load_alerts_in_ua, norm, read_raw  # noqa: E402
    26	from alerts.metrics import bootstrap  # noqa: E402
    27	from alerts.models.baselines import UnitHourRate  # noqa: E402
    28	from alerts.metrics import METRICS  # noqa: E402
    29	from alerts.models import registry  # noqa: E402
    30	from alerts.pipeline import build_all, build_tables, model_data  # noqa: E402
    31	
    32	logger = logging.getLogger('api_check')
    33	
    34	
    35	def main() -> int:
    36	    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(name)s: %(message)s')
    37	    t0 = time.time()
    38	    cfg = load_config()
    39	    out = path(cfg, 'reports')
    40	    md = ['# Check on fresh data: alerts.in.ua (stage 8)', '',
    41	          'Generated by `scripts/api_check.py`. Decisions: DECISIONS.md, D22. The sources are not joined (D02): '
    42	          'models are fitted once on the Vadimkin data and only predict here.', '']
    43	
    44	    # 8.1-8.2: raw data, locations, adapter
    45	    raw_dir = ROOT / cfg['api']['raw_dir']
    46	    manifest = pd.read_json(raw_dir / 'manifest.jsonl', lines=True)
    47	    raw = read_raw(raw_dir)
    48	    units = store.load_units(cfg)
    49	    neighbors = pd.read_csv(path(cfg, 'neighbors'))
    50	    locations = build_locations(units, cfg)
    51	    locations.to_csv(ROOT / 'data' / 'alerts_in_ua_locations.csv', index=False)
    52	    recs, st = load_alerts_in_ua(raw, locations)
    53	    have = set(zip(recs['oblast'], recs['raion'].fillna(recs['oblast'])))
    54	    missing = [k for k in zip(locations['oblast'], locations['raion']) if k not in have]
    55	    api_names = raw[(raw['location_type'] == 'raion') | (raw['location_title'] == KYIV_UK)]
    56	    api_names = api_names.drop_duplicates(['location_oblast', 'location_title'])
    57	   
… [обрезано: показано 3000 из 16054 символов]
```

</details>

<details><summary>🔧 Bash: Read fetch script and config · 20:20</summary>

**Аргументы**

```bash
cat -n scripts/fetch_alerts_in_ua.py; cat -n config.yaml
```

**Результат**

```
1	"""Download alert history from the alerts.in.ua API as is (PLAN 8.1, D22).
     2	
     3	    python scripts/fetch_alerts_in_ua.py --uids 22         # one oblast first: look at location_type
     4	    python scripts/fetch_alerts_in_ua.py --all-oblasts     # the 27 oblast uids, about 14 minutes
     5	
     6	The token is read from the environment variable named in config.api.token_env, or else from the
     7	git-ignored file config.api.token_file. It is sent only in the Authorization header and is never
     8	printed or written anywhere. Responses are saved unchanged to
     9	data/raw/alerts_in_ua/<uid>_<request time UTC>.json (git-ignored: publication terms are not
    10	defined); a manifest line per request records status, size and the Last-Modified header.
    11	
    12	Rate limits (devs.alerts.in.ua): history endpoints 2 requests per minute; systematic violations
    13	block the IP and the token. Hence a pause of config.api.pause_seconds between requests, a stop on
    14	401/403, and at most one retry after 429.
    15	"""
    16	import argparse
    17	import json
    18	import logging
    19	import os
    20	import sys
    21	import time
    22	import urllib.error
    23	import urllib.request
    24	from datetime import datetime, timezone
    25	from pathlib import Path
    26	
    27	sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
    28	
    29	from alerts.config import ROOT, load_config  # noqa: E402
    30	
    31	logger = logging.getLogger('fetch_alerts_in_ua')
    32	
    33	
    34	class Stop(Exception):
    35	    """An answer after which no further request may be sent (bad token, blocked IP)."""
    36	
    37	
    38	def read_token(api: dict) -> str:
    39	    token = os.environ.get(api['token_env'], '').strip()
    40	    if not token:
    41	        p = ROOT / api['token_file']
    42	        token = p.read_text(encoding='utf-8').strip() if p.exists() else ''
    43	    if not token:
    44	        raise Stop(f"no token: set {api['token_env']} or put it into {api['token_file']}")
    45	    return token
    46	
    47	
    48	def get(url: str, token: str, if_modified_since: str | None = None) -> tuple[int, bytes, dict]:
    49	    headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/json',
    50	               'User-Agent': 'AAFS research script (one-off history download)'}
    51	    if if_modified_since:
    52	        headers['If-Modified-Since'] = if_modified_since
    53	    req = urllib.request.Request(url, headers=headers)
    54	    try:
    55	        with urllib.request.urlopen(req, timeout=60) as r:
    56	            return r.status, r.read(), dict(r.headers)
    57	    except urllib.error.HTTPError as e:              # the message never contains the token
    58	        return e.code, e.read(), dict(e.headers)
    59	
    60	
    61	def fetch(uids: list, cfg: dict) -> list[dict]:
    62	    api = cfg['api']
    63	    token = read_token(api)
    64	    out_dir = ROOT 
… [обрезано: показано 3000 из 12322 символов]
```

</details>

<details><summary>🔧 Bash: Read api_check report · 20:20</summary>

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

<details><summary>🔧 Bash: Read README · 20:20</summary>

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

<details><summary>🔧 Bash: Read pipeline module · 20:20</summary>

**Аргументы**

```bash
wc -l src/alerts/*.py src/alerts/models/*.py && cat -n src/alerts/pipeline.py
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
    18 src/alerts/models/__init__.py
    81 src/alerts/models/baselines.py
    94 src/alerts/models/learned.py
  2486 total
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
    
… [обрезано: показано 3000 из 5594 символов]
```

</details>

<details><summary>🔧 Bash: Read scope, processor, mask modules · 20:20</summary>

**Аргументы**

```bash
cat -n src/alerts/scope.py src/alerts/processor.py src/alerts/mask.py
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
… [обрезано: показано 3000 из 13608 символов]
```

</details>

<details><summary>🔧 Bash: Read features and history modules · 20:20</summary>

**Аргументы**

```bash
cat -n src/alerts/features.py src/alerts/history.py
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
… [обрезано: показано 3000 из 14505 символов]
```

</details>

<details><summary>🔧 Bash: Read intervals and grid modules · 20:20</summary>

**Аргументы**

```bash
cat -n src/alerts/intervals.py src/alerts/grid.py
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
… [обрезано: показано 3000 из 14663 символов]
```

</details>

<details><summary>🔧 Bash: Inspect manifest and raw JSON structure · 20:20</summary>

**Аргументы**

```bash
cat data/raw/alerts_in_ua/manifest.jsonl | head -40; ls -la data/raw/alerts_in_ua | head -5; python -c "
import json;d=json.load(open('data/raw/alerts_in_ua/22_20261011T084539Z.json',encoding='utf-8'));print(list(d.keys()));print({k:(v if k!='alerts' else len(v)) for k,v in d.items()});print(json.dumps(d['alerts'][:3],ensure_ascii=False,indent=1))"
```

**Результат** (ошибка)

```
Exit code 1
{"uid": "22", "status": 200, "requested_utc": "2026-10-11T08:45:39.672979+00:00", "bytes": 1034093, "last_modified": null, "file": "22_20261011T084539Z.json", "alerts": 2373}
{"uid": "3", "status": 200, "requested_utc": "2026-10-11T08:46:02.785124+00:00", "bytes": 86410, "last_modified": null, "file": "3_20261011T084602Z.json", "alerts": 197}
{"uid": "4", "status": 200, "requested_utc": "2026-10-11T08:46:34.127459+00:00", "bytes": 207662, "last_modified": null, "file": "4_20261011T084634Z.json", "alerts": 489}
{"uid": "5", "status": 200, "requested_utc": "2026-10-11T08:47:05.426546+00:00", "bytes": 133371, "last_modified": null, "file": "5_20261011T084705Z.json", "alerts": 315}
{"uid": "8", "status": 200, "requested_utc": "2026-10-11T08:47:36.636201+00:00", "bytes": 59617, "last_modified": null, "file": "8_20261011T084736Z.json", "alerts": 140}
{"uid": "9", "status": 200, "requested_utc": "2026-10-11T08:48:07.792519+00:00", "bytes": 1043015, "last_modified": null, "file": "9_20261011T084807Z.json", "alerts": 2290}
{"uid": "10", "status": 200, "requested_utc": "2026-10-11T08:48:39.177795+00:00", "bytes": 220212, "last_modified": null, "file": "10_20261011T084839Z.json", "alerts": 512}
{"uid": "11", "status": 200, "requested_utc": "2026-10-11T08:49:10.392238+00:00", "bytes": 7804, "last_modified": null, "file": "11_20261011T084910Z.json", "alerts": 18}
{"uid": "12", "status": 200, "requested_utc": "2026-10-11T08:49:41.527852+00:00", "bytes": 530357, "last_modified": null, "file": "12_20261011T084941Z.json", "alerts": 1205}
{"uid": "13", "status": 200, "requested_utc": "2026-10-11T08:50:13.264271+00:00", "bytes": 18796, "last_modified": null, "file": "13_20261011T085013Z.json", "alerts": 42}
{"uid": "14", "status": 200, "requested_utc": "2026-10-11T08:50:44.407994+00:00", "bytes": 618910, "last_modified": null, "file": "14_20261011T085044Z.json", "alerts": 1460}
{"uid": "15", "status": 200, "requested_utc": "2026-10-11T08:51:15.713309+00:00", "bytes": 507192, "last_modified": null, "file": "15_20261011T085115Z.json", "alerts": 1096}
{"uid": "16", "status": 200, "requested_utc": "2026-10-11T08:51:46.973228+00:00", "bytes": 554, "last_modified": null, "file": "16_20261011T085146Z.json", "alerts": 1}
{"uid": "17", "status": 200, "requested_utc": "2026-10-11T08:52:18.137815+00:00", "bytes": 413136, "last_modified": null, "file": "17_20261011T085218Z.json", "alerts": 954}
{"uid": "18", "status": 200, "requested_utc": "2026-10-11T08:52:49.400442+00:00", "bytes": 372293, "last_modified": null, "file": "18_20261011T085249Z.json", "alerts": 875}
{"uid": "19", "status": 200, "requested_utc": "2026-10-11T08:53:20.723693+00:00", "bytes": 325015, "last_modified": null, "file": "19_20261011T085320Z.json", "alerts": 760}
{"uid": "20", "status": 200, "requested_utc": "2026-10-11T08:53:51.999089+00:00", "bytes": 440247, "last_modified": null, "file": "20_20261011T085351Z.json", "alerts": 1057}
{"uid": "21", "status": 200, "requested_utc"
… [обрезано: показано 3000 из 5709 символов]
```

</details>

<details><summary>🔧 Bash: Create scratch dir and check environment · 20:20</summary>

**Аргументы**

```bash
mkdir -p reviews/scratch/stage8 && ls reviews/scratch/ && git status --short | head -20 && python --version && python -c "import pandas, numpy, lightgbm; print(pandas.__version__, numpy.__version__, lightgbm.__version__)"
```

**Результат**

```
stage5-leakage
stage8
Python 3.12.9
3.0.6 2.5.3 4.7.0
```

</details>

<details><summary>🔧 Write: reviews/scratch/stage8/a01_raw.py · 20:21</summary>

**Аргументы**

```
# file: reviews/scratch/stage8/a01_raw.py
"""Stage 8 review: raw API responses - window, open alerts, types, levels, updated_at."""
import json
from pathlib import Path

import pandas as pd

from alerts.config import ROOT, load_config
from alerts.ingest.alerts_in_ua import read_raw

pd.set_option('display.width', 250)
pd.set_option('display.max_columns', 30)
pd.set_option('display.max_rows', 200)

cfg = load_config()
raw_dir = ROOT / cfg['api']['raw_dir']

# per file: meta, min/max started_at, finished_at, updated_at
rows = []
for f in sorted(raw_dir.glob('*_*.json')):
    body = json.loads(f.read_text(encoding='utf-8'))
    a = pd.DataFrame(body['alerts'])
    req = pd.to_datetime(f.stem.split('_', 1)[1], format='%Y%m%dT%H%M%SZ', utc=True)
    r = {'file': f.name, 'n': len(a), 'meta': body.get('meta'), 'req': req}
    if len(a):
        for c in ['started_at', 'finished_at', 'updated_at']:
            a[c] = pd.to_datetime(a[c], utc=True, format='ISO8601')
        ar = a[a['alert_type'] == 'air_raid']
        closed = ar[ar['finished_at'].notna()]
        r.update(min_start=ar['started_at'].min(), min_start_closed=closed['started_at'].min(),
                 min_fin=closed['finished_at'].min(), min_upd=ar['updated_at'].min(),
                 open=int(ar['finished_at'].isna().sum()),
                 oblast_title=a['location_oblast'].mode().iat[0] if len(a) else None)
    rows.append(r)
pf = pd.DataFrame(rows)
print(pf[['file', 'n', 'req', 'min_start', 'min_start_closed', 'min_fin', 'min_upd', 'open']].to_string())
print(pf[['file', 'meta']].to_string())

raw = read_raw(raw_dir)
print('\nunique ids', len(raw), 'columns', list(raw.columns))
print(raw['alert_type'].value_counts())
print(raw.groupby(['alert_type', 'location_type']).size())

ar = raw[raw['alert_type'] == 'air_raid']
# window: earliest start of closed alerts relative to request time
req = ar['requested_utc']
lag_start = (req - ar['started_at']).dt.total_seconds() / 86400
lag_fin = (req - ar['finished_at
… [обрезано: показано 2000 из 3527 символов]
```

**Результат**

```
File created successfully at: d:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage8\a01_raw.py (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Bash: Run raw data exploration script · 20:21</summary>

**Аргументы**

```bash
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage8/a01_raw.py 2>&1 | head -250
```

**Результат**

```
file     n                       req                        min_start                 min_start_closed                   min_fin                          min_upd  open
0   10_20261011T084839Z.json   512 2026-10-11 08:48:39+00:00 2026-09-11 08:53:24.559000+00:00 2026-09-11 08:53:24.559000+00:00 2026-09-11 10:06:11+00:00 2026-09-11 10:06:21.372000+00:00   0.0
1   11_20261011T084910Z.json    18 2026-10-11 08:49:10+00:00 2026-09-15 16:44:25.822000+00:00 2026-09-15 16:44:25.822000+00:00 2026-09-15 17:09:02+00:00 2026-09-15 17:09:03.125000+00:00   0.0
2   12_20261011T084941Z.json  1205 2026-10-11 08:49:41+00:00 2026-09-11 05:05:29.202000+00:00 2026-09-11 05:05:29.202000+00:00 2026-09-11 11:34:33+00:00 2026-09-11 11:34:33.403000+00:00   7.0
3   13_20261011T085013Z.json    42 2026-10-11 08:50:13+00:00 2026-09-12 22:00:05.164000+00:00 2026-09-12 22:00:05.164000+00:00 2026-09-12 22:14:27+00:00 2026-09-12 22:14:27.575000+00:00   0.0
4   14_20261011T085044Z.json  1460 2026-10-11 08:50:44+00:00 2026-09-11 08:38:20.363000+00:00 2026-09-11 08:38:20.363000+00:00 2026-09-11 09:49:56+00:00 2026-09-11 09:49:56.494000+00:00   7.0
5   15_20261011T085115Z.json  1096 2026-10-11 08:51:15+00:00 2026-09-11 07:37:17.743000+00:00 2026-09-11 07:37:17.743000+00:00 2026-09-11 09:26:38+00:00 2026-09-11 09:26:43.132000+00:00   2.0
6   16_20261011T085146Z.json     1 2026-10-11 08:51:46+00:00        2022-04-04 16:45:39+00:00                              NaT                       NaT 2023-10-29 18:22:37.357000+00:00   1.0
7   17_20261011T085218Z.json   954 2026-10-11 08:52:18+00:00 2026-09-11 08:16:27.293000+00:00 2026-09-11 08:16:27.293000+00:00 2026-09-11 09:09:27+00:00 2026-09-11 09:09:37.790000+00:00   0.0
8   18_20261011T085249Z.json   875 2026-10-11 08:52:49+00:00 2026-09-11 08:43:54.001000+00:00 2026-09-11 08:43:54.001000+00:00 2026-09-11 09:09:27+00:00 2026-09-11 09:09:37.894000+00:00   0.0
9   19_20261011T085320Z.json   760 2026-10-11 08:53:20+00:00 2026-09-11 07:37:17.643000+00:00 2026-09-11 07:37:17.643000+00:00 2026-09-11 09:26:38+00:00 2026-09-11 09:26:43.026000+00:00   4.0
10  20_20261011T085351Z.json  1057 2026-10-11 08:53:51+00:00 2026-09-11 06:28:15.950000+00:00 2026-09-11 06:28:15.950000+00:00 2026-09-11 09:46:03+00:00 2026-09-11 09:46:03.156000+00:00   3.0
11  21_20261011T085423Z.json   126 2026-10-11 08:54:23+00:00 2026-09-12 21:19:51.612000+00:00 2026-09-12 21:19:51.612000+00:00 2026-09-12 22:14:27+00:00 2026-09-12 22:14:27.499000+00:00   0.0
12  22_20261011T084539Z.json  2373 2026-10-11 08:45:39+00:00        2026-03-10 14:01:38+00:00 2026-09-11 06:13:18.631000+00:00 2026-09-11 09:46:03+00:00 2026-09-11 09:46:03.219000+00:00   8.0
13  22_20261011T085454Z.json  2373 2026-10-11 08:54:54+00:00        2026-03-10 14:01:38+00:00 2026-09-11 06:13:18.631000+00:00 2026-09-11 09:46:03+00:00 2026-09-11 09:46:03.219000+00:00   8.0
14  23_20261011T085525Z.json   385 2026-10-11 08:55:25+00:00 2026-09-11 11:46:35.403000+00:00 2026-09-11 11:46:35.403000+00:00 20
… [обрезано: показано 3000 из 23784 символов]
```

</details>

<details><summary>🔧 Write: reviews/scratch/stage8/a02_updated.py · 20:22</summary>

**Аргументы**

```
# file: reviews/scratch/stage8/a02_updated.py
"""Stage 8 review: late updated_at, duplicates across files, notes, alert_level, location fields."""
import json

import numpy as np
import pandas as pd

from alerts.config import ROOT, load_config
from alerts.ingest.alerts_in_ua import read_raw

pd.set_option('display.width', 250)
pd.set_option('display.max_columns', 30)
pd.set_option('display.max_rows', 300)
pd.set_option('display.max_colwidth', 60)

cfg = load_config()
raw_dir = ROOT / cfg['api']['raw_dir']

# all rows before dedup
frames = []
for f in sorted(raw_dir.glob('*_*.json')):
    a = pd.DataFrame(json.loads(f.read_text(encoding='utf-8'))['alerts'])
    a['file'] = f.name
    frames.append(a)
allr = pd.concat(frames, ignore_index=True)
for c in ['started_at', 'finished_at', 'updated_at']:
    allr[c] = pd.to_datetime(allr[c], utc=True, format='ISO8601')
print('rows before dedup', len(allr), 'unique ids', allr['id'].nunique())
nfiles = allr.groupby('id')['file'].nunique()
print('ids in >1 file:', (nfiles > 1).sum())
multi = allr[allr['id'].isin(nfiles[nfiles > 1].index)]
print('files of multi-file ids:', multi.groupby('id')['file'].apply(lambda s: tuple(sorted(x.split('_')[0] for x in s))).value_counts().head(10))
# do versions differ between the two Kharkiv downloads?
k = allr[allr['file'].str.startswith('22_')]
kk = k.groupby('id').agg(n=('file', 'size'), f_n=('finished_at', 'nunique'), u_n=('updated_at', 'nunique'),
                         fin_null=('finished_at', lambda s: s.isna().sum()))
print('Kharkiv ids with differing updated_at between the two downloads', int((kk['u_n'] > 1).sum()),
      'differing finished', int((kk['f_n'] > 1).sum()), 'ids only in one', int((kk['n'] == 1).sum()))
print('NaT updated_at', int(allr['updated_at'].isna().sum()), 'NaT started', int(allr['started_at'].isna().sum()))

raw = read_raw(raw_dir)
print('\nnotes value counts:', raw['notes'].value_counts(dropna=False).head(10).to_dict())
print('alert_level:', raw['alert_level']
… [обрезано: показано 2000 из 5562 символов]
```

**Результат**

```
File created successfully at: d:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage8\a02_updated.py (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Bash: Run updated_at analysis script · 20:22</summary>

**Аргументы**

```bash
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage8/a02_updated.py 2>&1 | head -250
```

**Результат**

```
rows before dedup 18905 unique ids 16532
ids in >1 file: 2373
files of multi-file ids: file
(22, 22)    2373
Name: count, dtype: int64
Kharkiv ids with differing updated_at between the two downloads 0 differing finished 0 ids only in one 0
NaT updated_at 0 NaT started 0

notes value counts: {None: 13100, nan: 3427, '': 3, 'Згідно інформації з Офіційних карт тривог': 1, 'ukrainealarm: активна з 21:02 (Дронова загроза, жовтий), до нас не дійшла': 1}
alert_level: {'yellow': 10247, 'red': 6285}
country: {None: 16532}

air_raid: same (location_uid, started_at), different ids: 0
Empty DataFrame
Columns: [id, location_type, location_title, started_at, finished_at, updated_at]
Index: []
overlapping records within a raion/oblast location (start < previous end): 4
           location_title                started_at               finished_at                updated_at
716    Кальміуський район 2026-09-12 16:02:28+00:00 2026-09-12 16:16:22+00:00 2026-09-12 16:16:22+00:00
719   Краматорський район 2026-09-12 16:02:29+00:00 2026-09-12 16:16:22+00:00 2026-09-12 16:16:22+00:00
717  Маріупольський район 2026-09-12 16:02:29+00:00 2026-09-12 16:16:22+00:00 2026-09-12 16:16:22+00:00
718    Волноваський район 2026-09-12 16:02:29+00:00 2026-09-12 16:16:22+00:00 2026-09-12 16:16:22+00:00

closed air_raid 16189  by level {'raion': 14124, 'city': 924, 'hromada': 924, 'oblast': 217}
updated_at - finished_at quantiles (s): {0.0: 0.0, 0.01: 0.0, 0.5: 3.0, 0.9: 10.0, 0.99: 120.1, 0.999: 1257687.2, 1.0: 1670268.0}
updated_at < finished_at: 0
late (>1h) by level: {'raion': 57, 'city': 18, 'hromada': 18}
late raion: 57
                location_oblast          location_title                started_at               finished_at                updated_at      dur_min  upd_after_end_h notes
650           Черкаська область     Золотоніський район 2026-09-12 12:26:21+00:00 2026-09-12 17:53:25+00:00 2026-09-30 18:32:00+00:00   327.066667       432.643056  None
1642            Сумська область        Охтирський район 2026-09-15 00:19:46+00:00 2026-09-15 12:54:50+00:00 2026-09-30 18:32:00+00:00   755.066667       365.619444  None
1966          Черкаська область         Уманський район 2026-09-15 15:49:08+00:00 2026-09-15 17:12:06+00:00 2026-09-30 18:32:00+00:00    82.966667       361.331667  None
1967          Вінницька область       Гайсинський район 2026-09-15 15:52:12+00:00 2026-09-15 17:12:06+00:00 2026-09-30 18:32:00+00:00    79.900000       361.331667  None
1982           Київська область        Бучанський район 2026-09-15 16:23:23+00:00 2026-09-15 17:12:07+00:00 2026-09-30 18:32:00+00:00    48.733333       361.331389   NaN
2109            Сумська область          Сумський район 2026-09-15 18:27:57+00:00 2026-09-15 20:02:02+00:00 2026-09-30 18:32:00+00:00    94.083333       358.499444  None
2683       Миколаївська область     Миколаївський район 2026-09-16 22:18:16+00:00 2026-09-17 00:34:58+00:00 2026-09-30 18:32:00+00:00   136.700000       329.9505
… [обрезано: показано 3000 из 20848 символов]
```

</details>

<details><summary>🔧 Bash: Read DECISIONS D09-D12 · 20:24</summary>

**Аргументы**

```bash
sed -n 181,300p DECISIONS.md
```

**Результат**

```
## D09. Сообщения об угрозах в канале

**Находка** (по коду процессора и постам канала):
- Кроме постов «🔴 Повітряна тривога» и «🟢 Відбій», канал публикует посты «Загроза ударних БпЛА». Цвет маркера означает уровень: 🟠 — угроза, 🔴🔴 — «підвищений рівень небезпеки».
- Угрозы публикуются для конкретного города или громады и часто идут **внутри уже объявленной тревоги**. Пример: 08:49 тревога в Харькове, в 08:50 для той же громады 🟠 «БпЛА невизначеного типу».
- Процессор считает началом тревоги любой пост с «Повітряна» **или** 🔴 в первой строке. Последствия:
  - угроза с 🔴 записывается как начало тревоги, а с 🟠 — пропускается. Одинаковые по типу сообщения обрабатываются по-разному в зависимости от цвета;
  - если для места уже идёт тревога, начавшаяся меньше 3 часов назад, новое «начало» её перезаписывает. Настоящий момент начала теряется, тревога выглядит короче;
  - если у угрозы нет собственного «відбою», запись остаётся открытой до следующего «відбою» по этому месту. Это вероятный источник многодневных «тревог» в громадах Никопольского района (8–26 дней).
- Тревога и угроза — разные сигналы. Тревога — официальный сигнал для территории с парным отбоем. Угроза — уточнение того, что и где летит, внутри тревоги или рядом с ней.

**Проверка (вариант B из 1б.4, ручная выборка).** Просмотрены три страницы публичной веб-версии канала, по 20 постов: перед ID 338381 (последние посты, сентябрь 2026), 336000 и 320000. Итог:
- всего 60 постов, из них 6 угроз «Загроза ударних БпЛА» (5 с маркером 🔴🔴, 1 с 🟠);
- у всех 6 угроз хэштег уровня города и громады (`#м_Запоріжжя_та_Запорізька_територіальна_громада`, `#м_Харків_та_Харківська_територіальна_громада`);
- угроз с хэштегом района (`_район`) или области (`_область`) — **0**;
- все посты с хэштегами районов — это «Повітряна тривога» или «Відбій тривоги».

Попутно подтверждён механизм клонов (D07): один пост «Повітряна тривога в» перечисляет пять районов Запорожской области или три района Одесской, и процессор превращает его в пять или три одинаковые записи.

**Решение:** на районном уровне угрозы в данные не попадают; для MVP данные оставляем как есть. Искажения из-за угроз касаются уровня громад и городов, который мы не используем (D08).

**Ограничение:** выборка маленькая (60 постов, 3 момента времени). Полная проверка через Telethon (вариант A) не выполнялась; в README указать как ограничение.

**Ограничение (найдено при исправлении D16):** если отбой потерян, а новая тревога той же локации пришла в пределах 3 часов, процессор заменяет открытую тревогу новой, и начало первой из CSV исчезает. В реальном времени единица была под тревогой с первого начала, а в данных она выглядит тихой до второго. Следов в CSV нет, поэтому ни замаскировать, ни исправить это нельзя, а насколько это часто, без архива канала не узнать. В README — в ограничения.

**Статус:** зафиксировано по ручной выборке.

---

## D10. Длинные тревоги и «статус неизвестен»

**Находка:**
- Длительность в охвате: медиана 47 минут, 75-й перцентиль 1
… [обрезано: показано 3000 из 9537 символов]
```

</details>

<details><summary>🔧 Write: reviews/scratch/stage8/a03_level.py · 20:24</summary>

**Аргументы**

```
# file: reviews/scratch/stage8/a03_level.py
"""Stage 8 review: the alert_level field (yellow / red) that the adapter ignores."""
import json

import numpy as np
import pandas as pd

from alerts.config import ROOT, load_config
from alerts.ingest.alerts_in_ua import read_raw

pd.set_option('display.width', 250)
pd.set_option('display.max_columns', 30)
pd.set_option('display.max_rows', 300)
pd.set_option('display.max_colwidth', 80)

cfg = load_config()
raw = read_raw(ROOT / cfg['api']['raw_dir'])
ar = raw[raw['alert_type'] == 'air_raid'].copy()
ar['fin'] = ar['finished_at'].fillna(ar['requested_utc'])
ar['dur_min'] = (ar['fin'] - ar['started_at']).dt.total_seconds() / 60
print('alert_level x location_type (air_raid):')
print(pd.crosstab(ar['location_type'], ar['alert_level'], dropna=False))
print('\nalert_level x alert_type (all):')
print(pd.crosstab(raw['alert_type'], raw['alert_level'], dropna=False))

r = ar[ar['location_type'].isin(['raion']) | (ar['location_title'] == 'м. Київ')]
print('\nraion+Kyiv by level: duration quantiles (min)')
print(r.groupby('alert_level')['dur_min'].quantile([.1, .25, .5, .75, .9]).unstack().round(1))
print('\nby oblast: share red among raion+Kyiv records')
print(r.groupby('location_oblast')['alert_level'].apply(lambda s: (s == 'red').mean()).round(2).sort_values().to_string())

# by time: share red per week
r = r.assign(week=r['started_at'].dt.tz_convert('Europe/Kyiv').dt.to_period('W').astype(str))
print('\nshare red per week:', r.groupby('week')['alert_level'].apply(lambda s: round((s == 'red').mean(), 3)).to_dict())
# hour profile per level
kh = r['started_at'].dt.tz_convert('Europe/Kyiv').dt.hour
print('\nstarts by Kyiv hour and level:')
print(pd.crosstab(kh, r['alert_level']).T.to_string())

# do level changes create new records? consecutive records of the same location touching each other
r = r.sort_values(['location_uid', 'started_at'])
prev_end = r.groupby('location_uid')['fin'].shift(1)
prev_lvl = r.groupby('location_uid')['al
… [обрезано: показано 2000 из 3501 символов]
```

**Результат**

```
File created successfully at: d:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage8\a03_level.py (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Bash: Analyze alert_level field in API data · 20:24</summary>

**Аргументы**

```bash
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage8/a03_level.py 2>&1 | head -200
```

**Результат**

```
d:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage8\a03_level.py:32: UserWarning: Converting to PeriodArray/Index representation will drop timezone information.
  r = r.assign(week=r['started_at'].dt.tz_convert('Europe/Kyiv').dt.to_period('W').astype(str))
alert_level x location_type (air_raid):
alert_level     red  yellow
location_type              
city            592     337
hromada         509     423
oblast           18     202
raion          4888    9280

alert_level x alert_type (all):
alert_level          red  yellow
alert_type                      
air_raid            6007   10242
artillery_shelling   277       5
urban_fights           1       0

raion+Kyiv by level: duration quantiles (min)
             0.10  0.25  0.50   0.75   0.90
alert_level                                
red          17.1  26.4  55.0  149.1  357.9
yellow       12.8  22.0  41.4   81.4  156.3

by oblast: share red among raion+Kyiv records
location_oblast
Рівненська область           0.05
м. Київ                      0.07
Хмельницька область          0.07
Тернопільська область        0.07
Київська область             0.09
Волинська область            0.09
Чернігівська область         0.10
Миколаївська область         0.10
Житомирська область          0.12
Одеська область              0.15
Полтавська область           0.15
Кіровоградська область       0.16
Черкаська область            0.18
Вінницька область            0.19
Чернівецька область          0.26
Херсонська область           0.28
Львівська область            0.44
Івано-Франківська область    0.48
Харківська область           0.54
Сумська область              0.55
Запорізька область           0.58
Донецька область             0.72
Дніпропетровська область     0.84
Закарпатська область         1.00

share red per week: {'2026-09-07/2026-09-13': 0.459, '2026-09-14/2026-09-20': 0.436, '2026-09-21/2026-09-27': 0.311, '2026-09-28/2026-10-04': 0.309, '2026-10-05/2026-10-11': 0.274}

starts by Kyiv hour and level:
started_at    0    1    2    3    4    5    6    7    8    9    10   11   12   13   14   15   16   17   18   19   20   21   22   23
alert_level                                                                                                                        
red          227  263  272  234  188  126  107  208  198  165  123  170  133  335  215  149  240  162  214  383  335  170  143  144
yellow       350  278  386  369  322  302  347  346  417  438  369  347  286  334  410  452  360  458  610  599  558  381  343  419

gap to previous record of same location (s): share <= 5 s 0.0006  <= 60 s 0.0117  <= 15 min 0.1464
touching (<= 5 s) pairs by (prev level -> level):
alert_level  yellow
alert_level        
yellow            8
pairs within 15 min by (prev level -> level):
alert_level  red  yellow
alert_level             
red          572     457
yellow       341     736

groups of records starting in the same minute in one oblast, by leve
… [обрезано: показано 3000 из 6211 символов]
```

</details>

<details><summary>🔧 Bash: Read leakage and backtest modules · 20:25</summary>

**Аргументы**

```bash
cat -n src/alerts/leakage.py src/alerts/backtest.py
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
… [обрезано: показано 3000 из 10532 символов]
```

</details>

<details><summary>🔧 Bash: Read models and metrics modules · 20:25</summary>

**Аргументы**

```bash
cat -n src/alerts/models/__init__.py src/alerts/models/baselines.py src/alerts/models/learned.py src/alerts/metrics.py
```

**Результат**

```
1	"""Model registry: name -> factory of a fresh unfitted model with fit(X, y) / predict_proba(X)."""
     2	from alerts.models.baselines import BASELINES
     3	from alerts.models.learned import LEARNED
     4	
     5	
     6	def registry(cfg: dict, names: list, params: dict | None = None) -> dict:
     7	    """Factories for the named models. Learned models need their tuned `params[name]`."""
     8	    out = {}
     9	    for name in names:
    10	        if name in BASELINES:
    11	            out[name] = (lambda cls=BASELINES[name]: cls(cfg))
    12	        elif name in LEARNED:
    13	            if not params or name not in params:
    14	                raise KeyError(f'{name} needs tuned parameters')
    15	            out[name] = (lambda cls=LEARNED[name], p=params[name]: cls(cfg, p))
    16	        else:
    17	            raise KeyError(f'unknown model {name}')
    18	    return out
    19	"""Baselines of PLAN stage 4 (D18). Same interface as the models: fit(X, y) / predict_proba(X).
    20	
    21	X is the backtest frame: grid columns (unit_id, t, oblast, ...) plus features. Every rate is
    22	shrunk towards its parent rate with additive smoothing of a fixed strength (config
    23	baselines.prior_strength), so that cells with few rows do not produce 0 or 1.
    24	"""
    25	import numpy as np
    26	import pandas as pd
    27	
    28	
    29	def _smoothed(pos: pd.Series, n: pd.Series, parent, prior: float) -> pd.Series:
    30	    return (pos + prior * parent) / (n + prior)
    31	
    32	
    33	class GlobalRate:
    34	    """B0: overall frequency of the target over the training rows."""
    35	    name = 'B0'
    36	
    37	    def __init__(self, cfg: dict):
    38	        pass
    39	
    40	    def fit(self, X: pd.DataFrame, y: np.ndarray):
    41	        self.p_ = float(np.mean(y))
    42	        return self
    43	
    44	    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
    45	        return np.full(len(X), self.p_)
    46	
    47	
    48	class UnitHourRate:
    49	    """B1: frequency for unit x hour of day (Kyiv) over the last window_days of training rows.
    50	
    51	    The window ends at the last training moment, which the backtest sets to (forecast day - h):
    52	    the most recent rows whose labels are fully known.
    53	    """
    54	    name = 'B1'
    55	
    56	    def __init__(self, cfg: dict):
    57	        self.window = pd.Timedelta(days=cfg['baselines']['b1_window_days'])
    58	        self.prior = cfg['baselines']['prior_strength']
    59	
    60	    def fit(self, X: pd.DataFrame, y: np.ndarray):
    61	        recent = (X['t'] > X['t'].max() - self.window).to_numpy()
    62	        d = pd.DataFrame({'unit_id': X['unit_id'].to_numpy()[recent],
    63	                          'hour': X['hour_kyiv'].to_numpy().astype(int)[recent], 'y': y[recent]})
    64	        self.global_ = float(d['y'].mean())
    65	        unit = d.groupby('unit_id')['y
… [обрезано: показано 3000 из 14482 символов]
```

</details>

<details><summary>🔧 Bash: Read store, config, timeutil, spans modules · 20:25</summary>

**Аргументы**

```bash
cat -n src/alerts/store.py src/alerts/config.py src/alerts/timeutil.py src/alerts/spans.py | head -200; head -5 data/alerts_in_ua_locations.csv; wc -l data/alerts_in_ua_locations.csv
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
    50	"""Loading config.yaml. Every threshold and date lives there, none in the code (PLAN 1б.6)."""
    51	from pathlib import Path
    52	
    53	import pandas as pd
    54	import yaml
    55	
    56	ROOT = Path(__file__).resolve().parents[2]
    57	
    58	_REQUIRED = {
    59	    'dataset': ['repo_url', 'commit', 'repo_dir', 'path', 'sha256', 'path_uk', 'sha256_uk'],
    60	    'volunteer': ['commit', 'path', 'sha256'],
    61	    'periods': ['work_start', 'warmup_end', 'train_end', 'val_end'],
    62	    'scope': ['excluded_oblasts', 'input_only_oblasts', 'oblast_level_units'],
    63	    'thresholds': ['pause_merge_min', 'long_alert_hours', 'clone_jaccard',
    64	                   'similar_pairs_report', 'outage_gap_hours'],
    65	    'processor': ['enabled', 'fake_end_duration_s', 'fake_end_next_start_h'],
    66	    'history': ['max_open_hours'],
    67	    'geo': ['path', 'sha256', 'vertex_decimals', 'min_shared_vertices', 'renames'],
    68	    'backtest': ['
… [обрезано: показано 3000 из 10026 символов]
```

</details>

<details><summary>🔧 Write: reviews/scratch/stage8/common.py · 20:25</summary>

**Аргументы**

```
# file: reviews/scratch/stage8/common.py
"""Shared helpers for the stage 8 review scripts. Nothing is written to disk."""
import logging
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from alerts import api_check as ac  # noqa: E402
from alerts import store  # noqa: E402
from alerts.config import ROOT, load_config, path  # noqa: E402
from alerts.ingest.alerts_in_ua import build_locations, load_alerts_in_ua, read_raw  # noqa: E402
from alerts.pipeline import build_tables  # noqa: E402

logging.basicConfig(level=logging.WARNING)


def api_inputs():
    cfg = load_config()
    raw = read_raw(ROOT / cfg['api']['raw_dir'])
    units = store.load_units(cfg)
    neighbors = pd.read_csv(path(cfg, 'neighbors'))
    locations = build_locations(units, cfg)
    recs, st = load_alerts_in_ua(raw, locations)
    level = raw.set_index('id')['alert_level']
    recs['alert_level'] = recs['api_id'].map(level)
    cfg_a = ac.api_config(cfg, raw)
    return cfg, cfg_a, raw, units, neighbors, locations, recs, st


def api_art(recs, cfg_a, units, neighbors):
    return build_tables(recs.drop(columns=['alert_level', 'api_id'], errors='ignore'), cfg_a,
                        units=units, neighbors=neighbors)

```

**Результат**

```
File created successfully at: d:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage8\common.py (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Write: reviews/scratch/stage8/a04_triang.py · 20:26</summary>

**Аргументы**

```
# file: reviews/scratch/stage8/a04_triang.py
"""Stage 8 review: reproduce the x1.27 triangulation and test its robustness.

Variants: API red-only / yellow-only, leave-one-oblast-out, per-oblast ratios, volunteer naive ends,
matching tolerance, and the matched share by alert level.
"""
import numpy as np
import pandas as pd

from common import api_art, api_inputs
from alerts import api_check as ac
from alerts.config import ts
from alerts.pipeline import build_all
from alerts.spans import union
from alerts.timeutil import to_sec

pd.set_option('display.width', 250)
pd.set_option('display.max_rows', 100)

cfg, cfg_a, raw, units, neighbors, locations, recs, st = api_inputs()
print('stats:', {k: st[k] for k in ['downloaded', 'open_at_download', 'dropped_city_hromada', 'records', 'oblast_records_expanded']})
print('air_raid city+hromada records (all):', int(raw[(raw['alert_type'] == 'air_raid') & raw['location_type'].isin(['city', 'hromada'])].shape[0]))
art_a = api_art(recs, cfg_a, units, neighbors)
art_v = build_all(cfg)
vol = ac.volunteer(cfg)
print('volunteer columns', list(vol.columns), len(vol))
print('volunteer naive share:', vol['naive'].mean() if 'naive' in vol else None)

hi_v = art_v.outages['start'].min().floor('D')
lo_v = hi_v - pd.Timedelta(days=28)
lo_a, hi_a = ts(cfg_a['periods']['work_start']), ts(cfg_a['data_end'])
print('windows', lo_v, hi_v, lo_a, hi_a)

ob_v = ac.oblast_intervals(art_v)
ob_a = ac.oblast_intervals(art_a)
obl = sorted(set(ob_v['oblast']) & set(vol['oblast']))
vi = ac.volunteer_intervals(vol)
print('oblasts', len(obl))


def ratios(ob_a_, vi_aug, vi_sep, oblasts):
    a = {('V', 'Aug'): ac.activity(ob_v, lo_v, hi_v, oblasts)['starts_per_oblast_day'],
         ('vol', 'Aug'): ac.activity(vi_aug, lo_v, hi_v, oblasts)['starts_per_oblast_day'],
         ('A', 'Sep'): ac.activity(ob_a_, lo_a, hi_a, oblasts)['starts_per_oblast_day'],
         ('vol', 'Sep'): ac.activity(vi_sep, lo_a, hi_a, oblasts)['starts_per_oblast_day']}
    src = a[('A', 
… [обрезано: показано 2000 из 6741 символов]
```

**Результат**

```
File created successfully at: d:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage8\a04_triang.py (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Bash: Run triangulation robustness script · 20:26</summary>

**Аргументы**

```bash
time PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage8/a04_triang.py 2>&1 | grep -v Warning | head -150
```

**Результат**

```
WARNING:alerts.pipeline:Channel outage (D15): 2026-08-29 05:55:28+00:00 -> 2026-09-02 13:48:04+00:00 (4 days 07:52:36)
stats: {'downloaded': 16532, 'open_at_download': 60, 'dropped_city_hromada': 1644, 'records': 14389, 'oblast_records_expanded': 1}
air_raid city+hromada records (all): 1861
volunteer columns ['oblast', 'started_at', 'finished_at', 'naive'] 115989
volunteer naive share: 0.05010819991550923
windows 2026-08-01 00:00:00+00:00 2026-08-29 00:00:00+00:00 2026-09-12 00:00:00+00:00 2026-10-11 08:00:00+00:00
oblasts 24

reproduction: sources x1.594, volunteers x1.255, factor x1.271; levels {('V', 'Aug'): 3.4017857142857144, ('vol', 'Aug'): 5.066964285714286, ('A', 'Sep'): 5.423295454545454, ('vol', 'Sep'): 6.357954545454546}
API red only: starts/oblast/day 1.24; sources x0.365, factor x0.291
   triangulate red: source matched 0.267, vol matched 0.055, median lag -29
API yellow only: starts/oblast/day 5.05; sources x1.485, factor x1.184
   triangulate yellow: source matched 0.335, vol matched 0.269, median lag -18
tol  2 min: Vadimkin matched 0.325 / vol 0.219; API matched 0.202 / vol 0.172
tol  5 min: Vadimkin matched 0.371 / vol 0.250; API matched 0.238 / vol 0.203
tol 10 min: Vadimkin matched 0.434 / vol 0.293; API matched 0.311 / vol 0.266
tol 20 min: Vadimkin matched 0.532 / vol 0.371; API matched 0.438 / vol 0.382
tol 30 min: Vadimkin matched 0.623 / vol 0.435; API matched 0.541 / vol 0.468
Traceback (most recent call last):
  File "d:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage8\a04_triang.py", line 73, in <module>
    s_, r_, f_, a_ = ratios(ob_a, vi, vi, [o])
                     ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "d:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage8\a04_triang.py", line 46, in ratios
    real = a[('vol', 'Sep')] / a[('vol', 'Aug')]
           ~~~~~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~
ZeroDivisionError: float division by zero

real	0m52.686s
user	0m0.092s
sys	0m0.311s
```

</details>

<details><summary>🔧 Write: reviews/scratch/stage8/a05_level_time.py · 20:27</summary>

**Аргументы**

```
# file: reviews/scratch/stage8/a05_level_time.py
"""Stage 8 review: alert_level over time and by oblast; volunteer start rate over time."""
import numpy as np
import pandas as pd

from alerts import api_check as ac
from alerts.config import ROOT, load_config
from alerts.ingest.alerts_in_ua import read_raw

pd.set_option('display.width', 250)
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 40)

cfg = load_config()
raw = read_raw(ROOT / cfg['api']['raw_dir'])
ar = raw[(raw['alert_type'] == 'air_raid') & (raw['location_type'].isin(['raion']) | (raw['location_title'] == 'м. Київ'))]
ar = ar[ar['started_at'] >= '2026-09-11']
ar = ar.assign(day=ar['started_at'].dt.floor('D'), red=(ar['alert_level'] == 'red'))
# days: share red and counts
d = ar.groupby('day').agg(n=('red', 'size'), red=('red', 'mean'))
print(d.round(2).T.to_string())
# by oblast x 5-day block
ar = ar.assign(block=((ar['day'] - pd.Timestamp('2026-09-11', tz='UTC')).dt.days // 5))
t = ar.pivot_table(index='location_oblast', columns='block', values='red', aggfunc='mean').round(2)
print('\nshare red by oblast and 5-day block (block 0 = Sep 11-15):')
print(t.to_string())
# old records
old = raw[raw['started_at'] < '2026-09-01']
print('\nlevels of records started before Sep 2026:')
print(old[['location_type', 'location_title', 'started_at', 'alert_type', 'alert_level']].to_string())

# first appearance of yellow by oblast
fy = ar[~ar['red']].groupby('location_oblast')['started_at'].min()
fr = ar[ar['red']].groupby('location_oblast')['started_at'].min()
print('\nfirst yellow / first red by oblast:')
print(pd.DataFrame({'first_yellow': fy, 'first_red': fr}).sort_values('first_yellow').to_string())

# volunteer starts per oblast-day by week, July-October
vol = ac.volunteer(cfg)
vol = vol[(vol['started_at'] >= '2026-06-01')]
w = vol.assign(week=vol['started_at'].dt.floor('D') - pd.to_timedelta(vol['started_at'].dt.dayofweek, unit='D'))
print('\nvolunteer records per week (all oblasts) an
… [обрезано: показано 2000 из 2116 символов]
```

**Результат**

```
File created successfully at: d:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage8\a05_level_time.py (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Bash: Run alert level over time analysis · 20:27</summary>

**Аргументы**

```bash
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage8/a05_level_time.py 2>&1 | grep -v Warning | head -150
```

**Результат**

```
day  2026-09-11 00:00:00+00:00  2026-09-12 00:00:00+00:00  2026-09-13 00:00:00+00:00  2026-09-14 00:00:00+00:00  2026-09-15 00:00:00+00:00  2026-09-16 00:00:00+00:00  2026-09-17 00:00:00+00:00  2026-09-18 00:00:00+00:00  2026-09-19 00:00:00+00:00  2026-09-20 00:00:00+00:00  2026-09-21 00:00:00+00:00  2026-09-22 00:00:00+00:00  2026-09-23 00:00:00+00:00  2026-09-24 00:00:00+00:00  2026-09-25 00:00:00+00:00  2026-09-26 00:00:00+00:00  2026-09-27 00:00:00+00:00  2026-09-28 00:00:00+00:00  2026-09-29 00:00:00+00:00  2026-09-30 00:00:00+00:00  2026-10-01 00:00:00+00:00  2026-10-02 00:00:00+00:00  2026-10-03 00:00:00+00:00  2026-10-04 00:00:00+00:00  2026-10-05 00:00:00+00:00  2026-10-06 00:00:00+00:00  2026-10-07 00:00:00+00:00  2026-10-08 00:00:00+00:00  2026-10-09 00:00:00+00:00  2026-10-10 00:00:00+00:00  2026-10-11 00:00:00+00:00
n                       289.00                     482.00                     301.00                     322.00                     523.00                     490.00                     500.00                     466.00                     493.00                     507.00                     496.00                     508.00                     617.00                     454.00                     560.00                     433.00                     397.00                     513.00                     505.00                     460.00                     428.00                     389.00                     424.00                     414.00                     452.00                      412.0                     493.00                     512.00                     608.00                     721.00                     216.00
red                       0.44                       0.57                       0.32                       0.41                       0.55                       0.44                       0.49                       0.39                       0.38                       0.33                       0.35                       0.31                       0.36                       0.26                       0.35                       0.23                       0.28                       0.34                       0.36                       0.28                       0.32                       0.23                       0.29                       0.36                       0.34                        0.2                       0.33                       0.22                       0.25                       0.31                       0.21

share red by oblast and 5-day block (block 0 = Sep 11-15):
block                         0     1     2     3     4     5     6
location_oblast                                                    
Івано-Франківська область  0.60  1.00  0.00  0.00   NaN  0.13   NaN
Волинська область          0.16  0.44  0.00  0.00  0.00  0.00   NaN
Вінницька область          0.19  0.42  0.20  0.20  0.21  0.12  0.00
Дніпропетровська область   0.98  1.00  0.76  0.68  0.79  0.84  0.96
Донецька 
… [обрезано: показано 3000 из 8831 символов]
```

</details>

<details><summary>🔧 Bash: Fix zero division and rerun triangulation · 20:27</summary>

**Аргументы**

```bash
python - <<'EOF'
p='reviews/scratch/stage8/a04_triang.py'
s=open(p,encoding='utf-8').read()
s=s.replace("""    src = a[('A', 'Sep')] / a[('V', 'Aug')]
    real = a[('vol', 'Sep')] / a[('vol', 'Aug')]
    return src, real, src / real, a""","""    src = a[('A', 'Sep')] / a[('V', 'Aug')] if a[('V', 'Aug')] else np.nan
    real = a[('vol', 'Sep')] / a[('vol', 'Aug')] if a[('vol', 'Aug')] else np.nan
    return src, real, src / real if real else np.nan, a""")
# skip the expensive level and tolerance parts on rerun
s=s.replace("for lvl in ['red', 'yellow']:","for lvl in []:")
s=s.replace("for tol in [2, 5, 10, 20, 30]:","for tol in []:")
open(p,'w',encoding='utf-8').write(s)
EOF
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage8/a04_triang.py 2>&1 | grep -v Warning | head -150
```

**Результат**

```
WARNING:alerts.pipeline:Channel outage (D15): 2026-08-29 05:55:28+00:00 -> 2026-09-02 13:48:04+00:00 (4 days 07:52:36)
stats: {'downloaded': 16532, 'open_at_download': 60, 'dropped_city_hromada': 1644, 'records': 14389, 'oblast_records_expanded': 1}
air_raid city+hromada records (all): 1861
volunteer columns ['oblast', 'started_at', 'finished_at', 'naive'] 115989
volunteer naive share: 0.05010819991550923
windows 2026-08-01 00:00:00+00:00 2026-08-29 00:00:00+00:00 2026-09-12 00:00:00+00:00 2026-10-11 08:00:00+00:00
oblasts 24

reproduction: sources x1.594, volunteers x1.255, factor x1.271; levels {('V', 'Aug'): 3.4017857142857144, ('vol', 'Aug'): 5.066964285714286, ('A', 'Sep'): 5.423295454545454, ('vol', 'Sep'): 6.357954545454546}

per oblast:
                          V_aug   A_sep  vol_aug  vol_sep     src   real  factor  api_red_share
oblast                                                                                         
Ivano-Frankivska oblast   0.107   0.477    0.036    0.273   4.455  7.636   0.583          0.476
Vinnytska oblast          1.536   4.739    0.964    4.602   3.086  4.773   0.647          0.192
Chernivetska oblast       0.143   1.091    0.107    1.057   7.636  9.864   0.774          0.260
Dnipropetrovska oblast    3.000   2.420   19.500   20.284   0.807  1.040   0.776          0.839
Kyivska oblast            4.250   7.909    5.929   13.295   1.861  2.243   0.830          0.086
Zhytomyrska oblast        2.036   7.466    1.393    5.693   3.667  4.087   0.897          0.115
Cherkaska oblast          3.679   7.466    2.250    5.011   2.030  2.227   0.911          0.184
Mykolaivska oblast       10.321  12.648   10.929   14.352   1.225  1.313   0.933          0.104
Kirovohradska oblast      5.107   8.420    4.286    7.159   1.649  1.670   0.987          0.161
Rivnenska oblast          0.536   4.125    0.429    3.170   7.700  7.398   1.041          0.051
Poltavska oblast          7.000   8.114    6.357    7.057   1.159  1.110   1.044          0.150
Ternopilska oblast        0.250   1.432    0.143    0.750   5.727  5.250   1.091          0.071
Zaporizka oblast          3.964   5.693    5.214    6.545   1.436  1.255   1.144          0.584
Khmelnytska oblast        0.571   3.409    0.429    2.114   5.966  4.932   1.210          0.071
Kharkivska oblast         4.929   7.534   16.107   19.159   1.529  1.189   1.285          0.542
Donetska oblast           2.214   2.318    4.321    3.477   1.047  0.805   1.301          0.723
Kyiv City                 3.143   7.261    2.750    4.602   2.310  1.674   1.381          0.074
Odeska oblast             9.964  11.455   10.357    8.489   1.150  0.820   1.403          0.149
Chernihivska oblast       6.321   6.136    8.214    5.182   0.971  0.631   1.539          0.101
Sumska oblast             4.929   8.727    7.929    8.489   1.771  1.071   1.654          0.554
Khersonska oblast         7.321   8.557    6.536    3.716   1.169  0.569   2.056          0.283
Lvivska oblast            0.071   0.5
… [обрезано: показано 3000 из 3971 символов]
```

</details>

<details><summary>🔧 Bash: Add ruler-consistent oblast subset analysis · 20:29</summary>

**Аргументы**

```bash
cat >> reviews/scratch/stage8/a04_triang.py <<'EOF'

# oblasts where the volunteer ruler agrees with Vadimkin on the August level within x2
po['ruler_aug'] = po['vol_aug'] / po['V_aug']
ok = po[(po['ruler_aug'] >= 0.5) & (po['ruler_aug'] <= 2)].index.tolist()
print('\nruler vol/Vadimkin in August within [0.5, 2]:', len(ok), 'oblasts; outside:',
      po.loc[~po.index.isin(ok), 'ruler_aug'].round(2).to_dict())
print('factor on these oblasts:', round(ratios(ob_a, vi, vi, ok)[2], 3), ' sources', round(ratios(ob_a, vi, vi, ok)[0], 3),
      ' volunteers', round(ratios(ob_a, vi, vi, ok)[1], 3))
w = po[['V_aug', 'A_sep', 'vol_aug', 'vol_sep']]
print('share of volunteer starts from Dnipropetrovska + Kharkivska: Aug',
      round(w.loc[['Dnipropetrovska oblast', 'Kharkivska oblast'], 'vol_aug'].sum() / w['vol_aug'].sum(), 3),
      'Sep-Oct', round(w.loc[['Dnipropetrovska oblast', 'Kharkivska oblast'], 'vol_sep'].sum() / w['vol_sep'].sum(), 3))
lf = np.log(po['factor'].dropna())
print('geometric mean of per-oblast factors', round(float(np.exp(lf.mean())), 3), ' on ruler-consistent oblasts',
      round(float(np.exp(np.log(po.loc[ok, 'factor']).mean())), 3))
EOF
sed -i "s/^for lvl in \[\]:/for lvl in []:/" reviews/scratch/stage8/a04_triang.py
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage8/a04_triang.py 2>&1 | grep -v Warning | tail -8
```

**Результат**

```
volunteer records Sep-Oct: 4476, naive share 0.076

hour-profile corr oblast level: Vadimkin Aug vs API Sep-Oct 0.632 ; volunteers Aug vs Sep-Oct 0.689

ruler vol/Vadimkin in August within [0.5, 2]: 18 oblasts; outside: {'Dnipropetrovska oblast': 6.5, 'Ivano-Frankivska oblast': 0.33, 'Kharkivska oblast': 3.27, 'Lvivska oblast': 61.0, 'Volynska oblast': 17.2, 'Zakarpatska oblast': 0.0}
factor on these oblasts: 1.196  sources 1.596  volunteers 1.334
share of volunteer starts from Dnipropetrovska + Kharkivska: Aug 0.293 Sep-Oct 0.258
geometric mean of per-oblast factors 1.282  on ruler-consistent oblasts 1.112
```

</details>

<details><summary>🔧 Bash: Inspect tuning json and predictions parquet · 20:30</summary>

**Аргументы**

```bash
cat reports/tuning_h3.json | head -50; ls reports reports/figures; python -c "
import pandas as pd
p=pd.read_parquet('data/predictions_h3.parquet'); print(p.shape, p.columns.tolist()); print(p.groupby('part').size())"
```

**Результат**

```
{
 "LR": {
  "C": 0.1,
  "half_life_days": null
 },
 "LGBM": {
  "num_leaves": 63,
  "min_child_samples": 200,
  "half_life_days": 28,
  "n_estimators": 84
 }
}reports:
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

reports/figures:
alerts_per_unit.png
api_vs_vadimkin.png
calibration_h1.png
calibration_h3.png
calibration_h6.png
durations.png
forecast_vs_fact.png
jaccard.png
level_transition.png
outage.png
(104135, 11) ['day', 'p_B0', 'p_B1', 'p_B2', 'p_LR', 'p_LGBM', 'part', 'y', 't', 'unit_id', 'oblast']
part
test    46270
val     57865
dtype: int64
```

</details>

<details><summary>🔧 Bash: Show tuning params for h=1,6 and leakage json · 20:30</summary>

**Аргументы**

```bash
cat reports/tuning_h1.json reports/tuning_h6.json | tr -d '\n '; echo; nproc 2>/dev/null; cat reports/leakage_check.json | head -30
```

**Результат**

```
{"LR":{"C":1.0,"half_life_days":28},"LGBM":{"num_leaves":15,"min_child_samples":200,"half_life_days":28,"n_estimators":108}}{"LR":{"C":0.01,"half_life_days":null},"LGBM":{"num_leaves":15,"min_child_samples":200,"half_life_days":28,"n_estimators":104}}
12
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
```

</details>

<details><summary>🔧 Write: reviews/scratch/stage8/b01_frozen.py · 20:31</summary>

**Аргументы**

```
# file: reviews/scratch/stage8/b01_frozen.py
"""Stage 8 review: reproduce the frozen-model predictions and B1_live (in memory), save them to scratch.

Writes only reviews/scratch/stage8/out/*.parquet. LightGBM with 2 threads (other agents share the CPU).
"""
import copy
import json
import time
from pathlib import Path

import pandas as pd

from common import api_art, api_inputs
from alerts import api_check as ac
from alerts.backtest import walk_forward
from alerts.config import path, ts
from alerts.metrics import bootstrap
from alerts.models import registry
from alerts.models.baselines import UnitHourRate
from alerts.pipeline import build_all, model_data

OUT = Path(__file__).resolve().parent / 'out'
OUT.mkdir(exist_ok=True)
t0 = time.time()
cfg, cfg_a, raw, units, neighbors, locations, recs, st = api_inputs()
cfg2 = copy.deepcopy(cfg)
cfg2['models']['threads'] = 2
art_a = api_art(recs, cfg_a, units, neighbors)
art_v = build_all(cfg)
data_v, data_a = model_data(art_v, cfg), model_data(art_a, cfg_a)
print(f'data built in {time.time() - t0:.0f} s: Vadimkin {len(data_v):,} rows, API {len(data_a):,} rows')
data_a.to_parquet(OUT / 'data_a.parquet')
data_v[data_v['part'] == 'test'].to_parquet(OUT / 'data_v_test.parquet')

names = cfg['backtest']['baselines'] + cfg['backtest']['models']
for h in cfg['backtest']['horizons']:
    tuned = json.loads((path(cfg, 'reports') / f'tuning_h{h}.json').read_text(encoding='utf-8'))
    t1 = time.time()
    preds = ac.frozen_predictions(data_v, ts(cfg['data_end']), data_a, h, registry(cfg2, names, tuned))
    tab = ac.frozen_tables(preds, names, cfg)
    r = tab.set_index(['model', 'metric'])
    print(f"h={h}: {tab.attrs['n_rows']:,} rows, {tab.attrs['n_days']} days, fit {time.time() - t1:.0f} s; "
          f"PR-AUC LGBM {r.at[('LGBM', 'pr_auc'), 'value']:.3f}, LGBM-B1 {r.at[('LGBM', 'pr_auc'), 'diff']:+.3f} "
          f"[{r.at[('LGBM', 'pr_auc'), 'diff_lo']:+.3f}, {r.at[('LGBM', 'pr_auc'), 'diff_hi']:+.3f}]")
    start = ts(cfg_a['p
… [обрезано: показано 2000 из 2830 символов]
```

**Результат**

```
File created successfully at: d:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage8\b01_frozen.py (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Bash: Reproduce frozen predictions and B1_live · 20:31</summary>

**Аргументы**

```bash
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage8/b01_frozen.py > reviews/scratch/stage8/out_b01.txt 2>&1; tail -20 reviews/scratch/stage8/out_b01.txt
```

**Результат**

```
Command running in background with ID: bapm8xkfg. Output is being written to: C:\Users\chyck\AppData\Local\Temp\claude\d--Flash-golova-KSE-AI-AAFS\57049ae5-374c-471e-8191-1ff2343b8a66\tasks\bapm8xkfg.output. You will be notified when it completes. To check interim output, use Read on that file path.
```

</details>

<details><summary>🔧 Write: reviews/scratch/stage8/a06_semantics.py · 20:32</summary>

**Аргументы**

```
# file: reviews/scratch/stage8/a06_semantics.py
"""Stage 8 review: source semantics - oblast-wide records, Kyiv, event gaps, mass closures, late updates."""
import numpy as np
import pandas as pd

from common import api_art, api_inputs
from alerts.config import ts
from alerts.timeutil import to_sec

pd.set_option('display.width', 250)
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 30)

cfg, cfg_a, raw, units, neighbors, locations, recs, st = api_inputs()
ar = raw[raw['alert_type'] == 'air_raid']

# 1. oblast-wide records and raion records of the same oblast at the same time
ob = ar[(ar['location_type'] == 'oblast') & (ar['location_title'] != 'м. Київ')]
print(ob[['location_title', 'started_at', 'finished_at', 'alert_level']].to_string())
myk = ob[ob['location_oblast'].str.startswith('Миколаїв')]
for _, r in myk.iterrows():
    fin = r['finished_at']
    same = ar[(ar['location_oblast'] == r['location_oblast']) & (ar['location_type'] == 'raion')
              & (ar['started_at'] < fin + pd.Timedelta(hours=1)) & (ar['finished_at'].fillna(ar['requested_utc']) > r['started_at'] - pd.Timedelta(hours=1))]
    print('Mykolaiv raion records within +-1 h of the oblast-wide record:')
    print(same[['location_title', 'started_at', 'finished_at', 'alert_level']].to_string())

# 2. Kyiv: types of records titled "м. Київ" and records with location_oblast "м. Київ"
print('\nKyiv title by type:', ar[ar['location_title'] == 'м. Київ']['location_type'].value_counts().to_dict())
print('records with location_oblast м. Київ by type:', raw[raw['location_oblast'] == 'м. Київ'].groupby(['alert_type', 'location_type']).size().to_dict())

# 3. records in schema: earliest start, events and the longest gap in [work_start, data_end)
lo, hi = ts(cfg_a['periods']['work_start']), ts(cfg_a['data_end'])
print('\nrecs: earliest start', recs['started_at'].min(), 'latest end', recs['finished_at'].max())
ev = np.sort(np.unique(np.concatenate([to_sec(recs['started_at']), to_
… [обрезано: показано 2000 из 5024 символов]
```

**Результат**

```
File created successfully at: d:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage8\a06_semantics.py (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Bash: Run source semantics checks · 20:32</summary>

**Аргументы**

```bash
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage8/a06_semantics.py 2>&1 | grep -v Warning | head -120
```

**Результат**

```
location_title                started_at               finished_at alert_level
0              Луганська область 2022-04-04 16:45:39+00:00                       NaT         red
1      Автономна Республіка Крим 2022-12-10 22:22:00+00:00                       NaT         red
11261       Миколаївська область 2026-10-02 02:51:23+00:00 2026-10-02 02:56:04+00:00      yellow
Mykolaiv raion records within +-1 h of the oblast-wide record:
            location_title                started_at               finished_at alert_level
11239  Миколаївський район 2026-10-02 01:44:06+00:00 2026-10-02 02:09:49+00:00      yellow
11248  Вознесенський район 2026-10-02 01:58:18+00:00 2026-10-02 02:09:49+00:00      yellow
11262    Баштанський район 2026-10-02 02:51:24+00:00 2026-10-02 02:56:04+00:00      yellow
11263  Первомайський район 2026-10-02 02:51:25+00:00 2026-10-02 02:56:04+00:00      yellow
11264  Миколаївський район 2026-10-02 02:51:24+00:00 2026-10-02 02:56:04+00:00      yellow
11265  Вознесенський район 2026-10-02 02:51:25+00:00 2026-10-02 02:56:04+00:00      yellow
11267  Миколаївський район 2026-10-02 02:56:53+00:00 2026-10-02 03:20:04+00:00      yellow
11273  Вознесенський район 2026-10-02 03:08:14+00:00 2026-10-02 03:18:54+00:00      yellow

Kyiv title by type: {'oblast': 217}
records with location_oblast м. Київ by type: {('air_raid', 'oblast'): 217}

recs: earliest start 2026-09-11 00:57:48+00:00 latest end 2026-10-11 08:59:35+00:00
longest gaps between events (h): [('2026-10-07 00:13:29+00:00', np.float64(3.74)), ('2026-09-13 22:15:07+00:00', np.float64(1.04)), ('2026-09-14 12:18:32+00:00', np.float64(0.96)), ('2026-10-04 23:58:15+00:00', np.float64(0.73)), ('2026-10-04 03:11:13+00:00', np.float64(0.67))]

ends shared by records of >= 3 oblasts in the same second: 388 ; records involved 3090 of 13838
                            n  oblasts
finished_at                           
2026-09-15 17:09:13+00:00  45       19
2026-09-15 17:09:02+00:00  37       18
2026-09-17 10:42:04+00:00  32       13
2026-09-17 10:41:54+00:00  33       12
2026-09-15 19:28:40+00:00  39        9
2026-09-16 23:53:44+00:00  32        7
2026-09-20 02:05:54+00:00  30        7
2026-09-18 17:00:22+00:00  24        7
2026-10-10 11:35:55+00:00  29        7
2026-09-22 01:42:09+00:00  24        7
starts shared by >= 3 oblasts in the same second: 177

raion records duration: < 60 s 15  < 300 s 220  exactly 3600 s 0  exactly 1800 s 1  > 24 h 101  of 13838
most frequent durations (rounded to 10 s): {1220.0: 70, 1180.0: 66, 1480.0: 62, 900.0: 61, 1160.0: 60}

late-updated records in schema: 57
h=3 test rows of the same unit with t in (finished_at, next start): 62 of 42004 (0.1476%); moments 35
hours between end and next start of the unit (late records): {'count': 57.0, 'mean': 1.45, 'std': 1.71, 'min': 0.02, '25%': 0.33, '50%': 0.77, '75%': 2.08, 'max': 7.83}
```

</details>

<details><summary>🔧 Bash: Check progress of frozen model reproduction · 20:33</summary>

**Аргументы**

```bash
cat tasks 2>/dev/null; cat "C:\Users\chyck\AppData\Local\Temp\claude\d--Flash-golova-KSE-AI-AAFS\57049ae5-374c-471e-8191-1ff2343b8a66\tasks\bapm8xkfg.output" 2>/dev/null | tail -5; cat reviews/scratch/stage8/out_b01.txt | grep -v Warning | tail
```

**Результат**

```
WARNING:alerts.pipeline:Channel outage (D15): 2026-08-29 05:55:28+00:00 -> 2026-09-02 13:48:04+00:00 (4 days 07:52:36)
```

</details>

<details><summary>🔧 Write: reviews/scratch/stage8/a07_long.py · 20:33</summary>

**Аргументы**

```
# file: reviews/scratch/stage8/a07_long.py
"""Stage 8 review: long alerts in the API, grid statuses, masked share, since_end NaN."""
import numpy as np
import pandas as pd

from common import api_art, api_inputs
from alerts.config import ts
from alerts.spans import clipped_seconds, union

pd.set_option('display.width', 250)
pd.set_option('display.max_rows', 120)
pd.set_option('display.max_columns', 30)

cfg, cfg_a, raw, units, neighbors, locations, recs, st = api_inputs()
d = (recs['finished_at'] - recs['started_at']).dt.total_seconds() / 3600
lo, hi = ts(cfg_a['periods']['work_start']), ts(cfg_a['data_end'])
long = recs[(d > 24) & (recs['finished_at'] > lo)].assign(hours=d)
print('records > 24 h overlapping the period:', len(long))
print(long.groupby('oblast').agg(n=('hours', 'size'), max_h=('hours', 'max'), median_h=('hours', 'median')).round(1).to_string())
print('distinct end seconds among them:', long['finished_at'].nunique(), '; distinct start seconds:', long['started_at'].nunique())
print(long.sort_values('started_at')[['oblast', 'raion', 'started_at', 'finished_at', 'hours', 'alert_level']].head(40).to_string())

art = api_art(recs, cfg_a, units, neighbors)
print('\nmask stats:', {k: v for k, v in art.mask_stats.items() if k != 'outages'})
gs = art.grid_stats['status']
print('grid statuses in the API test part (unit-hours):', {s: v['test'] for s, v in gs.items()})
tot = sum(v['test'] for v in gs.values())
print('share:', {s: round(v['test'] / tot, 4) for s, v in gs.items()})

# masked share by oblast (target units, test part)
tgt = units[units['role'] == 'target'].drop_duplicates('unit_id')
m = art.masks[art.masks['unit_id'].isin(tgt['unit_id']) & (art.masks['reason'] == 'long_24h')]
warm = ts(cfg_a['periods']['warmup_end'])
u = union(m, 'unit_id')
u['sec'] = [clipped_seconds(pd.Series([a]), pd.Series([b]), warm, hi) for a, b in zip(u['start'], u['end'])]
u = u.merge(tgt[['unit_id', 'oblast', 'unit_name']], on='unit_id')
print('\nmask (a) unit-hours in the t
… [обрезано: показано 2000 из 2264 символов]
```

**Результат**

```
File created successfully at: d:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage8\a07_long.py (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Bash: Analyze long alerts and masked share in API · 20:33</summary>

**Аргументы**

```bash
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage8/a07_long.py 2>&1 | grep -v Warning | head -120
```

**Результат**

```
records > 24 h overlapping the period: 101
                         n  max_h  median_h
oblast                                     
Chernihivska oblast      8   40.9      30.2
Dnipropetrovska oblast   4   30.0      28.2
Donetska oblast         80   42.9      35.2
Kyivska oblast           3   27.5      27.3
Sumska oblast            5   35.9      31.5
Zhytomyrska oblast       1   24.6      24.6
distinct end seconds among them: 24 ; distinct start seconds: 46
                      oblast                     raion                started_at               finished_at      hours alert_level
365      Chernihivska oblast       Chernihivskyi raion 2026-09-12 01:21:13+00:00 2026-09-13 07:34:47+00:00  30.226111         red
366      Chernihivska oblast        Koriukivskyi raion 2026-09-12 01:21:14+00:00 2026-09-13 07:34:47+00:00  30.225833         red
367            Sumska oblast         Konotopskyi raion 2026-09-12 01:35:51+00:00 2026-09-13 09:20:52+00:00  31.750278         red
368            Sumska oblast             Sumskyi raion 2026-09-12 01:35:51+00:00 2026-09-13 13:28:58+00:00  35.885278         red
370            Sumska oblast        Shostkynskyi raion 2026-09-12 01:51:21+00:00 2026-09-13 09:20:52+00:00  31.491944         red
371            Sumska oblast           Romenskyi raion 2026-09-12 01:51:21+00:00 2026-09-13 09:20:52+00:00  31.491944         red
381      Chernihivska oblast          Prylutskyi raion 2026-09-12 02:13:56+00:00 2026-09-13 07:34:47+00:00  29.347500         red
396            Sumska oblast          Okhtyrskyi raion 2026-09-12 02:15:53+00:00 2026-09-13 09:20:52+00:00  31.083056         red
411      Chernihivska oblast          Nizhynskyi raion 2026-09-12 02:20:09+00:00 2026-09-13 07:34:47+00:00  29.243889         red
443           Kyivska oblast       Vyshhorodskyi raion 2026-09-12 03:53:49+00:00 2026-09-13 07:23:51+00:00  27.500556         red
445      Chernihivska oblast  Novhorod-Siverskyi raion 2026-09-12 04:15:39+00:00 2026-09-13 07:34:47+00:00  27.318889         red
453           Kyivska oblast          Brovarskyi raion 2026-09-12 04:45:21+00:00 2026-09-13 08:01:42+00:00  27.272500         red
469       Zhytomyrska oblast        Korostenskyi raion 2026-09-12 06:22:33+00:00 2026-09-13 06:57:45+00:00  24.586667         red
722          Donetska oblast        Kramatorskyi raion 2026-09-12 21:27:24+00:00 2026-09-14 16:21:15+00:00  42.897500         red
723          Donetska oblast         Bakhmutskyi raion 2026-09-12 21:27:24+00:00 2026-09-14 16:21:15+00:00  42.897500         red
724          Donetska oblast           Donetskyi raion 2026-09-12 21:27:24+00:00 2026-09-14 16:21:15+00:00  42.897500         red
725          Donetska oblast          Horlivskyi raion 2026-09-12 21:27:24+00:00 2026-09-14 16:21:15+00:00  42.897500         red
726          Donetska oblast          Pokrovskyi raion 2026-09-12 21:27:25+00:00 2026-09-14 16:21:15+00:00  42.897222         red
727          Donetska oblast        Mariupolskyi raion 2026-09-12 21:2
… [обрезано: показано 3000 из 7599 символов]
```

</details>

<details><summary>🔧 Bash: Wait and check frozen reproduction progress · 20:33</summary>

**Аргументы**

```bash
sleep 60; cd /d/Flash/golova/KSE_AI/AAFS && grep -v Warning reviews/scratch/stage8/out_b01.txt | tail
```

**Результат** (ошибка)

```
<tool_use_error>Blocked: sleep 60 followed by: cd /d/Flash/golova/KSE_AI/AAFS grep -v Warning reviews/scratch/stage8/out_b01.txt tail. To wait for a condition, use Monitor with an until-loop (e.g. `until <check>; do sleep 2; done`). To wait for a command you started, use run_in_background: true. Do not chain shorter sleeps to work around this block.</tool_use_error>
```

</details>

<details><summary>🔧 Write: reviews/scratch/stage8/a08_redownload.py · 20:33</summary>

**Аргументы**

```
# file: reviews/scratch/stage8/a08_redownload.py
"""Stage 8 review: what api_config does after the planned second download (PLAN 8.1, D22 limitations).

Simulation in memory, no network: a second download one day later returns the same alerts whose
finished_at (or still open) lies within 30 days of the new request time, with a later request time.
The merge is the one of read_raw (sort by id, updated_at, requested_utc; keep the last).
"""
import pandas as pd

from alerts import api_check as ac
from alerts.config import ROOT, load_config
from alerts.ingest.alerts_in_ua import read_raw

cfg = load_config()
raw = read_raw(ROOT / cfg['api']['raw_dir'])
c1 = ac.api_config(cfg, raw)
print('one download : work_start', c1['periods']['work_start'], 'warmup_end', c1['periods']['warmup_end'], 'data_end', c1['data_end'])

for shift_h in [24, 34]:                      # Monday morning / Monday evening (Kyiv deadline day)
    second = raw.copy()
    second['requested_utc'] = second['requested_utc'] + pd.Timedelta(hours=shift_h)
    fin = second['finished_at'].fillna(second['requested_utc'])
    second = second[fin >= second['requested_utc'] - pd.Timedelta(days=30)]     # month_ago window by finished_at
    both = pd.concat([raw, second], ignore_index=True)
    merged = both.sort_values(['id', 'updated_at', 'requested_utc']).drop_duplicates('id', keep='last')
    c2 = ac.api_config(cfg, merged)
    only_first = (~raw['id'].isin(second['id'])).sum()
    print(f'+{shift_h} h download: ids only in the first download {only_first}; '
          f'work_start {c2["periods"]["work_start"]}, warmup_end {c2["periods"]["warmup_end"]}, data_end {c2["data_end"]}; '
          f'earliest requested_utc after merge {merged["requested_utc"].min()}')
    days = pd.date_range(pd.Timestamp(c2['periods']['warmup_end']), pd.Timestamp(c2['data_end']), freq='h', inclusive='left')
    print(f'   forecast moments {len(days)} (one download: '
          f'{len(pd.date_range(pd.Timestamp(c1["periods"]["warmup_en
… [обрезано: показано 2000 из 2069 символов]
```

**Результат**

```
File created successfully at: d:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage8\a08_redownload.py (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Bash: Simulate second download merge effect on periods · 20:33</summary>

**Аргументы**

```bash
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage8/a08_redownload.py 2>&1 | grep -v Warning
```

**Результат**

```
one download : work_start 2026-09-12T00:00:00+00:00 warmup_end 2026-09-19T00:00:00+00:00 data_end 2026-10-11T08:00:00+00:00
+24 h download: ids only in the first download 513; work_start 2026-09-13T00:00:00+00:00, warmup_end 2026-09-20T00:00:00+00:00, data_end 2026-10-11T08:00:00+00:00; earliest requested_utc after merge 2026-10-11 08:46:02+00:00
   forecast moments 512 (one download: 536)
+34 h download: ids only in the first download 720; work_start 2026-09-13T00:00:00+00:00, warmup_end 2026-09-20T00:00:00+00:00, data_end 2026-10-11T08:00:00+00:00; earliest requested_utc after merge 2026-10-11 08:46:02+00:00
   forecast moments 512 (one download: 536)
```

</details>

<details><summary>🔧 Bash: Check frozen reproduction output · 20:34</summary>

**Аргументы**

```bash
grep -v Warning reviews/scratch/stage8/out_b01.txt | tail; ls -la reviews/scratch/stage8/out 2>/dev/null
```

**Результат**

```
WARNING:alerts.pipeline:Channel outage (D15): 2026-08-29 05:55:28+00:00 -> 2026-09-02 13:48:04+00:00 (4 days 07:52:36)
total 2256
drwxr-xr-x 1 chyck 197609      0 Oct 11 20:33 .
drwxr-xr-x 1 chyck 197609      0 Oct 11 20:33 ..
-rw-r--r-- 1 chyck 197609 541877 Oct 11 20:31 data_a.parquet
-rw-r--r-- 1 chyck 197609 822840 Oct 11 20:31 data_v_test.parquet
-rw-r--r-- 1 chyck 197609 937439 Oct 11 20:33 frozen_h1.parquet
```

</details>

<details><summary>🔧 Write: reviews/scratch/stage8/a09_features.py · 20:34</summary>

**Аргументы**

```
# file: reviews/scratch/stage8/a09_features.py
"""Stage 8 review: feature shift between the Vadimkin test and the API part; left-censored since_end."""
from pathlib import Path

import numpy as np
import pandas as pd

from alerts.features import NUMERIC

pd.set_option('display.width', 250)
OUT = Path(__file__).resolve().parent / 'out'
a = pd.read_parquet(OUT / 'data_a.parquet')
v = pd.read_parquet(OUT / 'data_v_test.parquet')
a = a[(a['part'] == 'test') & a['y_3'].notna()]
v = v[v['y_3'].notna()]
print('rows h=3: API', len(a), 'Vadimkin test', len(v))
rows = []
for f in NUMERIC:
    rows.append({'feature': f, 'vad_mean': v[f].mean(), 'api_mean': a[f].mean(), 'vad_nan': v[f].isna().mean(), 'api_nan': a[f].isna().mean()})
print(pd.DataFrame(rows).round(3).to_string(index=False))
print('base rate h=3: Vadimkin test', round(v['y_3'].astype(float).mean(), 3), 'API', round(a['y_3'].astype(float).mean(), 3))
na = a[a['since_end_log_h'].isna()]
print('\nAPI rows with since_end NaN (no end seen since the window start):', len(na), 'units', na['unit_id'].nunique(),
      'by oblast', na['oblast'].value_counts().to_dict(), 'positives', int(na['y_3'].sum()))
# the largest since_end the API window allows vs what Vadimkin shows
print('max since_end hours: API', round(float(np.expm1(a['since_end_log_h'].max())), 1), ' Vadimkin test', round(float(np.expm1(v['since_end_log_h'].max())), 1))
# rows whose since_end is capped by the window start (Sep 11 ~09:00): since_end >= t - window start
ws = pd.Timestamp('2026-09-11 09:00', tz='UTC')
cap = (np.expm1(a['since_end_log_h']) * 3600 >= (a['t'] - ws).dt.total_seconds() - 3600 * 24 * 1)
print('API rows with since_end within a day of the window-start cap:', int(cap.sum()))

```

**Результат**

```
File created successfully at: d:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage8\a09_features.py (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Bash: Compare feature distributions API vs Vadimkin · 20:34</summary>

**Аргументы**

```bash
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage8/a09_features.py 2>&1 | grep -v Warning
```

**Результат**

```
rows h=3: API 42004 Vadimkin test 46270
                      feature  vad_mean  api_mean  vad_nan  api_nan
              since_end_log_h     3.089     2.584    0.000    0.000
                    starts_6h     0.488     0.691    0.000    0.000
                   starts_24h     2.178     3.028    0.000    0.000
                    starts_7d    15.757    21.125    0.000    0.000
             active_share_24h     0.110     0.148    0.000    0.000
          oblast_active_share     0.071     0.110    0.011    0.008
            oblast_starts_30m     0.153     0.252    0.000    0.000
            oblast_starts_60m     0.371     0.557    0.000    0.000
               oblasts_active     7.221     9.787    0.000    0.000
           country_starts_30m     5.285     8.097    0.000    0.000
           country_starts_60m    11.299    16.079    0.000    0.000
neighbor_oblasts_active_share     0.199     0.309    0.000    0.000
  neighbor_units_active_share     0.068     0.110    0.000    0.000
          neighbor_starts_60m     0.373     0.599    0.000    0.000
                    hour_kyiv    11.667    11.403    0.000    0.000
                     dow_kyiv     3.055     3.149    0.000    0.000
                     hour_sin    -0.018     0.007    0.000    0.000
                     hour_cos     0.003     0.005    0.000    0.000
                      dow_sin    -0.023    -0.072    0.000    0.000
                      dow_cos    -0.044     0.017    0.000    0.000
base rate h=3: Vadimkin test 0.255 API 0.34

API rows with since_end NaN (no end seen since the window start): 0 units 0 by oblast {} positives 0
max since_end hours: API 570.3  Vadimkin test 621.9
API rows with since_end within a day of the window-start cap: 0
```

</details>

<details><summary>🔧 Bash: Wait until frozen reproduction finishes · 20:34</summary>

**Аргументы**

```bash
until grep -q "done in" reviews/scratch/stage8/out_b01.txt; do sleep 5; done; grep -v Warning reviews/scratch/stage8/out_b01.txt
```

**Результат**

```
WARNING:alerts.pipeline:Channel outage (D15): 2026-08-29 05:55:28+00:00 -> 2026-09-02 13:48:04+00:00 (4 days 07:52:36)
data built in 36 s: Vadimkin 615,151 rows, API 42,151 rows
h=1: 42,151 rows, 23 days, fit 51 s; PR-AUC LGBM 0.501, LGBM-B1 +0.103 [+0.086, +0.118]
   LR - B1_live: PR-AUC +0.036 [+0.020, +0.050], log loss -0.022
   LGBM - B1_live: PR-AUC +0.052 [+0.032, +0.067], log loss -0.031
h=3: 42,004 rows, 23 days, fit 44 s; PR-AUC LGBM 0.750, LGBM-B1 +0.094 [+0.081, +0.106]
   LR - B1_live: PR-AUC -0.003 [-0.025, +0.016], log loss -0.012
   LGBM - B1_live: PR-AUC +0.021 [+0.002, +0.036], log loss -0.023
h=6: 41,785 rows, 23 days, fit 36 s; PR-AUC LGBM 0.859, LGBM-B1 +0.066 [+0.058, +0.074]
   LR - B1_live: PR-AUC +0.000 [-0.017, +0.014], log loss -0.012
   LGBM - B1_live: PR-AUC +0.006 [-0.008, +0.017], log loss -0.019
done in 227 s
```

</details>

<details><summary>🔔 Уведомление: Background command "Reproduce frozen predictions and B1_live" completed (exit code 0) · 20:35</summary>

```
<task-notification>
<task-id>bapm8xkfg</task-id>
<tool-use-id>toolu_015fLob9pE3FduhqBYDNoBtc</tool-use-id>
<output-file>C:\Users\chyck\AppData\Local\Temp\claude\d--Flash-golova-KSE-AI-AAFS\57049ae5-374c-471e-8191-1ff2343b8a66\tasks\bapm8xkfg.output</output-file>
<status>completed</status>
<summary>Background command "Reproduce frozen predictions and B1_live" completed (exit code 0)</summary>
</task-notification>
```

</details>

<details><summary>🔧 Write: reviews/scratch/stage8/b02_live.py · 20:35</summary>

**Аргументы**

```
# file: reviews/scratch/stage8/b02_live.py
"""Stage 8 review: robustness of "frozen LightGBM beats B1_live" (h = 1, 3, 6).

Uses the predictions saved by b01_frozen.py. Checks: per-day differences, start day of B1_live,
jackknife over days, history length of B1_live.
"""
from pathlib import Path

import numpy as np
import pandas as pd

from alerts.backtest import walk_forward
from alerts.config import load_config, ts
from alerts.metrics import bootstrap, score
from alerts.models.baselines import UnitHourRate

pd.set_option('display.width', 250)
OUT = Path(__file__).resolve().parent / 'out'
cfg = load_config()
data_a = pd.read_parquet(OUT / 'data_a.parquet')
warm = pd.Timestamp('2026-09-19', tz='UTC')
end = pd.Timestamp('2026-10-12', tz='UTC')
bs = cfg['bootstrap']

for h in [1, 3, 6]:
    preds = pd.read_parquet(OUT / f'frozen_h{h}.parquet')
    all_days = pd.date_range(warm + pd.Timedelta(days=1), end, freq='D', inclusive='left')
    live = walk_forward(data_a, h, all_days, lambda: UnitHourRate(cfg)).set_index('row')
    p = preds.loc[live.index].assign(p_B1_live=live['p'])
    print(f'\n=== h = {h} ===')
    # per day
    rows = []
    for d, g in p.groupby('day'):
        s = {m: score(g['y'], g[f'p_{m}'])['pr_auc'] for m in ['LGBM', 'LR', 'B1_live', 'B1']}
        rows.append({'day': d.date(), 'hist_days': (d - warm).days, 'n': len(g), 'pos': int(g['y'].sum()),
                     'LGBM-B1live': s['LGBM'] - s['B1_live'], 'LR-B1live': s['LR'] - s['B1_live']})
    pdays = pd.DataFrame(rows)
    sub = pdays[pdays['hist_days'] >= 7]
    print(pdays.round(3).to_string(index=False))
    print(f"days from Sep 26 (16): LGBM > B1_live on {int((sub['LGBM-B1live'] > 0).sum())} of {len(sub)}; "
          f"mean daily diff {sub['LGBM-B1live'].mean():+.3f}; Spearman(diff, history) "
          f"{sub['LGBM-B1live'].corr(sub['hist_days'], method='spearman'):+.2f}")
    # start day sensitivity (the report uses history >= 7 days, i.e. from Sep 26)
    for k in [1, 4, 7, 10, 14]:
… [обрезано: показано 2000 из 3372 символов]
```

**Результат**

```
File created successfully at: d:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage8\b02_live.py (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Bash: Robustness of LGBM vs B1_live comparison · 20:35</summary>

**Аргументы**

```bash
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage8/b02_live.py 2>&1 | grep -v Warning
```

**Результат**

```
=== h = 1 ===
       day  hist_days    n  pos  LGBM-B1live  LR-B1live
2026-09-20          1 1853  353        0.068      0.061
2026-09-21          2 1849  330        0.059      0.060
2026-09-22          3 1899  358        0.013      0.025
2026-09-23          4 1938  437       -0.075     -0.056
2026-09-24          5 1562  283        0.079      0.084
2026-09-25          6 1890  397        0.004     -0.025
2026-09-26          7 1941  326        0.076      0.080
2026-09-27          8 1958  284       -0.003      0.011
2026-09-28          9 1855  360        0.015     -0.003
2026-09-29         10 1931  306        0.071      0.047
2026-09-30         11 1557  232        0.036      0.029
2026-10-01         12 1996  268        0.019     -0.011
2026-10-02         13 2058  255        0.042      0.045
2026-10-03         14 2133  274        0.032      0.029
2026-10-04         15 2039  309        0.064      0.043
2026-10-05         16 1977  288        0.016      0.005
2026-10-06         17 2078  294        0.019      0.012
2026-10-07         18 1726  329       -0.061     -0.063
2026-10-08         19 1766  360        0.047      0.019
2026-10-09         20 1844  458        0.023     -0.013
2026-10-10         21 1715  491        0.025     -0.026
2026-10-11         22  630  147       -0.018     -0.001
days from Sep 26 (16): LGBM > B1_live on 13 of 16; mean daily diff +0.025; Spearman(diff, history) -0.29
  B1_live from 2026-09-20 (22 days, >= 1 days of history): LGBM-B1_live +0.043 [+0.020, +0.061]; LR-B1_live +0.034 [+0.016, +0.050]; B1_live PR-AUC 0.456
  B1_live from 2026-09-23 (19 days, >= 4 days of history): LGBM-B1_live +0.041 [+0.015, +0.061]; LR-B1_live +0.029 [+0.009, +0.044]; B1_live PR-AUC 0.450
  B1_live from 2026-09-26 (16 days, >= 7 days of history): LGBM-B1_live +0.052 [+0.032, +0.067]; LR-B1_live +0.036 [+0.020, +0.050]; B1_live PR-AUC 0.435
  B1_live from 2026-09-29 (13 days, >= 10 days of history): LGBM-B1_live +0.055 [+0.033, +0.070]; LR-B1_live +0.036 [+0.018, +0.047]; B1_live PR-AUC 0.424
  B1_live from 2026-10-03 (9 days, >= 14 days of history): LGBM-B1_live +0.054 [+0.019, +0.073]; LR-B1_live +0.031 [+0.000, +0.046]; B1_live PR-AUC 0.440
  jackknife over 16 days: diff +0.052, se 0.0095, t-interval [+0.032, +0.072]; min/max leave-one-day-out +0.046 / +0.056

=== h = 3 ===
       day  hist_days    n  pos  LGBM-B1live  LR-B1live
2026-09-20          1 1853  624        0.098      0.079
2026-09-21          2 1849  636        0.054      0.058
2026-09-22          3 1899  633       -0.025     -0.017
2026-09-23          4 1938  825       -0.020     -0.011
2026-09-24          5 1562  543        0.038     -0.006
2026-09-25          6 1890  722        0.013     -0.019
2026-09-26          7 1941  597        0.073      0.053
2026-09-27          8 1958  596       -0.008     -0.028
2026-09-28          9 1855  685       -0.005     -0.036
2026-09-29         10 1931  633        0.029     -0.009
2026-09-30         11 1557  437        0.039      0.041
2026-10-01    
… [обрезано: показано 3000 из 6896 символов]
```

</details>

*[ошибка API · 20:38: You&#x27;ve hit your weekly limit · resets 2am (Europe/Kyiv)]*

<details><summary>🔧 Bash: Check tests and tracked files for stage 8 · 08:42</summary>

**Аргументы**

```bash
cd "D:/Flash/golova/KSE_AI/AAFS" && grep -rn "alerts_in_ua\|api_check\|alert_level" tests/ | head; cat .gitignore; git ls-files data reports | head -40; git ls-files | grep -i "alerts_in_ua\|api_check"
```

**Результат**

```
.vs/
venv/
dataset_repo/
__pycache__/
*.pyc
.pytest_cache/
data/*.parquet
reviews/scratch/
scratch-gpro/

# secrets: never in version control
alerts_api/token.txt
*.token
.env
data/raw/
data/alerts_in_ua_locations.csv
data/intervals.csv
data/mask.csv
data/neighbors.csv
data/seen.csv
data/units.csv
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
data/alerts_in_ua_locations.csv
reports/api_check.md
scripts/api_check.py
scripts/fetch_alerts_in_ua.py
src/alerts/api_check.py
src/alerts/ingest/alerts_in_ua.py
```

</details>

<details><summary>🔧 Bash: Check whether volunteer commit is fetched by fetch_data · 08:42</summary>

**Аргументы**

```bash
cd "D:/Flash/golova/KSE_AI/AAFS" && grep -n "clone\|fetch\|checkout\|depth\|commit" scripts/fetch_data.py | head -20; git -C dataset_repo log --oneline -1 bf0c323 2>&1 | head -2; git -C dataset_repo rev-parse HEAD
```

**Результат**

```
1:"""Get the pinned dataset snapshot (D01): clone if missing, check out the commit, verify SHA-256."""
28:        _git('clone', ds['repo_url'], str(repo))
30:        _git('-C', str(repo), 'fetch', 'origin')
31:    _git('-C', str(repo), 'checkout', '--quiet', ds['commit'])
35:        raise ValueError(f'SHA-256 mismatch after checkout of {ds["commit"]}: {got}')
36:    logger.info(f'Snapshot {ds["commit"][:7]} checked out and verified')
bf0c323 Add new data
58ee75bc20113181b9ddf8029d4cbf3a62d8cd10
```

</details>

<details><summary>🔧 Write: reviews/scratch/stage8/a10_known_at.py · 08:43</summary>

**Аргументы**

```
# file: reviews/scratch/stage8/a10_known_at.py
"""Stage 8 review: with processor.enabled = false, known_at(cut) is plain truncation at the cut."""
import pandas as pd

from common import api_inputs
from alerts.leakage import known_at

cfg, cfg_a, raw, units, neighbors, locations, recs, st = api_inputs()
df = recs.drop(columns=['alert_level', 'api_id'])
cut = pd.Timestamp('2026-09-29 14:00', tz='UTC')
k = known_at(df, cut, cfg_a)
plain = df[df['started_at'] <= cut].copy()
still = plain['finished_at'] > cut
plain.loc[still, 'finished_at'] = cut + pd.Timedelta(seconds=1)
plain['duration'] = (plain['finished_at'] - plain['started_at']).dt.total_seconds()
plain = plain.reset_index(drop=True)
print('known_at == truncation at the cut:', k.equals(plain), '; rows', len(k), '; open at cut', int(still.sum()))
# with the Vadimkin rules switched on, the same records give a different replay?
k2 = known_at(df, cut, cfg)
print('with processor.enabled = true the replay differs:', not k2.equals(k),
      '(API records of exactly 3600 s:', int((df['duration'] == 3600).sum()), ')')

```

**Результат**

```
File created successfully at: D:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage8\a10_known_at.py (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Bash: Verify known_at equals truncation for API · 08:43</summary>

**Аргументы**

```bash
cd "D:/Flash/golova/KSE_AI/AAFS" && PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage8/a10_known_at.py 2>&1 | grep -v Warning
```

**Результат**

```
known_at == truncation at the cut: True ; rows 8620 ; open at cut 31
with processor.enabled = true the replay differs: False (API records of exactly 3600 s: 0 )
```

</details>

<details><summary>🔧 Bash: Locate cited lines in docs · 08:43</summary>

**Аргументы**

```bash
cd "D:/Flash/golova/KSE_AI/AAFS" && grep -n "1 644\|открыты 60\|1.27\|Профиль по часам\|сохраняет преимущество\|понедельник\|read_raw\|пройдена\|Повторное" DECISIONS.md PLAN.md | head -20; grep -n "пройдено\|×1.25\|при h = 1 і 3\|Відтворити\|alert_level" README.md; grep -n "alert_level\|notes" PLAN.md DECISIONS.md src/alerts/ingest/alerts_in_ua.py | head
```

**Результат**

```
DECISIONS.md:469:- Реальная версия — в `run_all.py`, срезы 2026-08-10 00:00 и 2026-08-21 14:00, результат в `reports/leakage_check.json`. Проверка пройдена: 568 и 593 тысячи обучающих строк, будущее после среза действительно изменилось.
DECISIONS.md:553:**Проверка утечки** пройдена для всех пяти моделей в обоих срезах на реальных данных (`reports/leakage_check.json`): обучающие строки, метки, признаки и прогнозы совпали бит в бит, набор строк в момент среза совпал полностью. Синтетическая версия (`tests/test_leakage.py`) включает LR и LightGBM с весом свежести.
DECISIONS.md:603:- всего 16 532 записи. Отброшены 282 `artillery_shelling`, одна `urban_fights` и 1 644 записи уровней city/hromada. На момент скачивания открыты 60 тревог: их конец — время запроса, позже `data_end`.
DECISIONS.md:621:- **реальное изменение или другой источник?** Волонтёрский ряд (`bf0c323`, закреплён хэшем) покрывает оба окна. На уровне областей у волонтёров начал стало ×1.25, у пары «Vadimkin → API» ×1.59. Значит, API фиксирует примерно в 1.27 раза больше начал, чем Vadimkin для той же реальности. Это сдвигает признаки-счётчики, и к этому надо относиться как к смене источника;
DECISIONS.md:623:- группы клонов (D07) в API те же (Жаккар ≈ 1.0). Профиль по часам суток изменился в реальности, а не из-за источника: у волонтёров август против сентября–октября — 0.69.
DECISIONS.md:635:- Честное сравнение — с B1, который каждый день переобучается только на строках API (без склейки источников), на днях, где у него есть хотя бы неделя истории. Против него модель, замороженная месяц назад, сохраняет преимущество при h = 1 и 3, того же порядка, что на основном тесте (D20). При h = 6 преимущества нет.
DECISIONS.md:638:**Проверка утечки (8.6)** на срезе 2026-09-29 14:00, внутри периода API, пройдена:
DECISIONS.md:643:- данные скачаны один раз, в воскресенье. Повторное скачивание объединяется по `id` с более поздним `updated_at` (`read_raw`);
PLAN.md:6:- Дедлайн: понедельник, 12.10.2026, 23:59 по Киеву.
PLAN.md:221:**Как сделано:** `src/alerts/models/learned.py`, `src/alerts/tuning.py`, решения и цифры — D20, отчёт — `reports/backtest_h3.md`. Гиперпараметры выбраны один раз на валидации, включая вес свежих данных (у LightGBM полураспад 28 дней). На тесте LightGBM лучше лучшего бейзлайна B1: PR-AUC 0.701 против 0.674, разность +0.027 [+0.010, +0.041]; log loss −0.021 [−0.033, −0.009]. Проверка утечки пройдена для всех моделей. Горизонты 1 и 6 не прогонялись (сокращаются первыми).
PLAN.md:243:**Как сделано:** скачивание — `scripts/fetch_alerts_in_ua.py` (11.10, 28 запросов, все 200); адаптер — `src/alerts/ingest/alerts_in_ua.py` (119 из 119 локаций; апостроф и Киев — D22); проверка — `scripts/api_check.py` и `src/alerts/api_check.py`, отчёт — `reports/api_check.md`; решения и цифры — D22. Сверх плана — B1, обновляемый на данных API: без него выигрыш замороженной модели был бы завышен втрое. Итог: против обновляемого B1 модель, замороженная месяц назад, сохраняет преимущество при h = 1 и 3
… [обрезано: показано 3000 из 3989 символов]
```

</details>

<details><summary>🔧 Read: reports/figures/api_vs_vadimkin.png · 08:44</summary>

**Аргументы**

```json
{
 "file_path": "D:\\Flash\\golova\\KSE_AI\\AAFS\\reports\\figures\\api_vs_vadimkin.png"
}
```

**Результат**

```
[изображение опущено]
```

</details>

<details><summary>🔧 Bash: Create report directory · 08:44</summary>

**Аргументы**

```bash
cd "D:/Flash/golova/KSE_AI/AAFS" && mkdir -p reviews/claude && ls reviews/claude
```

**Результат**

```
stage0-1b.md
stage3.md
```

</details>

<details><summary>🔧 Write: reviews/claude/stage8.md · 08:45</summary>

**Аргументы**

```
# file: reviews/claude/stage8.md
# Ревью этапа 8: проверка на свежих данных alerts.in.ua

Ревьюер: Claude (независимый). Скрипты и выводы: `reviews/scratch/stage8/` (`a01`–`a10`, `b01`, `b02`, `common.py`; промежуточные прогнозы в `out/`). Всё запускалось из корня с `PYTHONPATH=src`. Файлы проекта не менялись, к API не обращался, токен не открывал.

## 1. Резюме

Код этапа 8 корректен там, где его можно проверить механически. `b01_frozen.py` воспроизвёл все цифры `reports/api_check.md` до третьего знака, утечки в коде не нашёл. Окно `month_ago` обрезается по `finished_at`, поэтому выбор `work_start` и разогрева верен. Сопоставление 119 из 119 и разворачивание областных записей тоже в порядке.

Слабые места — в выводах и процедуре:
- Главный вывод README для основного горизонта («при h = 3 замороженная модель сохраняет преимущество над B1, обновляемым на API») неустойчив. Он держится на правиле старта B1_live, выбранном после того, как результат был виден. Когда у B1_live больше истории, преимущество уходит в шум; по дням оно положительно в 7 из 16 дней.
- Запланированное повторное скачивание в понедельник не добавит понедельник: из-за `data_end = min(requested_utc)` период сократится на сутки.
- Адаптер молча игнорирует поле `alert_level` (yellow/red). Оно делит записи примерно 65/35 и дрейфует внутри периода. В D22 и PLAN о нём ничего нет.
- Проверка утечки на API по построению сводится к обрезке по срезу. Поздних правок со стороны источника она не видит.
- Множитель «×1.27» верен по направлению, но его величина зависит от агрегации (1.1–1.3).

Вердикт: зона рабочая, но формулировки README/D22 надо смягчить, а процедуру повторного скачивания исправить до понедельника.

## 2. Находки

### S8-1. Вывод «преимущество при h = 3 сохраняется» не устойчив к выбору старта B1_live
- **Серьёзность:** критично: меняет вывод README для основного горизонта. **Уверенность:** проверено на данных.
- **Где:** `README.md:106-108`, `DECISIONS.md:635`, `PLAN.md:243`; правило «неделя ис
… [обрезано: показано 2000 из 16252 символов]
```

**Результат**

```
File created successfully at: D:\Flash\golova\KSE_AI\AAFS\reviews\claude\stage8.md (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Bash: Verify long-alert levels and Kyiv level counts · 08:45</summary>

**Аргументы**

```bash
cd "D:/Flash/golova/KSE_AI/AAFS" && PYTHONPATH=src PYTHONIOENCODING=utf-8 python -c "
import sys; sys.path.insert(0,'reviews/scratch/stage8')
from common import api_inputs
from alerts.config import ts
cfg, cfg_a, raw, units, neighbors, locations, recs, st = api_inputs()
d=(recs['finished_at']-recs['started_at']).dt.total_seconds()/3600
l=recs[(d>24)&(recs['finished_at']>ts(cfg_a['periods']['work_start']))]
print(len(l), l['alert_level'].value_counts().to_dict())
k=raw[(raw['location_title']=='м. Київ')&(raw['alert_type']=='air_raid')]
print(k['alert_level'].value_counts().to_dict())
" 2>&1 | grep -v Warning; wc -l reviews/claude/stage8.md
```

**Результат**

```
101 {'red': 91, 'yellow': 10}
{'yellow': 201, 'red': 16}
129 reviews/claude/stage8.md
```

</details>

<details><summary>🔧 Bash: Correct three facts in the report · 08:46</summary>

**Аргументы**

```bash
cd "D:/Flash/golova/KSE_AI/AAFS" && python - <<'EOF'
p='reviews/claude/stage8.md'
s=open(p,encoding='utf-8').read()
reps=[
("у Киева 202 из 217 записей yellow","у Киева 201 из 217 записей yellow"),
("  - все 101 запись длиннее 24 часов имеют уровень red;\n","  - из 101 записи длиннее 24 часов 91 имеет уровень red;\n"),
("  - что именно менялось в пачке, по одному снимку не определить: у 15 из 57 записей `notes` = NaN, у одной — пустая строка.\n",
 "  - что именно менялось в пачке, по одному снимку не определить: прежней версии записи нет.\n"),
]
for a,b in reps:
    assert a in s, a
    s=s.replace(a,b)
open(p,'w',encoding='utf-8').write(s)
EOF
grep -n "201 из 217\|91 имеет\|прежней версии" reviews/claude/stage8.md
```

**Результат**

```
50:  - у районных `air_raid` 9 280 yellow и 4 888 red; у Киева 201 из 217 записей yellow;
54:  - из 101 записи длиннее 24 часов 91 имеет уровень red;
73:  - что именно менялось в пачке, по одному снимку не определить: прежней версии записи нет.
```

</details>

<details><summary>🔧 Bash: Confirm no project files modified · 08:46</summary>

**Аргументы**

```bash
cd "D:/Flash/golova/KSE_AI/AAFS" && git status --short | head
```

**Результат**

```
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

<details><summary>🔧 SubagentHandback: {"message": "Ревью этапа 8 записано в `D:\\Flash\\golova\\KSE_AI\\AAFS\\reviews\\claude\\stage8.md`. Отчёт в `reviews/s… · 08:46</summary>

**Аргументы**

```json
{
 "message": "Ревью этапа 8 записано в `D:\\Flash\\golova\\KSE_AI\\AAFS\\reviews\\claude\\stage8.md`. Отчёт в `reviews/stage8.md` я раньше не записывал, поэтому восстанавливать было нечего. Файлы другой группы ревьюеров не читал. Все ограничения соблюдены: файлы проекта не трогал, к API не обращался, токен не открывал. В `git status` есть изменённый `.gitignore`, но его правил не я.\n\n**Резюме**\n- Код этапа 8 корректен там, где его можно проверить механически. Мой скрипт `b01_frozen.py` (LightGBM на 2 потоках) воспроизвёл все цифры `reports/api_check.md` до третьего знака, включая B1_live. Утечки в коде нет.\n- Окно `month_ago` обрезается по `finished_at`, а не по началу. Поэтому `work_start` = 12.09 и разогрев 7 дней выбраны верно; строк, где время с последнего отбоя (`since_end`) не определено, в API-части 0.\n- Сопоставление 119 из 119, Киев, разворачивание областной записи (единственная, по Николаевской области, совпадает с районными до секунды, двойного счёта нет) и слияние по `id` — в порядке.\n- Слабые места в выводах и процедуре: вывод README для h = 3 неустойчив; повторное скачивание в понедельник сократит период; поле `alert_level` игнорируется; проверка утечки на API сводится к обрезке по срезу; «×1.27» верно по направлению, но не по величине.\n- По известным 57 записям с поздним `updated_at` есть новое: у всех 55 записей пачки следующая тревога того же района началась до обновления, так что «висели открытыми до 30.09» опровергнуто. Худший случай затрагивает 62 из 42 004 строк (0.15%).\n- Вердикт: формулировки README и D22 нужно смягчить, а процедуру повторного скачивания исправить до понедельника. Перезапуск `run_all.py` ни для одного исправления не нужен.\n\n**Находки уровня «критично» и «существенно»**\n- **S8-1, критично, проверено на данных.** Вывод «при h = 3 преимущество над обновляемым B1 сохраняется» держится на правиле «у B1_live не меньше 7 дней истории», выбранном после того, как результат был виден. При ≥ 10 днях истории разность +0.019 [−
… [обрезано: показано 2000 из 4765 символов]
```

**Результат**

```
{"success":true,"message":"Report delivered to your caller."}
```

</details>
