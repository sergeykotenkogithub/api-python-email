"""
File-based repository module.

This module provides file-based storage operations for contact form data,
metrics, and other application data.
"""

import json
import aiofiles
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
from uuid import uuid4
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("FileRepository")


class FileRepository:
    """File-based repository for data storage."""
    
    def __init__(self):
        self.data_dir = Path(settings.DATA_DIR)
        self.contacts_dir = self.data_dir / "contacts"
        self.stats_dir = self.data_dir / "stats"
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create necessary directories if they don't exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.contacts_dir.mkdir(parents=True, exist_ok=True)
        self.stats_dir.mkdir(parents=True, exist_ok=True)
    
    async def save_contact(self, contact_data: Dict[str, Any]) -> str:
        """Save contact form submission to file."""
        contact_id = str(uuid4())
        timestamp = datetime.utcnow()
        
        contact_record = {
            "id": contact_id,
            **contact_data,
            "timestamp": timestamp.isoformat()
        }
        
        # Save to daily file
        date_str = timestamp.strftime("%Y-%m-%d")
        daily_file = self.contacts_dir / f"contacts_{date_str}.json"
        
        try:
            # Read existing data or create new list
            if daily_file.exists():
                async with aiofiles.open(daily_file, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    contacts = json.loads(content) if content else []
            else:
                contacts = []
            
            # Append new contact
            contacts.append(contact_record)
            
            # Write back to file with UTF-8 encoding
            async with aiofiles.open(daily_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(contacts, indent=2, ensure_ascii=False))
            
            logger.info(f"Contact saved: {contact_id}")
            return contact_id
            
        except Exception as e:
            logger.error(f"Failed to save contact: {e}")
            raise
    
    async def get_contacts_by_date(self, target_date: date = None) -> List[Dict[str, Any]]:
        """Get all contacts for a specific date."""
        if target_date is None:
            target_date = date.today()
        
        date_str = target_date.strftime("%Y-%m-%d")
        daily_file = self.contacts_dir / f"contacts_{date_str}.json"
        
        try:
            if not daily_file.exists():
                return []
            
            async with aiofiles.open(daily_file, 'r', encoding='utf-8') as f:
                content = await f.read()
                return json.loads(content) if content else []
                
        except Exception as e:
            logger.error(f"Failed to read contacts: {e}")
            return []
    
    async def get_all_contacts(self) -> List[Dict[str, Any]]:
        """Get all contacts from all daily files."""
        all_contacts = []
        
        try:
            for daily_file in self.contacts_dir.glob("contacts_*.json"):
                async with aiofiles.open(daily_file, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    contacts = json.loads(content) if content else []
                    all_contacts.extend(contacts)
            
            return sorted(all_contacts, key=lambda x: x.get("timestamp", ""))
            
        except Exception as e:
            logger.error(f"Failed to read all contacts: {e}")
            return []
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Calculate and return application metrics."""
        try:
            all_contacts = await self.get_all_contacts()
            today = date.today()
            today_contacts = await self.get_contacts_by_date(today)
            
            # Calculate metrics
            total_requests = len(all_contacts)
            today_requests = len(today_contacts)
            
            # Calculate sentiment distribution
            sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
            category_counts = {}
            
            for contact in all_contacts:
                ai_analysis = contact.get("ai_analysis", {})
                
                # Sentiment distribution
                sentiment = ai_analysis.get("sentiment", "neutral")
                if sentiment in sentiment_counts:
                    sentiment_counts[sentiment] += 1
                
                # Category distribution
                category = ai_analysis.get("category", "other")
                category_counts[category] = category_counts.get(category, 0) + 1
            
            # Get top categories
            sorted_categories = sorted(
                category_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            top_categories = [
                {"category": cat, "count": count} 
                for cat, count in sorted_categories[:5]
            ]
            
            metrics = {
                "total_requests": total_requests,
                "successful_requests": total_requests,  # All saved contacts are successful
                "failed_requests": 0,  # You might want to track failed attempts separately
                "requests_today": today_requests,
                "average_response_time_ms": 0.0,  # You'd need to track this separately
                "top_categories": top_categories,
                "sentiment_distribution": sentiment_counts,
                "last_updated": datetime.utcnow().isoformat()
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to calculate metrics: {e}")
            return {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "requests_today": 0,
                "average_response_time_ms": 0.0,
                "top_categories": [],
                "sentiment_distribution": {},
                "last_updated": datetime.utcnow().isoformat()
            }
    
    async def save_metrics(self, metrics: Dict[str, Any]):
        """Save metrics to file."""
        metrics_file = self.stats_dir / "metrics.json"
        
        try:
            async with aiofiles.open(metrics_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(metrics, indent=2, ensure_ascii=False))
            logger.info("Metrics saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")
            raise
    
    async def cleanup_old_files(self, days_to_keep: int = 30):
        """Clean up old contact files to save disk space."""
        try:
            cutoff_date = date.today() - timedelta(days=days_to_keep)
            
            for daily_file in self.contacts_dir.glob("contacts_*.json"):
                # Extract date from filename
                file_date_str = daily_file.stem.replace("contacts_", "")
                try:
                    file_date = datetime.strptime(file_date_str, "%Y-%m-%d").date()
                    if file_date < cutoff_date:
                        daily_file.unlink()
                        logger.info(f"Deleted old file: {daily_file.name}")
                except ValueError:
                    continue
                    
        except Exception as e:
            logger.error(f"Failed to cleanup old files: {e}")


# Create global repository instance
file_repository = FileRepository()


def get_repository() -> FileRepository:
    """Get file repository instance."""
    return file_repository