"""Data classes and types from the JSON-RPC."""

# flake8: noqa
from dataclasses import dataclass
from enum import IntEnum, StrEnum
from typing import Any, Literal, Optional, TypeAlias, TypeVar

from dacite import Config as _Config
from dacite import from_dict as __from_dict

from ._utils import camel2snake_dict as _camel2snake_dict

_config = _Config(cast=[StrEnum], type_hooks={})
_T = TypeVar("T")


def _from_dict(typ: type[_T], data: dict) -> _T:
    return __from_dict(typ, _camel2snake_dict(data), _config)


class ContactFlag(IntEnum):
    """Contact flags used for filtering"""

    VERIFIED_ONLY = 0x01
    ADD_SELF = 0x02


class ChatlistFlag(IntEnum):
    """Chatlist flags used for filtering"""

    ARCHIVED_ONLY = 0x01
    NO_SPECIALS = 0x02
    ADD_ALLDONE_HINT = 0x04
    FOR_FORWARDING = 0x08


class SpecialContactId(IntEnum):
    """Special contact IDs"""

    SELF = 1
    INFO = 2  # centered messages as "member added", used in all chats
    DEVICE = 5  #  messages "update info" in the device-chat
    LAST_SPECIAL = 9


class MessageState(IntEnum):
    """State of the message."""

    UNDEFINED = 0
    IN_FRESH = 10
    IN_NOTICED = 13
    IN_SEEN = 16
    OUT_PREPARING = 18
    OUT_DRAFT = 19
    OUT_PENDING = 20
    OUT_FAILED = 24
    OUT_DELIVERED = 26
    OUT_MDN_RCVD = 28


@dataclass(kw_only=True)
class AccountConfigured:
    addr: Optional[str] = None
    color: str
    display_name: Optional[str] = None
    id: int

    # Optional tag as "Work", "Family". Meant to help profile owner to differ between profiles with similar names.
    private_tag: Optional[str] = None
    profile_image: Optional[str] = None


@dataclass(kw_only=True)
class AccountUnconfigured:
    id: int


Account: TypeAlias = AccountConfigured | AccountUnconfigured


def _unmarshalAccount(data: dict) -> Account:
    kind = data.pop("kind")
    match kind:
        case "Configured":
            return _from_dict(AccountConfigured, data)
        case "Unconfigured":
            return _from_dict(AccountUnconfigured, data)
        case _:
            raise ValueError(f"Unknow Account kind: {kind}")


_config.type_hooks[Account] = _unmarshalAccount


@dataclass(kw_only=True)
class BasicChat:
    """
    cheaper version of fullchat, omits: - contact_ids - fresh_message_counter - ephemeral_timer - self_in_group - was_seen_recently - can_send

    used when you only need the basic metadata of a chat like type, name, profile picture
    """

    archived: bool
    chat_type: ChatType
    color: str
    id: int
    is_contact_request: bool
    is_device_chat: bool

    # True if the chat is encrypted. This means that all messages in the chat are encrypted, and all contacts in the chat are "key-contacts", i.e. identified by the PGP key fingerprint.
    #
    # False if the chat is unencrypted. This means that all messages in the chat are unencrypted, and all contacts in the chat are "address-contacts", i.e. identified by the email address. The UI should mark this chat e.g. with a mail-letter icon.
    #
    # Unencrypted groups are called "ad-hoc groups" and the user can't add/remove members, create a QR invite code, or set an avatar. These options should therefore be disabled in the UI.
    #
    # Note that it can happen that an encrypted chat contains unencrypted messages that were received in core <= v1.159.* and vice versa.
    #
    # See also `is_key_contact` on `Contact`.
    is_encrypted: bool
    is_muted: bool
    is_self_talk: bool
    is_unpromoted: bool
    name: str
    pinned: bool
    profile_image: Optional[str] = None


@dataclass(kw_only=True)
class CallInfo:

    # True if the call is started as a video call.
    has_video: bool

    # SDP offer.
    #
    # Can be used to manually answer the call even if incoming call event was missed.
    sdp_offer: str

    # Call state.
    #
    # For example, if the call is accepted, active, canceled, declined etc.
    state: CallState


# Fresh incoming or outgoing call that is still ringing.
#
# There is no separate state for outgoing call that has been dialled but not ringing on the other side yet as we don't know whether the other side received our call.
CallStateAlerting = Literal["Alerting"]
# Active call.
CallStateActive = Literal["Active"]


@dataclass(kw_only=True)
class CallStateCompleted:
    """Completed call that was once active and then was terminated for any reason."""

    # Call duration in seconds.
    duration: int


# Incoming call that was not picked up within a timeout or was explicitly ended by the caller before we picked up.
CallStateMissed = Literal["Missed"]
# Incoming call that was explicitly ended on our side before picking up or outgoing call that was declined before the timeout.
CallStateDeclined = Literal["Declined"]
# Outgoing call that has been canceled on our side before receiving a response.
#
# Incoming calls cannot be canceled, on the receiver side canceled calls usually result in missed calls.
CallStateCanceled = Literal["Canceled"]
CallState: TypeAlias = (
    CallStateAlerting
    | CallStateActive
    | CallStateCompleted
    | CallStateMissed
    | CallStateDeclined
    | CallStateCanceled
)


def _unmarshalCallState(data: dict) -> CallState:
    kind = data.pop("kind")
    match kind:
        case "Alerting":
            return kind
        case "Active":
            return kind
        case "Completed":
            return _from_dict(CallStateCompleted, data)
        case "Missed":
            return kind
        case "Declined":
            return kind
        case "Canceled":
            return kind
        case _:
            raise ValueError(f"Unknow CallState kind: {kind}")


_config.type_hooks[CallState] = _unmarshalCallState


@dataclass(kw_only=True)
class ChatListItemFetchResultChatListItem:
    avatar_path: Optional[str] = None
    chat_type: ChatType
    color: str

    # contact id if this is a dm chat (for view profile entry in context menu)
    dm_chat_contact: Optional[int] = None
    fresh_message_counter: int
    id: int
    is_archived: bool
    is_contact_request: bool
    is_device_talk: bool

    # True if the chat is encrypted. This means that all messages in the chat are encrypted, and all contacts in the chat are "key-contacts", i.e. identified by the PGP key fingerprint.
    #
    # False if the chat is unencrypted. This means that all messages in the chat are unencrypted, and all contacts in the chat are "address-contacts", i.e. identified by the email address. The UI should mark this chat e.g. with a mail-letter icon.
    #
    # Unencrypted groups are called "ad-hoc groups" and the user can't add/remove members, create a QR invite code, or set an avatar. These options should therefore be disabled in the UI.
    #
    # Note that it can happen that an encrypted chat contains unencrypted messages that were received in core <= v1.159.* and vice versa.
    #
    # See also `is_key_contact` on `Contact`.
    is_encrypted: bool

    # deprecated 2025-07, use chat_type instead
    is_group: bool
    is_muted: bool
    is_pinned: bool
    is_self_in_group: bool
    is_self_talk: bool
    is_sending_location: bool
    last_message_id: Optional[int] = None
    last_message_type: Optional[Viewtype] = None
    last_updated: Optional[int] = None
    name: str

    # showing preview if last chat message is image
    summary_preview_image: Optional[str] = None
    summary_status: int
    summary_text1: str
    summary_text2: str
    was_seen_recently: bool


@dataclass(kw_only=True)
class ChatListItemFetchResultArchiveLink:
    fresh_message_counter: int


@dataclass(kw_only=True)
class ChatListItemFetchResultError:
    error: str
    id: int


ChatListItemFetchResult: TypeAlias = (
    ChatListItemFetchResultChatListItem
    | ChatListItemFetchResultArchiveLink
    | ChatListItemFetchResultError
)


