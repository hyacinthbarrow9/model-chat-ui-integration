# Open WebUI model integration

A focused, dated guide for connecting Open WebUI to an OpenAI-compatible model service. It is an independent community note, not Open WebUI documentation and not affiliated with Open WebUI, ArgoLink, or a model vendor. **[ArgoLink](https://argolink.io/gh-model-chat-ui-integration)** is the compatible endpoint example. Last checked: 2026-10-07.

## What Open WebUI actually sends

The current [OpenAI-compatible provider guide](https://docs.openwebui.com/getting-started/quick-start/connect-a-provider/starting-with-openai-compatible/) says to open **Settings → Admin → Connections**, add an OpenAI API connection, supply a URL and key, and optionally add a model allowlist when model discovery is unavailable. The [connection reference](https://github.com/open-webui/docs/blob/main/docs/ecosystem/computer/ai/connect-a-model.md) distinguishes Provider (`OpenAI` or `Anthropic`), API Type (`Chat Completions` or `Responses`), Base URL, API Key, optional Prefix ID, and model list.

That distinction matters: Open WebUI is protocol-centric and currently focuses on Chat Completions, with newer protocol support varying by release. GPT-5.4's current catalog entry uses Responses, while GLM-5.3 and many image-compatible models use Chat Completions or their own route. Do not select a model merely because its name appears in the dropdown; inspect the API type and live model page.

## Add an ArgoLink connection

1. Open **Settings → Admin → Connections → Manage OpenAI API Connections** and click **Add Connection**.
2. Choose Provider `OpenAI`, set URL to `https://argolink.io/v1`, and paste the key into the secret field.
3. Add an explicit Model ID such as `gpt-5.4` if discovery is disabled or the service returns no model list. Verify the ID in [GET /v1/models](https://argolink.io/v1/models).
4. Save, select the connection, and send a minimal prompt. Inspect the request route in the server log before enabling tools or long context.

Use the base URL only. Open WebUI appends the endpoint path. Pasting `https://argolink.io/v1/chat/completions` into a field that appends its own route commonly produces a 404. Conversely, a provider that expects a full endpoint must be configured according to that release's field help.

## Docker compose

`configs/docker-compose.yml` is a secret-safe starting point. It requires the operator to choose a reviewed Open WebUI tag or digest and to supply the key outside the file:

```bash
export OPEN_WEBUI_IMAGE='ghcr.io/open-webui/open-webui:<reviewed-tag-or-digest>'
export OPENAI_API_KEY='replace-me'
export OPENAI_API_BASE_URL='https://argolink.io/v1'
docker compose -f configs/docker-compose.yml up -d
```

Do not use `latest` for a production deployment. Record the selected image digest and Open WebUI release in your change log. Keep `ENABLE_SIGNUP=false` unless the instance is intentionally public and protected by an external identity boundary. The example persists only the application volume; add a backup and access-control plan before operating it for others.

The environment variable path is convenient for a single connection. For multiple providers, use Open WebUI's connection UI and keep each key in the instance secret store. Never export a resolved environment file or workflow containing a real key.

## Model and protocol checks

At the 2026-10-07 check, GPT-5.4 was listed with a 1,050,000-token context, 128,000-token maximum output, and reasoning options `low`, `medium`, `high`, `xhigh`, and `max` (default `medium`). The page's effective rates and long-context rule are dated; read the [GPT-5.4 model page](https://argolink.io/en/models/gpt-5-4) again before publishing a price. A Chat Completions UI cannot be made to support Responses-only fields by renaming them.

For each selected model, record:

- exact model ID and catalog date;
- API type and route actually sent by your Open WebUI release;
- whether `/models` discovery worked or an allowlist was used;
- context, output, tools, images, and reasoning fields taken from the model page;
- timeout, rate-limit, and retry behavior.

## Troubleshooting

| Symptom | Likely cause | Action |
| --- | --- | --- |
| model list empty | discovery disabled, auth error, or `/models` not supported | test the connection; add a verified model allowlist |
| 404 | duplicated `/v1` or endpoint family mismatch | inspect the resolved request URL and API type |
| 400 | unsupported reasoning/tool/body field | compare the body with the model page |
| 401 | bad key or secret not mounted | rotate/check the secret without logging it |
| 429 / 503 | rate limit or capacity | honor `Retry-After`; do not replay a write blindly |
| stream stops early | protocol or proxy buffering issue | capture status, content type, response ID, and client release |

Video generation is an asynchronous submit/status/content contract and is intentionally outside this chat UI guide. Images also have model-specific sizes and output fields; configure them from their own model pages rather than copying chat fields.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

The tests inspect documentation and compose placeholders only. They do not start Docker or send a provider request.
