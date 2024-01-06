import fs from "fs";
import path from "path";
import { parseStream } from "fast-csv";
import type { IBookKeepingRow, RecordType } from "../types";
import { datasetPath, minKeyWordsFrequency } from "../../config/settings.json";

export async function keywordsGenerator(): Promise<Record<string, RecordType>> {
  const characterKeywords: Record<string, RecordType> = {};
  if (!datasetPath) {
    return characterKeywords;
  }

  // 获取数据集
  const locateDataSetPath = path.resolve(process.cwd(), datasetPath);
  const records = await getDataSetRecords(locateDataSetPath);

  const filteredRecords = records.filter((row) => {
    // 过滤的理由为，以下通常为个人微信红包交易，发生交易的理由可能有很多，不适合作为特征信息
    if (row["支付方式"] === "微信支付" && row["商品名称"] === "/") return false;

    // 如果备注不为空，则认为是特殊交易，不作为特征信息
    if (row["备注"].length > 0) return false;

    // 如果记录不含特征信息，则直接过滤
    if (
      row["类型"] === "" ||
      (row["交易对方"] === "" && row["商品名称"] === "")
    )
      return false;

    return true;
  });

  const characterFrequency: Record<string, number> = {};

  for (const record of filteredRecords) {
    const character = `${record["交易对方"]}|${record["商品名称"]}}`;

    if (!characterFrequency[character]) {
      characterFrequency[character] = 1;
    } else {
      characterFrequency[character] += 1;
    }

    if (characterFrequency[character] >= minKeyWordsFrequency) {
      // 如果特征词频达到阈值，则认为是特征词，计入特征词库
      if (!characterKeywords[character]) {
        characterKeywords[character] = record["类型"] as RecordType;
      } else {
        // 如果发现已存入特征词库，则判断类型是否一致，不一致则删掉特征，且永不录用
        if (characterKeywords[character] !== record["类型"]) {
          delete characterKeywords[character];
          characterFrequency[character] = -9999999;
        }
      }
    }
  }

  return characterKeywords;
}

async function getDataSetRecords(
  dataSetPath: string
): Promise<IBookKeepingRow[]> {
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
      .on("error", (error) => {
        reject(error)
      })
  });
}
