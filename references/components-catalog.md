# 星火任务链组件速查目录

本目录根据官方组件总览及其链接的组件说明整理，已经作为 skill 的离线知识层保存，用于普通任务中快速发现组件、判断用途并设计数据流。运行 skill 时优先使用本地目录和 `component-index.json`，不需要每次联网。表格只列关键输入/输出，不代表穷尽所有配置。

官方文档根路径：`https://flames.iflytek.com:2443/agent/docs/components/`。详情页路径相对于该路径；该地址用于后续维护、版本冲突或用户明确要求核对时，不是普通运行时的必需依赖。

## 通用组件

| 组件 | 适用场景 | 关键输入 -> 输出 | 详情页 |
|---|---|---|---|
| 脚本执行 | 结构转换、计算、字段抽取、轻量业务逻辑 | 自定义入参对象 -> 自定义出参对象；入口为 `execute(input)`；支持 JavaScript、Groovy、Python | `desc/script.html` |
| 接口调用 | 调用外部 HTTP API | `url`、`method`、`header`、`query`、按方法提供 `body` -> `output`（纯文本响应） | `desc/api-call.html` |
| 邮件发送 | 将任务结果发送为邮件 | 标题、收件人/抄送、内容、格式及 SMTP 配置 -> 状态码 `code` | `desc/send-email.html` |

总览另提及 WebSocket 通信和 HTTP 下载等通用能力；若当前组件面板中可见，先检查对应说明，不要凭总览猜配置。

## 控制组件

| 组件 | 适用场景 | 关键输入 -> 输出 | 详情页 |
|---|---|---|---|
| 条件组件 | 根据条件选择不同流程出口 | 条件参数 `args`、分支列表 `conditions` -> 命中分支；页面示例使用 Groovy 条件表达式和 `{{变量}}` 引用 | `ctrl/condition.html` |
| 遍历组件 | 对输入列表逐项执行子流程 | `list`、子流程 `process`、异常策略、扩展参数、间隔 -> 进度 `progress`、结果列表 `List` | `ctrl/foreach.html` |
| 循环组件 | 将上轮结果传给下一轮，直到条件不满足 | 首轮输入、循环子流程、继续条件 `condition`、异常策略、间隔 `sleepTime` -> `progress`、结果列表 `List`、最终 `output` | `ctrl/while.html` |

遍历面向已有列表的每个元素；循环是状态逐轮传递的 do-while 风格流程。循环需设置可终止条件并验证边界。表达式语法按详情页核对，不要假定各控制组件语法相同。

## 文本处理

| 组件 | 适用场景 | 关键输入 -> 输出 | 详情页 |
|---|---|---|---|
| 文本模板 | 把变量填入固定模板 | `arg`、`template`、模板引擎 -> `text` | `text/text-template.html` |
| 文本处理 | 按长度、分隔符或篇章规则切分文本 | `text`、`splitType`、相应长度/重叠设置 -> `list` | `text/text-process.html` |
| 列表处理 | 按索引取列表元素或把多段文本合并 | `list`、`index` -> `data`（具体模式核对组件配置） | `text/list-process.html` |
| 代码解析 | 从模型或文本内容中提取代码 | `codeString` -> `code` | `text/code-parser.html` |
| JSON 提取 | 从 JSON、代码块或格式不规整的模型输出中提字段 | `jsonString` -> 动态字段 `result` | `text/json-extract.html` |
| 要素抽取 | 按输入字段、Excel 或数据集 schema 从文本抽取信息 | 文本、要素定义/来源、补充说明及模型参数 -> 抽取结果 `text` | `text/extraction.html` |
| 同义词改写 | 基于同义词库改写查询词 | `query`、`libIdList` -> `rewrittenQuery`、`mappings` | `text/synonym-rewrite.html` |

## 文档处理

| 组件 | 适用场景 | 关键输入 -> 输出 | 详情页 |
|---|---|---|---|
| 图片读取 | 读取图片文件并得到 Base64 | `file` -> `base64` | `document/image-handle.html` |
| 文档获取 | 读取文本、Markdown、Word、Excel、PDF 等文档 | `file`、`format`、可选 `includeImages` -> `text` | `document/doc-read.html` |
| 文档生成 | 从 Markdown 生成文档 | `markdown`、可选 PPT 主题 -> `file`、下载链接 `url` | `document/doc-create.html` |
| Excel 读写 | 按行、列或区域读取 Excel | `file`、`type`、`startPosition`、可选 `endPosition` -> `texts` | `document/excel-rw.html` |
| 网页爬虫 | 抓取网页指定区域 | `url`、`selectors` -> `results`（列表，元素为 Markdown） | `document/crawler.html` |

