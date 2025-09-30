"""
Test suite standalone pour valider le scope validator (pas de dépendances SDK).

Tests identiques à test_scope_control.py mais sans dépendances Claude SDK.
"""

import sys
from scope_validator import (
    analyze_scope,
    ScopeViolationError
)


def test_1_legitimate_css_fix():
    """Test 1: Changement légitime de 2 fichiers CSS - devrait passer sans friction."""
    print("\n" + "="*80)
    print("TEST 1: Legitimate CSS Fix (2 fichiers)")
    print("="*80)

    files = [
        'src/components/Button.css',
        'src/components/Header.css'
    ]
    description = "Fix button alignment in header"

    try:
        result = analyze_scope(files, description)

        print(f"✅ Status: APPROVED")
        print(f"   Scope Level: {result['scope_level']}")
        print(f"   File Count: {result['file_count']}")
        print(f"   Warnings: {len(result['warnings'])}")

        if result['warnings']:
            for warning in result['warnings']:
                print(f"   {warning}")

        assert result['approved'] == True
        assert result['scope_level'] == "LOCAL"
        assert result['file_count'] == 2
        print("\n✅ TEST 1 PASSED: Changes légitimes approuvés sans friction")

    except Exception as e:
        print(f"❌ TEST 1 FAILED: {e}")
        return False

    return True


def test_2_moderate_scope_creep():
    """Test 2: Scope modéré de 5 fichiers - devrait approuver avec warning."""
    print("\n" + "="*80)
    print("TEST 2: Moderate Scope Creep (5 fichiers)")
    print("="*80)

    files = [
        'src/components/Button.css',
        'src/components/Header.css',
        'src/components/Footer.css',
        'src/components/Sidebar.css',
        'src/styles/theme.css'
    ]
    description = "Update color scheme across components"

    try:
        result = analyze_scope(files, description)

        print(f"⚠️  Status: APPROVED with WARNING")
        print(f"   Scope Level: {result['scope_level']}")
        print(f"   File Count: {result['file_count']}")
        print(f"   Warnings: {len(result['warnings'])}")

        for warning in result['warnings']:
            print(f"   {warning}")

        assert result['approved'] == True
        assert result['scope_level'] == "MODERATE"
        assert result['file_count'] == 5
        assert len(result['warnings']) > 0
        print("\n✅ TEST 2 PASSED: Scope modéré détecté avec warning approprié")

    except Exception as e:
        print(f"❌ TEST 2 FAILED: {e}")
        return False

    return True


def test_3_bulldozer_systemique():
    """Test 3: Cas historique - 11 fichiers incluant infrastructure - devrait bloquer."""
    print("\n" + "="*80)
    print("TEST 3: Bulldozer Systémique (11 fichiers) - CAS HISTORIQUE 2025-01-22")
    print("="*80)

    files = [
        'src/components/Button.css',
        'src/components/Header.css',
        'src/components/Footer.css',
        'src/styles/theme.css',
        'src/styles/variables.css',
        'public/index.html',
        'Dockerfile',
        'docker-compose.yml',
        'nginx.conf',
        'src/App.js',
        'package.json'
    ]
    description = "Fix CSS button styling issue"

    try:
        result = analyze_scope(files, description)

        # Si on arrive ici, le test a échoué (devrait lever exception)
        print(f"❌ TEST 3 FAILED: Should have blocked but approved")
        print(f"   Result: {result}")
        return False

    except ScopeViolationError as e:
        print(f"🚫 Status: BLOCKED (exception levée)")
        print(f"   Exception: {type(e).__name__}")
        print(f"   Message: {str(e)}")
        print(f"   File count: {e.file_count}")
        print(f"   Max allowed: {e.max_allowed}")

        assert e.file_count == 11
        assert e.max_allowed == 10
        print("\n✅ TEST 3 PASSED: Bulldozer Systémique bloqué via exception")
        print("   ✅ Le cas historique 2025-01-22 aurait été PRÉVENU")
        return True

    except Exception as e:
        print(f"❌ TEST 3 FAILED: Wrong exception type: {e}")
        return False


def test_4_anti_pattern_infrastructure_ui():
    """Test 4: Anti-pattern détection - infrastructure files pour UI issue."""
    print("\n" + "="*80)
    print("TEST 4: Anti-Pattern Detection (Infrastructure + UI)")
    print("="*80)

    files = [
        'src/components/Button.css',
        'Dockerfile',
        'docker-compose.yml'
    ]
    description = "Fix CSS button alignment"

    try:
        result = analyze_scope(files, description)

        print(f"⚠️  Status: APPROVED but with ANTI-PATTERN WARNING")
        print(f"   Scope Level: {result['scope_level']}")
        print(f"   File Count: {result['file_count']}")
        print(f"   Warnings: {len(result['warnings'])}")

        # Vérifier qu'au moins un warning mentionne l'anti-pattern
        anti_pattern_detected = any('ANTI-PATTERN' in w for w in result['warnings'])

        for warning in result['warnings']:
            print(f"   {warning}")

        assert result['approved'] == True
        assert result['scope_level'] == "LOCAL"
        assert anti_pattern_detected == True
        print("\n✅ TEST 4 PASSED: Anti-pattern infrastructure+UI détecté et signalé")

    except Exception as e:
        print(f"❌ TEST 4 FAILED: {e}")
        return False

    return True


def test_5_no_dependencies():
    """Test 5: Vérifier qu'aucune dépendance SDK n'est requise."""
    print("\n" + "="*80)
    print("TEST 5: No SDK Dependencies Required")
    print("="*80)

    try:
        # Essayer d'importer le module
        import scope_validator

        # Vérifier qu'il n'y a pas d'import claude_agent_sdk
        import inspect
        source = inspect.getsource(scope_validator)

        has_sdk_import = 'claude_agent_sdk' in source or 'anthropic' in source

        if has_sdk_import:
            print("❌ Module contains SDK imports")
            return False

        print("✅ Module is pure Python - no SDK dependencies")
        print("   Works with Claude MAX subscription only")
        print("\n✅ TEST 5 PASSED: Standalone implementation validated")
        return True

    except Exception as e:
        print(f"❌ TEST 5 FAILED: {e}")
        return False


def run_all_tests():
    """Execute tous les tests et affiche le résumé."""
    print("\n" + "="*80)
    print("SCOPE VALIDATOR - STANDALONE TEST SUITE")
    print("="*80)
    print("Validation sans dépendances SDK - Pure Python stdlib")
    print()

    tests = [
        ("Test 1: Legitimate CSS Fix", test_1_legitimate_css_fix),
        ("Test 2: Moderate Scope Creep", test_2_moderate_scope_creep),
        ("Test 3: Bulldozer Systémique (Historical)", test_3_bulldozer_systemique),
        ("Test 4: Anti-Pattern Detection", test_4_anti_pattern_infrastructure_ui),
        ("Test 5: No SDK Dependencies", test_5_no_dependencies),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} CRASHED: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED - STANDALONE VERSION VALIDÉE!")
        print("\nConclusions:")
        print("- ✅ Scope control fonctionne sans SDK")
        print("- ✅ Exception bloque >10 fichiers")
        print("- ✅ Anti-patterns détectés")
        print("- ✅ Pas de dépendances payantes requises")
        print("- ✅ Fonctionne avec Claude MAX uniquement")
        print("\n➡️  Ready for production deployment")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())