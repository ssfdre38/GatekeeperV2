from __future__ import annotations

from discord.ext.commands import Cog
from discord.ext.commands import Bot

import os
import logging

from amp_handler import AMPHandler
from amp import AMPInstance
import db
from db import DBHandler, Database, DBConfig
from Gatekeeper import Gatekeeper

from utils.helper.command import Helper_Command


class Gatekeeper_Cog(Cog):
    def __init__(self, client: Gatekeeper) -> None:
        # Core peices to be used.
        self._client: Gatekeeper = client
        self._name: str = os.path.basename(__file__).title()
        self._logger = logging.getLogger()  # Point all print/logging statments here!

        # All our AMP Related class's
        self._AMPHandler: AMPHandler = AMPHandler()
        self._AMP: AMPInstance = self._AMPHandler.AMP  # Main AMP object
        # self.AMPInstances: dict[str, str] = self.AMPHandler.AMP_Instances #Main AMP Instance Dictionary

        # All our DB Related classes
        self._DBHandler: DBHandler = db.getDBHandler()
        self._DB: Database = self._DBHandler.DB  # Main Database object
        self._DBConfig: DBConfig = self._DB.DBConfig

        # Any Helper classes here.
        self._command_helper: Helper_Command = Helper_Command()._setup(client=self._client)

        self._logger.info(f'**SUCCESS** Initializing Cog**{self._name}**')