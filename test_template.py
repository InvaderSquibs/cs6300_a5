#!/usr/bin/env python3
"""
Simple test script to verify the validation components work
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_recipe_data():
    """Test recipe data functionality"""
    print("Testing recipe data...")
    try:
        from recipe_data import get_random_recipe, format_recipe_for_summary, SAMPLE_RECIPES
        
        print(f"✅ Found {len(SAMPLE_RECIPES)} sample recipes")
        
        recipe = get_random_recipe()
        print(f"✅ Random recipe: {recipe['name']}")
        
        formatted = format_recipe_for_summary(recipe)
        print(f"✅ Formatted recipe length: {len(formatted)} characters")
        
        return True
    except Exception as e:
        print(f"❌ Recipe data test failed: {e}")
        return False

def test_validation_script():
    """Test that the main validation script can be imported"""
    print("\nTesting validation script structure...")
    try:
        # Read the validation script and check for key functions
        with open('validate_vdb.py', 'r') as f:
            content = f.read()
        
        required_functions = [
            'validate_environment',
            'test_llm_connection', 
            'initialize_vector_db',
            'process_recipes',
            'test_queries',
            'main'
        ]
        
        for func in required_functions:
            if f"def {func}" in content:
                print(f"✅ Found function: {func}")
            else:
                print(f"❌ Missing function: {func}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Validation script test failed: {e}")
        return False

def test_file_structure():
    """Test that all required files exist"""
    print("\nTesting file structure...")
    
    required_files = [
        'requirements.txt',
        'recipe_data.py',
        'llm_client.py', 
        'vector_db.py',
        'validate_vdb.py',
        'setup.sh',
        '.env.example',
        '.gitignore'
    ]
    
    all_present = True
    for filename in required_files:
        if os.path.exists(filename):
            print(f"✅ Found file: {filename}")
        else:
            print(f"❌ Missing file: {filename}")
            all_present = False
    
    return all_present

def main():
    print("=" * 50)
    print("  VECTOR TEMPLATE TEST SUITE")
    print("=" * 50)
    
    tests = [
        ("Recipe Data", test_recipe_data),
        ("File Structure", test_file_structure),
        ("Validation Script", test_validation_script)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        if test_func():
            print(f"✅ {test_name} test PASSED")
            passed += 1
        else:
            print(f"❌ {test_name} test FAILED")
    
    print(f"\n{'='*50}")
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The vector template is ready to use.")
        print("\nNext steps:")
        print("1. Run ./setup.sh to install dependencies") 
        print("2. Configure .env with your LLM endpoint")
        print("3. Run python validate_vdb.py")
    else:
        print("❌ Some tests failed. Please check the implementation.")
        sys.exit(1)

if __name__ == "__main__":
    main()