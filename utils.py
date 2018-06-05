from aiogram.utils.helper import Helper, HelperMode, ListItem


class States(Helper):
    mode = HelperMode.snake_case
    LANGUAGE_CHOICE = ListItem()
    MENU_RU = ListItem()
    MENU_EN = ListItem()
    DEV_MESSAGE_RU = ListItem()
    DEV_MESSAGE_EN = ListItem()
    GAME_RU_ON = ListItem()
    GAME_EN_ON = ListItem()
    GAME_RU_PAUSED = ListItem()
    GAME_EN_PAUSED = ListItem()
    GAME_RU_FINISH = ListItem()
    GAME_EN_FINISH = ListItem()
    RU_CHANGE_NICKNAME = ListItem()
    EN_CHANGE_NICKNAME = ListItem()
