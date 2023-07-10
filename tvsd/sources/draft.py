from bs4 import BeautifulSoup


def parse_season_title(soup: BeautifulSoup) -> str:
    """Parses the season title from the soup

    Args:
        soup (BeautifulSoup): Soup of the season details page

    Returns:
        str: Season title
    """
    return str(soup.title.string).replace(" - 小宝影院 - 在线视频", "")
