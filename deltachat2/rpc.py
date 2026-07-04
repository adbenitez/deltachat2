"""JSON-RPC API definition."""

from typing import Any, Optional

from ._utils import snakeclass2cameldict as _wrap
from .transport import RpcTransport
from .types import (
    Account,
    AccountConfigured,
    AccountUnconfigured,
    BasicChat,
    CallInfo,
    CallState,
    CallStateActive,
    CallStateAlerting,
    CallStateCanceled,
    CallStateCompleted,
    CallStateDeclined,
    CallStateMissed,
    ChatListItemFetchResult,
    ChatListItemFetchResultArchiveLink,
    ChatListItemFetchResultChatListItem,
    ChatListItemFetchResultError,
    ChatType,
    ChatVisibility,
    Contact,
    DownloadState,
    EnteredCertificateChecks,
    EnteredLoginParam,
    EphemeralTimer,
    EphemeralTimerDisabled,
    EphemeralTimerEnabled,
    Event,
    EventType,
    EventTypeAccountsBackgroundFetchDone,
    EventTypeAccountsChanged,
    EventTypeAccountsItemChanged,
    EventTypeCallEnded,
    EventTypeChatDeleted,
    EventTypeChatEphemeralTimerModified,
    EventTypeChatlistChanged,
    EventTypeChatlistItemChanged,
    EventTypeChatModified,
    EventTypeConfigSynced,
    EventTypeConfigureProgress,
    EventTypeConnectivityChanged,
    EventTypeContactsChanged,
    EventTypeDeletedBlobFile,
    EventTypeError,
    EventTypeErrorSelfNotInGroup,
    EventTypeEventChannelOverflow,
    EventTypeImapConnected,
    EventTypeImapInboxIdle,
    EventTypeImapMessageDeleted,
    EventTypeImapMessageMoved,
    EventTypeImexFileWritten,
    EventTypeImexProgress,
    EventTypeIncomingCall,
    EventTypeIncomingCallAccepted,
    EventTypeIncomingMsg,
    EventTypeIncomingMsgBunch,
    EventTypeIncomingReaction,
    EventTypeIncomingWebxdcNotify,
    EventTypeInfo,
    EventTypeLocationChanged,
    EventTypeMsgDeleted,
    EventTypeMsgDelivered,
    EventTypeMsgFailed,
    EventTypeMsgRead,
    EventTypeMsgsChanged,
    EventTypeMsgsNoticed,
    EventTypeNewBlobFile,
    EventTypeOutgoingCallAccepted,
    EventTypeReactionsChanged,
    EventTypeSecurejoinInviterProgress,
    EventTypeSecurejoinJoinerProgress,
    EventTypeSelfavatarChanged,
    EventTypeSmtpConnected,
    EventTypeSmtpMessageSent,
    EventTypeTransportsModified,
    EventTypeWarning,
    EventTypeWebxdcInstanceDeleted,
    EventTypeWebxdcRealtimeAdvertisementReceived,
    EventTypeWebxdcRealtimeData,
    EventTypeWebxdcStatusUpdate,
    FullChat,
    HttpResponse,
    Location,
    Message,
    MessageData,
    MessageInfo,
    MessageListItem,
    MessageListItemDayMarker,
    MessageListItemMessage,
    MessageLoadResult,
    MessageLoadResultLoadingError,
    MessageLoadResultMessage,
    MessageNotificationInfo,
    MessageQuote,
    MessageQuoteJustText,
    MessageQuoteWithMessage,
    MessageReadReceipt,
    MessageSearchResult,
    MuteDuration,
    MuteDurationForever,
    MuteDurationNotMuted,
    MuteDurationUntil,
    NotifyState,
    ProviderInfo,
    Qr,
    QrAccount,
    QrAddr,
    QrAskJoinBroadcast,
    QrAskVerifyContact,
    QrAskVerifyGroup,
    QrBackup2,
    QrBackupTooNew,
    QrFprMismatch,
    QrFprOk,
    QrFprWithoutAddr,
    QrLogin,
    QrProxy,
    QrReviveJoinBroadcast,
    QrReviveVerifyContact,
    QrReviveVerifyGroup,
    QrText,
    QrUrl,
    QrWebrtcInstance,
    QrWithdrawJoinBroadcast,
    QrWithdrawVerifyContact,
    QrWithdrawVerifyGroup,
    Reaction,
    Reactions,
    SecurejoinSource,
    SecurejoinUiPath,
    Socket,
    SystemMessageType,
    TransportListEntry,
    VcardContact,
    Viewtype,
    WebxdcMessageInfo,
    _from_dict,
    _unmarshalAccount,
    _unmarshalCallState,
    _unmarshalChatListItemFetchResult,
    _unmarshalEphemeralTimer,
    _unmarshalEventType,
    _unmarshalMessageListItem,
    _unmarshalMessageLoadResult,
    _unmarshalMessageQuote,
    _unmarshalMuteDuration,
    _unmarshalQr,
)


