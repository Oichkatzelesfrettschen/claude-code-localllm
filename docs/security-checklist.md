# Security Review Checklist

- [ ] Denylist paths enforced in routing policy.
- [ ] No secrets or credentials routed to local models.
- [ ] Router config stored outside repo (no secrets committed).
- [ ] Tool-call schema validated (no raw tool execution from untrusted output).
- [ ] Logs redact sensitive paths and tokens.
- [ ] Local model license obligations reviewed.
