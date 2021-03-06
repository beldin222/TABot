import discord
from discord.ext import commands
import configparser


class Config(commands.Cog):
    def __init__(self, bot):
        # Initialize config
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
        self.token = self.config["Settings"]["Token"]
        self.parser = self.config

    # Just a wrapper for the config function, makes it a little more convient to use.
    def get_server_config(self, server_id, key):
        try:
            response = self.config[str(server_id)][str(key)]
        except KeyError:
            response = None
        return response

    # Takes tuple, unpacks and sets changes and saves them to local config
    def set_server_config(self, data: tuple):
        """Allows server configs to be set in a somewhat prettier manner,
            while handling inconsistent key types (they're always converted to
            strings, since configparser doesn't like numerical keys.)

        Example Usage:
            server_config = (server_id, key, value)

        Args:
            data (tuple)
        """
        (server_id, key, value) = data
        try:
            self.config[str(server_id)]
        except KeyError:
            self.config[str(server_id)] = {}
        self.config[str(server_id)][str(key)] = str(value)
        with open("config.ini", "w") as configfile:
            self.config.write(configfile)
        return

    server_config = property(get_server_config, set_server_config)


def setup(bot):
    bot.add_cog(Config(bot))
