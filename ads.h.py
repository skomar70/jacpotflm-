import logging
import aiohttp
from pyrogram import filters
from pyrogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from database.ia_filterdb import Media

# Ads text
ADS_TEXT = "🔰 Please check before downloading 🔰\n✅ Join: @YourChannel"

# Shortener configuration
API_KEY = "YOUR_API_KEY"
BASE_URL = "https://ouo.io/api/"

async def short_url(long_url: str) -> str:
    """
    Async short URL using ouo.io API
    """
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{BASE_URL}{API_KEY}?s={long_url}"
            async with session.get(url) as r:
                if r.status == 200:
                    return (await r.text()).strip()
                return long_url
    except Exception as e:
        logging.error(f"Shortlink Error: {e}")
        return long_url


def register_handlers(app, ADMIN_ID: int):
    """
    Register all handlers for inline queries and admin broadcast
    """

    @app.on_inline_query()
    async def inline_handler(client, query: InlineQuery):
        search_text = query.query.strip()
        if not search_text:
            return await query.answer(results=[])

        logging.info(f"Inline search by {query.from_user.id}: {search_text}")

        # Search movies in DB
        results = await Media.collection.find(
            {"title": {"$regex": search_text, "$options": "i"}}
        ).to_list(length=10)

        if not results:
            return await query.answer(
                results=[],
                switch_pm_text="No movies found.",
                switch_pm_parameter="start"
            )

        inline_results = []
        for movie in results:
            original_link = movie.get("file_link") or movie.get("link")
            if not original_link:
                continue

            # Async short link
            short_link = await short_url(original_link)

            text = (
                f"{ADS_TEXT}\n"
                f"🎬 {movie.get('title', 'Unknown')}\n"
                f"📁 Size: {movie.get('file_size', 'N/A')}\n"
                f"🔗 Link: {short_link}"
            )

            inline_results.append(
                InlineQueryResultArticle(
                    title=movie.get('title', 'Unknown'),
                    description=f"Size: {movie.get('file_size', 'N/A')}",
                    input_message_content=InputTextMessageContent(
                        message_text=text,
                        parse_mode="Markdown"
                    )
                )
            )

        await query.answer(results=inline_results, cache_time=0)

    @app.on_message(filters.user(ADMIN_ID) & filters.command("broadcast"))
    async def broadcast_handler(client, message):
        if not message.reply_to_message:
            return await message.reply("Reply to a message to broadcast.")
        await message.reply("Broadcast system not implemented yet.")
