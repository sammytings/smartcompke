from google.oauth2 import service_account
from googleapiclient.discovery import build

from app.models import GoogleReview


class GoogleReviewService:


    @staticmethod
    def sync():


        credentials = service_account.Credentials.from_service_account_file(
            "google_credentials.json",
            scopes=[
                "https://www.googleapis.com/auth/business.manage"
            ]
        )


        service = build(
            "mybusiness",
            "v4",
            credentials=credentials
        )


        response = service.accounts().locations().reviews().list(
            parent="accounts/YOUR_ACCOUNT_ID/locations/YOUR_LOCATION_ID"
        ).execute()



        for item in response.get("reviews", []):


            GoogleReview.objects.update_or_create(

                google_review_id=item["reviewId"],

                defaults={

                    "reviewer_name":
                    item["reviewer"]["displayName"],


                    "comment":
                    item.get("comment",""),


                    "rating":
                    item["starRating"]

                }

            )