## 语言模型

| 组件 | 适用场景 | 关键输入 -> 输出 | 详情页 |
|---|---|---|---|
| 通用大模型 | 自然语言生成、归纳、分类、问答等 | `domain`、`prompt`、`temperature`、`topK` -> 流式 `text` | `llm/llm.html` |
| 多模态 | 基于图片和问题进行理解 | 固定模型、图片 `file`、问题 `text` -> 流式 `result` | `llm/multimodal.html` |
| 记忆组件 | 读取指定任务链/智能体会话的历史轮次 | `type`、`sessionId`、`rounds` -> `texts` | `llm/session-memory.html` |
| 长期记忆 | 按用户和查询召回长期记忆 | `query`、`limit`、`userId` -> `memories` | `llm/user-memory.html` |

总览也提及 Function Call 和代码解释器；本次组件侧栏没有对应独立详情页。仅当当前平台面板/版本确实提供时再选用并核对专属配置。

## 文档索引

| 组件 | 适用场景 | 关键输入 -> 输出 | 详情页 |
|---|---|---|---|
| 知识检索 | 从一个或多个知识库中召回相关片段 | `text`、知识库 `dbNames` -> `results`、原文引用 `parts` | `index/knowledge-search.html` |
| 知识库管理 | 读取知识库文档/分类及指定版本 | 知识库、版本、返回结构 -> `results` | `index/knowledge-manager.html` |
| 图谱知识库 | 基于知识图谱做实体/关系检索问答 | `graphLibId`、问题 `text`、`graphMode`、`graphLimit` -> `result`、`chunks`、`nodes`、`edges` | `index/graph-kb-qa.html` |

知识检索输出可包含片段和引用；回答生成通常还需要把检索结果映射到大模型输入。知识库管理不是问答检索的替代品，按目标选择。

## 数据处理

| 组件 | 适用场景 | 关键输入 -> 输出 | 详情页 |
|---|---|---|---|
| 数据库查询 | 对已配置数据库执行 SQL | `dbUri`、`user`、`password`、`dbName`、`sql` -> `results` | `data/mysql-query.html` |
| Excel 表查询 | 对 Excel 表执行 SQL 查询 | `file`、`sql`（表名示例 `table1`、`table2`） -> `results` | `data/excel-query.html` |

数据库凭据属于敏感数据。不要把真实密码写进提示词、示例或普通输出；按平台安全配置能力处理，并核对 SQL 权限和读写范围。

## 输出显示

| 组件 | 适用场景 | 关键输入 -> 输出 | 详情页 |
|---|---|---|---|
| HTML 组件 | 用 HTML 模板组织自定义结果展示 | `arg`、`template` -> HTML 格式 `text` | `output/html.html` |
| ECharts 图表 | 将结构化数据展示为图表 | ECharts `option` -> 图表 `text` | `output/echarts.html` |
| 打字机 | 将文本按间隔流式呈现 | `text`、`wordsCount`、`returnInterval` -> 流式 `text` | `output/type-writer.html` |

## 离线使用与更新边界

- 普通任务：读取本目录和 `component-index.json`，直接完成组件选择、节点配置草案及数据契约设计。
- 实际任务链优先：用户提供的 `baseInfo.json`、节点导出或平台截图中的真实字段优先于本目录的抽象描述。
- 需要联网的情况：本地没有该组件、用户明确要求最新官方变化、实际导出与本地知识冲突，或需要确认平台版本差异。
- 不应沉淀到通用目录：单个任务链的业务提示词、专有表名、真实地址、账号、密码和一次性变量名。
- 维护时才更新：发现稳定、跨任务可复用的组件规则后，再更新本目录和索引；单个任务的临时差异记录到 `ai痕迹/`。

## 选择提示

- 固定格式拼接优先考虑文本模板；需要 HTML 展示再用 HTML 组件。
- 调用外部服务用接口调用；需要字段映射、类型转换或响应瘦身时再加脚本节点。
- 逐项处理列表用遍历；依赖上一轮结果并按条件继续用循环。
- 知识库资料支撑回答时，把检索结果明确连入生成节点，并定义空召回时的处理方式。
- 模型输出需结构化时，优先要求模型按目标结构输出，再用 JSON 提取/脚本校验；不要假设自然语言输出天然符合 schema。
- 文件型输入输出须说明平台要求的文件对象/文件 ID 和格式；不要把文件路径、Base64、下载 URL 混为同一类型。
- 最终组件由需求和实际可用组件共同决定，遵循最小必要原则。
