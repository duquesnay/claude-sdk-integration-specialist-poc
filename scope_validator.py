"""
Integration Specialist Scope Validator - Pure Python (no SDK dependencies)

Validation programmatique des limites de scope pour prévenir le scope creep.
Utilisable sans abonnement Claude - juste de la logique Python.

Contexte: Learning 2025-01-22 - incident "Bulldozer Systémique" où l'agent a modifié
des fichiers infrastructure (Dockerfile) pour résoudre un problème CSS.
"""

from typing import Dict, List


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


def analyze_scope(files: List[str], description: str) -> Dict:
    """
    Analyse si les changements proposés respectent les limites de scope.

    Limites enforced:
    - LOCAL (1-3 fichiers): Auto-approve
    - MODERATE (4-5 fichiers): Approve avec warning
    - EXTENSIVE (6-10 fichiers): Approve avec strong warning
    - SYSTEMIC (>10 fichiers): BLOCKED via exception

    Args:
        files: Liste des fichiers à modifier
        description: Description du changement proposé

    Returns:
        dict avec:
        - approved (bool): Si le changement est approuvé
        - scope_level (str): LOCAL/MODERATE/EXTENSIVE
        - file_count (int): Nombre de fichiers
        - warnings (list): Warnings détectés

    Raises:
        ScopeViolationError: Si >10 fichiers (limite absolue)
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