def _unmarshalChatListItemFetchResult(data: dict) -> ChatListItemFetchResult:
    kind = data.pop("kind")
    match kind:
        case "ChatListItem":
            return _from_dict(ChatListItemFetchResultChatListItem, data)
        case "ArchiveLink":
            return _from_dict(ChatListItemFetchResultArchiveLink, data)
        case "Error":
            return _from_dict(ChatListItemFetchResultError, data)
        case _:
            raise ValueError(f"Unknow ChatListItemFetchResult kind: {kind}")


_config.type_hooks[ChatListItemFetchResult] = _unmarshalChatListItemFetchResult


class ChatType(StrEnum):

    SINGLE = "Single"
    GROUP = "Group"
    MAILINGLIST = "Mailinglist"
    OUT_BROADCAST = "OutBroadcast"
    IN_BROADCAST = "InBroadcast"


class ChatVisibility(StrEnum):

    NORMAL = "Normal"
    ARCHIVED = "Archived"
    PINNED = "Pinned"


@dataclass(kw_only=True)
class Contact:
    address: str
    auth_name: str
    color: str
    display_name: str

    # Is encryption available for this contact.
    #
    # This can only be true for key-contacts. However, it is possible to have a key-contact for which encryption is not available because we don't have a key yet, e.g. if we just scanned the fingerprint from a QR code.
    e2ee_avail: bool
    id: int
    is_blocked: bool

    # If the contact is a bot.
    is_bot: bool

    # Is the contact a key contact.
    is_key_contact: bool

    # True if the contact can be added to protected chats because SELF and contact have verified their fingerprints in both directions.
    #
    # See [`Rpc.verifier_id`]/`Contact.verifierId` for a guidance how to display these information.
    is_verified: bool

    # the contact's last seen timestamp
    last_seen: int
    name: str
    name_and_addr: str
    profile_image: Optional[str] = None
    status: str

    # The contact ID that verified a contact.
    #
    # As verifier may be unknown, use [`Rpc.is_verified`]/`Contact.isVerified` to check if a contact can be added to a protected chat.
    #
    # UI should display the information in the contact's profile as follows:
    #
    # - If `verifierId` != 0, display text "Introduced by ..." with the name of the contact. Prefix the text by a green checkmark.
    #
    # - If `verifierId` == 0 and `isVerified` != 0, display "Introduced" prefixed by a green checkmark.
    #
    # - if `verifierId` == 0 and `isVerified` == 0, display nothing
    #
    # This contains the contact ID of the verifier. If it is `DC_CONTACT_ID_SELF`, we verified the contact ourself. If it is None/Null, we don't have verifier information or the contact is not verified.
    verifier_id: Optional[int] = None
    was_seen_recently: bool


class DownloadState(StrEnum):

    DONE = "Done"
    AVAILABLE = "Available"
    FAILURE = "Failure"
    UNDECIPHERABLE = "Undecipherable"
    IN_PROGRESS = "InProgress"


class EnteredCertificateChecks(StrEnum):
    # `Automatic` means that provider database setting should be taken. If there is no provider database setting for certificate checks, check certificates strictly.
    AUTOMATIC = "automatic"

    # Ensure that TLS certificate is valid for the server hostname.
    STRICT = "strict"

    # Accept certificates that are expired, self-signed or otherwise not valid for the server hostname.
    ACCEPT_INVALID_CERTIFICATES = "acceptInvalidCertificates"


@dataclass(kw_only=True)
class EnteredLoginParam:
    """
    Login parameters entered by the user.

    Usually it will be enough to only set `addr` and `password`, and all the other settings will be autoconfigured.
    """

    # Email address.
    addr: str

    # TLS options: whether to allow invalid certificates and/or invalid hostnames. Default: Automatic
    certificate_checks: Optional[EnteredCertificateChecks] = None

    # IMAP server folder.
    #
    # Defaults to "INBOX" if not set. Should not be an empty string.
    imap_folder: Optional[str] = None

    # Imap server port.
    imap_port: Optional[int] = None

    # Imap socket security.
    imap_security: Optional[Socket] = None

    # Imap server hostname or IP address.
    imap_server: Optional[str] = None

    # Imap username.
    imap_user: Optional[str] = None

    # If true, login via OAUTH2 (not recommended anymore). Default: false
    oauth2: Optional[bool] = None

    # Password.
    password: str

    # SMTP Password.
    #
    # Only needs to be specified if different than IMAP password.
    smtp_password: Optional[str] = None

    # SMTP server port.
    smtp_port: Optional[int] = None

    # SMTP socket security.
    smtp_security: Optional[Socket] = None

    # SMTP server hostname or IP address.
    smtp_server: Optional[str] = None

    # SMTP username.
    smtp_user: Optional[str] = None


# Timer is disabled.
EphemeralTimerDisabled = Literal["disabled"]


@dataclass(kw_only=True)
class EphemeralTimerEnabled:
    """Timer is enabled."""

    # Timer duration in seconds.
    #
    # The value cannot be 0.
    duration: int


EphemeralTimer: TypeAlias = EphemeralTimerDisabled | EphemeralTimerEnabled


def _unmarshalEphemeralTimer(data: dict) -> EphemeralTimer:
    kind = data.pop("kind")
    match kind:
        case "disabled":
            return kind
        case "enabled":
            return _from_dict(EphemeralTimerEnabled, data)
        case _:
            raise ValueError(f"Unknow EphemeralTimer kind: {kind}")


_config.type_hooks[EphemeralTimer] = _unmarshalEphemeralTimer


@dataclass(kw_only=True)
class Event:

    # Account ID.
    context_id: int

    # Event payload.
    event: EventType


@dataclass(kw_only=True)
class EventTypeInfo:
    """
    The library-user may write an informational string to the log.

    This event should *not* be reported to the end-user using a popup or something like that.
    """

    msg: str


@dataclass(kw_only=True)
class EventTypeSmtpConnected:
    """Emitted when SMTP connection is established and login was successful."""

    msg: str


@dataclass(kw_only=True)
class EventTypeImapConnected:
    """Emitted when IMAP connection is established and login was successful."""

    msg: str


@dataclass(kw_only=True)
class EventTypeSmtpMessageSent:
    """Emitted when a message was successfully sent to the SMTP server."""

    msg: str


@dataclass(kw_only=True)
class EventTypeImapMessageDeleted:
    """Emitted when an IMAP message has been marked as deleted"""

    msg: str


@dataclass(kw_only=True)
class EventTypeImapMessageMoved:
    """Emitted when an IMAP message has been moved"""

    msg: str


# Emitted before going into IDLE on the Inbox folder.
EventTypeImapInboxIdle = Literal["ImapInboxIdle"]


@dataclass(kw_only=True)
class EventTypeNewBlobFile:
    """Emitted when an new file in the $BLOBDIR was created"""

    file: str


@dataclass(kw_only=True)
class EventTypeDeletedBlobFile:
    """Emitted when an file in the $BLOBDIR was deleted"""

    file: str


@dataclass(kw_only=True)
class EventTypeWarning:
    """
    The library-user should write a warning string to the log.

    This event should *not* be reported to the end-user using a popup or something like that.
    """

    msg: str


@dataclass(kw_only=True)
class EventTypeError:
    """
    The library-user should report an error to the end-user.

    As most things are asynchronous, things may go wrong at any time and the user should not be disturbed by a dialog or so.  Instead, use a bubble or so.

    However, for ongoing processes (eg. configure()) or for functions that are expected to fail (eg. autocryptContinueKeyTransfer()) it might be better to delay showing these events until the function has really failed (returned false). It should be sufficient to report only the *last* error in a message box then.
    """

    msg: str


