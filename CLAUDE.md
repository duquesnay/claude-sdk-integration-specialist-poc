# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Project Overview

**POC pour migration integration-specialist vers Claude Agent SDK**

**Objectif**: Remplacer l'agent Markdown `@integration-specialist` existant par un custom tool SDK qui enforce automatiquement les limites de scope.

**Contexte historique**: Learning 2025-01-22 documente un incident où `@integration-specialist` a modifié des fichiers infrastructure (Dockerfile) en résolvant un problème CSS - comportement "Bulldozer Systémique". Les limites de scope actuelles (≤5 files local, 6-10 confirmation, >10 plan) sont dans le prompt mais non enforced.

**Hypothèse**: Le SDK peut bloquer programmatiquement les dépassements de scope via exceptions Python.

## État actuel du projet

**Status**: Setup initial uniquement
- ✅ Virtual environment créé
- ✅ Documentation de référence établie
- ❌ Code d'implémentation pas encore créé

## Ce que tu dois savoir sur Claude Agent SDK

### Architecture SDK: Gather-Act-Verify

Le SDK structure les agents en 3 phases:
1. **Gather Context**: Collecte d'information (search, subagents, compaction)
2. **Take Action**: Exécution (custom tools, bash, code gen, MCP)
3. **Verify Work**: Validation (règles, feedback, judging)

### Custom Tools: Concept clé

Les custom tools sont des **fonctions Python** qui deviennent des outils utilisables par Claude:

```python
from claude_agent_sdk import custom_tool

@custom_tool
def analyze_integration_scope(files: list[str], description: str) -> dict:
    """Analyse si changements respectent limites de scope"""
    if len(files) > 10:
        raise ScopeViolationError("Max 10 files exceeded")

    # Analyse et retour
    return {
        "approved": True,
        "scope_level": "LOCAL",  # LOCAL/MODERATE/EXTENSIVE
        "warnings": []
    }
```

**Différence critique vs agents Markdown**:
- Markdown: Instructions interprétées par Claude (non enforced)
- SDK tool: Exceptions Python bloquantes (enforced)

### Installation

```bash
pip install claude-agent-sdk
```

**Note importante**: Le SDK est très récent (janvier 2025), il n'est PAS dans le training data de Claude. Référence la documentation officielle si besoin:
- Docs: https://docs.claude.com/en/docs/claude-code/sdk/sdk-overview
- GitHub: https://github.com/anthropics/claude-agent-sdk-python
- Blog: https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk

## Objectifs du POC

### Validation #1: Scope control automatique
Créer un custom tool qui:
- Accepte automatiquement ≤5 fichiers
- Warn sur 6-10 fichiers
- **Bloque via exception** >10 fichiers

### Validation #2: Anti-pattern detection
Détecter et signaler:
1. Infrastructure files (Dockerfile, docker-compose, etc.) pour problèmes UI/CSS
2. Changements dans >3 modules non-reliés
3. Abstractions complexes pour fixes simples

### Validation #3: Cas historique
Le tool doit **bloquer** le scénario 2025-01-22 (Dockerfile modifié pour CSS).

## Architecture cible (à implémenter)

```
integration_specialist_tool.py    # Custom tool SDK
examples/
  test_scope_control.py          # Tests de validation
requirements.txt                 # Dependencies
```

### Implémentation suggérée

**Scope levels**:
- LOCAL: 1-3 fichiers → auto-approve
- MODERATE: 4-5 fichiers → approve avec warning
- EXTENSIVE: 6-10 fichiers → approve avec confirmation requise
- SYSTEMIC: >10 fichiers → **BLOCK via exception**

**Anti-patterns à détecter**:
```python
INFRASTRUCTURE_FILES = ['Dockerfile', 'docker-compose.yml', 'nginx.conf',
                        '.k8s/', 'terraform/', '.github/workflows/']

def detect_anti_patterns(files: list[str], description: str) -> list[str]:
    warnings = []

    # Check 1: Infrastructure pour UI issue
    if any('ui' in desc.lower() or 'css' in desc.lower()
           for desc in [description]):
        if any(infra in f for f in files for infra in INFRASTRUCTURE_FILES):
            warnings.append("Infrastructure files modified for UI issue!")

    # Check 2: Modules non-reliés
    top_dirs = set(f.split('/')[0] for f in files)
    if len(top_dirs) > 3:
        warnings.append(f"Changes span {len(top_dirs)} unrelated modules")

    return warnings
```

## Commandes de développement

### Setup
```bash
python -m venv venv
source venv/bin/activate
pip install claude-agent-sdk anthropic pytest
```

### Tests
```bash
python examples/test_scope_control.py
```

## Métriques de succès

Le POC est validé si:
- [ ] Custom tool créé et fonctionnel
- [ ] Exception levée pour >10 fichiers
- [ ] Warning émis pour 6-10 fichiers
- [ ] Anti-pattern infrastructure+UI détecté
- [ ] Cas historique (Dockerfile pour CSS) serait bloqué

## ROI attendu

**Baseline actuel** (agent Markdown):
- 2-3 incidents scope creep/semaine
- ~4h/incident de cleanup
- Coût: 8-12h/semaine

**Avec SDK tool**:
- Incidents bloqués automatiquement
- Réduction estimée: 80%+ des incidents

## Prochaines étapes après POC réussi

1. **Phase 1**: Migration agent production
   - Remplacer `~/.claude/agents/integration-specialist.md`
   - Déployer comme custom tool dans workflows

2. **Phase 2**: Autres agents
   - Migrer `@refactoring-specialist`, `@solution-architect`
   - Pattern réutilisable établi

3. **Phase 3**: Distribution (optionnel)
   - Package pip `guillaume-claude-agents`
   - Open source patterns

## Anti-patterns à éviter

### ❌ Ne PAS faire
- Créer un MCP server (overkill pour ce POC)
- Over-engineer avec orchestration complexe
- Implémenter tous les agents d'un coup

### ✅ FAIRE
- POC simple et focalisé
- Custom tool unique pour integration-specialist
- Tests directs du scope control
- Validation sur cas historique réel

## Références

- Documentation SDK officielle: https://docs.claude.com/en/docs/claude-code/sdk/sdk-overview
- Learning 2025-01-22: `~/.claude-memories/CLAUDE.md` (Integration-Specialist Scope Control)
- Agent actuel: `~/.claude/agents/integration-specialist.md`
- Opportunités complètes: `~/ObsidianNotes/Code/AI/Claude Agent SDK - Opportunities.md`