import fs from "fs";
import path from "path";
import { writeToStream } from "fast-csv";
import { wechatPayFormatter } from "./wechatPayFormatter";
import { aliPayFormatter } from "./alipayFormatter";
import { IBookKeepingRow } from "./types";

export async function formatBillToCsv(filePaths: {
  destinationPath: string;
  aliPayOriginPath?: string;
  wechatPayOriginPath?: string;
}) {
  const { aliPayOriginPath, wechatPayOriginPath, destinationPath } = filePaths;

  let aliPayRecords: IBookKeepingRow[] = [];
  if (aliPayOriginPath) {
    aliPayRecords = await aliPayFormatter(aliPayOriginPath);
  }
  let wechatPayRecords: IBookKeepingRow[] = [];
  if (wechatPayOriginPath) {
    wechatPayRecords = await wechatPayFormatter(wechatPayOriginPath);
  }

  const bookKeepRecords = [...aliPayRecords, ...wechatPayRecords].sort(
    (a, b) => {
      return a.交易时间.getTime() - b.交易时间.getTime();
    }
  );

  const writeStream = fs.createWriteStream(destinationPath, {
    encoding: "utf8",
  });
  writeToStream(writeStream, bookKeepRecords, {
    headers: true,
    transform: (row: IBookKeepingRow) => {
      row["交易时间"] = row["交易时间"].toLocaleString() as any;
      return row;
    },
  });
}
