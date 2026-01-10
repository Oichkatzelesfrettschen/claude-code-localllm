# Operator Runbook

## Start/Stop
```
ccr start
ccr status
ccr stop
```

## Restart After Config Changes
```
ccr restart
```

## Logs
- `~/.claude-code-router/logs/`
- `~/.claude-code-router/claude-code-router.log`

## Backups
```
cp ~/.claude-code-router/config.json ~/.claude-code-router/config.json.bak
```

## Upgrades
```
npm update -g @musistudio/claude-code-router
```

## Health Checks
```
make tool-probe
make probe-suite
make runtime-probe
make vram-probe
```
