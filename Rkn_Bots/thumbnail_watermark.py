# thumbnail_watermark.py - Fixed Position, Background & Brightness
# (c) @RknDeveloperr

import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

class ThumbnailWatermark:
    def __init__(self, bot):
        self.bot = bot
        self.temp_dir = "thumb_watermark"
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # ════════════════════════════════════════════
        # 🔧 WATERMARK SETTINGS - YAHAN CHANGE KAREIN
        # ════════════════════════════════════════════
        self.font_size_ratio = 8       # Font size control
        self.font_size_min = 20        
        self.font_size_max = 60
        
        # 🎯 Position Offset (Center se thoda neeche)
        self.position_offset_y = 10    # 30px neeche (increase for more down)
        
        # 🎨 Background Settings
        self.bg_enabled = True         # Background on/off
        self.bg_opacity = 50           # 🔥 80 = Light (was 150, 0=transparent, 255=dark)
        self.bg_padding = 10           # Background box padding
        
        # ✨ Text Settings
        self.text_opacity = 255        # 🔥 255 = Fully Bright White (was 255, same but ensure)
        self.text_color = (255, 255, 255, 255)  # Bright White
        # ════════════════════════════════════════════
        
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
        """Add watermark to thumbnail image - Center + Down, Light Background, Bright White"""
        try:
            if not text:
                return image_path
            
            print(f"🖼️ Adding watermark to: {image_path}")
            print(f"📝 Text: {text}")
            
            # Open image
            img = Image.open(image_path).convert("RGBA")
            print(f"📐 Image size: {img.size}")
            
            # Calculate font size
            font_size = int(min(img.size) / self.font_size_ratio)
            font_size = max(self.font_size_min, min(font_size, self.font_size_max))
            print(f"🔤 Font size: {font_size}")
            
            # Create watermark layer
            watermark = Image.new("RGBA", img.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(watermark)
            
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
                except:
                    font = ImageFont.load_default()
                    print("⚠️ Using default font")
            
            # Get text dimensions
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            print(f"📏 Text size: {text_width}x{text_height}")
            
            # 🎯 Position: Center + Down (Y offset)
            x = (img.width - text_width) // 2
            y = (img.height - text_height) // 2 + self.position_offset_y
            print(f"📍 Position: ({x}, {y}) [Center + {self.position_offset_y}px down]")
            
            # 🎨 Background Box (Lighter)
            if self.bg_enabled:
                box_padding = self.bg_padding
                # 🔥 Light Background with less opacity
                bg_opacity = self.bg_opacity  # 80 = Light
                draw.rectangle(
                    [x - box_padding, y - box_padding, 
                     x + text_width + box_padding, y + text_height + box_padding],
                    fill=(0, 0, 0, bg_opacity)  # Light black background
                )
                print(f"📦 Added background box (opacity: {bg_opacity})")
            
            # ✨ Shadow (thoda light)
            shadow_offset = 2
            draw.text(
                (x + shadow_offset, y + shadow_offset),
                text,
                font=font,
                fill=(0, 0, 0, 150)  # Shadow
            )
            
            # ✨ Bright White Text (Fully White)
            draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
            print("✅ Bright white text drawn successfully")
            
            # Composite
            combined = Image.alpha_composite(img, watermark)
            
            # Save
            output_path = image_path.replace(".jpg", "_watermarked.jpg")
            combined.convert("RGB").save(output_path, quality=95)
            print(f"💾 Saved: {output_path}")
            
            return output_path
            
        except Exception as e:
            print(f"❌ Watermark error: {e}")
            import traceback
            traceback.print_exc()
            return image_path
    
    async def process_thumbnail(self, message, text):
        """Process thumbnail with watermark"""
        try:
            if not text:
                return None
            
            # Download thumbnail
            thumb_path = await self.download_thumbnail(message)
            if not thumb_path:
                print("❌ No thumbnail downloaded")
                return None
            
            print(f"📥 Downloaded: {thumb_path}")
            
            # Add watermark
            watermarked_path = await self.add_watermark(thumb_path, text)
            
            if watermarked_path and os.path.exists(watermarked_path):
                print(f"✅ Watermarked: {watermarked_path}")
                
                # Rename watermarked to original
                os.rename(watermarked_path, thumb_path)
                print(f"📝 Renamed watermarked to: {thumb_path}")
                
                return thumb_path
            
            return None
            
        except Exception as e:
            print(f"❌ Process thumbnail error: {e}")
            import traceback
            traceback.print_exc()
            return None

    async def replace_thumbnail(self, message, thumb_path):
        """Replace video thumbnail with watermarked one"""
        try:
            if not thumb_path or not os.path.exists(thumb_path):
                return False
            
            print(f"🔄 Replacing thumbnail for message: {message.id}")
            
            if not message.video:
                return False
            
            from pyrogram.types import InputMediaPhoto
            
            await self.bot.edit_message_media(
                chat_id=message.chat.id,
                message_id=message.id,
                media=InputMediaPhoto(
                    media=thumb_path,
                    caption=message.caption or ""
                )
            )
            print("✅ Thumbnail replaced successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Replace thumbnail error: {e}")
            return False

# ==================== GLOBAL INSTANCE ====================

thumb_watermark = None

async def init_thumb_watermark(bot):
    global thumb_watermark
    thumb_watermark = ThumbnailWatermark(bot)
    return thumb_watermark
