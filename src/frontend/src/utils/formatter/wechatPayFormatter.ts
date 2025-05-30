import { parseStream } from "fast-csv";
import type { IWechatBillRow, IBookKeepingRow } from "../../types";
import { transformCSVFileToBuffer } from ".";
import { Readable } from "stream";

export async function wechatPayFormatter(
  file: File
): Promise<IBookKeepingRow[]> {
  const csvBuffer = await transformCSVFileToBuffer(file);
  const csvStream = Readable.from(csvBuffer);

  return new Promise((resolve, reject) => {
    const bookKeepingRows: IBookKeepingRow[] = [];
    parseStream<IWechatBillRow, IBookKeepingRow>(csvStream, {
      headers: true,
      ignoreEmpty: true,
      skipLines: 14,
      trim: true,
    })
      .transform((row: IWechatBillRow) => {
        const bookKeepingRow: IBookKeepingRow = {
          交易时间: new Date(row.交易时间),
          类型: "",
          "金额(元)": row["金额(元)"].replace(/¥/g, ""),
          "收/支": row["收/支"],
          支付方式: row.支付方式 === "亲属卡" ? "亲属卡" : "微信支付",
          交易对方: row.交易对方,
          商品名称: row.商品,
          备注: row.备注 === "/" ? "" : row.备注,
        };
        return bookKeepingRow;
      })
      .on("data", (row: IBookKeepingRow) => {
        bookKeepingRows.push(row);
      })
      .on("end", () => {
        resolve(bookKeepingRows);
      })
      .on("error", (error: unknown) => reject(error));
  });
}
