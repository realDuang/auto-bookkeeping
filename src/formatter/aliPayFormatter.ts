import * as iconv from "iconv-lite";
import fs from "fs";
import { parseString } from "fast-csv";
import type { IAlipayBillRow, IBookKeepingRow } from "./types";

export async function aliPayFormatter(
  sourceFilePath: string
): Promise<IBookKeepingRow[]> {
  const csvBuffer = fs.readFileSync(sourceFilePath);

  // 将GBK编码转换为UTF-8编码
  const utf8Csv = iconv.decode(csvBuffer, "gbk");
  const lines = utf8Csv.split("\n");

  // 截取以"--------"开头的行中间的所有行
  let flag = false;
  const csvTableString = lines
    .filter((line: string) => {
      const isDividerLine = line.startsWith("--------");
      if (!flag) {
        if (isDividerLine) {
          flag = true;
        }
        return false;
      }
      if (isDividerLine) {
        flag = false;
        return false;
      }
      return true;
    })
    .map((line: string) => line.replace(/[\s]+,/g, ","))
    .join("");

  return new Promise((resolve, reject) => {
    const bookKeepingRows: IBookKeepingRow[] = [];
    parseString<IAlipayBillRow, IBookKeepingRow>(csvTableString, {
      headers: true,
      ignoreEmpty: true,
    })
      .transform((row: IAlipayBillRow) => {
        const bookKeepingRow: IBookKeepingRow = {
          交易时间: new Date(row.交易创建时间),
          类型: "",
          "金额(元)": row["金额（元）"],
          "收/支": row["收/支"] === "不计收支" ? "/" : row["收/支"],
          支付方式: "支付宝",
          交易对方: row.交易对方,
          商品名称: row.商品名称,
          备注: row.备注,
        };
        return bookKeepingRow;
      })
      .on("data", (row: IBookKeepingRow) => {
        bookKeepingRows.push(row);
      })
      .on("end", () => {
        resolve(bookKeepingRows);
      })
      .on("error", (error) => reject(error));
  });
}
