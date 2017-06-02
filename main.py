import discord
import webhook
import chatexchange
import html
from bs4 import BeautifulSoup


class TNBForwarder(discord.Client):
    room_id = "240"
    channel_id = "320121540022632459"

    async def on_ready(self):
        channel = self.get_channel(TNBForwarder.channel_id)

        self.webhooks = await self.get_webhooks(channel)
        #await self.webhook.execute("Test message", username="TestUsername", avatar_url="http://www.gravatar.com/avatar/1a37ae2ad0be3772ffa87aacc07ab5a1")
        self.chatexchange = chatexchange.Client(email="stackexchange_username", password="stackexchangepassword")
        self.chatroom = self.chatexchange.get_room(TNBForwarder.room_id)
        print("Forwarding...", self.webhooks)
        i = 0
        with self.chatroom.new_messages() as messages:
            for message in messages:
                user = message.owner
                content = message.content
                if content.startswith('<div class='):
                    soup = BeautifulSoup(content, "html.parser")
                    content = soup.find_all("a", href=True)[0]["href"]
                    if content.startswith("//"):
                        content = "http:"+content
                elif content.startswith("<a href="):
                    content = html.unescape(content)
                    soup = BeautifulSoup(content, "html.parser")
                    content = soup.find_all("a", href=True)[0]["href"]
                else:
                    # Regular messages
                    content = html.unescape(content)
                username = user.name
                avatar_url = self.get_user_avatar_url(user.id)
                try:
                    await self.webhooks[i].execute(content, username, avatar_url)
                except discord.errors.HTTPException:
                    #print(content, username, avatar_url)
                    await self.webhook[i].execute("<Unable to parse message>", username, avatar_url)
                i += 1
                i %= len(self.webhooks)

    async def create_webhook(self, channel, name, avatar_url):
        return await webhook.Webhook.create_webhook(self.http, channel, name, avatar_url)

    async def get_webhooks(self, channel):
        return await webhook.Webhook.get_webhooks(self.http, channel)

    async def get_webhook(self, channel, name):
        webhooks = await self.get_webhooks(channel)
        return discord.utils.get(webhooks, name=name)

    def get_user_avatar_url(self, user_id):
        browser = self.chatexchange._br
        profile_soup = browser.get_soup("users/{}".format(user_id))
        return profile_soup.find("img", {"class": "user-gravatar-128"})["src"]


if __name__ == "__main__":
    bot = TNBForwarder()
    bot.run("discord_email", "discord_password")
