# thumbnail_watermark.py - Simple Thumbnail Watermark System
# (c) @RknDeveloperr

import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

class ThumbnailWatermark:
    def __init__(self, bot):
        self.bot = bot
        self.temp_dir = "thumb_watermark"
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Always Center and White
        self.settings = {
            "enabled": False,
            "text": "",
            "position": "center",
            "color": "white"
        }
    
    async def download_thumbnail(self, message):
        """Download thumbnail from video message"""
        try:
            if not message.video or not message.video.thumbs:
                return None
            
            thumb = message.video.thumbs[0]
            file_name = f"{self.temp_dir}/thumb_{message.id}_{datetime.now().timestamp()}.jpg"
            
            await self.bot.download_media(thumb.file_id, file_name=file_name)
            return file_name
        except Exception as e:
            print(f"❌ Thumbnail download error: {e}")
            return None
    
    async def add_watermark(self, image_path, text):
        """Add watermark to thumbnail image - Always Center and White"""
        try:
            if not text:
                return image_path
            
            # Open image
            img = Image.open(image_path).convert("RGBA")
            
            # Create watermark layer
            watermark = Image.new("RGBA", img.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(watermark)
            
            # Calculate font size (auto-adjust based on image size)
            font_size = int(min(img.size) / 8)
            font_size = max(20, min(font_size, 60))
            
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
                except:
                    font = ImageFont.load_default()
            
            # Get text dimensions
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Always Center
            x = (img.width - text_width) // 2
            y = (img.height - text_height) // 2
            
            # Shadow for better visibility
            shadow_offset = 2
            draw.text(
                (x + shadow_offset, y + shadow_offset),
                text,
                font=font,
                fill=(0, 0, 0, 128)
            )
            
            # Always White
            draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
            
            # Composite
            combined = Image.alpha_composite(img, watermark)
            
            # Save
            output_path = image_path.replace(".jpg", "_watermarked.jpg")
            combined.convert("RGB").save(output_path, quality=95)
            
            return output_path
            
        except Exception as e:
            print(f"❌ Watermark error: {e}")
            return image_path
    
    async def process_thumbnail(self, message, text):
        """Process thumbnail with watermark"""
        try:
            if not text:
                return None
            
            # Download thumbnail
            thumb_path = await self.download_thumbnail(message)
            if not thumb_path:
                return None
            
            # Add watermark
            watermarked_path = await self.add_watermark(thumb_path, text)
            
            # Clean up original
            try:
                os.remove(thumb_path)
            except:
                pass
            
            return watermarked_path
            
        except Exception as e:
            print(f"❌ Process thumbnail error: {e}")
            return None

# ==================== GLOBAL INSTANCE ====================

thumb_watermark = None

async def init_thumb_watermark(bot):
    global thumb_watermark
    thumb_watermark = ThumbnailWatermark(bot)
    return thumb_watermark
