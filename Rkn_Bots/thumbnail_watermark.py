import os
import random
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from pyrogram.types import InputMediaPhoto

class ThumbnailWatermark:
    def __init__(self, bot):
        self.bot = bot
        self.temp_dir = "thumb_watermark"
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # 🔧 WATERMARK SETTINGS - BIGGER TEXT
        self.font_size_ratio = 6
        self.font_size_min = 50
        self.font_size_max = 120
        self.position_offset_y = 20
        self.bg_enabled = False
        self.text_color = (255, 255, 255, 255)
    
    async def download_thumbnail(self, message):
        try:
            if not message.video or not message.video.thumbs:
                print("❌ No thumbnail found in video")
                return None
            
            thumb = message.video.thumbs[0]
            unique_id = random.randint(1000, 9999)
            file_name = f"{self.temp_dir}/thumb_{message.id}_{datetime.now().timestamp()}_{unique_id}.jpg"
            
            await self.bot.download_media(thumb.file_id, file_name=file_name)
            print(f"✅ Thumbnail downloaded: {file_name}")
            return file_name
        except Exception as e:
            print(f"❌ Thumbnail download error: {e}")
            return None
    
    async def add_watermark(self, image_path, text):
        try:
            if not text:
                return image_path
            
            print(f"🖼️ Adding watermark to: {image_path}")
            
            img = Image.open(image_path).convert("RGBA")
            print(f"📐 Image size: {img.size}")
            
            # ✅ UNIQUE ID ADD KARO
            unique_id = random.randint(1000, 9999)
            text_with_id = f"{text} {unique_id}"
            print(f"📝 Text with unique ID: {text_with_id}")
            
            # Font size
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
            
            bbox = draw.textbbox((0, 0), text_with_id, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            print(f"📏 Text size: {text_width}x{text_height}")
            
            x = (img.width - text_width) // 2
            y = (img.height - text_height) // 2 + self.position_offset_y
            print(f"📍 Position: ({x}, {y})")
            
            # Shadow
            shadow_offset = 3
            draw.text(
                (x + shadow_offset, y + shadow_offset),
                text_with_id,
                font=font,
                fill=(0, 0, 0, 200)
            )
            
            # White text
            draw.text((x, y), text_with_id, font=font, fill=(255, 255, 255, 255))
            print("✅ White text drawn successfully")
            
            combined = Image.alpha_composite(img, watermark)
            
            # ✅ UNIQUE FILE NAME
            output_path = image_path.replace(".jpg", f"_{unique_id}_watermarked.jpg")
            combined.convert("RGB").save(output_path, quality=95)
            print(f"💾 Saved: {output_path}")
            
            return output_path
            
        except Exception as e:
            print(f"❌ Watermark error: {e}")
            import traceback
            traceback.print_exc()
            return image_path
    
    async def process_thumbnail(self, message, text):
        try:
            if not text:
                print("❌ No watermark text provided")
                return None
            
            thumb_path = await self.download_thumbnail(message)
            if not thumb_path:
                print("❌ Failed to download thumbnail")
                return None
            
            print(f"📥 Downloaded: {thumb_path}")
            
            watermarked_path = await self.add_watermark(thumb_path, text)
            
            if watermarked_path and os.path.exists(watermarked_path):
                if watermarked_path != thumb_path:
                    if os.path.exists(thumb_path):
                        os.remove(thumb_path)
                    os.rename(watermarked_path, thumb_path)
                    print(f"✅ Watermarked thumbnail saved: {thumb_path}")
                return thumb_path
            
            return None
            
        except Exception as e:
            print(f"❌ Process thumbnail error: {e}")
            import traceback
            traceback.print_exc()
            return None

thumb_watermark = None

async def init_thumb_watermark(bot):
    global thumb_watermark
    thumb_watermark = ThumbnailWatermark(bot)
    return thumb_watermark
