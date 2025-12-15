# This code comes from typer github repository comments section about aliasing commands
# This is extension for Typer to support command aliases
# Ref: https://github.com/fastapi/typer/issues/132#issuecomment-2417492805
# To be deleted after Typer supports command aliases natively
import re

import typer
import typer.core


class AliasGroup(typer.core.TyperGroup):
    """Typer Group subclass that supports commands with aliases.
    To alias a command, include the aliases in the command name,
    separated by commas.
    """

    _CMD_SPLIT_P = re.compile(r" ?[,|] ?")

    def get_command(self, ctx, cmd_name):
        cmd_name = self._group_cmd_name(self.commands.values(), cmd_name)
        return super().get_command(ctx, cmd_name)

    def _group_cmd_name(self, group_command_names, default_name):
        for cmd in group_command_names:
            if cmd.name and default_name in self._CMD_SPLIT_P.split(cmd.name):
                return cmd.name
        return default_name
