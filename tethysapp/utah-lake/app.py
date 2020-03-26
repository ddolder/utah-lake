from tethys_sdk.base import TethysAppBase, url_map_maker
from tethys_sdk.app_settings import CustomSetting


class UtahLake(TethysAppBase):
    """
    Tethys app class for Dam Inventory.
    """

    name = 'Utah Lake Stations'
    index = 'utah-lake:home'
    icon = 'utah-lake/images/dam_icon.png'
    package = 'utah-lake'
    root_url = 'utah-lake'
    color = '#244C96'
    description = ''
    tags = ''
    enable_feedback = False
    feedback_emails = []

    def url_maps(self):
        """
        Add controllers
        """
        UrlMap = url_map_maker(self.root_url)

        url_maps = (
            UrlMap(
                name='home',
                url='utah-lake',
                controller='utah-lake.controllers.home'
            ),
            UrlMap(
                name='add_station',
                url='utah-lake/stations/add',
                controller='utah-lake.controllers.add_station'
            ),

            UrlMap(
                name='stations',
                url='utah-lake/stations',
                controller='utah-lake.controllers.list_stations'
            ),
        )

        return url_maps

    def custom_settings(self):
        """
        Example custom_settings method.
        """S
        custom_settings = (
            CustomSetting(
                name='max_stations',
                type=CustomSetting.TYPE_INTEGER,
                description='Maximum number of stations that can be created in the app.',
                required=False
            ),
        )
        return custom_settings
