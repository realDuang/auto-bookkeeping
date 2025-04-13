import fs from "fs";
import path from "path";
import { formatBillRecords } from "./formatter";
import { writeToStream } from "fast-csv";
import type { IBookKeepingRow } from "./types";

import Excel from "exceljs";
import { billPreprocessor } from "./preprocessor";
import {
  destinationPath,
  templatePath,
  xlsxDestinationPath,
} from "../../config/settings.json";

export async function main() {
  const bookKeepRecords = await formatBillRecords();

  const filteredBookKeepRecords = await billPreprocessor(bookKeepRecords);

  const writeStream = fs.createWriteStream(
    path.resolve(process.cwd(), destinationPath),
    {
      encoding: "utf8",
    }
  );
  writeToStream(writeStream, filteredBookKeepRecords, {
    headers: true,
    transform: (row: IBookKeepingRow) => {
      row["交易时间"] = row["交易时间"].toLocaleString() as any;
      return row;
    },
  });
}

async function writeToXlsx(bookKeepRecords: IBookKeepingRow[]) {
  copyFile(
    path.resolve(process.cwd(), templatePath),
    path.resolve(process.cwd(), xlsxDestinationPath)
  );

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
