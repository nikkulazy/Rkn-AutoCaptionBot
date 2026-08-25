# thumbnail_watermark.py - Complete Thumbnail Watermark System
# (c) @RknDeveloperr

import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from pyrogram.types import InputMediaPhoto

class ThumbnailWatermark:
    def __init__(self, bot):
        self.bot = bot
        self.temp_dir = "thumb_watermark"
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # 🔧 WATERMARK SETTINGS - MIDDLE + DOWN, WHITE TEXT, BLACK BACKGROUND
        self.font_size_ratio = 8        # Font size ratio (image size / 8)
        self.font_size_min = 20         # Minimum font size
        self.font_size_max = 60         # Maximum font size
        self.position_offset_y = 30     # Thoda down (30px) - Middle + Down
        self.bg_enabled = True          # Background ON
        self.bg_opacity = 80            # Black background (80% opaque)
        self.bg_padding = 20            # Padding around text
        self.text_color = (255, 255, 255, 255)  # Pure White Text
        
        self.settings = {
            "enabled": False,
            "text": "",
            "position": "center_down",
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
        """Add watermark to thumbnail image - Center + Down, Black BG, White Text"""
        try:
            if not text:
                return image_path
            
            print(f"🖼️ Adding watermark to: {image_path}")
            print(f"📝 Text: {text}")
            
            img = Image.open(image_path).convert("RGBA")
            print(f"📐 Image size: {img.size}")
            
            # Calculate font size dynamically
            font_size = int(min(img.size) / self.font_size_ratio)
            font_size = max(self.font_size_min, min(font_size, self.font_size_max))
            print(f"🔤 Font size: {font_size}")
            
            # Create watermark layer
            watermark = Image.new("RGBA", img.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(watermark)
            
            # Load font
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
                except:
                    font = ImageFont.load_default()
                    print("⚠️ Using default font")
            
            # Calculate text size
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            print(f"📏 Text size: {text_width}x{text_height}")
            
            # Position: Center + Thoda Down
            x = (img.width - text_width) // 2
            y = (img.height - text_height) // 2 + self.position_offset_y
            print(f"📍 Position: ({x}, {y}) - Center + {self.position_offset_y}px Down")
            
            # ✅ BLACK BACKGROUND BOX
            if self.bg_enabled:
                box_padding = self.bg_padding
                draw.rectangle(
                    [x - box_padding, y - box_padding, 
                     x + text_width + box_padding, y + text_height + box_padding],
                    fill=(0, 0, 0, self.bg_opacity)  # Black with opacity
                )
                print(f"📦 Added black background box (opacity: {self.bg_opacity}%)")
            
            # ✅ SHADOW (for better readability)
            shadow_offset = 2
            draw.text(
                (x + shadow_offset, y + shadow_offset),
                text,
                font=font,
                fill=(0, 0, 0, 150)  # Black shadow
            )
            
            # ✅ WHITE TEXT
            draw.text((x, y), text, font=font, fill=self.text_color)
            print("✅ White text drawn successfully")
            
            # Combine images
            combined = Image.alpha_composite(img, watermark)
            
            # Save output
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
                print("❌ No watermark text")
                return None
            
            # Only process if video has thumbnail
            if not message.video or not message.video.thumbs:
                print("ℹ️ No thumbnail found in video")
                return None
            
            thumb_path = await self.download_thumbnail(message)
            if not thumb_path:
                print("❌ Failed to download thumbnail")
                return None
            
            print(f"📥 Downloaded: {thumb_path}")
            
            watermarked_path = await self.add_watermark(thumb_path, text)
            
            if watermarked_path and os.path.exists(watermarked_path):
                # Rename watermarked file to original path
                os.replace(watermarked_path, thumb_path)
                print(f"✅ Watermarked: {thumb_path}")
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
            
            # Keep original caption
            caption = message.caption or ""
            
            await self.bot.edit_message_media(
                chat_id=message.chat.id,
                message_id=message.id,
                media=InputMediaPhoto(
                    media=thumb_path,
                    caption=caption
                )
            )
            print("✅ Thumbnail replaced successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Replace thumbnail error: {e}")
            return False

# Global instance
thumb_watermark = None

async def init_thumb_watermark(bot):
    global thumb_watermark
    thumb_watermark = ThumbnailWatermark(bot)
    return thumb_watermark
