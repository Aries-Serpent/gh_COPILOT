#!/usr/bin/env python3
"""
Final Modular Organization Validation
"""

from pathlib import Path

def validate_organization():
    """Validate the comprehensive modular organization"""
    workspace = Path('.')
    scripts_dir = workspace / 'scripts'
    utils_dir = workspace / 'utils'
    
    print('🏆 COMPREHENSIVE MODULAR ORGANIZATION VALIDATION')
    print('='*60)
    
    # Check root directory Python files
    root_py_files = list(workspace.glob('*.py'))
    print(f'📁 Root Directory Python Files: {len(root_py_files)}')
    
    # Check scripts directory organization
    total_organized = 0
    if scripts_dir.exists():
        categories = [d for d in scripts_dir.iterdir() if d.is_dir()]
        print(f'📂 Script Categories: {len(categories)}')
        
        for category in categories:
            py_files = list(category.glob('*.py'))
            total_organized += len(py_files)
            print(f'   ✅ {category.name}: {len(py_files)} scripts')
        
        print(f'📊 Total Organized Scripts: {total_organized}')
    
    # Check utils directory
    if utils_dir.exists():
        util_modules = list(utils_dir.glob('*.py'))
        print(f'🔧 Utility Modules: {len(util_modules)}')
        for module in util_modules:
            print(f'   ✅ {module.name}')
    
    # Calculate organization percentage
    total_scripts = len(root_py_files) + total_organized
    organization_percentage = (total_organized / total_scripts * 100) if total_scripts > 0 else 100
    print(f'📈 Organization Percentage: {organization_percentage:.1f}%')
    
    print('='*60)
    if len(root_py_files) == 0 and total_organized > 0:
        print('🎯 STATUS: ✅ COMPREHENSIVE ORGANIZATION COMPLETE')
        return True
    else:
        print('🎯 STATUS: ⚠️ ORGANIZATION IN PROGRESS')
        return False

if __name__ == "__main__":
    validate_organization()
