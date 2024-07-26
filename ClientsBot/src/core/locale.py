import gettext
import os


def setup_locale():
    # Set the locale directory
    localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')

    # Set the text domain
    gettext.bindtextdomain('messages', localedir)
    gettext.textdomain('messages')

    # Create a translation object
    translation = gettext.translation('messages', localedir, fallback=True)

    # Install the translation object
    translation.install()
