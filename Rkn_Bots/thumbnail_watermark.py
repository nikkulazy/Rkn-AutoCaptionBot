# thumbnail_watermark.py - Complete Thumbnail Watermark System
# (c) @RknDeveloperr

import os
import asyncio
import aiohttp
import io
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageOps
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import Rkn_Bots

class ThumbnailWatermark:
    def __init__(self, bot):
        self.bot = bot
        self.temp_dir = "thumb_watermark"
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Load settings from config
        self.settings = {
            "enabled": Rkn_Bots.THUMB_WATERMARK_ENABLED if hasattr(Rkn_Bots, 'THUMB_WATERMARK_ENABLED') else True,
            "text": Rkn_Bots.THUMB_WATERMARK_TEXT if hasattr(Rkn_Bots, 'THUMB_WATERMARK_TEXT') else "📢 @WOLVERIN_P",
            "position": Rkn_Bots.THUMB_WATERMARK_POSITION if hasattr(Rkn_Bots, 'THUMB_WATERMARK_POSITION') else "bottom-right",
            "font_size": Rkn_Bots.THUMB_WATERMARK_FONT_SIZE if hasattr(Rkn_Bots, 'THUMB_WATERMARK_FONT_SIZE') else 20,
            "opacity": Rkn_Bots.THUMB_WATERMARK_OPACITY if hasattr(Rkn_Bots, 'THUMB_WATERMARK_OPACITY') else 70,
            "color": Rkn_Bots.THUMB_WATERMARK_COLOR if hasattr(Rkn_Bots, 'THUMB_WATERMARK_COLOR') else "white",
            "shadow": Rkn_Bots.THUMB_WATERMARK_SHADOW if hasattr(Rkn_Bots, 'THUMB_WATERMARK_SHADOW') else True,
            "background": Rkn_Bots.THUMB_WATERMARK_BACKGROUND if hasattr(Rkn_Bots, 'THUMB_WATERMARK_BACKGROUND') else "transparent",
            "padding": 10
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
    
    async def add_watermark(self, image_path, settings=None):
        """Add watermark to thumbnail image"""
        try:
            if settings:
                self.settings.update(settings)
            
            if not self.settings["enabled"]:
                return image_path
            
            # Open image
            img = Image.open(image_path).convert("RGBA")
            
            # Resize if too large
            max_size = 1280
            if img.width > max_size or img.height > max_size:
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Create watermark layer
            watermark = Image.new("RGBA", img.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(watermark)
            
            # Calculate font size
            font_size = int(min(img.size) * (self.settings["font_size"] / 100))
            font_size = max(10, min(font_size, 80))
            
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
                except:
                    font = ImageFont.load_default()
            
            # Get text dimensions
            text = self.settings["text"]
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Calculate position
            padding = self.settings["padding"]
            position = self.settings["position"]
            
            if position == "top-left":
                x = padding
                y = padding
            elif position == "top-right":
                x = img.width - text_width - padding
                y = padding
            elif position == "bottom-left":
                x = padding
                y = img.height - text_height - padding
            elif position == "bottom-right":
                x = img.width - text_width - padding
                y = img.height - text_height - padding
            elif position == "center":
                x = (img.width - text_width) // 2
                y = (img.height - text_height) // 2
            else:
                x = img.width - text_width - padding
                y = img.height - text_height - padding
            
            # Background box
            if self.settings["background"] != "transparent":
                bg_color = (0, 0, 0, 180) if self.settings["background"] == "black" else (255, 255, 255, 180)
                box_padding = 10
                draw.rectangle(
                    [x - box_padding, y - box_padding, 
                     x + text_width + box_padding, y + text_height + box_padding],
                    fill=bg_color
                )
            
            # Shadow
            if self.settings["shadow"]:
                shadow_offset = 2
                draw.text(
                    (x + shadow_offset, y + shadow_offset),
                    text,
                    font=font,
                    fill=(0, 0, 0, 128)
                )
            
            # Main text
            opacity = int(255 * (self.settings["opacity"] / 100))
            color = self.settings["color"].lower()
            
            color_map = {
                "white": (255, 255, 255, opacity),
                "black": (0, 0, 0, opacity),
                "red": (255, 0, 0, opacity),
                "blue": (0, 0, 255, opacity),
                "green": (0, 255, 0, opacity),
                "yellow": (255, 255, 0, opacity),
                "orange": (255, 165, 0, opacity),
                "purple": (128, 0, 128, opacity)
            }
            
            text_color = color_map.get(color, (255, 255, 255, opacity))
            draw.text((x, y), text, font=font, fill=text_color)
            
            # Composite
            combined = Image.alpha_composite(img, watermark)
            
            # Convert back
            output_path = image_path.replace(".jpg", "_watermarked.jpg")
            combined.convert("RGB").save(output_path, quality=95)
            
            return output_path
            
        except Exception as e:
            print(f"❌ Watermark error: {e}")
            return image_path
    
    async def process_thumbnail(self, message):
        """Process thumbnail with watermark"""
        try:
            # Download thumbnail
            thumb_path = await self.download_thumbnail(message)
            if not thumb_path:
                return None
            
            # Add watermark
            watermarked_path = await self.add_watermark(thumb_path)
            
            # Clean up original
            try:
                os.remove(thumb_path)
            except:
                pass
            
            return watermarked_path
            
        except Exception as e:
            print(f"❌ Process thumbnail error: {e}")
            return None
    
    async def get_settings_preview(self):
        """Get current settings for preview"""
        return f"""
📋 **Thumbnail Watermark Settings**

🎯 **Status:** {'✅ Enabled' if self.settings['enabled'] else '❌ Disabled'}
📝 **Text:** `{self.settings['text']}`
📍 **Position:** {self.settings['position']}
📏 **Font Size:** {self.settings['font_size']}%
🎨 **Opacity:** {self.settings['opacity']}%
🌈 **Color:** {self.settings['color']}
👻 **Shadow:** {'✅' if self.settings['shadow'] else '❌'}
📦 **Background:** {self.settings['background']}
🔲 **Padding:** {self.settings['padding']}px
"""

    async def update_setting(self, key, value):
        """Update a single setting"""
        if key in self.settings:
            self.settings[key] = value
            # Also update config
            if hasattr(Rkn_Bots, f'THUMB_WATERMARK_{key.upper()}'):
                setattr(Rkn_Bots, f'THUMB_WATERMARK_{key.upper()}', value)
            return True
        return False

# ==================== HELPER FUNCTIONS ====================

thumb_watermark = None

async def init_thumb_watermark(bot):
    global thumb_watermark
    thumb_watermark = ThumbnailWatermark(bot)
    return thumb_watermark

async def create_sample_thumbnail():
    """Create a sample thumbnail for preview"""
    try:
        # Create temp directory
        temp_dir = "thumb_watermark"
        os.makedirs(temp_dir, exist_ok=True)
        
        # Create a sample image
        img = Image.new('RGB', (640, 360), color='#1a1a2e')
        draw = ImageDraw.Draw(img)
        
        # Draw some shapes
        draw.rectangle([50, 50, 590, 310], outline='#e94560', width=3)
        
        # Add sample text
        try:
            font = ImageFont.truetype("arial.ttf", 30)
        except:
            font = ImageFont.load_default()
        
        draw.text((320, 160), "🎬 SAMPLE VIDEO", font=font, fill='white', anchor="mm")
        draw.text((320, 210), "Thumbnail Preview", font=font, fill='#e94560', anchor="mm")
        
        # Save
        path = f"{temp_dir}/sample_thumb_{datetime.now().timestamp()}.jpg"
        img.save(path, quality=95)
        
        return path
        
    except Exception as e:
        print(f"❌ Sample creation error: {e}")
        return None
