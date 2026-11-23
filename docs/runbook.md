# Operating Runbook

## Before the first live run

1. Confirm the sheet has `Raw_SKU_Data`, `Action_Exceptions`, and `System_Run_Log` tabs.
2. Confirm `Raw_SKU_Data` uses the required headers and contains only approved data.
3. Confirm the service-account email has Editor access to the sheet.
4. Confirm the local `.env` values are present and `credentials.json` exists locally.
5. Run `python -m src.main` locally and verify the exception tab and log row.
6. Add GitHub Actions secrets and run the workflow manually once.

## Daily monitoring

1. Check the newest `System_Run_Log` row has `SUCCESS`.
2. Check the GitHub Actions run is green.
3. Review non-healthy rows in `Action_Exceptions` and assign the follow-up action.
4. Track success rate monthly:

```text
success_rate = successful_scheduled_runs / total_scheduled_runs * 100
```

Target: at least 95% successful scheduled runs after the setup period.

## If a run fails

1. Read the latest GitHub Actions log and the `System_Run_Log` notes.
2. Check for changed sheet headers, invalid numeric values, missing secrets, expired credentials, or lost sheet sharing.
3. Correct the cause, then run the workflow manually.
4. Confirm one `SUCCESS` run updates the exception queue and log.
5. Record the root cause and the prevention step in the client handover notes.

## Security checks

- Never paste secrets into GitHub issues, commits, screenshots, or ChatGPT.
- Use GitHub Actions secrets for cloud execution and `.env` only for local execution.
- If a credential is exposed, revoke the service-account key in Google Cloud, create a replacement, update the secret, and remove the exposed material from the repository history.