@dataclass(kw_only=True)
class EventTypeErrorSelfNotInGroup:
    """An action cannot be performed because the user is not in the group. Reported eg. after a call to setChatName(), setChatProfileImage(), addContactToChat(), removeContactFromChat(), and messages sending functions."""

    msg: str


@dataclass(kw_only=True)
class EventTypeMsgsChanged:
    """Messages or chats changed.  One or more messages or chats changed for various reasons in the database: - Messages sent, received or removed - Chats created, deleted or archived - A draft has been set"""

    # Set if only a single chat is affected by the changes, otherwise 0.
    chat_id: int

    # Set if only a single message is affected by the changes, otherwise 0.
    msg_id: int


@dataclass(kw_only=True)
class EventTypeReactionsChanged:
    """Reactions for the message changed."""

    # ID of the chat which the message belongs to.
    chat_id: int

    # ID of the contact whose reaction set is changed.
    contact_id: int

    # ID of the message for which reactions were changed.
    msg_id: int


@dataclass(kw_only=True)
class EventTypeIncomingReaction:
    """
    A reaction to one's own sent message received. Typically, the UI will show a notification for that.

    In addition to this event, ReactionsChanged is emitted.
    """

    # ID of the chat which the message belongs to.
    chat_id: int

    # ID of the contact whose reaction set is changed.
    contact_id: int

    # ID of the message for which reactions were changed.
    msg_id: int

    # The reaction.
    reaction: str


@dataclass(kw_only=True)
class EventTypeIncomingWebxdcNotify:
    """Incoming webxdc info or summary update, should be notified."""

    # ID of the chat.
    chat_id: int

    # ID of the contact sending.
    contact_id: int

    # Link assigned to this notification, if any.
    href: Optional[str] = None

    # ID of the added info message or webxdc instance in case of summary change.
    msg_id: int

    # Text to notify.
    text: str


@dataclass(kw_only=True)
class EventTypeIncomingMsg:
    """
    There is a fresh message. Typically, the user will show a notification when receiving this message.

    There is no extra #DC_EVENT_MSGS_CHANGED event sent together with this event.
    """

    # ID of the chat where the message is assigned.
    chat_id: int

    # ID of the message.
    msg_id: int


# Downloading a bunch of messages just finished. This is an event to allow the UI to only show one notification per message bunch, instead of cluttering the user with many notifications.
EventTypeIncomingMsgBunch = Literal["IncomingMsgBunch"]


@dataclass(kw_only=True)
class EventTypeMsgsNoticed:
    """Messages were seen or noticed. chat id is always set."""

    chat_id: int


@dataclass(kw_only=True)
class EventTypeMsgDelivered:
    """A single message is sent successfully. State changed from  DC_STATE_OUT_PENDING to DC_STATE_OUT_DELIVERED, see `Message.state`."""

    # ID of the chat which the message belongs to.
    chat_id: int

    # ID of the message that was successfully sent.
    msg_id: int


@dataclass(kw_only=True)
class EventTypeMsgFailed:
    """A single message could not be sent. State changed from DC_STATE_OUT_PENDING or DC_STATE_OUT_DELIVERED to DC_STATE_OUT_FAILED, see `Message.state`."""

    # ID of the chat which the message belongs to.
    chat_id: int

    # ID of the message that could not be sent.
    msg_id: int


@dataclass(kw_only=True)
class EventTypeMsgRead:
    """A single message is read by the receiver. State changed from DC_STATE_OUT_DELIVERED to DC_STATE_OUT_MDN_RCVD, see `Message.state`."""

    # ID of the chat which the message belongs to.
    chat_id: int

    # ID of the message that was read.
    msg_id: int


@dataclass(kw_only=True)
class EventTypeMsgDeleted:
    """
    A single message was deleted.

    This event means that the message will no longer appear in the messagelist. UI should remove the message from the messagelist in response to this event if the message is currently displayed.

    The message may have been explicitly deleted by the user or expired. Internally the message may have been removed from the database, moved to the trash chat or hidden.

    This event does not indicate the message deletion from the server.
    """

    # ID of the chat where the message was prior to deletion. Never 0.
    chat_id: int

    # ID of the deleted message. Never 0.
    msg_id: int


@dataclass(kw_only=True)
class EventTypeChatModified:
    """
    Chat changed.  The name or the image of a chat group was changed or members were added or removed. See setChatName(), setChatProfileImage(), addContactToChat() and removeContactFromChat().

    This event does not include ephemeral timer modification, which is a separate event.
    """

    chat_id: int


@dataclass(kw_only=True)
class EventTypeChatEphemeralTimerModified:
    """Chat ephemeral timer changed."""

    # Chat ID.
    chat_id: int

    # New ephemeral timer value.
    timer: int


@dataclass(kw_only=True)
class EventTypeChatDeleted:
    """Chat deleted."""

    # Chat ID.
    chat_id: int


@dataclass(kw_only=True)
class EventTypeContactsChanged:
    """Contact(s) created, renamed, blocked or deleted."""

    # If set, this is the contact_id of an added contact that should be selected.
    contact_id: Optional[int] = None


@dataclass(kw_only=True)
class EventTypeLocationChanged:
    """Location of one or more contact has changed."""

    # contact_id of the contact for which the location has changed. If the locations of several contacts have been changed, this parameter is set to `None`.
    contact_id: Optional[int] = None


@dataclass(kw_only=True)
class EventTypeConfigureProgress:
    """Inform about the configuration progress started by configure()."""

    # Progress comment or error, something to display to the user.
    comment: Optional[str] = None

    # Progress.
    #
    # 0=error, 1-999=progress in permille, 1000=success and done
    progress: int


@dataclass(kw_only=True)
class EventTypeImexProgress:
    """Inform about the import/export progress started by imex()."""

    # 0=error, 1-999=progress in permille, 1000=success and done
    progress: int


@dataclass(kw_only=True)
class EventTypeImexFileWritten:
    """
    A file has been exported. A file has been written by imex(). This event may be sent multiple times by a single call to imex().

    A typical purpose for a handler of this event may be to make the file public to some system services.

    @param data2 0
    """

    path: str


@dataclass(kw_only=True)
class EventTypeSecurejoinInviterProgress:
    """
    Progress event sent when SecureJoin protocol has finished from the view of the inviter (Alice, the person who shows the QR code).

    These events are typically sent after a joiner has scanned the QR code generated by getChatSecurejoinQrCodeSvg().
    """

    # ID of the chat in case of success.
    chat_id: int

    # The type of the joined chat. This can take the same values as `BasicChat.chatType` ([`crate.api.types.chat.BasicChat.chat_type`]).
    chat_type: ChatType

    # ID of the contact that wants to join.
    contact_id: int

    # Progress, always 1000.
    progress: int


@dataclass(kw_only=True)
class EventTypeSecurejoinJoinerProgress:
    """Progress information of a secure-join handshake from the view of the joiner (Bob, the person who scans the QR code). The events are typically sent while secureJoin(), which may take some time, is executed."""

    # ID of the inviting contact.
    contact_id: int

    # Progress as: 400=vg-/vc-request-with-auth sent, typically shown as "alice@addr verified, introducing myself." (Bob has verified alice and waits until Alice does the same for him) 1000=vg-member-added/vc-contact-confirm received
    progress: int


# The connectivity to the server changed. This means that you should refresh the connectivity view and possibly the connectivtiy HTML; see getConnectivity() and getConnectivityHtml() for details.
EventTypeConnectivityChanged = Literal["ConnectivityChanged"]
# Deprecated by `ConfigSynced`.
EventTypeSelfavatarChanged = Literal["SelfavatarChanged"]


