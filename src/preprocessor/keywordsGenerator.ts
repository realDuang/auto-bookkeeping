import fs from "fs";
import { parseStream } from "fast-csv";
import type { IBookKeepingRow } from "../types";

export async function keywordsGenerator(
  dataSetPath: string
): Promise<IBookKeepingRow[]> {
  const records = await getDataSetRecords(dataSetPath);

  const filteredRecords = records.filter((row) => {
    return (
      row["类型"] !== "人情" && row["类型"] !== "礼物" && row["类型"] !== "交易"
    );
  });

  return filteredRecords;
}

function getDataSetRecords(dataSetPath: string): Promise<IBookKeepingRow[]> {
  return new Promise((resolve, reject) => {
    const dataSetRows: IBookKeepingRow[] = [];

    const csvStream = fs.createReadStream(dataSetPath);
    parseStream<IBookKeepingRow, IBookKeepingRow>(csvStream, {
      headers: true,
      ignoreEmpty: true,
      trim: true,
    })
      .on("data", (row: IBookKeepingRow) => {
        dataSetRows.push(row);
      })
      .on("end", () => {
        resolve(dataSetRows);
      })
      .on("error", (error) => reject(error));
  });
}
