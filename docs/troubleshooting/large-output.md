# Large Output Troubleshooting Guide

This guide outlines how to safely inspect or store command output without exceeding the 1600-byte line limit enforced by the Codex terminal. It complements the [AGENTS Guide](../../AGENTS.md#output-safety-and-clw) instructions.

## `clw` Pipeline

1. **Verify installation**
   ```bash
   /usr/local/bin/clw --help
   ```
2. **Set the wrap limit** (recommended 1550 bytes)
   ```bash
   export CLW_MAX_LINE_LENGTH=1550
   ```
3. **Pipe high-volume output through `clw`**
   ```bash
   grep -R "pattern" . | /usr/local/bin/clw
   ```

## Log-Chunk Workflow

1. **Redirect output to a log**
   ```bash
   some_command > /tmp/output.log
   ```
2. **Read the log in chunks**
   ```bash
   head -n 20 /tmp/output.log
   sed -n '21,40p' /tmp/output.log
   tail -n 20 /tmp/output.log
   ```
3. **Clean up when finished**
   ```bash
   rm /tmp/output.log
   ```

## Example Session

```bash
# search repository for TODOs and wrap output
rg TODO | /usr/local/bin/clw

# or log and review in chunks
rg TODO > /tmp/todo.log
head -n 50 /tmp/todo.log
rm /tmp/todo.log
```

For additional requirements and safety checks, see the [AGENTS Guide](../../AGENTS.md#output-safety-and-clw).
