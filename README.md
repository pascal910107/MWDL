# Minimal Web Description Language (MWDL)

MWDL（Minimal Web Description Language）是一種**極度簡潔**的網頁描述語言，旨在降低撰寫標記時的心智負擔，同時提升 AI 自動生成與解析的效率。透過縮排結構與直觀關鍵字，開發者能使用極少的標記快速組裝頁面元素、樣式與基本互動，而無需顧慮 HTML、CSS 與 JavaScript 三者的繁瑣細節。

---

## 主要特色

- **簡潔語法**：使用縮排表示層次，省略冗長閉合標籤。
- **內建樣式**：以鍵值對方式在元素標記中直接設定常用樣式（顏色、字型、間距等），不需獨立 CSS 檔案。
- **直觀元素**：關鍵字如 `Text`、`Image`、`Button`、`Form`、`Row` 等，語義清晰易讀。
- **基本互動**：支援 `onClick`、`onSubmit` 等事件屬性，以及簡單的 `If` 條件渲染。
- **響應式佈局**：容器（如 `Row`）預設具備自動換行機制，無需撰寫媒體查詢。
- **易於 AI 生成**：結構一致、扁平化，減少因標籤閉合錯誤而導致的無效輸出。

## 語法對照表
| MWDL       | HTML                          |
| ---------- | ----------------------------- |
| `Text`     | `<p>...</p>`                  |
| `Heading`  | `<h1>...</h1>`（可指定 `level`） |
| `Image`    | `<img src=... alt=.../>`      |
| `Link`     | `<a href=...>...</a>`         |
| `Input`    | `<input ... />`               |
| `Button`   | `<button>...</button>`        |
| `Form`     | `<form action=... method=post>`|
| `Section`  | `<div>` / `<section>`         |
| `Row`      | `<div style="display:flex;flex-wrap:wrap;">` |
| `If`       | Kept as comment/data-if logic  |

## 轉換

`lang2html.py` 是一個將「Minimal Web Description Language (MWDL)」語法，轉譯成標準 HTML 文件的輕量級工具。借助簡潔直觀的 MWDL 標記語言，開發者能以更高效的方式撰寫網頁結構、樣式與互動邏輯，並直接生成相容於瀏覽器的 HTML。

## 使用方式

```bash
# 轉換 MWDL 檔案到 HTML，並輸出到指定檔案：
python lang2html.py input.mwdl output.html

# 若省略輸出檔案，將結果印到終端：
python lang2html.py input.mwdl
```

- `input.mwdl`：包含 MWDL 語法的原始檔。  
- `output.html`：轉換後的 HTML 檔。如果省略，預設輸出到標準輸出 (stdout) 。

## 範例

在專案目錄下建立 `login.mwdl`：
```plaintext
Heading "用戶登入"

Image { src: "logo.png", alt: "Logo", width: "80%" }

Form { onSubmit: "/login" }:
  Text "用戶名："
  Input { name: "username", placeholder: "請輸入用戶名" }

  Text "密碼："
  Input { type: "password", name: "password", placeholder: "請輸入密碼" }

  Button "登入"

If loginError:
  Text "帳號或密碼錯誤，請重試。" { color: red }

Link "忘記密碼？" { href: "/reset-password" }
```

執行轉換：
```bash
python lang2html.py login.mwdl login.html
```

在瀏覽器打開 `login.html`，即可看到轉譯後的登入頁面。

## 定制與擴充

- **樣式管理**：可於轉譯腳本中加入全域 CSS 模板或 class 機制，以統一設計風格。
- **條件渲染**：目前以 HTML 註解標記 `If` 區塊，後續可改為輸出自訂屬性並由前端框架處理。
- **事件處理**：可擴展為生成完整的 JavaScript 函式或 ES 模組，支援更複雜的動態行為。
- **新語法**：如需支持更多元件（如表格、清單、動畫），請在 `_parse_line` 與 `_TAG_MAP` 中添加對應邏輯。
