# thumbnail_watermark.py - Thumbnail Watermark System
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
        
        # 🔧 WATERMARK SETTINGS
        self.font_size_ratio = 8
        self.font_size_min = 20
        self.font_size_max = 60
        self.position_offset_y = 30     # Center + Thoda Down
        self.bg_enabled = True
        self.bg_opacity = 80
        self.bg_padding = 20
        self.text_color = (255, 255, 255, 255)  # Pure White Text
    
    async def download_thumbnail(self, message):
        """Download thumbnail from video or document"""
        try:
            thumb = None
            
            if message.video and message.video.thumbs:
                thumb = message.video.thumbs[0]
                print("📸 Thumbnail from video")
            elif message.document and message.document.thumbs:
                thumb = message.document.thumbs[0]
                print("📸 Thumbnail from document")
            else:
                print("❌ No thumbnail found")
                return None
            
            file_name = f"{self.temp_dir}/thumb_{message.id}_{datetime.now().timestamp()}.jpg"
            await self.bot.download_media(thumb.file_id, file_name=file_name)
            print(f"✅ Thumbnail downloaded: {file_name}")
            return file_name
            
        except Exception as e:
            print(f"❌ Thumbnail download error: {e}")
            return None
    
    async def add_watermark(self, image_path, text):
        """Add watermark to thumbnail"""
        try:
            if not text:
                return image_path
            
            print(f"🖼️ Adding watermark to thumbnail: {image_path}")
            print(f"📝 Text: {text}")
            
            img = Image.open(image_path).convert("RGBA")
            print(f"📐 Thumbnail size: {img.size}")
            
            font_size = int(min(img.size) / self.font_size_ratio)
            font_size = max(self.font_size_min, min(font_size, self.font_size_max))
            print(f"🔤 Font size: {font_size}")
            
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
            
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            print(f"📏 Text size: {text_width}x{text_height}")
            
            # Position: Center + Thoda Down
            x = (img.width - text_width) // 2
            y = (img.height - text_height) // 2 + self.position_offset_y
            print(f"📍 Position: ({x}, {y})")
            
            # BLACK BACKGROUND BOX
            if self.bg_enabled:
                box_padding = self.bg_padding
                draw.rectangle(
                    [x - box_padding, y - box_padding, 
                     x + text_width + box_padding, y + text_height + box_padding],
                    fill=(0, 0, 0, self.bg_opacity)
                )
                print(f"📦 Added black background box")
            
            # SHADOW
            shadow_offset = 2
            draw.text(
                (x + shadow_offset, y + shadow_offset),
                text,
                font=font,
                fill=(0, 0, 0, 150)
            )
            
            # WHITE TEXT
            draw.text((x, y), text, font=font, fill=self.text_color)
            print("✅ White text added")
            
            combined = Image.alpha_composite(img, watermark)
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
            
            # Check if message has video or document with thumbnail
            has_thumbnail = False
            
            if message.video and message.video.thumbs:
                has_thumbnail = True
                print("✅ Video with thumbnail found")
            
            if message.document and message.document.thumbs:
                video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.3gp', '.ts']
                file_name = getattr(message.document, 'file_name', '')
                if any(file_name.lower().endswith(ext) for ext in video_extensions):
                    has_thumbnail = True
                    print("✅ Document (video file) with thumbnail found")
            
            if not has_thumbnail:
                print("ℹ️ No thumbnail found")
                return None
            
            thumb_path = await self.download_thumbnail(message)
            if not thumb_path:
                print("❌ Failed to download thumbnail")
                return None
            
            print(f"📥 Downloaded: {thumb_path}")
            
            watermarked_path = await self.add_watermark(thumb_path, text)
            
            if watermarked_path and os.path.exists(watermarked_path):
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
        """Replace thumbnail"""
        try:
            if not thumb_path or not os.path.exists(thumb_path):
                return False
            
            print(f"🔄 Replacing thumbnail for message: {message.id}")
            
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
