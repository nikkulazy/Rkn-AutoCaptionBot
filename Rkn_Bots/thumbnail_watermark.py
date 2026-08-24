from pyrogram import Client, filters, types, enums
from PIL import Image, ImageDraw, ImageFont
import os, asyncio

print("🔄 Loading thumbnail_watermark.py...")

# ==================== ADD WATERMARK TO THUMBNAIL ====================

async def add_watermark_to_image(image_path, watermark_text=None):
    """Add watermark text to image"""
    try:
        # Open image
        img = Image.open(image_path)
        
        # Create drawing object
        draw = ImageDraw.Draw(img)
        
        # Load default font
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        # Watermark text
        if not watermark_text:
            watermark_text = "@RknDeveloper"
        
        # Get image dimensions
        width, height = img.size
        
        # Calculate text position (bottom-right corner)
        text_width = draw.textlength(watermark_text, font=font)
        text_height = 20
        x = width - text_width - 20
        y = height - text_height - 20
        
        # Add semi-transparent background for better readability
        draw.rectangle(
            [x - 10, y - 10, x + text_width + 10, y + text_height + 10],
            fill=(0, 0, 0, 128)
        )
        
        # Add watermark text
        draw.text((x, y), watermark_text, fill=(255, 255, 255), font=font)
        
        # Save image
        img.save(image_path)
        return True
        
    except Exception as e:
        print(f"❌ Watermark error: {e}")
        return False

# ==================== AUTO WATERMARK ON PHOTOS ====================

@Client.on_message(filters.photo & filters.private)
async def auto_watermark_photo(client, message):
    """Auto add watermark to photos"""
    try:
        # Download photo
        photo_path = await message.download()
        
        # Add watermark
        await add_watermark_to_image(photo_path, "@RknDeveloper")
        
        # Send back
        await message.reply_photo(
            photo=photo_path,
            caption="✅ **Watermark Added!**\n\n📌 @RknDeveloper"
        )
        
        # Clean up
        os.remove(photo_path)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        await message.reply(f"❌ Error: {e}")

# ==================== THUMBNAIL WATERMARK FOR FILES ====================

@Client.on_message(filters.document | filters.video)
async def auto_watermark_file(client, message):
    """Add watermark to file thumbnails"""
    try:
        # Check if file has thumbnail
        if hasattr(message, 'thumb') and message.thumb:
            # Download thumbnail
            thumb_path = await message.download_thumb()
            
            if thumb_path:
                # Add watermark
                await add_watermark_to_image(thumb_path, "@RknDeveloper")
                
                # Send thumbnail back
                await message.reply_photo(
                    photo=thumb_path,
                    caption="✅ **Thumbnail Watermark Added!**\n\n📌 @RknDeveloper"
                )
                
                # Clean up
                os.remove(thumb_path)
        
    except Exception as e:
        print(f"❌ Thumbnail watermark error: {e}")

# ==================== COMMAND TO ADD WATERMARK ====================

@Client.on_message(filters.command("watermark") & filters.private)
async def watermark_cmd(client, message):
    """Manual watermark command"""
    if message.reply_to_message and message.reply_to_message.photo:
        try:
            # Download photo
            photo_path = await message.reply_to_message.download()
            
            # Add watermark
            await add_watermark_to_image(photo_path, "@RknDeveloper")
            
            # Send back
            await message.reply_photo(
                photo=photo_path,
                caption="✅ **Watermark Added Successfully!**\n\n📌 @RknDeveloper"
            )
            
            # Clean up
            os.remove(photo_path)
            
        except Exception as e:
            await message.reply(f"❌ Error: {e}")
    else:
        await message.reply(
            f"**📌 How to add watermark:**\n\n"
            f"Reply to a photo with `/watermark` command.\n\n"
            f"**Example:**\n"
            f"`/watermark` (reply to a photo)\n\n"
            f"✅ Watermark text: @RknDeveloper"
        )

print("✅ thumbnail_watermark.py loaded successfully!")
