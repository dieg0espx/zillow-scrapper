# BMAD Commands Quick Reference

## Main Commands

| Command | Description |
|---------|-------------|
| `/bmad-help` | Get help and see all commands |
| `/bmad-master` | Load main orchestrator agent |
| `/bmad-builder` | Load builder agent (create custom tools) |
| `/brainstorm` | Start brainstorming session |

## File Locations

### Agents
- `.claude/commands/core/agents/bmad-master.md` - Main orchestrator
- `.claude/commands/bmb/agents/bmad-builder.md` - Builder agent

### Core Workflows
- `.claude/commands/core/workflows/party-mode.md` - Multi-agent collaboration
- `.claude/commands/core/workflows/brainstorming.md` - Brainstorming sessions

### Builder Workflows
- `.claude/commands/bmb/workflows/create-agent.md` - Create custom agent
- `.claude/commands/bmb/workflows/create-workflow.md` - Create workflow
- `.claude/commands/bmb/workflows/create-module.md` - Create module
- `.claude/commands/bmb/workflows/edit-agent.md` - Edit agent
- `.claude/commands/bmb/workflows/edit-workflow.md` - Edit workflow
- `.claude/commands/bmb/workflows/audit-workflow.md` - Audit workflow

### Tools
- `.claude/commands/core/tools/shard-doc.md` - Document sharding tool

## Configuration Files

- `bmad/core/config.yaml` - Core configuration (user: Diego)
- `bmad/bmb/config.yaml` - Builder configuration
- `bmad/_cfg/manifest.yaml` - Installation manifest

## BMAD Directory Structure

```
bmad/
├── core/           # Core framework
├── bmm/            # BMad Method (development framework)
├── bmb/            # BMad Builder (create custom tools)
├── cis/            # Creative Intelligence Suite
└── _cfg/           # Configuration and manifests
```

## Quick Tips

1. **Start here:** `/bmad-help` or `/bmad-master`
2. **Need ideas?** Use `/brainstorm`
3. **Create custom tools:** Use `/bmad-builder`
4. **Multi-agent collaboration:** Load party-mode workflow
5. **Full documentation:** See `BMAD_SETUP.md` or `bmad/bmm/docs/`

## Support

- GitHub: https://github.com/bmad-code-org/BMAD-METHOD
- Discord: https://discord.gg/gk8jAdXWmj
- Docs: `bmad/mmm/docs/` or online at GitHub
