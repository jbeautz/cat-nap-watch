#!/usr/bin/env python3
"""
Photo Management Utilities for CatNap Watch
Handles cleanup and maintenance of stored photos
"""

import os
import glob
import time
import logging
from datetime import datetime, timedelta
from config import PHOTOS_DIR, MAX_STORED_PHOTOS

logger = logging.getLogger(__name__)

def cleanup_old_photos(max_photos=MAX_STORED_PHOTOS, dry_run=False):
    """
    Clean up old photos, keeping only the most recent ones.
    
    Args:
        max_photos: Maximum number of photos to keep
        dry_run: If True, only show what would be deleted
    
    Returns:
        Number of photos deleted
    """
    try:
        if not os.path.exists(PHOTOS_DIR):
            logger.info("Photos directory doesn't exist")
            return 0
        
        # Get all photo files sorted by modification time (newest first)
        photo_pattern = os.path.join(PHOTOS_DIR, "*.jpg")
        photo_files = glob.glob(photo_pattern)
        
        if not photo_files:
            logger.info("No photos found to clean up")
            return 0
        
        # Sort by modification time (newest first)
        photo_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        logger.info(f"Found {len(photo_files)} total photos")
        
        if len(photo_files) <= max_photos:
            logger.info(f"Photo count ({len(photo_files)}) is within limit ({max_photos})")
            return 0
        
        # Files to delete (oldest ones beyond the limit)
        files_to_delete = photo_files[max_photos:]
        
        if dry_run:
            logger.info(f"DRY RUN: Would delete {len(files_to_delete)} old photos:")
            for file_path in files_to_delete:
                file_age = datetime.fromtimestamp(os.path.getmtime(file_path))
                logger.info(f"  - {os.path.basename(file_path)} (from {file_age})")
            return len(files_to_delete)
        
        # Actually delete the files
        deleted_count = 0
        for file_path in files_to_delete:
            try:
                file_age = datetime.fromtimestamp(os.path.getmtime(file_path))
                os.remove(file_path)
                logger.info(f"Deleted old photo: {os.path.basename(file_path)} (from {file_age})")
                deleted_count += 1
            except Exception as e:
                logger.error(f"Failed to delete {file_path}: {e}")
        
        logger.info(f"Cleanup complete: deleted {deleted_count} old photos, kept {len(photo_files) - deleted_count}")
        return deleted_count
        
    except Exception as e:
        logger.error(f"Error during photo cleanup: {e}")
        return 0

def get_storage_info():
    """Get information about photo storage usage."""
    try:
        if not os.path.exists(PHOTOS_DIR):
            return {
                'photo_count': 0,
                'total_size_mb': 0,
                'oldest_photo': None,
                'newest_photo': None
            }
        
        photo_pattern = os.path.join(PHOTOS_DIR, "*.jpg")
        photo_files = glob.glob(photo_pattern)
        
        if not photo_files:
            return {
                'photo_count': 0,
                'total_size_mb': 0,
                'oldest_photo': None,
                'newest_photo': None
            }
        
        # Calculate total size
        total_size = sum(os.path.getsize(f) for f in photo_files)
        total_size_mb = total_size / (1024 * 1024)
        
        # Find oldest and newest
        photo_files.sort(key=lambda x: os.path.getmtime(x))
        oldest_file = photo_files[0]
        newest_file = photo_files[-1]
        
        oldest_time = datetime.fromtimestamp(os.path.getmtime(oldest_file))
        newest_time = datetime.fromtimestamp(os.path.getmtime(newest_file))
        
        return {
            'photo_count': len(photo_files),
            'total_size_mb': round(total_size_mb, 2),
            'oldest_photo': oldest_time,
            'newest_photo': newest_time
        }
        
    except Exception as e:
        logger.error(f"Error getting storage info: {e}")
        return {
            'photo_count': 0,
            'total_size_mb': 0,
            'oldest_photo': None,
            'newest_photo': None
        }

def main():
    """Command-line photo management utility."""
    import argparse
    
    parser = argparse.ArgumentParser(description="CatNap Watch Photo Management")
    parser.add_argument('--cleanup', action='store_true', help='Clean up old photos')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be deleted without actually deleting')
    parser.add_argument('--max-photos', type=int, default=MAX_STORED_PHOTOS, help=f'Maximum photos to keep (default: {MAX_STORED_PHOTOS})')
    parser.add_argument('--info', action='store_true', help='Show storage information')
    
    args = parser.parse_args()
    
    # Set up logging for command-line use
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    
    if args.info or (not args.cleanup):
        print("\n📊 CatNap Watch Photo Storage Info")
        print("=" * 35)
        
        info = get_storage_info()
        print(f"📸 Total photos: {info['photo_count']}")
        print(f"💾 Total size: {info['total_size_mb']} MB")
        
        if info['oldest_photo']:
            print(f"📅 Oldest photo: {info['oldest_photo'].strftime('%Y-%m-%d %H:%M:%S')}")
        if info['newest_photo']:
            print(f"🕒 Newest photo: {info['newest_photo'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        if info['photo_count'] > args.max_photos:
            excess = info['photo_count'] - args.max_photos
            print(f"⚠️  {excess} photos exceed the limit of {args.max_photos}")
        
        print()
    
    if args.cleanup:
        print(f"\n🧹 Photo Cleanup (max: {args.max_photos} photos)")
        print("=" * 40)
        
        deleted_count = cleanup_old_photos(args.max_photos, args.dry_run)
        
        if args.dry_run:
            print(f"\nDRY RUN: Would delete {deleted_count} photos")
        else:
            print(f"\nDeleted {deleted_count} old photos")

if __name__ == "__main__":
    main()