@dataclass(kw_only=True)
class EventTypeConfigSynced:
    """A multi-device synced config value changed. Maybe the app needs to refresh smth. For uniformity this is emitted on the source device too. The value isn't here, otherwise it would be logged which might not be good for privacy."""

    # Configuration key.
    key: str


@dataclass(kw_only=True)
class EventTypeWebxdcStatusUpdate:

    # Message ID.
    msg_id: int

    # Status update ID.
    status_update_serial: int


@dataclass(kw_only=True)
class EventTypeWebxdcRealtimeData:
    """Data received over an ephemeral peer channel."""

    # Realtime data.
    data: list[int]

    # Message ID.
    msg_id: int


@dataclass(kw_only=True)
class EventTypeWebxdcRealtimeAdvertisementReceived:
    """Advertisement received over an ephemeral peer channel. This can be used by bots to initiate peer-to-peer communication from their side."""

    # Message ID of the webxdc instance.
    msg_id: int


@dataclass(kw_only=True)
class EventTypeWebxdcInstanceDeleted:
    """Inform that a message containing a webxdc instance has been deleted"""

    # ID of the deleted message.
    msg_id: int


# Tells that the Background fetch was completed (or timed out). This event acts as a marker, when you reach this event you can be sure that all events emitted during the background fetch were processed.
#
# This event is only emitted by the account manager
EventTypeAccountsBackgroundFetchDone = Literal["AccountsBackgroundFetchDone"]
# Inform that set of chats or the order of the chats in the chatlist has changed.
#
# Sometimes this is emitted together with `UIChatlistItemChanged`.
EventTypeChatlistChanged = Literal["ChatlistChanged"]


@dataclass(kw_only=True)
class EventTypeChatlistItemChanged:
    """Inform that a single chat list item changed and needs to be rerendered. If `chat_id` is set to None, then all currently visible chats need to be rerendered, and all not-visible items need to be cleared from cache if the UI has a cache."""

    # ID of the changed chat
    chat_id: Optional[int] = None


# Inform that the list of accounts has changed (an account removed or added or (not yet implemented) the account order changes)
#
# This event is only emitted by the account manager
EventTypeAccountsChanged = Literal["AccountsChanged"]
# Inform that an account property that might be shown in the account list changed, namely: - is_configured (see is_configured()) - displayname - selfavatar - private_tag
#
# This event is emitted from the account whose property changed.
EventTypeAccountsItemChanged = Literal["AccountsItemChanged"]


@dataclass(kw_only=True)
class EventTypeEventChannelOverflow:
    """Inform than some events have been skipped due to event channel overflow."""

    # Number of events skipped.
    n: int


@dataclass(kw_only=True)
class EventTypeIncomingCall:
    """Incoming call."""

    # ID of the chat which the message belongs to.
    chat_id: int

    # True if incoming call is a video call.
    has_video: bool

    # ID of the info message referring to the call.
    msg_id: int

    # User-defined info as passed to place_outgoing_call()
    place_call_info: str


@dataclass(kw_only=True)
class EventTypeIncomingCallAccepted:
    """Incoming call accepted. This is esp. interesting to stop ringing on other devices."""

    # ID of the chat which the message belongs to.
    chat_id: int

    # The call was accepted from this device (process).
    from_this_device: bool

    # ID of the info message referring to the call.
    msg_id: int


@dataclass(kw_only=True)
class EventTypeOutgoingCallAccepted:
    """Outgoing call accepted."""

    # User-defined info passed to dc_accept_incoming_call(
    accept_call_info: str

    # ID of the chat which the message belongs to.
    chat_id: int

    # ID of the info message referring to the call.
    msg_id: int


@dataclass(kw_only=True)
class EventTypeCallEnded:
    """Call ended."""

    # ID of the chat which the message belongs to.
    chat_id: int

    # ID of the info message referring to the call.
    msg_id: int


# One or more transports has changed.
#
# UI should update the list.
#
# This event is emitted when transport synchronization messages arrives, but not when the UI modifies the transport list by itself.
EventTypeTransportsModified = Literal["TransportsModified"]
EventType: TypeAlias = (
    EventTypeInfo
    | EventTypeSmtpConnected
    | EventTypeImapConnected
    | EventTypeSmtpMessageSent
    | EventTypeImapMessageDeleted
    | EventTypeImapMessageMoved
    | EventTypeImapInboxIdle
    | EventTypeNewBlobFile
    | EventTypeDeletedBlobFile
    | EventTypeWarning
    | EventTypeError
    | EventTypeErrorSelfNotInGroup
    | EventTypeMsgsChanged
    | EventTypeReactionsChanged
    | EventTypeIncomingReaction
    | EventTypeIncomingWebxdcNotify
    | EventTypeIncomingMsg
    | EventTypeIncomingMsgBunch
    | EventTypeMsgsNoticed
    | EventTypeMsgDelivered
    | EventTypeMsgFailed
    | EventTypeMsgRead
    | EventTypeMsgDeleted
    | EventTypeChatModified
    | EventTypeChatEphemeralTimerModified
    | EventTypeChatDeleted
    | EventTypeContactsChanged
    | EventTypeLocationChanged
    | EventTypeConfigureProgress
    | EventTypeImexProgress
    | EventTypeImexFileWritten
    | EventTypeSecurejoinInviterProgress
    | EventTypeSecurejoinJoinerProgress
    | EventTypeConnectivityChanged
    | EventTypeSelfavatarChanged
    | EventTypeConfigSynced
    | EventTypeWebxdcStatusUpdate
    | EventTypeWebxdcRealtimeData
    | EventTypeWebxdcRealtimeAdvertisementReceived
    | EventTypeWebxdcInstanceDeleted
    | EventTypeAccountsBackgroundFetchDone
    | EventTypeChatlistChanged
    | EventTypeChatlistItemChanged
    | EventTypeAccountsChanged
    | EventTypeAccountsItemChanged
    | EventTypeEventChannelOverflow
    | EventTypeIncomingCall
    | EventTypeIncomingCallAccepted
    | EventTypeOutgoingCallAccepted
    | EventTypeCallEnded
    | EventTypeTransportsModified
)