class Rpc:
    """Access to the chatmail JSON-RPC API."""

    def __init__(self, transport: RpcTransport) -> None:
        self.transport = transport

    def sleep(self, delay: float) -> None:
        """Test function."""
        self.transport.call("sleep", delay)

    def check_email_validity(self, email: str) -> bool:
        """Checks if an email address is valid."""
        return self.transport.call("check_email_validity", email)

    def get_system_info(self) -> dict[Any, str]:
        """Returns general system info."""
        return self.transport.call("get_system_info")

    def get_next_event(self) -> Event:
        """
        Get the next event, and remove it from the event queue.

        If no events have happened since the last `get_next_event`
        (i.e. if the event queue is empty), the response will be returned
        only when a new event fires.

        Note that if you are using the `BaseDeltaChat` JavaScript class
        or the `Rpc` Python class, this function will be invoked
        by those classes internally and should not be used manually.
        """
        _result = self.transport.call("get_next_event")
        return _from_dict(Event, _result)

    def get_next_event_batch(self) -> list[Event]:
        """Waits for at least one event and return a batch of events."""
        _result = self.transport.call("get_next_event_batch")
        return [_from_dict(Event, _item) for _item in _result]

    def add_account(self) -> int:
        return self.transport.call("add_account")

    def migrate_account(self, path_to_db: str) -> int:
        """
        Imports/migrated an existing account from a database path into this account manager.
        Returns the ID of new account.
        """
        return self.transport.call("migrate_account", path_to_db)

    def remove_account(self, account_id: int) -> None:
        self.transport.call("remove_account", account_id)

    def get_all_account_ids(self) -> list[int]:
        return self.transport.call("get_all_account_ids")

    def select_account(self, id: int) -> None:
        """Select account in account manager, this saves the last used account to accounts.toml"""
        self.transport.call("select_account", id)

    def get_selected_account_id(self) -> Optional[int]:
        """Get the selected account from the account manager (on startup it is read from accounts.toml)"""
        return self.transport.call("get_selected_account_id")

    def set_accounts_order(self, order: list[int]) -> None:
        """
        Set the order of accounts.
        The provided list should contain all account IDs in the desired order.
        If an account ID is missing from the list, it will be appended at the end.
        If the list contains non-existent account IDs, they will be ignored.
        """
        self.transport.call("set_accounts_order", order)

    def get_all_accounts(self) -> list[Account]:
        """Get a list of all configured accounts."""
        _result = self.transport.call("get_all_accounts")
        return [_unmarshalAccount(_item) for _item in _result]

    def start_io_for_all_accounts(self) -> None:
        """Starts background tasks for all accounts."""
        self.transport.call("start_io_for_all_accounts")

    def stop_io_for_all_accounts(self) -> None:
        """Stops background tasks for all accounts."""
        self.transport.call("stop_io_for_all_accounts")

    def background_fetch(self, timeout_in_seconds: float) -> None:
        """
        Performs a background fetch for all accounts in parallel with a timeout.

        The `AccountsBackgroundFetchDone` event is emitted at the end even in case of timeout.
        Process all events until you get this one and you can safely return to the background
        without forgetting to create notifications caused by timing race conditions.
        """
        self.transport.call("background_fetch", timeout_in_seconds)

    def stop_background_fetch(self) -> None:
        self.transport.call("stop_background_fetch")

    def start_io(self, account_id: int) -> None:
        """Starts background tasks for a single account."""
        self.transport.call("start_io", account_id)

    def stop_io(self, account_id: int) -> None:
        """Stops background tasks for a single account."""
        self.transport.call("stop_io", account_id)

    def get_account_info(self, account_id: int) -> Account:
        """Get top-level info for an account."""
        _result = self.transport.call("get_account_info", account_id)
        return _unmarshalAccount(_result)

    def get_push_state(self, account_id: int) -> NotifyState:
        """Get the current push notification state."""
        return self.transport.call("get_push_state", account_id)

    def get_account_file_size(self, account_id: int) -> int:
        """Get the combined filesize of an account in bytes"""
        return self.transport.call("get_account_file_size", account_id)

    def get_provider_info(self, account_id: int, email: str) -> Optional[ProviderInfo]:
        """
        Returns provider for the given domain.

        This function looks up domain in offline database.

        For compatibility, email address can be passed to this function
        instead of the domain.
        """
        _result = self.transport.call("get_provider_info", account_id, email)
        return _result and _from_dict(ProviderInfo, _result)

    def is_configured(self, account_id: int) -> bool:
        """Checks if the context is already configured."""
        return self.transport.call("is_configured", account_id)

    def get_info(self, account_id: int) -> dict[Any, str]:
        """Get system info for an account."""
        return self.transport.call("get_info", account_id)

    def get_storage_usage_report_string(self, account_id: int) -> str:
        """Get storage usage report as formatted string"""
        return self.transport.call("get_storage_usage_report_string", account_id)

    def get_blob_dir(self, account_id: int) -> Optional[str]:
        """Get the blob dir."""
        return self.transport.call("get_blob_dir", account_id)

    def get_migration_error(self, account_id: int) -> Optional[str]:
        """
        If there was an error while the account was opened
        and migrated to the current version,
        then this function returns it.

        This function is useful because the key-contacts migration could fail due to bugs
        and then the account will not work properly.

        After opening an account, the UI should call this function
        and show the error string if one is returned.
        """
        return self.transport.call("get_migration_error", account_id)

    def copy_to_blob_dir(self, account_id: int, path: str) -> str:
        """Copy file to blob dir."""
        return self.transport.call("copy_to_blob_dir", account_id, path)

    def set_config(self, account_id: int, key: str, value: Optional[str]) -> None:
        """Sets the given configuration key."""
        self.transport.call("set_config", account_id, key, value)

    def batch_set_config(self, account_id: int, config: dict[Any, Optional[str]]) -> None:
        """Updates a batch of configuration values."""
        self.transport.call("batch_set_config", account_id, config)

    def set_config_from_qr(self, account_id: int, qr_content: str) -> None:
        """
        Set configuration values from a QR code (technically from the URI stored in it).
        Before this function is called, `check_qr()` should be used to get the QR code type.

        "DCACCOUNT:" and "DCLOGIN:" QR codes configure the account, but I/O mustn't be started for
        such QR codes, consider using [`Rpc.add_transport_from_qr`] which also restarts I/O.
        """
        self.transport.call("set_config_from_qr", account_id, qr_content)

    def check_qr(self, account_id: int, qr_content: str) -> Qr:
        _result = self.transport.call("check_qr", account_id, qr_content)
        return _unmarshalQr(_result)

    def get_config(self, account_id: int, key: str) -> Optional[str]:
        """Returns configuration value for the given key."""
        return self.transport.call("get_config", account_id, key)

    def batch_get_config(self, account_id: int, keys: list[str]) -> dict[Any, Optional[str]]:
        return self.transport.call("batch_get_config", account_id, keys)

    def get_all_ui_config_keys(self, account_id: int) -> list[str]:
        """Returns all `ui.*` config keys that were set by the UI."""
        return self.transport.call("get_all_ui_config_keys", account_id)

    def set_stock_strings(self, strings: dict[Any, str]) -> None:
        self.transport.call("set_stock_strings", strings)

    def configure(self, account_id: int) -> None:
        """
        Configures this account with the currently set parameters.
        Setup the credential config before calling this.

        Deprecated as of 2025-02; use `add_transport_from_qr()`
        or `add_or_update_transport()` instead.
        """
        self.transport.call("configure", account_id)

    def add_or_update_transport(self, account_id: int, param: EnteredLoginParam) -> None:
        """
        Configures a new email account using the provided parameters
        and adds it as a transport.

        If the email address is the same as an existing transport,
        then this existing account will be reconfigured instead of a new one being added.

        This function stops and starts IO as needed.

        Usually it will be enough to only set `addr` and `password`,
        and all the other settings will be autoconfigured.

        During configuration, ConfigureProgress events are emitted;
        they indicate a successful configuration as well as errors
        and may be used to create a progress bar.
        This function will return after configuration is finished.

        If configuration is successful,
        the working server parameters will be saved
        and used for connecting to the server.
        The parameters entered by the user will be saved separately
        so that they can be prefilled when the user opens the server-configuration screen again.

        See also:
        - [Rpc.is_configured()] to check whether there is
        at least one working transport.
        - [Rpc.add_transport_from_qr()] to add a transport
        from a server encoded in a QR code.
        - [Rpc.list_transports()] to get a list of all configured transports.
        - [Rpc.delete_transport()] to remove a transport.
        - [Rpc.set_transport_unpublished()] to set whether contacts see this transport.
        """
        self.transport.call("add_or_update_transport", account_id, _wrap(param))

    def add_transport(self, account_id: int, param: EnteredLoginParam) -> None:
        """Deprecated 2025-04. Alias for [Rpc.add_or_update_transport()]."""
        self.transport.call("add_transport", account_id, _wrap(param))

    def add_transport_from_qr(self, account_id: int, qr: str) -> None:
        """
        Adds a new email account as a transport
        using the server encoded in the QR code.
        See [Rpc.add_or_update_transport].
        """
        self.transport.call("add_transport_from_qr", account_id, qr)

    def list_transports(self, account_id: int) -> list[EnteredLoginParam]:
        """
        Returns the list of all email accounts that are used as a transport in the current profile.
        Use [Rpc.add_or_update_transport()] to add or change a transport
        and [Rpc.delete_transport()] to delete a transport.
        Use [Rpc.list_transports_ex()] to additionally query
        whether the transports are marked as 'unpublished'.
        """
        _result = self.transport.call("list_transports", account_id)
        return [_from_dict(EnteredLoginParam, _item) for _item in _result]

    def list_transports_ex(self, account_id: int) -> list[TransportListEntry]:
        """
        Returns the list of all email accounts that are used as a transport in the current profile.
        Use [Rpc.add_or_update_transport()] to add or change a transport
        and [Rpc.delete_transport()] to delete a transport.
        """
        _result = self.transport.call("list_transports_ex", account_id)
        return [_from_dict(TransportListEntry, _item) for _item in _result]

    def delete_transport(self, account_id: int, addr: str) -> None:
        """
        Removes the transport with the specified email address
        (i.e. [EnteredLoginParam.addr]).
        """
        self.transport.call("delete_transport", account_id, addr)

    def set_transport_unpublished(self, account_id: int, addr: str, unpublished: bool) -> None:
        """
        Change whether the transport is unpublished.

        Unpublished transports are not advertised to contacts,
        and self-sent messages are not sent there,
        so that we don't cause extra messages to the corresponding inbox,
        but can still receive messages from contacts who don't know our new transport addresses yet.

        The default is false, but when the user updates from a version that didn't have this flag,
        existing secondary transports are set to unpublished,
        so that an existing transport address doesn't suddenly get spammed with a lot of messages.
        """
        self.transport.call("set_transport_unpublished", account_id, addr, unpublished)

    def stop_ongoing_process(self, account_id: int) -> None:
        """Signal an ongoing process to stop."""
        self.transport.call("stop_ongoing_process", account_id)

    def export_self_keys(self, account_id: int, path: str, passphrase: Optional[str]) -> None:
        self.transport.call("export_self_keys", account_id, path, passphrase)

    def import_self_keys(self, account_id: int, path: str, passphrase: Optional[str]) -> None:
        self.transport.call("import_self_keys", account_id, path, passphrase)

    def get_fresh_msgs(self, account_id: int) -> list[int]:
        """
        Returns the message IDs of all _fresh_ messages of any chat.
        Typically used for implementing notification summaries
        or badge counters e.g. on the app icon.
        The list is already sorted and starts with the most recent fresh message.

        Messages belonging to muted chats or to the contact requests are not returned;
        these messages should not be notified
        and also badge counters should not include these messages.

        To get the number of fresh messages for a single chat, muted or not,
        use `get_fresh_msg_cnt()`.
        """
        return self.transport.call("get_fresh_msgs", account_id)

    def get_fresh_msg_cnt(self, account_id: int, chat_id: int) -> int:
        """
        Get the number of _fresh_ messages in a chat.
        Typically used to implement a badge with a number in the chatlist.

        If the specified chat is muted,
        the UI should show the badge counter "less obtrusive",
        e.g. using "gray" instead of "red" color.
        """
        return self.transport.call("get_fresh_msg_cnt", account_id, chat_id)

    def get_next_msgs(self, account_id: int) -> list[int]:
        """
        (deprecated) Gets messages to be processed by the bot and returns their IDs.

        Only messages with database ID higher than `last_msg_id` config value
        are returned. After processing the messages, the bot should
        update `last_msg_id` by calling [`markseen_msgs`]
        or manually updating the value to avoid getting already
        processed messages.

        Deprecated 2026-04: This returns the message's id as soon as the first part arrives,
        even if it is not fully downloaded yet.
        The bot needs to wait for the message to be fully downloaded.
        Since this is usually not the desired behavior,
        bots should instead use the #DC_EVENT_INCOMING_MSG / [`EventTypeIncomingMsg`]
        event for getting notified about new messages.

        [`markseen_msgs`]: Rpc.markseen_msgs
        """
        return self.transport.call("get_next_msgs", account_id)

    def wait_next_msgs(self, account_id: int) -> list[int]:
        """
        (deprecated) Waits for messages to be processed by the bot and returns their IDs.

        This function is similar to [`get_next_msgs`],
        but waits for internal new message notification before returning.
        New message notification is sent when new message is added to the database,
        on initialization, when I/O is started and when I/O is stopped.
        This allows bots to use `wait_next_msgs` in a loop to process
        old messages after initialization and during the bot runtime.
        To shutdown the bot, stopping I/O can be used to interrupt
        pending or next `wait_next_msgs` call.

        Deprecated 2026-04: This returns the message's id as soon as the first part arrives,
        even if it is not fully downloaded yet.
        The bot needs to wait for the message to be fully downloaded.
        Since this is usually not the desired behavior,
        bots should instead use the #DC_EVENT_INCOMING_MSG / [`EventTypeIncomingMsg`]
        event for getting notified about new messages.

        [`get_next_msgs`]: Rpc.get_next_msgs
        """
        return self.transport.call("wait_next_msgs", account_id)

    def estimate_auto_deletion_count(self, account_id: int, from_server: bool, seconds: int) -> int:
        """
        Estimates the number of messages that will be deleted
        by the `set_config()`-option `delete_device_after`.

        This is typically used to show the estimated impact to the user
        before actually enabling deletion of old messages.

        Messages in the "Saved Messages" chat are not counted as they will not be deleted automatically.

        Parameters:
        - `from_server`: Deprecated, pass `false` here
        - `seconds`: Count messages older than the given number of seconds.

        Returns the number of messages that are older than the given number of seconds.
        """
        return self.transport.call("estimate_auto_deletion_count", account_id, from_server, seconds)

    def get_chatlist_entries(
        self,
        account_id: int,
        list_flags: Optional[int],
        query_string: Optional[str],
        query_contact_id: Optional[int],
    ) -> list[int]:
        return self.transport.call(
            "get_chatlist_entries", account_id, list_flags, query_string, query_contact_id
        )

    def get_similar_chat_ids(self, account_id: int, chat_id: int) -> list[int]:
        """
        Returns chats similar to the given one.

        Experimental API, subject to change without notice.
        """
        return self.transport.call("get_similar_chat_ids", account_id, chat_id)

    def get_chatlist_items_by_entries(
        self, account_id: int, entries: list[int]
    ) -> dict[Any, ChatListItemFetchResult]:
        _result = self.transport.call("get_chatlist_items_by_entries", account_id, entries)
        return {_key: _unmarshalChatListItemFetchResult(_val) for _key, _val in _result.items()}

    def get_full_chat_by_id(self, account_id: int, chat_id: int) -> FullChat:
        _result = self.transport.call("get_full_chat_by_id", account_id, chat_id)
        return _from_dict(FullChat, _result)

    def get_basic_chat_info(self, account_id: int, chat_id: int) -> BasicChat:
        """
        get basic info about a chat,
        use chatlist_get_full_chat_by_id() instead if you need more information
        """
        _result = self.transport.call("get_basic_chat_info", account_id, chat_id)
        return _from_dict(BasicChat, _result)

    def accept_chat(self, account_id: int, chat_id: int) -> None:
        self.transport.call("accept_chat", account_id, chat_id)

    def block_chat(self, account_id: int, chat_id: int) -> None:
        self.transport.call("block_chat", account_id, chat_id)

    def delete_chat(self, account_id: int, chat_id: int) -> None:
        """
        Delete a chat.

        Messages are deleted from the device and the chat database entry is deleted.
        After that, a `EventTypeMsgsChanged` event is emitted.
        Messages are deleted from the server in background.

        Things that are _not done_ implicitly:

        - The chat or the contact is **not blocked**, so new messages from the user/the group may appear as a contact request
        and the user may create the chat again.
        - **Groups are not left** - this would
        be unexpected as (1) deleting a normal chat also does not prevent new mails
        from arriving, (2) leaving a group requires sending a message to
        all group members - especially for groups not used for a longer time, this is
        really unexpected when deletion results in contacting all members again,
        (3) only leaving groups is also a valid usecase.

        To leave a chat explicitly, use leave_group()
        """
        self.transport.call("delete_chat", account_id, chat_id)

    def get_chat_encryption_info(self, account_id: int, chat_id: int) -> str:
        """
        Get encryption info for a chat.
        Get a multi-line encryption info, containing encryption preferences of all members.
        Can be used to find out why messages sent to group are not encrypted.

        returns Multi-line text
        """
        return self.transport.call("get_chat_encryption_info", account_id, chat_id)

    def get_chat_securejoin_qr_code(self, account_id: int, chat_id: Optional[int]) -> str:
        """
        Get QR code text that will offer a [SecureJoin](https://securejoin.delta.chat/) invitation.

        If `chat_id` is a group chat ID, SecureJoin QR code for the group is returned.
        If `chat_id` is unset, setup contact QR code is returned.
        """
        return self.transport.call("get_chat_securejoin_qr_code", account_id, chat_id)

    def get_chat_securejoin_qr_code_svg(
        self, account_id: int, chat_id: Optional[int]
    ) -> tuple[str, str]:
        """
        Get QR code (text and SVG) that will offer a Setup-Contact or Verified-Group invitation.
        The QR code is compatible to the OPENPGP4FPR format
        so that a basic fingerprint comparison also works e.g. with OpenKeychain.

        The scanning device will pass the scanned content to `checkQr()` then;
        if `checkQr()` returns `askVerifyContact` or `askVerifyGroup`
        an out-of-band-verification can be joined using `secure_join()`

        @deprecated as of 2026-03; use create_qr_svg(get_chat_securejoin_qr_code()) instead.

        chat_id: If set to a group-chat-id,
        the Verified-Group-Invite protocol is offered in the QR code;
        works for protected groups as well as for normal groups.
        If not set, the Setup-Contact protocol is offered in the QR code.
        See https://securejoin.delta.chat/ for details about both protocols.

        return format: `[code, svg]`
        """
        return self.transport.call("get_chat_securejoin_qr_code_svg", account_id, chat_id)

    def secure_join(self, account_id: int, qr: str) -> int:
        """
        Continue a Setup-Contact or Verified-Group-Invite protocol
        started on another device with `get_chat_securejoin_qr_code_svg()`.
        This function is typically called when `check_qr()` returns
        type=AskVerifyContact or type=AskVerifyGroup.

        The function returns immediately and the handshake runs in background,
        sending and receiving several messages.
        During the handshake, info messages are added to the chat,
        showing progress, success or errors.

        Subsequent calls of `secure_join()` will abort previous, unfinished handshakes.

        See https://securejoin.delta.chat/ for details about both protocols.

        **qr**: The text of the scanned QR code. Typically, the same string as given
        to `check_qr()`.

        **returns**: The chat ID of the joined chat, the UI may redirect to the this chat.
        A returned chat ID does not guarantee that the chat is protected or the belonging contact is verified.

        """
        return self.transport.call("secure_join", account_id, qr)

    def secure_join_with_ux_info(
        self,
        account_id: int,
        qr: str,
        source: Optional[SecurejoinSource],
        uipath: Optional[SecurejoinUiPath],
    ) -> int:
        """
        Like `secure_join()`, but allows to pass a source and a UI-path.
        You only need this if your UI has an option to send statistics
        to Delta Chat's developers.

        **source**: The source where the QR code came from.
        E.g. a link that was clicked inside or outside Delta Chat,
        the "Paste from Clipboard" action,
        the "Load QR code as image" action,
        or a QR code scan.

        **uipath**: Which UI path did the user use to arrive at the QR code screen.
        If the SecurejoinSource was ExternalLink or InternalLink,
        pass `None` here, because the QR code screen wasn't even opened.
        ```
        """
        return self.transport.call("secure_join_with_ux_info", account_id, qr, source, uipath)

    def leave_group(self, account_id: int, chat_id: int) -> None:
        self.transport.call("leave_group", account_id, chat_id)

    def remove_contact_from_chat(self, account_id: int, chat_id: int, contact_id: int) -> None:
        """
        Remove a member from a group.

        If the group is already _promoted_ (any message was sent to the group),
        all group members are informed by a special status message that is sent automatically by this function.

        Sends out #DC_EVENT_CHAT_MODIFIED and #DC_EVENT_MSGS_CHANGED if a status message was sent.
        """
        self.transport.call("remove_contact_from_chat", account_id, chat_id, contact_id)

    def add_contact_to_chat(self, account_id: int, chat_id: int, contact_id: int) -> None:
        """
        Add a member to a group.

        If the group is already _promoted_ (any message was sent to the group),
        all group members are informed by a special status message that is sent automatically by this function.

        If the group has group protection enabled, only verified contacts can be added to the group.

        Sends out #DC_EVENT_CHAT_MODIFIED and #DC_EVENT_MSGS_CHANGED if a status message was sent.
        """
        self.transport.call("add_contact_to_chat", account_id, chat_id, contact_id)

    def get_chat_contacts(self, account_id: int, chat_id: int) -> list[int]:
        """
        Get the contact IDs belonging to a chat.

        - for normal chats, the function always returns exactly one contact,
        DC_CONTACT_ID_SELF is returned only for SELF-chats.

        - for group chats all members are returned, DC_CONTACT_ID_SELF is returned
        explicitly as it may happen that oneself gets removed from a still existing
        group

        - for broadcast channels, all recipients are returned, DC_CONTACT_ID_SELF is not included

        - for mailing lists, the behavior is not documented currently, we will decide on that later.
        for now, the UI should not show the list for mailing lists.
        (we do not know all members and there is not always a global mailing list address,
        so we could return only SELF or the known members; this is not decided yet)
        """
        return self.transport.call("get_chat_contacts", account_id, chat_id)

    def get_past_chat_contacts(self, account_id: int, chat_id: int) -> list[int]:
        """Returns contact IDs of the past chat members."""
        return self.transport.call("get_past_chat_contacts", account_id, chat_id)

    def create_group_chat(self, account_id: int, name: str, protect: bool) -> int:
        """
        Create a new encrypted group chat (with key-contacts).

        After creation,
        the group has one member with the ID DC_CONTACT_ID_SELF
        and is in _unpromoted_ state.
        This means, you can add or remove members, change the name,
        the group image and so on without messages being sent to all group members.

        This changes as soon as the first message is sent to the group members
        and the group becomes _promoted_.
        After that, all changes are synced with all group members
        by sending status message.

        To check, if a chat is still unpromoted, you can look at the `is_unpromoted` property of `BasicChat` or `FullChat`.
        This may be useful if you want to show some help for just created groups.

        `protect` argument is deprecated as of 2025-10-22 and is left for compatibility.
        Pass `false` here.
        """
        return self.transport.call("create_group_chat", account_id, name, protect)

    def create_group_chat_unencrypted(self, account_id: int, name: str) -> int:
        """
        Create a new unencrypted group chat.

        Same as [`Rpc.create_group_chat`], but the chat is unencrypted and can only have
        address-contacts.
        """
        return self.transport.call("create_group_chat_unencrypted", account_id, name)

    def create_broadcast_list(self, account_id: int) -> int:
        """Deprecated 2025-07 in favor of create_broadcast()."""
        return self.transport.call("create_broadcast_list", account_id)

    def create_broadcast(self, account_id: int, chat_name: str) -> int:
        """
        Create a new, outgoing **broadcast channel**
        (called "Channel" in the UI).

        Broadcast channels are similar to groups on the sending device,
        however, recipients get the messages in a read-only chat
        and will not see who the other members are.

        Called `broadcast` here rather than `channel`,
        because the word "channel" already appears a lot in the code,
        which would make it hard to grep for it.

        Returns the created chat's id.
        """
        return self.transport.call("create_broadcast", account_id, chat_name)

    def set_chat_name(self, account_id: int, chat_id: int, new_name: str) -> None:
        """
        Set group name.

        If the group is already _promoted_ (any message was sent to the group),
        or if this is a brodacast channel,
        all members are informed by a special status message that is sent automatically by this function.

        Sends out #DC_EVENT_CHAT_MODIFIED and #DC_EVENT_MSGS_CHANGED if a status message was sent.
        """
        self.transport.call("set_chat_name", account_id, chat_id, new_name)

    def set_chat_description(self, account_id: int, chat_id: int, description: str) -> None:
        """
        Set group or broadcast channel description.

        If the group is already _promoted_ (any message was sent to the group),
        or if this is a brodacast channel,
        all members are informed by a special status message that is sent automatically by this function.

        Sends out #DC_EVENT_CHAT_MODIFIED and #DC_EVENT_MSGS_CHANGED if a status message was sent.

        See also [`Rpc.get_chat_description`] / `getChatDescription()`.
        """
        self.transport.call("set_chat_description", account_id, chat_id, description)

    def get_chat_description(self, account_id: int, chat_id: int) -> str:
        """
        Load the chat description from the database.

        UIs show this in the profile page of the chat,
        it is settable by [`Rpc.set_chat_description`] / `setChatDescription()`.
        """
        return self.transport.call("get_chat_description", account_id, chat_id)

    def set_chat_profile_image(
        self, account_id: int, chat_id: int, image_path: Optional[str]
    ) -> None:
        """
        Set group profile image.

        If the group is already _promoted_ (any message was sent to the group),
        or if this is a brodacast channel,
        all members are informed by a special status message that is sent automatically by this function.

        Sends out #DC_EVENT_CHAT_MODIFIED and #DC_EVENT_MSGS_CHANGED if a status message was sent.

        To find out the profile image of a chat, use dc_chat_get_profile_image()

        @param image_path Full path of the image to use as the group image. The image will immediately be copied to the
        `blobdir`; the original image will not be needed anymore.
        If you pass null here, the group image is deleted (for promoted groups, all members are informed about
        this change anyway).
        """
        self.transport.call("set_chat_profile_image", account_id, chat_id, image_path)

    def set_chat_visibility(
        self, account_id: int, chat_id: int, visibility: ChatVisibility
    ) -> None:
        self.transport.call("set_chat_visibility", account_id, chat_id, visibility)

    def set_chat_ephemeral_timer(self, account_id: int, chat_id: int, timer: int) -> None:
        self.transport.call("set_chat_ephemeral_timer", account_id, chat_id, timer)

    def get_chat_ephemeral_timer(self, account_id: int, chat_id: int) -> int:
        return self.transport.call("get_chat_ephemeral_timer", account_id, chat_id)

    def add_device_message(
        self, account_id: int, label: str, msg: Optional[MessageData]
    ) -> Optional[int]:
        """
        Add a message to the device-chat.
        Device-messages usually contain update information
        and some hints that are added during the program runs, multi-device etc.
        The device-message may be defined by a label;
        if a message with the same label was added or skipped before,
        the message is not added again, even if the message was deleted in between.
        If needed, the device-chat is created before.

        Sends the `EventTypeMsgsChanged` event on success.

        Setting msg to None will prevent the device message with this label from being added in the future.
        """
        return self.transport.call("add_device_message", account_id, label, _wrap(msg))

    def marknoticed_all_chats(self, account_id: int) -> None:
        """
        Mark all messages in all chats as _noticed_.
        Skips messages from blocked contacts, but does not skip messages in muted chats.

        _Noticed_ messages are no longer _fresh_ and do not count as being unseen
        but are still waiting for being marked as "seen" using markseen_msgs()
        (read receipts aren't sent for noticed messages).

        Calling this function usually results in the event #DC_EVENT_MSGS_NOTICED.
        See also markseen_msgs().
        """
        self.transport.call("marknoticed_all_chats", account_id)

    def marknoticed_chat(self, account_id: int, chat_id: int) -> None:
        """
        Mark all messages in a chat as _noticed_.
        _Noticed_ messages are no longer _fresh_ and do not count as being unseen
        but are still waiting for being marked as "seen" using markseen_msgs()
        (read receipts aren't sent for noticed messages).

        Calling this function usually results in the event #DC_EVENT_MSGS_NOTICED.
        See also markseen_msgs().
        """
        self.transport.call("marknoticed_chat", account_id, chat_id)

    def markfresh_chat(self, account_id: int, chat_id: int) -> None:
        """
        Marks the last incoming message in the chat as _fresh_.

        UI can use this to offer a "mark unread" option,
        so that already noticed chats get a badge counter again.
        """
        self.transport.call("markfresh_chat", account_id, chat_id)

    def get_first_unread_message_of_chat(self, account_id: int, chat_id: int) -> Optional[int]:
        """
        Returns the message that is immediately followed by the last seen
        message.
        From the point of view of the user this is effectively
        "first unread", but in reality in the database a seen message
        _can_ be followed by a fresh (unseen) message
        if that message has not been individually marked as seen.
        """
        return self.transport.call("get_first_unread_message_of_chat", account_id, chat_id)

    def set_chat_mute_duration(self, account_id: int, chat_id: int, duration: MuteDuration) -> None:
        """
        Set mute duration of a chat.

        The UI can then call is_chat_muted() when receiving a new message
        to decide whether it should trigger an notification.

        Muted chats should not sound or vibrate
        and should not show a visual notification in the system area.
        Moreover, muted chats should be excluded from global badge counter
        (get_fresh_msgs() skips muted chats therefore)
        and the in-app, per-chat badge counter should use a less obtrusive color.

        Sends out #DC_EVENT_CHAT_MODIFIED.
        """
        self.transport.call("set_chat_mute_duration", account_id, chat_id, _wrap(duration))

    def is_chat_muted(self, account_id: int, chat_id: int) -> bool:
        """
        Check whether the chat is currently muted (can be changed by set_chat_mute_duration()).

        This is available as a standalone function outside of fullchat, because it might be only needed for notification
        """
        return self.transport.call("is_chat_muted", account_id, chat_id)

    def markseen_msgs(self, account_id: int, msg_ids: list[int]) -> None:
        """
        Mark messages as presented to the user.
        Typically, UIs call this function on scrolling through the message list,
        when the messages are presented at least for a little moment.
        The concrete action depends on the type of the chat and on the users settings
        (dc_msgs_presented() may be a better name therefore, but well. :)

        - For normal chats, the IMAP state is updated, MDN is sent
        (if set_config()-options `mdns_enabled` is set)
        and the internal state is changed to @ref DC_STATE_IN_SEEN to reflect these actions.

        - For contact requests, no IMAP or MDNs is done
        and the internal state is not changed therefore.
        See also marknoticed_chat().

        Moreover, timer is started for incoming ephemeral messages.
        This also happens for contact requests chats.

        This function updates `last_msg_id` configuration value
        to the maximum of the current value and IDs passed to this function.
        Bots which mark messages as seen can rely on this side effect
        to avoid updating `last_msg_id` value manually.

        One #DC_EVENT_MSGS_NOTICED event is emitted per modified chat.
        """
        self.transport.call("markseen_msgs", account_id, msg_ids)

    def get_message_ids(
        self, account_id: int, chat_id: int, info_only: bool, add_daymarker: bool
    ) -> list[int]:
        """
        Get all message IDs belonging to a chat.

        The list is already sorted and starts with the oldest message.
        Clients should not try to re-sort the list as this would be an expensive action
        and would result in inconsistencies between clients.
        Note that the messages are not necessarily sorted by their ID or by their displayed timestamp;
        UIs need to handle both the case of descending message IDs
        and of decreasing timestamps.

        Optionally, 'daymarkers' added to the ID array may help to
        implement virtual lists.

        Parameters:

        * chat_id The chat ID of which the messages IDs should be queried.
        * _info_only: Deprecated, pass `false` here.
        * `add_daymarker` - If `true`, add day markers as `DC_MSG_ID_DAYMARKER` to the result,
        e.g. [1234, 1237, 9, 1239]. The day marker timestamp is the midnight one for the
        corresponding (following) day in the local timezone.
        """
        return self.transport.call("get_message_ids", account_id, chat_id, info_only, add_daymarker)

    def get_existing_msg_ids(self, account_id: int, msg_ids: list[int]) -> list[int]:
        """
        Checks if the messages with given IDs exist.

        Returns IDs of existing messages.
        """
        return self.transport.call("get_existing_msg_ids", account_id, msg_ids)

    def get_message_list_items(
        self, account_id: int, chat_id: int, info_only: bool, add_daymarker: bool
    ) -> list[MessageListItem]:
        """
        Get all messages belonging to a chat.

        Similar to `get_message_ids` / `getMessageIds`,
        see that function for details.
        The difference is that this function here returns a list of `MessageListItem`,
        which is an enum of a message or a daymarker.
        """
        _result = self.transport.call(
            "get_message_list_items", account_id, chat_id, info_only, add_daymarker
        )
        return [_unmarshalMessageListItem(_item) for _item in _result]

    def get_message(self, account_id: int, msg_id: int) -> Message:
        _result = self.transport.call("get_message", account_id, msg_id)
        return _from_dict(Message, _result)

    def get_message_html(self, account_id: int, message_id: int) -> Optional[str]:
        return self.transport.call("get_message_html", account_id, message_id)

    def get_messages(self, account_id: int, message_ids: list[int]) -> dict[Any, MessageLoadResult]:
        """
        get multiple messages in one call,
        if loading one message fails the error is stored in the result object in it's place.

        this is the batch variant of [get_message]
        """
        _result = self.transport.call("get_messages", account_id, message_ids)
        return {_key: _unmarshalMessageLoadResult(_val) for _key, _val in _result.items()}

    def get_message_notification_info(
        self, account_id: int, message_id: int
    ) -> MessageNotificationInfo:
        """Fetch info desktop needs for creating a notification for a message"""
        _result = self.transport.call("get_message_notification_info", account_id, message_id)
        return _from_dict(MessageNotificationInfo, _result)

    def delete_messages(self, account_id: int, message_ids: list[int]) -> None:
        """
        Delete messages. The messages are deleted on the current device and
        on the IMAP server.
        """
        self.transport.call("delete_messages", account_id, message_ids)

    def delete_messages_for_all(self, account_id: int, message_ids: list[int]) -> None:
        """
        Delete messages. The messages are deleted on the current device,
        on the IMAP server and also for all chat members
        """
        self.transport.call("delete_messages_for_all", account_id, message_ids)

    def get_message_info(self, account_id: int, message_id: int) -> str:
        """
        Get an informational text for a single message. The text is multiline and may
        contain e.g. the raw text of the message.

        The max. text returned is typically longer (about 100000 characters) than the
        max. text returned by dc_msg_get_text() (about 30000 characters).
        """
        return self.transport.call("get_message_info", account_id, message_id)

    def get_message_info_object(self, account_id: int, message_id: int) -> MessageInfo:
        """Returns additional information for single message."""
        _result = self.transport.call("get_message_info_object", account_id, message_id)
        return _from_dict(MessageInfo, _result)

    def get_message_read_receipt_count(self, account_id: int, message_id: int) -> int:
        """
        Returns count of read receipts on message.

        This view count is meant as a feedback measure for the channel owner only.
        """
        return self.transport.call("get_message_read_receipt_count", account_id, message_id)

    def get_message_read_receipts(
        self, account_id: int, message_id: int
    ) -> list[MessageReadReceipt]:
        """Returns contacts that sent read receipts and the time of reading."""
        _result = self.transport.call("get_message_read_receipts", account_id, message_id)
        return [_from_dict(MessageReadReceipt, _item) for _item in _result]

    def download_full_message(self, account_id: int, message_id: int) -> None:
        """
        Asks the core to start downloading a message fully.
        This function is typically called when the user hits the "Download" button
        that is shown by the UI in case `download_state` is `'Available'` or `'Failure'`

        On success, the @ref DC_MSG "view type of the message" may change
        or the message may be replaced completely by one or more messages with other message IDs.
        That may happen e.g. in cases where the message was encrypted
        and the type could not be determined without fully downloading.
        Downloaded content can be accessed as usual after download.

        To reflect these changes a @ref DC_EVENT_MSGS_CHANGED event will be emitted.
        """
        self.transport.call("download_full_message", account_id, message_id)

    def search_messages(self, account_id: int, query: str, chat_id: Optional[int]) -> list[int]:
        """
        Search messages containing the given query string.
        Searching can be done globally (chat_id=None) or in a specified chat only (chat_id set).

        Global search results are typically displayed using dc_msg_get_summary(), chat
        search results may just highlight the corresponding messages and present a
        prev/next button.

        For the global search, the result is limited to 1000 messages,
        this allows an incremental search done fast.
        So, when getting exactly 1000 messages, the result actually may be truncated;
        the UIs may display sth. like "1000+ messages found" in this case.
        The chat search (if chat_id is set) is not limited.
        """
        return self.transport.call("search_messages", account_id, query, chat_id)

    def message_ids_to_search_results(
        self, account_id: int, message_ids: list[int]
    ) -> dict[Any, MessageSearchResult]:
        _result = self.transport.call("message_ids_to_search_results", account_id, message_ids)
        return {_key: _from_dict(MessageSearchResult, _val) for _key, _val in _result.items()}

    def save_msgs(self, account_id: int, message_ids: list[int]) -> None:
        self.transport.call("save_msgs", account_id, message_ids)

    def get_contact(self, account_id: int, contact_id: int) -> Contact:
        """Get a single contact options by ID."""
        _result = self.transport.call("get_contact", account_id, contact_id)
        return _from_dict(Contact, _result)

    def create_contact(self, account_id: int, email: str, name: Optional[str]) -> int:
        """
        Add a single contact as a result of an explicit user action.

        This will always create or look up an address-contact,
        i.e. a contact identified by an email address,
        with all messages sent to and from this contact being unencrypted.
        If the user just clicked on an email address,
        you should first check [`Rpc.lookup_contact_id_by_addr`]/`lookupContactIdByAddr.`,
        and only if there is no contact yet, call this function here.

        Returns contact id of the created or existing contact.
        """
        return self.transport.call("create_contact", account_id, email, name)

    def create_chat_by_contact_id(self, account_id: int, contact_id: int) -> int:
        """Returns contact id of the created or existing DM chat with that contact"""
        return self.transport.call("create_chat_by_contact_id", account_id, contact_id)

    def block_contact(self, account_id: int, contact_id: int) -> None:
        self.transport.call("block_contact", account_id, contact_id)

    def unblock_contact(self, account_id: int, contact_id: int) -> None:
        self.transport.call("unblock_contact", account_id, contact_id)

    def get_blocked_contacts(self, account_id: int) -> list[Contact]:
        _result = self.transport.call("get_blocked_contacts", account_id)
        return [_from_dict(Contact, _item) for _item in _result]

    def get_contact_ids(self, account_id: int, list_flags: int, query: Optional[str]) -> list[int]:
        """
        Returns ids of known and unblocked contacts.

        By default, key-contacts are listed.

        * `list_flags` - A combination of flags:
        - `DC_GCL_ADD_SELF` - Add SELF unless filtered by other parameters.
        - `DC_GCL_ADDRESS` - List address-contacts instead of key-contacts.
        * `query` - A string to filter the list.
        """
        return self.transport.call("get_contact_ids", account_id, list_flags, query)

    def get_contacts(self, account_id: int, list_flags: int, query: Optional[str]) -> list[Contact]:
        """
        Returns known and unblocked contacts.

        Formerly called `getContacts2` in Desktop.
        See [`Rpc.get_contact_ids`] for parameters and more info.
        """
        _result = self.transport.call("get_contacts", account_id, list_flags, query)
        return [_from_dict(Contact, _item) for _item in _result]

    def get_contacts_by_ids(self, account_id: int, ids: list[int]) -> dict[Any, Contact]:
        _result = self.transport.call("get_contacts_by_ids", account_id, ids)
        return {_key: _from_dict(Contact, _val) for _key, _val in _result.items()}

    def delete_contact(self, account_id: int, contact_id: int) -> None:
        self.transport.call("delete_contact", account_id, contact_id)

    def change_contact_name(self, account_id: int, contact_id: int, name: str) -> None:
        """Sets display name for existing contact."""
        self.transport.call("change_contact_name", account_id, contact_id, name)

    def get_contact_encryption_info(self, account_id: int, contact_id: int) -> str:
        """
        Get encryption info for a contact.
        Get a multi-line encryption info, containing your fingerprint and the
        fingerprint of the contact, used e.g. to compare the fingerprints for a simple out-of-band verification.
        """
        return self.transport.call("get_contact_encryption_info", account_id, contact_id)

    def lookup_contact_id_by_addr(self, account_id: int, addr: str) -> Optional[int]:
        """
        Looks up a known and unblocked contact with a given e-mail address.
        To get a list of all known and unblocked contacts, use contacts_get_contacts().

        **POTENTIAL SECURITY ISSUE**: If there are multiple contacts with this address
        (e.g. an address-contact and a key-contact),
        this looks up the most recently seen contact,
        i.e. which contact is returned depends on which contact last sent a message.
        If the user just clicked on a mailto: link, then this is the best thing you can do.
        But **DO NOT** internally represent contacts by their email address
        and do not use this function to look them up;
        otherwise this function will sometimes look up the wrong contact.
        Instead, you should internally represent contacts by their ids.

        To validate an e-mail address independently of the contact database
        use check_email_validity().
        """
        return self.transport.call("lookup_contact_id_by_addr", account_id, addr)

    def parse_vcard(self, path: str) -> list[VcardContact]:
        """Parses a vCard file located at the given path. Returns contacts in their original order."""
        _result = self.transport.call("parse_vcard", path)
        return [_from_dict(VcardContact, _item) for _item in _result]

    def import_vcard(self, account_id: int, path: str) -> list[int]:
        """
        Imports contacts from a vCard file located at the given path.

        Returns the ids of created/modified contacts in the order they appear in the vCard.
        """
        return self.transport.call("import_vcard", account_id, path)

    def import_vcard_contents(self, account_id: int, vcard: str) -> list[int]:
        """
        Imports contacts from a vCard.

        Returns the ids of created/modified contacts in the order they appear in the vCard.
        """
        return self.transport.call("import_vcard_contents", account_id, vcard)

    def make_vcard(self, account_id: int, contacts: list[int]) -> str:
        """Returns a vCard containing contacts with the given ids."""
        return self.transport.call("make_vcard", account_id, contacts)

    def get_chat_id_by_contact_id(self, account_id: int, contact_id: int) -> Optional[int]:
        """
        Returns the [`ChatId`] for the 1:1 chat with `contact_id` if it exists.

        If it does not exist, `None` is returned.
        """
        return self.transport.call("get_chat_id_by_contact_id", account_id, contact_id)

    def get_chat_media(
        self,
        account_id: int,
        chat_id: Optional[int],
        message_type: Viewtype,
        or_message_type2: Optional[Viewtype],
        or_message_type3: Optional[Viewtype],
    ) -> list[int]:
        """
        Returns all message IDs of the given types in a chat.
        Typically used to show a gallery.

        The list is already sorted and starts with the oldest message.
        Clients should not try to re-sort the list as this would be an expensive action
        and would result in inconsistencies between clients.

        Setting `chat_id` to `None` (`null` in typescript) means get messages with media
        from any chat of the currently used account.
        """
        return self.transport.call(
            "get_chat_media", account_id, chat_id, message_type, or_message_type2, or_message_type3
        )

    def export_backup(self, account_id: int, destination: str, passphrase: Optional[str]) -> None:
        self.transport.call("export_backup", account_id, destination, passphrase)

    def import_backup(self, account_id: int, path: str, passphrase: Optional[str]) -> None:
        self.transport.call("import_backup", account_id, path, passphrase)

    def provide_backup(self, account_id: int) -> None:
        """
        Offers a backup for remote devices to retrieve.

        Can be canceled by stopping the ongoing process.  Success or failure can be tracked
        via the `ImexProgress` event which should either reach `1000` for success or `0` for
        failure.

        This **stops IO** while it is running.

        Returns once a remote device has retrieved the backup, or is canceled.
        """
        self.transport.call("provide_backup", account_id)

    def get_backup_qr(self, account_id: int) -> str:
        """
        Returns the text of the QR code for the running [`Rpc.provide_backup`].

        This QR code text can be used in [`Rpc.get_backup`] on a second device to
        retrieve the backup and setup this second device.

        This call will block until the QR code is ready,
        even if there is no concurrent call to [`Rpc.provide_backup`],
        but will fail after 60 seconds to avoid deadlocks.
        """
        return self.transport.call("get_backup_qr", account_id)

    def get_backup_qr_svg(self, account_id: int) -> str:
        """
        Returns the rendered QR code for the running [`Rpc.provide_backup`].

        This QR code can be used in [`Rpc.get_backup`] on a second device to
        retrieve the backup and setup this second device.

        This call will block until the QR code is ready,
        even if there is no concurrent call to [`Rpc.provide_backup`],
        but will fail after 60 seconds to avoid deadlocks.

        @deprecated as of 2026-03; use `create_qr_svg(get_backup_qr())` instead.

        Returns the QR code rendered as an SVG image.
        """
        return self.transport.call("get_backup_qr_svg", account_id)

    def create_qr_svg(self, text: str) -> str:
        """Renders the given text as a QR code SVG image."""
        return self.transport.call("create_qr_svg", text)

    def get_backup(self, account_id: int, qr_text: str) -> None:
        """
        Gets a backup from a remote provider.

        This retrieves the backup from a remote device over the network and imports it into
        the current device.

        Can be canceled by stopping the ongoing process.

        Do not forget to call start_io on the account after a successful import,
        otherwise it will not connect to the email server.
        """
        self.transport.call("get_backup", account_id, qr_text)

    def maybe_network(self) -> None:
        """
        Indicate that the network likely has come back.
        or just that the network conditions might have changed
        """
        self.transport.call("maybe_network")

    def get_connectivity(self, account_id: int) -> int:
        """
        Get the current connectivity, i.e. whether the device is connected to the IMAP server.
        One of:
        - DC_CONNECTIVITY_NOT_CONNECTED (1000-1999): Show e.g. the string "Not connected" or a red dot
        - DC_CONNECTIVITY_CONNECTING (2000-2999): Show e.g. the string "Connecting…" or a yellow dot
        - DC_CONNECTIVITY_WORKING (3000-3999): Show e.g. the string "Getting new messages" or a spinning wheel
        - DC_CONNECTIVITY_CONNECTED (>=4000): Show e.g. the string "Connected" or a green dot

        We don't use exact values but ranges here so that we can split up
        states into multiple states in the future.

        Meant as a rough overview that can be shown
        e.g. in the title of the main screen.

        If the connectivity changes, a #DC_EVENT_CONNECTIVITY_CHANGED will be emitted.
        """
        return self.transport.call("get_connectivity", account_id)

    def get_connectivity_html(self, account_id: int) -> str:
        """
        Get an overview of the current connectivity, and possibly more statistics.
        Meant to give the user more insight about the current status than
        the basic connectivity info returned by get_connectivity(); show this
        e.g., if the user taps on said basic connectivity info.

        If this page changes, a #DC_EVENT_CONNECTIVITY_CHANGED will be emitted.

        This comes as an HTML from the core so that we can easily improve it
        and the improvement instantly reaches all UIs.
        """
        return self.transport.call("get_connectivity_html", account_id)

    def set_location(self, latitude: float, longitude: float, accuracy: float) -> bool:
        """
        Sets current location.

        Returns true if location streaming is currently
        enabled and locations should be updated.

        Location is represented as latitude and longitude in degrees
        and horizontal accuracy in meters.
        """
        return self.transport.call("set_location", latitude, longitude, accuracy)

    def get_locations(
        self,
        account_id: int,
        chat_id: Optional[int],
        contact_id: Optional[int],
        timestamp_begin: int,
        timestamp_end: int,
    ) -> list[Location]:
        _result = self.transport.call(
            "get_locations", account_id, chat_id, contact_id, timestamp_begin, timestamp_end
        )
        return [_from_dict(Location, _item) for _item in _result]

    def send_locations_to_chat(self, account_id: int, chat_id: int, seconds: int) -> None:
        """
        Enables location streaming in chat identified by `chat_id` for `seconds` seconds.

        Pass 0 as the number of seconds to disable location streaming in the chat.
        """
        self.transport.call("send_locations_to_chat", account_id, chat_id, seconds)

    def is_sending_locations(self, account_id: int) -> bool:
        """Returns whether any chat is sending locations."""
        return self.transport.call("is_sending_locations", account_id)

    def is_sending_locations_to_chat(self, account_id: int, chat_id: int) -> bool:
        """Returns whether `chat_id` is sending locations."""
        return self.transport.call("is_sending_locations_to_chat", account_id, chat_id)

    def stop_sending_locations(self) -> None:
        """Stops sending locations to all chats."""
        self.transport.call("stop_sending_locations")

    def send_webxdc_status_update(
        self, account_id: int, instance_msg_id: int, update_str: str, descr: Optional[str]
    ) -> None:
        self.transport.call(
            "send_webxdc_status_update", account_id, instance_msg_id, update_str, descr
        )

    def send_webxdc_realtime_data(
        self, account_id: int, instance_msg_id: int, data: list[int]
    ) -> None:
        self.transport.call("send_webxdc_realtime_data", account_id, instance_msg_id, data)

    def send_webxdc_realtime_advertisement(self, account_id: int, instance_msg_id: int) -> None:
        self.transport.call("send_webxdc_realtime_advertisement", account_id, instance_msg_id)

    def leave_webxdc_realtime(self, account_id: int, instance_message_id: int) -> None:
        """
        Leaves the gossip of the webxdc with the given message id.

        NB: When this is called before closing a webxdc app in UIs, it must be guaranteed that
        `send_webxdc_realtime_*()` functions aren't called for the given `instance_message_id`
        anymore until the app is open again.
        """
        self.transport.call("leave_webxdc_realtime", account_id, instance_message_id)

    def get_webxdc_status_updates(
        self, account_id: int, instance_msg_id: int, last_known_serial: int
    ) -> str:
        return self.transport.call(
            "get_webxdc_status_updates", account_id, instance_msg_id, last_known_serial
        )

    def get_webxdc_info(self, account_id: int, instance_msg_id: int) -> WebxdcMessageInfo:
        """Get info from a webxdc message"""
        _result = self.transport.call("get_webxdc_info", account_id, instance_msg_id)
        return _from_dict(WebxdcMessageInfo, _result)

    def get_webxdc_href(self, account_id: int, info_msg_id: int) -> Optional[str]:
        """
        Get href from a WebxdcInfoMessage which might include a hash holding
        information about a specific position or state in a webxdc app (optional)
        """
        return self.transport.call("get_webxdc_href", account_id, info_msg_id)

    def get_webxdc_blob(self, account_id: int, instance_msg_id: int, path: str) -> str:
        """
        Get blob encoded as base64 from a webxdc message

        path is the path of the file within webxdc archive
        """
        return self.transport.call("get_webxdc_blob", account_id, instance_msg_id, path)

    def set_webxdc_integration(self, account_id: int, file_path: str) -> None:
        """
        Sets Webxdc file as integration.
        `file` is the .xdc to use as Webxdc integration.
        """
        self.transport.call("set_webxdc_integration", account_id, file_path)

    def init_webxdc_integration(self, account_id: int, chat_id: Optional[int]) -> Optional[int]:
        """
        Returns Webxdc instance used for optional integrations.
        UI can open the Webxdc as usual.
        Returns `None` if there is no integration; the caller can add one using `set_webxdc_integration` then.
        `integrate_for` is the chat to get the integration for.
        """
        return self.transport.call("init_webxdc_integration", account_id, chat_id)

    def place_outgoing_call(
        self, account_id: int, chat_id: int, place_call_info: str, has_video: bool
    ) -> int:
        """Starts an outgoing call."""
        return self.transport.call(
            "place_outgoing_call", account_id, chat_id, place_call_info, has_video
        )

    def accept_incoming_call(self, account_id: int, msg_id: int, accept_call_info: str) -> None:
        """Accepts an incoming call."""
        self.transport.call("accept_incoming_call", account_id, msg_id, accept_call_info)

    def end_call(self, account_id: int, msg_id: int) -> None:
        """Ends incoming or outgoing call."""
        self.transport.call("end_call", account_id, msg_id)

    def call_info(self, account_id: int, msg_id: int) -> CallInfo:
        """Returns information about the call."""
        _result = self.transport.call("call_info", account_id, msg_id)
        return _from_dict(CallInfo, _result)

    def ice_servers(self, account_id: int) -> str:
        """Returns JSON with ICE servers, to be used for WebRTC video calls."""
        return self.transport.call("ice_servers", account_id)

    def get_http_response(self, account_id: int, url: str) -> HttpResponse:
        """
        Makes an HTTP GET request and returns a response.

        `url` is the HTTP or HTTPS URL.
        """
        _result = self.transport.call("get_http_response", account_id, url)
        return _from_dict(HttpResponse, _result)

    def forward_messages(self, account_id: int, message_ids: list[int], chat_id: int) -> None:
        """
        Forward messages to another chat.

        All types of messages can be forwarded,
        however, they will be flagged as such (dc_msg_is_forwarded() is set).

        Original sender, info-state and webxdc updates are not forwarded on purpose.
        """
        self.transport.call("forward_messages", account_id, message_ids, chat_id)

    def forward_messages_to_account(
        self, src_account_id: int, src_message_ids: list[int], dst_account_id: int, dst_chat_id: int
    ) -> None:
        """
        Forward messages to a chat in another account.
        See [`Rpc.forward_messages`] for more info.
        """
        self.transport.call(
            "forward_messages_to_account",
            src_account_id,
            src_message_ids,
            dst_account_id,
            dst_chat_id,
        )

    def resend_messages(self, account_id: int, message_ids: list[int]) -> None:
        """
        Resend messages and make information available for newly added chat members.
        Resending sends out the original message, however, recipients and webxdc-status may differ.
        Clients that already have the original message can still ignore the resent message as
        they have tracked the state by dedicated updates.

        Some messages cannot be resent, eg. info-messages, drafts, already pending messages or messages that are not sent by SELF.

        message_ids all message IDs that should be resend. All messages must belong to the same chat.
        """
        self.transport.call("resend_messages", account_id, message_ids)

    def send_sticker(self, account_id: int, chat_id: int, sticker_path: str) -> int:
        """@deprecated as of 2026-04; use `send_msg` with `Viewtype.Sticker` instead."""
        return self.transport.call("send_sticker", account_id, chat_id, sticker_path)

    def send_reaction(self, account_id: int, message_id: int, reaction: list[str]) -> int:
        """
        Sends a reaction to message.

        A reaction is a string that represents an emoji.
        You can call this function again to change the emoji;
        the last sent reaction overrides all previously sent reactions.
        It is possible to remove the reaction by sending an empty string.
        """
        return self.transport.call("send_reaction", account_id, message_id, reaction)

    def get_message_reactions(self, account_id: int, message_id: int) -> Optional[Reactions]:
        """Returns reactions to the message."""
        _result = self.transport.call("get_message_reactions", account_id, message_id)
        return _result and _from_dict(Reactions, _result)

    def send_msg(self, account_id: int, chat_id: int, data: MessageData) -> int:
        return self.transport.call("send_msg", account_id, chat_id, _wrap(data))

    def send_edit_request(self, account_id: int, msg_id: int, new_text: str) -> None:
        self.transport.call("send_edit_request", account_id, msg_id, new_text)

    def can_send(self, account_id: int, chat_id: int) -> bool:
        """Checks if messages can be sent to a given chat."""
        return self.transport.call("can_send", account_id, chat_id)

    def save_msg_file(self, account_id: int, msg_id: int, path: str) -> None:
        """
        Saves a file copy at the user-provided path.

        Fails if file already exists at the provided path.
        """
        self.transport.call("save_msg_file", account_id, msg_id, path)

    def remove_draft(self, account_id: int, chat_id: int) -> None:
        self.transport.call("remove_draft", account_id, chat_id)

    def get_draft(self, account_id: int, chat_id: int) -> Optional[Message]:
        """Get draft for a chat, if any."""
        _result = self.transport.call("get_draft", account_id, chat_id)
        return _result and _from_dict(Message, _result)

    def misc_get_sticker_folder(self, account_id: int) -> str:
        return self.transport.call("misc_get_sticker_folder", account_id)

    def misc_save_sticker(self, account_id: int, msg_id: int, collection: str) -> None:
        """Saves a sticker to a collection/folder in the account's sticker folder."""
        self.transport.call("misc_save_sticker", account_id, msg_id, collection)

    def misc_get_stickers(self, account_id: int) -> dict[Any, list[str]]:
        """
        for desktop, get stickers from stickers folder,
        grouped by the collection/folder they are in.
        """
        return self.transport.call("misc_get_stickers", account_id)

    def misc_send_text_message(self, account_id: int, chat_id: int, text: str) -> int:
        """Returns the messageid of the sent message"""
        return self.transport.call("misc_send_text_message", account_id, chat_id, text)

    def misc_send_msg(
        self,
        account_id: int,
        chat_id: int,
        text: Optional[str],
        file: Optional[str],
        filename: Optional[str],
        location: Optional[tuple[float, float]],
        quoted_message_id: Optional[int],
    ) -> tuple[int, Message]:
        """
        Send a message to a chat.

        This function returns after the message has been placed in the sending queue.
        This does not imply that the message was really sent out yet.
        However, from your view, you're done with the message.
        Sooner or later it will find its way.

        **Attaching files:**

        Pass the file path in the `file` parameter.
        If `file` is not in the blob directory yet,
        it will be copied into the blob directory.
        If you want, you can delete the file immediately after this function returns.

        You can also write the attachment directly into the blob directory
        and then pass the path as the `file` parameter;
        this will prevent an unnecessary copying of the file.

        In `filename`, you can pass the original name of the file,
        which will then be shown in the UI.
        in this case the current name of `file` on the filesystem will be ignored.

        In order to deduplicate files that contain the same data,
        the file will be named `<hash>.<extension>`, e.g. `ce940175885d7b78f7b7e9f1396611f.jpg`.

        NOTE:
        - This function will rename the file. To get the new file path, call `get_file()`.
        - The file must not be modified after this function was called.
        - Images etc. will NOT be recoded.
        In order to recode images,
        use `misc_set_draft` and pass `Image` as the viewtype.
        """
        return self.transport.call(
            "misc_send_msg", account_id, chat_id, text, file, filename, location, quoted_message_id
        )

    def misc_set_draft(
        self,
        account_id: int,
        chat_id: int,
        text: Optional[str],
        file: Optional[str],
        filename: Optional[str],
        quoted_message_id: Optional[int],
        view_type: Optional[Viewtype],
    ) -> None:
        self.transport.call(
            "misc_set_draft",
            account_id,
            chat_id,
            text,
            file,
            filename,
            quoted_message_id,
            view_type,
        )

    def misc_send_draft(self, account_id: int, chat_id: int) -> int:
        return self.transport.call("misc_send_draft", account_id, chat_id)
