from fastapi import APIRouter, Query, status


callback_router = APIRouter()


@callback_router.get(
    "/spotify",
    # response_model=SuccessResponse[StatusResponse],
    status_code=status.HTTP_200_OK,
)
async def spotify_callback(
    code: str = Query(..., description="Spotify authorization code"),
    state: str = Query(..., description="OAuth state parameter")
):
    """Callback from Spotify OAuth."""
    # htelegram_id = await SpotifyRepository.get_oauth_state(state)
    # if not htelegram_id:
    #     logger.warning("[spotify] invalid or expired OAuth state: {state}", state=state[:8])
    #     raise InvalidOAuthStateError
    #
    # logger.info("[{htelegram_id}] [spotify] OAuth callback processing", htelegram_id=htelegram_id[:8])
    # await SpotifyRepository.delete_oauth_state(state)
    #
    # settings = get_settings()
    # await SpotifyService.handle_oauth_callback(code, settings.SPOTIFY_REDIRECT_URI, htelegram_id)
    #
    # logger.success("[{htelegram_id}] [spotify] OAuth completed successfully", htelegram_id=htelegram_id[:8])
    # status_response = StatusResponse(
    #     htelegram_id=htelegram_id[:8],
    #     status="success",
    #     message="Spotify tokens saved successfully",
    # )
    # return create_success_response(data=status_response)
