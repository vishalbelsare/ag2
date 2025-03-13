# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0

# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0


from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from autogen.tools.experimental.google_api.authentication.credentials import get_credentials_from_json


def test_end2end() -> None:
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    client_secret_file = "client_secret_ag2.json"
    creds = get_credentials_from_json(
        client_secret_file=client_secret_file,
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
    )

    try:
        service = build("sheets", "v4", credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        # The ID and range of a sample spreadsheet.
        spreadsheet_id = "1BdWBOyCAyIPE6sgtPqGPxDqrgBpvl6zmSgGRQ_I3s-Y"
        range_name = "Sheet1!A2:E"
        result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
        values = result.get("values", [])

        if not values:
            print("No data found.")
            return

        print("Name, Major:")
        for row in values:
            print(row)
    except HttpError as err:
        print(err)
