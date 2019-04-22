"""Platform for Grocy integration."""
import logging

import voluptuous as vol
from homeassistant.components.sensor import Sensor, PLATFORM_SCHEMA
from homeassistant.const import CONF_URL, CONF_API_KEY
import homeassistant.helpers.config_validation as cv


_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_URL): cv.string,
    vol.Required(CONF_API_KEY): cv.string,
})

def setup_platform(hass, config, add_devices, discovery_info=None):
    from pygrocy import Grocy
    import json

    api_url = config.get(CONF_URL)
    password = config.get(CONF_API_KEY)

    _LOGGER.debug("Trying to set up grocy client...")
    grocy = Grocy(api_url, password)

    _LOGGER.debug("Trying to get current stock...")
    stocks = json.loads(grocy.stock())

    _LOGGER.debug("Got stock with %d items", len(stocks))

    add_devices(StockSensor(stock, grocy) for stock in stocks)

class StockSensor(Sensor):
    """Representation of a Sensor for a product."""

    def __init__(self, stock, grocy):
        _LOGGER.debug("Setting up product with id: %s", stock['product_id'])
        self._grocy = grocy
        self._product_id = int(stock['product_id'])
        self._best_before_date = stock['best_before_date']
        self._state = float(stock['amount'])
    
    @property
    def state(self):
        return self._state

    @property
    def product_id(self):
        return self._state

    @property
    def best_before_date(self):
        return self._best_before_date

    def update(self):
        import json
        product = json.loads(self._grocy.product(self._product_id))
        self._state = int(product['stock_amount'])
        self._best_before_date = product['next_best_before_date']
