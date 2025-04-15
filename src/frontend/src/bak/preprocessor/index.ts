import { RecordType, type IBookKeepingRow, type KeywordsMap } from "../types";
import Settings from "../../../../../config/settings.json";
import { keywordsGenerator } from "./keywordsGenerator";

export async function billPreprocessor(
  bookKeepRecords: IBookKeepingRow[]
): Promise<IBookKeepingRow[]> {
  // 优先去掉非收支部分
  const filteredBookKeepRecords = bookKeepRecords.filter((row) => {
    return !(row["收/支"] === "/" && !row["商品名称"].includes("退款"));
  });

  // 用户设定关键词优先匹配
  const keywordsMap = Settings.keywords as unknown as KeywordsMap;
  const keywords = Object.keys(keywordsMap);
  const recordTypes = Object.values(RecordType);

  const userFillBookKeepRecords = filteredBookKeepRecords.map((row) => {
    if (row["类型"] !== "") return row;

    const keyword = keywords.find((keyword) =>
      row["商品名称"].includes(keyword)
    );
    if (keyword && recordTypes.some((type) => type === keywordsMap[keyword])) {
      row["类型"] = keywordsMap[keyword] as RecordType;
      return row;
    }

    return row;
  });

  // 根据以往数据集自动填充
  const characterKeywords: Record<string, RecordType> =
    await keywordsGenerator();

  const autoFillBookKeepRecords = userFillBookKeepRecords.map((row) => {
    if (row["类型"] !== "") return row;

    const character = `${row["交易对方"]}|${row["商品名称"]}}`;
    if (characterKeywords[character]) {
      row["类型"] = characterKeywords[character];
      return row;
    }
    return row;
  });

  return autoFillBookKeepRecords;
}
