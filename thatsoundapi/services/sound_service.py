from thatsoundapi.services.spotify.spotify_service import get_recent_played_tracks


async def recent_played_tracks(hgramid: str):
    # Implement yandex_music and Last.FM. Now only Spotify
    await get_recent_played_tracks()

    # Никита привет ты остановился на том что надо отрефакторить функцию get_recently_played_tracks (она огромная)
    # необходимо написать декоратор который всегда проверяет спотифай токен
    # типа вешаешь ее над функцией и это означает что токен точно не стухнет пока выполняется функция
