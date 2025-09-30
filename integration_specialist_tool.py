"""
Integration Specialist Custom Tool - Claude Agent SDK

Ce custom tool remplace l'agent Markdown @integration-specialist par un enforcement
programmatique des limites de scope via exceptions Python.

Contexte: Learning 2025-01-22 - incident "Bulldozer Systémique" où l'agent a modifié
des fichiers infrastructure (Dockerfile) pour résoudre un problème CSS.
"""

from typing import Dict, List
from claude_agent_sdk import tool


class ScopeViolationError(Exception):
    """Exception levée quand les limites de scope sont dépassées."""

    def __init__(self, message: str, file_count: int, max_allowed: int):
        self.file_count = file_count
        self.max_allowed = max_allowed
        super().__init__(message)


# Fichiers infrastructure à surveiller
INFRASTRUCTURE_FILES = [
    'Dockerfile',
    'docker-compose.yml',
    'docker-compose.yaml',
    'nginx.conf',
    '.k8s/',
    'kubernetes/',
    'terraform/',
    '.tf',
    '.github/workflows/',
    'Jenkinsfile',
    '.circleci/',
]


def detect_anti_patterns(files: List[str], description: str) -> List[str]:
    """
    Détecte les anti-patterns documentés dans Learning 2025-01-22.

    Anti-patterns détectés:
    1. Infrastructure files modifiés pour problèmes UI/CSS
    2. Changements dans >3 modules non-reliés
    3. Abstractions complexes pour fixes simples (via description)

    Args:
        files: Liste des fichiers à modifier
        description: Description du changement

    Returns:
        Liste des warnings détectés
    """
    warnings = []

    # Check 1: Infrastructure pour UI issue
    desc_lower = description.lower()
    if any(keyword in desc_lower for keyword in ['ui', 'css', 'style', 'button', 'layout']):
        infra_found = [f for f in files if any(infra in f for infra in INFRASTRUCTURE_FILES)]
        if infra_found:
            warnings.append(
                f"⚠️ ANTI-PATTERN: Infrastructure files modified for UI issue!\n"
                f"   Files: {', '.join(infra_found)}\n"
                f"   Recommendation: Keep infrastructure changes separate from UI fixes"
            )

    # Check 2: Modules non-reliés (>3 top-level directories)
    top_dirs = set()
    for f in files:
        parts = f.split('/')
        if len(parts) > 1:
            top_dirs.add(parts[0])

    if len(top_dirs) > 3:
        warnings.append(
            f"⚠️ ANTI-PATTERN: Changes span {len(top_dirs)} unrelated modules: {', '.join(sorted(top_dirs))}\n"
            f"   Recommendation: Split into focused changes per module"
        )

    # Check 3: Abstractions complexes pour fixes simples
    complexity_keywords = ['factory', 'manager', 'handler', 'builder', 'strategy', 'adapter']
    simple_fix_keywords = ['fix', 'bug', 'typo', 'minor']

    desc_has_complexity = any(kw in desc_lower for kw in complexity_keywords)
    desc_is_simple = any(kw in desc_lower for kw in simple_fix_keywords)

    if desc_has_complexity and desc_is_simple:
        warnings.append(
            f"⚠️ ANTI-PATTERN: Complex abstractions ({[kw for kw in complexity_keywords if kw in desc_lower]}) for simple fix\n"
            f"   Recommendation: Use simplest solution that works"
        )

    return warnings


def _analyze_scope_impl(files: List[str], description: str) -> Dict:
    """
    Implémentation interne de l'analyse de scope.

    Séparée pour permettre tests synchrones tout en ayant un tool async.
    """
    file_count = len(files)

    # Enforcement absolu: >10 fichiers = BLOCKED
    if file_count > 10:
        raise ScopeViolationError(
            f"Scope limit exceeded: {file_count} files requested (max: 10)\n"
            f"Recommendation: Break this change into smaller, focused tasks\n"
            f"Files: {', '.join(files[:5])}{'...' if len(files) > 5 else ''}",
            file_count=file_count,
            max_allowed=10
        )

    # Déterminer scope level
    if file_count <= 3:
        scope_level = "LOCAL"
        scope_message = "✅ Local scope - auto-approved"
    elif file_count <= 5:
        scope_level = "MODERATE"
        scope_message = "⚠️ Moderate scope - approved with caution"
    else:  # 6-10
        scope_level = "EXTENSIVE"
        scope_message = "⚠️ Extensive scope - approaching limit (max 10 files)"

    # Détection anti-patterns
    warnings = detect_anti_patterns(files, description)

    # Warning additionnel si scope élevé
    if scope_level in ["MODERATE", "EXTENSIVE"]:
        warnings.insert(0, scope_message)

    return {
        "approved": True,
        "scope_level": scope_level,
        "file_count": file_count,
        "warnings": warnings,
        "files": files
    }


@tool(
    "analyze_integration_scope",
    "Analyse if proposed changes respect scope limits (max 10 files). Detects anti-patterns like infrastructure files for UI issues.",
    {
        "files": list[str],
        "description": str
    }
)
async def analyze_integration_scope(args: dict) -> dict:
    """
    SDK tool wrapper pour l'analyse de scope.

    Args:
        args: Dict avec 'files' (list) et 'description' (str)

    Returns:
        Dict avec 'content' contenant le résultat
    """
    try:
        result = _analyze_scope_impl(args["files"], args["description"])

        # Format SDK: retourner dict avec 'content'
        return {
            "content": [{
                "type": "text",
                "text": f"Scope analysis complete:\n"
                        f"  - Approved: {result['approved']}\n"
                        f"  - Scope Level: {result['scope_level']}\n"
                        f"  - File Count: {result['file_count']}\n" +
                        ("\n  - Warnings:\n    " + "\n    ".join(result['warnings']) if result['warnings'] else "")
            }],
            "result": result  # Données brutes pour tests
        }
    except ScopeViolationError as e:
        return {
            "content": [{
                "type": "text",
                "text": f"🚫 SCOPE VIOLATION BLOCKED\n\n{str(e)}"
            }],
            "is_error": True,
            "error": {
                "type": "ScopeViolationError",
                "file_count": e.file_count,
                "max_allowed": e.max_allowed
            }
        }


# Export fonction pour tests synchrones
analyze_integration_scope_sync = _analyze_scope_impl


@tool(
    "get_integration_statistics",
    "Get statistics about scope analyses performed",
    {}
)
async def get_integration_statistics(args: dict) -> dict:
    """
    Retourne des statistiques sur les analyses effectuées.

    Note: Dans ce POC, les stats sont mock. En production, utiliser
    un système de persistence (DB, fichier, etc.)
    """
    stats = {
        "total_analyses": 0,
        "average_file_count": 0.0,
        "scope_distribution": {
            "LOCAL": 0,
            "MODERATE": 0,
            "EXTENSIVE": 0,
            "BLOCKED": 0
        },
        "anti_patterns_detected": 0,
        "note": "Statistics tracking not implemented in POC - would require persistence layer"
    }

    return {
        "content": [{
            "type": "text",
            "text": f"Integration Statistics:\n"
                    f"  - Total analyses: {stats['total_analyses']}\n"
                    f"  - Average file count: {stats['average_file_count']}\n"
                    f"  - Scope distribution: {stats['scope_distribution']}\n"
                    f"  - Anti-patterns detected: {stats['anti_patterns_detected']}\n\n"
                    f"Note: {stats['note']}"
        }],
        "stats": stats
    }