from groq import Groq
from django.conf import settings

from .knowledge import SMARTCOMPUTERS_KNOWLEDGE


class GrokClient:

    def __init__(self):

        self.client = Groq(
            api_key=settings.GROQ_API_KEY
        )


    def chat(self, user_message, context=""):

        try:

            # Combine business knowledge with optional extra context
            system_prompt = SMARTCOMPUTERS_KNOWLEDGE

            if context:
                system_prompt += f"""

Additional Context:
{context}
"""


            response = self.client.chat.completions.create(

                model="llama-3.1-8b-instant",

                messages=[

                    {
                        "role": "system",
                        "content": system_prompt
                    },

                    {
                        "role": "user",
                        "content": user_message
                    }

                ],

                temperature=0.7,

                max_tokens=500

            )


            answer = response.choices[0].message.content


            return {

                "success": True,

                "message": answer

            }


        except Exception as e:

            return {

                "success": False,

                "message": str(e)

            }