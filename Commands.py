import discord
from discord.ext import commands
import asyncio
import tracemalloc
from Config import client, bot_status, blacklisted_words, token, support_role

# Kick command
@client.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'{member.mention} has been kicked.')

# Ban command
@client.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'{member.mention} has been banned.')

# Give role command
@client.command()
@commands.has_permissions(manage_roles=True)
async def giverole(ctx, member: discord.Member, role: discord.Role):
    await member.add_roles(role)
    message = await ctx.send(f'{member.mention} has been given the {role.name} role.')
    await asyncio.sleep(3)
    await message.delete()
    await ctx.channel.purge(limit=1, check=lambda m: m.author == member)

# Remove role command
@client.command()
@commands.has_permissions(manage_roles=True)
async def removerole(ctx, member: discord.Member, role: discord.Role):
    await member.remove_roles(role)
    message = await ctx.send(f'{member.mention} has had the {role.name} role removed.')
    await asyncio.sleep(3)
    await message.delete()
    await ctx.channel.purge(limit=1, check=lambda m: m.author == member)

# Ticket command
@client.command()
async def ticket(ctx):
    category = discord.utils.get(ctx.guild.categories, name='Tickets')
    ticket_channel = await ctx.guild.create_text_channel(name=f'ticket-{ctx.author.display_name}', category=category)
    await ticket_channel.set_permissions(ctx.author, read_messages=True, send_messages=True)
    staff_role = discord.utils.get(ctx.guild.roles, name=support_role)
    await ticket_channel.set_permissions(ctx.guild.default_role, read_messages=False) # remove read permissions for everyone
    await ticket_channel.set_permissions(staff_role, read_messages=True) # allow staff to read messages

    # Add the "X" reaction to the ticket channel's first message
    message = await ticket_channel.send('React below to close ticket')
    await message.add_reaction('❌')

    # Wait for the "X" reaction and delete the ticket channel if it's added
    def check(reaction, user):
        return str(reaction.emoji) == '❌' and user == ctx.author and reaction.message.channel == ticket_channel

    try:
        reaction, user = await client.wait_for('reaction_add', check=check, timeout=3400)
    except asyncio.TimeoutError:
        await ticket_channel.send('Ticket closed due to inactivity.')
    else:
        await ticket_channel.delete()
        await ctx.send(f'{ctx.author.mention}, your ticket has been closed.')

# Purge command
@client.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, limit: int):
    await ctx.message.delete()
    deleted = await ctx.channel.purge(limit=limit)
    await ctx.send(f"Deleted {len(deleted)} message(s).", delete_after=3)

# List commands
@client.command()
async def botCommands(ctx):
    tracemalloc.start()
    message = await ctx.send(
     """!purge
     !ticket
     !kick
     !ban
     !giverole
     !removerole
     !get_key
     !redeem_key
     """)

    await asyncio.sleep(3)

    await message.delete()
    await ctx.message.delete()

    tracemalloc.stop()

# Blacklist Words
@client.event
async def on_message(message):
    for word in blacklisted_words:
        if word in message.content.lower():
            await message.delete()
            await message.channel.send(f"{message.author.mention}, your message contained a blacklisted word and has been deleted.")
            await asyncio.sleep(3)
            return
    await client.process_commands(message)


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name=bot_status))

client.run(token)
