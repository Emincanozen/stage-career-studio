# Contributing

Thanks for helping! Rules of the project:

1. **Never commit real personal data** (CVs, photos, contact details, tracker files). Tests use fictional data only.
2. Keep the Python toolkit **dependency-free** (standard library only).
3. Keep the "prepare only" guarantee: nothing may send applications or messages.
4. Run before opening a PR:
   ```bash
   cd skills/stage-career-studio/scripts
   python -m unittest test_stage_studio
   node test_dashboard.cjs
   ```
5. Translations of `SKILL.md` and references are welcome (open an issue first to agree on structure).
