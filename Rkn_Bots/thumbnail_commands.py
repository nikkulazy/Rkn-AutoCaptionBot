# thumbnail_commands.py - Complete Thumbnail Watermark Commands
# Add this to your Caption.py or keep as separate file

from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import Rkn_Bots
from .thumbnail_watermark import thumb_watermark, create_sample_thumbnail
import os

# ==================== THUMBNAIL WATERMARK COMMANDS ====================

@Client.on_message(filters.private & filters.command("setthumbwm"))
async def set_thumb_watermark(bot, message):
    """Set thumbnail watermark text"""
    user_id = message.from_user.id
    
    if user_id not in Rkn_Bots.ADMIN:
        return await message.reply("❌ Only admins can set thumbnail watermark!")
    
    if len(message.command) < 2:
        current_text = Rkn_Bots.THUMB_WATERMARK_TEXT
        return await message.reply(
            f"📝 **Set Thumbnail Watermark**\n\n"
            f"**Usage:** `/setthumbwm Your watermark text`\n\n"
            f"**Example:**\n"
            f"`/setthumbwm 📢 @wolverine273`\n"
            f"`/setthumbwm © 2024 MyChannel`\n\n"
            f"**Current Text:** `{current_text}`\n\n"
            f"**Variables:**\n"
            f"• `{channel}` - Your channel name\n"
            f"• `{date}` - Current date"
        )
    
    watermark_text = message.text.split(" ", 1)[1]
    
    # Update config
    Rkn_Bots.THUMB_WATERMARK_TEXT = watermark_text
    
    # Update global watermark instance
    if thumb_watermark:
        thumb_watermark.settings["text"] = watermark_text
    
    await message.reply(
        f"✅ **Thumbnail Watermark Updated!**\n\n"
        f"**New Watermark:**\n`{watermark_text}`\n\n"
        f"This will be applied to all new video thumbnails."
    )

