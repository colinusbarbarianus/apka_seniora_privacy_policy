# Threat catalog (remote update source)

These files are the "Nie daj się" / "Wise Guard" app's threat catalog, hosted
here so the list can be updated without publishing a new app version. The app
only fetches this when the user taps "Sprawdź aktualizacje" in Settings — no
automatic/background downloads.

- `threats_pl.json` / `threats_en.json` — same schema as the app's bundled
  `assets/threats/threats_*.json`. Keep `meta.version` bumped and
  `meta.last_updated` current on every change, or the app won't treat it as
  a newer update than what's already installed/bundled.
- `threats_pl.json.sig` / `threats_en.json.sig` — Ed25519 signature (base64)
  over the exact bytes of the matching `.json` file. The app has the public
  key baked in and refuses any file whose signature doesn't check out — so a
  compromised host or a MITM can't feed the app fake "advice".

## Updating the catalog

1. Edit `threats_pl.json` and/or `threats_en.json`, bump `meta.version`.
2. Re-sign (needs the private signing key — see below, never commit it):
   ```
   export THREATS_SIGNING_KEY_B64="<the private key>"
   python3 scripts/sign_threats.py
   ```
3. Commit and push both the `.json` and the regenerated `.json.sig` files.
4. GitHub Pages redeploys automatically — no other step needed.

## The private signing key

Generated once, delivered to Tomek out of band (not in this repo). Store it
in a password manager or the local `.keystores` folder, never in git, never
in chat logs going forward. If it's ever lost, generate a new Ed25519
keypair, update the public key baked into the app
(`app/lib/core/platform/content_trust.dart`), and ship that as a normal app
update — old installs keep working off the bundled catalog until they update.
