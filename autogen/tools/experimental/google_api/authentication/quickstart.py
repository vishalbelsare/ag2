# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0


from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .simple_authentication import get_credentials

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "1BdWBOyCAyIPE6sgtPqGPxDqrgBpvl6zmSgGRQ_I3s-Y"
SAMPLE_RANGE_NAME = "Sheet1!A2:E"


def main() -> None:
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    client_secret_file = "client_secret_ag2.json"
    creds = get_credentials(
        client_secret_file=client_secret_file,
        service="spreadsheets",
        scopes={"readonly"},
    )

    try:
        service = build("sheets", "v4", credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME).execute()
        values = result.get("values", [])

        if not values:
            print("No data found.")
            return

        print("Name, Major:")
        for row in values:
            print(row)
    except HttpError as err:
        print(err)


if __name__ == "__main__":
    main()
