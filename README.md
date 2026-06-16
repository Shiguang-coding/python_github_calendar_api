# What's this?

本项目的演化路径：[Zfour/hexo-github-calendar](https://github.com/Zfour/hexo-github-calendar)（最原始项目）→ [Zfour/python_github_calendar_api](https://github.com/Zfour/python_github_calendar_api)（后端 API）→ [Barry-Flynn/python_github_calendar_api](https://github.com/Barry-Flynn/python_github_calendar_api)（改进版，规范了传参方式）→ 本仓库（修复兼容性问题）。

原理是通过 Python 爬取 GitHub 用户贡献数据，部署到 Vercel 上作为 API 使用。调用方式为标准的 key-value 格式：`/api?user=GitHub用户名`。推荐结合本文档自行部署，如果帮到你了，请给个免费的 star 鼓励支持一下我吧！

如果你有 Hexo 博客，可以搭配使用 [Barry-Flynn/hexo-github-calendar](https://github.com/Barry-Flynn/hexo-github-calendar) 插件在前端渲染贡献热力图（该插件同样 fork 自 [Zfour/hexo-github-calendar](https://github.com/Zfour/hexo-github-calendar)）。


## 相对上游的改动

> 最后更新：2026-06-16

本仓库基于 [Barry-Flynn/python_github_calendar_api](https://github.com/Barry-Flynn/python_github_calendar_api) 做了以下调整：

### 1. 重写贡献数据解析逻辑

**原因**：原版通过正则匹配 GitHub 个人主页 HTML 中的 SVG 贡献图（`data-date` 属性 + `<tool-tip>` 文本），但 GitHub 频繁改版前端结构，导致旧正则无法正确匹配贡献数量，返回的 count 全部为 0。

**改动**：改用 GitHub 专用的贡献数据页面 `https://github.com/users/{username}/contributions`，该页面为服务端渲染，数据完整可靠。通过 `data-date` 属性获取完整日期（含年份），通过 `<tool-tip>` 元素中的文本提取贡献数量。

### 2. 更新 Python 依赖版本

**原因**：原版 `requirements.txt` 锁定的依赖版本过旧（`requests==2.25.1`、`urllib3==1.26.2`），在 Vercel 当前默认的 Python 3.12 环境下，旧版 `urllib3` 内部依赖的 `six` 模块不可用，导致 `ModuleNotFoundError: No module named 'urllib3.packages.six.moves'` 运行时崩溃。

**改动**：将依赖升级为：
```
certifi>=2023.7.22
charset-normalizer>=3.1.0
idna>=3.4
requests>=2.31.0
urllib3>=2.0.0
```

### 3. 移除不必要的 URL 参数拼接

**原因**：原版请求 GitHub 时拼接了 `?action=show&controller=profiles&tab=contributions&user_id=` 等参数，这些参数在当前 GitHub 版本中已无效。

**改动**：直接请求 `https://github.com/users/{username}/contributions`，无需额外参数。


## 如何部署自用的 Vercel API

### 1. 注册 Vercel

首先前往 [Vercel 官网](https://vercel.com/)，点击右上角的 sign up 进行注册。

> **注意**：Vercel 最低要求 Node.js 20.x（18.x 已不支持），但本项目为 Python 项目，Node.js 版本设置不影响运行。

极有可能遇到的 bug：

若注册时提示 `Error:This user account is blocked.Contact support@vercel.com for more information.`

这是由于 `Vercel` 不支持大部分国内邮箱。可以将 `github` 账号主邮箱改为 `Gmail` 邮箱。建议一开始注册 `github` 账号时就使用 `Gmail` 等国外邮箱。

### 2. 新建项目

打开 [dashboard](https://vercel.com/dashboard) 点击新建项目的 `New Project` 按钮。导入本仓库或你 fork 后的仓库。

`Vercel` 的 `PROJECT NAME` 可以自定义，之后不支持修改。下方选项保持默认即可。

点击 Deploy 完成部署。

### 3. 检查 API 是否配置成功

访问 API 链接，格式为：`https://你的域名/api?user=GitHub用户名`

例如：`https://python-github-calendar-api.vercel.app/api?user=shiguang-coding`

如果返回包含 `total` 和 `contributions` 的 JSON 数据则说明配置成功。

### 4. （可选）绑定自定义域名

在 Vercel 项目的 Settings → Domains 中添加自定义域名，然后按提示添加 DNS 解析记录（CNAME 指向 `cname.vercel-dns.com` 或 A 记录指向 `76.76.21.22`）。


## License

MIT
