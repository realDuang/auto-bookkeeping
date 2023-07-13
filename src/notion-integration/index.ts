import {
  APIErrorCode,
  ClientErrorCode,
  Client as NotionClient,
  isNotionClientError,
} from "@notionhq/client";
import dotenv from "dotenv";
import { IBookKeepingRow } from "src/types";

dotenv.config();

async function addBookKeepRecord(
  notion: NotionClient,
  record: IBookKeepingRow
) {
  const databaseId = process.env.NOTION_DATABASE_ID;

  try {
    const response = await notion.pages.create({
      parent: { database_id: databaseId ?? "" },
      properties: {
        title: {
          title: [
            {
              text: {
                content: "",
              },
            },
          ],
        },
      },
    });
    console.log(response);
    console.log("Success! Entry added.");
  } catch (error: unknown) {
    if (isNotionClientError(error)) {
      switch (error.code) {
        case ClientErrorCode.RequestTimeout:
          console.log("Request timed out. Please try again.");
          break;
        case APIErrorCode.ObjectNotFound:
          console.log("Database not found.");
          break;
        case APIErrorCode.Unauthorized:
          console.log('Please check your "NOTION_KEY".');
          break;
        default:
          // you could even take advantage of exhaustiveness checking
          console.log(error);
      }
    }
  }
}

async function main(records: IBookKeepingRow[]) {
  const notion = new NotionClient({
    auth: process.env.NOTION_KEY,
  });
  const databaseId = process.env.NOTION_DATABASE_ID;

  const resp = await notion.databases.query({
    database_id: databaseId ?? "",
  });
  console.log((resp.results[0] as any).properties);
  // await notion.pages.addBookKeepRecord(notion);
}

main([])
  .then(() => process.exit(0))
  .catch((err) => {
    console.error(err);
    process.exit(1);
  });