def _unmarshalEventType(data: dict) -> EventType:
    kind = data.pop("kind")
    match kind:
        case "Info":
            return _from_dict(EventTypeInfo, data)
        case "SmtpConnected":
            return _from_dict(EventTypeSmtpConnected, data)
        case "ImapConnected":
            return _from_dict(EventTypeImapConnected, data)
        case "SmtpMessageSent":
            return _from_dict(EventTypeSmtpMessageSent, data)
        case "ImapMessageDeleted":
            return _from_dict(EventTypeImapMessageDeleted, data)
        case "ImapMessageMoved":
            return _from_dict(EventTypeImapMessageMoved, data)
        case "ImapInboxIdle":
            return kind
        case "NewBlobFile":
            return _from_dict(EventTypeNewBlobFile, data)
        case "DeletedBlobFile":
            return _from_dict(EventTypeDeletedBlobFile, data)
        case "Warning":
            return _from_dict(EventTypeWarning, data)
        case "Error":
            return _from_dict(EventTypeError, data)
        case "ErrorSelfNotInGroup":
            return _from_dict(EventTypeErrorSelfNotInGroup, data)
        case "MsgsChanged":
            return _from_dict(EventTypeMsgsChanged, data)
        case "ReactionsChanged":
            return _from_dict(EventTypeReactionsChanged, data)
        case "IncomingReaction":
            return _from_dict(EventTypeIncomingReaction, data)
        case "IncomingWebxdcNotify":
            return _from_dict(EventTypeIncomingWebxdcNotify, data)
        case "IncomingMsg":
            return _from_dict(EventTypeIncomingMsg, data)
        case "IncomingMsgBunch":
            return kind
        case "MsgsNoticed":
            return _from_dict(EventTypeMsgsNoticed, data)
        case "MsgDelivered":
            return _from_dict(EventTypeMsgDelivered, data)
        case "MsgFailed":
            return _from_dict(EventTypeMsgFailed, data)
        case "MsgRead":
            return _from_dict(EventTypeMsgRead, data)
        case "MsgDeleted":
            return _from_dict(EventTypeMsgDeleted, data)
        case "ChatModified":
            return _from_dict(EventTypeChatModified, data)
        case "ChatEphemeralTimerModified":
            return _from_dict(EventTypeChatEphemeralTimerModified, data)
        case "ChatDeleted":
            return _from_dict(EventTypeChatDeleted, data)
        case "ContactsChanged":
            return _from_dict(EventTypeContactsChanged, data)
        case "LocationChanged":
            return _from_dict(EventTypeLocationChanged, data)
        case "ConfigureProgress":
            return _from_dict(EventTypeConfigureProgress, data)
        case "ImexProgress":
            return _from_dict(EventTypeImexProgress, data)
        case "ImexFileWritten":
            return _from_dict(EventTypeImexFileWritten, data)
        case "SecurejoinInviterProgress":
            return _from_dict(EventTypeSecurejoinInviterProgress, data)
        case "SecurejoinJoinerProgress":
            return _from_dict(EventTypeSecurejoinJoinerProgress, data)
        case "ConnectivityChanged":
            return kind
        case "SelfavatarChanged":
            return kind
        case "ConfigSynced":
            return _from_dict(EventTypeConfigSynced, data)
        case "WebxdcStatusUpdate":
            return _from_dict(EventTypeWebxdcStatusUpdate, data)
        case "WebxdcRealtimeData":
            return _from_dict(EventTypeWebxdcRealtimeData, data)
        case "WebxdcRealtimeAdvertisementReceived":
            return _from_dict(EventTypeWebxdcRealtimeAdvertisementReceived, data)
        case "WebxdcInstanceDeleted":
            return _from_dict(EventTypeWebxdcInstanceDeleted, data)
        case "AccountsBackgroundFetchDone":
            return kind
        case "ChatlistChanged":
            return kind
        case "ChatlistItemChanged":
            return _from_dict(EventTypeChatlistItemChanged, data)
        case "AccountsChanged":
            return kind
        case "AccountsItemChanged":
            return kind
        case "EventChannelOverflow":
            return _from_dict(EventTypeEventChannelOverflow, data)
        case "IncomingCall":
            return _from_dict(EventTypeIncomingCall, data)
        case "IncomingCallAccepted":
            return _from_dict(EventTypeIncomingCallAccepted, data)
        case "OutgoingCallAccepted":
            return _from_dict(EventTypeOutgoingCallAccepted, data)
        case "CallEnded":
            return _from_dict(EventTypeCallEnded, data)
        case "TransportsModified":
            return kind
        case _:
            raise ValueError(f"Unknow EventType kind: {kind}")


_config.type_hooks[EventType] = _unmarshalEventType


@dataclass(kw_only=True)
class FullChat:
    archived: bool
    can_send: bool
    chat_type: ChatType
    color: str
    contact_ids: list[int]
    ephemeral_timer: int
    fresh_message_counter: int
    id: int
    is_contact_request: bool
    is_device_chat: bool

    # True if the chat is encrypted. This means that all messages in the chat are encrypted, and all contacts in the chat are "key-contacts", i.e. identified by the PGP key fingerprint.
    #
    # False if the chat is unencrypted. This means that all messages in the chat are unencrypted, and all contacts in the chat are "address-contacts", i.e. identified by the email address. The UI should mark this chat e.g. with a mail-letter icon.
    #
    # Unencrypted groups are called "ad-hoc groups" and the user can't add/remove members, create a QR invite code, or set an avatar. These options should therefore be disabled in the UI.
    #
    # Note that it can happen that an encrypted chat contains unencrypted messages that were received in core <= v1.159.* and vice versa.
    #
    # See also `is_key_contact` on `Contact`.
    is_encrypted: bool
    is_muted: bool
    is_self_talk: bool
    is_unpromoted: bool
    mailing_list_address: Optional[str] = None
    name: str

    # Contact IDs of the past chat members.
    past_contact_ids: list[int]
    pinned: bool
    profile_image: Optional[str] = None

    # Note that this is different from [`ChatListItem.is_self_in_group`](`crate.api.types.chat_list.ChatListItemFetchResult.ChatListItem.is_self_in_group`). This property should only be accessed when [`FullChat.chat_type`] is [`Chattype.Group`].
    self_in_group: bool
    was_seen_recently: bool


@dataclass(kw_only=True)
class HttpResponse:

    # base64-encoded response body.
    blob: str

    # Encoding, e.g. "utf-8".
    encoding: Optional[str] = None

    # MIME type, e.g. "text/plain" or "text/html".
    mimetype: Optional[str] = None


@dataclass(kw_only=True)
class Location:
    accuracy: float
    chat_id: int
    contact_id: int
    is_independent: bool
    latitude: float
    location_id: int
    longitude: float
    marker: Optional[str] = None
    msg_id: int
    timestamp: int


@dataclass(kw_only=True)
class Message:
    chat_id: int
    dimensions_height: int
    dimensions_width: int
    download_state: DownloadState
    duration: int

    # An error text, if there is one.
    error: Optional[str] = None
    file: Optional[str] = None

    # The size of the file in bytes, if applicable. If message is a pre-message, then this is the size of the file to be downloaded.
    file_bytes: int
    file_mime: Optional[str] = None
    file_name: Optional[str] = None
    from_id: int
    has_deviating_timestamp: bool
    has_html: bool

    # Check if a message has a POI location bound to it. These locations are also returned by `get_locations` method. The UI may decide to display a special icon beside such messages.
    has_location: bool
    id: int

    # if is_info is set, this refers to the contact profile that should be opened when the info message is tapped.
    info_contact_id: Optional[int] = None

    # True if the message was sent by a bot.
    is_bot: bool
    is_edited: bool
    is_forwarded: bool
    is_info: bool
    original_msg_id: Optional[int] = None
    override_sender_name: Optional[str] = None
    parent_id: Optional[int] = None
    quote: Optional[MessageQuote] = None
    reactions: Optional[Reactions] = None
    received_timestamp: int
    saved_message_id: Optional[int] = None
    sender: Contact

    # True if the message was correctly encrypted&signed, false otherwise. Historically, UIs showed a small padlock on the message then.
    #
    # Today, the UIs should instead show a small email-icon on the message if `show_padlock` is `false`, and nothing if it is `true`.
    show_padlock: bool
    sort_timestamp: int
    state: int
    subject: str

    # when is_info is true this describes what type of system message it is
    system_message_type: SystemMessageType
    text: str
    timestamp: int
    vcard_contact: Optional[VcardContact] = None
    view_type: Viewtype
    webxdc_href: Optional[str] = None


@dataclass(kw_only=True)
class MessageData:
    file: Optional[str] = None
    filename: Optional[str] = None
    html: Optional[str] = None
    location: Optional[tuple[float, float]] = None
    override_sender_name: Optional[str] = None

    # Quoted message id. Takes preference over `quoted_text` (see below).
    quoted_message_id: Optional[int] = None
    quoted_text: Optional[str] = None
    text: Optional[str] = None
    viewtype: Optional[Viewtype] = None


@dataclass(kw_only=True)
class MessageInfo:
    ephemeral_timer: EphemeralTimer

    # When message is ephemeral this contains the timestamp of the message expiry
    ephemeral_timestamp: Optional[int] = None
    error: Optional[str] = None
    hop_info: str
    rfc724_mid: str
    server_urls: list[str]


