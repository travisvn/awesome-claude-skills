<p align="center">
  <a href="https://github.com/travisvn/awesome-claude-skills">
    <img alt="Awesome Claude Skills" src="https://pc0o4oduww.ufs.sh/f/crfz5GypRfo0lI4924gMSJKLY6297aVP0zZpilXBvqTbDyrs"/>
  </a>
</p>

# Awesome Claude Skills

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
[![Last Updated](https://img.shields.io/badge/updated-Oct%202025-green.svg)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![License](https://img.shields.io/badge/license-CC0--1.0-blue.svg)](LICENSE)

> A curated list of awesome Claude Skills, resources, and tools for customizing Claude AI workflows

Claude Skills are specialized folders containing instructions, scripts, and resources that enhance Claude's performance on specific tasks. Announced on October 16, 2025, Skills are composable, portable, efficient, and powerful.

## Contents

- [Official Resources](#official-resources)
- [Quick Start](#quick-start)
- [Recent Updates](#recent-updates)
- [Documentation](#documentation)
- [Official Skills](#official-skills)
  - [Document Skills](#document-skills)
  - [Design & Creative](#design--creative)
  - [Development](#development)
  - [Communication](#communication)
  - [Skill Creation](#skill-creation)
- [Community Skills](#community-skills)
- [Installation & Setup](#installation--setup)
- [Creating Your First Skill](#creating-your-first-skill)
- [Skills vs Other Approaches](#skills-vs-other-approaches)
- [Tools & Utilities](#tools--utilities)
- [Tutorials & Guides](#tutorials--guides)
- [Videos & Tutorials](#videos--tutorials)
- [Articles & Blog Posts](#articles--blog-posts)
- [Community](#community)
- [Security & Best Practices](#security--best-practices)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)
- [Key Features](#key-features)
- [Availability](#availability)
- [Use Cases](#use-cases)
- [Contributing](#contributing)

## Official Resources

- [Claude Skills Announcement](https://www.anthropic.com/news/skills) - Official announcement from Anthropic
- [anthropics/skills](https://github.com/anthropics/skills) - Official public repository for Skills
- [Claude Developer Platform](https://docs.claude.com/) - Official documentation
- [Skills API Endpoint](https://docs.claude.com/en/api/skills) - `/v1/skills` API documentation

## Quick Start

### Claude Code

```bash
/plugin marketplace add anthropics/skills
```

### Claude Desktop

[Enable Skills here](https://claude.ai/settings/capabilities)

## Recent Updates

### October 2025

- **Oct 18**: Linux path bug reported in Agent SDK ([#268](https://github.com/anthropics/claude-agent-sdk-python/issues/268))
- **Oct 16**: 🎉 **Claude Skills officially announced** - Available across Claude.ai, Code, and API
- **Oct 16**: Initial skills released including docx, pdf, pptx, xlsx, algorithmic-art, canvas-design, and more

## Documentation

- [Skills Overview](https://www.anthropic.com/news/skills) - Introduction to Claude Skills
- [Equipping Agents with Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) - Engineering blog post on Agent Skills
- [Claude Cookbooks - Skills](https://github.com/anthropics/claude-cookbooks/tree/main/skills) - Example notebooks and tutorials
- [Anthropic Cookbook - Skills](https://github.com/anthropics/anthropic-cookbook/tree/main/skills) - Additional skill examples and guides

## Official Skills

### Document Skills

Skills for working with complex file formats:

- **[docx](https://github.com/anthropics/skills/tree/main/document-skills/docx)** - Create, edit, and analyze Word documents with support for tracked changes, comments, formatting preservation, and text extraction
- **[pdf](https://github.com/anthropics/skills/tree/main/document-skills/pdf)** - Comprehensive PDF manipulation toolkit for extracting text and tables, creating new PDFs, merging/splitting documents, and handling forms
- **[pptx](https://github.com/anthropics/skills/tree/main/document-skills/pptx)** - Create, edit, and analyze PowerPoint presentations with support for layouts, templates, charts, and automated slide generation
- **[xlsx](https://github.com/anthropics/skills/tree/main/document-skills/xlsx)** - Create, edit, and analyze Excel spreadsheets with support for formulas, formatting, data analysis, and visualization

### Design & Creative

- **[algorithmic-art](https://github.com/anthropics/skills/tree/main/algorithmic-art)** - Create generative art using p5.js with seeded randomness, flow fields, and particle systems
- **[canvas-design](https://github.com/anthropics/skills/tree/main/canvas-design)** - Design beautiful visual art in .png and .pdf formats using design philosophies
- **[slack-gif-creator](https://github.com/anthropics/skills/tree/main/slack-gif-creator)** - Create animated GIFs optimized for Slack's size constraints

### Development

- **[artifacts-builder](https://github.com/anthropics/skills/tree/main/artifacts-builder)** - Build complex claude.ai HTML artifacts using React, Tailwind CSS, and shadcn/ui components
- **[mcp-server](https://github.com/anthropics/skills/tree/main/mcp-server)** - Guide for creating high-quality MCP servers to integrate external APIs and services
- **[webapp-testing](https://github.com/anthropics/skills/tree/main/webapp-testing)** - Test local web applications using Playwright for UI verification and debugging

### Communication

- **[brand-guidelines](https://github.com/anthropics/skills/tree/main/brand-guidelines)** - Apply Anthropic's official brand colors and typography to artifacts
- **[internal-comms](https://github.com/anthropics/skills/tree/main/internal-comms)** - Write internal communications like status reports, newsletters, and FAQs

### Skill Creation

- **[skill-creator](https://github.com/anthropics/skills/tree/main/skill-creator)** - Interactive skill creation tool that guides you through building new skills with Q&A

## Community Skills

- [simonw/claude-skills](https://github.com/simonw/claude-skills) - Extracted contents of `/mnt/skills` from Claude's code interpreter environment

_More community skills coming soon! Submit a PR to add your skill._

## Installation & Setup

### Claude.ai Web Interface

1. Go to [Settings > Capabilities](https://claude.ai/settings/capabilities)
2. Enable Skills toggle
3. Browse available skills or upload custom skills
4. **For Team/Enterprise**: Admin must enable Skills organization-wide first

### Claude Code CLI

```bash
# Install skills from marketplace
/plugin marketplace add anthropics/skills

# Or install from local directory
/plugin add /path/to/skill-directory
```

### Claude API

Skills are accessible via the `/v1/skills` API endpoint. See the [Skills API documentation](https://docs.claude.com/en/api/skills) for detailed integration examples.

```python
import anthropic

client = anthropic.Client(api_key="your-api-key")
# See API docs for full implementation details
```

## Creating Your First Skill

### Method 1: Use skill-creator (Recommended)

The easiest way to create a skill is to use the built-in `skill-creator`:

1. Enable the skill-creator skill in Claude
2. Ask Claude: "Use the skill-creator to help me build a skill for [your task]"
3. Answer the interactive questions about your workflow
4. Claude generates the complete skill structure for you

### Method 2: Manual Creation

1. **Create folder structure**:
   ```
   my-skill/
   ├── SKILL.md          # Main skill file with frontmatter
   ├── scripts/          # Optional executable scripts
   │   └── helper.py
   └── resources/        # Optional supporting files
       └── template.json
   ```

2. **Create SKILL.md with frontmatter**:
   ```yaml
   ---
   name: my-skill
   description: Brief description for skill discovery (keep concise)
   ---

   # Detailed Instructions

   Claude will read these instructions when the skill is activated.

   ## Usage
   Explain how to use this skill...

   ## Examples
   Provide clear examples...
   ```

3. **Add executable scripts** (optional):
   - Python, JavaScript, or other scripts Claude can execute
   - Reference them in your SKILL.md instructions

4. **Test locally**:
   - Install the skill in Claude Code or Claude Desktop
   - Test with relevant tasks
   - Iterate and refine

5. **Share**:
   - Publish to GitHub
   - Submit to this awesome list via PR
   - Share with your team via git repos or internal distribution

### Best Practices

- **Keep descriptions concise** - The frontmatter description is used for skill discovery
- **Use clear, actionable instructions** - Write instructions as if for a human collaborator
- **Include examples** - Show specific examples in your SKILL.md
- **Version your skills** - Use git tags for version management
- **Document dependencies** - List any prerequisites or required packages
- **Test thoroughly** - Verify your skill works across different scenarios

## Skills vs Other Approaches

### Skills vs MCP (Model Context Protocol)

| Feature | Skills | MCP |
|---------|--------|-----|
| **Purpose** | Task-specific expertise and workflows | External data/API integration |
| **Portability** | Same format everywhere (Claude.ai, Code, API) | Requires server configuration |
| **Code Execution** | Can include executable scripts | Provides tools/resources |
| **Token Efficiency** | 30-50 tokens until loaded | Varies by implementation |
| **Best For** | Repeatable tasks, document workflows | Database access, API integrations |

**Use Together**: Skills can create MCP servers! The `mcp-server` skill helps build high-quality MCP integrations.

### Skills vs System Prompts

| Feature | Skills | System Prompts |
|---------|--------|----------------|
| **Structure** | Folder with YAML frontmatter, instructions, scripts | Plain text instructions |
| **Reusability** | Version-controlled, shareable, composable | Copy-paste, conversation-specific |
| **Loading** | On-demand (only when relevant) | Always in context |
| **Maintenance** | Centralized updates | Manual updates per conversation |
| **Composability** | Multiple skills stack automatically | Manual combination |

**Key Advantage**: Skills are loaded on-demand, consuming only 30-50 tokens until needed, keeping Claude fast while providing specialized expertise.

## Tools & Utilities

- **Claude Code** - Use Skills through the `anthropics/skills` marketplace
- **Claude API** - Access Skills programmatically via the `/v1/skills` endpoint
- **Claude Agent SDK** - Build custom agents that leverage Skills

## Tutorials & Guides

- [Classification Skill Guide](https://github.com/anthropics/anthropic-cookbook/blob/main/skills/classification/guide.ipynb) - Tutorial on creating classification skills
- [Contextual Embeddings](https://github.com/anthropics/anthropic-cookbook/tree/main/skills/contextual-embeddings) - Using Skills with embeddings
- [How to Create Your First Claude Skill](https://skywork.ai/blog/ai-agent/how-to-create-claude-skill-step-by-step-guide/) - Step-by-step tutorial with examples

## Videos & Tutorials

_Video tutorials coming soon! Have a good video about Claude Skills? Submit a PR!_

Example topics we'd love to see:
- Getting started with Claude Skills
- Building your first custom skill
- Skills vs MCP comparison
- Enterprise deployment strategies

## Articles & Blog Posts

- [Claude Skills Unlocks Enterprise-Grade AI Customization](https://www.startuphub.ai/ai-news/ai-video/2025/claude-skills-unlocks-enterprise-grade-ai-customization/) - Analysis of enterprise use cases
- [Claude just got customizable 'Skills'](https://www.tomsguide.com/ai/claude-just-got-customizable-skills-heres-how-they-could-supercharge-your-workflow) - Tom's Guide overview
- [Simon Willison: Claude Skills](https://simonwillison.net/2025/Oct/10/claude-skills/) - Technical deep dive and skill extraction
- [How Anthropic's 'Skills' make Claude faster, cheaper, and more consistent](https://venturebeat.com/ai/how-anthropics-skills-make-claude-faster-cheaper-and-more-consistent-for) - VentureBeat analysis
- [Skills for Claude!](https://blog.fsck.com/2025/10/16/skills-for-claude/) - Community perspective

## Community

### Discussions

- [Hacker News Discussion](https://news.ycombinator.com/item?id=45607117) - Community reactions and insights on the Skills announcement
- [GitHub Discussions](https://github.com/anthropics/skills/discussions) - Official discussions on the anthropics/skills repository

### Featured Community Skills

Curated list of high-quality community contributions:

- [simonw/claude-skills](https://github.com/simonw/claude-skills) - Extracted contents of `/mnt/skills` from Claude's code interpreter environment

_Have you built an awesome skill? Submit a PR to showcase it here!_

### Skill Ideas & Requests

Looking for inspiration or want to request a skill?

- Browse [skill request issues](https://github.com/travisvn/awesome-claude-skills/labels/skill-request)
- Submit your own skill idea
- Collaborate with other developers

## Security & Best Practices

### Vetting Skills

⚠️ **Important**: Skills can execute arbitrary code in Claude's environment.

- **Only install skills from trusted sources**
- **Review SKILL.md and all scripts** before enabling a skill
- **Be cautious of skills** that request sensitive data access
- **Audit carefully** before deploying to production or enterprise environments

### Security Concerns

- **Malicious skills** may introduce vulnerabilities or enable data exfiltration
- **Prompt injection attacks** could be amplified through compromised skills
- **Sandboxing limitations** - Understand the security model before enterprise deployment

### Best Practices

- **Version control** - Track all skills in git with proper version tags
- **Code review** - Peer review custom skills before team distribution
- **Least privilege** - Only grant necessary permissions and access
- **Regular audits** - Periodically review installed skills
- **Documentation** - Maintain clear documentation for custom skills
- **Testing** - Thoroughly test skills in non-production environments first

### Enterprise Considerations

- As of October 2025, Claude.ai does not support centralized admin management for custom skills
- Use version control and internal repositories for team skill distribution
- Establish clear policies for skill vetting and approval
- Monitor skill usage and performance

## Troubleshooting

### Known Issues

- **Linux path bug (Oct 18, 2025)**: Agent SDK uses hardcoded macOS paths instead of environment home directory
  - [Issue #268](https://github.com/anthropics/claude-agent-sdk-python/issues/268)
  - Workaround: Manually specify skill paths

- **Enterprise distribution**: No centralized admin management yet for custom skills on claude.ai
  - Use git repositories for team distribution
  - API integration provides more control

### Common Problems

**Skills not appearing in Claude**
- Check Settings > Capabilities to ensure Skills are enabled
- For Team/Enterprise: Verify admin has enabled Skills organization-wide
- Restart Claude after installing new skills

**Skills not loading/activating**
- Verify SKILL.md has proper YAML frontmatter format
- Check that `name` and `description` fields are present
- Ensure file structure matches expected format

**Permission errors**
- Review admin settings for Team/Enterprise accounts
- Check file permissions in skill directories
- Verify API key has appropriate permissions

**Skill execution failures**
- Check script dependencies are installed
- Review error logs for specific issues
- Test scripts independently outside of Claude

### Getting Help

- [Official Skills Repository Issues](https://github.com/anthropics/skills/issues)
- [Claude Documentation](https://docs.claude.com/)
- [Community Discussions](https://github.com/anthropics/skills/discussions)

## FAQ

**Q: How much do skills impact token usage?**

A: Skills are highly efficient. Each skill only uses 30-50 tokens until it's loaded. The full skill content only loads when Claude determines it's relevant to the task.

**Q: Can I share skills with my team?**

A: Yes! Skills can be shared via:
- Git repositories (recommended)
- Internal file sharing
- Claude API for programmatic distribution
- Enterprise-wide deployment features (coming soon)

**Q: Do skills work with all Claude models?**

A: Skills are available for Pro, Max, Team, and Enterprise users. Free tier users do not have access to Skills.

**Q: Can skills call external APIs?**

A: Yes, skills can include scripts that call external APIs. For complex API integrations, consider using MCP (Model Context Protocol) alongside skills.

**Q: How does Claude decide which skill to use?**

A: Claude scans all available skills' frontmatter (name and description), evaluates relevance to the current task, then loads the full content of relevant skills. Multiple skills can be loaded and composed together automatically.

**Q: Can I use Skills and MCP together?**

A: Absolutely! They complement each other. Use Skills for task-specific workflows and MCP for external data/API integration. The `mcp-server` skill can even help you build MCP servers.

**Q: Are there any costs beyond my Claude subscription?**

A: No additional costs for using official skills. Community and custom skills are free to use, though some may require external services (APIs, databases, etc.) that have their own costs.

**Q: Can I monetize custom skills?**

A: Currently, there is no official marketplace for paid skills. Anthropic has mentioned plans for community contributions and a potential marketplace in the future.

**Q: How do I update a skill?**

A: For skills from git repositories, pull the latest changes. For manually installed skills, replace the skill folder with the updated version. Always test updates in a non-production environment first.

## Key Features

### Composable

Skills stack together automatically. Claude identifies which skills are needed and coordinates their use without manual intervention.

### Portable

Skills use the same format everywhere. Build once, use across:

- Claude.ai web interface
- Claude Code CLI
- Claude API integrations
- Custom agents via SDK

### Efficient

Claude only loads what's needed, when it's needed. Skills don't slow down Claude - they enhance it with on-demand expertise.

### Powerful

Skills can include executable code for tasks where traditional programming is more reliable than token generation.

## Availability

Skills are available to:

- Pro users
- Max users
- Team users (admin must enable)
- Enterprise users (admin must enable)

## Use Cases

- Formatting Excel formulas and spreadsheets
- Applying company branding to PowerPoint decks
- Following legal policies when reviewing contracts
- Creating specialized document workflows
- Building custom API integrations via MCP
- Testing web applications automatically
- Generating consistent internal communications
- Creating branded visual content

## Contributing

Contributions are welcome! Please read the [contribution guidelines](CONTRIBUTING.md) first.

To add a new skill or resource:

1. Fork this repository
2. Add your item to the appropriate section
3. Submit a pull request

Please ensure your contribution:

- Follows the existing format
- Includes a clear description
- Links to the relevant resource
- Is related to Claude Skills
