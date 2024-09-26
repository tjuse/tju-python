from tju.consts import PROFILE_URL_PATH
from tju.exceptions import DataError
from tju.models import Profile
from tju.parser import parse_profile

from ..base import BaseClient


class ProfileMixin(BaseClient):
    def __init__(self):
        super().__init__()

    @property
    def profile(self) -> Profile:
        """Get the user profile of the current session."""
        if "profile" not in self._session._cache:
            profile_html = self._session.get(PROFILE_URL_PATH).text
            self._session._cache["profile"] = parse_profile(profile_html)
        profile = Profile.Schema().load(self._session._cache["profile"])
        if not isinstance(profile, Profile):
            raise DataError("Invalid profile")
        return profile
