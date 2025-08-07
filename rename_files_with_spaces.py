#!/usr/bin/env python3
"""
🔧 File Renaming Tool: Replace Spaces with Underscores
Systematically rename all files in a directory to replace spaces with underscores
"""

from pathlib import Path
from datetime import datetime
from typing import Union
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FileRenamer:
    """🔧 Professional file renaming with space-to-underscore conversion"""

    def __init__(self, target_directory: Union[str, Path]):
        """Initialize renamer with directory to process."""
        self.target_directory = Path(target_directory)
        self.renamed_files = []
        self.skipped_files = []
        self.errors = []
        
    def validate_directory(self) -> bool:
        """✅ Validate target directory exists and is accessible"""
        if not self.target_directory.exists():
            logger.error(f"❌ Directory does not exist: {self.target_directory}")
            return False
            
        if not self.target_directory.is_dir():
            logger.error(f"❌ Path is not a directory: {self.target_directory}")
            return False
            
        logger.info(f"✅ Directory validated: {self.target_directory}")
        return True
    
    def get_files_with_spaces(self) -> list:
        """🔍 Identify all files that contain spaces in their names"""
        files_with_spaces = []
        
        try:
            for file_path in self.target_directory.iterdir():
                if file_path.is_file() and ' ' in file_path.name:
                    files_with_spaces.append(file_path)
                    
            logger.info(f"🔍 Found {len(files_with_spaces)} files with spaces")
            
            # Log each file for transparency
            for file_path in files_with_spaces:
                logger.info(f"   📄 {file_path.name}")
                
        except Exception as e:
            logger.error(f"❌ Error scanning directory: {e}")
            self.errors.append(f"Directory scan error: {e}")
            
        return files_with_spaces
    
    def generate_new_filename(self, original_name: str) -> str:
        """🔄 Generate new filename by replacing spaces with underscores"""
        # Replace spaces with underscores
        new_name = original_name.replace(' ', '_')
        
        # Clean up any multiple underscores (just in case)
        while '__' in new_name:
            new_name = new_name.replace('__', '_')
            
        return new_name
    
    def rename_file_safely(self, file_path: Path) -> bool:
        """🔄 Safely rename a single file with proper error handling"""
        try:
            original_name = file_path.name
            new_name = self.generate_new_filename(original_name)
            
            # Skip if no change needed
            if original_name == new_name:
                logger.info(f"⏭️  Skipped (no spaces): {original_name}")
                self.skipped_files.append(original_name)
                return True
            
            # Generate new path
            new_path = file_path.parent / new_name
            
            # Check if target already exists
            if new_path.exists():
                logger.warning(f"⚠️  Target exists, skipping: {new_name}")
                self.skipped_files.append(f"{original_name} (target exists)")
                return False
            
            # Perform the rename
            file_path.rename(new_path)
            
            logger.info(f"✅ Renamed: '{original_name}' → '{new_name}'")
            self.renamed_files.append({
                'original': original_name,
                'new': new_name,
                'timestamp': datetime.now().isoformat()
            })
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error renaming {file_path.name}: {e}")
            self.errors.append(f"Rename error for {file_path.name}: {e}")
            return False
    
    def rename_all_files(self) -> dict:
        """🚀 Rename all files with spaces in the directory"""
        logger.info("="*60)
        logger.info("🚀 STARTING FILE RENAMING OPERATION")
        logger.info(f"📁 Target Directory: {self.target_directory}")
        logger.info("="*60)
        
        # Validate directory
        if not self.validate_directory():
            return self.generate_summary()
        
        # Get files with spaces
        files_with_spaces = self.get_files_with_spaces()
        
        if not files_with_spaces:
            logger.info("✅ No files with spaces found - nothing to rename!")
            return self.generate_summary()
        
        # Rename each file
        logger.info(f"🔄 Processing {len(files_with_spaces)} files...")
        
        for file_path in files_with_spaces:
            self.rename_file_safely(file_path)
        
        # Generate and return summary
        summary = self.generate_summary()
        self.log_summary(summary)

        try:
            from tools.convert_daily_whitepaper import convert_pdfs
            from scripts.documentation.update_daily_state_index import update_index

            for message in convert_pdfs(self.target_directory):
                logger.info(message)
            index_path = self.target_directory.parent / "daily_state_index.md"
            update_index(source_dir=self.target_directory, index_path=index_path)
        except Exception as e:  # noqa: BLE001
            logger.error(f"❌ Conversion step failed: {e}")
            self.errors.append(f"Conversion error: {e}")

        return summary
    
    def generate_summary(self) -> dict:
        """📊 Generate comprehensive summary of renaming operation"""
        return {
            'operation_timestamp': datetime.now().isoformat(),
            'target_directory': str(self.target_directory),
            'files_renamed': len(self.renamed_files),
            'files_skipped': len(self.skipped_files),
            'errors_encountered': len(self.errors),
            'renamed_files_details': self.renamed_files,
            'skipped_files_details': self.skipped_files,
            'error_details': self.errors,
            'operation_status': 'SUCCESS' if not self.errors else 'PARTIAL_SUCCESS' if self.renamed_files else 'FAILED'
        }
    
    def log_summary(self, summary: dict):
        """📋 Log comprehensive summary of the operation"""
        logger.info("="*60)
        logger.info("📊 FILE RENAMING OPERATION SUMMARY")
        logger.info("="*60)
        logger.info(f"📁 Directory: {summary['target_directory']}")
        logger.info(f"✅ Files Renamed: {summary['files_renamed']}")
        logger.info(f"⏭️  Files Skipped: {summary['files_skipped']}")
        logger.info(f"❌ Errors: {summary['errors_encountered']}")
        logger.info(f"🎯 Status: {summary['operation_status']}")
        
        if summary['renamed_files_details']:
            logger.info("\n📝 RENAMED FILES:")
            for file_info in summary['renamed_files_details']:
                logger.info(f"   '{file_info['original']}' → '{file_info['new']}'")
        
        if summary['skipped_files_details']:
            logger.info("\n⏭️  SKIPPED FILES:")
            for skipped in summary['skipped_files_details']:
                logger.info(f"   {skipped}")
        
        if summary['error_details']:
            logger.info("\n❌ ERRORS:")
            for error in summary['error_details']:
                logger.info(f"   {error}")
        
        logger.info("="*60)

def main() -> dict:
    """🎯 Main execution function"""
    # Target directory relative to this script
    target_directory = Path(__file__).resolve().parent / 'documentation/generated/daily_state_update'
    
    # Create renamer and execute
    renamer = FileRenamer(target_directory)
    summary = renamer.rename_all_files()

    # Return summary for potential further processing
    return summary

if __name__ == "__main__":
    try:
        result = main()
        print(f"\n🎯 Operation completed with status: {result['operation_status']}")
        print(f"📊 Files renamed: {result['files_renamed']}")
        
    except Exception as e:
        logger.error(f"💥 Critical error in main execution: {e}")
        print(f"❌ Script failed with error: {e}")
