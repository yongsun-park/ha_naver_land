from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the integration from a config entry."""
    apt_id = entry.data["username"]
    area = entry.data["variables"]
    exclude_low_floors = entry.options.get("exclude_low_floors", False)
    low_floor_limit = entry.options.get("low_floor_limit", 5)

    # NaverLandApi 객체 저장
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "apt_id": apt_id,
        "area": area,
        "exclude_low_floors": exclude_low_floors,
        "low_floor_limit": low_floor_limit,
    }

    # 센서 플랫폼 설정
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
