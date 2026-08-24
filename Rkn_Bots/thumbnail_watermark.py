# (c) @RknDeveloperr
# Thumbnail Watermark Feature

import os
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from PIL import Image, ImageDraw, ImageFont
from config import Rkn_Bots

# ==================== THUMBNAIL WATERMARK FUNCTION ====================

async def add_watermark_to_thumbnail(input_path, output_path, text="© Rkn Developer"):
    """Add watermark text to thumbnail image"""
    try:
        # Open image
        img = Image.open(input_path)
        
        # Create a drawing context
        draw = ImageDraw.Draw(img)
        
        # Get image dimensions
        width, height = img.size
        
        # Font size based on image size
        font_size = max(20, int(min(width, height) / 20))
        
        # Try to load a font, fallback to default
        try:
            # Try to use a system font
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            # Fallback to default font
            font = ImageFont.load_default()
        
        # Calculate text position (bottom-right corner with padding)
        padding = 20
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = width - text_width - padding
        y = height - text_height - padding
        
        # Draw text shadow for better visibility
        shadow_offset = 2
        draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=(0, 0, 0, 128))
        
        # Draw main text with semi-transparent background
        # Draw background rectangle
        bg_padding = 10
        draw.rectangle(
            [x - bg_padding, y - bg_padding, x + text_width + bg_padding, y + text_height + bg_padding],
            fill=(0, 0, 0, 100)
        )
        
        # Draw text in white
        draw.text((x, y), text, font=font, fill=(255, 255, 255))
        
        # Save the image
        img.save(output_path, "JPEG", quality=95)
        return True
        
    except Exception as e:
        print(f"❌ Error adding watermark: {e}")
        return False

# ==================== THUMBNAIL PROCESSING ====================

@Client.on_message(filters.channel & filters.media)
async def process_thumbnail_with_watermark(bot, message: Message):
    """Process thumbnail and add watermark"""
    
    # Check if message has media with thumbnail
    if not message.media:
        return
    
    # Check if we should process this channel
    channel_id = message.chat.id
    
    # You can add channel filter logic here if needed
    
    # Process different media types
    media_types = ["video", "document", "audio", "photo"]
    
    for media_type in media_types:
        media_obj = getattr(message, media_type, None)
        if not media_obj:
            continue
            
        # Check if media has thumbnail
        if hasattr(media_obj, "thumb"):
            try:
                # Download thumbnail
                thumb_path = await bot.download_media(media_obj.thumb)
                if thumb_path:
                    # Add watermark
                    output_path = f"{thumb_path}_watermarked.jpg"
                    success = await add_watermark_to_thumbnail(thumb_path, output_path)
                    
                    if success:
                        # Update message with watermarked thumbnail
                        # Note: This requires editing the message, which may not be possible
                        # for all media types. This is a placeholder for the logic.
                        print(f"✅ Watermark added to thumbnail for {media_type} in channel {channel_id}")
                    
                    # Clean up
                    try:
                        os.remove(thumb_path)
                    except:
                        pass
                    
            except Exception as e:
                print(f"⚠️ Error processing thumbnail: {e}")
