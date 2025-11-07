---
name: 'bmad-help'
description: 'Get help with BMAD framework and available commands'
---

# BMAD Framework Help

BMAD-METHOD v6.0.0-alpha.7 is installed in this project.

## Available Slash Commands

### Main Agents
- `/bmad-master` - Load the main orchestrator (recommended starting point)
- `/bmad-builder` - Load the builder agent for creating custom agents/workflows

### Quick Access Workflows
- `/brainstorm` - Start a brainstorming session
- `/party-mode` - Enable multi-agent collaboration mode
- `/create-agent` - Create a new custom agent
- `/create-workflow` - Create a new workflow

## How to Use BMAD

### Method 1: Load an Agent (Recommended)
```
/bmad-master
```
This loads the main orchestrator who will:
1. Greet you by name (Diego)
2. Show available workflows
3. Wait for your selection

### Method 2: Access Nested Commands
Browse the installed agents and workflows:
- Core agents: `.claude/commands/core/agents/`
- BMB workflows: `.claude/commands/bmb/workflows/`

## Project Configuration
- User name: Diego
- Output folder: /Users/diego/Desktop/ZillowScrapper/docs
- Configuration files: `bmad/core/config.yaml`, `bmad/bmb/config.yaml`

## Documentation
- Setup guide: `BMAD_SETUP.md` in project root
- Full docs: `bmad/bmm/docs/`
- Online: https://github.com/bmad-code-org/BMAD-METHOD

## Modules Installed
- **Core** - Framework foundation
- **BMM** - BMad Method (agile development)
- **BMB** - BMad Builder (create custom tools)
- **CIS** - Creative Intelligence Suite

## Getting Started
1. Try `/bmad-master` to explore available workflows
2. Use `/brainstorm` if you want to generate ideas
3. Use `/bmad-builder` if you want to create custom agents

For more help, see BMAD_SETUP.md in your project root.