@dataclass(kw_only=True)
class MessageListItemMessage:
    msg_id: int


@dataclass(kw_only=True)
class MessageListItemDayMarker:
    """Day marker, separating messages that correspond to different days according to local time."""

    # Marker timestamp, for day markers, in unix milliseconds
    timestamp: int


MessageListItem: TypeAlias = MessageListItemMessage | MessageListItemDayMarker


def _unmarshalMessageListItem(data: dict) -> MessageListItem:
    kind = data.pop("kind")
    match kind:
        case "message":
            return _from_dict(MessageListItemMessage, data)
        case "dayMarker":
            return _from_dict(MessageListItemDayMarker, data)
        case _:
            raise ValueError(f"Unknow MessageListItem kind: {kind}")


_config.type_hooks[MessageListItem] = _unmarshalMessageListItem


@dataclass(kw_only=True)
class MessageLoadResultMessage:
    chat_id: int
    dimensions_height: int
    dimensions_width: int
    download_state: DownloadState
    duration: int

    # An error text, if there is one.
    error: Optional[str] = None
    file: Optional[str] = None

    # The size of the file in bytes, if applicable. If message is a pre-message, then this is the size of the file to be downloaded.
    file_bytes: int
    file_mime: Optional[str] = None
    file_name: Optional[str] = None
    from_id: int
    has_deviating_timestamp: bool
    has_html: bool

    # Check if a message has a POI location bound to it. These locations are also returned by `get_locations` method. The UI may decide to display a special icon beside such messages.
    has_location: bool
    id: int

    # if is_info is set, this refers to the contact profile that should be opened when the info message is tapped.
    info_contact_id: Optional[int] = None

    # True if the message was sent by a bot.
    is_bot: bool
    is_edited: bool
    is_forwarded: bool
    is_info: bool
    original_msg_id: Optional[int] = None
    override_sender_name: Optional[str] = None
    parent_id: Optional[int] = None
    quote: Optional[MessageQuote] = None
    reactions: Optional[Reactions] = None
    received_timestamp: int
    saved_message_id: Optional[int] = None
    sender: Contact

    # True if the message was correctly encrypted&signed, false otherwise. Historically, UIs showed a small padlock on the message then.
    #
    # Today, the UIs should instead show a small email-icon on the message if `show_padlock` is `false`, and nothing if it is `true`.
    show_padlock: bool
    sort_timestamp: int
    state: int
    subject: str

    # when is_info is true this describes what type of system message it is
    system_message_type: SystemMessageType
    text: str
    timestamp: int
    vcard_contact: Optional[VcardContact] = None
    view_type: Viewtype
    webxdc_href: Optional[str] = None


@dataclass(kw_only=True)
class MessageLoadResultLoadingError:
    error: str


MessageLoadResult: TypeAlias = MessageLoadResultMessage | MessageLoadResultLoadingError


def _unmarshalMessageLoadResult(data: dict) -> MessageLoadResult:
    kind = data.pop("kind")
    match kind:
        case "message":
            return _from_dict(MessageLoadResultMessage, data)
        case "loadingError":
            return _from_dict(MessageLoadResultLoadingError, data)
        case _:
            raise ValueError(f"Unknow MessageLoadResult kind: {kind}")


_config.type_hooks[MessageLoadResult] = _unmarshalMessageLoadResult


@dataclass(kw_only=True)
class MessageNotificationInfo:
    account_id: int
    chat_id: int
    chat_name: str
    chat_profile_image: Optional[str] = None
    id: int
    image: Optional[str] = None
    image_mime_type: Optional[str] = None

    # also known as summary_text1
    summary_prefix: Optional[str] = None

    # also known as summary_text2
    summary_text: str


@dataclass(kw_only=True)
class MessageQuoteJustText:
    text: str


@dataclass(kw_only=True)
class MessageQuoteWithMessage:
    author_display_color: str
    author_display_name: str

    # The quoted message does not always belong to the same chat, e.g. when "Reply Privately" is used.
    chat_id: int
    image: Optional[str] = None
    is_forwarded: bool
    message_id: int
    override_sender_name: Optional[str] = None
    text: str
    view_type: Viewtype


MessageQuote: TypeAlias = MessageQuoteJustText | MessageQuoteWithMessage


def _unmarshalMessageQuote(data: dict) -> MessageQuote:
    kind = data.pop("kind")
    match kind:
        case "JustText":
            return _from_dict(MessageQuoteJustText, data)
        case "WithMessage":
            return _from_dict(MessageQuoteWithMessage, data)
        case _:
            raise ValueError(f"Unknow MessageQuote kind: {kind}")


_config.type_hooks[MessageQuote] = _unmarshalMessageQuote


@dataclass(kw_only=True)
class MessageReadReceipt:
    contact_id: int
    timestamp: int


@dataclass(kw_only=True)
class MessageSearchResult:
    author_color: str
    author_id: int

    # if sender name if overridden it will show it as ~alias
    author_name: str
    author_profile_image: Optional[str] = None
    chat_color: str
    chat_id: int
    chat_name: str
    chat_profile_image: Optional[str] = None
    chat_type: ChatType
    id: int
    is_chat_archived: bool
    is_chat_contact_request: bool
    message: str
    timestamp: int


MuteDurationNotMuted = Literal["NotMuted"]
MuteDurationForever = Literal["Forever"]


@dataclass(kw_only=True)
class MuteDurationUntil:
    duration: int


MuteDuration: TypeAlias = MuteDurationNotMuted | MuteDurationForever | MuteDurationUntil


def _unmarshalMuteDuration(data: dict) -> MuteDuration:
    kind = data.pop("kind")
    match kind:
        case "NotMuted":
            return kind
        case "Forever":
            return kind
        case "Until":
            return _from_dict(MuteDurationUntil, data)
        case _:
            raise ValueError(f"Unknow MuteDuration kind: {kind}")


_config.type_hooks[MuteDuration] = _unmarshalMuteDuration


class NotifyState(StrEnum):
    # Not subscribed to push notifications.
    NOT_CONNECTED = "NotConnected"

    # Subscribed to heartbeat push notifications.
    HEARTBEAT = "Heartbeat"

    # Subscribed to push notifications for new messages.
    CONNECTED = "Connected"


@dataclass(kw_only=True)
class ProviderInfo:
    before_login_hint: str

    # Unique ID, corresponding to provider database filename.
    id: str
    overview_page: str
    status: int


@dataclass(kw_only=True)
class QrAskVerifyContact:
    """
    Ask the user whether to verify the contact.

    If the user agrees, pass this QR code to [`crate.securejoin.join_securejoin`].
    """

    # Authentication code.
    authcode: str

    # ID of the contact.
    contact_id: int

    # Fingerprint of the contact key as scanned from the QR code.
    fingerprint: str

    # Invite number.
    invitenumber: str

    # Whether the inviter supports the new Securejoin v3 protocol
    is_v3: bool


@dataclass(kw_only=True)
class QrAskVerifyGroup:
    """Ask the user whether to join the group."""

    # Authentication code.
    authcode: str

    # ID of the contact.
    contact_id: int

    # Fingerprint of the contact key as scanned from the QR code.
    fingerprint: str

    # Group ID.
    grpid: str

    # Group name.
    grpname: str

    # Invite number.
    invitenumber: str

    # Whether the inviter supports the new Securejoin v3 protocol
    is_v3: bool


