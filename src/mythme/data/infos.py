from functools import lru_cache
from mythme.model.chat import ChatMessage
from mythme.utils.config import config
from mythme.utils.bedrock import invoke_anthropic_chat


@lru_cache(maxsize=128)
def get_movie_info(json_info: str) -> str:
    prompt = "Here's some basic information about a specific movie:\n\n"
    prompt += f"```json\n{json_info}\n```\n\n"
    prompt += """(Rating is on a scale of 0 to 5).
 Based on this, enhance this information to provide more details about the movie. Details should include:
   - A brief plot summary and description of the movie's themes and style
   - Awards the movie has won or been nominated for, if any
   - The director and their significance in the film industry, including other well-known films they've directed
   - Cast members along with a few of their best-known roles in other movies, including any awards/nominations if any
   - Any interesting trivia or context to help someone understand why this movie is significant or worth watching
   - Information about the movie's specific genre or movement (e.g. Film Noir, Pre-Code, Horror), if relevant
   - Rotten Tomatoes Tomatometer and Popcornmeter scores, and Metacritic rating if available\n"""

    system_prompt = """You are a movie information assistant. Your job is to provide more detailed information
about a movie based on some basic info provided in the prompt. Your style is like a reporter for Variety in the
1930s/40s. The user is likely familiar with classic movies but may not be an expert, so provide enough context
for a general movie fan to understand the movie's significance and its key players. Be concise but informative,
and focus on the most interesting and relevant details. Do not include follow-up questions in your answer."""

    response = invoke_anthropic_chat(
        config.chat.mythme_models["movie_details"],
        [ChatMessage(role="user", content=prompt)],
        system_prompt=system_prompt,
    )

    return response.content.text.strip()


@lru_cache(maxsize=128)
def get_program_info(json_info: str) -> str:
    prompt = "Here's some basic information about a specific TV program:\n\n"
    prompt += f"```json\n{json_info}\n```\n\n"
    prompt += """Enhance this information to provide more details about the TV program. Details should include:
   - A brief plot summary and description of the show's history and airings
   - Awards the TV program has won or been nominated for, if any
   - The creator (if relevant) and any other reasonably well-known TV shows they've been involved with
   - Cast members along with a few of their best-known roles in other TV shows, including any awards/nominations if any
   - Any interesting trivia or context to help someone understand why this TV program is significant or worth watching
   - Information about the TV program's specific genre (e.g. Sitcom, Drama, Reality), if relevant
   - Links to the TV program's pages on IMDB, TMDB and/or RottenTomatoes, if available\n"""

    system_prompt = """You are a TV program information assistant. Your job is to provide more detailed information
about a TV show based on some basic info provided in the prompt. The user is likely familiar a range of TV shows
but may not be an expert (especially in newer programming), so provide enough context for a general TV fan to
understand the TV program's significance and its key players. Be concise but informative, and focus on the most
interesting and relevant details. Do not include follow-up questions in your answer."""

    response = invoke_anthropic_chat(
        config.chat.mythme_models["tv_program_details"],
        [ChatMessage(role="user", content=prompt)],
        system_prompt=system_prompt,
    )

    return response.content.text.strip()
