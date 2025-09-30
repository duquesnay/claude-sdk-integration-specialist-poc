#!/usr/bin/env python3
"""
Script CLI pour valider le scope avant modifications.

Usage:
    python check_scope.py <file1> <file2> ... -- "description"

Exit codes:
    0: Scope approved
    1: Scope violation (>10 files)
    2: Invalid usage

Example:
    python check_scope.py src/app.css src/theme.css -- "Fix button styling"
"""

import sys
from integration_specialist_tool import (
    analyze_integration_scope_sync,
    ScopeViolationError
)


def main():
    if len(sys.argv) < 3:
        print("Usage: check_scope.py <file1> <file2> ... -- \"description\"", file=sys.stderr)
        print("\nExample:", file=sys.stderr)
        print('  check_scope.py src/a.css src/b.css -- "Fix CSS"', file=sys.stderr)
        sys.exit(2)

    # Parse args: everything before "--" is files, after is description
    try:
        separator_idx = sys.argv.index("--")
        files = sys.argv[1:separator_idx]
        description = " ".join(sys.argv[separator_idx + 1:])
    except ValueError:
        # No separator, assume last arg is description
        files = sys.argv[1:-1]
        description = sys.argv[-1]

    if not files:
        print("Error: No files specified", file=sys.stderr)
        sys.exit(2)

    if not description:
        print("Error: No description provided", file=sys.stderr)
        sys.exit(2)

    # Analyze scope
    try:
        result = analyze_integration_scope_sync(files, description)

        # Print result
        print(f"\n{'='*80}")
        print(f"SCOPE ANALYSIS")
        print(f"{'='*80}")
        print(f"Status: ✅ APPROVED")
        print(f"Scope Level: {result['scope_level']}")
        print(f"File Count: {result['file_count']}/{10}")

        if result['warnings']:
            print(f"\n⚠️  WARNINGS:")
            for warning in result['warnings']:
                print(f"  {warning}")
        else:
            print(f"\n✅ No warnings detected")

        print(f"{'='*80}\n")
        sys.exit(0)

    except ScopeViolationError as e:
        print(f"\n{'='*80}", file=sys.stderr)
        print(f"🚫 SCOPE VIOLATION - BLOCKED", file=sys.stderr)
        print(f"{'='*80}", file=sys.stderr)
        print(f"\n{str(e)}\n", file=sys.stderr)
        print(f"File count: {e.file_count}", file=sys.stderr)
        print(f"Max allowed: {e.max_allowed}", file=sys.stderr)
        print(f"{'='*80}\n", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ ERROR: {e}\n", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()