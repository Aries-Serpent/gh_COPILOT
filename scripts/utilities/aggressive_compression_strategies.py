#!/usr/bin/env python3
"""
🔥 AGGRESSIVE COMPRESSION STRATEGIES
================================================================
Advanced compression strategies for extreme size reduction
when standard compression doesn't meet the 99.9MB target
================================================================
"""

import json
import gzip
import bz2
import lzma
import pickle
from pathlib import Path
from datetime import datetime, timedelta
import hashlib
import sqlite3
from tqdm import tqdm
import logging

logger = logging.getLogger(__name__)

class AggressiveCompressionStrategies:
    """🔥 Advanced compression strategies for extreme size reduction"""
    
    def __init__(self, source_file, target_size_mb=99.0):
        self.source_file = Path(source_file)
        self.target_size_mb = target_size_mb
        self.results_dir = self.source_file.parent
        
    def strategy_1_data_archival(self, data):
        """📦 Archive old validation data"""
        logger.info("📦 Applying data archival strategy...")
        
        archived_data = {"current_data": {}, "archived_summary": {}}
        cutoff_date = datetime.now() - timedelta(days=30)
        
        for key, value in data.items():
            if isinstance(value, list):
                current_items = []
                archived_count = 0
                
                for item in value:
                    # Check if item has timestamp
                    item_date = None
                    if isinstance(item, dict):
                        for date_field in ["timestamp", "created_at", "date", "last_updated"]:
                            if date_field in item:
                                try:
                                    item_date = datetime.fromisoformat(str(item[date_field]).replace('Z', '+00:00'))
                                    break
                                except:
                                    continue
                    
                    if item_date and item_date < cutoff_date:
                        archived_count += 1
                    else:
                        current_items.append(item)
                
                archived_data["current_data"][key] = current_items
                if archived_count > 0:
                    archived_data["archived_summary"][key] = {
                        "archived_items": archived_count,
                        "cutoff_date": cutoff_date.isoformat()
                    }
            else:
                archived_data["current_data"][key] = value
        
        return archived_data
    
    def strategy_2_binary_compression(self, data):
        """🗜️ Apply binary compression algorithms"""
        logger.info("🗜️ Applying binary compression algorithms...")
        
        outputs = {}
        json_data = json.dumps(data, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
        
        # LZMA compression (highest ratio)
        lzma_output = self.results_dir / "database_validation_results.json.xz"
        with lzma.open(lzma_output, 'wb', preset=9) as f:
            f.write(json_data)
        outputs["lzma"] = {"path": lzma_output, "size_mb": lzma_output.stat().st_size / (1024 * 1024)}
        
        # BZ2 compression
        bz2_output = self.results_dir / "database_validation_results.json.bz2"
        with bz2.open(bz2_output, 'wb', compresslevel=9) as f:
            f.write(json_data)
        outputs["bz2"] = {"path": bz2_output, "size_mb": bz2_output.stat().st_size / (1024 * 1024)}
        
        # Pickle compression (if data structure allows)
        try:
            pickle_output = self.results_dir / "database_validation_results.pkl.gz"
            with gzip.open(pickle_output, 'wb', compresslevel=9) as f:
                pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
            outputs["pickle_gzip"] = {"path": pickle_output, "size_mb": pickle_output.stat().st_size / (1024 * 1024)}
        except Exception as e:
            logger.warning(f"Pickle compression failed: {e}")
        
        return outputs
    
    def strategy_3_database_migration(self, data):
        """🗄️ Migrate to optimized database format"""
        logger.info("🗄️ Migrating to optimized database format...")
        
        # Create optimized SQLite database with compression
        db_output = Path(self.results_dir.parent) / "databases" / "database_validation_results_optimized.db"
        if db_output.exists():
            db_output.unlink()
        
        conn = sqlite3.connect(db_output)
        cursor = conn.cursor()
        
        # Enable SQLite optimizations
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=10000")
        cursor.execute("PRAGMA temp_store=MEMORY")
        
        # Create optimized tables
        cursor.execute("""
            CREATE TABLE validation_entries (
                id INTEGER PRIMARY KEY,
                category TEXT,
                status TEXT,
                count INTEGER,
                sample_data TEXT,
                hash TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE validation_stats (
                id INTEGER PRIMARY KEY,
                metric_name TEXT,
                metric_value REAL,
                metric_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert data efficiently
        entry_id = 0
        for key, value in tqdm(data.items(), desc="🗄️ Migrating data"):
            if isinstance(value, list):
                # Batch similar entries
                for item in value:
                    if isinstance(item, dict):
                        item_hash = hashlib.md5(str(item).encode()).hexdigest()
                        cursor.execute("""
                            INSERT OR IGNORE INTO validation_entries 
                            (category, status, count, sample_data, hash)
                            VALUES (?, ?, ?, ?, ?)
                        """, (
                            key,
                            item.get('status', 'unknown'),
                            item.get('count', 1),
                            json.dumps(item)[:1000],  # Truncate large data
                            item_hash
                        ))
            elif isinstance(value, (int, float)):
                cursor.execute("""
                    INSERT INTO validation_stats (metric_name, metric_value, metric_type)
                    VALUES (?, ?, ?)
                """, (key, value, type(value).__name__))
        
        # Create indexes and optimize
        cursor.execute("CREATE INDEX idx_category ON validation_entries(category)")
        cursor.execute("CREATE INDEX idx_status ON validation_entries(status)")
        cursor.execute("CREATE INDEX idx_metric ON validation_stats(metric_name)")
        cursor.execute("VACUUM")
        cursor.execute("ANALYZE")
        
        conn.commit()
        conn.close()
        
        return {"path": db_output, "size_mb": db_output.stat().st_size / (1024 * 1024)}
    
    def strategy_4_smart_sampling(self, data):
        """📊 Intelligent data sampling"""
        logger.info("📊 Applying intelligent data sampling...")
        
        sampled_data = {}
        
        for key, value in data.items():
            if isinstance(value, list) and len(value) > 100:
                # Apply statistical sampling
                total_items = len(value)
                sample_size = min(50, max(10, total_items // 20))  # 5% sample, min 10, max 50
                
                # Stratified sampling if possible
                if value and isinstance(value[0], dict):
                    # Group by status or type for representative sampling
                    groups = {}
                    for item in value:
                        group_key = item.get('status', item.get('type', 'unknown'))
                        if group_key not in groups:
                            groups[group_key] = []
                        groups[group_key].append(item)
                    
                    sampled_items = []
                    items_per_group = max(1, sample_size // len(groups))
                    
                    for group_name, group_items in groups.items():
                        sampled_items.extend(group_items[:items_per_group])
                    
                    # If we need more items, add from largest groups
                    while len(sampled_items) < sample_size and sum(len(g) for g in groups.values()) > len(sampled_items):
                        for group_items in sorted(groups.values(), key=len, reverse=True):
                            if len(sampled_items) >= sample_size:
                                break
                            remaining_items = [item for item in group_items if item not in sampled_items]
                            if remaining_items:
                                sampled_items.append(remaining_items[0])
                else:
                    # Simple random sampling for non-dict items
                    import random
                    sampled_items = random.sample(value, sample_size)
                
                sampled_data[key] = {
                    "sample_data": sampled_items,
                    "original_count": total_items,
                    "sample_count": len(sampled_items),
                    "sampling_ratio": len(sampled_items) / total_items,
                    "note": f"Sampled {len(sampled_items)} items from {total_items} total"
                }
            else:
                sampled_data[key] = value
        
        return sampled_data
    
    def strategy_5_hybrid_approach(self, data):
        """🔄 Combined approach using multiple strategies"""
        logger.info("🔄 Applying hybrid compression approach...")
        
        # Step 1: Archive old data
        archived_data = self.strategy_1_data_archival(data)
        
        # Step 2: Apply smart sampling to current data
        sampled_data = self.strategy_4_smart_sampling(archived_data["current_data"])
        
        # Step 3: Combine with archive summary
        hybrid_data = {
            "current_validation_data": sampled_data,
            "archive_summary": archived_data["archived_summary"],
            "compression_metadata": {
                "strategies_applied": ["archival", "sampling"],
                "original_size_estimate": "111+ MB",
                "compression_timestamp": datetime.now().isoformat()
            }
        }
        
        return hybrid_data
    
    def execute_aggressive_compression(self, data):
        """🚀 Execute all aggressive compression strategies"""
        logger.info("🚀 Executing aggressive compression strategies...")
        
        strategies = {}
        
        with tqdm(total=100, desc="🔥 Aggressive compression", unit="%") as pbar:
            
            # Strategy 1: Data Archival
            pbar.set_description("📦 Data archival")
            try:
                archived_data = self.strategy_1_data_archival(data)
                archival_output = self.results_dir / "database_validation_results_archived.json"
                with open(archival_output, 'w', encoding='utf-8') as f:
                    json.dump(archived_data, f, separators=(',', ':'), ensure_ascii=False)
                strategies["archival"] = {
                    "path": archival_output, 
                    "size_mb": archival_output.stat().st_size / (1024 * 1024)
                }
            except Exception as e:
                logger.error(f"Archival strategy failed: {e}")
            pbar.update(20)
            
            # Strategy 2: Binary Compression
            pbar.set_description("🗜️ Binary compression")
            try:
                binary_outputs = self.strategy_2_binary_compression(data)
                strategies.update(binary_outputs)
            except Exception as e:
                logger.error(f"Binary compression failed: {e}")
            pbar.update(20)
            
            # Strategy 3: Database Migration
            pbar.set_description("🗄️ Database migration")
            try:
                db_output = self.strategy_3_database_migration(data)
                strategies["optimized_database"] = db_output
            except Exception as e:
                logger.error(f"Database migration failed: {e}")
            pbar.update(20)
            
            # Strategy 4: Smart Sampling
            pbar.set_description("📊 Smart sampling")
            try:
                sampled_data = self.strategy_4_smart_sampling(data)
                sampling_output = self.results_dir / "database_validation_results_sampled.json"
                with open(sampling_output, 'w', encoding='utf-8') as f:
                    json.dump(sampled_data, f, separators=(',', ':'), ensure_ascii=False)
                strategies["smart_sampling"] = {
                    "path": sampling_output,
                    "size_mb": sampling_output.stat().st_size / (1024 * 1024)
                }
            except Exception as e:
                logger.error(f"Sampling strategy failed: {e}")
            pbar.update(20)
            
            # Strategy 5: Hybrid Approach
            pbar.set_description("🔄 Hybrid approach")
            try:
                hybrid_data = self.strategy_5_hybrid_approach(data)
                hybrid_output = self.results_dir / "database_validation_results_hybrid.json"
                with open(hybrid_output, 'w', encoding='utf-8') as f:
                    json.dump(hybrid_data, f, separators=(',', ':'), ensure_ascii=False)
                strategies["hybrid"] = {
                    "path": hybrid_output,
                    "size_mb": hybrid_output.stat().st_size / (1024 * 1024)
                }
            except Exception as e:
                logger.error(f"Hybrid strategy failed: {e}")
            pbar.update(20)
        
        # Find strategies that meet target
        successful_strategies = {}
        for name, info in strategies.items():
            if info["size_mb"] <= self.target_size_mb:
                successful_strategies[name] = info
        
        return strategies, successful_strategies

def apply_aggressive_compression(source_file, target_size_mb=99.0):
    """🔥 Apply aggressive compression strategies to large validation file"""
    
    logger.info(f"🔥 Starting aggressive compression for {source_file}")
    
    # Load original data
    with open(source_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    compressor = AggressiveCompressionStrategies(source_file, target_size_mb)
    all_strategies, successful_strategies = compressor.execute_aggressive_compression(data)
    
    # Generate report
    report = {
        "original_file": str(source_file),
        "original_size_mb": Path(source_file).stat().st_size / (1024 * 1024),
        "target_size_mb": target_size_mb,
        "strategies_attempted": len(all_strategies),
        "successful_strategies": len(successful_strategies),
        "all_outputs": {k: {**v, "path": str(v["path"])} for k, v in all_strategies.items()},
        "successful_outputs": {k: {**v, "path": str(v["path"])} for k, v in successful_strategies.items()},
        "timestamp": datetime.now().isoformat()
    }
    
    report_path = Path(source_file).parent / f"aggressive_compression_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"📋 Aggressive compression report: {report_path}")
    
    return successful_strategies, report_path

if __name__ == "__main__":
    source_file = "e:/gh_COPILOT/results/database_validation_results.json"
    successful, report_path = apply_aggressive_compression(source_file)
    
    if successful:
        print(f"✅ Aggressive compression found {len(successful)} successful strategies")
        for name, info in successful.items():
            print(f"   {name}: {info['size_mb']:.2f} MB")
    else:
        print("❌ No aggressive compression strategy met the target size")
    
    print(f"📋 Full report: {report_path}")
