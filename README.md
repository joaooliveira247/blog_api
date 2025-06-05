# ✍️ [Blog API Challenge](https://github.com/wesleybertipaglia/backend-challenges/blob/main/challenges/junior/api-blog.md)

## 💻 Requirements:

### [`Docker`](https://www.docker.com/) & [`Docker compose`](https://docs.docker.com/compose/)

### [`UV`](https://docs.astral.sh/uv/)

## Installation & Running:

### Docker

```bash
docker compose up -d
```

### uv

This project uses a package and dependency maganer called uv. [Installation guide](https://docs.astral.sh/uv/getting-started/installation/)

1º step: `uv installation`

```curl
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2º step: `Creating virtual enviroment and activating`

```bash
uv venv
```

```bash
source .venv/bin/activate
```

> **__Note:__**
>
> On Linux and macOS, the commands to install and activate the virtual environment are the same. For Windows, please refer to the official documentation.

3º step: `install all dependencies`

```bash
uv sync --all-groups
```

> **__Warning:__**
>
> Please remember to configure the `.env` file. [.env example file](./.env.example)

## 📜 Documentation:

<details>
    <summary><code>Database Diagram</code></summary>

<img src="https://i.imgur.com/wGU5L0H.png">

</details>

### ▶️ Commands

```bash
uv run main.py update-role <user_id> <role(admin|dev|user)>
```

This command updates a user's role from the CLI. Updating a role via the API is only allowed if your role is admin.

```
uv run main.py run --host=<(optional|default=127.0.0.1)> --port=<(optional|default=8000)>
```

This command starts the API.

## 🐍 Usage libraries:
