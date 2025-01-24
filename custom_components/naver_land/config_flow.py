import logging
from typing import Any

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_USERNAME, CONF_VARIABLES
from .naver_land import NaverLandApi
from .const import DOMAIN, TITLE

_LOGGER = logging.getLogger(__name__)

# 필드 추가: 저층 제외 여부 및 제외할 층수
CONF_EXCLUDE_LOW_FLOORS = "exclude_low_floors"
CONF_LOW_FLOOR_LIMIT = "low_floor_limit"

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_VARIABLES): cv.string,
        vol.Optional(CONF_EXCLUDE_LOW_FLOORS, default=False): cv.boolean,
        vol.Optional(CONF_LOW_FLOOR_LIMIT, default=5): cv.positive_int,
    }
)


async def async_validate_login(hass, apt_id: str, area: str) -> dict[str, Any]:
    """아파트 ID와 지역 정보가 유효한지 확인."""
    client = NaverLandApi(apt_id, area)

    errors = {}
    try:
        apt_name = await client.get_apt_name()
        if apt_name is None:
            _LOGGER.exception("아파트 정보 취득 실패")
            errors["base"] = "invalid_apt_id"
    except Exception as ex:
        _LOGGER.exception("아파트 정보 취득 실패 : %s", ex)
        errors["base"] = "invalid_apt_id"
    return errors


class NaverLandConfigFlow(ConfigFlow, domain=DOMAIN):
    """설정 흐름 정의."""
    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """초기 단계 처리."""

        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        apt_id = user_input[CONF_USERNAME]
        area = user_input[CONF_VARIABLES]
        exclude_low_floors = user_input[CONF_EXCLUDE_LOW_FLOORS]
        low_floor_limit = user_input[CONF_LOW_FLOOR_LIMIT]

        # 아파트 ID와 지역 정보 유효성 검증
        if errors := await async_validate_login(self.hass, apt_id, area):
            return self.async_show_form(
                step_id="user",
                data_schema=STEP_USER_DATA_SCHEMA,
                errors=errors,
            )

        # 유효성 검증 통과 후 설정 저장
        await self.async_set_unique_id(f"{DOMAIN}_{apt_id}")
        self._abort_if_unique_id_configured()
        return self.async_create_entry(
            title=f"{TITLE} ({apt_id})",
            data={
                CONF_USERNAME: apt_id,
                CONF_VARIABLES: area,
                CONF_EXCLUDE_LOW_FLOORS: exclude_low_floors,
                CONF_LOW_FLOOR_LIMIT: low_floor_limit,
            },
        )
