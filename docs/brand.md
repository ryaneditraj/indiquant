# Brand system — Sonar

## Hierarchy

```
Thugir Group
 └── Money Radar  (https://moneyradar.in)   ← parent brand / platform
      └── Sonar                             ← this open-source research OS
```

Never present Sonar as unrelated to Money Radar. Always attribute Thugir Group as builder.

## Naming

| Use | Form |
|-----|------|
| Product | **Sonar** |
| Repo (suggested) | `sonar` or `thugir-sonar` |
| Full lockup | Sonar by Money Radar |
| Domain parent | moneyradar.in |
| Product path | moneyradar.in/sonar |

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
  name: "Sonar"
  parent_brand: "Money Radar"
  parent_url: "https://moneyradar.in"
  organization: "Thugir Group"
```
