import sys
from typing import Union

from together.lib.utils._log import log_info
# from typing import TYPE_CHECKING

def get_google_colab_secret(secret_name: str = "TOGETHER_API_KEY") -> Union[str, None]:
    """
    Checks to see if the user is running in Google Colab, and looks for the Together API Key secret.

    Args:
        secret_name (str, optional). Defaults to TOGETHER_API_KEY

    Returns:
        str: if the API key is found; None if an error occurred or the secret was not found.
    """
    # If running in Google Colab, check for Together in notebook secrets
    if "google.colab" in sys.modules:
        from google.colab import userdata # type: ignore

        try:
            api_key = userdata.get(secret_name)
            if not isinstance(api_key, str):
                return None
            else:
                return str(api_key)
        except userdata.NotebookAccessError:
            log_info(
                "The TOGETHER_API_KEY Colab secret was found, but notebook access is disabled. Please enable notebook "
                "access for the secret."
            )
        except userdata.SecretNotFoundError:
            # warn and carry on
            log_info("Colab: No Google Colab secret named TOGETHER_API_KEY was found.")

        return None

    else:
        return None