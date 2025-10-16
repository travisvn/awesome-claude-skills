# Awesome Claude Skills [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

> A curated list of awesome Claude Skills, resources, and tools for customizing Claude AI workflows

Claude Skills are specialized folders containing instructions, scripts, and resources that enhance Claude's performance on specific tasks. Announced on October 16, 2025, Skills are composable, portable, efficient, and powerful.

## Contents

- [Official Resources](#official-resources)
- [Documentation](#documentation)
- [Official Skills](#official-skills)
  - [Document Skills](#document-skills)
  - [Design & Creative](#design--creative)
  - [Development](#development)
  - [Communication](#communication)
- [Community Skills](#community-skills)
- [Tools & Utilities](#tools--utilities)
- [Tutorials & Guides](#tutorials--guides)
- [Articles & Blog Posts](#articles--blog-posts)
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

## Community Skills

- [simonw/claude-skills](https://github.com/simonw/claude-skills) - Extracted contents of `/mnt/skills` from Claude's code interpreter environment

_More community skills coming soon! Submit a PR to add your skill._

## Tools & Utilities

- **Claude Code** - Use Skills through the `anthropics/skills` marketplace
- **Claude API** - Access Skills programmatically via the `/v1/skills` endpoint
- **Claude Agent SDK** - Build custom agents that leverage Skills

## Tutorials & Guides

### Creating Skills

Skills are simple to create:

- Create a folder with a `SKILL.md` file
- Add YAML frontmatter with metadata
- Write clear instructions for Claude
- Optionally include executable scripts and resources

### Example Skill Structure

```
my-skill/
├── SKILL.md          # Main skill file with frontmatter and instructions
├── scripts/          # Optional executable scripts
└── resources/        # Optional supporting files
```

### Guides

- [Classification Skill Guide](https://github.com/anthropics/anthropic-cookbook/blob/main/skills/classification/guide.ipynb) - Tutorial on creating classification skills
- [Contextual Embeddings](https://github.com/anthropics/anthropic-cookbook/tree/main/skills/contextual-embeddings) - Using Skills with embeddings

## Articles & Blog Posts

- [Claude Skills Unlocks Enterprise-Grade AI Customization](https://www.startuphub.ai/ai-news/ai-video/2025/claude-skills-unlocks-enterprise-grade-ai-customization/) - Analysis of enterprise use cases
- [Claude just got customizable 'Skills'](https://www.tomsguide.com/ai/claude-just-got-customizable-skills-heres-how-they-could-supercharge-your-workflow) - Tom's Guide overview
- [Simon Willison: Claude Skills](https://simonwillison.net/2025/Oct/10/claude-skills/) - Technical deep dive and skill extraction
- [How Anthropic's 'Skills' make Claude faster, cheaper, and more consistent](https://venturebeat.com/ai/how-anthropics-skills-make-claude-faster-cheaper-and-more-consistent-for) - VentureBeat analysis
- [Skills for Claude!](https://blog.fsck.com/2025/10/16/skills-for-claude/) - Community perspective

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
