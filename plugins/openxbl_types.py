from typing import Any, Optional, TypedDict


class People(TypedDict):
    """A dictionary representing a People Object from Open XBL."""

    xuid: str
    isFavorite: bool
    isFollowingCaller: bool
    isFollowedByCaller: bool
    isIdentityShared: bool
    addedDateTimeUtc: Optional[str]
    displayName: Optional[str]
    realName: str
    displayPicRaw: str
    showUserAsAvatar: str
    gamertag: str
    gamerScore: str
    modernGamertag: str
    modernGamertagSuffix: str
    uniqueModernGamertag: str
    xboxOneRep: str
    presenceState: Optional[str]
    presenceText: Optional[str]
    presenceDevices: Optional[str]
    isBroadcasting: bool
    isCloaked: Optional[bool]
    isQuarantined: bool
    isXbox360Gamerpic: bool
    lastSeenDateTimeUtc: Optional[str]
    suggestion: Optional[str]
    recommendation: Optional[str]
    search: dict[str, Any]
    titleHistory: Optional[str]
    multiplayerSummary: Optional[str]
    recentPlayer: Optional[str]
    follower: Optional[str]
    preferredColor: dict[str, Any]
    presenceDetails: Optional[str]
    titlePresence: Optional[str]
    titleSummaries: Optional[str]
    presenceTitleIds: Optional[str]
    detail: dict[str, Any]
    communityManagerTitles: Optional[str]
    socialManager: Optional[str]
    broadcast: Optional[str]
    avatar: Optional[str]
    linkedAccounts: Optional[str]
    colorTheme: str
    preferredFlag: str
    preferredPlatforms: list[Any]


class ProfileSettings(TypedDict):
    """A dictionary representing profile settings."""

    id: str
    value: str


class ProfileUser(TypedDict):
    """A dictionary representing a profile user."""

    id: str
    hostId: str
    settings: list[ProfileSettings]
    isSponsoredUser: bool
