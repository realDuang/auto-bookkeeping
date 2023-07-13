import fs from "fs";
import path from "path";
import { formatBillRecords } from "./formatter";
import { writeToStream } from "fast-csv";
import type { IBookKeepingRow } from "./types";

import Excel from "exceljs";
import { billPreprocessor } from "./preprocessor";

const aliPayOriginPath = path.resolve(
  __dirname,
  "../data-source/origin-data/alipay_record.csv"
);
const wechatPayOriginPath = path.resolve(
  __dirname,
  "../data-source/origin-data/wechat_record.csv"
);
const destinationPath = path.resolve(__dirname, "../out/processed-data.csv");
const templatePath = path.resolve(__dirname, "../template/template.xlsx");
const xlsxDestinationPath = path.resolve(
  __dirname,
  "../out/processed-data.xlsx"
);

export async function main() {
  const bookKeepRecords = await formatBillRecords({
    aliPayOriginPath,
    wechatPayOriginPath,
  });

  const filteredBookKeepRecords = await billPreprocessor(bookKeepRecords);

  const writeStream = fs.createWriteStream(destinationPath, {
    encoding: "utf8",
  });
  writeToStream(writeStream, filteredBookKeepRecords, {
    headers: true,
    transform: (row: IBookKeepingRow) => {
      row["交易时间"] = row["交易时间"].toLocaleString() as any;
      return row;
    },
  });
}

async function writeToXlsx(bookKeepRecords: IBookKeepingRow[]) {
  copyFile(templatePath, xlsxDestinationPath);

  const options = {
    filename: xlsxDestinationPath,
    useStyles: true,
  };
  const workbook = new Excel.stream.xlsx.WorkbookWriter(options);
  // 在加载时强制工作簿计算属性
  // workbook.calcProperties.fullCalcOnLoad = true;

  const worksheet = workbook.getWorksheet("移动支付流水");
  // console.log(worksheet);

  workbook.eachSheet((worksheet, sheetId) => {
    console.log(sheetId);
  });

  for (const record of bookKeepRecords) {
    worksheet.addRow(record).commit();
  }
  await workbook.commit();
}

function copyFile(sourcePath: string, destinationPath: string): Promise<void> {
  return new Promise((resolve, reject) => {
    const source = fs.createReadStream(sourcePath);
    const destination = fs.createWriteStream(destinationPath);
    source.pipe(destination);

    destination.on("finish", () => {
      resolve();
    });
    destination.on("error", (err) => {
      reject(err);
    });
  });
}

main();