@dataclass(kw_only=True)
class QrAskJoinBroadcast:
    """Ask the user whether to join the broadcast channel."""

    # Authentication code.
    authcode: str

    # ID of the contact who owns the broadcast channel and created the QR code.
    contact_id: int

    # Fingerprint of the broadcast channel owner's key as scanned from the QR code.
    fingerprint: str

    # A string of random characters, uniquely identifying this broadcast channel across all databases/clients. Called `grpid` for historic reasons: The id of multi-user chats is always called `grpid` in the database because groups were once the only multi-user chats.
    grpid: str

    # Invite number.
    invitenumber: str

    # Whether the inviter supports the new Securejoin v3 protocol
    is_v3: bool

    # The user-visible name of this broadcast channel
    name: str


@dataclass(kw_only=True)
class QrFprOk:
    """
    Contact fingerprint is verified.

    Ask the user if they want to start chatting.
    """

    # Contact ID.
    contact_id: int


@dataclass(kw_only=True)
class QrFprMismatch:
    """Scanned fingerprint does not match the last seen fingerprint."""

    # Contact ID.
    contact_id: Optional[int] = None


@dataclass(kw_only=True)
class QrFprWithoutAddr:
    """The scanned QR code contains a fingerprint but no e-mail address."""

    # Key fingerprint.
    fingerprint: str


@dataclass(kw_only=True)
class QrAccount:
    """Ask the user if they want to create an account on the given domain."""

    # Server domain name.
    domain: str


@dataclass(kw_only=True)
class QrBackup2:
    """Provides a backup that can be retrieved using iroh-net based backup transfer protocol."""

    # Authentication token.
    auth_token: str

    # Iroh node address.
    node_addr: str


QrBackupTooNew = Literal["backupTooNew"]


@dataclass(kw_only=True)
class QrWebrtcInstance:
    """Ask the user if they want to use the given service for video chats."""

    domain: str
    instance_pattern: str


@dataclass(kw_only=True)
class QrProxy:
    """
    Ask the user if they want to use the given proxy.

    Note that HTTP(S) URLs without a path and query parameters are treated as HTTP(S) proxy URL. UI may want to still offer to open the URL in the browser if QR code contents starts with `http://` or `https://` and the QR code was not scanned from the proxy configuration screen.
    """

    # Host extracted from the URL to display in the UI.
    host: str

    # Port extracted from the URL to display in the UI.
    port: int

    # Proxy URL.
    #
    # This is the URL that is going to be added.
    url: str


@dataclass(kw_only=True)
class QrAddr:
    """
    Contact address is scanned.

    Optionally, a draft message could be provided. Ask the user if they want to start chatting.
    """

    # Contact ID.
    contact_id: int

    # Draft message.
    draft: Optional[str] = None


@dataclass(kw_only=True)
class QrUrl:
    """
    URL scanned.

    Ask the user if they want to open a browser or copy the URL to clipboard.
    """

    url: str


@dataclass(kw_only=True)
class QrText:
    """
    Text scanned.

    Ask the user if they want to copy the text to clipboard.
    """

    text: str


@dataclass(kw_only=True)
class QrWithdrawVerifyContact:
    """Ask the user if they want to withdraw their own QR code."""

    # Authentication code.
    authcode: str

    # Contact ID.
    contact_id: int

    # Fingerprint of the contact key as scanned from the QR code.
    fingerprint: str

    # Invite number.
    invitenumber: str


@dataclass(kw_only=True)
class QrWithdrawVerifyGroup:
    """Ask the user if they want to withdraw their own group invite QR code."""

    # Authentication code.
    authcode: str

    # Contact ID.
    contact_id: int

    # Fingerprint of the contact key as scanned from the QR code.
    fingerprint: str

    # Group ID.
    grpid: str

    # Group name.
    grpname: str

    # Invite number.
    invitenumber: str


@dataclass(kw_only=True)
class QrWithdrawJoinBroadcast:
    """Ask the user if they want to withdraw their own broadcast channel invite QR code."""

    # Authentication code.
    authcode: str

    # Contact ID. Always `ContactId.SELF`.
    contact_id: int

    # Fingerprint of the contact key as scanned from the QR code.
    fingerprint: str

    # ID, uniquely identifying this chat. Called grpid for historic reasons.
    grpid: str

    # Invite number.
    invitenumber: str

    # Broadcast name.
    name: str


@dataclass(kw_only=True)
class QrReviveVerifyContact:
    """Ask the user if they want to revive their own QR code."""

    # Authentication code.
    authcode: str

    # Contact ID.
    contact_id: int

    # Fingerprint of the contact key as scanned from the QR code.
    fingerprint: str

    # Invite number.
    invitenumber: str


@dataclass(kw_only=True)
class QrReviveVerifyGroup:
    """Ask the user if they want to revive their own group invite QR code."""

    # Authentication code.
    authcode: str

    # Contact ID.
    contact_id: int

    # Fingerprint of the contact key as scanned from the QR code.
    fingerprint: str

    # Group ID.
    grpid: str

    # Contact ID.
    grpname: str

    # Invite number.
    invitenumber: str


@dataclass(kw_only=True)
class QrReviveJoinBroadcast:
    """Ask the user if they want to revive their own broadcast channel invite QR code."""

    # Authentication code.
    authcode: str

    # Contact ID. Always `ContactId.SELF`.
    contact_id: int

    # Fingerprint of the contact key as scanned from the QR code.
    fingerprint: str

    # Globally unique chat ID. Called grpid for historic reasons.
    grpid: str

    # Invite number.
    invitenumber: str

    # Broadcast name.
    name: str


@dataclass(kw_only=True)
class QrLogin:
    """
    `dclogin:` scheme parameters.

    Ask the user if they want to login with the email address.
    """

    address: str


Qr: TypeAlias = (
    QrAskVerifyContact
    | QrAskVerifyGroup
    | QrAskJoinBroadcast
    | QrFprOk
    | QrFprMismatch
    | QrFprWithoutAddr
    | QrAccount
    | QrBackup2
    | QrBackupTooNew
    | QrWebrtcInstance
    | QrProxy
    | QrAddr
    | QrUrl
    | QrText
    | QrWithdrawVerifyContact
    | QrWithdrawVerifyGroup
    | QrWithdrawJoinBroadcast
    | QrReviveVerifyContact
    | QrReviveVerifyGroup
    | QrReviveJoinBroadcast
    | QrLogin
)


def _unmarshalQr(data: dict) -> Qr:
    kind = data.pop("kind")
    match kind:
        case "askVerifyContact":
            return _from_dict(QrAskVerifyContact, data)
        case "askVerifyGroup":
            return _from_dict(QrAskVerifyGroup, data)
        case "askJoinBroadcast":
            return _from_dict(QrAskJoinBroadcast, data)
        case "fprOk":
            return _from_dict(QrFprOk, data)
        case "fprMismatch":
            return _from_dict(QrFprMismatch, data)
        case "fprWithoutAddr":
            return _from_dict(QrFprWithoutAddr, data)
        case "account":
            return _from_dict(QrAccount, data)
        case "backup2":
            return _from_dict(QrBackup2, data)
        case "backupTooNew":
            return kind
        case "webrtcInstance":
            return _from_dict(QrWebrtcInstance, data)
        case "proxy":
            return _from_dict(QrProxy, data)
        case "addr":
            return _from_dict(QrAddr, data)
        case "url":
            return _from_dict(QrUrl, data)
        case "text":
            return _from_dict(QrText, data)
        case "withdrawVerifyContact":
            return _from_dict(QrWithdrawVerifyContact, data)
        case "withdrawVerifyGroup":
            return _from_dict(QrWithdrawVerifyGroup, data)
        case "withdrawJoinBroadcast":
            return _from_dict(QrWithdrawJoinBroadcast, data)
        case "reviveVerifyContact":
            return _from_dict(QrReviveVerifyContact, data)
        case "reviveVerifyGroup":
            return _from_dict(QrReviveVerifyGroup, data)
        case "reviveJoinBroadcast":
            return _from_dict(QrReviveJoinBroadcast, data)
        case "login":
            return _from_dict(QrLogin, data)
        case _:
            raise ValueError(f"Unknow Qr kind: {kind}")


