# Brand system — Indiquant

## Hierarchy

```
Thugir Group
 └── Money Radar  (https://moneyradar.in)   ← parent brand / platform
      └── Indiquant                         ← this open-source research OS
```

GitHub ships under the personal account: **`ryaneditraj/indiquant`**.

Never present Indiquant as unrelated to Money Radar. Always attribute Thugir Group as builder.

## Why “Indiquant”

Chosen for GitHub discoverability:

- Signals **India + quantitative finance** in one word
- Avoids collisions (`sonar` → SonarQube, `quant-os` → generic)
- Short, brandable, topic-friendly (`indiquant`, `nse`, `bse`)

## Naming

| Use | Form |
|-----|------|
| Product | **Indiquant** |
| Repo | [`ryaneditraj/indiquant`](https://github.com/ryaneditraj/indiquant) |
| Full lockup | Indiquant by Money Radar |
| Domain parent | moneyradar.in |
| Product path | moneyradar.in/indiquant |

## Voice

- Precise, confident, zero hype
- “Scan”, “prove”, “reject”, “evidence”
- Never claim guaranteed returns
- Always non-commercial unless separately licensed

## Visual

| Token | Hex | Role |
|-------|-----|------|
| Canvas | `#030712` | Radar night |
| Accent | `#3dff9a` | Ping / edge found |
| Radar cyan | `#22d3ee` | Parent / secondary |
| Ink | `#e8eefc` | Primary text |

Typography: **Fraunces** (display) · **Sora** (UI) · **IBM Plex Mono** (ids)

Mark: concentric radar rings + sweep blip.

## Config

```yaml
app:
  name: "Indiquant"
  parent_brand: "Money Radar"
  parent_url: "https://moneyradar.in"
  organization: "Thugir Group"
  github_url: "https://github.com/ryaneditraj/indiquant"
```
