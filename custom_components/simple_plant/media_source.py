# MIT LICENCE - Copyright (c) 2026  ndesgranges
"""Expose the plants photo history as a media source."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from aiohttp import web
from homeassistant.components.http import KEY_HASS, HomeAssistantView
from homeassistant.components.media_player import BrowseError, MediaClass
from homeassistant.components.media_source import (
    BrowseMediaSource,
    MediaSource,
    MediaSourceItem,
    PlayMedia,
    Unresolvable,
)
from homeassistant.util.dt import as_local

from .const import DOMAIN, IMAGES_MIME_TYPES

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

PHOTO_URL = f"/api/{DOMAIN}/photo"


async def async_get_media_source(hass: HomeAssistant) -> SimplePlantMediaSource:
    """Set up the Simple Plant media source."""
    return SimplePlantMediaSource(hass)


def _get_photo(
    hass: HomeAssistant, entry_id: str, filename: str
) -> dict[str, Any] | None:
    """Return the photo of a plant history matching the filename."""
    entry = hass.config_entries.async_get_entry(entry_id)
    if entry is None or entry.domain != DOMAIN:
        return None
    return next(
        (
            photo
            for photo in entry.data.get("photo_history", [])
            if Path(photo["path"]).name == filename
        ),
        None,
    )


def _photo_file(hass: HomeAssistant, photo: dict[str, Any]) -> Path:
    """Return the file path of a photo."""
    return Path(hass.config.path(photo["path"].lstrip("/")))


class SimplePlantPhotoView(HomeAssistantView):
    """Serve the photos of the plants history to authenticated users."""

    url = PHOTO_URL + "/{entry_id}/{filename}"
    name = f"api:{DOMAIN}:photo"

    async def get(
        self, request: web.Request, entry_id: str, filename: str
    ) -> web.FileResponse:
        """Serve a photo."""
        hass = request.app[KEY_HASS]
        if (photo := _get_photo(hass, entry_id, filename)) is None:
            raise web.HTTPNotFound
        return web.FileResponse(_photo_file(hass, photo))


class SimplePlantMediaSource(MediaSource):
    """Provide the plants photo history as media sources."""

    name: str = "Simple Plant"

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the media source."""
        super().__init__(DOMAIN)
        self.hass = hass

    async def async_resolve_media(self, item: MediaSourceItem) -> PlayMedia:
        """Resolve a photo to a url."""
        entry_id, _, filename = (item.identifier or "").partition("/")
        if (photo := _get_photo(self.hass, entry_id, filename)) is None:
            msg = f"Could not resolve media item: {item.identifier}"
            raise Unresolvable(msg)
        return PlayMedia(
            f"{PHOTO_URL}/{entry_id}/{filename}",
            _content_type(photo),
            path=_photo_file(self.hass, photo),
        )

    async def async_browse_media(self, item: MediaSourceItem) -> BrowseMediaSource:
        """Browse plants, then their photos."""
        entries = {
            entry.entry_id: entry
            for entry in self.hass.config_entries.async_entries(DOMAIN)
            if entry.data.get("photo_history")
        }
        if not item.identifier:
            return self._browse_root(list(entries.values()))
        if item.identifier in entries:
            return self._browse_plant(entries[item.identifier], with_children=True)
        msg = f"Unknown item: {item.identifier}"
        raise BrowseError(msg)

    def _browse_root(self, entries: list[ConfigEntry]) -> BrowseMediaSource:
        return BrowseMediaSource(
            domain=DOMAIN,
            identifier=None,
            media_class=MediaClass.DIRECTORY,
            media_content_type="",
            title=self.name,
            can_play=False,
            can_expand=True,
            children_media_class=MediaClass.DIRECTORY,
            children=[
                self._browse_plant(entry, with_children=False)
                for entry in sorted(entries, key=lambda entry: entry.title.lower())
            ],
        )

    def _browse_plant(
        self, entry: ConfigEntry, *, with_children: bool
    ) -> BrowseMediaSource:
        photos = entry.data["photo_history"]
        return BrowseMediaSource(
            domain=DOMAIN,
            identifier=entry.entry_id,
            media_class=MediaClass.DIRECTORY,
            media_content_type="",
            title=entry.title,
            thumbnail=_url(entry, photos[-1]),
            can_play=False,
            can_expand=True,
            children_media_class=MediaClass.IMAGE,
            children=[_browse_photo(entry, photo) for photo in photos]
            if with_children
            else None,
        )


def _browse_photo(entry: ConfigEntry, photo: dict[str, Any]) -> BrowseMediaSource:
    filename = Path(photo["path"]).name
    date = as_local(datetime.fromisoformat(photo["date"]))
    return BrowseMediaSource(
        domain=DOMAIN,
        identifier=f"{entry.entry_id}/{filename}",
        media_class=MediaClass.IMAGE,
        media_content_type=_content_type(photo),
        title=date.strftime("%Y-%m-%d %H:%M"),
        thumbnail=_url(entry, photo),
        can_play=True,
        can_expand=False,
    )


def _url(entry: ConfigEntry, photo: dict[str, Any]) -> str:
    return f"{PHOTO_URL}/{entry.entry_id}/{Path(photo['path']).name}"


def _content_type(photo: dict[str, Any]) -> str:
    return IMAGES_MIME_TYPES.get(Path(photo["path"]).suffix, "image/jpeg")
