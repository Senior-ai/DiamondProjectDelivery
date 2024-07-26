from .help import dp
from .start import dp
from .handle_contact import dp
from .settings import dp
from .unknown_commands_handler import dp
from .query_messages_handler import dp


__all__ = ["dp"]


"""
When creating other files in src/commands, it is necessary to import dp from them, as done above. 
There is no need to modify anything in the list of public objects (__all__).
"""