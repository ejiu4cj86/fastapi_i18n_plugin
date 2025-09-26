# FastAPI I18n Plugin

A plugin for FastAPI to handle internationalization (i18n) using `gettext`.

## Features

*   **Cookie-based Locale Detection**: Detects locale from cookies.
*   **Gettext Translation Support**: Integrates with `gettext` for message translation.
*   **API Endpoints**: Provides endpoints to set the locale and retrieve translations.
*   **Middleware Integration**: Seamlessly integrates with FastAPI's middleware to set translation functions on `request.state`.

## Installation

```bash
pip install fastapi-i18n-plugin
```

## Usage

### 1. Prepare Translation Files (Gettext .po and .mo files)

This plugin uses `gettext` for translations, which typically involves `.po` (Portable Object) and `.mo` (Machine Object) files.

1.  **Create a `locales` directory** in your project root.
2.  **Create a domain directory** (e.g., `en`, `zh_TW`) inside `locales` for each supported language.
3.  **Inside each language directory, create `LC_MESSAGES` directory.**
4.  **Inside `LC_MESSAGES`, create a `.po` file** (e.g., `messages.po`).

**Example `locales/en/LC_MESSAGES/messages.po`**:

```po
msgid ""
msgstr ""
"Project-Id-Version: 0.1.0\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=utf-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Language: en\n"

msgid "hello"
msgstr "Hello"

msgid "welcome"
msgstr "Welcome to our application!"
```

**Example `locales/zh_TW/LC_MESSAGES/messages.po`**:

```po
msgid ""
msgstr ""
"Project-Id-Version: 0.1.0\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=utf-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Language: zh_TW\n"

msgid "hello"
msgstr "哈囉"

msgid "welcome"
msgstr "歡迎使用我們的應用程式！"
```

5.  **Compile `.po` files to `.mo` files**: Use the `msgfmt` command-line tool (part of `gettext` utilities) to compile your `.po` files into `.mo` files.

    ```bash
    msgfmt -o locales/en/LC_MESSAGES/messages.mo locales/en/LC_MESSAGES/messages.po
    msgfmt -o locales/zh_TW/LC_MESSAGES/messages.mo locales/zh_TW/LC_MESSAGES/messages.po
    ```

### 2. Basic Setup in FastAPI

```python
from fastapi import FastAPI, Request
from fastapi_i18n_plugin import FastAPIi18n
from pathlib import Path
from starlette.templating import Jinja2Templates # Assuming you use Jinja2 for templates

app = FastAPI()

# Initialize Jinja2Templates (if used)
templates = Jinja2Templates(directory="templates")
app.state.jinja_env = templates.env # Expose jinja_env for middleware

# Configure and initialize the i18n plugin
# Note: localedir should point to the directory containing your language directories (e.g., 'en', 'zh_TW')
i18n_instance = FastAPIi18n(
    localedir=Path("./locales"),
    supported_locales=["en", "zh_TW"],
    default_locale="en",
)
i18n_instance.init_app(app)

# Example routes
@app.get("/")
async def read_root(request: Request):
    # Access the translation function via request.state._
    _ = request.state._
    return {"message": _("welcome")}

@app.get("/hello")
async def read_hello(request: Request):
    _ = request.state._
    return {"message": _("hello")}

# To run this example:
# 1. Save the code above as main.py
# 2. Prepare your locales directory with .po and .mo files as described above.
# 3. Run: uvicorn main:app --reload
# 4. Test in your browser:
#    - http://localhost:8000/             (should show "Welcome to our application!")
#    - http://localhost:8000/hello        (should show "Hello")
#
# To change locale, use the provided API endpoint or manually set the 'locale' cookie:
#    - http://localhost:8000/api/set-language/zh_TW (sets cookie, then refresh / or /hello)
#    - Refresh http://localhost:8000/             (should show "歡迎使用我們的應用程式！")
```

## API Endpoints Provided by the Plugin

The `FastAPIi18n` plugin automatically adds the following API endpoints:

*   **`GET /api/set-language/{locale}`**: Sets the `locale` cookie for the client.
    *   Example: `/api/set-language/zh_TW`
*   **`GET /api/translations/{locale}`**: Returns a JSON object of all translations for the specified locale.
    *   Example: `/api/translations/en`

## Configuration Parameters for `FastAPIi18n`

| Parameter         | Type          | Default   | Description                                                                 |
| :---------------- | :------------ | :-------- | :-------------------------------------------------------------------------- |
| `localedir`       | `Path`        | (Required) | Path to the directory containing your language directories (e.g., `locales/en/LC_MESSAGES/messages.mo`). |
| `supported_locales` | `list[str]`   | (Required) | A list of supported locale codes (e.g., `["en", "zh_TW"]`).             |
| `default_locale`  | `str`         | (Required) | The default locale to use if no other locale is detected.                   |

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.