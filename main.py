import asyncio
import random
from telethon import TelegramClient, functions, types
from telethon.errors import FloodWaitError
from rich.console import Console
from rich.panel import Panel
from rich.progress import track
import questionary

console = Console()

# ========== Welcome Banner ==========
console.print(Panel.fit(
    "[bold magenta]isyrae-reactor 💖[/bold magenta]\n"
    "[white]Automate emoji reactions on Telegram messages.\nMade with love by [bold cyan]@isyrae[/bold cyan][/white]",
    border_style="magenta"))

# ========== Input Setup ==========
api_id = int(questionary.text("🔑 Enter your Telegram API ID").ask())
api_hash = questionary.text("🔐 Enter your Telegram API HASH").ask().strip()
session_name = questionary.text("📁 Session name (e.g. isyrae)").ask().strip()
target_username = questionary.text("🎯 Target Username (without @)").ask().strip()

reaction_pool = questionary.checkbox(
    "💖 Select your favorite reaction emojis",
    choices=["❤️", "🥰", "🔥", "😍", "😳", "😎", "💋", "👍", "👏"]
).ask()

if not reaction_pool:
    console.print("[bold red]❌ No emoji selected! Exiting.[/bold red]")
    exit()

# ========== Async Main Logic ==========
async def main():
    client = TelegramClient(session_name, api_id, api_hash)
    await client.start()
    console.print("[bold green]✅ Successfully logged into Telegram.[/bold green]")

    try:
        user = await client.get_entity(target_username)
    except Exception as e:
        console.print(f"[bold red]❌ Failed to find user:[/bold red] {e}")
        return

    console.print(f"[cyan]📩 Fetching messages from:[/cyan] @{target_username}")
    reacted = 0
    skipped = 0

    async for msg in client.iter_messages(user, reverse=True):
        if msg.sender_id != user.id:
            continue
        if msg.reactions and any(r.chosen for r in msg.reactions.results or []):
            skipped += 1
            continue

        emoji = random.choice(reaction_pool)

        try:
            await client(functions.messages.SendReactionRequest(
                peer=msg.peer_id,
                msg_id=msg.id,
                reaction=[types.ReactionEmoji(emoticon=emoji)],
                big=True
            ))
            console.print(f"{emoji} [green]Reacted to message[/green] [bold]#{msg.id}[/bold]")
            reacted += 1
            await asyncio.sleep(1.5)

        except FloodWaitError as e:
            wait_time = e.seconds + 5
            console.print(f"[yellow]⏳ Rate limit hit! Waiting {wait_time} seconds...[/yellow]")
            await asyncio.sleep(wait_time)
        except Exception as e:
            console.print(f"[red]⚠️ Error on msg {msg.id}:[/red] {e}")
            await asyncio.sleep(2)

    await client.disconnect()
    console.print(Panel.fit(
        f"[bold green]🎉 Done! Reacted to {reacted} messages.[/bold green]\n"
        f"[dim]Skipped {skipped} that already had reactions.[/dim]",
        border_style="bright_magenta"))

# ========== Run ==========
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[red]🛑 Script interrupted by user.[/red]")
