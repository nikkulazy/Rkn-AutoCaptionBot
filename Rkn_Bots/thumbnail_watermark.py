# thumbnail_watermark.py - Only Thumbnail Watermark System
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
        
        # 🔧 WATERMARK SETTINGS - Only on Thumbnail
        self.font_size_ratio = 8        # Font size ratio
        self.font_size_min = 20         # Minimum font size
        self.font_size_max = 60         # Maximum font size
        self.position_offset_y = 30     # Center + Thoda Down
        self.bg_enabled = True          # Black Background ON
        self.bg_opacity = 80            # 80% opaque
        self.bg_padding = 20            # Padding around text
        self.text_color = (255, 255, 255, 255)  # Pure White Text
        
        self.settings = {
            "enabled": False,
            "text": "",
            "position": "center_down",
            "color": "white"
        }
    
    async def download_thumbnail(self, message):
        """✅ Sirf thumbnail download karega - Video nahi"""
        try:
            # Check if video has thumbnail
            if not message.video or not message.video.thumbs:
                print("❌ No thumbnail found in video")
                return None
            
            # Get first thumbnail
            thumb = message.video.thumbs[0]
            file_name = f"{self.temp_dir}/thumb_{message.id}_{datetime.now().timestamp()}.jpg"
            
            # Download only thumbnail
            await self.bot.download_media(thumb.file_id, file_name=file_name)
            print(f"✅ Thumbnail downloaded: {file_name}")
            return file_name
        except Exception as e:
            print(f"❌ Thumbnail download error: {e}")
            return None
    
    async def add_watermark(self, image_path, text):
        """✅ Sirf thumbnail image pe watermark add karega"""
        try:
            if not text:
                return image_path
            
            print(f"🖼️ Adding watermark to thumbnail: {image_path}")
            print(f"📝 Text: {text}")
            
            # Open thumbnail image
            img = Image.open(image_path).convert("RGBA")
            print(f"📐 Thumbnail size: {img.size}")
            
            # Calculate font size
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
            
            # ✅ BLACK BACKGROUND BOX on thumbnail
            if self.bg_enabled:
                box_padding = self.bg_padding
                draw.rectangle(
                    [x - box_padding, y - box_padding, 
                     x + text_width + box_padding, y + text_height + box_padding],
                    fill=(0, 0, 0, self.bg_opacity)
                )
                print(f"📦 Added black background box on thumbnail")
            
            # ✅ SHADOW for readability
            shadow_offset = 2
            draw.text(
                (x + shadow_offset, y + shadow_offset),
                text,
                font=font,
                fill=(0, 0, 0, 150)
            )
            
            # ✅ WHITE TEXT on thumbnail
            draw.text((x, y), text, font=font, fill=self.text_color)
            print("✅ White text added to thumbnail")
            
            # Combine images
            combined = Image.alpha_composite(img, watermark)
            
            # Save watermarked thumbnail
            output_path = image_path.replace(".jpg", "_watermarked.jpg")
            combined.convert("RGB").save(output_path, quality=95)
            print(f"💾 Watermarked thumbnail saved: {output_path}")
            
            return output_path
            
        except Exception as e:
            print(f"❌ Watermark error: {e}")
            import traceback
            traceback.print_exc()
            return image_path
    
    async def process_thumbnail(self, message, text):
        """✅ Process: Sirf thumbnail download karo, watermark add karo, replace karo"""
        try:
            if not text:
                print("❌ No watermark text")
                return None
            
            # ✅ Sirf video mein thumbnail ho toh hi process karo
            if not message.video:
                print("ℹ️ Not a video message")
                return None
            
            if not message.video.thumbs:
                print("ℹ️ Video has no thumbnail")
                return None
            
            # Download thumbnail
            thumb_path = await self.download_thumbnail(message)
            if not thumb_path:
                print("❌ Failed to download thumbnail")
                return None
            
            print(f"📥 Downloaded thumbnail: {thumb_path}")
            
            # Add watermark to thumbnail
            watermarked_path = await self.add_watermark(thumb_path, text)
            
            if watermarked_path and os.path.exists(watermarked_path):
                # Replace original thumbnail with watermarked one
                os.replace(watermarked_path, thumb_path)
                print(f"✅ Watermarked thumbnail ready: {thumb_path}")
                return thumb_path
            
            return None
            
        except Exception as e:
            print(f"❌ Process thumbnail error: {e}")
            import traceback
            traceback.print_exc()
            return None

    async def replace_thumbnail(self, message, thumb_path):
        """✅ Sirf thumbnail replace karega - Video file nahi"""
        try:
            if not thumb_path or not os.path.exists(thumb_path):
                return False
            
            print(f"🔄 Replacing thumbnail for video: {message.id}")
            
            if not message.video:
                return False
            
            # Keep original caption
            caption = message.caption or ""
            
            # ✅ Sirf thumbnail replace karo, video nahi
            await self.bot.edit_message_media(
                chat_id=message.chat.id,
                message_id=message.id,
                media=InputMediaPhoto(
                    media=thumb_path,  # Sirf thumbnail image
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