@Client.on_message(filters.private & filters.command("thumbwmsettings"))
async def thumb_wm_settings(bot, message):
    """Show and manage thumbnail watermark settings"""
    user_id = message.from_user.id
    
    if user_id not in Rkn_Bots.ADMIN:
        return await message.reply("❌ Only admins can use this!")
    
    settings_text = await get_thumb_wm_settings_text()
    
    buttons = [
        [
            InlineKeyboardButton("📝 Change Text", callback_data="thumbwm_text"),
            InlineKeyboardButton("📍 Position", callback_data="thumbwm_position")
        ],
        [
            InlineKeyboardButton("📏 Font Size", callback_data="thumbwm_size"),
            InlineKeyboardButton("🎨 Opacity", callback_data="thumbwm_opacity")
        ],
        [
            InlineKeyboardButton("🌈 Color", callback_data="thumbwm_color"),
            InlineKeyboardButton("👻 Shadow", callback_data="thumbwm_shadow")
        ],
        [
            InlineKeyboardButton("📦 Background", callback_data="thumbwm_bg"),
            InlineKeyboardButton("🔲 Padding", callback_data="thumbwm_padding")
        ],
        [
            InlineKeyboardButton("✅ Enable" if not Rkn_Bots.THUMB_WATERMARK_ENABLED else "✅ Enabled", 
                               callback_data="thumbwm_enable"),
            InlineKeyboardButton("❌ Disable" if Rkn_Bots.THUMB_WATERMARK_ENABLED else "❌ Disabled", 
                               callback_data="thumbwm_disable")
        ],
        [
            InlineKeyboardButton("👁️ Preview", callback_data="thumbwm_preview"),
            InlineKeyboardButton("🏠 Back", callback_data="back_to_menu")
        ]
    ]
    
    await message.reply(
        f"**🎨 Thumbnail Watermark Settings**\n\n"
        f"{settings_text}\n\n"
        f"Select an option below:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_message(filters.private & filters.command("thumbwmpreview"))
async def thumb_wm_preview(bot, message):
    """Preview thumbnail watermark"""
    user_id = message.from_user.id
    
    if user_id not in Rkn_Bots.ADMIN:
        return await message.reply("❌ Only admins can use this!")
    
    msg = await message.reply("🔄 Generating preview...")
    
    try:
        # Create sample thumbnail
        sample_path = await create_sample_thumbnail()
        
        if sample_path and thumb_watermark:
            # Add watermark
            watermarked = await thumb_watermark.add_watermark(sample_path)
            
            if watermarked and os.path.exists(watermarked):
                await msg.delete()
                await message.reply_photo(
                    photo=watermarked,
                    caption=f"**👁️ Thumbnail Watermark Preview**\n\n"
                            f"**Current Settings:**\n"
                            f"• Text: `{Rkn_Bots.THUMB_WATERMARK_TEXT}`\n"
                            f"• Position: {Rkn_Bots.THUMB_WATERMARK_POSITION}\n"
                            f"• Font Size: {Rkn_Bots.THUMB_WATERMARK_FONT_SIZE}%\n"
                            f"• Opacity: {Rkn_Bots.THUMB_WATERMARK_OPACITY}%\n"
                            f"• Color: {Rkn_Bots.THUMB_WATERMARK_COLOR}\n"
                            f"• Shadow: {'✅' if Rkn_Bots.THUMB_WATERMARK_SHADOW else '❌'}"
                )
                
                # Cleanup
                try:
                    os.remove(sample_path)
                    os.remove(watermarked)
                except:
                    pass
                return
    
    except Exception as e:
        print(f"❌ Preview error: {e}")
    
    await msg.edit_text("❌ Failed to generate preview. Please try again.")

# ==================== CALLBACK HANDLERS ====================

@Client.on_callback_query()
async def thumb_wm_callback(bot, callback_query):
    """Handle thumbnail watermark callbacks"""
    data = callback_query.data
    
    if not data.startswith("thumbwm_") and data != "thumbwmsettings":
        return
    
    user_id = callback_query.from_user.id
    
    if user_id not in Rkn_Bots.ADMIN:
        await callback_query.answer("❌ Only admins can do this!", show_alert=True)
        return
    
    option = data.replace("thumbwm_", "")
    
    # Position options
    if option == "position":
        buttons = [
            [InlineKeyboardButton("⬆️ Top-Left", callback_data="thumbwm_pos_tl")],
            [InlineKeyboardButton("⬆️ Top-Right", callback_data="thumbwm_pos_tr")],
            [InlineKeyboardButton("⬇️ Bottom-Left", callback_data="thumbwm_pos_bl")],
            [InlineKeyboardButton("⬇️ Bottom-Right", callback_data="thumbwm_pos_br")],
            [InlineKeyboardButton("🎯 Center", callback_data="thumbwm_pos_center")],
            [InlineKeyboardButton("🔙 Back", callback_data="thumbwmsettings")]
        ]
        await callback_query.message.edit_text(
            "📍 **Select Position:**\n\nChoose where to place the watermark:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        await callback_query.answer()
        return
    
    # Position set
    if option.startswith("pos_"):
        position = option.replace("pos_", "")
        position_map = {
            "tl": "top-left",
            "tr": "top-right", 
            "bl": "bottom-left",
            "br": "bottom-right",
            "center": "center"
        }
        if position in position_map:
            Rkn_Bots.THUMB_WATERMARK_POSITION = position_map[position]
            if thumb_watermark:
                thumb_watermark.settings["position"] = position_map[position]
            await callback_query.answer(f"✅ Position set to {position_map[position]}")
            await show_thumb_settings(bot, callback_query)
        return
    
    # Enable/Disable
    if option == "enable":
        Rkn_Bots.THUMB_WATERMARK_ENABLED = True
        if thumb_watermark:
            thumb_watermark.settings["enabled"] = True
        await callback_query.answer("✅ Watermark enabled")
        await show_thumb_settings(bot, callback_query)
        return
    
    if option == "disable":
        Rkn_Bots.THUMB_WATERMARK_ENABLED = False
        if thumb_watermark:
            thumb_watermark.settings["enabled"] = False
        await callback_query.answer("❌ Watermark disabled")
        await show_thumb_settings(bot, callback_query)
        return
    
    # Shadow toggle
    if option == "shadow":
        current = Rkn_Bots.THUMB_WATERMARK_SHADOW
        Rkn_Bots.THUMB_WATERMARK_SHADOW = not current
        if thumb_watermark:
            thumb_watermark.settings["shadow"] = not current
        status = "enabled" if Rkn_Bots.THUMB_WATERMARK_SHADOW else "disabled"
        await callback_query.answer(f"✅ Shadow {status}")
        await show_thumb_settings(bot, callback_query)
        return
    
    # Preview
    if option == "preview":
        await callback_query.answer("🔄 Generating preview...")
        # Create a new message for preview
        await thumb_wm_preview(bot, callback_query.message)
        return
    
    # Back to settings
    if option == "wmsettings" or option == "back":
        await show_thumb_settings(bot, callback_query)
        return
    
    # Settings menu
    if option == "settings":
        await show_thumb_settings(bot, callback_query)
        return
    
    # Other options - show value input prompt
    if option in ["text", "size", "opacity", "color", "bg", "padding"]:
        prompt_map = {
            "text": "📝 **Enter new watermark text:**\n\nExample: `📢 @wolverine273`\n\nSend text as reply:",
            "size": "📏 **Enter font size (1-100):**\n\nExample: `25`\n\nSend number as reply:",
            "opacity": "🎨 **Enter opacity (1-100):**\n\nExample: `70`\n\nSend number as reply:",
            "color": "🌈 **Enter color:**\n\nOptions: `white`, `black`, `red`, `blue`, `green`, `yellow`, `orange`, `purple`\n\nSend color as reply:",
            "bg": "📦 **Enter background:**\n\nOptions: `transparent`, `black`, `white`\n\nSend option as reply:",
            "padding": "🔲 **Enter padding (1-30):**\n\nExample: `15`\n\nSend number as reply:"
        }
        
        # Store the option being set
        await callback_query.message.edit_text(
            f"{prompt_map.get(option, 'Enter value:')}\n\n"
            f"⚠️ Reply with the value in this chat."
        )
        
        # Store callback data for next message
        # We'll handle this in a separate message handler
        await callback_query.answer()
        return

# ==================== HELPER FUNCTIONS ====================

async def get_thumb_wm_settings_text():
    """Get formatted settings text"""
    status = Rkn_Bots.THUMB_WATERMARK_ENABLED
    return f"""
📋 **Current Settings:**

🎯 **Status:** {'✅ Enabled' if status else '❌ Disabled'}
📝 **Text:** `{Rkn_Bots.THUMB_WATERMARK_TEXT}`
📍 **Position:** `{Rkn_Bots.THUMB_WATERMARK_POSITION}`
📏 **Font Size:** `{Rkn_Bots.THUMB_WATERMARK_FONT_SIZE}%`
🎨 **Opacity:** `{Rkn_Bots.THUMB_WATERMARK_OPACITY}%`
🌈 **Color:** `{Rkn_Bots.THUMB_WATERMARK_COLOR}`
👻 **Shadow:** {'✅' if Rkn_Bots.THUMB_WATERMARK_SHADOW else '❌'}
📦 **Background:** `{Rkn_Bots.THUMB_WATERMARK_BACKGROUND}`
"""

async def show_thumb_settings(bot, callback_query):
    """Show thumbnail watermark settings"""
    settings_text = await get_thumb_wm_settings_text()
    
    buttons = [
        [
            InlineKeyboardButton("📝 Change Text", callback_data="thumbwm_text"),
            InlineKeyboardButton("📍 Position", callback_data="thumbwm_position")
        ],
        [
            InlineKeyboardButton("📏 Font Size", callback_data="thumbwm_size"),
            InlineKeyboardButton("🎨 Opacity", callback_data="thumbwm_opacity")
        ],
        [
            InlineKeyboardButton("🌈 Color", callback_data="thumbwm_color"),
            InlineKeyboardButton("👻 Shadow", callback_data="thumbwm_shadow")
        ],
        [
            InlineKeyboardButton("📦 Background", callback_data="thumbwm_bg"),
            InlineKeyboardButton("🔲 Padding", callback_data="thumbwm_padding")
        ],
        [
            InlineKeyboardButton("✅ Enable" if not Rkn_Bots.THUMB_WATERMARK_ENABLED else "✅ Enabled", 
                               callback_data="thumbwm_enable"),
            InlineKeyboardButton("❌ Disable" if Rkn_Bots.THUMB_WATERMARK_ENABLED else "❌ Disabled", 
                               callback_data="thumbwm_disable")
        ],
        [
            InlineKeyboardButton("👁️ Preview", callback_data="thumbwm_preview"),
            InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_menu")
        ]
    ]
    
    await callback_query.message.edit_text(
        f"**🎨 Thumbnail Watermark Settings**\n\n"
        f"{settings_text}\n\n"
        f"Select an option below:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    await callback_query.answer()

# ==================== HANDLE TEXT REPLIES FOR SETTINGS ====================

@Client.on_message(filters.private & filters.text & filters.reply)
async def handle_thumb_settings_reply(bot, message):
    """Handle text replies for settings"""
    user_id = message.from_user.id
    
    if user_id not in Rkn_Bots.ADMIN:
        return
    
    # Check if replying to a settings message
    if not message.reply_to_message or not message.reply_to_message.text:
        return
    
    reply_text = message.reply_to_message.text
    
    # Check what setting is being set
    if "watermark text" in reply_text.lower():
        # Set text
        Rkn_Bots.THUMB_WATERMARK_TEXT = message.text
        if thumb_watermark:
            thumb_watermark.settings["text"] = message.text
        await message.reply(f"✅ Watermark text updated to: `{message.text}`")
        return
    
    elif "font size" in reply_text.lower():
        try:
            value = int(message.text)
            if 1 <= value <= 100:
                Rkn_Bots.THUMB_WATERMARK_FONT_SIZE = value
                if thumb_watermark:
                    thumb_watermark.settings["font_size"] = value
                await message.reply(f"✅ Font size updated to: {value}%")
            else:
                await message.reply("❌ Please enter a value between 1 and 100")
        except ValueError:
            await message.reply("❌ Please enter a valid number")
        return
    
    elif "opacity" in reply_text.lower():
        try:
            value = int(message.text)
            if 1 <= value <= 100:
                Rkn_Bots.THUMB_WATERMARK_OPACITY = value
                if thumb_watermark:
                    thumb_watermark.settings["opacity"] = value
                await message.reply(f"✅ Opacity updated to: {value}%")
            else:
                await message.reply("❌ Please enter a value between 1 and 100")
        except ValueError:
            await message.reply("❌ Please enter a valid number")
        return
    
    elif "color" in reply_text.lower():
        colors = ["white", "black", "red", "blue", "green", "yellow", "orange", "purple"]
        if message.text.lower() in colors:
            Rkn_Bots.THUMB_WATERMARK_COLOR = message.text.lower()
            if thumb_watermark:
                thumb_watermark.settings["color"] = message.text.lower()
            await message.reply(f"✅ Color updated to: {message.text}")
        else:
            await message.reply(f"❌ Invalid color. Options: {', '.join(colors)}")
        return
    
    elif "background" in reply_text.lower():
        options = ["transparent", "black", "white"]
        if message.text.lower() in options:
            Rkn_Bots.THUMB_WATERMARK_BACKGROUND = message.text.lower()
            if thumb_watermark:
                thumb_watermark.settings["background"] = message.text.lower()
            await message.reply(f"✅ Background updated to: {message.text}")
        else:
            await message.reply(f"❌ Invalid option. Options: {', '.join(options)}")
        return
    
    elif "padding" in reply_text.lower():
        try:
            value = int(message.text)
            if 1 <= value <= 30:
                Rkn_Bots.THUMB_WATERMARK_PADDING = value
                if thumb_watermark:
                    thumb_watermark.settings["padding"] = value
                await message.reply(f"✅ Padding updated to: {value}px")
            else:
                await message.reply("❌ Please enter a value between 1 and 30")
        except ValueError:
            await message.reply("❌ Please enter a valid number")
        return