_config.type_hooks[Qr] = _unmarshalQr


@dataclass(kw_only=True)
class Reaction:
    """A single reaction emoji."""

    # Emoji frequency.
    count: int

    # Emoji.
    emoji: str

    # True if we reacted with this emoji.
    is_from_self: bool


@dataclass(kw_only=True)
class Reactions:
    """Structure representing all reactions to a particular message."""

    # Unique reactions and their count, sorted in descending order.
    reactions: list[Reaction]

    # Map from a contact to it's reaction to message. There is only a single reaction per contact, but this contains a list of reactions for historical reasons.
    reactions_by_contact: dict[Any, list[str]]


class SecurejoinSource(StrEnum):
    # Because of some problem, it is unknown where the QR code came from.
    UNKNOWN = "Unknown"

    # The user opened a link somewhere outside Delta Chat
    EXTERNAL_LINK = "ExternalLink"

    # The user clicked on a link in a message inside Delta Chat
    INTERNAL_LINK = "InternalLink"

    # The user clicked "Paste from Clipboard" in the QR scan activity
    CLIPBOARD = "Clipboard"

    # The user clicked "Load QR code as image" in the QR scan activity
    IMAGE_LOADED = "ImageLoaded"

    # The user scanned a QR code
    SCAN = "Scan"


class SecurejoinUiPath(StrEnum):
    # The UI path is unknown, or the user didn't open the QR code screen at all.
    UNKNOWN = "Unknown"

    # The user directly clicked on the QR icon in the main screen
    QR_ICON = "QrIcon"

    # The user first clicked on the `+` button in the main screen, and then on "New Contact"
    NEW_CONTACT = "NewContact"


class Socket(StrEnum):
    # Unspecified socket security, select automatically.
    AUTOMATIC = "automatic"

    # TLS connection.
    SSL = "ssl"

    # STARTTLS connection.
    STARTTLS = "starttls"

    # No TLS, plaintext connection.
    PLAIN = "plain"


class SystemMessageType(StrEnum):

    UNKNOWN = "Unknown"
    GROUP_NAME_CHANGED = "GroupNameChanged"
    GROUP_DESCRIPTION_CHANGED = "GroupDescriptionChanged"
    GROUP_IMAGE_CHANGED = "GroupImageChanged"
    MEMBER_ADDED_TO_GROUP = "MemberAddedToGroup"
    MEMBER_REMOVED_FROM_GROUP = "MemberRemovedFromGroup"
    AUTOCRYPT_SETUP_MESSAGE = "AutocryptSetupMessage"
    SECUREJOIN_MESSAGE = "SecurejoinMessage"
    LOCATION_STREAMING_ENABLED = "LocationStreamingEnabled"
    LOCATION_ONLY = "LocationOnly"
    INVALID_UNENCRYPTED_MAIL = "InvalidUnencryptedMail"
    CHAT_E2EE = "ChatE2ee"
    CHAT_PROTECTION_ENABLED = "ChatProtectionEnabled"
    CHAT_PROTECTION_DISABLED = "ChatProtectionDisabled"
    WEBXDC_STATUS_UPDATE = "WebxdcStatusUpdate"
    CALL_ACCEPTED = "CallAccepted"
    CALL_ENDED = "CallEnded"

    # 1:1 chats info message telling that SecureJoin has started and the user should wait for it to complete.
    SECUREJOIN_WAIT = "SecurejoinWait"

    # 1:1 chats info message telling that SecureJoin is still running, but the user may already send messages.
    SECUREJOIN_WAIT_TIMEOUT = "SecurejoinWaitTimeout"

    # Chat ephemeral message timer is changed.
    EPHEMERAL_TIMER_CHANGED = "EphemeralTimerChanged"

    # Self-sent-message that contains only json used for multi-device-sync; if possible, we attach that to other messages as for locations.
    MULTI_DEVICE_SYNC = "MultiDeviceSync"

    # Webxdc info added with `info` set in `send_webxdc_status_update()`.
    WEBXDC_INFO_MESSAGE = "WebxdcInfoMessage"

    # This message contains a users iroh node address.
    IROH_NODE_ADDR = "IrohNodeAddr"


@dataclass(kw_only=True)
class TransportListEntry:

    # Whether this transport is set to 'unpublished'. See `set_transport_unpublished` / `setTransportUnpublished` for details.
    is_unpublished: bool

    # The login data entered by the user.
    param: EnteredLoginParam


@dataclass(kw_only=True)
class VcardContact:

    # Email address.
    addr: str

    # Contact color as hex string.
    color: str

    # The contact's name, or the email address if no name was given.
    display_name: str

    # Public PGP key in Base64.
    key: Optional[str] = None

    # Profile image in Base64.
    profile_image: Optional[str] = None

    # Last update timestamp.
    timestamp: Optional[int] = None


class Viewtype(StrEnum):

    UNKNOWN = "Unknown"

    # Text message.
    TEXT = "Text"

    # Image message. If the image is an animated GIF, the type `Viewtype.Gif` should be used.
    IMAGE = "Image"

    # Animated GIF message.
    GIF = "Gif"

    # Message containing a sticker, similar to image.
    #
    # If possible, the ui should display the image without borders in a transparent way. A click on a sticker will offer to install the sticker set in some future.
    STICKER = "Sticker"

    # Message containing an Audio file.
    AUDIO = "Audio"

    # A voice message that was directly recorded by the user. For all other audio messages, the type `Viewtype.Audio` should be used.
    VOICE = "Voice"

    # Video messages.
    VIDEO = "Video"

    # Message containing any file, eg. a PDF.
    FILE = "File"

    # Message is a call.
    CALL = "Call"

    # Message is an webxdc instance.
    WEBXDC = "Webxdc"

    # Message containing shared contacts represented as a vCard (virtual contact file) with email addresses and possibly other fields. Use `parse_vcard()` to retrieve them.
    VCARD = "Vcard"


@dataclass(kw_only=True)
class WebxdcMessageInfo:

    # if the Webxdc represents a document, then this is the name of the document
    document: Optional[str] = None

    # App icon file name. Defaults to an standard icon if nothing is set in the manifest.
    #
    # To get the file, use dc_msg_get_webxdc_blob(). (not yet in jsonrpc, use rust api or cffi for it)
    #
    # App icons should should be square, the implementations will add round corners etc. as needed.
    icon: str

    # True if full internet access should be granted to the app.
    internet_access: bool

    # Define if the local user is the one who initially shared the webxdc application in the chat.
    is_app_sender: bool

    # Define if the app runs in a broadcasting context.
    is_broadcast: bool

    # The name of the app.
    #
    # Defaults to the filename if not set in the manifest.
    name: str

    # Address to be used for `window.webxdc.selfAddr` in JS land.
    self_addr: str

    # Milliseconds to wait before calling `sendUpdate()` again since the last call. Should be exposed to `window.sendUpdateInterval` in JS land.
    send_update_interval: int

    # Maximum number of bytes accepted for a serialized update object. Should be exposed to `window.sendUpdateMaxSize` in JS land.
    send_update_max_size: int

    # URL where the source code of the Webxdc and other information can be found; defaults to an empty string. Implementations may offer an menu or a button to open this URL.
    source_code_url: Optional[str] = None

    # short string describing the state of the app, sth. as "2 votes", "Highscore: 123", can be changed by the apps
    summary: Optional[str] = None
