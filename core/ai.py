from groq import Groq
from core.logger import logger
from config import Config

client = Groq(api_key=Config.GROQ_API_KEY)

def get_ai_reply(user_message: str, context_info: str = "") -> str:
    """
    Gets AI reply for unexpected messages.
    context_info = current state so AI knows where user is in flow
    """
    try:
        system_prompt = f"""You are {Config.BOT_NAME}, a friendly assistant for {Config.COMPANY_NAME}.

Our services: {', '.join(Config.SERVICES)}

Your job:
- Answer questions about our company and services
- Be friendly and concise — under 80 words
- Always encourage user to submit their details
- If user asks about pricing say: "Our team will discuss pricing after reviewing your requirement"
- If you don't know something, say so honestly

Current context: {context_info if context_info else 'User just started'}"""

        response = client.chat.completions.create(
            model=Config.GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=150
        )

        reply = response.choices[0].message.content.strip()

        if not reply:
            return "Could you rephrase that? I want to make sure I help you correctly."

        return reply

    except Exception as e:
        logger.error(f"AI reply failed: {e}")
        return "I'm having a technical issue. Please try again."