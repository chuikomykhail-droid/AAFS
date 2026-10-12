# Субагент: Review stage 2

- **Агент:** `a3bb0394762b36564` (general-purpose), запущен из сессии [57049ae5](../2026-10-11_critical-analysis_57049ae5.md#t-aXiGmu42NRgX)
- **Период (UTC):** 2026-10-11 17:19 → 2026-10-12 05:50
- **Период (Киев):** 2026-10-11 20:19 → 2026-10-12 08:50
- **Сообщений:** 1 (задания и сообщения основного агента — 1, ответы субагента — 0); вызовов инструментов — 48
- **Исходный JSONL:** `ai_logs/claude_code/raw/claude_code_raw.zip → subagents/57049ae5_agent-a3bb0394762b36564.jsonl`

> Служебные вставки (`<system-reminder>`, вложения с окружением и контекстом IDE, мета-сообщения — 87 записей) и блоки рассуждений (thinking — 36) сюда не включены: они есть в исходном JSONL. Время — киевское. Вызовы инструментов свёрнуты; аргументы обрезаны до 2000 символов, результаты — до 3000. Токен alerts.in.ua и email автора заменены на `[REDACTED_TOKEN]` / `[REDACTED_EMAIL]`.

---

<a id="m-95c4d5cb"></a>

### 📨 Задание от основного агента · 2026-10-11 20:19

Рабочая папка проекта: d:\Flash\golova\KSE_AI\AAFS (Windows; доступны Bash (Git Bash) и PowerShell).

Прочитай файл `reviews/prompts/02_stage2.md` целиком и выполни задание из него в точности, включая все ограничения: не изменять файлы проекта, не запускать `scripts/run_all.py`, `scripts/api_check.py`, скрипты скачивания и `save_all`, не трогать git, не открывать токен. Параллельно с тобой в той же папке работают шесть других агентов-ревьюеров — пиши только в `reviews/stage2.md` и `reviews/scratch/stage2/`.

Когда отчёт записан, верни в ответе: резюме отчёта (5–10 строк) и список находок уровня «критично» и «существенно» — по одной строке на находку (id, суть, файл:строка, уровень проверки).

<details><summary>🔧 Read: reviews/prompts/02_stage2.md · 20:19</summary>

**Аргументы**

```json
{
 "file_path": "d:\\Flash\\golova\\KSE_AI\\AAFS\\reviews\\prompts\\02_stage2.md"
}
```

**Результат**

```
1	# Ревью проекта AAFS: этап 2: интервалы, seen, AlertHistory
2	
3	Ты — независимый критический ревьюер. Параллельно с тобой другие агенты проверяют другие этапы того же проекта. Твоя зона — этап 2: сегменты и эпизоды, таблица `seen` (что видел наблюдатель в реальном времени), доступ к истории «на момент t» (`AlertHistory`), модель процессора датасета. На соседние этапы смотри только тогда, когда без этого не понять твой.
4	
5	## Проект
6	
7	- Репозиторий — текущая папка (`AAFS`), ветка `stages-7-8`. Python-проект: прогноз воздушных тревог в Украине по районам. Для каждой единицы (район; Киев — одна единица), где в момент `t` (каждый час) тихо, модель выдаёт вероятность того, что тревога начнётся в `(t, t+h]`, h = 1, 3, 6 (основной — 3).
8	- Данные — снимок датасета Vadimkin (`dataset_repo/`, коммит `58ee75b`). Официальный ряд заканчивается 2026-09-07. Тест — 2026-08-10…2026-09-07, walk-forward с ежесуточным переобучением. Этап 8 — проверка на данных alerts.in.ua за сентябрь–октябрь.
9	- Это тестовое задание с дедлайном 12.10.2026 23:59 по Киеву. Проверяющие оценивают процесс: пойманные ошибки, обоснованность решений, отсутствие утечки из будущего. Найденная проблема ценна, даже если её не успеют исправить: тогда она уйдёт в раздел ограничений.
10	- Документы: `PLAN.md` (правила работы 1–13; у каждого этапа «Исходное задание» и «Как сделано»), `DECISIONS.md` (решения D00–D22, справочные цифры, журнал пойманных ошибок ИИ), `README.md` (на украинском), отчёты в `reports/`.
11	
12	Сначала прочитай раздел «Правила работы» в `PLAN.md`, описание своего этапа в `PLAN.md` и разделы `DECISIONS.md`: D09, D10, D11, D12, D15, D16, D19 (часть про 24 часа), D21. Код и тесты своей зоны читай целиком, а не выборочно.
13	
14	## Твоя зона: файлы
15	
16	- `src/alerts/spans.py`, `src/alerts/intervals.py`, `src/alerts/processor.py`, `src/alerts/history.py`, `src/alerts/store.py`.
17	- `src/alerts/pipeline.py`: `build_tables`, `alert_history`.
18	- Тесты: `tests/test_intervals.py`, `tests/test_history.py`.
19	- Результаты: `data/intervals.csv`, `data/seen.csv`, `reports/stage2_summary.md`.
20	- Для семантики процессора: `dataset_repo/processors/official_channel_processor.py`.
21	
22	## Что проверить
23	
24	1. **`spans.merge_labels` и `union`.** Проверь края: касающиеся интервалы, вложенные, одинаковые начала, неотсортированный вход, повторяющийся индекс. Сравни с наивной реализацией на случайных данных (property-based тест в scratch).
25	2. **Границы в `AlertHistory`.**
26	   - `active` — `[s, e)`; `starts` — `(t−w, t]`; `seconds_since_end` — последний конец `≤ t`; `seconds_active` — `(t−w, t]`.
27	   - Согласованы ли они между собой, с сеткой (`grid.py`) и с меткой `(t, t+h]`? Что происходит, когда событие ровно в `t`?
28	3. **`seen`.** Ограничение 24 ч применяется к каждой записи до объединения (D19).
29	   - Для единиц из нескольких районов (клоны, Донецкая `I00`): может ли цепочка коротких записей одного района вместе с «зависшей» записью другого дать странный рез
… [обрезано: показано 3000 из 8497 символов]
```

</details>

<details><summary>🔧 Bash: List project structure and file sizes · 20:19</summary>

**Аргументы**

```bash
ls && ls src/alerts tests reviews reviews/scratch 2>/dev/null; wc -l PLAN.md DECISIONS.md src/alerts/*.py tests/*.py
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
   424 PLAN.md
   704 DECISIONS.md
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
  4073 total
```

</details>

<details><summary>🔧 Grep: ^#+ в PLAN.md · 20:19</summary>

**Аргументы**

```json
{
 "pattern": "^#+ ",
 "path": "d:\\Flash\\golova\\KSE_AI\\AAFS\\PLAN.md",
 "output_mode": "content"
}
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

<details><summary>🔧 Grep: ^#+ в DECISIONS.md · 20:19</summary>

**Аргументы**

```json
{
 "pattern": "^#+ ",
 "path": "d:\\Flash\\golova\\KSE_AI\\AAFS\\DECISIONS.md",
 "output_mode": "content"
}
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

<details><summary>🔧 Read: PLAN.md · 20:19</summary>

**Аргументы**

```json
{
 "file_path": "d:\\Flash\\golova\\KSE_AI\\AAFS\\PLAN.md",
 "offset": 1,
 "limit": 300
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
… [обрезано: показано 3000 из 29743 символов]
```

</details>

<details><summary>🔧 Read: DECISIONS.md · 20:19</summary>

**Аргументы**

```json
{
 "file_path": "d:\\Flash\\golova\\KSE_AI\\AAFS\\DECISIONS.md",
 "offset": 181,
 "limit": 230
}
```

**Результат**

```
181	## D09. Сообщения об угрозах в канале
182	
183	**Находка** (по коду процессора и постам канала):
184	- Кроме постов «🔴 Повітряна тривога» и «🟢 Відбій», канал публикует посты «Загроза ударних БпЛА». Цвет маркера означает уровень: 🟠 — угроза, 🔴🔴 — «підвищений рівень небезпеки».
185	- Угрозы публикуются для конкретного города или громады и часто идут **внутри уже объявленной тревоги**. Пример: 08:49 тревога в Харькове, в 08:50 для той же громады 🟠 «БпЛА невизначеного типу».
186	- Процессор считает началом тревоги любой пост с «Повітряна» **или** 🔴 в первой строке. Последствия:
187	  - угроза с 🔴 записывается как начало тревоги, а с 🟠 — пропускается. Одинаковые по типу сообщения обрабатываются по-разному в зависимости от цвета;
188	  - если для места уже идёт тревога, начавшаяся меньше 3 часов назад, новое «начало» её перезаписывает. Настоящий момент начала теряется, тревога выглядит короче;
189	  - если у угрозы нет собственного «відбою», запись остаётся открытой до следующего «відбою» по этому месту. Это вероятный источник многодневных «тревог» в громадах Никопольского района (8–26 дней).
190	- Тревога и угроза — разные сигналы. Тревога — официальный сигнал для территории с парным отбоем. Угроза — уточнение того, что и где летит, внутри тревоги или рядом с ней.
191	
192	**Проверка (вариант B из 1б.4, ручная выборка).** Просмотрены три страницы публичной веб-версии канала, по 20 постов: перед ID 338381 (последние посты, сентябрь 2026), 336000 и 320000. Итог:
193	- всего 60 постов, из них 6 угроз «Загроза ударних БпЛА» (5 с маркером 🔴🔴, 1 с 🟠);
194	- у всех 6 угроз хэштег уровня города и громады (`#м_Запоріжжя_та_Запорізька_територіальна_громада`, `#м_Харків_та_Харківська_територіальна_громада`);
195	- угроз с хэштегом района (`_район`) или области (`_область`) — **0**;
196	- все посты с хэштегами районов — это «Повітряна тривога» или «Відбій тривоги».
197	
198	Попутно подтверждён механизм клонов (D07): один пост «Повітряна тривога в» перечисляет пять районов Запорожской области или три района Одесской, и процессор превращает его в пять или три одинаковые записи.
199	
200	**Решение:** на районном уровне угрозы в данные не попадают; для MVP данные оставляем как есть. Искажения из-за угроз касаются уровня громад и городов, который мы не используем (D08).
201	
202	**Ограничение:** выборка маленькая (60 постов, 3 момента времени). Полная проверка через Telethon (вариант A) не выполнялась; в README указать как ограничение.
203	
204	**Ограничение (найдено при исправлении D16):** если отбой потерян, а новая тревога той же локации пришла в пределах 3 часов, процессор заменяет открытую тревогу новой, и начало первой из CSV исчезает. В реальном времени единица была под тревогой с первого начала, а в данных она выглядит тихой до второго. Следов в CSV нет, поэтому ни замаскировать, ни исправить это нельзя, а насколько это часто, без архива канала не узнать. В README — в ограничения.
205	
206	**Статус:** зафиксировано по ручной выборке.
207	
208	---
209	
210	
… [обрезано: показано 3000 из 20255 символов]
```

</details>

<details><summary>🔧 Read: DECISIONS.md · 20:19</summary>

**Аргументы**

```json
{
 "file_path": "d:\\Flash\\golova\\KSE_AI\\AAFS\\DECISIONS.md",
 "offset": 477,
 "limit": 228
}
```

**Результат**

```
477	## D19. Признаки (этап 5)
478	
479	**Как читается история.** Все признаки — функции от `AlertHistory` (D16), то есть от событий с отметкой `≤ t`. Считаются векторно для всех моментов сразу: матрицы «моменты × единицы» плюс одна выборка по строкам сетки. На 617 тысяч строк — 1.6 с (`src/alerts/features.py`).
480	
481	**Решение по тревогам с неизвестным концом** (открыто с D10/D16): тревога, у которой отбой не виден, считается активной **не дольше 24 часов** (`history.max_open_hours`), как предлагал план. Правило причинное: в момент `t` известно только время начала и то, был ли отбой. Применяется к каждой записи до объединения: иначе единица из нескольких районов (Донецкая, 8 районов с перекрывающимися записями) «погасла» бы посреди многодневной законной тревоги. Это проверяет `tests/test_history.py`. Состояние «на момент t» хранится в `data/seen.csv`. Пар «единица × момент», где тревога держится открытой без видимого отбоя, стало 1 046 вместо 3 529. Строки сетки не изменились.
482	
483	**Перерыв канала (D15):**
484	- строки, у которых последние 24 часа задевают перерыв, в модели не идут (`lookback_ok`): окна 6 и 24 часа у них неполные. Это отбор по времени, а не по исходу; в тесте он убирает 1 758 строк (с 48 402 до 46 644);
485	- число тревог за 7 дней масштабируется на наблюдаемую часть окна (не меньше 38%);
486	- время с последнего отбоя считается только по наблюдаемому времени.
487	
488	Обучающий и валидационный периоды перерыва не содержат, так что для них эти правила — тождество.
489	
490	**Набор** (окна — `(t − w, t]`, левая граница не входит):
491	
492	| Группа | Признаки |
493	|---|---|
494	| Своя единица | `since_end_log_h` — log(1 + часы с последнего отбоя); `starts_6h`, `starts_24h`, `starts_7d` — начала эпизодов; `active_share_24h` |
495	| Своя область | `oblast_active_share` — доля **других** единиц области под тревогой (для областей из одной единицы — пусто); `oblast_starts_30m`, `oblast_starts_60m` |
496	| Страна | `oblasts_active` (24 области, включая Киев и Донецкую); `country_starts_30m`, `country_starts_60m` |
497	| Соседи | `neighbor_oblasts_active_share`; сверх плана — `neighbor_units_active_share`, `neighbor_starts_60m` по соседним единицам |
498	| Календарь | `hour_kyiv`, `dow_kyiv` и их sin/cos (для логистической регрессии) |
499	| Идентичность | `unit_id` (категориальный в LightGBM, one-hot в LR) |
500	
501	Признаков с монотонным трендом («дни с начала данных») нет — урок Kizashi.
502	
503	**Соседство** (`src/alerts/geo.py`, `data/neighbors.csv`, правило 9):
504	- источник — границы районов из того же снимка датасета (`example/ukr_admin2.geojson`, OCHA, действуют с 2025-09-01), закреплены SHA-256;
505	- соседи — районы, у границ которых не меньше двух общих вершин (с округлением до 1e-5°). Пар с единственной общей точкой нет, так что порог ни на что не влияет;
506	- три района переименованы в 2023–2024 годах и сопоставлены явно, в `config.geo.renames`: Красноградский → Берестинский, Червоноградский → Шептицкий, Владим
… [обрезано: показано 3000 из 27795 символов]
```

</details>

<details><summary>🔧 Bash: Print zone source files with line numbers · 20:19</summary>

**Аргументы**

```bash
for f in src/alerts/spans.py src/alerts/intervals.py src/alerts/processor.py src/alerts/history.py src/alerts/store.py src/alerts/pipeline.py src/alerts/timeutil.py; do echo "=== $f"; cat -n $f; done
```

**Результат**

```
=== src/alerts/spans.py
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
    57	def count_in(points: np.ndarray, lo
… [обрезано: показано 3000 из 27481 символов]
```

</details>

<details><summary>🔧 Bash: Print tests and related modules · 20:20</summary>

**Аргументы**

```bash
for f in tests/test_intervals.py tests/test_history.py tests/conftest.py src/alerts/scope.py src/alerts/mask.py src/alerts/grid.py config.yaml; do echo "=== $f"; cat -n $f; done
```

**Результат**

```
<persisted-output>
Output too large (40.3KB). Full output saved to: C:\Users\chyck\.claude\projects\d--Flash-golova-KSE-AI-AAFS\57049ae5-374c-471e-8191-1ff2343b8a66\tool-results\bs1jwovud.txt

Preview (first 2KB):
=== tests/test_intervals.py
     1	import pandas as pd
     2	import pytest
     3	from conftest import records, units_table, utc
     4	
     5	from alerts.intervals import build_intervals, episodes
     6	from alerts.mask import MASK_COLUMNS
     7	from alerts.scope import select_scope
     8	
     9	NO_MASKS = pd.DataFrame(columns=MASK_COLUMNS)
    10	
    11	UNITS = units_table([
    12	    ('Kyiv City', 'Kyiv City', 'U_KYIV'),
    13	    ('A', 'Raion 1', 'U_A'),
    14	    ('A', 'Raion 2', 'U_A'),  # clone of Raion 1
    15	    ('B', 'Raion 3', 'U_B'),
    16	])
    17	
    18	
    19	def kyiv(start, end):
    20	    return ('Kyiv City', None, 'oblast', start, end)
    21	
    22	
    23	def build(rows, cfg, masks=NO_MASKS):
    24	    return episodes(build_intervals(select_scope(records(rows), cfg), UNITS, masks, cfg))
    25	
    26	
    27	@pytest.fixture
    28	def kyiv_cfg(cfg):
    29	    cfg['scope']['oblast_level_units'] = ['Kyiv City']
    30	    return cfg
    31	
    32	
    33	def test_overlap_nesting_pauses_and_masks(kyiv_cfg):
    34	    cfg = kyiv_cfg
    35	    rows = [
    36	        kyiv('2026-01-01T10:00:00Z', '2026-01-01T11:00:00Z'),  # overlap
    37	        kyiv('2026-01-01T10:30:00Z', '2026-01-01T11:30:00Z'),
    38	        kyiv('2026-01-02T10:00:00Z', '2026-01-02T12:00:00Z'),  # nested
    39	        kyiv('2026-01-02T10:30:00Z', '2026-01-02T11:30:00Z'),
    40	        kyiv('2026-01-03T10:00:00Z', '2026-01-03T11:00:00Z'),  # pause of exactly 15 min: merged
    41	        kyiv('2026-01-03T11:15:00Z', '2026-01-03T12:00:00Z'),
    42	        kyiv('2026-01-04T10:00:00Z', '2026-01-04T11:00:00Z'),  # pause of 16 min: not merged
    43	        kyiv('2026-01-04T11:16:00Z', '2026-01-04T12:00:00Z'),
    44	        ('B', 'Raion 3', 'raion', '2026-01-05T10:00:00Z', '2026-01-05T11:00:00Z'),
    45	    ]
    46	    masks = pd.DataFrame([{'unit_id': 'U_KYIV', 'start': utc('2026-01-04T10:00:00Z'),
...
</persisted-output>
```

</details>

<details><summary>🔧 Read: C:/Users/chyck/.claude/projects/d--Flash-golova-KSE-AI-AAFS/57049ae5-374c-471e-8191-1ff2343b8a66/tool-results/bs1jwovud… · 20:20</summary>

**Аргументы**

```json
{
 "file_path": "C:\\Users\\chyck\\.claude\\projects\\d--Flash-golova-KSE-AI-AAFS\\57049ae5-374c-471e-8191-1ff2343b8a66\\tool-results\\bs1jwovud.txt"
}
```

**Результат**

```
1	=== tests/test_intervals.py
2	     1	import pandas as pd
3	     2	import pytest
4	     3	from conftest import records, units_table, utc
5	     4	
6	     5	from alerts.intervals import build_intervals, episodes
7	     6	from alerts.mask import MASK_COLUMNS
8	     7	from alerts.scope import select_scope
9	     8	
10	     9	NO_MASKS = pd.DataFrame(columns=MASK_COLUMNS)
11	    10	
12	    11	UNITS = units_table([
13	    12	    ('Kyiv City', 'Kyiv City', 'U_KYIV'),
14	    13	    ('A', 'Raion 1', 'U_A'),
15	    14	    ('A', 'Raion 2', 'U_A'),  # clone of Raion 1
16	    15	    ('B', 'Raion 3', 'U_B'),
17	    16	])
18	    17	
19	    18	
20	    19	def kyiv(start, end):
21	    20	    return ('Kyiv City', None, 'oblast', start, end)
22	    21	
23	    22	
24	    23	def build(rows, cfg, masks=NO_MASKS):
25	    24	    return episodes(build_intervals(select_scope(records(rows), cfg), UNITS, masks, cfg))
26	    25	
27	    26	
28	    27	@pytest.fixture
29	    28	def kyiv_cfg(cfg):
30	    29	    cfg['scope']['oblast_level_units'] = ['Kyiv City']
31	    30	    return cfg
32	    31	
33	    32	
34	    33	def test_overlap_nesting_pauses_and_masks(kyiv_cfg):
35	    34	    cfg = kyiv_cfg
36	    35	    rows = [
37	    36	        kyiv('2026-01-01T10:00:00Z', '2026-01-01T11:00:00Z'),  # overlap
38	    37	        kyiv('2026-01-01T10:30:00Z', '2026-01-01T11:30:00Z'),
39	    38	        kyiv('2026-01-02T10:00:00Z', '2026-01-02T12:00:00Z'),  # nested
40	    39	        kyiv('2026-01-02T10:30:00Z', '2026-01-02T11:30:00Z'),
41	    40	        kyiv('2026-01-03T10:00:00Z', '2026-01-03T11:00:00Z'),  # pause of exactly 15 min: merged
42	    41	        kyiv('2026-01-03T11:15:00Z', '2026-01-03T12:00:00Z'),
43	    42	        kyiv('2026-01-04T10:00:00Z', '2026-01-04T11:00:00Z'),  # pause of 16 min: not merged
44	    43	        kyiv('2026-01-04T11:16:00Z', '2026-01-04T12:00:00Z'),
45	    44	        ('B', 'Raion 3', 'raion', '2026-01-05T10:00:00Z', '2026-01-05T11:00:00Z'),
46	    45	    ]
47	    46	    masks = pd.DataFrame([{'unit_id': 'U_KYIV', 'start': utc('2026-01-04T10:00:00Z'),
48	    47	                           'end': utc('2026-01-04T11:16:00Z'), 'reason': 'fake_1h'}])
49	    48	    ep = build(rows, cfg, masks)
50	    49	    k = ep[ep['unit_id'] == 'U_KYIV']
51	    50	    k = k.set_index(k['start_utc'].dt.day.rename('day'))
52	    51	
53	    52	    assert (k.loc[1, 'start_utc'], k.loc[1, 'end_utc']) == (utc('2026-01-01T10:00:00Z'), utc('2026-01-01T11:30:00Z'))
54	    53	    assert (k.loc[2, 'start_utc'], k.loc[2, 'end_utc']) == (utc('2026-01-02T10:00:00Z'), utc('2026-01-02T12:00:00Z'))
55	    54	    assert (k.loc[3, 'start_utc'], k.loc[3, 'end_utc']) == (utc('2026-01-03T10:00:00Z'), utc('2026-01-03T12:00:00Z'))
56	    55	    jan4 = k.loc[4].sort_values('start_utc')
57	    56	    assert len(jan4) == 2
58	    57	    assert jan4['uncertain'].tolist() == [True, False]  # the mask ends where the second alert starts
59	    58	    assert ep.loc[ep['unit_id'] == 'U_B', 'uncertain'].tolist()
… [обрезано: показано 3000 из 43526 символов]
```

</details>

<details><summary>🔧 Bash: Print dataset processor code · 20:20</summary>

**Аргументы**

```bash
cat -n dataset_repo/processors/official_channel_processor.py; ls dataset_repo/processors
```

**Результат**

```
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
    71	            self.active_alerts_by_location = pickle.load(f)
    72	
    73	    def dump_active_alert
… [обрезано: показано 3000 из 17155 символов]
```

</details>

<details><summary>🔧 Bash: Print leakage, features, knowledge test · 20:21</summary>

**Аргументы**

```bash
cat -n src/alerts/leakage.py src/alerts/features.py; cat -n tests/test_knowledge.py
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
… [обрезано: показано 3000 из 16432 символов]
```

</details>

<details><summary>🔧 Bash: Show stage 2 summary and data heads · 20:24</summary>

**Аргументы**

```bash
cat reports/stage2_summary.md; echo ----; head -5 data/intervals.csv data/seen.csv; wc -l data/intervals.csv data/seen.csv; git log --oneline -3 -- data/intervals.csv data/seen.csv; git status --short | head
```

**Результат**

```
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
----
==> data/intervals.csv <==
unit_id,start_utc,end_utc,uncertain,episode,n_records
I00,2025-11-06 22:48:24+00:00,2025-11-08 05:34:08+00:00,True,0,8
I00,2025-11-08 06:16:07+00:00,2025-11-09 06:15:11+00:00,False,1,8
I00,2025-11-09 06:53:32+00:00,2025-11-09 23:21:14+00:00,False,2,8
I00,2025-11-10 04:19:03+00:00,2025-11-10 15:23:23+00:00,False,3,8

==> data/seen.csv <==
unit_id,start,end
I00,2025-11-06 22:48:24+00:00,2025-11-07 22:48:32+00:00
I00,2025-11-08 06:16:07+00:00,2025-11-09 06:15:11+00:00
I00,2025-11-09 06:53:32+00:00,2025-11-09 23:21:14+00:00
I00,2025-11-10 04:19:03+00:00,2025-11-10 15:23:23+00:00
  73738 data/intervals.csv
  73689 data/seen.csv
 147427 total
4c6e5d8 Stages 3-6: grid and targets, backtest with baselines, features, models
4203bc2 Fix as-of leak from processor-invented alert ends (D16)
53e2373 Stage 2 review: channel outage mask, as-of history, refactor
```

</details>

<details><summary>🔧 Bash: Create scratch dir, check env, grep usage · 20:24</summary>

**Аргументы**

```bash
mkdir -p reviews/scratch/stage2 && ls reviews reviews/scratch; python --version; python -c "import pandas, numpy; print(pandas.__version__, numpy.__version__)"; python -c "import hypothesis" 2>&1 | tail -1; grep -rn "seconds_since_start" --include=*.py . | grep -v archive
```

**Результат**

```
reviews:
prompts
scratch

reviews/scratch:
stage0-1b
stage2
stage3
stage4-6
stage5-leakage
stage7
stage8
Python 3.12.9
3.0.6 2.5.3
ModuleNotFoundError: No module named 'hypothesis'
./src/alerts/history.py:71:    def seconds_since_start(self, T) -> np.ndarray:
```

</details>

<details><summary>🔧 Write: reviews/scratch/stage2/s01_build_compare.py · 20:25</summary>

**Аргументы**

```
# file: reviews/scratch/stage2/s01_build_compare.py
"""Stage-2 review: rebuild tables in memory, cache them in scratch, compare with data/*.csv on disk.

Run from the repo root: PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage2/s01_build_compare.py
Nothing in data/ or reports/ is written.
"""
import pickle
import time
from pathlib import Path

import pandas as pd

from alerts import store
from alerts.config import load_config
from alerts.pipeline import build_all

OUT = Path('reviews/scratch/stage2/art.pkl')

cfg = load_config()
t0 = time.time()
art = build_all(cfg)
print(f'build_all: {time.time() - t0:.1f} s')
with open(OUT, 'wb') as f:
    pickle.dump(art, f)

iv_disk = store.load_intervals(cfg)
seen_disk = store.load_seen(cfg)

for name, mem, disk in [('intervals', art.intervals, iv_disk), ('seen', art.seen, seen_disk)]:
    print(f'\n== {name}: memory {mem.shape}, disk {disk.shape}')
    print('memory dtypes:', dict(mem.dtypes.astype(str)))
    print('disk dtypes:  ', dict(disk.dtypes.astype(str)))
    m = mem.reset_index(drop=True).copy()
    d = disk.reset_index(drop=True).copy()
    for c in m.columns:
        if str(m[c].dtype).startswith('datetime64'):
            m[c] = m[c].dt.as_unit('s')
            d[c] = d[c].dt.as_unit('s')
    try:
        pd.testing.assert_frame_equal(m, d, check_dtype=False, check_exact=True)
        print('EQUAL (values, check_exact=True, dtype unit normalised to s)')
    except AssertionError as e:
        print('DIFFERENT:', str(e)[:2000])
    # sub-second parts in memory?
    for c in m.columns:
        if str(mem[c].dtype).startswith('datetime64'):
            frac = (mem[c] - mem[c].dt.floor('s')).dt.total_seconds()
            print(f'  {c}: unit={mem[c].dt.unit}, tz={mem[c].dt.tz}, sub-second values={int((frac != 0).sum())}')

grid_disk = store.load_grid(cfg)
g = art.grid.reset_index(drop=True)
print('\n== grid: memory', g.shape, 'disk', grid_disk.shape)
try:
    pd.testing.assert_frame_equal(g, grid_disk
… [обрезано: показано 2000 из 2471 символов]
```

**Результат**

```
File created successfully at: d:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage2\s01_build_compare.py (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Bash: Rebuild tables in memory and compare with disk · 20:25</summary>

**Аргументы**

```bash
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage2/s01_build_compare.py 2>&1 | grep -v "^INFO" | tail -40
```

**Результат**

```
Channel outage (D15): 2026-08-29 05:55:28+00:00 -> 2026-09-02 13:48:04+00:00 (4 days 07:52:36)
build_all: 13.1 s

== intervals: memory (73737, 6), disk (73737, 6)
memory dtypes: {'unit_id': 'str', 'start_utc': 'datetime64[s, UTC]', 'end_utc': 'datetime64[s, UTC]', 'uncertain': 'bool', 'episode': 'int64', 'n_records': 'int64'}
disk dtypes:   {'unit_id': 'str', 'start_utc': 'datetime64[s, UTC]', 'end_utc': 'datetime64[s, UTC]', 'uncertain': 'bool', 'episode': 'int64', 'n_records': 'int64'}
EQUAL (values, check_exact=True, dtype unit normalised to s)
  start_utc: unit=s, tz=UTC, sub-second values=0
  end_utc: unit=s, tz=UTC, sub-second values=0

== seen: memory (73688, 3), disk (73688, 3)
memory dtypes: {'unit_id': 'str', 'start': 'datetime64[s, UTC]', 'end': 'datetime64[s, UTC]'}
disk dtypes:   {'unit_id': 'str', 'start': 'datetime64[s, UTC]', 'end': 'datetime64[s, UTC]'}
EQUAL (values, check_exact=True, dtype unit normalised to s)
  start: unit=s, tz=UTC, sub-second values=0
  end: unit=s, tz=UTC, sub-second values=0

== grid: memory (616909, 7) disk (616909, 7)
grid EQUAL
masks EQUAL
```

</details>

<details><summary>🔧 Bash: Inspect loader and raw timestamp formats · 20:25</summary>

**Аргументы**

```bash
cat -n src/alerts/ingest/vadimkin.py | head -60; head -3 dataset_repo/datasets/official_data_en.csv; awk -F, 'NR>1{print length($5), length($6)}' dataset_repo/datasets/official_data_en.csv | sort | uniq -c | head
```

**Результат**

```
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
    35	    dedup_rows = len(df)
    36	
    37	    df['duration'] = (df['finished_at'] - df['started_at']).dt.total_seconds()
    38	    df = df[df['duration'] > 0].reset_index(drop=True)
    39	    cleaned_rows = len(df)
    40	
    41	    logger.info(f'Loaded {path}')
    42	    logger.info(f'Rows initially: {initial_rows:,}')
    43	    logger.info(f'Rows after drop_duplicates: {dedup_rows:,}')
    44	    logger.info(f'Rows after dropping duration <= 0: {cleaned_rows:,}')
    45	
    46	    df.attrs['row_counts'] = {'raw': initial_rows, 'dedup': dedup_rows, 'cleaned': cleaned_rows}
    47	    return df
oblast,raion,hromada,level,started_at,finished_at,source
Vinnytska oblast,,,oblast,2022-03-15 16:10:34+00:00,2022-03-15 16:50:07+00:00,official
Zhytomyrska oblast,,,oblast,2022-03-15 16:11:25+00:00,2022-03-15 16:54:23+00:00,official
 299275 25 25
```

</details>

<details><summary>🔧 Write: reviews/scratch/stage2/s02_spans_property.py · 20:25</summary>

**Аргументы**

```
# file: reviews/scratch/stage2/s02_spans_property.py
"""Property test of spans.merge_labels / spans.union against a naive sweep (stage-2 review, item 1).

Edge cases are forced by drawing integer times from a tiny range: touching intervals, nested ones,
equal starts, equal (start, end) duplicates, unsorted input, repeated index, several keys, gap > 0.
"""
import numpy as np
import pandas as pd

from alerts.spans import covers, count_in, merge_labels, reaches, union

T0 = pd.Timestamp('2026-01-01', tz='UTC')


def naive_union(rows, gap):
    """rows: list of (key, s, e) ints. Classic sort-and-extend sweep."""
    out = []
    for k in sorted({r[0] for r in rows}):
        iv = sorted((s, e) for kk, s, e in rows if kk == k)
        cs, ce = iv[0]
        for s, e in iv[1:]:
            if s - ce <= gap:
                ce = max(ce, e)
            else:
                out.append((k, cs, ce))
                cs, ce = s, e
        out.append((k, cs, ce))
    return sorted(out)


def naive_partition(rows, gap):
    """Group of every row (by position) of a frame sorted by (key, start, end)."""
    groups, cur_key, ce, gid = [], None, None, -1
    for k, s, e in rows:
        if k != cur_key or s - ce > gap:
            gid += 1
            cur_key, ce = k, e
        else:
            ce = max(ce, e)
        groups.append(gid)
    return groups


def frame(rows, rng, shuffle=True, dup_index=True):
    df = pd.DataFrame(rows, columns=['key', 's', 'e'])
    df['start'] = T0 + pd.to_timedelta(df['s'], unit='s')
    df['end'] = T0 + pd.to_timedelta(df['e'], unit='s')
    if shuffle:
        df = df.sample(frac=1, random_state=int(rng.integers(1 << 30)))
    if dup_index:
        df.index = rng.integers(0, 3, len(df))       # repeated index values
    return df


rng = np.random.default_rng(42)
n_cases, fails_union, fails_labels = 3000, 0, 0
for case in range(n_cases):
    n = int(rng.integers(1, 25))
    keys = rng.choice(['a', 'b', 'c'], n)
    s = rng.integers(0, 30, n)
    
… [обрезано: показано 2000 из 5055 символов]
```

**Результат**

```
File created successfully at: d:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage2\s02_spans_property.py (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Bash: Run property test of span operations · 20:25</summary>

**Аргументы**

```bash
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage2/s02_spans_property.py 2>&1 | tail -20
```

**Результат**

```
union vs naive: 3000/3000 equal; merge_labels on sorted input: 3000/3000 equal
unsorted keys, labels = [0, 1, 1] (row 3 of key a is put into the group of key b)
unsorted starts, labels = [0, 0, 0]
covers [s,e): {9: False, 10: True, 14: True, 15: False, 19: False, 20: True, 25: False}
reaches (lo,hi) vs [s,e): [(5, 10, False), (5, 11, True), (15, 20, False), (14, 15, True), (25, 30, False)]
count_in (lo,hi]: [1, 1, 1]
reaches/covers vs brute force: mismatches 0 of 2000
```

</details>

<details><summary>🔧 Bash: Find callers of merge_labels and union · 20:27</summary>

**Аргументы**

```bash
grep -rn "merge_labels\|union(" --include=*.py src scripts | grep -v "def "
```

**Результат**

```
src/alerts/api_check.py:113:    return union(iv.rename(columns={'start_utc': 'start', 'end_utc': 'end'})[['oblast', 'start', 'end']], 'oblast')
src/alerts/api_check.py:122:    v = union(vol[['oblast', 'started_at', 'finished_at']].rename(columns={'started_at': 'start', 'finished_at': 'end'}),
src/alerts/api_check.py:181:    iv = union(iv[iv['oblast'].isin(oblasts)], 'oblast')
src/alerts/grid.py:64:    by_reason = {r: union(g, 'unit_id') for r, g in masks.groupby('reason')}
src/alerts/grid.py:65:    unlabelled = union(masks[masks['reason'].isin(_UNLABELLED)], 'unit_id')
src/alerts/grid.py:66:    known = union(masks[masks['reason'].isin(_KNOWN_START)], 'unit_id')
src/alerts/history.py:33:        seen = union(seen, 'unit_id')
src/alerts/history.py:45:        out = union(out.assign(k=0), 'k') if len(out) else out
src/alerts/intervals.py:23:from alerts.spans import merge_labels, overlaps, union
src/alerts/intervals.py:42:    seg_id = merge_labels(rec, 'unit_id', 'started_at', 'finished_at')
src/alerts/intervals.py:50:    seg['episode'] = merge_labels(seg, 'unit_id', 'start_utc', 'end_utc', gap=pause)
src/alerts/intervals.py:69:    return union(pd.DataFrame({'unit_id': rec['unit_id'], 'start': rec['started_at'], 'end': end}),
src/alerts/intervals.py:82:    relevant = union(masks[masks['reason'].isin(UNCERTAIN_REASONS)], 'unit_id')
src/alerts/mask.py:13:reason but may overlap across reasons. Use spans.union() for the total masked time.
src/alerts/mask.py:80:    parts = [union(g, 'unit_id').assign(reason=reason)
src/alerts/mask.py:112:        total = union(sel, 'unit_id')
src/alerts/spans.py:27:    labels = merge_labels(df, key, start, end, gap)
scripts/run_all.py:55:                outage = union(art.masks[art.masks['reason'] == 'outage'].assign(k=0), 'k')
```

</details>

<details><summary>🔧 Bash: Read processor dataclasses, legacy states, git history · 20:28</summary>

**Аргументы**

```bash
cat -n dataset_repo/processors/tg_dataclasses.py; head -60 dataset_repo/processors/legacy_states.py; git -C dataset_repo log --oneline -8 -- processors/official_channel_processor.py 2>&1 | head; git -C dataset_repo log --oneline -1 2>&1
```

**Результат**

```
1	from dataclasses import dataclass, asdict
     2	from datetime import datetime
     3	from typing import Literal, Optional
     4	
     5	from translitua import translit
     6	
     7	PLACE_LEVEL = Literal["oblast", "raion", "hromada"]
     8	
     9	
    10	@dataclass
    11	class OfficialAirRaidAlertChannelAlert:
    12	    """Class for keeping track of an item in inventory."""
    13	
    14	    oblast: str
    15	    raion: str
    16	    hromada: str
    17	    level: PLACE_LEVEL
    18	    started_at: datetime
    19	    finished_at: Optional[datetime] = None
    20	    source: Literal["official", "volunteer"] = "official"
    21	
    22	    def dict(self, lang: str = "uk"):
    23	        if lang == "uk":
    24	            return {k: str(v) for k, v in asdict(self).items()}
    25	
    26	        transliterated = {}
    27	
    28	        keys_to_transliterate = ["oblast", "raion", "hromada"]
    29	        special_rules = {
    30	            # Official:
    31	            "м. Київ": "Kyiv City",
    32	            # Volunteer naming:
    33	            "Київ": "Kyiv City",
    34	        }
    35	
    36	        for k, v in asdict(self).items():
    37	            if k in keys_to_transliterate:
    38	                if v in special_rules:
    39	                    transliterated[k] = special_rules[v]
    40	                    continue
    41	
    42	                transliterated[k] = translit(v)
    43	                continue
    44	
    45	            transliterated[k] = str(v)
    46	
    47	        return transliterated
    48	
    49	
    50	@dataclass
    51	class ETryvogaChannelAlert:
    52	    region: str
    53	    started_at: datetime
    54	    finished_at: Optional[datetime] = None
    55	    naive: bool = False
    56	
    57	    def dict(self, lang: str = "uk") -> dict[str, str]:
    58	        if lang == "uk":
    59	            return {k: str(v) for k, v in asdict(self).items()}
    60	
    61	        result = {}
    62	
    63	        for k, v in asdict(self).items():
    64	            if k == "region":
    65	                if v == "Київ":
    66	                    result[k] = "Kyiv City"
    67	                else:
    68	                    result[k] = translit(v)
    69	            else:
    70	                result[k] = str(v)
    71	
    72	        return result
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
_COMMUNITY_RENAM
… [обрезано: показано 3000 из 4917 символов]
```

</details>

<details><summary>🔧 Bash: Processor git history with dates · 20:28</summary>

**Аргументы**

```bash
git -C dataset_repo log --format='%h %ad %s' --date=short -- processors/official_channel_processor.py processors/legacy_states.py | head -30; echo; git -C dataset_repo log --format='%h %ad %s' --date=short -G'hours=3|hours=1|timedelta' -- processors/official_channel_processor.py processors/ | head
```

**Результат**

```
50ce482 2026-01-25 Update script to not skip renamed hromadas
bd4ab5c 2026-01-11 Fix swapped oblast and raion in special rules for Гребінківська громада
708d8d4 2024-06-01 Add mode
d7f571f 2024-06-01 Add mode
1ad2eae 2024-06-01 Dump pickle state between parsing
1ef829e 2023-02-16 Refactor volunteer processor to make processors easier to extend

50ce482 2026-01-25 Update script to not skip renamed hromadas
1ef829e 2023-02-16 Refactor volunteer processor to make processors easier to extend
c9ae2a3 2023-02-16 Refactor official processor
7f8255a 2022-04-01 Add dataset with more accurate data
```

</details>

<details><summary>🔧 Bash: Show the rename-handling processor commit · 20:28</summary>

**Аргументы**

```bash
git -C dataset_repo show 50ce482 --stat | head; git -C dataset_repo show 50ce482 -- processors/official_channel_processor.py | head -120
```

**Результат**

```
commit 50ce4820acc9dff56a8aa79ca3cc278aeeeb52a1
Author: Vadym Klymenko <mail@vadimklimenko.com>
Date:   Sun Jan 25 17:04:31 2026 +0200

    Update script to not skip renamed hromadas

 datasets/README.md                            |     8 +-
 datasets/official_data_en.csv                 | 17457 ++++++++++++++++--------
 datasets/official_data_uk.csv                 | 17457 ++++++++++++++++--------
 example/run.py                                |     0
commit 50ce4820acc9dff56a8aa79ca3cc278aeeeb52a1
Author: Vadym Klymenko <mail@vadimklimenko.com>
Date:   Sun Jan 25 17:04:31 2026 +0200

    Update script to not skip renamed hromadas

diff --git a/processors/official_channel_processor.py b/processors/official_channel_processor.py
index 76de2f7..d5ce5f0 100644
--- a/processors/official_channel_processor.py
+++ b/processors/official_channel_processor.py
@@ -5,17 +5,17 @@ import logging
 import os.path
 import pathlib
 import pickle
-from typing import Optional
+from typing import Optional, List
 
 from telethon.tl.types import Message
 
+from .legacy_states import get_new_name
 from .tg_dataclasses import OfficialAirRaidAlertChannelAlert, PLACE_LEVEL
 
 logging.basicConfig()
 logger = logging.getLogger(__name__)
 logger.setLevel(logging.DEBUG)
 
-# UK means ukrainian language code, not United Kingdom :)
 data_uk_file_path = pathlib.Path(__file__).parent.resolve() / "../datasets/official_data_uk.csv"
 data_en_file_path = pathlib.Path(__file__).parent.resolve() / "../datasets/official_data_en.csv"
 
@@ -119,45 +119,46 @@ class OfficialAirAlertProcessor:
     def process_message(self, message: Message):
         logger.info("Processing message %s", message.message)
 
-        hashed_location, is_activated, is_deactivated = self.parse_message(message)
+        hashed_locations, is_activated, is_deactivated = self.parse_message(message)
 
         if not is_activated and not is_deactivated:
             logger.error("Can't parse %s, skipping...", message.message)
             return
 
-        oblast_name, raion_name, hromada_name, level = self.hash_states_by_name[hashed_location]
-
-        if is_activated:
-            if current_alert := self.active_alerts_by_location.get(hashed_location):
-                # Looks like it was started some time ago, but there are no message when alert was completed
-                more_than_3_hours_difference = (message.date - current_alert.started_at) > datetime.timedelta(hours=3)
-                if more_than_3_hours_difference:
-                    # Looks like it was not marked as completed, but another alert was started
-                    # otherwise just rewrite this alert
-                    current_alert.finished_at = current_alert.started_at + datetime.timedelta(hours=1)
-                    self.completed_alerts.append(current_alert)
-
-            alert = OfficialAirRaidAlertChannelAlert(
-                started_at=message.date,
-                oblast=oblast_name,
-                raion=raion_name,
-   
… [обрезано: показано 3000 из 6206 символов]
```

</details>

<details><summary>🔧 Bash: Show rest of processor diff and README diff · 20:28</summary>

**Аргументы**

```bash
git -C dataset_repo show 50ce482 -- processors/official_channel_processor.py | sed -n 120,200p; git -C dataset_repo show 50ce482 -- datasets/README.md
```

**Результат**

```
last_line = "#м_херсон_та_херсонська_територіальна_громада"
 
-        if not self.hash_states_by_name.get(last_line):
-            # TODO Raise an exception someday
-            logger.error("Can't process %s", last_line)
-            return None, None, None
+        # Split last line by spaces and take only first part
+        # #Херсонський_район #Бериславський_район #Скадовський_район #Каховський_район #Генічеський_район
+        hashtag_locations = last_line.split(" ")
+        for hashtag_location in hashtag_locations:
+            if not self.hash_states_by_name.get(hashtag_location):
+                # TODO Raise an exception someday
+                logger.error("Can't process %s", hashtag_location)
+                return None, None, None
 
         is_activated = ("Повітряна" in first_line) or ("🔴" in first_line)
         is_deactivated = ("Відбій" in first_line) or ("🟢" in first_line)
@@ -198,7 +209,7 @@ class OfficialAirAlertProcessor:
             )
             return None, None, None
 
-        return last_line, is_activated, is_deactivated
+        return hashtag_locations, is_activated, is_deactivated
 
     @staticmethod
     def location_to_hashtag(location: str) -> str:
@@ -224,16 +235,32 @@ class OfficialAirAlertProcessor:
 
             for raion in state["districts"]:
                 raion_name = raion["districtName"]
+
+                maybe_renamed_raion = get_new_name(state_name, raion_name)
+                maybe_renamed_raion_name = maybe_renamed_raion[0] if maybe_renamed_raion else None
+
                 hashed_raion_name = self.location_to_hashtag(raion_name)
                 self.hash_states_by_name[hashed_raion_name] = (
                     state_name,
-                    raion_name,
+                    maybe_renamed_raion_name or raion_name,
                     "",
                     "raion",
                 )
 
+                # Special fix for renamed raions
+                if maybe_renamed_raion_name:
+                    hashed_renamed_raion_name = self.location_to_hashtag(maybe_renamed_raion_name)
+                    self.hash_states_by_name[hashed_renamed_raion_name] = (
+                        state_name,
+                        maybe_renamed_raion_name,
+                        "",
+                        "raion",
+                    )
+
                 for hromada in raion["communities"]:
                     hromada_name = hromada["communityName"]
+                    maybe_renamed_hromada = get_new_name(state_name, raion_name, hromada_name)
+                    maybe_renamed_hromada_name = maybe_renamed_hromada[1] if maybe_renamed_hromada else None
                     hashed_hromada_name = self.location_to_hashtag(hromada_name)
 
                     # There are hromadas with duplicated names, so adding only hromadas where sirens were used at least once.
@@ -302,6 +329,16 @@ class OfficialAirAlertProcessor:
                         self.hash_states_by_name[hashed_hromada_name] = (
   
… [обрезано: показано 3000 из 5227 символов]
```

</details>

<details><summary>🔧 Bash: Analyze data changes in the rename commit · 20:28</summary>

**Аргументы**

```bash
git -C dataset_repo show --numstat --format='%h %ad' 50ce482 | head; git -C dataset_repo show 50ce482 -- datasets/official_data_en.csv > reviews/scratch/stage2/diff_50ce482.txt; grep -c '^+[^+]' reviews/scratch/stage2/diff_50ce482.txt; grep -c '^-[^-]' reviews/scratch/stage2/diff_50ce482.txt; grep '^+[^+]' reviews/scratch/stage2/diff_50ce482.txt | cut -d, -f4,5 | cut -c1-12 | sort | uniq -c | sort -k2 | head -40
```

**Результат**

```
50ce482 Sun Jan 25 17:04:31 2026 +0200

3	5	datasets/README.md
12141	5316	datasets/official_data_en.csv
12141	5316	datasets/official_data_uk.csv
0	0	example/run.py
146	0	example/ukr_admin2.geojson
62	0	processors/legacy_states.py
73	36	processors/official_channel_processor.py
-	-	processors/pkl/official_active_alerts.pkl
12141
5316
    615 hromada,2024
    930 hromada,2025
    100 hromada,2026
    619 oblast,2024-
    936 oblast,2025-
      7 oblast,2026-
      1 raion,2022-0
    485 raion,2025-0
   4789 raion,2025-1
   3659 raion,2026-0
```

</details>

<details><summary>🔧 Bash: Removed lines by level and month, hunk headers · 20:28</summary>

**Аргументы**

```bash
F=reviews/scratch/stage2/diff_50ce482.txt; grep '^-[^-]' $F | cut -d, -f4,5 | cut -c1-12 | sort | uniq -c | sort -k2 | head -30; echo; grep -n '^@@' $F | head -20
```

**Результат**

```
615 hromada,2024
    892 hromada,2025
     60 hromada,2026
    619 oblast,2024-
    936 oblast,2025-
      7 oblast,2026-
      1 raion,2022-0
    485 raion,2025-0
   1287 raion,2025-1
    414 raion,2026-0

11:@@ -458,7 +458,7 @@ Kyivska oblast,Bilotserkivskyi raion,m. Bila Tserkva ta Bilotserkivska terytoria
20:@@ -44602,6 +44602,7 @@ Odeska oblast,,,oblast,2024-05-12 07:43:42+00:00,2024-05-12 08:11:53+00:00,offic
28:@@ -45322,6 +45323,7 @@ Kirovohradska oblast,,,oblast,2024-05-20 08:27:07+00:00,2024-05-20 08:31:57+00:0
36:@@ -46382,6 +46384,7 @@ Ivano-Frankivska oblast,,,oblast,2024-05-31 23:55:44+00:00,2024-06-01 02:37:41+0
44:@@ -46466,25 +46469,24 @@ Khersonska oblast,,,oblast,2024-06-01 14:54:41+00:00,2024-06-01 15:41:28+00:00,o
79:@@ -46529,12 +46531,16 @@ Donetska oblast,Pokrovskyi raion,Pokrovska terytorialna hromada,hromada,2024-06-
96:@@ -46543,10 +46549,6 @@ Poltavska oblast,,,oblast,2024-06-02 21:26:48+00:00,2024-06-02 21:53:42+00:00,of
107:@@ -46588,8 +46590,11 @@ Dnipropetrovska oblast,Nikopolskyi raion,m. Marhanets ta Marhanetska terytorialn
119:@@ -46600,9 +46605,6 @@ Chernihivska oblast,,,oblast,2024-06-03 18:58:22+00:00,2024-06-03 21:26:28+00:00
129:@@ -46652,8 +46654,14 @@ Dnipropetrovska oblast,Nikopolskyi raion,Myrivska terytorialna hromada,hromada,2
144:@@ -46686,12 +46694,6 @@ Poltavska oblast,,,oblast,2024-06-04 22:51:20+00:00,2024-06-04 23:25:14+00:00,of
157:@@ -46790,7 +46792,12 @@ Khersonska oblast,,,oblast,2024-06-05 13:56:55+00:00,2024-06-05 14:28:27+00:00,o
170:@@ -46817,11 +46824,6 @@ Sumska oblast,,,oblast,2024-06-05 22:59:28+00:00,2024-06-05 23:32:49+00:00,offic
182:@@ -46860,12 +46862,12 @@ Sumska oblast,,,oblast,2024-06-06 11:54:07+00:00,2024-06-06 12:36:48+00:00,offic
196:@@ -46938,10 +46940,15 @@ Kirovohradska oblast,,,oblast,2024-06-07 12:14:32+00:00,2024-06-07 12:26:14+00:0
212:@@ -46959,11 +46966,6 @@ Poltavska oblast,,,oblast,2024-06-07 21:09:16+00:00,2024-06-07 21:45:59+00:00,of
224:@@ -46994,14 +46996,14 @@ Poltavska oblast,,,oblast,2024-06-08 12:54:00+00:00,2024-06-08 13:05:13+00:00,of
242:@@ -47020,9 +47022,11 @@ Mykolaivska oblast,,,oblast,2024-06-09 09:39:17+00:00,2024-06-09 10:58:26+00:00,
254:@@ -47041,6 +47045,7 @@ Cherkaska oblast,,,oblast,2024-06-09 13:41:43+00:00,2024-06-09 13:54:26+00:00,of
262:@@ -47050,7 +47055,10 @@ Dnipropetrovska oblast,,,oblast,2024-06-09 15:07:23+00:00,2024-06-09 15:23:36+00
```

</details>

<details><summary>🔧 Write: reviews/scratch/stage2/s03_processor.py · 20:29</summary>

**Аргументы**

```
# file: reviews/scratch/stage2/s03_processor.py
"""Stage-2 review, item 5: the processor model (alerts.processor) against the data.

Uses the cached artifacts from s01 (reviews/scratch/stage2/art.pkl).
"""
import pickle

import numpy as np
import pandas as pd

from alerts.config import load_config, ts

cfg = load_config()
art = pickle.load(open('reviews/scratch/stage2/art.pkl', 'rb'))
sc_all, sc = art.scope_all, art.scope
H = pd.Timedelta(hours=1)
data_end = ts(cfg['data_end'])

print('scope (period) records:', len(sc), ' roles:', sc['role'].value_counts().to_dict())

# --- 1. records of exactly 3600 s and the next start of their location -------------------------
one = sc[sc['duration'] == 3600].copy()
gap = (one['next_start'] - one['started_at'])
one['cls'] = np.select([gap.isna(), gap <= 3 * H], ['no next start', 'next <= 3h'], 'next > 3h')
print('\n3600-s records in the period scope:', len(one), one['cls'].value_counts().to_dict())
print(one.groupby(['role', 'cls']).size().to_string())
print('next <= 3h (treated as open until the next start although the processor cannot have invented them):')
print(one[one['cls'] == 'next <= 3h'][['oblast', 'raion', 'started_at', 'next_start']].to_string())
print('no next start:')
print(one[one['cls'] == 'no next start'][['oblast', 'raion', 'role', 'started_at', 'finished_at']].to_string())

# --- 2. duration density around 3600 s: how many *real* 1-h alerts hide among the "invented" ones? ---
# Count posts, not records: clones of one post share (oblast, start, end).
posts = sc[sc['role'] == 'target'].drop_duplicates(['oblast', 'started_at', 'finished_at'])
d = posts['duration'].astype(int)
win = d[(d >= 3600 - 300) & (d <= 3600 + 300)]
cnt = win.value_counts().sort_index()
neigh = cnt.drop(3600, errors='ignore')
print(f'\nTarget posts (unique oblast,start,end): {len(posts):,}')
print(f'posts with duration in [3300, 3900] s except 3600: {len(win) - cnt.get(3600, 0)} over 600 s '
      f'-> {neigh.sum() / 600:.2f} per second; exa
… [обрезано: показано 2000 из 4508 символов]
```

**Результат**

```
File created successfully at: d:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage2\s03_processor.py (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Bash: Run processor-model checks on data · 20:29</summary>

**Аргументы**

```bash
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage2/s03_processor.py 2>&1 | tail -70
```

**Результат**

```
scope (period) records: 86455  roles: {'target': 80159, 'input': 6296}

3600-s records in the period scope: 82 {'next > 3h': 76, 'next <= 3h': 6}
role    cls       
target  next <= 3h     6
        next > 3h     76
next <= 3h (treated as open until the next start although the processor cannot have invented them):
                       oblast                 raion                started_at                next_start
20302           Sumska oblast      Okhtyrskyi raion 2026-01-27 09:44:35+00:00 2026-01-27 11:29:38+00:00
21101       Kharkivska oblast  Bohodukhivskyi raion 2026-01-31 23:46:52+00:00 2026-02-01 01:19:00+00:00
29331           Sumska oblast         Sumskyi raion 2026-03-04 16:29:41+00:00 2026-03-04 19:03:54+00:00
44683           Odeska oblast         Odeskyi raion 2026-04-28 18:23:58+00:00 2026-04-28 19:30:26+00:00
53065  Dnipropetrovska oblast     Samarivskyi raion 2026-05-27 09:24:20+00:00 2026-05-27 12:06:06+00:00
53066  Dnipropetrovska oblast     Dniprovskyi raion 2026-05-27 09:24:20+00:00 2026-05-27 12:06:11+00:00
no next start:
Empty DataFrame
Columns: [oblast, raion, role, started_at, finished_at]
Index: []

Target posts (unique oblast,start,end): 60,347
posts with duration in [3300, 3900] s except 3600: 3408 over 600 s -> 5.68 per second; exactly 3600 s: 60
  [3590,3610] excluding 3600: 131 posts over 20 s -> 6.55/s
  [3540,3660] excluding 3600: 705 posts over 120 s -> 5.88/s
records 3300..3900 s (not 3600): 4136, share with next start > 3 h after start: 0.501; no next start: 3

exact duration (s), posts with that duration, mean posts per second within +-10 s:
   (60, 1, np.float64(1.25))
   (300, 4, np.float64(3.25))
   (600, 4, np.float64(5.95))
   (900, 15, np.float64(13.05))
   (1200, 11, np.float64(12.65))
   (1800, 8, np.float64(11.35))
   (2700, 7, np.float64(8.05))
   (3600, 60, np.float64(6.55))
   (5400, 2, np.float64(3.8))
   (7200, 1, np.float64(2.1))
   (10800, 2, np.float64(1.65))
   (14400, 1, np.float64(0.95))
   (21600, 2, np.float64(0.25))
   (43200, 0, 0.0)
   (86400, 0, 0.0)
spikes (count > 5x neighbours, >= 4 posts): [(3600, 60, 6.55), (7437, 8, 1.55), (10235, 6, 1.05), (10837, 5, 0.85), (11430, 5, 0.8), (11487, 4, 0.65), (11662, 4, 0.7), (12220, 5, 0.6), (12417, 4, 0.75), (12545, 4, 0.7), (12583, 6, 0.85), (12749, 4, 0.7), (13070, 5, 0.6), (13132, 4, 0.55), (13810, 4, 0.55), (14077, 4, 0.65), (14165, 4, 0.7), (14464, 4, 0.5), (14577, 4, 0.55), (14700, 4, 0.2), (14717, 4, 0.75), (14791, 4, 0.75), (14903, 4, 0.3), (15193, 4, 0.75), (15463, 4, 0.6), (15514, 4, 0.55), (15577, 4, 0.6), (15734, 4, 0.3), (16021, 4, 0.2), (16966, 4, 0.35), (20161, 5, 0.65), (20282, 4, 0.3)]
Samarivskyi raion: all-time records 1458, first 2025-05-01 21:54:28+00:00, 3600-s 2, >24 h 0
Zviahelskyi raion: all-time records 266, first 2022-03-20 12:04:04+00:00, 3600-s 2, >24 h 0
Novomoskovskyi raion: all-time records 0, first NaT, 3600-s 0, >24 h 0
Novohrad-Volynskyi raion: all-time records 0, fi
… [обрезано: показано 3000 из 3133 символов]
```

</details>

<details><summary>🔧 Write: reviews/scratch/stage2/s04_episode_starts.py · 20:30</summary>

**Аргументы**

```
# file: reviews/scratch/stage2/s04_episode_starts.py
"""Stage-2 review, items 3-4: episode starts (read by AlertHistory.starts) vs the seen state.

For every episode start x of a unit: was the unit already "under alert" in `seen` at x, and why?
For every start of a seen interval: is there an episode start at the same moment, and why not?
The interesting class: an episode start x of one raion while ANOTHER raion of the same unit holds a
record of exactly 3600 s that the processor had not yet closed (its invented end is written only at
the next start s2 > x). At x nobody knew that record had ended, so x being a new episode is future
information.
"""
import pickle

import numpy as np
import pandas as pd

from alerts.config import load_config
from alerts.scope import attach_units

cfg = load_config()
art = pickle.load(open('reviews/scratch/stage2/art.pkl', 'rb'))
iv, seen, units = art.intervals, art.seen, art.units
P = pd.Timedelta(minutes=cfg['thresholds']['pause_merge_min'])
CAP = pd.Timedelta(hours=cfg['history']['max_open_hours'])

rec = attach_units(art.scope, units)
rec['seen_end'] = rec['open_until'].where(rec['open_until'] <= rec['started_at'] + CAP, rec['started_at'] + CAP)
multi = units.groupby('unit_id')['raion'].nunique()
multi = set(multi[multi > 1].index)
print('multi-location units:', sorted(multi))

ep_start = iv.groupby('episode').agg(unit_id=('unit_id', 'first'), x=('start_utc', 'min')).reset_index(drop=True)


def seen_active_at(u, x):
    s = seen[(seen['unit_id'] == u) & (seen['start'] < x) & (seen['end'] > x)]
    return len(s) > 0


rows = []
for r in ep_start.itertuples():
    if not seen_active_at(r.unit_id, r.x):
        continue
    ru = rec[rec['unit_id'] == r.unit_id]
    starter = ru[ru['started_at'] == r.x]
    hold = ru[(ru['started_at'] < r.x) & (ru['seen_end'] > r.x)]
    held_beyond_record = hold[hold['finished_at'] < r.x]          # kept open only by open_until (3600 s)
    same_loc = held_beyond_record.merge(starter[['oblast', 'raion
… [обрезано: показано 2000 из 4368 символов]
```

**Результат**

```
File created successfully at: d:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage2\s04_episode_starts.py (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Bash: Vectorize and run episode-start analysis · 20:30</summary>

**Аргументы**

```bash
python - <<'EOF'
import re
p='reviews/scratch/stage2/s04_episode_starts.py'
t=open(p,encoding='utf-8').read()
old='''def seen_active_at(u, x):
    s = seen[(seen['unit_id'] == u) & (seen['start'] < x) & (seen['end'] > x)]
    return len(s) > 0


rows = []
for r in ep_start.itertuples():
    if not seen_active_at(r.unit_id, r.x):
        continue
'''
new='''from alerts.timeutil import to_sec
flag = np.zeros(len(ep_start), dtype=bool)
for u, idx in ep_start.groupby('unit_id').indices.items():
    g = seen[seen['unit_id'] == u]
    s, e = to_sec(g['start']), to_sec(g['end'])
    x = to_sec(ep_start['x'].iloc[idx])
    k = np.searchsorted(s, x, side='left') - 1          # last seen interval starting strictly before x
    flag[idx] = (k >= 0) & (e[np.maximum(k, 0)] > x)

rows = []
for r in ep_start[flag].itertuples():
'''
assert old in t
open(p,'w',encoding='utf-8').write(t.replace(old,new))
EOF
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage2/s04_episode_starts.py 2>&1 | tail -60
```

**Результат**

```
multi-location units: ['I00', 'U001', 'U003', 'U025']

Episode starts: 66,644; of them while `seen` is already active: 48
cls
other    48

OTHER-location cases (x = episode start, s2 = when the open 3600-s record was written):
Empty DataFrame
Columns: [unit_id, x, s2, rule_b, starter, holder]
Index: []

seen intervals: 73,688; starting without an episode start: 7092
cls
bridged pause (<= 15 min after the previous end)    7059
inside a >24 h record of the SAME location            33
cls                                               multi
bridged pause (<= 15 min after the previous end)  False    6494
                                                  True      565
inside a >24 h record of the SAME location        False       8
                                                  True       25
```

</details>

<details><summary>🔧 Bash: Classify the 48 known discrepancy starts · 20:33</summary>

**Аргументы**

```bash
cat > reviews/scratch/stage2/s05_inspect48.py <<'EOF'
"""Inspect the 48 episode starts that happen while `seen` is already active (known discrepancy)."""
import pickle
import pandas as pd
from alerts.config import load_config
from alerts.scope import attach_units

cfg = load_config()
art = pickle.load(open('reviews/scratch/stage2/art.pkl', 'rb'))
CAP = pd.Timedelta(hours=24)
rec = attach_units(art.scope, art.units)
rec['seen_end'] = rec['open_until'].where(rec['open_until'] <= rec['started_at'] + CAP, rec['started_at'] + CAP)
A = pd.read_csv('reviews/scratch/stage2/s04_starts_while_seen_active.csv', parse_dates=['x'])
cls = []
for r in A.itertuples():
    ru = rec[rec['unit_id'] == r.unit_id]
    x = pd.Timestamp(r.x)
    hold = ru[(ru['started_at'] < x) & (ru['seen_end'] >= x) & (ru['finished_at'] < x)]
    starter = ru[ru['started_at'] == x]
    same = hold.merge(starter[['oblast', 'raion']], on=['oblast', 'raion'])
    if len(same):
        c = 'same location: 3600-s record held open until this start'
    elif len(hold):
        c = 'OTHER location holds a 3600-s record open'
    else:
        c = '?'
    cls.append(c)
    if c != 'same location: 3600-s record held open until this start':
        print(r.unit_id, x, c); print(ru[(ru['started_at'] > x - pd.Timedelta(hours=26)) & (ru['started_at'] <= x + pd.Timedelta(hours=1))][['raion','started_at','finished_at','open_until','seen_end','is_fake_end']].to_string())
A['cls'] = cls
print(A.groupby('cls').size().to_string())
print(A.groupby(['cls', A['unit_id'].isin(['I00','U001','U003','U025']).rename('multi')]).size().to_string())
EOF
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage2/s05_inspect48.py 2>&1 | tail -40
```

**Результат**

```
cls
same location: 3600-s record held open until this start    48
cls                                                      multi
same location: 3600-s record held open until this start  False    47
                                                         True      1
```

</details>

<details><summary>🔧 Bash: Search other-location starts inside open invented records · 20:34</summary>

**Аргументы**

```bash
cat > reviews/scratch/stage2/s06_p1.py <<'EOF'
"""Episode starts x of a unit that lie inside (s + 1 h + 15 min, s2) of a rule-(b) record of ANOTHER
raion of the same unit: in the full data x is a new episode, but until s2 the record was still open."""
import pickle
import pandas as pd
from alerts.config import load_config
from alerts.scope import attach_units

cfg = load_config()
art = pickle.load(open('reviews/scratch/stage2/art.pkl', 'rb'))
rec = attach_units(art.scope, art.units)
ep = art.intervals.groupby('episode').agg(unit_id=('unit_id', 'first'), x=('start_utc', 'min')).reset_index(drop=True)
P = pd.Timedelta(minutes=15)
out = []
for a in rec[rec['is_fake_end']].itertuples():
    e = ep[(ep['unit_id'] == a.unit_id) & (ep['x'] > a.finished_at + P) & (ep['x'] < a.next_start)]
    for x in e['x']:
        out.append((a.unit_id, a.raion, a.started_at, a.next_start, x))
print('rule-(b) records in period scope:', int(rec['is_fake_end'].sum()),
      'of them in multi-location units:', int(rec.loc[rec['is_fake_end'], 'unit_id'].isin(['I00','U001','U003','U025']).sum()))
print('episode starts inside (s+1h+15min, s2) of a rule-(b) record of the same unit:', len(out))
for o in out: print(o)
# same for ALL 3600-s records (open_until extension), real or not
out2 = []
for a in rec[(rec['duration'] == 3600)].itertuples():
    e = ep[(ep['unit_id'] == a.unit_id) & (ep['x'] > a.finished_at + P) & (ep['x'] < a.next_start)]
    out2 += [(a.unit_id, a.raion, a.started_at, a.next_start, x) for x in e['x']]
print('same for every 3600-s record:', len(out2))
EOF
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage2/s06_p1.py 2>&1 | tail -20
```

**Результат**

```
rule-(b) records in period scope: 76 of them in multi-location units: 6
episode starts inside (s+1h+15min, s2) of a rule-(b) record of the same unit: 0
same for every 3600-s record: 0
```

</details>

<details><summary>🔧 Bash: Analyze multi-raion units and cap variants · 20:34</summary>

**Аргументы**

```bash
cat > reviews/scratch/stage2/s07_multi_units.py <<'EOF'
"""Item 3: seen for units made of several raions; per-record cap vs other variants (D19)."""
import pickle
import numpy as np
import pandas as pd
from alerts.config import load_config
from alerts.scope import attach_units
from alerts.spans import union
from alerts.timeutil import to_sec

cfg = load_config()
art = pickle.load(open('reviews/scratch/stage2/art.pkl', 'rb'))
rec = attach_units(art.scope, art.units)
CAP = pd.Timedelta(hours=24)
MULTI = ['I00', 'U001', 'U003', 'U025']
iv = art.intervals

# 1. other-location records starting inside a >24 h record (after its cap) of the same unit
n = 0
for a in rec[(rec['finished_at'] - rec['started_at'] > CAP) & rec['unit_id'].isin(MULTI)].itertuples():
    o = rec[(rec['unit_id'] == a.unit_id) & ((rec['oblast'] != a.oblast) | (rec['raion'] != a.raion))
            & (rec['started_at'] > a.started_at + CAP) & (rec['started_at'] < a.finished_at)]
    n += len(o)
print('long records (>24 h) in multi-location units:',
      int(((rec['finished_at'] - rec['started_at'] > CAP) & rec['unit_id'].isin(MULTI)).sum()),
      '; other-raion records starting after the cap inside them:', n)

# 2. segments > 24 h whose records are all <= 24 h (legit multi-day alerts made of chained records)
r2 = rec.assign(long=(rec['finished_at'] - rec['started_at']) > CAP)
seg_long = iv[(iv['end_utc'] - iv['start_utc']) > CAP]
print('segments > 24 h by unit:', seg_long['unit_id'].value_counts().to_dict())
chained = 0
for s in seg_long.itertuples():
    rr = r2[(r2['unit_id'] == s.unit_id) & (r2['started_at'] >= s.start_utc) & (r2['finished_at'] <= s.end_utc)]
    if not rr['long'].any():
        chained += 1
        print('  chained, no record > 24 h:', s.unit_id, s.start_utc, s.end_utc, 'records', len(rr))
print('segments > 24 h made only of records <= 24 h:', chained)

# 3. per-record cap (code) vs cap applied after the union (alternative): unit-hours that differ
def seen_variant(per_record):
  
… [обрезано: показано 2000 из 2942 символов]
```

**Результат**

```
long records (>24 h) in multi-location units: 427 ; other-raion records starting after the cap inside them: 0
segments > 24 h by unit: {'I00': 45, 'U084': 20, 'U001': 13, 'U083': 6, 'U018': 3, 'U050': 3, 'U062': 3, 'U014': 2, 'U034': 2, 'U003': 1, 'U008': 1, 'U010': 1, 'U011': 1, 'U023': 1, 'U041': 1, 'U048': 1, 'U049': 1, 'U052': 1, 'U060': 1, 'U063': 1, 'U064': 1, 'U067': 1, 'U081': 1}
segments > 24 h made only of records <= 24 h: 0
seen hours, per-record cap minus union-then-cap (non-zero units): {'I00': 0.01, 'U000': 0.59, 'U003': 0.01, 'U005': 0.79, 'U012': 2.9, 'U015': 0.47, 'U016': 0.82, 'U020': 13.66, 'U025': 3.28, 'U026': 0.79, 'U035': 3.28, 'U036': 0.43, 'U040': 1.34, 'U045': 2.01, 'U051': 1.33, 'U052': 2.14, 'U055': 0.8, 'U057': 0.29, 'U061': 0.61, 'U068': 2.14, 'U069': 0.57, 'U071': 0.18, 'U074': 0.48, 'U077': 2.01, 'U082': 0.82, 'U088': 0.43, 'U094': 0.76, 'U095': 2.9, 'U096': 0.47, 'U097': 0.82, 'U102': 0.43}
```

</details>

<details><summary>🔧 Write: reviews/scratch/stage2/s08_asof_layer.py · 20:36</summary>

**Аргументы**

```
# file: reviews/scratch/stage2/s08_asof_layer.py
"""Item 2/6: the as-of contract checked at the AlertHistory layer, not only on grid features.

For a cut: AlertHistory from the full data vs AlertHistory from leakage.known_at(cut) (what the
dataset contained at the cut). Every method, every unit, every 5 minutes in (cut - 7 d, cut].
seconds_since_start is not used by any feature, so test_knowledge / knowledge_check never see it.

Usage: python s08_asof_layer.py [cut ...]   (default: config cuts + cuts after real 1-h alerts)
"""
import pickle
import sys
import time

import numpy as np
import pandas as pd

from alerts.config import load_config
from alerts.history import AlertHistory
from alerts.intervals import build_intervals, build_seen
from alerts.leakage import known_at
from alerts.mask import build_masks
from alerts.scope import select_scope

cfg = load_config()
art = pickle.load(open('reviews/scratch/stage2/art.pkl', 'rb'))
units = art.units
ids = units['unit_id'].drop_duplicates().tolist()
H, MIN = pd.Timedelta(hours=1), pd.Timedelta(minutes=1)


def history(df):
    scope_all = select_scope(df, cfg, period=False)
    scope = select_scope(df, cfg, period=True)
    masks, _, _ = build_masks(df, scope_all, units, cfg)
    return AlertHistory(build_seen(scope, units, cfg), build_intervals(scope, units, masks, cfg), ids, masks)


def answers(h, T):
    out = {'active': h.active(T), 'since_end': h.seconds_since_end(T), 'since_start': h.seconds_since_start(T),
           'outage_24h': h.outage_seconds(T, 24 * H), 'outage_7d': h.outage_seconds(T, 7 * 24 * H)}
    for w in [30 * MIN, 60 * MIN, 6 * H, 24 * H, 7 * 24 * H]:
        out[f'starts_{w}'] = h.starts(T, w)
    out['seconds_active_24h'] = h.seconds_active(T, 24 * H)
    return out


full = AlertHistory(art.seen, art.intervals, ids, art.masks)
cuts = [pd.Timestamp(c, tz='UTC') for c in sys.argv[1:]] or [
    pd.Timestamp(c) for c in cfg['leakage_check']['cuts']] + [
    pd.Timestamp('2026-01-27 11:00', tz='UTC'), 
… [обрезано: показано 2000 из 3315 символов]
```

**Результат**

```
File created successfully at: d:\Flash\golova\KSE_AI\AAFS\reviews\scratch\stage2\s08_asof_layer.py (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Bash: Run as-of layer check across cuts · 20:36</summary>

**Аргументы**

```bash
sed -i "s|pd.Timestamp('2026-04-28 19:00', tz='UTC'),   # Odeskyi: 18:23:58-19:23:58 ... wait: record ends 19:23:58|pd.Timestamp('2026-04-28 19:25', tz='UTC'),   # Odeskyi: 18:23:58-19:23:58, next 19:30:26 (not an hourly moment)|" reviews/scratch/stage2/s08_asof_layer.py && grep -n "Odeskyi" reviews/scratch/stage2/s08_asof_layer.py && PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage2/s08_asof_layer.py 2>&1 | grep -v "^INFO\|WARNING" | tail -30
```

**Результат**

```
50:    pd.Timestamp('2026-04-28 19:25', tz='UTC'),   # Odeskyi: 18:23:58-19:23:58, next 19:30:26 (not an hourly moment)
cut 2026-08-10 00:00:00+00:00: 2016 moments x 105 units, 3 s -> all methods equal
cut 2026-08-21 14:00:00+00:00: 2016 moments x 105 units, 3 s -> all methods equal
cut 2026-01-27 11:00:00+00:00: 2016 moments x 105 units, 2 s -> DIFFERENT
   active: 4 cells differ; first (t, unit, full, known): [('2026-01-27 10:45:00+00:00', 'U066', np.True_, np.False_), ('2026-01-27 10:50:00+00:00', 'U066', np.True_, np.False_), ('2026-01-27 10:55:00+00:00', 'U066', np.True_, np.False_)]
   since_end: 4 cells differ; first (t, unit, full, known): [('2026-01-27 10:45:00+00:00', 'U066', np.float64(16995.0), np.float64(25.0)), ('2026-01-27 10:50:00+00:00', 'U066', np.float64(17295.0), np.float64(325.0)), ('2026-01-27 10:55:00+00:00', 'U066', np.float64(17595.0), np.float64(625.0))]
   seconds_active_24h: 4 cells differ; first (t, unit, full, known): [('2026-01-27 10:45:00+00:00', 'U066', np.float64(33837.0), np.float64(33812.0)), ('2026-01-27 10:50:00+00:00', 'U066', np.float64(33837.0), np.float64(33512.0)), ('2026-01-27 10:55:00+00:00', 'U066', np.float64(33837.0), np.float64(33212.0))]
cut 2026-04-28 19:25:00+00:00: 2016 moments x 105 units, 2 s -> DIFFERENT
   active: 1 cells differ; first (t, unit, full, known): [('2026-04-28 19:25:00+00:00', 'U065', np.True_, np.False_)]
   since_end: 1 cells differ; first (t, unit, full, known): [('2026-04-28 19:25:00+00:00', 'U065', np.float64(22328.0), np.float64(62.0))]
   seconds_active_24h: 1 cells differ; first (t, unit, full, known): [('2026-04-28 19:25:00+00:00', 'U065', np.float64(12141.0), np.float64(12079.0))]
cut 2026-05-27 11:00:00+00:00: 2016 moments x 105 units, 3 s -> DIFFERENT
   active: 16 cells differ; first (t, unit, full, known): [('2026-05-27 10:25:00+00:00', 'U019', np.True_, np.False_), ('2026-05-27 10:25:00+00:00', 'U077', np.True_, np.False_), ('2026-05-27 10:30:00+00:00', 'U019', np.True_, np.False_)]
   since_end: 16 cells differ; first (t, unit, full, known): [('2026-05-27 10:25:00+00:00', 'U019', np.float64(23553.0), np.float64(40.0)), ('2026-05-27 10:25:00+00:00', 'U077', np.float64(23553.0), np.float64(40.0)), ('2026-05-27 10:30:00+00:00', 'U019', np.float64(23853.0), np.float64(340.0))]
   seconds_active_24h: 16 cells differ; first (t, unit, full, known): [('2026-05-27 10:25:00+00:00', 'U019', np.float64(17557.0), np.float64(17517.0)), ('2026-05-27 10:25:00+00:00', 'U077', np.float64(21618.0), np.float64(21578.0)), ('2026-05-27 10:30:00+00:00', 'U019', np.float64(17857.0), np.float64(17517.0))]
cut 2026-03-04 18:00:00+00:00: 2016 moments x 105 units, 2 s -> DIFFERENT
   active: 7 cells differ; first (t, unit, full, known): [('2026-03-04 17:30:00+00:00', 'U083', np.True_, np.False_), ('2026-03-04 17:35:00+00:00', 'U083', np.True_, np.False_), ('2026-03-04 17:40:00+00:00', 'U083', np.True_, np.False_)]
   since_end: 7 cells differ; first (t, unit, full, known): [('2026-03-04 17
… [обрезано: показано 3000 из 3530 символов]
```

</details>

*[ошибка API · 20:36: You&#x27;ve hit your weekly limit · resets 2am (Europe/Kyiv)]*

<details><summary>🔧 Bash: Run the D21 knowledge check at chosen cuts · 08:42</summary>

**Аргументы**

```bash
cd "D:/Flash/golova/KSE_AI/AAFS" && ls reviews/scratch/stage2/ && ls reviews/ && cat > reviews/scratch/stage2/s09_knowledge_cut.py <<'EOF'
"""D21 knowledge_check (the real one) at hourly cuts right after a real 1-h alert (next start <= 3 h)."""
import pickle
import sys
import pandas as pd
from alerts.config import load_config
from alerts.leakage import knowledge_check

cfg = load_config()
art = pickle.load(open('reviews/scratch/stage2/art.pkl', 'rb'))
for c in sys.argv[1:]:
    cut = pd.Timestamp(c, tz='UTC')
    try:
        print(cut, 'PASSED', knowledge_check(art.df, cfg, cut, units=art.units, neighbors=art.neighbors))
    except AssertionError as e:
        print(cut, 'FAILED:', str(e)[:900])
EOF
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage2/s09_knowledge_cut.py "2026-01-27 11:00" "2026-03-04 18:00" "2026-05-27 11:00" 2>&1 | grep -v "^INFO\|WARNING\|Channel outage" | tail -40
```

**Результат**

```
art.pkl
diff_50ce482.txt
s01_build_compare.py
s02_spans_property.py
s03_processor.py
s04_episode_starts.py
s04_seen_starts_without_episode.csv
s04_starts_while_seen_active.csv
s05_inspect48.py
s06_p1.py
s07_multi_units.py
s08_asof_layer.py
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
2026-01-27 11:00:00+00:00 FAILED: features known at 2026-01-27 11:00:00+00:00.iloc[:, 5] (column name="oblast_active_share") are different

features known at 2026-01-27 11:00:00+00:00.iloc[:, 5] (column name="oblast_active_share") values are different (0.02054 %)
[index]: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, ...]
[left]:  [0.0, 0.0, 0.0, 0.0, 0.0, 0.33333334, 0.0, 0.33333334, 0.33333334, 0.33333334, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.33333334, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.33333334, 0.0, 0.0, nan, 0.0, 0.0, 0.0, 0.0, 0.33333334, 0
2026-03-04 18:00:00+00:00 FAILED: features known at 2026-03-04 18:00:00+00:00.iloc[:, 5] (column name="oblast_active_share") are different

features known at 2026-03-04 18:00:00+00:00.iloc[:, 5] (column name="oblast_active_share") values are different (0.02652 %)
[index]: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, ...]
[left]:  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.6666667, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.6666667, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.6666667, n
2026-05-27 11:00:00+00:00 FAILED: features known at 2026-05-27 11:00:00+00:00.iloc[:, 5] (column name="oblast_active_share") are different

features known at 2026-05-27 11:00:00+00:00.iloc[:, 5] (column name="oblast_active_share") values are different (0.0069 %)
[index]: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, ...]
[left]:  [0.6666667, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.16666667, 0.16666
… [обрезано: показано 3000 из 3161 символов]
```

</details>

<details><summary>🔧 Bash: Quantify since_end measured from 24h cap · 08:44</summary>

**Аргументы**

```bash
cd "D:/Flash/golova/KSE_AI/AAFS" && mkdir -p reviews/claude && cat > reviews/scratch/stage2/s10_cap_after_end.py <<'EOF'
"""Item 2/3: after a capped (>24 h) record has really ended (all-clear seen at e), `seen` still says
the alert ended at s + 24 h. Own-unit features of rows at t > e: since_end and active_share_24h are
measured from the cap, not from the observed all-clear. Compare with a variant whose state for
moments >= e uses the observed end (only ends <= t are used, so it stays causal for since_end)."""
import pickle
import numpy as np
import pandas as pd
from alerts.config import load_config
from alerts.history import AlertHistory
from alerts.scope import attach_units
from alerts.spans import union

cfg = load_config()
art = pickle.load(open('reviews/scratch/stage2/art.pkl', 'rb'))
ids = art.units['unit_id'].drop_duplicates().tolist()
rec = attach_units(art.scope, art.units)
alt_seen = union(pd.DataFrame({'unit_id': rec['unit_id'], 'start': rec['started_at'], 'end': rec['open_until']}), 'unit_id')
h0 = AlertHistory(art.seen, art.intervals, ids, art.masks)
h1 = AlertHistory(alt_seen, art.intervals, ids, art.masks)
g = art.grid
T = pd.DatetimeIndex(np.sort(g['t'].unique()))
ti = np.searchsorted(T, g['t']); uj = g['unit_id'].map({u: j for j, u in enumerate(ids)}).to_numpy()
se0, se1 = h0.seconds_since_end(T)[ti, uj], h1.seconds_since_end(T)[ti, uj]
# the variant is causal only where its last end <= t is a real all-clear; restrict to rows where the
# capped version's last end is a cap end, i.e. the two last ends differ and the variant's end is later
diff = ~np.isclose(np.nan_to_num(se0, nan=-1), np.nan_to_num(se1, nan=-1))
later = diff & (np.nan_to_num(se1, nan=np.inf) < np.nan_to_num(se0, nan=np.inf))
print('grid rows:', len(g), '; since_end differs:', int(diff.sum()), '; variant end is later (all-clear seen):', int(later.sum()))
print(pd.Series(g['part'].to_numpy()[later]).value_counts().to_dict())
print('since_end in hours, capped vs observed all-clear (media
… [обрезано: показано 2000 из 2730 символов]
```

**Результат**

```
grid rows: 616909 ; since_end differs: 81 ; variant end is later (all-clear seen): 81
{'train': 54, 'test': 22, 'val': 5}
since_end in hours, capped vs observed all-clear (median, max): 11.7 110.5 | 0.94 12.33
since_end_log_h difference (median): 2.02
base rate of y_3 in these rows: 0.864  rows with label: 81
{'U084': 17, 'U003': 13, 'U001': 8, 'U062': 7, 'U014': 5, 'U083': 5, 'U052': 3, 'U050': 3}
```

</details>

<details><summary>🔧 Bash: Check exact boundary semantics synthetic and real · 08:44</summary>

**Аргументы**

```bash
cd "D:/Flash/golova/KSE_AI/AAFS" && cat > reviews/scratch/stage2/s11_boundaries.py <<'EOF'
"""Item 2: exact-boundary semantics on synthetic data (history, grid, labels) and on the real grid."""
import pickle
import sys
import numpy as np
import pandas as pd
sys.path.insert(0, 'tests')
from conftest import _BASE_CFG, records, units_table, utc   # noqa: E402
import copy
from alerts.history import AlertHistory
from alerts.intervals import build_intervals, build_seen
from alerts.grid import build_grid
from alerts.mask import build_masks
from alerts.scope import select_scope
from alerts.timeutil import to_sec

cfg = copy.deepcopy(_BASE_CFG)
UNITS = units_table([('B', 'Raion 3', 'U_B'), ('C', 'Raion 4', 'U_C')])
rows = [('B', 'Raion 3', 'raion', '2026-01-10T10:00:00Z', '2026-01-10T12:00:00Z'),   # starts and ends on the hour
        ('B', 'Raion 3', 'raion', '2026-01-11T09:00:00Z', '2026-01-12T10:00:00Z'),   # 25 h, ends on the hour (rule a)
        ('C', 'Raion 4', 'raion', '2026-01-10T07:00:00Z', '2026-01-10T07:30:00Z')]
df = records(rows)
scope_all, scope = select_scope(df, cfg, period=False), select_scope(df, cfg)
masks, _, _ = build_masks(df, scope_all, UNITS, cfg)
iv = build_intervals(scope, UNITS, masks, cfg)
seen = build_seen(scope, UNITS, cfg)
h = AlertHistory(seen, iv, ['U_B', 'U_C'], masks)
T = pd.DatetimeIndex([utc(x) for x in ['2026-01-10T09:00:00Z', '2026-01-10T10:00:00Z', '2026-01-10T12:00:00Z',
                                         '2026-01-10T13:00:00Z', '2026-01-12T10:00:00Z', '2026-01-12T11:00:00Z']])
H = pd.Timedelta(hours=1)
print('t:', [str(t)[5:16] for t in T])
print('active U_B      ', h.active(T)[:, 0].tolist())
print('starts(1h) U_B  ', h.starts(T, H)[:, 0].tolist(), ' starts(2h) at 12:00 counts 10:00 start? ', h.starts(T[2:3], 2 * H)[0, 0])
print('since_end U_B   ', h.seconds_since_end(T)[:, 0].tolist())
print('since_start U_B ', h.seconds_since_start(T)[:, 0].tolist())
print('sec_active(2h)  ', h.seconds_active(T, 2 * H)[:, 0].tolist())
cfg[
… [обрезано: показано 2000 из 3339 символов]
```

**Результат**

```
t: ['01-10 09:00', '01-10 10:00', '01-10 12:00', '01-10 13:00', '01-12 10:00', '01-12 11:00']
active U_B       [False, True, False, False, False, False]
starts(1h) U_B   [0, 1, 0, 0, 0, 0]  starts(2h) at 12:00 counts 10:00 start?  0
since_end U_B    [nan, nan, 0.0, 3600.0, 3600.0, 7200.0]
since_start U_B  [nan, 0.0, 7200.0, 10800.0, 90000.0, 93600.0]
sec_active(2h)   [0.0, 0.0, 7200.0, 3600.0, 3600.0, 0.0]
2026-01-10T09:00:00Z row [1, 1]
2026-01-10T10:00:00Z no row 
2026-01-10T12:00:00Z row [0, 0]
2026-01-11T08:00:00Z row [1, 1]
2026-01-12T10:00:00Z row [0, 0]
mask rows:                       start                       end          reason
0 2026-01-11 09:00:00+00:00 2026-01-12 10:00:00+00:00        long_24h
1 2026-03-01 00:00:00+00:00 2026-03-01 00:00:00+00:00  after_data_end
real grid rows with t == end of a long_24h mask: 0
real grid rows with t == a segment end: 15 ; segment starts exactly on an hourly moment: 23
```

</details>

<details><summary>🔧 Bash: Check duration spikes and seen hold durations · 08:45</summary>

**Аргументы**

```bash
cd "D:/Flash/golova/KSE_AI/AAFS" && cat > reviews/scratch/stage2/s12_spikes_holds.py <<'EOF'
"""Item 5: spikes by unique post (start, end); rule-(b) posts and how long seen holds them open."""
import pickle
import numpy as np
import pandas as pd
art = pickle.load(open('reviews/scratch/stage2/art.pkl', 'rb'))
sc = art.scope
p = sc.drop_duplicates(['started_at', 'finished_at'])
vc = p['duration'].astype(int).value_counts()
spk = [(v, int(c), round(float(np.mean([vc.get(v + k, 0) for k in range(-10, 11) if k])), 2))
       for v, c in vc.items() if c >= 3 and c > 5 * max(np.mean([vc.get(v + k, 0) for k in range(-10, 11) if k]), 0.2)]
print('spikes by unique (start, end):', sorted(spk))
print('posts at 1800 s:', vc.get(1800, 0), ' mean +-10 s:', round(np.mean([vc.get(1800 + k, 0) for k in range(-10, 11) if k]), 2))
b = sc[sc['is_fake_end'] & (sc['role'] == 'target')]
print('rule-(b) target records:', len(b), ' unique posts (start,end):', len(b.drop_duplicates(['started_at', 'finished_at'])))
hold = (np.minimum(b['next_start'], b['started_at'] + pd.Timedelta(hours=24)) - b['finished_at']).dt.total_seconds() / 3600
print('seen holds rule-(b) records open beyond the recorded end, hours: median', round(hold.median(), 1),
      'p25', round(hold.quantile(.25), 1), 'max', round(hold.max(), 1), '; capped at 24 h:', int((b['next_start'] > b['started_at'] + pd.Timedelta(hours=24)).sum()))
EOF
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage2/s12_spikes_holds.py 2>&1 | tail -8
```

**Результат**

```
spikes by unique (start, end): [(3600, 57, 6.55), (7437, 8, 1.55), (10235, 6, 1.05), (10837, 5, 0.85), (11043, 3, 0.5), (11430, 5, 0.8), (11487, 4, 0.65), (11524, 3, 0.45), (11662, 4, 0.7), (11760, 3, 0.55), (11871, 3, 0.55), (12036, 3, 0.45), (12047, 3, 0.55), (12220, 5, 0.6), (12417, 4, 0.75), (12545, 4, 0.7), (12583, 6, 0.85), (12694, 3, 0.5), (12724, 3, 0.45), (12738, 3, 0.45), (12749, 4, 0.7), (12899, 3, 0.5), (12955, 3, 0.45), (13070, 5, 0.6), (13132, 4, 0.55), (13386, 3, 0.5), (13549, 3, 0.55), (13556, 3, 0.55), (13810, 4, 0.55), (14077, 4, 0.65), (14165, 4, 0.7), (14337, 3, 0.45), (14464, 4, 0.5), (14577, 4, 0.55), (14700, 4, 0.2), (14717, 4, 0.75), (14727, 3, 0.55), (14758, 3, 0.5), (14780, 3, 0.5), (14791, 4, 0.75), (14847, 3, 0.5), (14903, 4, 0.3), (14941, 3, 0.55), (15038, 3, 0.55), (15193, 4, 0.75), (15287, 3, 0.55), (15346, 3, 0.55), (15415, 3, 0.45), (15463, 4, 0.6), (15514, 4, 0.55), (15577, 4, 0.6), (15714, 3, 0.45), (15722, 3, 0.45), (15729, 3, 0.45), (15734, 4, 0.3), (15842, 3, 0.3), (15911, 3, 0.55), (15977, 3, 0.4), (16021, 4, 0.2), (16308, 3, 0.5), (16504, 3, 0.5), (16537, 3, 0.4), (16610, 3, 0.4), (16707, 3, 0.4), (16751, 3, 0.55), (16952, 3, 0.5), (16966, 4, 0.35), (17412, 3, 0.35), (17441, 3, 0.45), (17726, 3, 0.55), (18020, 3, 0.45), (18102, 3, 0.3), (18173, 3, 0.25), (18198, 3, 0.45), (18369, 3, 0.35), (18432, 3, 0.3), (18553, 3, 0.5), (18927, 3, 0.4), (19001, 3, 0.15), (19236, 3, 0.2), (19261, 3, 0.35), (19360, 3, 0.45), (19423, 3, 0.4), (19437, 3, 0.45), (19663, 3, 0.15), (19728, 3, 0.25), (20070, 3, 0.3), (20161, 5, 0.65), (20282, 4, 0.3), (20554, 3, 0.4), (20577, 3, 0.15), (20874, 3, 0.4), (20908, 3, 0.55), (21634, 3, 0.4), (22209, 3, 0.05), (22307, 3, 0.25), (22364, 3, 0.25), (22691, 3, 0.3), (22975, 3, 0.1), (23340, 3, 0.1), (23373, 3, 0.35), (23380, 3, 0.4), (23387, 3, 0.2), (23784, 3, 0.4), (23871, 3, 0.45), (24115, 3, 0.25), (27727, 3, 0.1), (29858, 3, 0.2), (35452, 3, 0.1), (36298, 3, 0.0), (37564, 3, 0.2), (37940, 3, 0.2), (46382, 3, 0.15), (55544, 3, 0.25), (68877, 3, 0.15), (110736, 3, 0.1)]
posts at 1800 s: 8  mean +-10 s: 11.35
rule-(b) target records: 76  unique posts (start,end): 53
seen holds rule-(b) records open beyond the recorded end, hours: median 12.7 p25 5.8 max 23.0 ; capped at 24 h: 31
```

</details>

<details><summary>🔧 Bash: Verify seen vs segments and held_open rows · 08:45</summary>

**Аргументы**

```bash
cd "D:/Flash/golova/KSE_AI/AAFS" && cat > reviews/scratch/stage2/s13_seen_vs_segments.py <<'EOF'
"""Item 3b: seen vs intervals, all differences explained? held_open rows of the grid = which records?"""
import pickle
import numpy as np
import pandas as pd
from alerts.config import load_config
from alerts.history import AlertHistory
from alerts.scope import attach_units
from alerts.spans import union, covers
from alerts.timeutil import to_sec
from alerts.grid import moments

cfg = load_config()
art = pickle.load(open('reviews/scratch/stage2/art.pkl', 'rb'))
rec = attach_units(art.scope, art.units)
seg = union(rec[['unit_id', 'started_at', 'finished_at']].rename(columns={'started_at': 'start', 'finished_at': 'end'}), 'unit_id')
iv = art.intervals.rename(columns={'start_utc': 'start', 'end_utc': 'end'})[['unit_id', 'start', 'end']]
pd.testing.assert_frame_equal(seg.reset_index(drop=True), iv.reset_index(drop=True), check_dtype=False)
print('segments == union of records [start, finished_at): OK')
d = rec['open_until'] != rec['finished_at']
print('open_until != finished_at:', int(d.sum()), '; all of them 3600 s:', bool((rec.loc[d, 'duration'] == 3600).all()),
      '; open_until < finished_at anywhere:', int((rec['open_until'] < rec['finished_at']).sum()))

# held_open grid status: quiet by segments, not masked, but active in seen
ids = art.grid['unit_id'].drop_duplicates().tolist()
T = moments(cfg); t = to_sec(T)
held = AlertHistory(art.seen, art.intervals, ids).active(T)
res = []
for j, u in enumerate(ids):
    g = art.intervals[art.intervals['unit_id'] == u]
    ins = covers(to_sec(g['start_utc']), to_sec(g['end_utc']), t)
    m = union(art.masks[art.masks['unit_id'] == u], 'unit_id')
    inm = covers(to_sec(m['start']), to_sec(m['end']), t)
    ep = art.intervals[art.intervals['unit_id'] == u].groupby('episode').agg(s=('start_utc', 'min'), e=('end_utc', 'max'))
    inep = covers(to_sec(ep['s']), to_sec(ep['e']), t)
    for i in np.flatnonzero(held[:, j] & ~ins & ~inm 
… [обрезано: показано 2000 из 2426 символов]
```

**Результат**

```
segments == union of records [start, finished_at): OK
open_until != finished_at: 82 ; all of them 3600 s: True ; open_until < finished_at anywhere: 0
held_open unit-moments (rows removed): 8
   U008 2026-02-01 01:00:00+00:00 [{'raion': 'Bohodukhivskyi raion', 'started_at': Timestamp('2026-01-31 23:46:52+0000', tz='UTC'), 'finished_at': Timestamp('2026-02-01 00:46:52+0000', tz='UTC'), 'next_start': Timestamp('2026-02-01 01:19:00+0000', tz='UTC'), 'is_fake_end': False}]
   U019 2026-05-27 11:00:00+00:00 [{'raion': 'Dniprovskyi raion', 'started_at': Timestamp('2026-05-27 09:24:20+0000', tz='UTC'), 'finished_at': Timestamp('2026-05-27 10:24:20+0000', tz='UTC'), 'next_start': Timestamp('2026-05-27 12:06:11+0000', tz='UTC'), 'is_fake_end': False}]
   U019 2026-05-27 12:00:00+00:00 [{'raion': 'Dniprovskyi raion', 'started_at': Timestamp('2026-05-27 09:24:20+0000', tz='UTC'), 'finished_at': Timestamp('2026-05-27 10:24:20+0000', tz='UTC'), 'next_start': Timestamp('2026-05-27 12:06:11+0000', tz='UTC'), 'is_fake_end': False}]
   U066 2026-01-27 11:00:00+00:00 [{'raion': 'Okhtyrskyi raion', 'started_at': Timestamp('2026-01-27 09:44:35+0000', tz='UTC'), 'finished_at': Timestamp('2026-01-27 10:44:35+0000', tz='UTC'), 'next_start': Timestamp('2026-01-27 11:29:38+0000', tz='UTC'), 'is_fake_end': False}]
   U077 2026-05-27 11:00:00+00:00 [{'raion': 'Samarivskyi raion', 'started_at': Timestamp('2026-05-27 09:24:20+0000', tz='UTC'), 'finished_at': Timestamp('2026-05-27 10:24:20+0000', tz='UTC'), 'next_start': Timestamp('2026-05-27 12:06:06+0000', tz='UTC'), 'is_fake_end': False}]
   U077 2026-05-27 12:00:00+00:00 [{'raion': 'Samarivskyi raion', 'started_at': Timestamp('2026-05-27 09:24:20+0000', tz='UTC'), 'finished_at': Timestamp('2026-05-27 10:24:20+0000', tz='UTC'), 'next_start': Timestamp('2026-05-27 12:06:06+0000', tz='UTC'), 'is_fake_end': False}]
   U083 2026-03-04 18:00:00+00:00 [{'raion': 'Sumskyi raion', 'started_at': Timestamp('2026-03-04 16:29:41+0000', tz='UTC'), 'finished_at': Timestamp('2026-03-04 17:29:41+0000', tz='UTC'), 'next_start': Timestamp('2026-03-04 19:03:54+0000', tz='UTC'), 'is_fake_end': False}]
   U083 2026-03-04 19:00:00+00:00 [{'raion': 'Sumskyi raion', 'started_at': Timestamp('2026-03-04 16:29:41+0000', tz='UTC'), 'finished_at': Timestamp('2026-03-04 17:29:41+0000', tz='UTC'), 'next_start': Timestamp('2026-03-04 19:03:54+0000', tz='UTC'), 'is_fake_end': False}]
```

</details>

<details><summary>🔧 Bash: Run test suite and check since_start coverage · 08:47</summary>

**Аргументы**

```bash
cd "D:/Flash/golova/KSE_AI/AAFS" && PYTHONIOENCODING=utf-8 timeout 300 python -m pytest -q -p no:cacheprovider 2>&1 | tail -5; grep -rn "seconds_since_start\|since_start" tests/ src/ | grep -v "\.pyc"
```

**Результат**

```
..........................                                               [100%]
26 passed in 26.24s
src/alerts/history.py:71:    def seconds_since_start(self, T) -> np.ndarray:
```

</details>

<details><summary>🔧 Bash: Recount stage 2 summary held-open numbers · 08:47</summary>

**Аргументы**

```bash
cd "D:/Flash/golova/KSE_AI/AAFS" && cat > reviews/scratch/stage2/s14_summary_numbers.py <<'EOF'
"""Rule 8: recount stage2_summary numbers on held-open state (1,046 unit-moments, 153 moments) and bridged pauses."""
import pickle
import numpy as np
from alerts.config import load_config
from alerts.history import AlertHistory
from alerts.spans import covers
from alerts.timeutil import to_sec
from alerts.grid import moments
from alerts.intervals import episodes

cfg = load_config()
art = pickle.load(open('reviews/scratch/stage2/art.pkl', 'rb'))
tg = art.units[art.units['role'] == 'target']['unit_id'].drop_duplicates().tolist()
T = moments(cfg); t = to_sec(T)
act = AlertHistory(art.seen, art.intervals, tg).active(T)
ep = episodes(art.intervals)
held = np.zeros_like(act); br = np.zeros_like(act)
for j, u in enumerate(tg):
    g = art.intervals[art.intervals['unit_id'] == u]; e = ep[ep['unit_id'] == u]
    ins = covers(to_sec(g['start_utc']), to_sec(g['end_utc']), t)
    held[:, j] = act[:, j] & ~ins
    br[:, j] = covers(to_sec(e['start_utc']), to_sec(e['end_utc']), t) & ~ins
print('held open (seen active, segments quiet):', int(held.sum()), 'unit-moments,', int(held.any(1).sum()), 'moments')
print('bridged pauses:', int(br.sum()), 'unit-moments,', int(br.any(1).sum()), 'moments')
EOF
PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage2/s14_summary_numbers.py 2>&1 | tail -3
```

**Результат**

```
held open (seen active, segments quiet): 1046 unit-moments, 153 moments
bridged pauses: 791 unit-moments, 425 moments
```

</details>

<details><summary>🔧 Bash: Grep README for related claims · 08:47</summary>

**Аргументы**

```bash
cd "D:/Flash/golova/KSE_AI/AAFS" && grep -n "24 год\|1 год\|seen\|знання\|known_at\|knowledge\|вигадан" README.md | head -20
```

**Результат**

```
52:- тривоги, довші за добу, і тривоги з кінцем, вигаданим процесором датасету, маскуються як «статус
75:  `t`: вигаданий процесором кінець тривоги записується заднім числом, тому до наступного початку
146:від вигаданих цифр і неперевірених висновків до витоку з майбутнього, який знайшла людина, а не тест.
```

</details>

<details><summary>🔧 Bash: Read README leak-protection section · 08:47</summary>

**Аргументы**

```bash
cd "D:/Flash/golova/KSE_AI/AAFS" && sed -n 68,90p README.md
```

**Результат**

```
межами районів зі знімка датасету, а не з пам'яті. Календар, ідентичність одиниці.
- **Моделі (D20):** логістична регресія і LightGBM. Гіперпараметри, зокрема вагу свіжих даних,
  обрано один раз на валідації.

## Захист від витоку

- Ознаки читають історію лише через `AlertHistory`. Вона віддає те, що спостерігач бачив до моменту
  `t`: вигаданий процесором кінець тривоги записується заднім числом, тому до наступного початку
  тривога вважається відкритою (D16, D21).
- **Псування майбутнього** (D18): усі записи після зрізу перемішуються, усе перезбирається; навчальні
  рядки, ознаки й прогнози всіх моделей у момент зрізу збігаються біт у біт.
- **Знання на момент зрізу** (D21): відтворюється, що лежало в датасеті на момент зрізу, з урахуванням
  записів, зроблених пізніше за їхні власні мітки часу. Ознаки мають збігатися з порахованими за
  повними даними.
- Обидві перевірки виконуються на реальних даних під час кожного запуску (`reports/leakage_check.json`)
  і в тестах на синтетиці; кожну перевірено підміною з витоком.

## Перевірка на свіжих даних: alerts.in.ua, через місяць (D22)

Основний тест закінчується 7 вересня. API alerts.in.ua дає історію за останні 30 днів, тобто
з 12 вересня по 11 жовтня. Це **інше джерело**, тому дані не склеюються: моделі, навчені на даних до
7 вересня, заморожені й лише прогнозують, а ознаки рахуються за даними API. Детально —
[`reports/api_check.md`](reports/api_check.md).
```

</details>

<details><summary>🔧 Bash: Check scratch sizes and line refs · 08:48</summary>

**Аргументы**

```bash
cd "D:/Flash/golova/KSE_AI/AAFS" && ls -la reviews/scratch/stage2/ | awk '{print $5, $9}'; grep -n "Цена: 6\|Применяется к каждой записи до объединения\|время с последнего отбоя\|since_end_log_h\` — log" DECISIONS.md | head; grep -n "is_fake_end\|written" src/alerts/leakage.py
```

**Результат**

```
0 .
0 ..
87630158 art.pkl
4223020 diff_50ce482.txt
2419 s01_build_compare.py
5002 s02_spans_property.py
4460 s03_processor.py
4634 s04_episode_starts.py
644975 s04_seen_starts_without_episode.csv
3168 s04_starts_while_seen_active.csv
1554 s05_inspect48.py
1522 s06_p1.py
2780 s07_multi_units.py
3273 s08_asof_layer.py
567 s09_knowledge_cut.py
2501 s10_cap_after_end.py
3143 s11_boundaries.py
1306 s12_spikes_holds.py
2218 s13_seen_vs_segments.py
1200 s14_summary_numbers.py
390:- Цена: 6 настоящих тревог ровно на 1 час (следующее начало через 1.1–2.7 ч) считаются открытыми до следующей тревоги, то есть максимум на 1.7 ч дольше. Это неточность измерения, не зависящая от будущего.
481:**Решение по тревогам с неизвестным концом** (открыто с D10/D16): тревога, у которой отбой не виден, считается активной **не дольше 24 часов** (`history.max_open_hours`), как предлагал план. Правило причинное: в момент `t` известно только время начала и то, был ли отбой. Применяется к каждой записи до объединения: иначе единица из нескольких районов (Донецкая, 8 районов с перекрывающимися записями) «погасла» бы посреди многодневной законной тревоги. Это проверяет `tests/test_history.py`. Состояние «на момент t» хранится в `data/seen.csv`. Пар «единица × момент», где тревога держится открытой без видимого отбоя, стало 1 046 вместо 3 529. Строки сетки не изменились.
486:- время с последнего отбоя считается только по наблюдаемому времени.
494:| Своя единица | `since_end_log_h` — log(1 + часы с последнего отбоя); `starts_6h`, `starts_24h`, `starts_7d` — начала эпизодов; `active_share_24h` |
12:Corruption cannot see leaks made by the source itself: a record written later than its own
45:    A record exists once it has been written: at its all-clear, or for an invented end at the next
46:    start of its location. Records started by the cut but not yet written were open alerts; they are
55:    written = rec['next_start'].where(rec['is_fake_end'], rec['finished_at'])
57:    still_open = (written[out.index] > cut).to_numpy()
```

</details>

<details><summary>🔧 Write: reviews/claude/stage2.md · 08:49</summary>

**Аргументы**

```
# file: reviews/claude/stage2.md
# Ревью этапа 2: интервалы, `seen`, `AlertHistory`, модель процессора

Ревьюер: Claude (независимо от других ревьюеров; их отчёты не читались). Скрипты лежат в `reviews/scratch/stage2/`, запуск из корня:
`PYTHONPATH=src PYTHONIOENCODING=utf-8 python reviews/scratch/stage2/<x>.py`. `s01` пересобирает таблицы в памяти (`build_all`, 13 с) и кладёт кэш `art.pkl`, остальные скрипты читают этот кэш. Файлы проекта не менялись. `run_all`, `save_all`, API и скачивание не запускались.

## 1. Резюме

Слой данных этапа 2 в целом корректен. `merge_labels`/`union` совпали с наивной реализацией на 3000 случайных случаев с краевыми ситуациями. Границы `[s, e)`, `(t−w, t]` и `(t, t+h]` согласованы между собой и с сеткой. Таблицы на диске совпадают с пересборкой бит в бит, точность и часовой пояс не теряются. Все 48 известных расхождений «начало эпизода при активном `seen`» — случай той же локации. Новых путей утечки, которые реально встречаются в данных, нет.

Главная находка — **два разных описания одного и того же процессора в коде.** `build_seen` держит открытой *любую* запись ровно 3600 с, а `leakage.known_at` считает настоящими часовые записи со следующим началом не позже 3 ч. Из-за этого проверка знания D21 на реальных данных **падает** на трёх из трёх срезов, выбранных сразу после таких записей. На метрики это не влияет, но утверждение D21 и README «ознаки мають збігатися» верно только для срезов вне примерно 4.6 ч окон за 10 месяцев.

Остальное — мелочи: оценки и обоснования в D16 и D19, `since_end` после ограничения 24 ч, неиспользуемый и непротестированный `seconds_since_start`, незадокументированная смена версии процессора датасета. Критичных находок нет.

## 2. Находки

### S2-1. `known_at` и `build_seen` по-разному моделируют выдуманный конец, поэтому проверка знания D21 падает на реальных данных
- **Серьёзность:** существенно. **Уверенность:** проверено на данных.
- **Где:**
  - `src/alerts/leakage.py:55` — `written = next_start.where(i
… [обрезано: показано 2000 из 15267 символов]
```

**Результат**

```
File created successfully at: D:\Flash\golova\KSE_AI\AAFS\reviews\claude\stage2.md (file state is current in your context — no need to Read it back)
```

</details>

<details><summary>🔧 Bash: Remove large cache files, adjust report notes · 08:49</summary>

**Аргументы**

```bash
cd "D:/Flash/golova/KSE_AI/AAFS" && rm -f reviews/scratch/stage2/art.pkl reviews/scratch/stage2/diff_50ce482.txt && python - <<'EOF'
p='reviews/claude/stage2.md'
t=open(p,encoding='utf-8').read()
t=t.replace("`s01` пересобирает таблицы в памяти (`build_all`, 13 с) и кладёт кэш `art.pkl`, остальные скрипты читают этот кэш.",
 "`s01` пересобирает таблицы в памяти (`build_all`, 13 с) и кладёт кэш `art.pkl`, остальные скрипты читают этот кэш. Кэш (88 МБ) после работы удалён, чтобы не попал в git; сначала запустите `s01`.")
t=t.replace("(`diff_50ce482.txt`)", "(`git -C dataset_repo show 50ce482 -- datasets/official_data_en.csv`)")
open(p,'w',encoding='utf-8').write(t)
EOF
wc -l reviews/claude/stage2.md; ls reviews/scratch/stage2/
```

**Результат**

```
126 reviews/claude/stage2.md
s01_build_compare.py
s02_spans_property.py
s03_processor.py
s04_episode_starts.py
s04_seen_starts_without_episode.csv
s04_starts_while_seen_active.csv
s05_inspect48.py
s06_p1.py
s07_multi_units.py
s08_asof_layer.py
s09_knowledge_cut.py
s10_cap_after_end.py
s11_boundaries.py
s12_spikes_holds.py
s13_seen_vs_segments.py
s14_summary_numbers.py
```

</details>

<details><summary>🔧 SubagentHandback: {"message": "Отчёт по этапу 2 записан в `reviews/claude/stage2.md` (126 строк). Отчёт в старом месте `reviews/stage2.md… · 08:50</summary>

**Аргументы**

```json
{
 "message": "Отчёт по этапу 2 записан в `reviews/claude/stage2.md` (126 строк). Отчёт в старом месте `reviews/stage2.md` я не записывал, восстанавливать там нечего, чужие отчёты и `scratch-gpro/` не открывал. Файлы проекта не менял. `run_all`, `save_all`, `api_check`, скачивание и API не запускал, токен не открывал, git только читал (`log`/`show` в `dataset_repo`). Скрипты лежат в `reviews/scratch/stage2/` (s01–s14). Кэш `art.pkl` (88 МБ) после работы удалил, чтобы он не попал в git; `s01` создаёт его заново за 13 с.\n\n**Резюме**\n- Слой данных этапа 2 корректен. `merge_labels`/`union` совпали с наивной реализацией на 3000 случайных наборов с краевыми случаями.\n- Границы `[s, e)`, окно признаков `(t−w, t]` и метка `(t, t+h]` согласованы между собой и с сеткой: событие ровно в `t` обрабатывается одинаково везде.\n- `intervals`, `seen`, `mask` и `grid` на диске совпадают с пересборкой в памяти бит в бит, точность и часовой пояс не теряются. Цифры `stage2_summary.md` повторяются, тесты: 26 passed.\n- Все 48 известных расхождений «начало эпизода при активном `seen`» — новый пост той же локации, то есть законный случай.\n- Путь утечки через начала эпизодов (не записанный ещё выдуманный конец другого района той же единицы) в коде есть, в данных встречается 0 раз. То же со сценарием «цепочка коротких записей одного района плюс зависшая запись другого».\n- Главная находка: проверка знания D21 (`leakage.known_at`) и таблица `seen` (`build_seen`) по-разному описывают один и тот же процессор. Поэтому `knowledge_check` на реальных данных падает на всех трёх срезах, выбранных сразу после настоящих часовых тревог. На метрики это не влияет.\n- Мелочи:\n  - цена решения D16 занижена: по плотности длительностей среди записей правила (б) спрятаны ещё 1–3 настоящие часовые тревоги, и `seen` держит их открытыми до 23 ч, а не до 1.7 ч;\n  - после тревоги длиннее 24 ч `since_end` отсчитывается от `s+24 ч`, а не от увиденного отбоя: 81 строка, из них 22 в тесте;\n  - обоснование D19 «
… [обрезано: показано 2000 из 3523 символов]
```

**Результат**

```
{"success":true,"message":"Report delivered to your caller."}
```

</details>
